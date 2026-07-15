from flask import render_template,Blueprint,redirect,url_for,request,flash,Response,jsonify,current_app
from flask_login import login_required,current_user,logout_user
from Proctorshield import db
from sqlalchemy import text
from Proctorshield.student.utils import shuffle,random
from Proctorshield.models import Student,Teacher,Quiz
from Proctorshield.student.utils import bar_graph
import copy
import os
import subprocess
import time
import threading



student = Blueprint("student",__name__,url_prefix="/student" ,template_folder="templates",static_folder="static")



@student.route("/home")
@login_required
def home():
    quotes = ["Let us study things that are no more. It is necessary to understand them, if only to avoid them.","The authority of those who teach is often an obstacle to those who want to learn","To acquire knowledge, one must study; but to acquire wisdom, one must observe."]
    random.shuffle(quotes)
    if current_user.student is None:
        logout_user()
        #return error page ERROR 403
        return "unauthorized acess attempted you have been logged out"
    return render_template("student_home.html",quotes = quotes, title = "Home")


@student.route("/log_violation", methods=['POST'])
@login_required
def log_violation():
    if current_user.student is None:
        return jsonify({"error": "Unauthorized"}), 403
    data = request.get_json()
    if not data:
        return jsonify({"error": "Bad request"}), 400
    
    quiz_id = data.get("quiz_id")
    violation_type = data.get("type") # "tab_switches", "fullscreen_exits", "face_missing", "multiple_faces", "look_away", "noise_violations"
    
    if not quiz_id or not violation_type:
        return jsonify({"error": "Missing parameters"}), 400
        
    from Proctorshield.models import ProctorLog, SuspiciousSnapshot
    log = ProctorLog.query.filter_by(student_id=current_user.student.id, quiz_id=quiz_id).first()
    if not log:
        log = ProctorLog(student_id=current_user.student.id, quiz_id=quiz_id)
        db.session.add(log)
        db.session.commit() # Save log first so we have log.id
        
    if violation_type == "tab_switches":
        log.tab_switches += 1
    elif violation_type == "fullscreen_exits":
        log.fullscreen_exits += 1
    elif violation_type == "face_missing":
        log.face_missing += 1
    elif violation_type == "multiple_faces":
        log.multiple_faces += 1
    elif violation_type == "look_away":
        log.look_away += 1
    elif violation_type == "noise_violations":
        log.noise_violations += 1
    
    total = (log.tab_switches + log.fullscreen_exits + log.face_missing + 
             log.multiple_faces + log.look_away + log.noise_violations)
    
    from Proctorshield.ai_engine import ProctorAIEngine
    prob, report = ProctorAIEngine.analyze_violations(log)
    log.ai_anomaly_score = prob
    log.ai_risk_diagnostics = report
    
    if prob >= 0.60:
        log.status = "Flagged"
    elif prob >= 0.15:
        log.status = "Suspicious"
    else:
        log.status = "Clean"
        
    # Process Snapshot Base64 if present
    image_b64 = data.get("image")
    if image_b64 and "," in image_b64:
        import base64
        import uuid
        header, encoded = image_b64.split(",", 1)
        try:
            image_data = base64.b64decode(encoded)
            if os.environ.get("VERCEL"):
                snapshots_dir = "/tmp/static/snapshots"
            else:
                snapshots_dir = os.path.join(current_app.root_path, "static", "snapshots")
            os.makedirs(snapshots_dir, exist_ok=True)
                
            filename = f"std_{current_user.id}_quiz_{quiz_id}_{violation_type}_{uuid.uuid4().hex[:8]}.jpg"
            filepath = os.path.join(snapshots_dir, filename)
            with open(filepath, "wb") as f:
                f.write(image_data)
                
            snapshot = SuspiciousSnapshot(proctor_log_id=log.id, violation_type=violation_type, image_path=f"snapshots/{filename}")
            db.session.add(snapshot)
        except Exception as e:
            current_app.logger.error(f"Failed to save snapshot: {e}")
            
    db.session.commit()
    return jsonify({"success": True, "total_violations": total, "status": log.status})


@student.route("/register_fingerprint", methods=['POST'])
@login_required
def register_fingerprint():
    if current_user.student is None:
        return jsonify({"error": "Unauthorized"}), 403
    data = request.get_json()
    if not data:
        return jsonify({"error": "Bad request"}), 400
        
    quiz_id = data.get("quiz_id")
    resolution = data.get("screen_resolution", "Unknown")
    platform = data.get("os_platform", "Unknown")
    
    if not quiz_id:
        return jsonify({"error": "Missing quiz_id"}), 400
        
    from Proctorshield.models import ExamFingerprint
    fp = ExamFingerprint.query.filter_by(student_id=current_user.student.id, quiz_id=quiz_id).first()
    if not fp:
        ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        ua = request.headers.get('User-Agent', 'Unknown')
        fp = ExamFingerprint(
            student_id=current_user.student.id,
            quiz_id=quiz_id,
            ip_address=ip,
            user_agent=ua[:255],
            screen_resolution=resolution,
            os_platform=platform
        )
        db.session.add(fp)
        db.session.commit()
        
    return jsonify({"success": True})


