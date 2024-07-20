import discord
import os
import pymongo
import datetime
from discord.ext import commands
from discord import app_commands
import random

guilds = [
    990445490401341511, 1020927428459241522, 989086863434334279,
    494097970208178186, 1028690906901139486
]

MONGODB = os.environ['MONGODB']

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]


class Hunt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='hunt', description='Hunt for loots once per 10 minutes')
    async def hunting(self, ctx: discord.Interaction):
        userFind = mycol.find_one({"userid": str(ctx.user.id)})

        if userFind == None:
            await ctx.response.send_message(
                f'Neee {ctx.user.name}-nyan, yuk bisa yuk /regist dulu~',
                ephemeral=True)
            return

        now = datetime.datetime.now()
        then = userFind["hunt"]
        duration = now - then
        duration = int(duration.total_seconds())

        if duration < 600:
            duration = 600 - duration
            if duration > 60:
                minLeft = duration / 60
                secLeft = duration % 60
                embedVar = discord.Embed(
                    title=
                    f"Hunt Command for {ctx.user.name}-nyan is still on cooldown...",
                    description=
                    f'Duration Left : {int(minLeft)} minute(s) and {int(secLeft)} second(s)',
                    color=0x808080)

            else:
                embedVar = discord.Embed(
                    title=
                    f"Hunt Command for {ctx.user.name}-nyan is still on cooldown...",
                    description=f'Duration Left : {int(duration)} second(s)',
                    color=0x808080)

            await ctx.response.send_message(embed=embedVar, ephemeral=True)
            return

        await ctx.response.defer()
        randValue = random.randint(0, 100)
        d = datetime.datetime.strptime(
            str(datetime.datetime.now().isoformat()), "%Y-%m-%dT%H:%M:%S.%f")
        if randValue <= 10:
            embedVar = discord.Embed(
                title="Hunt Result by " + ctx.user.name,
                description=
                f'Waduh, {ctx.user.name}-nyan menemukan seorang loli yang tengah menari-nari dan malah menghabiskan waktunya memandanginya..',
                color=0x808080)
            loliGifs = [
                'https://cdn.discordapp.com/attachments/995337235211763722/1014927108633542656/loli30.gif',
                'https://cdn.discordapp.com/attachments/995337235211763722/1014933310612443246/loli29n.gif',
                'https://cdn.discordapp.com/attachments/995337235211763722/1014927109258498078/loli28.gif',
                'https://cdn.discordapp.com/attachments/995337235211763722/1014927109594038312/loli27.gif',
                'https://cdn.discordapp.com/attachments/995337235211763722/1014927109904404621/loli26.gif',
                'https://cdn.discordapp.com/attachments/995337235211763722/1014927110244139018/loli25.gif',
                'https://cdn.discordapp.com/attachments/995337235211763722/1014927110730694656/loli24.gif',
                'https://cdn.discordapp.com/attachments/995337235211763722/1014927111041069167/loli23.gif',
                'https://cdn.discordapp.com/attachments/995337235211763722/1014927111368212490/loli22.gif',
                'https://cdn.discordapp.com/attachments/995337235211763722/1014927111938646138/loli21.gif',
                'https://cdn.discordapp.com/attachments/995337235211763722/1014928168659988580/loli20.gif',
                'https://cdn.discordapp.com/attachments/995337235211763722/1014928169071026226/loli19.gif',
                'https://cdn.discordapp.com/attachments/995337235211763722/1014928169553375282/loli18.gif',
                'https://cdn.discordapp.com/attachments/995337235211763722/1014928169884717096/loli17.gif',
                'https://cdn.discordapp.com/attachments/995337235211763722/1014928170190897233/loli16.gif',
                'https://cdn.discordapp.com/attachments/995337235211763722/1014928170509668404/loli15.gif',
                'https://cdn.discordapp.com/attachments/995337235211763722/1014928170941698098/loli14.gif',
                'https://cdn.discordapp.com/attachments/995337235211763722/1014928171252072498/loli13.gif',
                'https://cdn.discordapp.com/attachments/995337235211763722/1014928171570831481/loli12.gif',
                'https://cdn.discordapp.com/attachments/995337235211763722/1014928171897978962/loli11.gif',
                'https://cdn.discordapp.com/attachments/995337235211763722/1014928666100240504/loli10.gif',
                'https://cdn.discordapp.com/attachments/995337235211763722/1014928666582597632/loli9.gif',
                'https://cdn.discordapp.com/attachments/995337235211763722/1014928666964275230/loli8.gif',
                'https://cdn.discordapp.com/attachments/995337235211763722/1014928667450810388/loli7.gif',
                'https://cdn.discordapp.com/attachments/995337235211763722/1014928667853467688/loli6.gif',
                'https://cdn.discordapp.com/attachments/995337235211763722/1014928668226768916/loli5.gif',
                'https://cdn.discordapp.com/attachments/995337235211763722/1014928668730073118/loli4.gif',
                'https://cdn.discordapp.com/attachments/995337235211763722/1014928669489254511/loli3.gif',
                'https://cdn.discordapp.com/attachments/995337235211763722/1014928670114193409/loli2.gif',
                'https://cdn.discordapp.com/attachments/995337235211763722/1014928669027860601/loli1.gif'
            ]

            gifLink = random.choice(loliGifs)
            embedVar.set_thumbnail(url=gifLink)
            newvalues = {"$set": {"hunt": d}}

        elif randValue <= 50:
            goldCount = userFind["gold"] + 20
            number = 2
            xpCount = userFind["exp"]
            levelCount = userFind["level"]
            if number < ((levelCount * 2) - xpCount):
                xpCount += number
                newvalues = {
                    "$set": {
                        "exp": xpCount,
                        "gold": goldCount,
                        "hunt": d
                    }
                }

            else:
                number -= ((levelCount * 2) - xpCount)
                levelCount += 1

                while number >= (levelCount * 2):
                    number -= (levelCount * 2)
                    levelCount += 1

                xpCount = number
                newvalues = {
                    "$set": {
                        "level": levelCount,
                        "exp": xpCount,
                        "gold": goldCount,
                        "hunt": d
                    }
                }

            embedVar = discord.Embed(
                title="Hunt Result by " + ctx.user.name,
                description=
                f'Agak miris, {ctx.user.name}-nyan hanya berhasil membunuh satu slime dan mendapat 20 Gold dan 2 EXP',
                color=0x32cd32)
            embedVar.set_thumbnail(
                url=
                "https://cdn.discordapp.com/attachments/995337235211763722/1014523086890078278/slimy.gif"
            )

        elif randValue <= 75:
            goldCount = userFind["gold"] + 40
            number = 4
            xpCount = userFind["exp"]
            levelCount = userFind["level"]
            if number < ((levelCount * 2) - xpCount):
                xpCount += number
                newvalues = {
                    "$set": {
                        "exp": xpCount,
                        "gold": goldCount,
                        "hunt": d
                    }
                }

            else:
                number -= ((levelCount * 2) - xpCount)
                levelCount += 1

                while number >= (levelCount * 2):
                    number -= (levelCount * 2)
                    levelCount += 1

                xpCount = number
                newvalues = {
                    "$set": {
                        "level": levelCount,
                        "exp": xpCount,
                        "gold": goldCount,
                        "hunt": d
                    }
                }

            embedVar = discord.Embed(
                title="Hunt Result by " + ctx.user.name,
                description=
                f'Walau tak seberapa, {ctx.user.name}-nyan setidaknya berhasil membunuh satu goblin dan mendapat 40 Gold dan 4 EXP',
                color=0x877a23)
            embedVar.set_thumbnail(
                url=
                "https://cdn.discordapp.com/attachments/995337235211763722/1014500269360414731/goblin.gif"
            )

        elif randValue <= 90:
            goldCount = userFind["gold"] + 70
            number = 6
            xpCount = userFind["exp"]
            levelCount = userFind["level"]
            if number < ((levelCount * 2) - xpCount):
                xpCount += number
                newvalues = {
                    "$set": {
                        "exp": xpCount,
                        "gold": goldCount,
                        "hunt": d
                    }
                }

            else:
                number -= ((levelCount * 2) - xpCount)
                levelCount += 1

                while number >= (levelCount * 2):
                    number -= (levelCount * 2)
                    levelCount += 1

                xpCount = number
                newvalues = {
                    "$set": {
                        "level": levelCount,
                        "exp": xpCount,
                        "gold": goldCount,
                        "hunt": d
                    }
                }

            embedVar = discord.Embed(
                title="Hunt Result by " + ctx.user.name,
                description=
                f'Sedikit beruntung, {ctx.user.name}-nyan berhasil membunuh satu skeleton dan mendapat 70 Gold dan 6 EXP',
                color=0x6699cc)
            embedVar.set_thumbnail(
                url=
                "https://cdn.discordapp.com/attachments/995337235211763722/1014513523910512720/skeleviolin.gif"
            )

        elif randValue <= 96:
            goldCount = userFind["gold"] + 100
            number = 10
            xpCount = userFind["exp"]
            levelCount = userFind["level"]
            if number < ((levelCount * 2) - xpCount):
                xpCount += number
                newvalues = {
                    "$set": {
                        "exp": xpCount,
                        "gold": goldCount,
                        "hunt": d
                    }
                }

            else:
                number -= ((levelCount * 2) - xpCount)
                levelCount += 1

                while number >= (levelCount * 2):
                    number -= (levelCount * 2)
                    levelCount += 1

                xpCount = number
                newvalues = {
                    "$set": {
                        "level": levelCount,
                        "exp": xpCount,
                        "gold": goldCount,
                        "hunt": d
                    }
                }

            embedVar = discord.Embed(
                title="Hunt Result by " + ctx.user.name,
                description=
                f'Berusaha lumayan keras, {ctx.user.name}-nyan akhirnya berhasil membunuh satu ogre dan mendapat 100 Gold dan 10 EXP',
                color=0xbdb369)
            embedVar.set_thumbnail(
                url=
                "https://cdn.discordapp.com/attachments/995337235211763722/1014922579745722408/shrekik.gif"
            )

        elif randValue <= 99:
            goldCount = userFind["gold"] + 200
            number = 14
            xpCount = userFind["exp"]
            levelCount = userFind["level"]
            if number < ((levelCount * 2) - xpCount):
                xpCount += number
                newvalues = {
                    "$set": {
                        "exp": xpCount,
                        "gold": goldCount,
                        "hunt": d
                    }
                }

            else:
                number -= ((levelCount * 2) - xpCount)
                levelCount += 1

                while number >= (levelCount * 2):
                    number -= (levelCount * 2)
                    levelCount += 1

                xpCount = number
                newvalues = {
                    "$set": {
                        "level": levelCount,
                        "exp": xpCount,
                        "gold": goldCount,
                        "hunt": d
                    }
                }

            embedVar = discord.Embed(
                title="Hunt Result by " + ctx.user.name,
                description=
                f'Wah ngeri, {ctx.user.name}-nyan dengan kerennya berhasil membunuh satu golem dan mendapat 200 Gold dan 14 EXP',
                color=0x9d00ff)
            embedVar.set_thumbnail(
                url=
                "https://cdn.discordapp.com/attachments/995337235211763722/1014523953764647014/golemm.gif"
            )

        elif randValue <= 100:
            goldCount = userFind["gold"] + 600
            number = 20
            xpCount = userFind["exp"]
            levelCount = userFind["level"]
            if number < ((levelCount * 2) - xpCount):
                xpCount += number
                newvalues = {
                    "$set": {
                        "exp": xpCount,
                        "gold": goldCount,
                        "hunt": d
                    }
                }

            else:
                number -= ((levelCount * 2) - xpCount)
                levelCount += 1

                while number >= (levelCount * 2):
                    number -= (levelCount * 2)
                    levelCount += 1

                xpCount = number
                newvalues = {
                    "$set": {
                        "level": levelCount,
                        "exp": xpCount,
                        "gold": goldCount,
                        "hunt": d
                    }
                }

            embedVar = discord.Embed(
                title="Hunt Result by " + ctx.user.name,
                description=
                f"JACKPOT!! {ctx.user.name}-nyan berhasil mengalahkan seekor naga api dan menjual kepalanya seharga 600 Gold dan 20 EXP",
                color=0xf73718)
            embedVar.set_thumbnail(
                url=
                "https://cdn.discordapp.com/attachments/995337235211763722/1014922986442211338/drago.gif"
            )

        embedVar.set_footer(text="Cooldown : 10 Minutes",
                            icon_url=ctx.user.avatar.url)
        await ctx.followup.send(embed=embedVar)
        mycol.update_one(userFind, newvalues)


async def setup(bot):
    await bot.add_cog(Hunt(bot))
