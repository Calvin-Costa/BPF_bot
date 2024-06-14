from peewee import *
from playhouse.migrate import *
"""A variável db recebe a classe SqliteDatabase do peewee que cria 
um banco de dados SQL"""
db = SqliteDatabase('bot.db')

class BaseModel(Model):
    class Meta:
        database = db

class Rank(BaseModel):
    rank_id: AutoField = AutoField()
    rank: CharField = CharField(max_length=7)

class Guild(BaseModel):
    guild_id: AutoField = AutoField()
    guild_disc_id: IntegerField = IntegerField()

class User(BaseModel):
    user_id: AutoField = AutoField()
    user_disc_id = IntegerField()
    current_xp = FloatField(default=0)
    level = IntegerField(default=1)
    guild_id = ForeignKeyField(Guild,backref='guilds')

class Book(BaseModel):
    book_id = AutoField()
    book_name = TextField()
    times_in_tierlist = IntegerField(default=0)
    guild_id = ForeignKeyField(Guild, backref='guilds')

class Tierlist(BaseModel):
    tierlist_id: AutoField = AutoField()
    user_id: ForeignKeyField = ForeignKeyField(User,backref='users')
    book_id: ForeignKeyField =  ForeignKeyField(Book,backref='books')
    rank_id: ForeignKeyField = ForeignKeyField(Rank,backref='ranks')
    guild_id: ForeignKeyField = ForeignKeyField(Guild,backref='guilds')
    position: IntegerField = IntegerField(null=False)

db.create_tables([User, Book, Rank, Guild, Tierlist])

with db.atomic():
    Rank.get_or_create(rank='Rank S')
    Rank.get_or_create(rank='Rank A')
    Rank.get_or_create(rank='Rank B')
    Rank.get_or_create(rank='Rank C')
    Rank.get_or_create(rank='Rank D')
    Rank.get_or_create(rank='Rank E')

"""How to add a column:

(btw, don't forget to import playhouse)
from playhouse.migrate import *
"""
# migrator = SqliteMigrator(db)
# guild_id = IntegerField(null=True)
# with db.atomic():
#     migrate(migrator.drop_column('user','guild id', guild_id))
#     print('success')

# query = User.update(guild_id = 1).where(User.user_id == 1)
# query.execute()