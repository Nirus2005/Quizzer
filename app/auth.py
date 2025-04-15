from flask import Blueprint, render_template, flash, redirect, url_for, request
from .models import Subject, Quiz,User, Score, Question, Chapter
from .database import db
from flask_login import logout_user, login_required, LoginManager, current_user, login_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from app.admin import SubjectForm,ChapterForm, SubjectEditForm, ChapterEditForm, DeleteForm, QuizForm, QuizEditForm,QuestionForm, QuestionEditForm
from datetime import date

auth = Blueprint('auth', __name__)
bcrypt = Bcrypt()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

# defining flaskforms

class SignupForm(FlaskForm):
    email =  StringField(validators=[InputRequired(), Length(min=6, max=100)], render_kw={"placeholder":"Email"})
    
    username =  StringField(validators=[InputRequired(), Length(min=2, max=50)], render_kw={"placeholder":"Username"})

    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder":"Password"})

    submit = SubmitField("Signup")

    def validate_email(self, email):
        existing_email= User.query.filter_by(email=email.data).first()
        if existing_email :
            raise ValidationError("Email already exists. Please proceed to Login.")
        
class LoginForm(FlaskForm):
    email =  StringField(validators=[InputRequired(), Length(min=4, max=100)], render_kw={"placeholder":"Email"})

    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder":"Password"})

    submit = SubmitField("Login")


# landing page

@auth.route('/')
def base():
    if current_user.is_authenticated:
        if current_user.is_admin:
            flash('You do not have access to this page.', 'error')
            return redirect(url_for('admin.admin_dashboard'))
        return redirect(url_for('user.user_dashboard', username=current_user.username))
    return render_template('base.html')


# login page 

@auth.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user= User.query.filter_by(email=form.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                flash('You have Logged in successfully', 'success')
                if user.is_admin:
                    return redirect(url_for('admin.admin_dashboard'))
                else :
                    return redirect(url_for('user.user_dashboard'))
            else:
                flash('Incorrect Password. Retry.','error')
        else:
            flash('Email not found. Signup or try another Email.', 'error')

    return render_template('login.html', form = form)


# signup page

@auth.route('/signup', methods=['GET','POST'])
def signup():
    form = SignupForm()

    if form.validate_on_submit():            
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(email=form.email.data, username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account Created successfully. Proceed to Login','success')

        return redirect(url_for('auth.login'))

    return render_template('signup.html', form = form)


# logout return to login page

@auth.route('/logout', methods =['GET','POST'])
@login_required
def logout():
    logout_user()
    flash('You have logged out successfully.', 'info')
    return redirect(url_for('auth.login'))


# search functionality

@auth.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('query', '').strip()
    table = request.args.get('table', '')

    
    results = []
    subjectForm = SubjectForm()
    chapterForm = ChapterForm()
    deleteForm=DeleteForm()
    chapterEditForm = ChapterEditForm()
    subjectEditForm = SubjectEditForm()
    quizForm = QuizForm()
    quizEditForm =QuizEditForm()
    questionEditForm=QuestionEditForm()
    questionForm=QuestionForm()
    
    heading=f"Search results for '{query}'"

    # Handle search for different tables


    if current_user.is_admin:    # logged in as admin 
        if not query or not table:
            return redirect(url_for('admin.admin_dashboard')) 
        
        if table == 'subject':
            results = Subject.query.filter(Subject.name.ilike(f"%{query}%")).all()
            chapters = Chapter.query.all()
            return render_template("admin.html",subjectForm=subjectForm, subjects=results, chapters= chapters, chapterForm=chapterForm, deleteForm=deleteForm, chapterEditForm=chapterEditForm, subjectEditForm=subjectEditForm,heading=heading)

        elif table == 'quizzes':
            results = Quiz.query.filter(Quiz.name.ilike(f"%{query}%")).all()
            subjects = Subject.query.all()
            questions = Question.query.all()
            chapters = Chapter.query.all()
            chapters_by_subject = {}

            for chapter in chapters:
                if chapter.subject_id not in chapters_by_subject:
                    chapters_by_subject[chapter.subject_id] = []
                chapters_by_subject[chapter.subject_id].append((chapter.id, chapter.name))

            return render_template("admin_quizzes.html",quizForm=quizForm, subjectForm=subjectForm, quizzes=results, subjects= subjects,questionForm=questionForm, questions=questions, deleteForm=deleteForm, chapters_by_subject=chapters_by_subject, questionEditForm=questionEditForm, quizEditForm=quizEditForm, heading=heading)

        elif table == 'users':
            results = User.query.filter(User.username.ilike(f"%{query}%"), User.is_admin==False).all()
            user_attempts = {}
            for user in results:
                attempted_quizzes = db.session.query(Quiz.name,Quiz.id, Score.score, db.func.count(Question.id).label("total_questions")).join(Score, Score.quiz_id == Quiz.id).join(Question, Question.quiz_id == Quiz.id).filter(Score.user_id == user.id).group_by(Quiz.id, Score.score).all()
                user_attempts[user.id] = attempted_quizzes
            return render_template("admin_users.html", users=results, user_attempts=user_attempts, heading=heading)
    
    
    else: #logged in as user 
            if not query:
                return redirect(url_for('user.user_dashboard')) 
            results = Subject.query.filter(Subject.name.ilike(f"%{query}%")).all()
            availabe_quizzes = {}  
            upcoming_quizzes = {}  
            today = date.today() 

            for subject in results:
                #quizzes that the user can attempt
                todays_quizzes = (
                    Quiz.query
                    .join(Chapter)
                    .filter(
                        Chapter.subject_id == subject.id,
                        Quiz.date == today,
                        ~Quiz.id.in_(db.session.query(Score.quiz_id).filter_by(user_id=current_user.id)), 
                        Quiz.id.in_(db.session.query(Question.quiz_id))
                    ).all()
                    )
                #quizzes that not available yet
                future_quizzes = (
                    Quiz.query
                    .join(Chapter)
                    .filter(
                        Chapter.subject_id == subject.id,
                        Quiz.date > today,
                        ~Quiz.id.in_(db.session.query(Score.quiz_id).filter_by(user_id=current_user.id)), 
                        Quiz.id.in_(db.session.query(Question.quiz_id))
                    ).all()
                    )
                
                if todays_quizzes:  
                    availabe_quizzes[subject] = todays_quizzes
                if future_quizzes:  
                    upcoming_quizzes[subject] = future_quizzes

            return render_template('user.html', available_quizzes=availabe_quizzes, upcoming_quizzes = upcoming_quizzes, subjects=results,heading=heading)
  