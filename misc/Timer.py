import discord
from discord.ui import Button, View
from discord.ext import commands
from discord import app_commands
import asyncio


class Timer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name='timer',
        description='Create a button that auto end after a set period of time')
    @app_commands.describe(timer="The number of seconds to wait for")
    async def timer_test(self, ctx: discord.Interaction, timer: int):
        if timer <= 0:
            await ctx.response.send_message(
                f"Neeee {ctx.user.name}-nyan, ngga jelas banget ah, ngapain coba timer kurang dari 0 detik",
                ephemeral=True)
            return

        buttonTime = Button(label='End',
                            style=discord.ButtonStyle.danger,
                            row=0)
        buttonCheck = Button(label='Check Time',
                             style=discord.ButtonStyle.gray,
                             row=0)
        flag = False

        async def end_callback(interaction):
            if interaction.user.id != ctx.user.id:
                await interaction.response.send_message(
                    f"Neee {interaction.user.name}-nyan, mending /timer sendiri deh, jangan pake punya orang lain ih",
                    ephemeral=True)
                return

            nonlocal flag
            flag = True
            embedEdit = discord.Embed(
                title=f"Timer ditutup secara paksa dengan button",
                description="Sudah abis kak",
                color=0xffff00)
            await interaction.response.edit_message(embed=embedEdit, view=None)

        async def check_callback(interaction):
            await interaction.response.send_message(
                f"Sabar yah {interaction.user.name}-nyan, waktu tersisa {timer - time} detik lagi..",
                ephemeral=True)

        buttonTime.callback = end_callback
        buttonCheck.callback = check_callback
        view = View(timeout=None)
        view.add_item(buttonTime)
        view.add_item(buttonCheck)

        embedVar = discord.Embed(title=f'[ Timer ]',
                                 description=f"for {timer} seconds",
                                 color=0x8b0000)
        await ctx.response.send_message(embed=embedVar, view=view)

        time = 0
        while True:
            await asyncio.sleep(1)
            time += 1
            if time == timer:
                embedEnd = discord.Embed(
                    title=f"Timer ditutup karena waktu habis",
                    description="Sudah abis kak",
                    color=0xffff00)
                await ctx.edit_original_response(embed=embedEnd, view=None)
                break
            if flag:
                break


async def setup(bot):
    await bot.add_cog(Timer(bot))
