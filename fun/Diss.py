import discord
import random
from discord.ext import commands
from discord.commands import Option

guilds = [990445490401341511]

class Diss(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.slash_command(name='diss', description='Disses a target')
  @commands.has_any_role('Encoder Magang', 'Owner')
  async def diss_target(self, ctx, member: Option(discord.Member, "Member to diss", required=True)):
    dissLines = [
        'Cupu bgt si', 'Diem ya lemah', 'Sini gelud penakut',
        'Gausah sok jago', 'Janji ga nangis dek?', 'Belajar dulu sana'
    ]

    dissString = random.choice(dissLines)
    await ctx.respond(f'Oi {member.name}, {dissString}')

def setup(bot):
  bot.add_cog(Diss(bot))