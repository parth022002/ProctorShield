import os

class Config():
    SECRET_KEY = os.environ.get("SECRET_KEY", "7c9270027a164800f09e52vb828q1384523667f")
    
    # change if not using gmail
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp://live.smtp.mailtrap.io:587")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL", "True") == "True"

    # add email and password 
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "api")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "4b969e70dba93d83958d3be57ad3a28b")
    
    # Database Configuration
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        # SQLite database on serverless Vercel environment must reside in read-write /tmp
        if os.environ.get("VERCEL"):
            db_url = "sqlite:////tmp/site.db"
        else:
            db_url = "sqlite:///site.db"
    elif db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_DATABASE_URI = db_url