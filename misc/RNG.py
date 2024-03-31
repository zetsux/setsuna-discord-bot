import discord
import random
from discord.ext import commands
from discord import app_commands


class RNG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name='rng',
        description='Generates a random number from 1 to the entered number')
    @app_commands.describe(max="The max range of random number",
                           count="The number of rolls wanted")
    async def random_number_generate(self,
                                     ctx: discord.Interaction,
                                     max: int,
                                     count: int = 1):
        await ctx.response.defer()
        if max > 1 and count >= 1:
            rngStr = ""

            for n in range(count):
                randValue = random.randint(1, max)
                if n % 2 == 0:
                    rngStr = rngStr + f"➳ {n+1}) [{randValue}]\n"

                else:
                    rngStr = rngStr + f"➸ {n+1}) [{randValue}]\n"

            embedVar = discord.Embed(
                title=f"[ RNG Result ( 1 - {max} | {count}x ) ]",
                description=f"```{rngStr}```",
                color=ctx.user.color)
            embedVar.set_author(name=ctx.user.name,
                                icon_url=ctx.user.avatar.url)
            await ctx.followup.send(embed=embedVar)

        elif max <= 1:
            await ctx.followup.send(
                f'Neee {ctx.user.name}-nyan, yang bener dong masukkin angka maxnya. Masa maxnya {max} sih..',
                ephemeral=True)

        elif count < 1:
            await ctx.followup.send(
                f'Neee {ctx.user.name}-nyan, yang bener dong masukkin countnya. Masa countnya {count} sih..',
                ephemeral=True)


async def setup(bot):
    await bot.add_cog(RNG(bot))