@student.route("/quiz/<int:quiz_id>",methods=['POST','GET'])
@login_required
def quiz(quiz_id):
    if current_user.student is None:
        logout_user()
        return redirect(url_for('main.welcome'))
    quiz = Quiz.query.filter_by(id = quiz_id).first_or_404()
    from Proctorshield.models import ProctorLog
    log = ProctorLog.query.filter_by(student_id=current_user.student.id, quiz_id=quiz.id).first()
    attempts_made = log.attempts_count if log else 0
    if attempts_made >= quiz.attempts_allowed:
        flash(f'You have reached the maximum number of attempts allowed for this quiz ({quiz.attempts_allowed}).','warning')
        return redirect(url_for('student.home'))
    if quiz not in current_user.student.assigned_quizzes:
        flash("You are not allowed to access the page you requested","warning")
        return redirect(url_for('student.home'))
    if not quiz.active:
        flash("The quiz you are trying to attemp is not active right now","warning")
        return redirect(url_for('student.home'))
    
    questions = quiz.questions
    orig_questions = dict()
    index = 1
    for question in questions:
        orig_questions[ str(question.question_desc)] = [str(question.option_1),str(question.option_2),str(question.option_3),str(question.option_4)]
        index += 1


    questions = copy.deepcopy(orig_questions)
    shuffled_q = shuffle(questions)

    for i in questions.keys():
        random.shuffle(questions[i])
    
    question_count = len(orig_questions)

    # Initialize ProctorLog for live monitoring when student starts setup
    from Proctorshield.models import ProctorLog
    log = ProctorLog.query.filter_by(student_id=current_user.student.id, quiz_id=quiz.id).first()
    if not log:
        log = ProctorLog(student_id=current_user.student.id, quiz_id=quiz.id)
        db.session.add(log)
        db.session.commit()
    else:
        # Reset log for the new attempt if they already attempted once
        if log.attempts_count > 0:
            log.tab_switches = 0
            log.fullscreen_exits = 0
            log.face_missing = 0
            log.multiple_faces = 0
            log.look_away = 0
            log.noise_violations = 0
            log.status = "Clean"
            log.ai_anomaly_score = 0.0
            log.ai_risk_diagnostics = "Secure. No anomalies detected."
            log.screen_recording = None
            log.camera_recording = None
            
            # Delete previous snapshots
            from Proctorshield.models import SuspiciousSnapshot
            SuspiciousSnapshot.query.filter_by(proctor_log_id=log.id).delete()
            db.session.commit()

    profile_photo = current_user.student.profile_photo if current_user.student else None
    return render_template('quiz.html', quiz=quiz, quiz_id=quiz.id, title = quiz.title, shuffled_questions = shuffled_q , questions = questions, question_count = question_count, profile_photo=profile_photo)








    

@student.route("/quiz_post/<int:quiz_id>", methods=['POST'])
@login_required
def quiz_post(quiz_id):

 
    quiz = Quiz.query.filter_by(id = quiz_id).first_or_404()
    if not quiz.active:
        flash('QUIZ NOT SUBMITTED The quiz you are trying to submit has expired','danger')
        return redirect(url_for('student.home'))
    from Proctorshield.models import ProctorLog
    log = ProctorLog.query.filter_by(student_id=current_user.student.id, quiz_id=quiz.id).first()
    attempts_made = log.attempts_count if log else 0
    if attempts_made >= quiz.attempts_allowed:
        flash('You have reached the maximum number of attempts allowed for this quiz.','danger')
        return redirect(url_for('student.home'))
    questions = quiz.questions
    orig_questions = dict()
    orig_questions_marks = dict()
    for question in questions:
        orig_questions[str(question.question_desc)] = [str(question.option_1),str(question.option_2),str(question.option_3),str(question.option_4)]
        orig_questions_marks[str(question.question_desc)] = question.marks
    
    questions = copy.deepcopy(orig_questions)

    marks = 0
    for i in questions.keys():
        answered = request.form[i]
        if orig_questions[i][0] == answered:
            marks += orig_questions_marks[i]
    
    if quiz not in current_user.student.submitted_quiz:
        current_user.student.submitted_quiz.append(quiz)
        db.session.commit()
        db.session.execute(text('UPDATE submits_quiz SET marks = :marks WHERE student_id = :student_id and quiz_id = :quiz_id'), {'marks': marks, 'student_id': current_user.student.id, 'quiz_id': quiz_id})
    else:
        res = db.session.execute(text('SELECT marks FROM submits_quiz WHERE student_id = :student_id AND quiz_id = :quiz_id'), {'student_id': current_user.student.id, 'quiz_id': quiz_id}).fetchone()
        existing_marks = res[0] if res else 0
        final_marks = max(existing_marks or 0, marks)
        db.session.execute(text('UPDATE submits_quiz SET marks = :marks WHERE student_id = :student_id AND quiz_id = :quiz_id'), {'marks': final_marks, 'student_id': current_user.student.id, 'quiz_id': quiz_id})
        
    if not log:
        log = ProctorLog(student_id=current_user.student.id, quiz_id=quiz.id)
        db.session.add(log)
    log.attempts_count += 1
    db.session.commit()
    flash(f'Your response for Quiz : {quiz.title} has been submitted','success')
    return redirect(url_for('student.home'))

