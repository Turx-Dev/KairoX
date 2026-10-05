import os
import aiosqlite

import discord
from discord.ext import commands
from dotenv import load_dotenv

from database import init_db, DB_PATH


load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")


intents = discord.Intents.default()
intents.message_content = True


class KairoX(commands.Bot):
    async def setup_hook(self):
        await init_db()
        await self.load_extension("cogs.xp")


bot = KairoX(
    command_prefix="!",
    intents=intents
)

@bot.event
async def on_ready():
    print(f"KairoX online como {bot.user}")


@bot.command()
async def ping(ctx):
    ping = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! Latência: **{ping}ms**")


@bot.command()
async def rank(ctx):
    if ctx.guild is None:
        return

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            SELECT xp, level
            FROM users
            WHERE user_id = ? AND guild_id = ?
            """,
            (ctx.author.id, ctx.guild.id)
        )

        user = await cursor.fetchone()

    if user is None:
        await ctx.send(
            f"📊 {ctx.author.mention}, você ainda não ganhou XP."
        )
        return

    xp, level = user
    required_xp = level * 100

    await ctx.send(
        f"🏆 **Rank de {ctx.author.display_name}**\n"
        f"⭐ Nível: **{level}**\n"
        f"✨ XP: **{xp}/{required_xp}**"
    )

bot.run(TOKEN)
