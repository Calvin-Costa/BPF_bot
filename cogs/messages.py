import discord
from discord import app_commands
from discord.ext import commands
import random
class Messages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if msg.author.bot:
                return
        #await self.bot.process_commands(msg)
        # if random.random()*100 >= 90:
        #     await msg.add_reaction('👍')

async def setup(bot):
    await bot.add_cog(Messages(bot))