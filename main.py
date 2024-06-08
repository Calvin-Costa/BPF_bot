import random
import os

import discord
from discord.ext import commands
from discord import app_commands
import db.database #to run db.__init__ and initialize database
from bot_token import TOKEN

permission = discord.Intents.default()
#permitir que o bot leia mensagens:
permission.message_content = True
# permitir que o bot veja os membros:
permission.members = True


bot = commands.Bot(command_prefix=".", intents= permission)
async def load_cogs():
    for file in os.listdir('cogs'):
        if file.endswith('.py'):
            print(f'Cog {file} inicializada')
            await bot.load_extension(f'cogs.{file[:-3]}')

@bot.event
async def on_ready():
    print("Beware of Bot!")
    await load_cogs()
    
@bot.event
async def on_message(msg:discord.Message):
    if msg.author.bot:
        return
    await bot.process_commands(msg)
    chance = random.random()
    if chance >= 0.9:
        await msg.add_reaction('👍')

@bot.event
async def on_message_delete(msg:discord.Message):
    if msg.author.bot:
        return
    await msg.channel.send('ihhh apagou por que? tá com medinho do que vou ler é?!')

@bot.command()
async def sincronizar(ctx:commands.Context):
    if ctx.author.id == 287796413893705731:
        comandos_sincronizados = await bot.tree.sync()
        await ctx.reply(f'{len(comandos_sincronizados)} comandos sincronizados.')
    else:
        await ctx.reply('Você não pode fazer isso. =/ )')

#isso é a última coisa que tem que ter:
bot.run(TOKEN)



