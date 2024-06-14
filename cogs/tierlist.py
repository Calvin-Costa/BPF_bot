import typing
import os

import discord
from discord import app_commands
from discord.ext import commands

from db.data_handler import DataHandler
from drawer.drawer import TierlistImage
from views.tierlist_views import TierlistViews

class tierlist(commands.GroupCog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DataHandler()
        super().__init__()

    async def guild_autocomplete(self,interact: discord.Interaction, current: str) -> typing.List[app_commands.Choice[str]]:
        data = []
        guild_id = await self.db.get_or_create_guild_model(interact.guild_id)
        novel_list = await self.db.get_books_in_guild(guild_id)
        if len(current) > 3:
            novel_list = list(filter(lambda x: current.lower() in x.lower(), novel_list))
        for choice_novel in novel_list[:25]:
            data.append(app_commands.Choice(name=choice_novel, value=choice_novel))
        return data
    
    async def user_autocomplete(self,interact: discord.Interaction, current: str) -> typing.List[app_commands.Choice[str]]:
        data = []
        guild_id = await self.db.get_or_create_guild_model(interact.guild_id)
        user_id = await self.db.get_or_create_user_model(interact.user.id,guild_id)

        novel_list = await self.db.get_user_books_per_guild(guild_id, user_id)
        if len(current) > 3:
            novel_list = list(filter(lambda x: current.lower() in x.lower(), novel_list))
        for choice_novel in novel_list[:25]:
            data.append(app_commands.Choice(name=choice_novel, value=choice_novel))
        return data

    @app_commands.command(name="add", description="adds a story in tierlist")
    @app_commands.autocomplete(name=guild_autocomplete)
    @app_commands.choices(tier=[
        app_commands.Choice(name="Rank S", value="1"),
        app_commands.Choice(name="Rank A", value='2'),
        app_commands.Choice(name="Rank B", value='3'), 
        app_commands.Choice(name="Rank C", value='4'),
        app_commands.Choice(name="Rank D", value='5')])
    async def tierlist_add(self, interaction: discord.Interaction, tier: app_commands.Choice[str], name: str) -> None:
        """adiciona uma história"""
        if len(name) > 60:
            await interaction.response.send_message(f"That name was too long! It needs to be {len(name)-80} less characters!")
            return
        success_message = await self.tierlist_handler(interaction, int(tier.value), name, command='add')
        if success_message:
            await interaction.response.send_message("Story added!", ephemeral=True)
            return
        await interaction.response.send_message("Story already in your list!", ephemeral=True)



    @app_commands.command(name="del", description="deletes a story from tierlist")
    @app_commands.autocomplete(name=user_autocomplete)
    async def tierlist_del(self, interaction: discord.Interaction, name: str) -> None:
        """deleta uma história"""
        success_message = await self.tierlist_handler(interaction,1,name,command='del')
        if success_message:
            await interaction.response.send_message("Story removed!", ephemeral=True)
        else:
            await interaction.response.send_message("Story not found!", ephemeral=True)

    @app_commands.command(name="show", description="shows entire tierlist")
    async def tierlist_show(self, interaction: discord.Interaction, name: typing.Optional[discord.Member]) -> None:
        """mostra a tierlist"""
        message = f"{interaction.user.display_name}, here's your tierlist!"
        if name:
            message = f"{interaction.user.display_name}, here's {name.mention} tier list!"
        
        embed,image, guild_id, user_id = await self.show_novels(interaction, name)

        tierlist_view = TierlistViews(guild_id, user_id,interaction.user.display_name,name)
        await interaction.response.send_message(message, file=image, view=tierlist_view)

    @app_commands.command(name="swap", description="swaps two titles (in the same rank) on your tierlist")
    @app_commands.autocomplete(firstnovel=user_autocomplete, secondnovel=user_autocomplete)
    async def tierlist_swap(self, interaction: discord.Interaction, firstnovel: str, secondnovel: str) -> None:
        success = await self.tierlist_swapper(interaction,firstnovel,secondnovel)
        if not success:
            await interaction.response.send_message("Swapping failed! Are you sure both novels are the same rank?", ephemeral=True)
        await interaction.response.send_message(f'{firstnovel} and {secondnovel} swapped positions!', ephemeral= True)

    async def tierlist_swapper(self, interaction: discord.Interaction, firstnovel: str, secondnovel: str):
        guild_id = interaction.guild_id
        user_id = interaction.user.id
        guild_id = await self.db.get_or_create_guild_model(guild_id)
        user_id = await self.db.get_or_create_user_model(user_id, guild_id)
        return await self.db.tierlist_swap_positions(user_id,guild_id,firstnovel,secondnovel)

    async def tierlist_handler(self, interaction: discord.Interaction,tier: app_commands.Choice[str],name: str, command: str):
        guild_id = str(interaction.guild_id)
        user_id = str(interaction.user.id)

        if command == 'add':
            success_message = await self.add_novels(tier,name,guild_id,user_id)
        elif command == 'del':
            success_message = await self.del_novels(name,guild_id,user_id)
        return success_message
    
    async def add_novels(self, tier, name, guild_id, user_id)-> bool:
        guild_id = await self.db.get_or_create_guild_model(guild_id)
        user_id = await self.db.get_or_create_user_model(user_id, guild_id)
        book_id, new_book = await self.db.get_or_create_book_id(book_name=name,guild_id=guild_id)

        success_message = await self.db.get_or_create_tierlist_entry(user_id=user_id, book_id=book_id, rank=tier, guild_id= guild_id)

        if success_message and not new_book:
            await self.db.alter_times_in_tierlist(book_id,guild_id,1)

        return success_message

    async def del_novels(self, name, guild_id, user_id) -> bool:
        '''Caminho do algoritmo:
        1- Checar se a história existe na tierlist
        2- Remover a história
        3- Checar se a história existe em Book e se times_in_tierlist = 1
        '''
        guild_id = await self.db.get_or_create_guild_model(guild_id)
        user_id = await self.db.get_or_create_user_model(user_id, guild_id)
        print('passei aqui')
        success_message = False
        novel_id, novel_exists = await self.db.get_book_id(name,guild_id)
        if novel_exists:
            await self.db.remove_book_from_tierlist(book_id=novel_id, user_id=user_id,guild_id=guild_id)
            success_message = True
        return success_message

    async def show_novels(self,interaction: discord.Interaction, name = None):
        guild_id = interaction.guild_id
        user_id = interaction.user.id
        if name:
            user_id = name.id
        guild_id = await self.db.get_or_create_guild_model(guild_id)
        user_id = await self.db.get_or_create_user_model(user_id, guild_id)

        user_data = await self.db.show_tierlist_entries(user_id,guild_id)
        print(user_data)

        tierlist_image = TierlistImage()
        tierlist_image.draw_tier_list(user_data,user_id)
        file_path = (f'drawer/{user_id}_img.png')
        draw_image = discord.File(file_path, f"{user_id}_img.png")
        embed = discord.Embed(color=discord.Color.red())
        embed.set_image(url=f"attachment://{user_id}_img.png")

        return embed,draw_image, guild_id,user_id

async def setup(bot):
    await bot.add_cog(tierlist(bot))