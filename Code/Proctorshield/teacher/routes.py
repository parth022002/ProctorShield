from flask import render_template,Blueprint,flash,redirect,url_for,request,send_from_directory,Response
from flask_login import login_required,current_user,logout_user
from Proctorshield.models import Quiz,Quiz_Questions,Student
from Proctorshield import db
from sqlalchemy import text
import datetime
import csv
import os
import threading

teacher = Blueprint('teacher',__name__,url_prefix="/teacher",template_folder='templates')



@teacher.route('/home')
@login_required
def home():
    if current_user.teacher is None:
        flash("Permission denied to access the page",'danger')
        return redirect(url_for('student.home'))
    return render_template('teacher_home.html',title = 'Home')


@teacher.route("/create_new_quiz", methods = ['GET', 'POST'])
@login_required
def create_new_quiz():
    if current_user.teacher is None:
        flash("Permission denied to access the page",'danger')
        return redirect(url_for('student.home'))
        
    if request.method == 'POST':
        current_teacher = current_user.teacher
        response = request.form
        
        # Robustly count questions starting with prefix 'Question'
        question_keys = [k for k in response.keys() if k.startswith('Question')]
        no_of_questions = len(question_keys)
        
        total_marks = 0
        start_time = response['start_time']
        end_time = response['end_time']
        duration = int(response.get('duration', 30)) # default duration to 30 mins
        attempts_allowed = int(response.get('attempts_allowed', 1))
        
        start_time = datetime.datetime.strptime(start_time,'%Y-%m-%d')
        end_time = datetime.datetime.strptime(end_time,'%Y-%m-%d')
        end_time += datetime.timedelta(seconds=24*60*60 - 1)

        quiz = Quiz(title = response['title'], start_time = start_time, end_time = end_time, duration = duration, attempts_allowed = attempts_allowed, teacher_id = current_teacher.id)
        
        for num in range(1, int(no_of_questions) + 1):
            # Handle empty/N/A values for True/False questions dynamically
            opt_c = response.get('Option'+str(num)+'C', '-')
            opt_d = response.get('Option'+str(num)+'D', '-')
            if not opt_c:
                opt_c = '-'
            if not opt_d:
                opt_d = '-'
                
            total_marks += int(response['Marks'+str(num)])
            question = Quiz_Questions(
                question_desc = response['Question'+str(num)], 
                option_1 = response['Option'+str(num)+'A'], 
                option_2 = response['Option'+str(num)+'B'], 
                option_3 = opt_c, 
                option_4 = opt_d, 
                marks = int(response['Marks'+str(num)])
            )
            question.quiz = quiz
            db.session.add(question)
        
        quiz.marks = total_marks
        db.session.add(quiz)
        db.session.commit()

        flash('The Quiz has been created', 'success')
        return redirect(url_for('teacher.home'))
        
    return render_template('create_quiz.html', title = 'Create Quiz')


@teacher.route('/activate_quiz_list')
@login_required
def activate_quiz_list():
    if current_user.teacher is None:
        flash('Access Denide','danger')
        return redirect(url_for('student.home'))
    teacher = current_user.teacher
    quiz_list = list(teacher.quiz_created)
    quiz_exists = bool(len(quiz_list))
    return render_template('quiz_list_activate.html',title = 'Activate Quiz', quiz_list = quiz_list, quiz_exists = quiz_exists)


