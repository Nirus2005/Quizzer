from flask import Flask
from .auth import bcrypt, login_manager
from .database import db, DB_NAME
from .models import User
from flask_wtf.csrf import CSRFProtect

#appand blueprints 
def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI']=f'sqlite:///{DB_NAME}'
    app.config['SECRET_KEY']="QWERTYUIOP"
    
    db.init_app(app)
    login_manager.init_app(app)
    
    from .auth import auth
    app.register_blueprint(auth, url_prefix='/')

    from .admin import admin
    app.register_blueprint(admin, url_prefix='/')
    
    from .user import user
    app.register_blueprint(user, url_prefix='/')

    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

app =create_app()

# Hard coding the admin credentials into the DB  
with app.app_context():
    admin = User.query.filter_by(is_admin=True).first()
    if not admin :
        hashed_password = bcrypt.generate_password_hash("quiz_master")
        admin = User(email="quiz_master@gmail.com", username= "Quiz_Master", password= hashed_password ,is_admin=True)
        db.session.add(admin)
        db.session.commit()