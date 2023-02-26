"""Beamng-mp cog"""
import re
from typing import List
import discord
from discord import app_commands
from discord.ext import commands
from .commands import beamng


class BeamngMp(commands.Cog):
    """Beamng-mp cog"""

    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        super().__init__()  # this is now required in this context.

    async def servername_autocomplete(
        self,
        _interaction: discord.Interaction,
        current: str,
    ) -> List[app_commands.Choice[str]]:
        """Autocomplete servernames of community"""
        server_list = await beamng.read_api()
        filtered_servers = [
            app_commands.Choice(
                name=re.sub(r"\^[a-z_0-9]", "", server.get("sname", ""))[:100],
                value=re.sub(r"\^[a-z_0-9]", "", server.get("sname", ""))[:100],
            )
            for server in server_list
            if current.lower()
            in re.sub(r"\^[a-z_0-9]", "", server.get("sname", "")).lower()
        ]
        # discord limits to max 25 items
        return filtered_servers[:25]

    @app_commands.command(
        name="mpname",
        description="Get info based on a specific server (uses first matching result)",
    )
    @app_commands.describe(servername="For which server?")
    @app_commands.autocomplete(
        servername=servername_autocomplete,
    )
    async def mpname(self, interaction: discord.Interaction, servername: str) -> None:
        """Get beamng serverinfo"""
        await interaction.response.defer()
        await beamng.mpname(interaction, servername)

    @mpname.error
    async def mpname_error(self, interaction: discord.Interaction, _error) -> None:
        """On command error"""
        embed = discord.Embed(
            color=0xE74C3C, description="No servers found with that servername"
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="mpdiscord", description="Get the servers based on Discord name + tag"
    )
    @app_commands.describe(discord_tag="(Discord-name#tag)")
    async def mpdiscord(
        self, interaction: discord.Interaction, discord_tag: str
    ) -> None:
        """Get beamng serverinfo by discord tag"""
        await interaction.response.defer()
        await beamng.mpdiscord(interaction, discord_tag)

    @mpdiscord.error
    async def mpdiscord_error(self, interaction: discord.Interaction, _error) -> None:
        """On command error"""
        embed = discord.Embed(
            color=0xE74C3C, description="No servers found with that ownername"
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="mpip", description="Get the servers based on serverip")
    @app_commands.describe(server_ip="example: 123.432.54.3")
    async def mpip(self, interaction: discord.Interaction, server_ip: str) -> None:
        """Get beamng servers by ip"""
        await interaction.response.defer()
        await beamng.mpip(interaction, server_ip)

    @mpip.error
    async def mpip_error(self, interaction: discord.Interaction, _error) -> None:
        """On command error"""
        embed = discord.Embed(
            color=0xE74C3C, description="No servers found with that ip"
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="mpinfo", description="Get info about all the running servers"
    )
    async def mpinfo(self, interaction: discord.Interaction) -> None:
        """Get all the running servers"""
        await interaction.response.defer()
        await beamng.mpinfo(interaction)


async def setup(bot: commands.Bot) -> None:
    """Setup the cog within discord.py lib"""
    await bot.add_cog(BeamngMp(bot))
