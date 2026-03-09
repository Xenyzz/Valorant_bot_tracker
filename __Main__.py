from bisect import insort_left
from collections import defaultdict
from ssl import cert_time_to_seconds

from discord._types import ClientT
from discord.app_commands import describe

import tracker as val_api
import db

import discord
from discord.ext import commands
from discord import app_commands, Interaction, Embed

from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
GUILD_ID = 945118071574642699
bot = commands.Bot(command_prefix="/", intents=intents)


class RegisterModal(discord.ui.Modal, title="Register Profile"):
    nametag = discord.ui.TextInput(label="Valorant Nametag", placeholder="Enter your nametag: ")
    description = discord.ui.TextInput(label="Description", placeholder="You can text anything you want to: ")

    async def on_submit(self, interaction: discord.Interaction):
        db.reg_user(
            discord_id=interaction.user.id,
            valorant_nametag=self.nametag.value,
            user_description=self.description.value
        )
        await interaction.response.send_message("Profile created",ephemeral=True)


class Admin:
    admins = [945116351167627315]

    def __init__(self, user_id):
        self.user_id = user_id

    @classmethod
    def add_admin(cls, user_id: int):
        cls.admins.append(user_id)

    @classmethod
    def is_admin(cls, user_id):
        return user_id in cls.admins


async def get_tracker(nametag: str) -> Embed:
    player_data = val_api.get_users_info(nametag)
    rank_data = val_api.get_api_mmr(nametag)
    peak_rank = val_api.get_max_rank(rank_data)
    current_rank = val_api.get_current_rank(rank_data)
    player_matches = val_api.get_match_list(nametag)
    kill_deaths_ratio = val_api.get_player_stats(player_matches)

    embed = discord.Embed(
        title="peak rating",
        description=f"{peak_rank[0]}, {peak_rank[1].upper()}",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="current rating",
        value=f"{current_rank[0]}, {current_rank[1]}",
        inline=True
    )

    embed.add_field(
        name="account_level",
        value=f"{player_data.get('account_level')}",
        inline=True
    )

    embed.add_field(
        name="Stats",
        value=f"V26A1: **{kill_deaths_ratio}** K/D",
        inline=True
    )

    embed.set_footer(text=f"Last updated: {player_data.get('last_updated')}")
    embed.set_thumbnail(url=player_data.get("card"))

    return embed


@bot.event
async def on_ready():
    print(f"Бот запущен как {bot.user}")
    await bot.tree.sync()
    guild = discord.Object(id=GUILD_ID)
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)
    print("Synced to guild", GUILD_ID)


@bot.tree.command(name="register")
async def register(interaction: discord.Interaction):
    await interaction.response.send_modal(RegisterModal())


@bot.tree.command(name="profile")
async def profile(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    user_info = db.show_table(discord_id=interaction.user.id)
    if user_info:

        nametag = user_info[1]
        description = user_info[2]
        avatar_url = interaction.user.display_avatar.url

        embed = await get_tracker(nametag)
        embed.set_thumbnail(url=avatar_url)
        embed.set_author(
            name=interaction.user.name,
            icon_url=interaction.user.display_avatar.url
        )
        embed.add_field(
            name="description",
            value=description,
            inline=False
        )
        embed.set_thumbnail(url=None)
        embed.set_image(url="https://i1.sndcdn.com/avatars-bMDr60iRk2Vrzyl9-RymFow-t240x240.jpg")

        await interaction.followup.send(embed=embed)
        return
    await interaction.response.send_message("You have no profile, use command /reg to create profile", ephemeral=True)


@bot.tree.command(name="tracker")
@app_commands.describe(nametag="Enter your valorant nametag to display your stats")
async def tracker(interaction: discord.Interaction, nametag: str):
    await interaction.response.defer(thinking=True)
    embed = get_tracker(nametag)
    await interaction.followup.send(embed=embed)


@bot.command()
async def add_admin(ctx, member: discord.Member):
    if Admin.is_admin(ctx.author.id):
        Admin.add_admin(member.id)
        await ctx.send(f"Пользователь, {member.mention}, теперь админ")
        return
    await ctx.send("Недостаточно прав")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "джарвис папа дома" in message.content.lower() and Admin.is_admin(message.author.id):
        file = discord.File("image.png")
        await message.channel.send(f"Пошел нахуй! {message.author.mention} 🥵🥵", file=file)

    await bot.process_commands(message)


bot.run(TOKEN)