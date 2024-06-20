import json
import typing
import peewee
from peewee import fn
from db.database import db, User, Book, Tierlist, Rank, Guild, BannedUser

class DataHandler:
    def __init__(self):
        pass 

    async def printer(self, param):
        print(f"type: {type(param)}, value: {param}")
              
    async def get_user(self, user_disc_id:int, guild_disc_id:int):
        with db.atomic():
            try:
                user = (User.select().join(Guild, on=(User.guild_id == Guild.guild_id)).where((User.user_disc_id == user_disc_id) & (Guild.guild_disc_id == guild_disc_id)).get())
                return user.user_id
            except User.DoesNotExist:
                return None
        
    async def create_user(self,user_disc_id,guild_id) -> int:
        with db.atomic():
            user = User.create(user_disc_id = user_disc_id, guild_id = guild_id)        
            return user.user_id

    
    async def get_guild(self, guild_disc_id: int) -> int|None:
        try:
            with db.atomic():
                guild = Guild.get(Guild.guild_disc_id==guild_disc_id)
                return guild.guild_id
        except Guild.DoesNotExist:
            return None
        
    async def create_guild(self, guild_disc_id):
        with db.atomic():
            guild = Guild.create(guild_disc_id=guild_disc_id)
            return guild.guild_id

    async def get_book(self, book_name: str, guild_id: int):
        try:
            with db.atomic():
                book = Book.get(Book.book_name == book_name, Book.guild_id == guild_id)
                return book.book_id
        except Book.DoesNotExist:
            return None

    async def create_book(self, book_name:str, guild_id: int):
        book = Book.create(book_name = book_name, guild_id = guild_id)
        return book.book_id
    
    async def get_tierlist(self, user_id: int, book_id: int, guild_id: int):
        with db.atomic():
            try:
                Tierlist.get(Tierlist.book_id == book_id,
                              Tierlist.user_id == user_id,
                              Tierlist.guild_id == guild_id)
                return Tierlist
            except Tierlist.DoesNotExist:
                return None
                

    async def create_tierlist(self, user_id, book_id,guild_id,rank):
        with db.atomic():
            position = await self.get_last_position(user_id, guild_id, rank)
            Tierlist.create(book_id = book_id,
                                    user_id = user_id,
                                    guild_id = guild_id,
                                    rank_id =  rank,
                                    position = position)
            await self.alter_times_in_tierlist(book_id,guild_id,1)
        

    async def get_book_in_tierlist(self, user_id:int, guild_id:int, book_name: str,tier:typing.Optional[int]=None):
        try:
            with db.atomic():
                book = (Tierlist.select().join(Book).where(Tierlist.guild_id == guild_id,Tierlist.user_id == user_id,Book.book_name == book_name).get())

                # else:
                #     book = Tierlist.select().join(Book).where(Tierlist.guild_id == guild_id, Tierlist.user_id == user_id, Book.book_name == book_name).get()
                await self.printer(book)
                return book
        except Tierlist.DoesNotExist:
            print('book not found')
            return None 
        

        
    async def get_last_position(self, user_id: int, guild_id: int, rank:int) -> int:
        with db.atomic():
            position_number = 0
            try:
                last_position = (Tierlist.select().where(Tierlist.user_id == user_id,Tierlist.rank_id == rank,Tierlist.guild_id == guild_id).order_by(Tierlist.position.desc()).limit(1)).first()
                if last_position:
                    position_number = last_position.position
            except Exception as e:
                position_number = 0
                print(f'       !!!Error!!!:\n\n{e}\n\n!!!Error!!!')
            return position_number + 1
        
    async def get_list_of_guild_books(self, guild_id: int):
        with db.atomic():
            book_list = Book.select(Book.book_name, Book.times_in_tierlist).where(Book.guild_id == guild_id).order_by(Book.times_in_tierlist.desc())
            guild_books = []
            for book in book_list:
                guild_books.append(book.book_name)
        return guild_books

    async def get_user_books_per_guild(self, guild_id: int, user_id: int):
        with db.atomic():
            user_books = []
            user_book_list = (Book.select(Book.book_name).join(Tierlist).where(Tierlist.guild_id == guild_id, Tierlist.user_id == user_id))

            for book in user_book_list:
                user_books.append(book.book_name)
        return user_books

    async def remove_book_from_tierlist(self, name:str, user_id: int, guild_id: int):
        book = await self.get_book_in_tierlist(user_id,guild_id, name)
        print('o book existe?',book)
        if book is None:
            print('nao')
            return False
        with db.atomic():
            # Update positions of other books
            await self.update_deleted_position(book.position,user_id, guild_id)
            print('posições alteradas')
            # Delete the book from the tier list
            Tierlist.delete().where(Tierlist.book_id == book.book_id, Tierlist.user_id == user_id, Tierlist.guild_id == guild_id).execute()
            print('livro deletado')
            # Alter times in the tier list
            await self.alter_times_in_tierlist(book.book_id, guild_id, -1)
            print('alterado as vezes que o livro aparece na tierlist')
            print("Book removed successfully from the tier list.")
            return True
        
    async def remove_book_from_guild(self, name:str, guild_id: int):
        try:
            with db.atomic():
                book = Book.get(Book.book_name == name, Book.guild_id == guild_id)
                
                if not book:
                    print('book not found')
                    return False
                users_with_book = Tierlist.select().join(Book).where(Book.book_name == name)
                print('book found')
                for user in users_with_book:
                    print('hi')
                    book_position = Tierlist.select().join(Book).where(Tierlist.user_id == user.user_id,Book.book_name == name).get()
                    print(f'User: {user.user_id}, book name: {name}')
                    await self.update_deleted_position(book_position.position,user.user_id, guild_id)
                    print('update deleted position successfully')
                    Tierlist.delete().where(Tierlist.book_id == book.book_id, Tierlist.user_id == user.user_id, Tierlist.guild_id == guild_id).execute()
                    print(f'deleted from {user.user_id} tierlist successfully')
                Book.delete().where(Book.book_name == name).execute()
                return True
        except Exception as e:
            print(e)
            return False


    async def update_deleted_position(self, removed_position, user_id, guild_id):
        try:
            with db.atomic():
                    # Update positions of books with higher positions
                    Tierlist.update(position = Tierlist.position - 1).where((Tierlist.position > removed_position) & (Tierlist.user_id == user_id, Tierlist.guild_id == guild_id)).execute()
                    print(f"Updated positions for books with position > {removed_position}.")
        except Exception as e:
            print(f"An error occurred while updating positions: {e}")

    async def alter_times_in_tierlist(self, book_id:int ,guild_id:int , value:int):
        with db.atomic():
            book_count = (Tierlist.select().join(Book).where(Tierlist.guild_id == guild_id, Book.book_id == book_id).count())

            if (book_count + value) <= 0:
                Book.delete().where(Book.book_id== book_id, Book.guild_id == guild_id).execute()
                print('BOOK DELETED: Book was DELETED from Book Table.\nseriously.')
            else:
                Book.update(times_in_tierlist = book_count).where(Book. book_id==book_id, Book.guild_id == guild_id).execute()
                print('Book times in tierlist has been updated')

    async def show_tierlist_entries(self, user_id: int, guild_id: int):
        with db.atomic():
            tierlist_ranks = {'Rank S': [], 'Rank A': [], 'Rank B': [], 'Rank C': [], 'Rank D': [], 'Rank E': []}

            user_entries = (Tierlist
                 .select()
                 .join(Rank, on=(Tierlist.rank_id == Rank.rank_id))
                 .join(Book, on=(Tierlist.book_id == Book.book_id))
                 .join(Guild, on=(Tierlist.guild_id == Guild.guild_id))
                 .join(User, on=(Tierlist.user_id == User.user_id))
                 .where(Tierlist.guild_id == guild_id , Tierlist.user_id == user_id).order_by(Tierlist.position))

            for tierlist in user_entries:
                tier_rank = tierlist.rank_id.rank
                tierlist_ranks[tier_rank].append(tierlist.book_id.book_name)

            return tierlist_ranks
        
    async def tierlist_swap_positions(self, user_id: int, guild_id: int, first_book: str, second_book: str,tier:int):
        with db.atomic():
            print(f'Getting books position of User {user_id} in Guild {guild_id}')
            # Fetch the book positions
            first_novel = await self.get_book_in_tierlist(user_id, guild_id, first_book, tier)
            second_novel = await self.get_book_in_tierlist(user_id, guild_id, second_book,tier)
            print(first_novel.book_id,second_novel.book_id,'>')
            if first_novel is None or second_novel is None:
                print('One or more books doesn\'t exist')
                return False
            
            # Check if both books are in the same rank
            if first_novel.rank_id != second_novel.rank_id:
                print('Books are in different ranks! Returning false')
                return False            
            print(f'First book: {first_novel.book_id.book_name}, Rank: {first_novel.rank_id}, Position: {first_novel.position}')
            print(f'Second book: {second_novel.book_id.book_name}, Rank: {second_novel.rank_id}, Position: {second_novel.position}')
            
            # Update positions
            print('Books are the same rank.')
            
            update_first = (Tierlist
                            .update({Tierlist.position: second_novel.position})
                            .where(Tierlist.user_id == user_id, 
                                Tierlist.guild_id == guild_id, 
                                Tierlist.book_id == first_novel.book_id))
            
            update_second = (Tierlist
                            .update({Tierlist.position: first_novel.position})
                            .where(Tierlist.user_id == user_id, 
                                    Tierlist.guild_id == guild_id, 
                                    Tierlist.book_id == second_novel.book_id))
            
            # Execute the updates
            update_first.execute()
            update_second.execute()
            
            print('tierlist_swap_positions executed successfully. Returning true.')
            return True

    async def get_banned_users(self, user_id, guild_id):
        with db.atomic():
            try:
                user = BannedUser.select().where(BannedUser.user_id == user_id, BannedUser.guild_id == guild_id).get()
                if user:
                    return True
                else:
                    return False
            except Exception as e:
                print('erro em ver um usuario banido: ',e)

    async def create_banned_user(self, user_id, guild_id):
        with db.atomic():
            try:
                BannedUser.create(user_id=user_id, guild_id=guild_id)
                return True
            except Exception as e:
                print('erro em criar um usuario banido: ',e)
                return False

    async def delete_banned_user(self, user_id, guild_id):
        with db.atomic():
            try:
                print(f'o usuario a ser desbanido é {user_id}')
                BannedUser.delete().where(BannedUser.user_id == user_id, BannedUser.guild_id == guild_id).execute()
                return True
            except Exception as e:
                print('erro em remover um usuario banido: ',e)
                return False