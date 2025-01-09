from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from . import db
import json
import random
import requests
import html
from .models import Question

views = Blueprint('views', __name__)

def fetch_questions():
    Question.query.delete()
    db.session.commit()
    
    response = requests.get('https://opentdb.com/api.php?amount=10&type=multiple')
    data = response.json()
    
    if data['response_code'] == 0: 
        for q in data['results']:
            question_text = html.unescape(q['question'])
            correct_answer = html.unescape(q['correct_answer'])
            incorrect_answers = [html.unescape(ans) for ans in q['incorrect_answers']]
            
            options = incorrect_answers + [correct_answer]
            random.shuffle(options)
            
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
    return render_template("home.html", user=current_user)

@views.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    if request.method == 'GET':
        fetch_questions()
    questions = Question.query.all()

    if request.method == 'POST':
        score = 0
        for question in questions:
            user_answer = request.form.get(f"question{question.id}")
            if user_answer and int(user_answer) == question.correct_option:
                score += 1
        flash(f'You scored {score} out of {len(questions)}!', category='success')
        return redirect(url_for('views.results', score=score, total=len(questions))) 

    return render_template("quiz.html", questions=questions)

@views.route('/results')
@login_required
def results():
    score = request.args.get('score', type=int)
    total = request.args.get('total', type=int)

    return render_template("results.html", score=score, total=total)