from flask import Blueprint, render_template, flash, redirect, url_for, request
from .models import User, Subject, Chapter, Quiz, Question, Score, Answers
from .database import db
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, Length, ValidationError, DataRequired
from wtforms import StringField, SubmitField, TextAreaField, SelectField, DateField
from flask_bcrypt import Bcrypt
from datetime import date


admin = Blueprint('admin', __name__)
bcrypt = Bcrypt()


# defining flaskforms for diff inputs
class SubjectForm(FlaskForm):
    name = StringField(validators=[InputRequired(), Length(min=2, max=100)], render_kw={"placeholder": "Subject Name"})

    description = TextAreaField(validators=[DataRequired(), Length(min=4, max=100)], render_kw={"placeholder": "Subject Description"})

    submit = SubmitField("Add Subject")

class SubjectEditForm(FlaskForm):
    name = StringField(validators=[InputRequired(), Length(min=2, max=100)], render_kw={"placeholder": "Subject Name"})

    description = TextAreaField(validators=[DataRequired(), Length(min=4, max=100)], render_kw={"placeholder": "Subject Description"})

    submit = SubmitField("Edit Subject")

class ChapterForm(FlaskForm):
    name = StringField(validators=[InputRequired(), Length(min=2, max=100)], render_kw={"placeholder": "Chapter Name"})

    description = TextAreaField(validators=[DataRequired(), Length(min=4, max=100)], render_kw={"placeholder": "Chapter Description"})

    submit = SubmitField("Add Chapter")

class ChapterEditForm(FlaskForm):
    name = StringField(validators=[InputRequired(), Length(min=2, max=100)], render_kw={"placeholder": "Chapter Name"})

    description = TextAreaField(validators=[DataRequired(), Length(min=4, max=100)], render_kw={"placeholder": "Chapter Description"})

    submit = SubmitField("Edit Chapter")

class QuizForm(FlaskForm):
    name = StringField("Quiz Name", validators=[DataRequired()])

    subject = SelectField("Subject", choices=[], validators=[DataRequired()], validate_choice=False)
    
    chapter = SelectField("Chapter", choices=[], validators=[DataRequired()], validate_choice=False)

    date = DateField("Date of Quiz", format="%Y-%m-%d", validators=[DataRequired()])

    time_limit_hours = SelectField("Hours", choices=[(str(i), str(i)) for i in range(0, 6)], validators=[DataRequired()])
    time_limit_minutes = SelectField("Minutes", choices=[("00", "00"),("05", "05"),("10", "10"),("15", "15"),("20", "20"), ("25", "25"), ("30", "30"), ("35", "35"),("40", "40"),("45", "45"),("50", "50"),("55", "55"),], validators=[DataRequired()])


    submit = SubmitField("Add Quiz")

    def validate_date(self, field):
        if field.data < date.today():
            raise ValidationError("Due date cannot be in the past.")

class QuizEditForm(FlaskForm):
    name = StringField("Quiz Name", validators=[DataRequired()])

    date = DateField("Date of Quiz", format="%Y-%m-%d", validators=[DataRequired()])

    time_limit_hours = SelectField("Hours", choices=[(str(i), str(i)) for i in range(0, 6)], validators=[DataRequired()])
    time_limit_minutes = SelectField("Minutes", choices=[("00", "00"),("05", "05"),("10", "10"),("15", "15"),("20", "20"), ("25", "25"), ("30", "30"), ("35", "35"),("40", "40"),("45", "45"),("50", "50"),("55", "55"),], validators=[DataRequired()])

    submit = SubmitField("Edit Quiz")

    def validate_date(self, field):
        if field.data < date.today():
            raise ValidationError("Date of Quiz cannot be in the past.")   

class QuestionForm(FlaskForm):
    name = TextAreaField("Question", validators=[DataRequired()])

    option_1 = StringField("Option 1", validators=[DataRequired()])
    
    option_2 = StringField("Option 2", validators=[DataRequired()])
    
    option_3 = StringField("Option 3", validators=[DataRequired()])
    
    option_4 = StringField("Option 4", validators=[DataRequired()])
    
    correct_answer = SelectField("Correct Answer", choices=[
        ("1", "Option 1"), 
        ("2", "Option 2"), 
        ("3", "Option 3"), 
        ("4", "Option 4")
    ], validators=[DataRequired()])
    
    submit = SubmitField("Add Question")

