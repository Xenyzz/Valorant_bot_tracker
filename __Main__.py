import tracker as val_api
import db

import discord
from discord.ext import commands
from discord import app_commands, Embed

from dotenv import load_dotenv
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)


class RegisterModal(discord.ui.Modal, title="Register Profile"):
    nametag = discord.ui.TextInput(label="Valorant Nametag", placeholder="Name#TAG")
    description = discord.ui.TextInput(label="Description", placeholder="Anything about yourself")

    async def on_submit(self, interaction: discord.Interaction):
        success = db.reg_user(
            discord_id=interaction.user.id,
            valorant_nametag=self.nametag.value,
            user_description=self.description.value
        )
        if success:
            await interaction.response.send_message("✅ Profile created!", ephemeral=True)
        else:
            await interaction.response.send_message(
                "⚠️ Profile already exists. Use `/edit_profile` to update it.", ephemeral=True
            )


class EditModal(discord.ui.Modal, title="Edit Profile"):
    nametag = discord.ui.TextInput(
        label="Valorant Nametag",
        required=False,
        placeholder="Leave empty to keep current"
    )
    description = discord.ui.TextInput(
        label="Description",
        required=False,
        placeholder="Leave empty to keep current"
    )

    async def on_submit(self, interaction: discord.Interaction):
        db.edit_user(
            discord_id=interaction.user.id,
            valorant_nametag=self.nametag.value or None,
            user_description=self.description.value or None
        )
        await interaction.response.send_message("✅ Profile updated!", ephemeral=True)


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


async def get_tracker(nametag: str) -> Embed | None:
    """Builds a Valorant stats embed. Returns None if data is unavailable."""
    try:
        player_data = val_api.get_users_info(nametag)
        rank_data = val_api.get_api_mmr(nametag)

        if not player_data or not rank_data:
            return None

        peak_rank = val_api.get_max_rank(rank_data)
        current_rank = val_api.get_current_rank(rank_data)
        player_matches = val_api.get_match_list(nametag)
        kd_ratio = val_api.get_player_stats(player_matches) if player_matches else "N/A"

        embed = discord.Embed(
            title=f"🏆 Peak: {peak_rank[0]} — {peak_rank[1].upper()}",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="Current Rank",
            value=f"{current_rank[0]} / {current_rank[1]} RR",
            inline=True
        )
        embed.add_field(
            name="Account Level",
            value=str(player_data.get("account_level", "?")),
            inline=True
        )
        embed.add_field(
            name="K/D (this act)",
            value=str(kd_ratio),
            inline=True
        )
        embed.set_footer(text=f"Last updated: {player_data.get('last_updated', '?')}")
        embed.set_thumbnail(url=player_data.get("card"))

        return embed

    except Exception as e:
        logger.error(f"get_tracker error for '{nametag}': {e}")
        return None


@bot.event
async def on_ready():
    logger.info(f"Bot started as {bot.user}")
    await bot.tree.sync()
    logger.info("Global slash commands synced")


@bot.tree.command(name="register", description="Create your Valorant profile")
async def register(interaction: discord.Interaction):
    await interaction.response.send_modal(RegisterModal())


@bot.tree.command(name="edit_profile", description="Edit your Valorant profile")
async def edit_profile(interaction: discord.Interaction):
    await interaction.response.send_modal(EditModal())


@bot.tree.command(name="profile", description="View your saved Valorant profile")
async def profile(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)

    user_info = db.show_table(discord_id=interaction.user.id)
    if not user_info:
        await interaction.followup.send(
            "❌ You don't have a profile yet. Use `/register` to create one.",
            ephemeral=True
        )
        return

    nametag = user_info[1]
    description = user_info[2]

    embed = await get_tracker(nametag)
    if not embed:
        await interaction.followup.send(
            "⚠️ Could not fetch stats. Check that your nametag is correct or try again later.",
            ephemeral=True
        )
        return

    embed.set_author(
        name=interaction.user.display_name,
        icon_url=interaction.user.display_avatar.url
    )
    embed.add_field(name="Description", value=description or "—", inline=False)

    await interaction.followup.send(embed=embed)


@bot.tree.command(name="tracker", description="Look up any Valorant player")
@app_commands.describe(nametag="Valorant nametag (Name#TAG)")
async def tracker(interaction: discord.Interaction, nametag: str):
    await interaction.response.defer(thinking=True)

    embed = await get_tracker(nametag)
    if not embed:
        await interaction.followup.send(
            "⚠️ Could not fetch stats. Check the nametag and try again.",
            ephemeral=True
        )
        return

    await interaction.followup.send(embed=embed)


@bot.command()
async def add_admin(ctx, member: discord.Member):
    if Admin.is_admin(ctx.author.id):
        Admin.add_admin(member.id)
        await ctx.send(f"✅ {member.mention} is now an admin.")
    else:
        await ctx.send("❌ You don't have permission to do this.")



# ==================== Web server (health check) ====================

from aiohttp import web
import asyncio

async def handle_health(request):
    return web.json_response({
        "status": "ok",
        "bot": str(bot.user),
        "guilds": len(bot.guilds),
        "latency_ms": round(bot.latency * 1000, 1),
    })

async def run_web_server():
    PORT = int(os.getenv("PORT", 8080))
    app = web.Application()
    app.router.add_get("/", handle_health)
    app.router.add_get("/health", handle_health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logger.info(f"Health server running on port {PORT}")
    return runner

# ==================== Entry point ====================

async def main():
    web_runner = None
    try:
        web_runner = await run_web_server()
        async with bot:
            await bot.start(TOKEN)
    except KeyboardInterrupt:
        logger.info("Shutdown requested")
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
    finally:
        if web_runner:
            await web_runner.cleanup()
        logger.info("Bot stopped")

if __name__ == "__main__":
    asyncio.run(main())