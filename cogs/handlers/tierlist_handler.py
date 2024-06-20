import os
import logging
import titlecase
import typing

from discord import (Interaction,
                     Member, 
                     Embed, 
                     Color, 
                     SelectOption)
from discord.ui import Select
from thefuzz import fuzz
from thefuzz import process

from db.data_handler import DataHandler
from views.tierlist_views import TierlistViews, SelectMenuView

class TierlistHandler():
    def __init__(self) -> None:
        self.db = DataHandler()

    async def get_user_data(self, interaction:Interaction,user: typing.Optional[Member] = None) -> tuple[int]:
        guild_disc_id = interaction.guild.id
        user_disc_id=interaction.user.id
        if user:
            user_disc_id = user.id
        user_id = await self.db.get_user(user_disc_id, guild_disc_id)
        guild_id = await self.db.get_guild(guild_disc_id)
        if guild_id is None:
            guild_id = await self.db.create_guild(guild_disc_id)
        if user_id is None:
            user_id = await self.db.create_user(user_disc_id,guild_id)
        
        return user_id, guild_id

    async def add_novels_handler(self,interaction:Interaction,book_name:str, tier:int):
        if len(book_name) > 60:
            await interaction.response.send_message(f"That name was too long! It needs to be {len(book_name)-80} less characters!")
            return None
        user_id, guild_id = await self.get_user_data(interaction)
        book_name = await self.string_formatting(book_name)
        check_name = await self.name_check(book_name,guild_id)
        if len(check_name) > 1:
            await self.add_novels_selection(interaction,tier,guild_id,user_id,check_name)
        else:
            await self.add_novels(interaction,book_name,tier,guild_id,user_id)
        #view.add_item(SelectMenu(options))

    async def add_novels_selection(self,interaction:Interaction,tier,guild_id,user_id,check_name):
        options = []
        for name in check_name:
            options.append(SelectOption(label=name))
        view = SelectMenuView(options)
        await interaction.response.send_message("The name you sent is similar to one or more books already in this server. Perhaps you meant one of them instead?", view=view, ephemeral=True)
        await view.wait()
        selected_value = view.sel_value
        message_success = f"{selected_value}'s already in your list!"
        book_id = await self.db.get_book(book_name=selected_value,guild_id=guild_id)
        print(f'Book id is: {book_id}')
        print(selected_value)
        if book_id is None:
            print('Book not found')
            book_id = await self.db.create_book(selected_value,guild_id) ### futuramente fatorar o nome do livro aqui qualquercoisa
            print(f'New Book id is: {book_id}')
        print('this command was reloaded')
        tierlist_exists = await self.db.get_tierlist(user_id,book_id,guild_id)

        if not tierlist_exists:
            await self.db.create_tierlist(user_id,book_id,guild_id,tier)
            message_success = f"{selected_value} Added!"
        await interaction.followup.send(message_success, ephemeral=True)

    async def add_novels(self,interaction:Interaction, book_name,tier, guild_id, user_id) -> None:
        message_success = "Story already in your list!"
        book_id = await self.db.get_book(book_name=book_name,guild_id=guild_id)

        if book_id is None:
            book_id = await self.db.create_book(book_name,guild_id) ### futuramente fatorar o nome do livro aqui qualquercoisa

        tierlist_exists = await self.db.get_tierlist(user_id,book_id,guild_id)

        if not tierlist_exists:
            message_success = "Story Added!"
            await self.db.create_tierlist(user_id,book_id,guild_id,tier)
        await interaction.response.send_message(message_success, ephemeral=True)

    async def del_novels(self,interaction:Interaction, name) -> bool:
        user_id, guild_id = await self.get_user_data(interaction)
        message_success = "Story not found!"
        book_removed = await self.db.remove_book_from_tierlist(name,user_id,guild_id)
        if book_removed:
            message_success = "Story Removed!"
        await interaction.response.send_message(message_success, ephemeral=True)
    #ok?
    async def show_novels(self,interaction: Interaction, user:Member = None):
        user_id, guild_id = await self.get_user_data(interaction,user)
        bot_message = f"{interaction.user.display_name}, here's your tierlist!"

        if user:
            bot_message = f"{interaction.user.display_name}, here's {user.mention} tier list!"
        tierlist_view = TierlistViews()

        user_data = await self.db.show_tierlist_entries(user_id,guild_id)

        message_list = ['']
        for rank,novel_list in user_data.items():
            message = ''
            if len(novel_list) == 0:
                message += 'Empty. '

            for index,novel_name in enumerate(novel_list):
                message += f"「{novel_name}」 "
                if index < len(novel_list)-1:
                    message += ' ' #f"{index +1}: "
            if message_list[0] == '':
                message_list[0] = message
            else:
                message_list.append(message)

        embed_rank_s = Embed(color=Color.brand_red(), description=message_list[0], title='  ** Rank S ** ')
        embed_rank_a = Embed(color=Color.dark_orange(), description=message_list[1], title=" ** Rank A **")
        embed_rank_b = Embed(color=Color.orange(), description=message_list[2], title=" ** Rank B** ")
        embed_rank_c = Embed(color=Color.yellow(), description=message_list[3], title=" ** Rank C **")
        embed_rank_d = Embed(color=Color.green(), description=message_list[4], title=" ** Rank D **")
        embed_rank_e = Embed(color=Color.dark_teal(), description=message_list[5], title=" ** Rank E **")
        rank_embeds=[embed_rank_s,embed_rank_a,embed_rank_b,embed_rank_c,embed_rank_d,embed_rank_e]

        await interaction.response.send_message(bot_message,embeds=rank_embeds, view=tierlist_view)
    
    async def swap_novels(self, interaction: Interaction,tier:int, firstnovel:str, secondnovel:str):
        user_id, guild_id = await self.get_user_data(interaction)
        firstnovel = await self.string_formatting(firstnovel)
        secondnovel = await self.string_formatting(secondnovel)
        print(f"UserID: {user_id}\nGuildID: {guild_id}\nTier:{tier}\nFirstBookName: {firstnovel}\nSecondBookName: {secondnovel}")
        swap_success = await self.db.tierlist_swap_positions(user_id,guild_id,firstnovel,secondnovel,tier)

        if swap_success:
            await interaction.response.send_message(f'{firstnovel} and {secondnovel} swapped positions!', ephemeral= True)
        else:
            await interaction.response.send_message("Swap error: Either one or both doesn't exist or they aren't the same rank.", ephemeral=True)

    async def admindel_novels(self,interaction:Interaction,name:str,):
        _, guild_id = await self.get_user_data(interaction)
        message = "Book not found or another error occurred."
        book_removed = await self.db.remove_book_from_guild(name,guild_id)
        if book_removed:
            message = "Book removed successfully!"
        await interaction.response.send_message(message)
        ...

    async def ban_user(self,interaction:Interaction,user:Member):
        user_id, guild_id = await self.get_user_data(interaction,user)
        message = "Failed to ban user"
        ban_user = await self.db.create_banned_user(user_id,guild_id)
        if ban_user:
            message= "User banned successfully"
        await interaction.response.send_message(message,ephemeral=True)

    async def unban_user(self,interaction:Interaction,user:Member):
        user_id, guild_id = await self.get_user_data(interaction,user)
        message = "Failed to unban user"
        unban_user = await self.db.delete_banned_user(user_id,guild_id)
        if unban_user:
            message = "User unbanned successfully"
        await interaction.response.send_message(message,ephemeral=True)

    async def string_formatting(self,text:str):
        text_titlecased = titlecase.titlecase(text)
        return text_titlecased

    async def name_check(self,input_name:str, guild_id:int) -> list[str]:
        """This function checks if the name inserted already exists in the Database, using thefuzz library to find similar matches"""
        guild_book_list = await self.db.get_list_of_guild_books(guild_id)
        similar_matches = [input_name]
        for book in guild_book_list:
            ratio =  fuzz.ratio(input_name,book) 
            if ratio > 70 and ratio < 100:
               similar_matches.append(book)
        return similar_matches