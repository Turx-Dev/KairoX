import random

import discord
from discord.ext import commands

from database import DB_PATH
import aiosqlite


class XP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        guild = message.guild

        if guild is None:
            return

        user_id = message.author.id
        guild_id = guild.id

        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute(
                """
                SELECT xp, level
                FROM users
                WHERE user_id = ? AND guild_id = ?
                """,
                (user_id, guild_id)
            )

            user = await cursor.fetchone()

            if user is None:
                xp = random.randint(5, 15)
                level = 1

                await db.execute(
                    """
                    INSERT INTO users
                    (user_id, guild_id, xp, level, coins)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (user_id, guild_id, xp, level, 0)
                )

            else:
                xp, level = user
                xp += random.randint(5, 15)

                required_xp = level * 100

                if xp >= required_xp:
                    level += 1
                    xp -= required_xp

                    await message.channel.send(
                        f"🎉 {message.author.mention} subiu para o nível **{level}**!"
                    )

                await db.execute(
                    """
                    UPDATE users
                    SET xp = ?, level = ?
                    WHERE user_id = ? AND guild_id = ?
                    """,
                    (xp, level, user_id, guild_id)
                )

            await db.commit()


async def setup(bot):
    await bot.add_cog(XP(bot))
