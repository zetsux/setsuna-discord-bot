import discord
import os
from discord.ui import Button, View
from discord.ext import commands
from discord import app_commands
import aiohttp

guilds = [
    990445490401341511, 1020927428459241522, 989086863434334279,
    494097970208178186, 1028690906901139486
]

CHATAPIKEY = os.environ['CHATKEY']


class GenerateImg(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name='setsuimg',
        description='Ask Setsuna to generate an image based on the given prompt'
    )
    @app_commands.checks.has_any_role('Encoder Magang', 'Owner')
    @app_commands.describe(prompt="The prompt to generate the image", number="The number of images to generate (max: 10)")
    async def generateImgCommand(
        self, ctx: discord.Interaction,
        prompt: str,
        number: int):
        await ctx.response.defer()

        if number > 10 or number < 1:
            await ctx.followup.send(
                f'Neee anata ngga jelas deh, {ctx.user.name}-nyan',
                ephemeral=True)
            return

        try:
            async with aiohttp.ClientSession() as session:
                pl = {"prompt": prompt, "n": number, "size": f"1024x1024"}
                h = {"Authorization": f"Bearer {CHATAPIKEY}"}

                async with session.post(
                        "https://api.openai.com/v1/images/generations",
                        json=pl,
                        headers=h) as r:
                    response = await r.json()

                    index = 1
                    buttonPP = Button(label='Previous Page',
                                      emoji='👈',
                                      style=discord.ButtonStyle.gray,
                                      row=0)
                    buttonNP = Button(label='Next Page',
                                      emoji='👉',
                                      style=discord.ButtonStyle.gray,
                                      row=0)

                    async def pp_callback(interaction):
                        nonlocal index
                        if index == 1:
                            await interaction.followup.send(
                                f"Neee {interaction.user.name}, ini udah page paling awal loh..",
                                ephemeral=True)
                            return

                        index -= 1
                        embedEd = discord.Embed(color=0x9457EB)
                        embedEd.set_image(url=response["data"][index -
                                                               1]["url"])
                        embedEd.set_footer(
                            text=
                            f"Image : {index}/{number}\nPrompt : {prompt}\nRequested by : {ctx.user.name}",
                            icon_url=ctx.user.avatar.url)
                        await interaction.response.edit_message(embed=embedEd)

                    async def np_callback(interaction):
                        nonlocal index
                        if index == number:
                            await interaction.followup.send(
                                f"Neee {interaction.user.name}, ini udah page paling akhir loh..",
                                ephemeral=True)
                            return

                        index += 1
                        embedEd = discord.Embed(color=0x9457EB)
                        embedEd.set_image(url=response["data"][index -
                                                               1]["url"])
                        embedEd.set_footer(
                            text=
                            f"Image : {index}/{number}\nPrompt : {prompt}\nRequested by : {ctx.user.name}",
                            icon_url=ctx.user.avatar.url)
                        await interaction.response.edit_message(embed=embedEd)

                    buttonPP.callback = pp_callback
                    buttonNP.callback = np_callback
                    inView = View(timeout=600)
                    inView.add_item(buttonPP)
                    inView.add_item(buttonNP)

                    embedVar = discord.Embed(color=0x9457EB)
                    embedVar.set_image(url=response["data"][0]["url"])
                    embedVar.set_footer(
                        text=
                        f"Image : {index}/{number}\nPrompt : {prompt}\nRequested by : {ctx.user.name}",
                        icon_url=ctx.user.avatar.url)
                    imgMsg = await ctx.followup.send(embed=embedVar,
                                                             view=inView)
                    checkView = await inView.wait()

                    if checkView:
                        embedVar = discord.Embed(color=0x9457EB)
                        embedVar.set_image(url=response["data"][index -
                                                                1]["url"])
                        embedVar.set_footer(
                            text=
                            f"Image : {index}/{number}\nPrompt : {prompt}\nRequested by : {ctx.user.name}",
                            icon_url=ctx.user.avatar.url)
                        await imgMsg.edit_original_response(embed=embedVar,
                                                            view=None)

        except Exception as e:
            embedVar = discord.Embed(
                title=f"[ Error!!! ]",
                description=
                f"Maaf, fiturnya lagi error, coba tanya ke yg bikin bot deh.",
                color=0x28282B)
            await ctx.followup.send(embed=embedVar)
            print(e)


async def setup(bot):
    await bot.add_cog(GenerateImg(bot))
