from flask import Flask
from app import create_app
from app.routes import visit

app = create_app()

from app.models import User
# def print_user(id):
    # with app.app_context():

    #     user = User.query.get(1)
    #     user = User.query.filter_by(email = "demo@example.com").first()
    #     print(user)
        
    #     print(user.name)

# print_user(1)

app.register_blueprint(visit)

if __name__=="__main__":
    app.run(debug=True,port=5000)
