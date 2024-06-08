from peewee import *

"""A variável db recebe a classe SqliteDatabase do peewee que cria 
um banco de dados SQL"""
db = SqliteDatabase('bot.db')

class User(Model):
    user_id = IntegerField(primary_key=True)
    current_xp = FloatField(default=0)
    level = IntegerField(default=1)
    """ a próxima parte é importante pois com ela o peewee vai entender em qual db a tabela vai conversar"""
    class Meta:
        database = db

class Book(Model):
    book_id = IntegerField()
    book_name = TextField()
    times_in_tierlist = IntegerField()
    class Meta:
        database = db


class Tierlist(Model):
    tierlist_id: IntegerField()
    user_id: ForeignKeyField(User,backref='users')
    book_id: ForeignKeyField(Book,backref='books')
    tier_rank: CharField(max_length=7)
    class Meta:
        database = db