@teacher.route('/activate_quiz/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def activate_quiz(quiz_id):
    if current_user.teacher is None:
        flash('Access Denied','danger')
        return redirect(url_for('student.home'))
    teacher = current_user.teacher
    quiz = Quiz.query.filter_by(id = quiz_id).first_or_404()
    if quiz.teacher_id != teacher.id:
        return redirect(url_for('teacher.home'))
        
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'deactivate':
            quiz.active = False
            quiz.assigned_students = []
            db.session.commit()
            flash(f'Quiz "{quiz.title}" has been deactivated.', 'warning')
        else:
            selected_ids = request.form.getlist('assigned_student_ids')
            selected_students = Student.query.filter(Student.id.in_([int(sid) for sid in selected_ids])).all()
            quiz.assigned_students = selected_students
            quiz.active = True
            db.session.commit()
            flash(f'Quiz "{quiz.title}" is now active for {len(selected_students)} selected students.', 'success')
            
        return redirect(url_for('teacher.activate_quiz_list'))
        
    students = Student.query.filter_by(approved=True).all()
    return render_template('activate_quiz_settings.html', quiz=quiz, students=students)

@teacher.route('/view_performance_list')
@login_required
def view_performance_list():
    if current_user.teacher is None:
        flash('Access Denied','danger')
        return redirect(url_for('student.home'))
    teacher = current_user.teacher
    quiz_list = list(teacher.quiz_created) 
    quiz_exists = bool(len(quiz_list))
    return render_template('quiz_list_teacher.html',title = 'View Performace', quiz_list = quiz_list, quiz_exists = quiz_exists)



# def run_script():
#     while True:
#         # Capture frame-by-frame
#         success, frame = camera.read()
#         if not success:
#             break
#         else:
            
            

#             head_pose_thread = threading.Thread(target=head_pose.pose)
#             audio_thread = threading.Thread(target=audio.sound)
#             detection_thread = threading.Thread(target=detection.run_detection)
#             head_pose_thread.start()
#             audio_thread.start()
#             detection_thread.start()

#             head_pose_thread.join()
#             audio_thread.join()
#             detection_thread.join()

#                         # Convert the frame to bytes
#             ret, buffer = cv2.imencode('.jpg', frame)
#             frame_bytes = buffer.tobytes()
#             yield (b'--frame\r\n'
#                             b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
# @teacher.route('/view_performance/video')
# def stream_data():
#         data_generator = run_script()
#         return Response(data_generator, mimetype='text/plain')
                
# script_thread = threading.Thread(target=run_script)

#     # Start the thread
# script_thread.start()
@teacher.route('/view_performance/video') 
def video_feed():
    return render_template('video_feed.html')          









@teacher.route('/view_performance/<int:quiz_id>', methods = ['POST','GET'])
@login_required
def view_performance(quiz_id):
    if current_user.teacher is None:
        flash('Access Denied','danger')
        return redirect(url_for('student.home'))
    quiz = Quiz.query.filter_by(id = quiz_id).first_or_404()
    teacher = current_user.teacher
    marks = list(db.session.execute(text('SELECT student_id,marks FROM submits_quiz WHERE quiz_id = :quiz_id'), {'quiz_id': quiz_id}))
    data = list()
    
    from Proctorshield.models import ProctorLog
    for i,entry in enumerate(marks):
        student_id = entry[0]
        student_name = Student.query.filter_by(id = student_id).first().user.name
        log = ProctorLog.query.filter_by(student_id=student_id, quiz_id=quiz_id).first()
        
        data_entry = dict()
        data_entry['sr_no'] = i+1
        data_entry['student_id'] = student_id
        data_entry['student_name'] = student_name
        data_entry['marks'] = entry[1]
        data_entry['tab_switches'] = log.tab_switches if log else 0
        data_entry['fullscreen_exits'] = log.fullscreen_exits if log else 0
        data_entry['face_missing'] = log.face_missing if log else 0
        data_entry['multiple_faces'] = log.multiple_faces if log else 0
        data_entry['look_away'] = log.look_away if log else 0
        data_entry['noise_violations'] = log.noise_violations if log else 0
        data_entry['total_violations'] = (
            data_entry['tab_switches'] + data_entry['fullscreen_exits'] +
            data_entry['face_missing'] + data_entry['multiple_faces'] +
            data_entry['look_away'] + data_entry['noise_violations']
        )
        data_entry['status'] = log.status if log else "Clean"
        data_entry['log_id'] = log.id if log else None
        
        data.append(data_entry)
    data_exists = bool(len(data))
    if request.method == 'POST':
        path = os.getcwd() + f'/Proctorshield/results/{quiz.title}_results.csv'
        try:
            with open(path,'w',newline='',encoding='utf-8') as file:
                field_names = list(data[0])
                writer = csv.DictWriter(file, fieldnames = field_names)
                writer.writeheader()
                for entry in data:
                    writer.writerow(entry)
            return send_from_directory(directory='results', filename=f'{quiz.title}_results.csv', as_attachment = True)
        except IOError:
            flash('Downloading Error Occurred','warning')
            return redirect(url_for('teacher.home'))
    return render_template('view_quiz_performance.html',title = "View Performance", quiz_title = quiz.title, data = data)


@teacher.route('/toggle_publish/<int:quiz_id>', methods=['POST'])
@login_required
def toggle_publish(quiz_id):
    if current_user.teacher is None:
        flash('Access Denied', 'danger')
        return redirect(url_for('student.home'))
    quiz = Quiz.query.filter_by(id=quiz_id).first_or_404()
    if quiz.teacher_id != current_user.teacher.id:
        flash('Access Denied', 'danger')
        return redirect(url_for('teacher.home'))
        
    quiz.results_published = not quiz.results_published
    db.session.commit()
    
    status = "published" if quiz.results_published else "unpublished"
    flash(f'Results for quiz "{quiz.title}" have been successfully {status}!', 'success')
    return redirect(url_for('teacher.view_performance_list'))


@teacher.route('/get_snapshots/<int:log_id>')
@login_required
def get_snapshots(log_id):
    from flask import jsonify
    if current_user.teacher is None:
        return jsonify({"error": "Unauthorized"}), 403
    from Proctorshield.models import ProctorLog, SuspiciousSnapshot
    log = ProctorLog.query.get_or_404(log_id)
    if log.quiz.teacher_id != current_user.teacher.id:
        return jsonify({"error": "Unauthorized"}), 403
        
    snapshots = SuspiciousSnapshot.query.filter_by(proctor_log_id=log_id).all()
    snapshots_data = []
    for s in snapshots:
        snapshots_data.append({
            "id": s.id,
            "type": s.violation_type,
            "image_url": url_for('static', filename=s.image_path),
            "timestamp": s.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })
        
    from Proctorshield.models import ExamFingerprint
    fp = ExamFingerprint.query.filter_by(student_id=log.student_id, quiz_id=log.quiz_id).first()
    fp_data = None
    if fp:
        fp_data = {
            "ip_address": fp.ip_address,
            "user_agent": fp.user_agent,
            "screen_resolution": fp.screen_resolution,
            "os_platform": fp.os_platform,
            "timestamp": fp.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }
        
    return jsonify({
        "success": True, 
        "snapshots": snapshots_data,
        "fingerprint": fp_data,
        "student_name": log.student.user.name,
        "quiz_title": log.quiz.title,
        "ai_anomaly_score": log.ai_anomaly_score,
        "ai_risk_diagnostics": log.ai_risk_diagnostics,
        "screen_recording": url_for('static', filename=log.screen_recording) if log.screen_recording else None,
        "camera_recording": url_for('static', filename=log.camera_recording) if log.camera_recording else None
    })


@teacher.route('/live_monitoring/<int:quiz_id>')
@login_required
def live_monitoring(quiz_id):
    if current_user.teacher is None:
        flash('Access Denied', 'danger')
        return redirect(url_for('student.home'))
    quiz = Quiz.query.filter_by(id=quiz_id).first_or_404()
    if quiz.teacher_id != current_user.teacher.id:
        flash('Access Denied', 'danger')
        return redirect(url_for('teacher.home'))
        
    return render_template('live_monitoring.html', quiz=quiz)


@teacher.route('/live_monitoring_data/<int:quiz_id>')
@login_required
def live_monitoring_data(quiz_id):
    from flask import jsonify
    if current_user.teacher is None:
        return jsonify({"error": "Unauthorized"}), 403
    quiz = Quiz.query.filter_by(id=quiz_id).first_or_404()
    if quiz.teacher_id != current_user.teacher.id:
        return jsonify({"error": "Unauthorized"}), 403
        
    from Proctorshield.models import ProctorLog, Student
    # Get all logs for this quiz
    logs = ProctorLog.query.filter_by(quiz_id=quiz_id).all()
    
    # Check who has submitted
    submitted_student_ids = [s.id for s in quiz.submitted_by]
    
    data = []
    for log in logs:
        student_name = log.student.user.name
        is_submitted = log.student_id in submitted_student_ids
        
        total_violations = (
            log.tab_switches + log.fullscreen_exits +
            log.face_missing + log.multiple_faces +
            log.look_away + log.noise_violations
        )
        
        status = log.status
        if total_violations > 8:
            status = "Flagged"
        elif total_violations > 3:
            status = "Suspicious"
        else:
            status = "Clean"
            
        data.append({
            "student_name": student_name,
            "student_id": log.student_id,
            "tab_switches": log.tab_switches,
            "fullscreen_exits": log.fullscreen_exits,
            "face_alerts": log.face_missing + log.multiple_faces,
            "look_away": log.look_away,
            "noise_violations": log.noise_violations,
            "total_violations": total_violations,
            "status": status,
            "is_submitted": is_submitted
        })
        
    return jsonify({
        "success": True,
        "quiz_title": quiz.title,
        "active": quiz.active,
        "students": data
    })


@teacher.route('/approve_students', methods=['GET', 'POST'])
@login_required
def approve_students():
    if current_user.teacher is None:
        flash('Access Denied','danger')
        return redirect(url_for('student.home'))
        
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        action = request.form.get('action') # "approve" or "reject"
        student = Student.query.get(student_id)
        if student:
            if action == 'approve':
                student.approved = True
                db.session.commit()
                flash(f'Student {student.user.name} has been approved successfully.', 'success')
            elif action == 'reject':
                user = student.user
                db.session.delete(student)
                db.session.delete(user)
                db.session.commit()
                flash(f'Student registration has been rejected and deleted.', 'warning')
        return redirect(url_for('teacher.approve_students'))
        
    pending_students = Student.query.filter_by(approved=False).all()
    approved_students = Student.query.filter_by(approved=True).all()
    return render_template('approve_students.html', pending_students=pending_students, approved_students=approved_students, title='Approve Students')




    






    
    
    

