import discord
import os
from discord.ext import commands
from discord import app_commands
import aiohttp
import typing

guilds = [
    990445490401341511, 1020927428459241522, 989086863434334279,
    494097970208178186, 1028690906901139486
]

CHATAPIKEY = os.environ['CHATKEY']


class Chat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name='setsuchat',
        description='Chat with and Ask Setsuna to answer or even do things')
    @app_commands.describe(prompt="The chat to send",
                           answer="The form of the answer")
    async def chatCommand(
            self,
            ctx: discord.Interaction,
            prompt: str,
            answer: typing.Literal["Normal Chat",
                                   "Code Blocks"] = "Normal Chat"):
        await ctx.response.defer()
        try:
            async with aiohttp.ClientSession() as session:
                pl = {
                    "model": "text-davinci-003",
                    "prompt": prompt,
                    "temperature": 0.5,
                    "max_tokens": 4000,
                    "presence_penalty": 0,
                    "frequency_penalty": 0,
                    "best_of": 1,
                }
                h = {"Authorization": f"Bearer {CHATAPIKEY}"}

                async with session.post(
                        "https://api.openai.com/v1/completions",
                        json=pl,
                        headers=h) as r:
                    response = await r.json()

                    if answer == "Normal Chat":
                        await ctx.followup.send(response["choices"][0]["text"])

                    else:
                        embedVar = discord.Embed(
                            description="```" +
                            response["choices"][0]["text"] + "```",
                            color=0x9457EB)
                        await ctx.followup.send(embed=embedVar)

        except Exception as e:
            embedVar = discord.Embed(
                title=f"[ Error!!! ]",
                description=
                f"Maaf, fiturnya lagi error, coba tanya ke yg bikin bot deh.",
                color=0x28282B)
            await ctx.followup.send(embed=embedVar)
            print(e)


async def setup(bot):
    await bot.add_cog(Chat(bot))
