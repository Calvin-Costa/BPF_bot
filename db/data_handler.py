import json
import peewee
from db.database import db, User, Book, Tierlist, Rank, Guild, fn

class DataHandler:
    def __init__(self):
        pass 

    async def printer(self, param):
        print(f"type: {type(param)}, value: {param}")
              
    async def get_or_create_user_model(self, user_disc_id: int, guild_id: int):
        with db.atomic():
            user, _ = User.get_or_create(user_disc_id = user_disc_id, guild_id= guild_id)
            return user
        
    async def get_or_create_guild_model(self, guild_disc_id: int):
        with db.atomic():
            guild, _ = Guild.get_or_create(guild_disc_id = guild_disc_id)
            return guild.guild_id
        
    async def get_or_create_book_id(self,book_name:str, guild_id: int):
        with db.atomic():
            new_book = False
            try:
                book = Book.get(Book.guild_id == guild_id , fn.LOWER(Book.book_name) == book_name.lower())
            except Book.DoesNotExist:
                book_name = book_name.title()
                book = Book.create(book_name=book_name, guild_id=guild_id, times_in_tierlist=1)
                new_book = True
            print(book.book_id)
            return book.book_id, new_book  # Return book id

    async def get_or_create_tierlist_entry(self, user_id: int, book_id: int, rank: int, guild_id: int): #insert book entry into tier list
        with db.atomic():
            position = await self.get_last_position(user_id, guild_id, rank)
            print(position)
            print(user_id, book_id, guild_id)
            existing_tierlist = False
            try:
                tierlist = Tierlist.get(Tierlist.book_id == book_id, Tierlist.user_id == user_id, Tierlist.guild_id == guild_id)
            except Tierlist.DoesNotExist:
                tierlist = Tierlist.create(book_id = book_id, user_id = user_id, guild_id = guild_id , rank_id =  rank, position = position)
                existing_tierlist = True
            return existing_tierlist
        
    #pegar o rank pois a position é por rank!!!!
    async def get_last_position(self, user_id: int, guild_id: int, rank:int) -> int:
        try:
            position = Tierlist.select().where(Tierlist.user_id == user_id, Tierlist.guild_id == guild_id, Tierlist.rank_id == rank).order_by(Tierlist.position.desc()).get()
            position_number = position.position
            #Tierlist.select().where(Tierlist.user_id == user_id, Tierlist.guild_id == guild_id, Tierlist.rank_id == rank).order_by(Tierlist.position.desc()).get()
            #print(f"type: {type(position)}, value: {position}")
            
        except Exception as e:
            position_number = 0
            print(f'!!!!!!!!!!!!!!!Error!!!!!!!!!!!!!!!!!!!:\n\n {e}\n\n!!!!!!!!!!!!!!!Error!!!!!!!!!!!!!!!!!!!:')
        return position_number + 1
        
    # #nem tá sendo usada....?
    # async def get_tierlist_entry(self, user_id: int, book_id: int, guild_id: int):
    #     with db.atomic(): #checks if book is already in user tierliest
    #         book_in_tierlist = Tierlist.get_or_none(book_id=book_id,
    #                                                  user_id= user_id, guild_id=guild_id)
    #     return book_in_tierlist
    

    async def get_book_id(self,book_name:str, guild_id: int):
        with db.atomic():
            # Check if the book already exists
            existing_book = Book.get_or_none(book_name=book_name, guild_id=guild_id)
            if existing_book:
                return existing_book.book_id, True   #return book ID and that it exists
        return None, False  #Return nothing as book ID and False as it doesn't exist
                
    #vai ser chamada com o autocomplete... ironicamente incompleta por enquanto.
    async def get_books_in_guild(self, guild_id: int):
        with db.atomic():
            book_list = Book.select(Book.book_name, Book.times_in_tierlist).where(Book.guild_id == guild_id).order_by(Book.times_in_tierlist.desc())
            guild_books = []
            for book in book_list:
                guild_books.append(book.book_name)
        return guild_books

    async def get_user_books_per_guild(self, guild_id: int, user_id: int):
        with db.atomic():
            book_list = (Book.select(Book.book_name).join(Tierlist).where(Tierlist.guild_id == guild_id, Tierlist.user_id == user_id))
            #self.printer(book_list)
            user_books = []
            for book in book_list:
                user_books.append(book.book_name)
        return user_books


    async def remove_book_from_tierlist(self, book_id:int ,user_id: int, guild_id:int):
        with db.atomic():
            
            await self.update_deleted_position(book_id, user_id, guild_id)

            Tierlist.delete().where(Tierlist.book_id == book_id, Tierlist.user_id == user_id, Tierlist.guild_id == guild_id).execute()
            await self.alter_times_in_tierlist(book_id,guild_id,-1)

    async def update_deleted_position(self, book_id, user_id, guild_id):
        with db.atomic():
            removed_book = Tierlist.select().where(Tierlist.book_id == book_id, Tierlist.user_id == user_id, Tierlist.guild_id == guild_id).get()
            Tierlist.update(position = Tierlist.position - 1).where(Tierlist.position > removed_book.position).execute()

    async def alter_times_in_tierlist(self, book_id:int ,guild_id:int , value:int):
        with db.atomic():
            book_counter = Book.select(Book.times_in_tierlist).where(Book.book_id== book_id, Book.guild_id == guild_id).get()

            Book.update(times_in_tierlist = book_counter.times_in_tierlist + value).where(Book.book_id==book_id, Book.guild_id == guild_id).execute()

            if (book_counter.times_in_tierlist + value) == 0:
                Book.delete().where(Book.book_id== book_id, Book.guild_id == guild_id).execute()



    async def show_tierlist_entries(self, user_id: int, guild_id: int):
        with db.atomic():
            tierlist_ranks = {'Rank S': [], 'Rank A': [], 'Rank B': [], 'Rank C': [], 'Rank D': []}

            a = (Tierlist
                 .select()
                 .join(Rank, on=(Tierlist.rank_id == Rank.rank_id))
                 .join(Book, on=(Tierlist.book_id == Book.book_id))
                 .join(Guild, on=(Tierlist.guild_id == Guild.guild_id))
                 .join(User, on=(Tierlist.user_id == User.user_id))
                 .where(Tierlist.guild_id == guild_id , Tierlist.user_id == user_id).order_by(Tierlist.position))
            #print(a.sql())
            for tierlist in a:
                #print(tierlist.tierlist_id, tierlist.user_id, tierlist.book_id, tierlist.rank_id, tierlist.guild_id, tierlist.position)
                tier_rank = tierlist.rank_id.rank
                #print(tierlist)
                #print(f'User: {tierlist.user_id}, Guild: {tierlist.guild_id}, Name: {tierlist.book_id.book_name}')
                tierlist_ranks[tier_rank].append(tierlist.book_id.book_name)
            return tierlist_ranks
        
    async def tierlist_swap_positions(self, user_id: int, guild_id:int,first_book:str, second_book:str):
        
        with db.atomic():
            #get position of each book
            first_novel = await self.get_book(user_id, guild_id,first_book)
            second_novel = await self.get_book(user_id,guild_id,second_book)
            #print(f'type: {type(first_position)}, value: {first_position}')
            #print(f'type: {type(first_position)}, value: {first_position}')
            #get books id
            if first_novel.rank_id != second_novel.rank_id:
                return False
            #change position of first book:
            Tierlist.update(position = second_novel.position).where(Tierlist.user_id == user_id, Tierlist.guild_id == guild_id, Tierlist.book_id == first_novel.id).execute()
            #change position of second book:
            Tierlist.update(position = first_novel.position).where(Tierlist.user_id == user_id, Tierlist.guild_id == guild_id, Tierlist.book_id == second_novel.id).execute()
            return True

    async def get_book(self, user_id:int, guild_id:int, book_name: str):
        with db.atomic():
            book = Tierlist.select().join(Book).where(Tierlist.guild_id == guild_id, Tierlist.user_id == user_id, Book.book_name == book_name).get()
            return book