class QuestionEditForm(FlaskForm):
    name = TextAreaField("Question", validators=[DataRequired()])

    option_1 = StringField("Option 1", validators=[DataRequired()])
    
    option_2 = StringField("Option 2", validators=[DataRequired()])
    
    option_3 = StringField("Option 3", validators=[DataRequired()])
    
    option_4 = StringField("Option 4", validators=[DataRequired()])
    
    correct_answer = SelectField("Correct Answer", choices=[
        ("1", "Option 1"), 
        ("2", "Option 2"), 
        ("3", "Option 3"), 
        ("4", "Option 4")
    ], validators=[DataRequired()])
    
    submit = SubmitField("Edit Question")

class DeleteForm(FlaskForm):
    submit = SubmitField('Delete')



# All admin routes 

#dashboard
@admin.route('/admin-dashboard', methods=['GET','POST'])
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('You do not have access to this page.', 'error')
        return redirect(url_for('user.user_dashboard'))
    
    subjectForm = SubjectForm()
    chapterForm = ChapterForm()
    deleteForm=DeleteForm()
    chapterEditForm = ChapterEditForm()
    subjectEditForm = SubjectEditForm()


    subs = Subject.query.all()
    chaps = Chapter.query.all()

    heading="Subjects and Chapters"
    return render_template("admin.html",subjectForm=subjectForm, subjects=subs, chapters= chaps, chapterForm=chapterForm, deleteForm=deleteForm, chapterEditForm=chapterEditForm, subjectEditForm=subjectEditForm, heading=heading)


# Subjects

@admin.route("/add-subject", methods=["POST", "GET"])
def add_subject():
    form = SubjectForm()
    if form.validate_on_submit():
        existing_sub = Subject.query.filter_by(name=form.name.data).first()
        if existing_sub:
            flash("Subject name already exists. Use a different name.", "error")
            return redirect(url_for("admin.admin_dashboard"))
        new_sub = Subject(
            name=form.name.data, 
            description=form.description.data
        )
        db.session.add(new_sub)
        db.session.commit()
        
        flash("Subject added successfully!", "success")
        return redirect(url_for("admin.admin_dashboard"))

    heading="Subjects and Chapters"
    flash("Subject addition failed. Try Again.", "error")
    return render_template("admin.html", subjectForm=form, heading=heading) 


@admin.route('/delete-subject/<subject_id>', methods=['POST'])
@login_required
def delete_subject(subject_id):
    
    if not current_user.is_admin:
        flash("Unauthorized access!", "error")
        return redirect(url_for("user.user_dashboard"))
    subject = Subject.query.filter_by(id=subject_id).first()
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted successfully!', 'success')
    return redirect(url_for("admin.admin_dashboard")) 


@admin.route('/edit_subject/<int:subject_id>', methods=['GET', 'POST'])
def edit_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    subjectEditForm=SubjectEditForm()
    if request.method == 'POST':
        if subjectEditForm.validate_on_submit():
            subject.name = subjectEditForm.name.data
            subject.description = subjectEditForm.description.data
            db.session.commit()
            flash('Subject editted successfully!', 'success')
        else:
            flash('Subject editting unsuccessfull!', 'error')

    return redirect(url_for('admin.admin_dashboard')) 

# Chapters

@admin.route("/add-chapter/<int:subject_id>", methods=["POST"])
@login_required
def add_chapter(subject_id):
    if not current_user.is_admin:
        flash("Unauthorized access!", "error")
        return redirect(url_for("user.user_dashboard"))

    subject = Subject.query.get(subject_id)
    
    if not subject:
        flash("Subject not found.", "error")
        return redirect(url_for("admin.admin_dashboard"))

    form = ChapterForm()

    if form.validate_on_submit():
        existing_chap = Chapter.query.filter_by(name=form.name.data).first()
        if existing_chap:
            flash("Chapter name already exists. Use a different name.", "error")
            return redirect(url_for("admin.admin_dashboard"))
        
        new_chapter = Chapter(
            name=form.name.data,
            description=form.description.data,
            subject_id=subject_id
        )
        db.session.add(new_chapter)
        db.session.commit()
        flash("Chapter added successfully!", "success")
    else:
        flash("Error while adding chapter. Check inputs.", "error")

    return redirect(url_for("admin.admin_dashboard"))



