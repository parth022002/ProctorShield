from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from Proctorshield.config import Config


mail = Mail()
bcrypt = Bcrypt()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_message_category = "info"
login_manager.login_view = "auth.login"



def create_app(config_class = Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    login_manager.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)
    db.init_app(app)

    # Perform automated database initialization & migrations
    with app.app_context():
        from Proctorshield.models import User, Student, Teacher, Quiz, Quiz_Questions, ProctorLog
        import os
        from sqlalchemy import inspect, text

        # Skip heavy legacy migrations on Vercel to optimize serverless cold starts.
        if not os.environ.get("VERCEL"):
            db.create_all()
            try:
                db.session.execute(text("ALTER TABLE quiz ADD COLUMN duration INTEGER DEFAULT 30"))
                db.session.commit()
                print("Successfully migrated: Added duration column to quiz table!")
            except Exception as e:
                db.session.rollback()

            try:
                db.session.execute(text('''
                    CREATE TABLE IF NOT EXISTS quiz_assigned_students (
                        student_id INTEGER NOT NULL,
                        quiz_id INTEGER NOT NULL,
                        PRIMARY KEY (student_id, quiz_id),
                        FOREIGN KEY(student_id) REFERENCES student (id) ON DELETE CASCADE,
                        FOREIGN KEY(quiz_id) REFERENCES quiz (id) ON DELETE CASCADE
                    )
                '''))
                db.session.commit()
                print("Successfully created quiz_assigned_students table!")
            except Exception as e:
                db.session.rollback()

            try:
                db.session.execute(text("ALTER TABLE student ADD COLUMN profile_photo TEXT"))
                db.session.commit()
                print("Successfully migrated: Added profile_photo column to student table!")
            except Exception as e:
                db.session.rollback()

            try:
                db.session.execute(text("ALTER TABLE quiz ADD COLUMN results_published BOOLEAN DEFAULT 0"))
                db.session.commit()
                print("Successfully migrated: Added results_published column to quiz table!")
            except Exception as e:
                db.session.rollback()

            try:
                db.session.execute(text("ALTER TABLE proctor_log ADD COLUMN screen_recording TEXT"))
                db.session.commit()
                print("Successfully migrated: Added screen_recording column to proctor_log table!")
            except Exception as e:
                db.session.rollback()

            try:
                db.session.execute(text("ALTER TABLE proctor_log ADD COLUMN camera_recording TEXT"))
                db.session.commit()
                print("Successfully migrated: Added camera_recording column to proctor_log table!")
            except Exception as e:
                db.session.rollback()

            try:
                db.session.execute(text("ALTER TABLE quiz ADD COLUMN attempts_allowed INTEGER DEFAULT 1"))
                db.session.commit()
                print("Successfully migrated: Added attempts_allowed column to quiz table!")
            except Exception as e:
                db.session.rollback()

            try:
                db.session.execute(text("ALTER TABLE proctor_log ADD COLUMN attempts_count INTEGER DEFAULT 0"))
                db.session.commit()
                print("Successfully migrated: Added attempts_count column to proctor_log table!")
            except Exception as e:
                db.session.rollback()

            try:
                db.session.execute(text("ALTER TABLE student ADD COLUMN approved BOOLEAN DEFAULT 0"))
                db.session.commit()
                db.session.execute(text("UPDATE student SET approved = 1"))
                db.session.commit()
                print("Successfully migrated: Added approved column to student table and approved existing students!")
            except Exception as e:
                db.session.rollback()
        else:
            # On Vercel, use a fast single query to check table presence.
            # If the database is completely empty/new, initialize the tables.
            try:
                inspector = inspect(db.engine)
                if not inspector.has_table("user"):
                    db.create_all()
                    print("Vercel startup: Created tables for fresh database.")
            except Exception as e:
                print("Vercel database initialization check failed:", e)

    from Proctorshield.main.routes import main
    from Proctorshield.auth.routes import auth
    from Proctorshield.student.routes import student
    from Proctorshield.teacher.routes import teacher


    app.register_blueprint(student)
    app.register_blueprint(teacher)
    app.register_blueprint(main)
    app.register_blueprint(auth)

    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

    if os.environ.get("VERCEL"):
        from flask import send_from_directory
        @app.route('/static/snapshots/<path:filename>')
        def serve_snapshots(filename):
            return send_from_directory('/tmp/static/snapshots', filename)

        @app.route('/static/recordings/<path:filename>')
        def serve_recordings(filename):
            return send_from_directory('/tmp/static/recordings', filename)

    return app

