from website import create_app, db
from website.models import Question

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)