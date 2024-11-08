"""Help cog"""

import discord
from discord.ext import commands
from discord.ext.commands import AutoShardedBot
from discord import app_commands


class AdminOnly(commands.Cog):
    """Other commands"""

    def __init__(self, bot: AutoShardedBot):
        self.bot = bot

    @app_commands.command(name="help", description="The help command")
    async def help_command(self, interaction: discord.Interaction):
        """Main help command"""
        await interaction.response.defer()
        embed = discord.Embed(
            title="Help",
            color=0xFFA500,
            description="Get information about the current running BeamMP servers.",
        )
        embed.add_field(
            name="Main commands",
            value="""
        **/mpdiscord (Discord-name#tag)** Get the servers based on Discord name + tag.
        **/mpinfo ** Get info about all the running servers.
        **/mpip (server IP)** Get the servers based on serverip.
        **/mpname (server name)** Get info based on a specific server (uses first matching result).
        [See the source code on GitHub for this bot](https://github.com/community-network/beamng-mp)
        """,
            inline=False,
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.set_footer(
            text=f"Requested by {interaction.user.name}",
            icon_url=self.bot.user.avatar.url,
        )
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Setup the cog within discord.py lib"""
    await bot.add_cog(AdminOnly(bot))
