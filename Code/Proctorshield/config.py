class Config():
    SECRET_KEY = "7c9270027a164800f09e52vb828q1384523667f"
    #change if not using gmail
    MAIL_SERVER = "smtp://live.smtp.mailtrap.io:587"
    MAIL_PORT = 587
    MAIL_USE_SSL = True
    #mail port info ends

    #add email and password 
    MAIL_USERNAME = "api"
    MAIL_PASSWORD = "4b969e70dba93d83958d3be57ad3a28b"
    SQLALCHEMY_DATABASE_URI = "sqlite:///site.db"