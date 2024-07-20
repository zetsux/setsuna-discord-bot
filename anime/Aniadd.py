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


class Aniadd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name='aniadd',
        description='Add the entered number of anime to the chosen user')
    @app_commands.checks.has_any_role('Encoder Magang', 'Owner')
    @app_commands.describe(name="The name of anime character to add",
                           number="The number of characters to add",
                           member="The user to add to (or self is empty)")
    async def anime_add(self,
                        ctx: discord.Interaction,
                        name: str,
                        number: int,
                        member: discord.Member = None):
        if number <= 0:
            await ctx.response.send_message(
                f'Neee anata ngga jelas deh, {ctx.user.name}-nyan',
                ephemeral=True)
            return

        await ctx.response.defer()

        if not member:
            userID = ctx.user.id
        else:
            userID = member.id

        targetFind = mycol.find_one({"userid": str(userID)})
        mentionTarget = '<@' + str(userID) + '>'
        if targetFind == None:
            await ctx.followup.send(
                f'Neee {mentionTarget}-nyan, yuk /regist yuk, ada yang mau ngegift anata tuhh'
            )

        else:
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
                        "uniAni": mUni,
                        "allAni": mAll + 1,
                        stringIndex:
                        targetFind["animeCount"][animeIndex] + number
                    }
                }
                mycol.update_one(targetFind, newvalues)
                arrangelb(member.id)

            else:
                newvalues = {
                    "$push": {
                        "animeName": name,
                        "animeCount": number
                    },
                    "$set": {
                        "uniAni": mUni + 1,
                        "allAni": mAll + 1
                    }
                }
                mycol.update_one(targetFind, newvalues)
                arrangelb(member.id)

            await ctx.followup.send(
                f'Omedetou {mentionTarget}-nyan! Anata mendapatkan {number} {name}!!'
            )


async def setup(bot):
    await bot.add_cog(Aniadd(bot))
