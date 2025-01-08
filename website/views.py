from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from . import db
import json
from .models import Question

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return render_template("home.html", user=current_user)

@views.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
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