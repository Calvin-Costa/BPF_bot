import peewee
from db.database import db, User, Book, Tierlist

db.connect()

db.create_tables([User,Book, Tierlist])

user = User.create(user_id = 1)