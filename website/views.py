from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, session
from flask_login import login_required, current_user
from . import db
import json
import random
import requests
import html
from .models import Question, Score, User
from sqlalchemy import func

views = Blueprint('views', __name__)

def fetch_questions():
    """fetch questions using opentdb API"""
    Question.query.delete()
    db.session.commit()
    
    response = requests.get('https://opentdb.com/api.php?amount=10&type=multiple')
    data = response.json()
    
    if data['response_code'] == 0: 
        questions = []
        for question in data['results']:
            questions.append(question)
        
        for q in data['results']:
            question_text = html.unescape(q['question'])
            correct_answer = html.unescape(q['correct_answer'])
            incorrect_answers = [html.unescape(ans) for ans in q['incorrect_answers']]
            
            options = incorrect_answers + [correct_answer]
            for _ in range(len(options) * 2):  
                i, j = random.randint(0, len(options) - 1), random.randint(0, len(options) - 1)
                options[i], options[j] = options[j], options[i]
            
            correct_option_index = options.index(correct_answer) + 1  

            question = Question(
                question=question_text,
                option_1=options[0],
                option_2=options[1],
                option_3=options[2],
                option_4=options[3],
                correct_option=correct_option_index 
            )
            db.session.add(question)
    
    db.session.commit()

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    """home page"""
    return render_template("home.html", user=current_user)

@views.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    """quiz page"""
    if request.method == 'GET':
        fetch_questions()
    questions = Question.query.all()

    if request.method == 'POST':
        score = 0
        total = len(questions)
        user_answers = []
        for question in questions:
            user_answer = request.form.get(f"question{question.id}")
            selected_option = None
            if user_answer:
                selected_option = getattr(question, f'option_{user_answer}')
            correct_option = getattr(question, f'option_{question.correct_option}')
            is_correct = user_answer and int(user_answer) == question.correct_option

            if is_correct:
                score += 1

            # Add question and answer details to the user's answer list
            user_answers.append({
                'question': question.question,
                'user_answer': selected_option,
                'correct_answer': correct_option,
                'is_correct': is_correct
            })

        

        new_score = Score(
            score=score,
            total_questions=total,
            user_id=current_user.id
        )
        db.session.add(new_score)
        db.session.commit()

        session['last_quiz_answers'] = user_answers

        flash(f'You scored {score} out of {len(questions)}!', category='success')
        return redirect(url_for('views.results', score=score, total=len(questions))) 

    return render_template("quiz.html", questions=questions)

@views.route('/results')
@login_required
def results():
    """results page"""
    try:
        raw_score = request.args.get('score')
        if raw_score is not None:  
            score = int(raw_score)  
        else:
            score = None
        raw_total = request.args.get('total')  
        if raw_total is not None:  
            total = int(raw_total)  
        else:
            total = None

        if score is None or total is None:
            return redirect(url_for('views.home'))
    
        user_stats = db.session.query(
            func.avg(Score.score * 100.0 / Score.total_questions).label('average'),
            func.count(Score.id).label('attempts')
        ).filter_by(user_id=current_user.id).first()
    

        leaderboard = db.session.query(
            User.first_name,
            func.avg(Score.score * 100.0 / Score.total_questions).label('average'),
            func.count(Score.id).label('attempts')
        ).join(Score).group_by(User.id).order_by(
            func.avg(Score.score * 100.0 / Score.total_questions).desc()
        ).limit(10).all()
    
        return render_template(
            "results.html",
            score=score,
            total=total,
            user=current_user,
            average=user_stats.average if user_stats.average else 0,
            attempts=user_stats.attempts,
            leaderboard=leaderboard
        ) 
    except AttributeError:
        flash('No quiz results found.', 'error')
        return redirect(url_for('views.home'))  
    except KeyError as e:
        flash('No quiz results found.', 'error')
        return redirect(url_for('views.home'))
    except Exception as e:
        flash('An error occurred.', 'error')
        return redirect(url_for('views.home'))


@views.route('/review')
@login_required
def review():
    """review page"""
    try:
        answers = session.get('last_quiz_answers')
        if not answers:
            flash('No quiz results to review.', 'error')
            return redirect(url_for('views.home'))
    
        return render_template('review.html', answers=answers, user=current_user)
    except Exception as e:
        flash('An error occurred.', 'error')
        return redirect(url_for('views.home'))

@views.route('/blog')
@login_required
def blog():
    """blog page"""
    return render_template("blog.html", user=current_user)

@views.route('/contact')
@login_required
def contact():
    """contact page"""
    return render_template('contact_us.html')