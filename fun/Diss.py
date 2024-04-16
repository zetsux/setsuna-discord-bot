import discord
import random
from discord.ext import commands
from discord import app_commands


class Diss(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='diss', description='Disses a target')
    @app_commands.checks.has_any_role('Encoder Magang', 'Owner')
    @app_commands.describe(member='The member to diss')
    async def diss_target(self, ctx: discord.Interaction,
                          member: discord.Member):
        dissLines = [
            'Cupu bgt si', 'Diem ya lemah', 'Sini gelud penakut',
            'Gausah sok jago', 'Janji ga nangis dek?', 'Belajar dulu sana'
        ]

        dissString = random.choice(dissLines)
        await ctx.response.send_message(f'Oi {member.name}, {dissString}')


async def setup(bot):
    await bot.add_cog(Diss(bot))
