import discord
from discord.ext import commands
from discord import app_commands


class Pedo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='pedo', description='Expose a lolicon')
    @app_commands.describe(member="The member to target")
    async def pedo(self, ctx: discord.Interaction, member: discord.Member = None):
      try:
        mentionUser = '<@' + str(member.id) + '>'
        embed = discord.Embed()
        embed.set_image(
            url='https://some-random-api.ml/canvas/lolice?avatar=' +
            ctx.user.avatar.url)
        await ctx.response.send_message(f"{mentionUser}", embed=embed)
      except Exception as error:
        await ctx.response.send_message("Yang bikin gif anime lg turu")
        print(error)

async def setup(bot):
    await bot.add_cog(Pedo(bot))
