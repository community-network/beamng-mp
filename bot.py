"""discord api connection"""

import os
import asyncio
import discord
from discord.ext import commands
import discordlists
from cogs.api.redis import RedisClient
import healthcheck

TOKEN = os.getenv("TOKEN", "")


class MyBot(commands.AutoShardedBot):
    """Bot setup class."""

    async def setup_hook(self):
        await healthcheck.start(self)
        self.remove_command("help")
        await self.load_extension("cogs.beamng_mp")
        await self.load_extension("cogs.admin_only")
        await self.load_extension("cogs.other")
        await self.load_extension("cogs.sync")


intents = discord.Intents.default()
bot = MyBot(fetch_offline_members=False, command_prefix="mp!", intents=intents)


@bot.event
async def on_ready():
    """On bot ready"""
    print("bot started \n")
    print(f"Connected on {len(bot.guilds)} server(s)")

    redis_client = RedisClient()
    await redis_client.redis_connect()

    # sync /sync
    await bot.tree.sync(guild=discord.Object(770746735533228083))

    top_token = os.getenv("TOP_TOKEN", "")
    # https://botblock.org/
    if top_token != "":
        print("running prod")
        api = discordlists.Client(bot)
        api.set_auth("top.gg", top_token)
        api.start_loop()

    while True:
        try:
            await bot.change_presence(
                activity=discord.Game(f"in {len(bot.guilds)} servers")
            )
            await asyncio.sleep(900)
        except Exception as e:
            print(e)


# dont give a error if a command doesn't exist
@bot.event
async def on_command_error(ctx, error):
    """On any error"""
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        return
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            color=0xE74C3C, description="Your not allowed to use this command"
        )
        await ctx.send(embed=embed)
    raise error


# run the bot
bot.run(TOKEN)
