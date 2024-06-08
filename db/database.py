from peewee import *

"""A variável db recebe a classe SqliteDatabase do peewee que cria 
um banco de dados SQL"""
db = SqliteDatabase('bot.db')

class User(Model):
    user_id = IntegerField()
    current_xp = FloatField(default=0)
    level = IntegerField(default=1)
    