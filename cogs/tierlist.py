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
        self.ranks = [app_commands.Choice(name="Rank S", value="Rank S"),app_commands.Choice(name="Rank A", value="Rank A"), app_commands.Choice(name="Rank B", value="Rank B"), app_commands.Choice(name="Rank C", value="Rank C"),app_commands.Choice(name="Rank D", value="Rank D")]

    async def name_autocomplete(self,interact: discord.Interaction, current: str) -> typing.List[app_commands.Choice[str]]:
        data = []
        novel_list = await self.db.load_novels()
        if len(current) > 3:
            novel_list = list(filter(lambda x: current.lower() in x.lower(), novel_list))
        for choice_novel in novel_list[:25]:
            data.append(app_commands.Choice(name=choice_novel, value=choice_novel))
        return data
    
    async def del_autocomplete(self,interact: discord.Interaction, current: str) -> typing.List[app_commands.Choice[str]]:
        data = []
        novel_list = await self.db.load_tierlist()
        tier = interact.namespace.tier
        user_list = novel_list[str(interact.guild_id)][str(interact.user.id)][tier]
        if len(current) > 3:
            user_list = list(filter(lambda x: current.lower() in x.lower(), user_list))
        for choice_novel in user_list[:25]:
            data.append(app_commands.Choice(name=choice_novel, value=choice_novel))
        return data

    @app_commands.command(name="add", description="adiciona uma história da tierlist")
    @app_commands.autocomplete(name=name_autocomplete)
    @app_commands.choices(tier=[app_commands.Choice(name="Rank S", value="Rank S"),app_commands.Choice(name="Rank A", value="Rank A"), app_commands.Choice(name="Rank B", value="Rank B"), app_commands.Choice(name="Rank C", value="Rank C"),app_commands.Choice(name="Rank D", value="Rank D")])
    async def tierlist_add(self, interaction: discord.Interaction, tier: app_commands.Choice[str], name: str) -> None:
        """adiciona uma história"""
        await self.tierlist_handler(interaction,tier,name,command='add')
        #await interaction.response.send_message(tier.value)
        await interaction.response.send_message("História adicionada!", ephemeral=True)

    @app_commands.command(name="del", description="deleta uma história da tierlist")
    @app_commands.autocomplete(name=name_autocomplete)
    @app_commands.choices(tier=[app_commands.Choice(name="Rank S", value="Rank S"),app_commands.Choice(name="Rank A", value="Rank A"), app_commands.Choice(name="Rank B", value="Rank B"), app_commands.Choice(name="Rank C", value="Rank C"),app_commands.Choice(name="Rank D", value="Rank D")])
    async def tierlist_del(self, interaction: discord.Interaction, tier: app_commands.Choice[str], name: str) -> None:
        """deleta uma história"""
        success_message = await self.tierlist_handler(interaction,tier,name,command='del')
        if success_message:
            await interaction.response.send_message("História deletada!", ephemeral=True)
        else:
            await interaction.response.send_message("História não encontrada!", ephemeral=True)

    @app_commands.command(name="show", description="mostra toda a tierlist")
    async def tierlist_show(self, interaction: discord.Interaction, name: typing.Optional[discord.Member]) -> None:
        """mostra a tierlist"""
        embed,image = await self.show_novels(interaction, name)
        message = f"{interaction.user.nick}, here's your tierlist!"
        if name:
            message = f"{interaction.user.nick}, here's {name.mention} tier list!"
        tierlist_view = TierlistViews(name)
        await interaction.response.send_message(message, file=image, view=tierlist_view)

    async def tierlist_handler(self, interaction: discord.Interaction,tier: app_commands.Choice[str],name: str, command: str):
        user_tierlist = await self.db.load_tierlist()
        guild_id = str(interaction.guild_id)
        user_id = str(interaction.user.id)
        action = {'add': self.add_novels,'del': self.del_novels}
        success_message = await action[command](tier,name,user_tierlist, guild_id, user_id)
        return success_message
    
    async def add_novels(self, tier, name,user_tierlist, guild_id, user_id):
        novels = await self.db.load_novels()
        success_message = True
        if name not in novels:
            novels.append(name)
            await self.db.save_novels(novels)
        if name not in user_tierlist[guild_id][user_id][tier.value]:
            user_tierlist[guild_id][user_id][tier.value].append(name)
            await self.db.save_tierlist(user_tierlist)
        return success_message

    async def del_novels(self, tier, name, user_tierlist, guild_id, user_id):
        success_message = True
        if name in user_tierlist[guild_id][user_id][tier.value]:
            user_tierlist[guild_id][user_id][tier.value].remove(name)
            await self.db.save_tierlist(user_tierlist)
        else:
            success_message = False
        return success_message

    async def show_novels(self,interaction: discord.Interaction, name = None):
        user_tierlist = await self.db.load_tierlist()
        guild_id = str(interaction.guild_id)
        user_id = str(interaction.user.id)
        print(name)
        if name:
            user_id = str(name.id)
        if guild_id not in user_tierlist:
            user_tierlist[guild_id] = {user_id: {"Rank S": [], "Rank A": [], "Rank B": [], "Rank C": [], "Rank D": []}}
            await self.db.save_tierlist(tierlist_data=user_tierlist)

        if user_id not in user_tierlist[guild_id]:
            user_tierlist[guild_id][user_id] = {"Rank S": [], "Rank A": [], "Rank B": [], "Rank C": [], "Rank D": []}
            await self.db.save_tierlist(tierlist_data=user_tierlist)

        user_data = user_tierlist[guild_id][user_id]

        tierlist_image = TierlistImage()
        tierlist_image.draw_tier_list(user_data,user_id)
        file_path = (f'drawer/{user_id}_img.png')
        draw_image = discord.File(file_path, f"{user_id}_img.png")
        embed = discord.Embed(color=discord.Color.red())
        embed.set_image(url=f"attachment://{user_id}_img.png")


        return embed,draw_image


        # message = ""
        # for rank,novel_list in user_data.items():
        #     message += f"{rank}: "
        #     for index,novel_name in enumerate(novel_list):
        #         message += f"{novel_name}"
        #         if index < len(novel_list)-1:
        #             message +=", "
        #     message += "\n"


async def setup(bot):
    await bot.add_cog(tierlist(bot))