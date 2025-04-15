from .database import db
from flask_login import UserMixin

# defining diff tables along with option for cascading deletes

class User(db.Model, UserMixin):
    id=db.Column(db.Integer, primary_key=True, autoincrement=True )
    email= db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255),nullable=False)
    username = db.Column(db.String(50) , nullable=False)
    is_admin = db.Column(db.Boolean,default=False, nullable=False)

    scores =db.relationship("Score", backref="user", cascade="all,  delete-orphan", passive_deletes=True)
    answers =db.relationship( "Answers", backref="user", cascade="all, delete-orphan", passive_deletes=True)


class Subject( db.Model):
    id = db.Column( db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50) , unique= True, nullable=False)
    description = db.Column(db.String(100),nullable=False)

    chapter =db.relationship('Chapter', backref='subject', cascade="all, delete-orphan", passive_deletes=True)


class Chapter(db.Model):
    id =db.Column(db.Integer, primary_key=True, autoincrement=True)
    name =db.Column(db.String(50), nullable=False)
    description =db.Column(db.String(100), nullable=False)
    subject_id =db.Column(db.Integer, db.ForeignKey('subject.id', ondelete="CASCADE"), nullable=False)

    quiz =db.relationship('Quiz', backref='chapter', cascade="all, delete-orphan", passive_deletes=True)


class Quiz(db.Model):
    id= db.Column(db.Integer, primary_key=True, autoincrement=True)
    name= db.Column(db.String(50), nullable=False)
    chapter_id= db.Column(db.Integer, db.ForeignKey('chapter.id', ondelete="CASCADE"), nullable=False)
    date= db.Column(db.Date, nullable=False, default=db.func.current_date)
    time_limit= db.Column(db.Integer, nullable= False, default=15)

    question =db.relationship("Question",backref='quiz', cascade="all, delete-orphan", passive_deletes=True)
    scores =db.relationship("Score", backref="quiz", cascade="all, delete-orphan", passive_deletes=True)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question = db.Column(db.String(500),nullable=False)
    choice_A =db.Column(db.String(100) , nullable=False)
    choice_B =db.Column(db.String(100),nullable=False)
    choice_C =db.Column(db.String(100),nullable=False)
    choice_D =db.Column(db.String(100),nullable=False)
    correct_answer = db.Column(db.String(1),nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete="CASCADE"),nullable=False)

    answers =db.relationship("Answers", backref="question", cascade="all, delete-orphan", passive_deletes=True)



class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    score = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False )
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete="CASCADE"), nullable=False )


class Answers(db.Model):
    id= db.Column(db.Integer, primary_key=True, autoincrement=True )
    user_id= db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    question_id= db.Column(db.Integer, db.ForeignKey('question.id', ondelete="CASCADE"), nullable=False )
    selected_answer= db.Column(db.String(1), nullable=True)
