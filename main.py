import random
import os

from db.database import db, User, Book, Tierlist, Rank
import settings

from discord.ext import commands
from discord import app_commands, Intents, Message





permission = Intents.default()
#permitir que o bot leia mensagens:
permission.message_content = True
# permitir que o bot veja os membros:
permission.members = True


bot = commands.Bot(command_prefix=";;", intents= permission)
async def load_cogs():
    for file in os.listdir('cogs'):
        if file.endswith('.py'):
            print(f'Cog {file} inicializada')
            await bot.load_extension(f'cogs.{file[:-3]}')
            
@bot.command()
async def reload(ctx: commands.Context):
    for file in os.listdir('cogs'):
        if file.endswith('.py'):
            print(f'Cog {file} inicializada')
            await bot.reload_extension(f'cogs.{file[:-3]}')
    await ctx.message.add_reaction("✅")

@bot.event
async def on_ready():
    print("Beware of Bot!")
    await load_cogs()
    
@bot.event
async def on_message(msg:Message):
    if msg.author.bot:
        return
    await bot.process_commands(msg)

@bot.command()
async def sincronizar(ctx:commands.Context):
    if ctx.author.id == 287796413893705731:
        comandos_sincronizados = await bot.tree.sync()
        await ctx.reply(f'{len(comandos_sincronizados)} comandos sincronizados.')
    else:
        await ctx.reply('Você não pode fazer isso. =/ ')


#a ORM peewee cria a tabela apenas se ela já não existir
db.create_tables([User,Book, Tierlist, Rank])
#isso é a última coisa que tem que ter:
bot.run(settings.DISCORD_BOT_TOKEN)