@student.route("/list_quiz")
@login_required
def list_quiz():
    if current_user.student is None:
        flash('Access Denied','danger')
        return redirect(url_for('teacher.home'))
    quiz_list = [quiz for quiz in current_user.student.assigned_quizzes if quiz.active]
    quiz_exists = bool(len(quiz_list))
    return render_template('quiz_list.html',quiz_list = quiz_list,quiz_exists = quiz_exists, title = "Quizzes")


@student.route("/view_performance")
@login_required
def view_performance():
    if current_user.student is None:
        flash('Access Denied','danger')
        return redirect(url_for('teacher.home'))
    student = current_user.student
    quiz_submitted_query = tuple(db.session.execute(text('SELECT * FROM submits_quiz WHERE student_id = :student_id'), {'student_id': student.id}))
    quiz_submitted = list()
    
    for quiz in quiz_submitted_query:
        quiz_obj = Quiz.query.filter_by(id=quiz[1]).first()
        if quiz_obj and quiz_obj.results_published:
            all_marks = list(db.session.execute(text('SELECT marks FROM submits_quiz WHERE quiz_id = :quiz_id'), {'quiz_id': quiz[1]}))
            all_marks = [x[0] for x in all_marks]
            quiz_submitted.append(dict(quiz_title = quiz_obj.title,marks = quiz[3],all_marks = all_marks ))
    graph = bar_graph(quiz_submitted)

    return render_template('view_performance.html',graph = graph, title = 'Your Performance')
   
@student.route('/view_result')
@login_required
def view_result():
    if current_user.student is None:
        flash('Access Denied','danger')
        return redirect(url_for('teacher.home'))
    student = current_user.student
    quiz_submitted_query = tuple(db.session.execute(text('SELECT * FROM submits_quiz WHERE student_id = :student_id'), {'student_id': student.id}))
    quiz_submitted = list()
    
    for quiz in quiz_submitted_query:
        quiz_obj = Quiz.query.filter_by(id=quiz[1]).first()
        if quiz_obj and quiz_obj.results_published:
            quiz_submitted.append(dict(title = quiz_obj.title,marks = quiz[3],total_marks = quiz_obj.marks))

    quiz_exists = bool(len(quiz_submitted))
    return render_template('view_result.html',quiz_list = quiz_submitted, title = "View Result", quiz_exists = quiz_exists)




    
@student.route('/add_teacher', methods = ['GET','POST'])
@login_required
def add_teacher():
    if current_user.student is None:
        flash('Access Denied','danger')
        return redirect(url_for('teacher.home'))
    if request.method == 'GET':
        return render_template('add_teacher.html',title = 'Add Teacher')
    if request.method == 'POST':
        teacher_id = request.form['teacher_id']
        teacher = Teacher.query.filter_by(id = teacher_id).first()
        if teacher is None:
            flash(f'Teacher with teacher id {teacher_id} does not exist','danger')
            return redirect(url_for('student.add_teacher'))
        if current_user.student in teacher.students:
            flash('The teacher is already added','info')
            return redirect(url_for('student.add_teacher'))
        teacher.students.append(current_user.student)
        db.session.commit()
        flash('Teacher has been added','success')
        return redirect(url_for('student.add_teacher'))


@student.route('/upload_recording', methods=['POST'])
@login_required
def upload_recording():
    if current_user.student is None:
        return jsonify({"error": "Unauthorized"}), 403
        
    quiz_id = request.form.get("quiz_id")
    recording_type = request.form.get("type") # "screen" or "camera"
    
    if not quiz_id or not recording_type or 'video' not in request.files:
        return jsonify({"error": "Missing parameters"}), 400
        
    video_file = request.files['video']
    
    # Save the file
    filename = f"recording_{recording_type}_{current_user.student.id}_{quiz_id}.webm"
    if os.environ.get("VERCEL"):
        static_dir = "/tmp/static/recordings"
    else:
        static_dir = os.path.join(current_app.root_path, 'static', 'recordings')
    os.makedirs(static_dir, exist_ok=True)
    
    filepath = os.path.join(static_dir, filename)
    video_file.save(filepath)
    
    # Update ProctorLog in DB
    from Proctorshield.models import ProctorLog
    log = ProctorLog.query.filter_by(student_id=current_user.student.id, quiz_id=quiz_id).first()
    if not log:
        log = ProctorLog(student_id=current_user.student.id, quiz_id=quiz_id)
        db.session.add(log)
        
    rel_path = f"recordings/{filename}"
    if recording_type == "screen":
        log.screen_recording = rel_path
    elif recording_type == "camera":
        log.camera_recording = rel_path
        
    db.session.commit()
    return jsonify({"success": True, "path": rel_path})
            
        

