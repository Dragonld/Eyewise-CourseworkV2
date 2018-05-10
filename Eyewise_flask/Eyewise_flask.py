# analysis of missed and empty appointments and profitability(appointments compared to money spent)
# link to google api calander and send out automated email
from app import app, db
from app.models import User, Post


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Post': Post
    }


# if __name__ == "__main__":
#     app.run()

if __name__ == "__main__":
    app.run(host="0.0.0.0")
