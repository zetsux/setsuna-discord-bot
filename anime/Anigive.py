import discord
import os
import pymongo
from discord.ext import commands
from discord import app_commands

MONGODB = os.environ['MONGODB']

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]


def arrangelb(idUser):
    inFind = mycol.find_one({'userid': str(idUser)})

    lbFind = mycol.find_one({'func': "anilb"})
    newvalues = {'$pull': {'board': str(idUser)}}
    mycol.update_one(lbFind, newvalues)

    index = 0
    lbFind = mycol.find_one({'func': "anilb"})
    lbBoard = lbFind['board']
    dUni = inFind["uniAni"]
    dAll = inFind["allAni"]

    for i in lbBoard:
        iUser = mycol.find_one({"userid": i})
        iUni = iUser["uniAni"]
        iAll = iUser["allAni"]

        if dUni > iUni or (dUni == iUni and dAll > iAll):
            break

        index += 1

    lbFind = mycol.find_one({'func': "anilb"})
    newvalues = {
        "$push": {
            'board': {
                '$each': [str(idUser)],
                "$position": index
            }
        }
    }
    mycol.update_one(lbFind, newvalues)


class Anigive(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name='anigive',
        description='Give the entered number of anime to the chosen user')
    @app_commands.describe(name="The name of anime character to give",
                           number="The number of characters to give",
                           member="The user to give to")
    async def anime_give(self, ctx: discord.Interaction, name: str,
                         number: int, member: discord.Member):
        if number <= 0:
            await ctx.response.send_message(
                f'Neee anata ngga jelas deh, {ctx.user.name}-nyan',
                ephemeral=True)
            return

        if not member:
            await ctx.response.send_message(
                f'Tagnya yang serius dong, {ctx.user.name}-nyan',
                ephemeral=True)

        elif member.id == ctx.user.id:
            await ctx.response.send_message(
                f'Tagnya yang serius dong, {ctx.user.name}-nyan',
                ephemeral=True)

        else:
            await ctx.response.defer()

            userFind = mycol.find_one({"userid": str(ctx.user.id)})
            if userFind == None:
                await ctx.followup.send(
                    f'Neee {ctx.user.name}-nyan, yuk bisa yuk /regist dulu~',
                    ephemeral=True)

            else:
                targetFind = mycol.find_one({"userid": str(member.id)})
                mentionTarget = '<@' + str(member.id) + '>'
                if targetFind == None:
                    await ctx.followup.send(
                        f'Neee {mentionTarget}-nyan, yuk /regist yuk, ada yang mau ngegift anata tuhh'
                    )

                else:
                    animeInven = userFind["animeName"]
                    mUni = userFind["uniAni"]
                    mAll = userFind["allAni"]
                    if name in animeInven:
                        animeIndex = 0

                        for x in animeInven:
                            if x == name:
                                break
                            animeIndex += 1

                        stringIndex = "animeCount." + str(animeIndex)

                        if userFind["animeCount"][animeIndex] < number:
                            await ctx.followup.send(
                                f'Neee {ctx.user.name}-nyan, anata cuma punya {userFind["animeCount"][animeIndex]} {name}, ngga cukup dong',
                                ephemeral=True)
                            return

                        elif userFind["animeCount"][animeIndex] == number:
                            await ctx.followup.send(
                                f'Omedetou {mentionTarget}-nyan! Anata mendapatkan pemberian seluruh koleksi {name} dari {ctx.user.name}-nyan sejumlah {number}'
                            )
                            mycol.update_one(
                                userFind, {
                                    "$set": {
                                        "uniAni": mUni - 1,
                                        "allAni": mAll - 1,
                                        stringIndex: 0
                                    }
                                })

                        elif userFind["animeCount"][animeIndex] > number:
                            await ctx.followup.send(
                                f'Omedetou {mentionTarget}-nyan! Anata mendapatkan pemberian {number} {name} dari {ctx.user.name}-nyan'
                            )
                            newvalues = {
                                "$set": {
                                    "allAni":
                                    mAll - 1,
                                    stringIndex:
                                    userFind["animeCount"][animeIndex] - number
                                }
                            }
                            mycol.update_one(userFind, newvalues)

                        animeInven = targetFind["animeName"]
                        animeCounting = targetFind["animeCount"]
                        mUni = targetFind["uniAni"]
                        mAll = targetFind["allAni"]
                        if name in animeInven:
                            animeIndex = 0

                            for x in animeInven:
                                if x == name:
                                    break
                                animeIndex += 1

                            if animeCounting[animeIndex] == 0:
                                mUni += 1

                            stringIndex = "animeCount." + str(animeIndex)
                            newvalues = {
                                "$set": {
                                    "uniAni":
                                    mUni,
                                    "allAni":
                                    mAll + 1,
                                    stringIndex:
                                    targetFind["animeCount"][animeIndex] +
                                    number
                                }
                            }
                            mycol.update_one(targetFind, newvalues)

                        else:
                            newvalues = {
                                "$set": {
                                    "uniAni": mUni + 1,
                                    "allAni": mAll + 1,
                                },
                                "$push": {
                                    "animeName": name,
                                    "animeCount": number
                                }
                            }
                            mycol.update_one(targetFind, newvalues)

                        arrangelb(ctx.user.id)
                        arrangelb(member.id)

                    else:
                        await ctx.followup.send(
                            f'Neee {ctx.user.name}-nyan, jangan halu yaa, anata ngga punya yang namanya {name}...\natau salah tulis nama mungkin, coba dicek lagi deh.',
                            ephemeral=True)


async def setup(bot):
    await bot.add_cog(Anigive(bot))
