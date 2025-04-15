from flask import Blueprint, render_template, flash, redirect, url_for, request
from .models import User, Subject, Chapter, Quiz, Question, Score, Answers
from .database import db
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, Length, ValidationError, DataRequired
from wtforms import StringField, SubmitField, TextAreaField, SelectField, DateField
from flask_bcrypt import Bcrypt
from datetime import date, datetime, timedelta

user = Blueprint('user', __name__)
bcrypt = Bcrypt()

#user landing page

@user.route('/user-dashboard', methods=['GET','POST'])
@login_required
def user_dashboard():

    subjects = Subject.query.all()  
    availabe_quizzes = {}  
    upcoming_quizzes = {}  

    today = date.today() 

    for subject in subjects:
        todays_quizzes = (
            Quiz.query
            .join(Chapter)
            .filter(
                Chapter.subject_id == subject.id,
                Quiz.date == today,
                ~Quiz.id.in_(db.session.query(Score.quiz_id).filter_by(user_id=current_user.id)),  # Exclude attempted quizzes
                Quiz.id.in_(db.session.query(Question.quiz_id))
            ).all()
            )
        future_quizzes = (
            Quiz.query
            .join(Chapter)
            .filter(
                Chapter.subject_id == subject.id,
                Quiz.date > today,
                ~Quiz.id.in_(db.session.query(Score.quiz_id).filter_by(user_id=current_user.id)),  # Exclude attempted quizzes
                Quiz.id.in_(db.session.query(Question.quiz_id))
            ).all()
            )
        
        if todays_quizzes:  
            availabe_quizzes[subject] = todays_quizzes
        if future_quizzes:  
            upcoming_quizzes[subject] = future_quizzes
    heading="Available Subjects and Quizzes"
    return render_template('user.html', available_quizzes=availabe_quizzes, upcoming_quizzes = upcoming_quizzes, subjects=subjects, heading=heading)


# route to the quiz attempt page

@user.route('/take-quiz/<int:quiz_id>', methods=['GET','POST'])
@login_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz.id).all()
    total_questions = len(questions)

    if request.method == 'POST':
        score = 0
        results=[]
        for question in questions:
            user_answer = request.form.get(f'question_{question.id}')

            user_choice = Answers(
                user_id=current_user.id,
                question_id=question.id,
                selected_answer=user_answer
            )
            db.session.add(user_choice)
            if user_answer == question.correct_answer:
                is_correct = True
                score += 1
            else:
                is_correct=False
            results.append((question, user_answer, is_correct))
        new_score = Score(user_id=current_user.id, quiz_id=quiz.id, score=score)
        db.session.add(new_score)
        db.session.commit()

        return render_template('quiz_result.html', quiz=quiz, results=results,score=score ,total_questions=total_questions, button_text='Continue')
    

    return render_template('take_quiz.html', quiz=quiz, questions=questions , time_limit=quiz.time_limit)


#quiz_results routes

@user.route('/quiz-result/<int:quiz_id>',  methods=['GET','POST'])
@login_required
def quiz_result(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz.id).all()
    user_answers = Answers.query.filter_by(user_id=current_user.id).all()
    score_entry = Score.query.filter_by(user_id = current_user.id, quiz_id= quiz_id).first()
    if score_entry:
        score = score_entry.score
    total_questions = len(questions)
    results = []
    for question in questions:
        for ans in user_answers:
            if ans.question_id == question.id:
                user_answer = ans.selected_answer 
        
        is_correct = (user_answer == question.correct_answer)

        results.append((question, user_answer, is_correct))
    print(results)
    return render_template('quiz_result.html', quiz=quiz, results=results, score=score, total_questions=total_questions,button_text='Go Back')



#all result history of the user

@user.route('/user-result',  methods=['GET','POST'])
@login_required
def user_result():
    subjects = Subject.query.all()  
    subject_quizzes = {}  
    heading="Results"
    for subject in subjects:
        quizzes = (
            Quiz.query
            .join(Chapter)
            .filter(
                Chapter.subject_id == subject.id,
                Quiz.id.in_(db.session.query(Score.quiz_id).filter_by(user_id=current_user.id))  # Exclude attempted quizzes
            )
            .all())

        
        if quizzes:  
            subject_quizzes[subject] = quizzes

    return render_template('user_results.html', subject_quizzes=subject_quizzes, heading=heading)    


