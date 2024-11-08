"""Discord command syncing"""

from typing import Literal, Optional
from pprint import pprint
import discord
from discord.ext import commands
from discord import app_commands


class Sync(commands.Cog):
    """Syncs the slashcommands to discord"""

    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @app_commands.command(name="sync", description="Sync commands")
    @app_commands.describe(guilds="Guilds to sync", spec="Type of sync")
    async def sync(
        self,
        interaction: discord.Interaction,
        guilds: str = None,
        spec: Optional[Literal["~", "*", "^"]] = None,
    ) -> None:
        """Main sync command"""
        is_owner = await self.bot.is_owner(interaction.user)
        if is_owner:
            await interaction.response.defer()
            if not guilds:
                if spec == "~":
                    synced = await self.bot.tree.sync(guild=interaction.guild)
                elif spec == "*":
                    self.bot.tree.copy_global_to(guild=interaction.guild)
                    synced = await self.bot.tree.sync(guild=interaction.guild)
                elif spec == "^":
                    self.bot.tree.clear_commands(guild=interaction.guild)
                    await self.bot.tree.sync(guild=interaction.guild)
                    synced = []
                else:
                    synced = await self.bot.tree.sync()
                items = [item.name for item in synced]
                sync_type_msg = "globally" if spec is None else "to the current guild."
                await interaction.followup.send(
                    f"Synced {len(synced)} commands {sync_type_msg}"
                )
                print("synced commands:")
                pprint(items)
                return

            ret = 0
            for guild in guilds.split(" "):
                try:
                    await self.bot.tree.sync(guild=discord.Object(id=guild))
                except discord.HTTPException:
                    pass
                else:
                    ret += 1

            await interaction.followup.send(
                f"Synced the tree to {ret}/{len(guilds.split(' '))}."
            )

    @sync.error
    async def bfsync_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        """On command error"""
        print(error)
        await interaction.followup.send(f"Failed to sync:\n{error}")


async def setup(bot: commands.Bot) -> None:
    """Setup the cog within discord.py lib"""
    await bot.add_cog(Sync(bot), guild=discord.Object(770746735533228083))
