import discord
from discord.ext import commands
from discord import app_commands

guilds = [990445490401341511]


class Checkping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="pinger",
                          description="Check Ping")
    async def pinger(self, ctx: discord.Interaction):
        embed = discord.Embed(
            title="Current Ping",
            description=f"Ping is `{round(self.bot.latency * 100, 2)}` ms",
            color=ctx.user.color)
        await ctx.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Checkping(bot))
