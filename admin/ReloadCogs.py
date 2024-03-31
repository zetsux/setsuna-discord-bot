import discord
from discord.ext import commands
from discord import app_commands
from discord import app_commands
import os


class ReloadCogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='reloadcogs', description='Reload Cogs')
    @app_commands.checks.has_any_role('Encoder Magang', 'Owner')
    async def reload(self, interaction: discord.Interaction):
        await interaction.response.defer()
        str = ""
        for folder in os.listdir("./"):
            path = f"./{folder}"

            if not os.path.isdir(path) or folder == "events":
                continue

            for filename in os.listdir(f"./{folder}"):
                if filename.endswith(".py"):
                    try:
                        if f"{folder}.{filename[:-3]}" in self.bot.extensions:
                            await self.bot.reload_extension(
                                f"{folder}.{filename[:-3]}")
                        else:
                            await self.bot.load_extension(
                                f"{folder}.{filename[:-3]}")
                        str += f"{folder}.{filename[:-3]}\n"
                    except Exception as error:
                        print(error)

        await interaction.followup.send(f"{str}")


async def setup(bot):
    await bot.add_cog(ReloadCogs(bot))
