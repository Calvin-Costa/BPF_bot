import typing


from discord import app_commands, Interaction, Member, Embed, Color, SelectOption
from discord.ui import Select
from discord.ext import commands

from db.data_handler import DataHandler
from .handlers.tierlist_handler import TierlistHandler
from views.tierlist_views import TierlistViews, SelectMenuView

class Tierlist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DataHandler()
        self.th = TierlistHandler()
        super().__init__()

    async def guild_autocomplete(self,interaction: Interaction, current: str) -> typing.List[app_commands.Choice[str]]:
        data = []
        _,guild_id = await self.th.get_user_data(interaction)
        novel_list = await self.db.get_list_of_guild_books(guild_id)
        if len(current) > 3:
            novel_list = list(filter(lambda x: current.lower().strip().replace(' ', '') in x.lower().strip().replace(' ', ''), novel_list))
        for choice_novel in novel_list[:25]:
            data.append(app_commands.Choice(name=choice_novel, value=choice_novel))
        return data

    async def user_autocomplete(self,interaction: Interaction, current: str) -> typing.List[app_commands.Choice[str]]:
        data = []
        user_id,guild_id = await self.th.get_user_data(interaction)
        novel_list = await self.db.get_user_books_per_guild(guild_id, user_id)
        if len(current) > 3:
            novel_list = list(filter(lambda x: current.lower().strip().replace(' ', '') in x.lower().strip().replace(' ', ''), novel_list))
        for choice_novel in novel_list[:25]:
            data.append(app_commands.Choice(name=choice_novel, value=choice_novel))
        return data
    
    tierlist = app_commands.Group(name="tierlist", description="...")
    admin = app_commands.Group(name="admin", description="...")

    @tierlist.command(name="add", description="adds a story in tierlist")
    @app_commands.autocomplete(name=guild_autocomplete)
    @app_commands.choices(tier=[
        app_commands.Choice(name="Rank S", value="1"),
        app_commands.Choice(name="Rank A", value='2'),
        app_commands.Choice(name="Rank B", value='3'), 
        app_commands.Choice(name="Rank C", value='4'),
        app_commands.Choice(name="Rank D", value='5'),
        app_commands.Choice(name="Rank E", value='6')])
    async def tierlist_add(self, interaction: Interaction,tier: app_commands.Choice[str], name: str) -> None:
        """adiciona uma história"""
        tier_value = int(tier.value)
        await self.th.add_novels_handler(interaction,name,tier=tier_value)

    @tierlist.command(name="del", description="deletes a story from tierlist")
    @app_commands.autocomplete(name=user_autocomplete)
    async def tierlist_del(self, interaction: Interaction, name: str) -> None:
        """deleta uma história"""
        await self.th.del_novels(interaction,name)
       

    @tierlist.command(name="show", description="shows entire tierlist")
    async def tierlist_show(self, interaction: Interaction, name: typing.Optional[Member]) -> None:
        """mostra a tierlist"""
        await self.th.show_novels(interaction,user=name)

    


    @tierlist.command(name="swap", description="swaps two titles (in the same rank) on your tierlist")
    @app_commands.choices(tier=[
        app_commands.Choice(name="Rank S", value="1"),
        app_commands.Choice(name="Rank A", value='2'),
        app_commands.Choice(name="Rank B", value='3'), 
        app_commands.Choice(name="Rank C", value='4'),
        app_commands.Choice(name="Rank D", value='5'),
        app_commands.Choice(name="Rank E", value='6')])
    @app_commands.autocomplete(firstnovel=user_autocomplete, secondnovel=user_autocomplete)
    async def tierlist_swap(self, interaction: Interaction,tier: app_commands.Choice[str], firstnovel: str, secondnovel: str) -> None:
        tier_value = int(tier.value)
        await self.th.swap_novels(interaction,tier_value,firstnovel,secondnovel)

    @admin.command(name="banuser", description="ADMIN COMMAND: ban a user from using the tierlist")
    async def tierlist_ban(self, interaction: Interaction, user: Member) -> None:
        if interaction.user.guild_permissions.administrator:
            await self.th.ban_user(interaction,'banuser',user)
        else:
            await interaction.response.send_message("You aren\'t an administrator. Permission denied.", ephemeral=True)

    @admin.command(name="unbanuser", description="ADMIN COMMAND: unban a user from using the tierlist")
    async def tierlist_unban(self, interaction: Interaction, user: Member) -> None:
        if interaction.user.guild_permissions.administrator:
            await self.th.unban_user(interaction,user)
        else:
            await interaction.response.send_message("You aren\'t an administrator. Permission denied.", ephemeral=True)

    @admin.command(name="remove", description="ADMIN COMMAND: removes a book from the server")
    @app_commands.autocomplete(book=guild_autocomplete)
    async def tierlist_admindelete(self,interaction:Interaction,book: str):
        if interaction.user.guild_permissions.administrator:
            await self.th.admindel_novels(interaction,book)
        else:
            await interaction.response.send_message("You aren\'t an administrator. Permission denied.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Tierlist(bot))