@admin.route('/delete-chapter/<chapter_id>', methods=['POST'])
@login_required
def delete_chapter(chapter_id):
    
    if not current_user.is_admin:
        flash("Unauthorized access!", "error")
        return redirect(url_for("user.user_dashboard"))
    chapter = Chapter.query.filter_by(id=chapter_id).first()
    db.session.delete(chapter)
    db.session.commit()
    flash('Chapter deleted successfully!', 'success')
    return redirect(url_for("admin.admin_dashboard"))  


@admin.route('/edit_chapter/<int:chapter_id>', methods=['GET', 'POST'])
def edit_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    
    chapterEditForm=ChapterEditForm()
    if request.method == 'POST':
        if chapterEditForm.validate_on_submit():
            chapter.name = chapterEditForm.name.data
            chapter.description = chapterEditForm.description.data
            db.session.commit()
            flash('Chapter editted successfully!', 'success')
        else:
            flash('Chapter editting unsuccessfull!', 'error')

    return redirect(url_for('admin.admin_dashboard')) 


# Quizes Page

@admin.route('/admin-quizzes', methods=['GET','POST'])
@login_required
def admin_quizzes() :
    if not current_user.is_admin:
        flash('You do not have access to this page.', 'error')
        return redirect(url_for('user.user_dashboard'))
    
    quizForm = QuizForm()
    questionForm = QuestionForm()
    subjectForm=SubjectForm()
    deleteForm=DeleteForm()
    questionEditForm= QuestionEditForm()
    quizEditForm= QuizEditForm()

    quizzes = Quiz.query.all()
    subjects = Subject.query.all()
    chapters = Chapter.query.all()
    questions = Question.query.all()
    
    quizForm.subject.choices = [(subject.id, subject.name) for subject in subjects]

    chapters_by_subject = {}
    for chapter in chapters:
        if chapter.subject_id not in chapters_by_subject:
            chapters_by_subject[chapter.subject_id] = []
        chapters_by_subject[chapter.subject_id].append((chapter.id, chapter.name))

    heading="Quizzes"

    return render_template("admin_quizzes.html",quizForm=quizForm, subjectForm=subjectForm, quizzes=quizzes, subjects= subjects,questionForm=questionForm, questions=questions, deleteForm=deleteForm, chapters_by_subject=chapters_by_subject, questionEditForm=questionEditForm, quizEditForm=quizEditForm, heading=heading)

#quizzes

@admin.route('/add-quiz', methods=['GET','POST'])
@login_required
def add_quiz():
    form = QuizForm()
    if form.validate_on_submit():
        time_limit = (int(form.time_limit_hours.data) * 60) + int(form.time_limit_minutes.data)

        new_quiz = Quiz(
            name=form.name.data, 
            chapter_id=form.chapter.data,
            date=form.date.data,
            time_limit=time_limit
        )
        db.session.add(new_quiz)
        db.session.commit()
        flash("Quiz added successfully!", "success")
    else:
        flash("Error while adding quiz. Check inputs.", "error")
    return redirect(url_for("admin.admin_quizzes"))


@admin.route('/delete-quiz/<quiz_id>', methods=['POST'])
@login_required
def delete_quiz(quiz_id):
    if not current_user.is_admin:
        flash("Unauthorized access!", "error")
        return redirect(url_for("admin.user_quizzes"))
    
    Question.query.filter_by(quiz_id=quiz_id).delete()
    db.session.commit()
    quiz = Quiz.query.filter_by(id=quiz_id).first()
    db.session.delete(quiz)
    db.session.commit()

    flash('Quiz deleted successfully!', 'success')
    return redirect(url_for("admin.admin_quizzes")) 


