"""Admin-only commands"""
import discord
from discord.ext import commands
from discord import app_commands


class AdminOnly(commands.GroupCog, name="cogs"):
    """Cog management"""

    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        super().__init__()  # this is now required in this context.

    @app_commands.command(name="load", description="Load a modules")
    @app_commands.describe(module="Module to load")
    async def load(self, interaction: discord.Interaction, module: str) -> None:
        """Loads a module."""
        is_owner = await self.bot.is_owner(interaction.user)
        if is_owner:
            try:
                await interaction.response.defer()
                await self.bot.load_extension(f"cogs.{module}")
            except Exception as e:
                embed = discord.Embed(
                    color=0xE74C3C, description=f"\N{PISTOL}\n{type(e).__name__}: {e}"
                )
                await interaction.followup.send(embed=embed)
            else:
                embed = discord.Embed(color=0xE74C3C, description="\N{OK HAND SIGN}")
                await interaction.followup.send(embed=embed)

    @app_commands.command(name="unload", description="Unload a modules")
    @app_commands.describe(module="Module to unload")
    async def unload(self, interaction: discord.Interaction, module: str) -> None:
        """Unloads a module."""
        is_owner = await self.bot.is_owner(interaction.user)
        if is_owner:
            try:
                await interaction.response.defer()
                await self.bot.unload_extension(f"cogs.{module}")
            except Exception as e:
                embed = discord.Embed(
                    color=0xE74C3C, description=f"\N{PISTOL}\n{type(e).__name__}: {e}"
                )
                await interaction.followup.send(embed=embed)
            else:  # ephemeral=True
                embed = discord.Embed(color=0xE74C3C, description="\N{OK HAND SIGN}")
                await interaction.followup.send(embed=embed)

    @app_commands.command(name="reload", description="Reload a modules")
    @app_commands.describe(module="Module to unload")
    async def _reload(self, interaction: discord.Interaction, module: str) -> None:
        """Reloads a module."""
        is_owner = await self.bot.is_owner(interaction.user)
        if is_owner:
            try:
                await interaction.response.defer()
                await self.bot.reload_extension(f"cogs.{module}")
            except Exception as e:
                embed = discord.Embed(
                    color=0xE74C3C, description=f"\N{PISTOL}\n{type(e).__name__}: {e}"
                )
                await interaction.followup.send(embed=embed)
            else:
                embed = discord.Embed(color=0xE74C3C, description="\N{OK HAND SIGN}")
                await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Setup the cog within discord.py lib"""
    await bot.add_cog(AdminOnly(bot), guild=discord.Object(770746735533228083))
