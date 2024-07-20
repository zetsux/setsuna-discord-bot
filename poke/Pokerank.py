import discord
import os
import pymongo
from discord.ext import commands
from discord import app_commands

MONGODB = os.environ['MONGODB']

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]


class Pokerank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name='pokerank',
        description='Check the leaderboard for pokeduel Ranking')
    async def poke_rank(self, ctx: discord.Interaction):
        targetFind = mycol.find_one({"userid": str(ctx.user.id)})
        mentionTarget = '<@' + str(ctx.user.id) + '>'
        if targetFind == None:
            await ctx.response.send_message(
                f'Neee {mentionTarget}-nyan, yuk /regist yuk, ada yang mau ngegift anata tuhh'
            )

        else:
            await ctx.response.defer()
            pokeLB = mycol.find_one({"func": "duellb"})
            pokeBoard = pokeLB["board"]

            lbString = "```"

            rank = 1
            noSelf = True
            for id in pokeBoard:
                try:
                    user = self.bot.get_user(int(id))
                    username = user.name
                except:
                    continue

                if rank <= 10:
                    if id == str(ctx.user.id):
                        wUser = targetFind["win"]
                        lUser = targetFind["lose"]
                        dUser = targetFind["draw"]
                        lbString += f"{rank}) {username} (You) [{wUser}/{lUser}/{dUser}]\n"
                        noSelf = False

                    else:
                        userFind = mycol.find_one({"userid": id})
                        wUser = userFind["win"]
                        lUser = userFind["lose"]
                        dUser = userFind["draw"]
                        lbString += f"{rank}) {username} [{wUser}/{lUser}/{dUser}]\n"

                elif noSelf:
                    if id == str(ctx.user.id):
                        wUser = targetFind["win"]
                        lUser = targetFind["lose"]
                        dUser = targetFind["draw"]

                        if rank == 17:
                            lbString += ".\n"

                        elif rank == 18:
                            lbString += ".\n.\n"

                        else:
                            lbString += ".\n.\n.\n"

                        lbString += f"{rank}) {username} (You) [{wUser}/{lUser}/{dUser}]\n"
                        noSelf = False

                else:
                    break

                rank += 1

            embedVar = discord.Embed(title="「 Poke Duelist Leaderboard 」",
                                     description=f"{lbString}```\n",
                                     color=0xFFD700)
            embedVar.set_thumbnail(
                url=
                'https://cdn.discordapp.com/attachments/995337235211763722/1033610224445177856/slowpoke-pokemon.gif'
            )
            embedVar.set_footer(
                text="Note :\n[Win Count/Lose Count/Draw Count]",
                icon_url=ctx.user.avatar.url)
            await ctx.followup.send(embed=embedVar)


async def setup(bot):
    await bot.add_cog(Pokerank(bot))
