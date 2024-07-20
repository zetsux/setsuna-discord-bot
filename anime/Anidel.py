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


class Anidel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name='anidel',
        description=
        'Delete anime from your inventory with count is entered number')
    @app_commands.describe(name="The name of anime character to delete",
                           number="The number of characters to delete")
    async def anime_remove(self, ctx: discord.Interaction, name: str,
                           number: int):
        if number <= 0:
            await ctx.response.send_message(
                f'Neee anata ngga jelas deh, {ctx.user.name}-nyan',
                ephemeral=True)
            return

        await ctx.response.defer()

        userFind = mycol.find_one({"userid": str(ctx.user.id)})
        if userFind == None:
            await ctx.followup.send(
                f'Neee {ctx.user.name}-nyan, yuk bisa yuk /regist dulu~',
                ephemeral=True)

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

                if userFind["animeCount"][animeIndex] < number:
                    await ctx.followup.send(
                        f'Neee {ctx.user.name}-nyan, anata cuma punya {userFind["animeCount"][animeIndex]} {name}',
                        ephemeral=True)

                elif userFind["animeCount"][animeIndex] == number:
                    await ctx.followup.send(
                        f'Omedetou {ctx.user.name}-nyan, penghapusan {number} {name} berhasil. Menghapuskan seluruh koleksi {name} anata'
                    )
                    stringIndex = "animeCount." + str(animeIndex)
                    mycol.update_one(
                        userFind, {
                            "$set": {
                                "uniAni": mUni - 1,
                                "allAni": mAll - 1,
                                stringIndex: 0
                            }
                        })
                    arrangelb(ctx.user.id)

                elif userFind["animeCount"][animeIndex] > number:
                    await ctx.followup.send(
                        f'Omedetou {ctx.user.name}-nyan, penghapusan {number} {name} berhasil. Membuat jumlah koleksi {name} anata tersisa {userFind["animeCount"][animeIndex] - number}'
                    )

                    stringIndex = "animeCount." + str(animeIndex)
                    newvalues = {
                        "$set": {
                            "allAni":
                            mAll - 1,
                            stringIndex:
                            userFind["animeCount"][animeIndex] - number
                        }
                    }
                    mycol.update_one(userFind, newvalues)
                    arrangelb(ctx.user.id)

            else:
                await ctx.followup.send(
                    f'Neee {ctx.user.name}-nyan, jangan halu yaa, anata ngga punya yang namanya {name}...\natau salah tulis nama mungkin, coba dicek lagi deh.',
                    ephemeral=True)


async def setup(bot):
    await bot.add_cog(Anidel(bot))
