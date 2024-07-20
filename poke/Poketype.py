import discord
from discord.ext import commands
from discord import app_commands

class Poketype(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name='poketype', description='Open a chart to see pokemon typing')
  async def pokemochart(self, ctx: discord.Interaction):
    embedVar = discord.Embed(title=f"[ PokeType Chart ]",
                             description=f' ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼',
                             color=0xee1515)
    embedVar.set_image(
        url=
        'https://cdn.discordapp.com/attachments/995337235211763722/1019540327507435560/pokechart.png'
    )
    await ctx.response.send_message(embed=embedVar)

async def setup(bot):
  await bot.add_cog(Poketype(bot))