@admin.route('/edit-quiz/<int:quiz_id>', methods=['GET','POST'])
@login_required
def edit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    form = QuizEditForm()

    if form.validate_on_submit():        
        quiz.date=form.date.data
        quiz.time_limit = (int(form.time_limit_hours.data) * 60) + int(form.time_limit_minutes.data)
        quiz.name=form.name.data
        db.session.commit()
        flash("Quiz added successfully!", "success")

    else:
        flash("Error while adding quiz. Check inputs.", "error")

    return redirect(url_for("admin.admin_quizzes"))


# Questions 

@admin.route("/add-question/<int:quiz_id>", methods=["POST"])
@login_required
def add_question(quiz_id):
    if not current_user.is_admin:
        flash("Unauthorized access!", "error")
        return redirect(url_for("user.user_dashboard"))

    form = QuestionForm()

    if form.validate_on_submit():
        existing_question = Question.query.filter_by(question=form.name.data, quiz_id=quiz_id).first()
        if existing_question:
            flash("Question already exists. Use a different name.", "error")
            return redirect(url_for("admin.admin_quizzes"))
        
        new_question = Question(question=form.name.data,choice_A=form.option_1.data, choice_B=form.option_2.data,choice_C=form.option_3.data, choice_D=form.option_4.data, correct_answer = form.correct_answer.data, quiz_id = quiz_id)
        db.session.add(new_question)
        db.session.commit()
        flash("Question added successfully!", "success")

    else:
        print(form.errors)
        flash("Error while adding question. Check inputs.", "error")

    return redirect(url_for("admin.admin_quizzes"))



@admin.route('/delete-question/<question_id>', methods=['POST'])
@login_required
def delete_question(question_id):
    if not current_user.is_admin:
        flash("Unauthorized access!", "error")
        return redirect(url_for("admin.user_quizzes"))
    
    question = Question.query.filter_by(id=question_id).first()
    db.session.delete(question)
    db.session.commit()

    flash('Question deleted successfully!', 'success')

    return redirect(url_for("admin.admin_quizzes")) 

@admin.route('/edit_question/<int:question_id>', methods=['GET', 'POST'])
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)
    
    questionEditForm=QuestionEditForm()

    if request.method == 'POST':

        if questionEditForm.validate_on_submit():
            question.question = questionEditForm.name.data
            question.option_A = questionEditForm.option_1.data
            question.option_B = questionEditForm.option_2.data
            question.option_C = questionEditForm.option_3.data
            question.option_D = questionEditForm.option_4.data
            question.correct_answer = questionEditForm.correct_answer.data
            db.session.commit()
            flash('Question editted successfully!', 'success')

        else:
            flash('Question editting unsuccessfull!', 'error')

    return redirect(url_for('admin.admin_quizzes')) 


# users page 
    
@admin.route('/admin-users', methods=['GET','POST'])
@login_required
def admin_users():
    if not current_user.is_admin:
        flash('You do not have access to this page.', 'error')
        return redirect(url_for('user.user_dashboard'))
    
    users = User.query.filter_by(is_admin=False)
    user_attempts = {}
    heading="Users"

    for user in users:
        attempted_quizzes = db.session.query(Quiz.name,Quiz.id, Score.score, db.func.count(Question.id).label("total_questions")).join(Score, Score.quiz_id == Quiz.id).join(Question, Question.quiz_id == Quiz.id).filter(Score.user_id == user.id).group_by(Quiz.id, Score.score).all()
        user_attempts[user.id] = attempted_quizzes
        
    return render_template("admin_users.html", users=users, user_attempts=user_attempts, heading=heading)


# route for admin to view user quiez attempts


@admin.route('/quiz-result/<int:quiz_id>/<int:user_id>',  methods=['GET','POST'])
@login_required
def admin_quiz_result(quiz_id,user_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz.id).all()
    user_answers = Answers.query.filter_by(user_id=user_id).all()
    score_entry = Score.query.filter_by(user_id = user_id, quiz_id= quiz_id).first()

    if score_entry:
        score = score_entry.score

    total_questions = len(questions)
    results =[]

    for question in questions:
        for ans in user_answers:
            if ans.question_id == question.id:
                user_answer = ans.selected_answer 
        
        is_correct = (user_answer == question.correct_answer)

        results.append((question, user_answer, is_correct))
        
    return render_template('admin_quiz_result.html', quiz=quiz, results=results, score=score, total_questions=total_questions,button_text='Go Back')

