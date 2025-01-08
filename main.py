from website import create_app, db
from website.models import Question

app = create_app()
with app.app_context():
    question1 = Question(
        question="What is the capital of France?",
        option_1="Paris",
        option_2="London",
        option_3="Berlin",
        option_4="Madrid",
        correct_option=1
    )
    question2 = Question(
        question="What is 2 + 2?",
        option_1="3",
        option_2="4",
        option_3="5",
        option_4="6",
        correct_option=2
    )
    db.session.add(question1)
    db.session.add(question2)
    db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)