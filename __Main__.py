from collections import defaultdict
from ssl import cert_time_to_seconds

import tracker
import discord
from discord.ext import commands
from discord import app_commands

from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)


class Admin:
    admins = [945116351167627315]
    def __init__(self, user_id):
        self.user_id = user_id

    @classmethod
    def add_admin(cls, user_id : int):
        cls.admins.append(user_id)

    @classmethod
    def is_admin(cls, user_id):
        return user_id in cls.admins

@bot.event
async def on_ready():
    print(f"Бот запущен как {bot.user}")

@bot.tree.command(name="tracker")
@app_commands.describe(query="Enter your valorant nametag to display your stats")
async def tracker(interaction : discord.Interaction, nametag : str):
    await interaction.response.send_message(f"ты ввел")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
async def add_admin(ctx, member : discord.Member):
    if Admin.is_admin(ctx.author.id):
        Admin.add_admin(member.id)
        await ctx.send(f"Пользователь, {member.mention}, теперь админ")
        return
    await ctx.send(f"недостаточно прав")

@bot.command()
async def tracker(ctx, )


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "джарвис папа дома" in message.content.lower() and Admin.is_admin(message.author.id):
        file = discord.File("image.png")
        await message.channel.send(f"Добро пожаловать! {message.author.mention} 🥵🥵", file=file)

    await bot.process_commands(message)



bot.run(TOKEN)