
from models import db, User
from random import sample, randint
from app import app


db.drop_all()
db.create_all()

# names = [
#     ("John", "Doe"),
#     ("James", "Bond"),
#     ("Reese", "Witherspoon"),
#     ("Al", "Pacino"),
# ]

# for first, last in names:
#     user = User(first_name=first, last_name=last)
#     db.session.add(user)