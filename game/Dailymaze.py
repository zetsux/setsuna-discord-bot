import discord
import os
import pymongo
import datetime
from discord.ui import Button, View
from discord.ext import commands
from discord import app_commands
import pytz
import random

guilds = [
    990445490401341511, 1020927428459241522, 989086863434334279,
    494097970208178186, 1028690906901139486
]

MONGODB = os.environ['MONGODB']

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]

row = 10
col = 10


def isPath(arr):
    Dir = [[0, 1], [0, -1], [1, 0], [-1, 0]]
    q = []
    q.append((0, 0))

    while (len(q) > 0):
        p = q[0]
        q.pop(0)
        arr[p[0]][p[1]] = -1
        if (p == (row - 1, col - 1)):
            return True

        for i in range(4):
            a = p[0] + Dir[i][0]
            b = p[1] + Dir[i][1]
            if (a >= 0 and b >= 0 and a < row and b < col and arr[a][b] != -1):
                q.append((a, b))
    return False


class Dailymaze(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name='dailymaze',
        description='Play in daily minigame from level 1-7 with different prizes'
    )
    @app_commands.describe(level="The level of difficulty (1-7)")
    async def daily_dungeon(self, ctx: discord.Interaction, level: int):
        if level <= 0:
            await ctx.response.send_message(
                f'Sumpa gajelas lu {ctx.user.name}-nyan', ephemeral=True)
            return

        elif level > 7:
            await ctx.response.send_message(
                f'Kegedean bro {ctx.user.name}-nyan, levelnya cuma 1-7',
                ephemeral=True)
            return

        userFind = mycol.find_one({"userid": str(ctx.user.id)})
        indoTz = pytz.timezone("Asia/Jakarta")
        nowDay = datetime.datetime.now(indoTz)
        # print(str(nowDay.hour) + '/' + str(nowDay.minute) + '/' + str(nowDay.second))
        currentDay = str(nowDay.day) + '/' + str(nowDay.month) + '/' + str(
            nowDay.year)

        if userFind == None:
            await ctx.response.send_message(
                f'Neee {ctx.user.name}-nyan, yuk bisa yuk /regist dulu~',
                ephemeral=True)
            return

        if currentDay == userFind['daily']:
            await ctx.response.send_message(
                f'Neee {ctx.user.name}-nyan, hari ini kan anata udah pake /dailymaze, besok lagi yaa~',
                ephemeral=True)
            return

        await ctx.response.defer()
        global row, col
        row = level * 2
        col = level * 2
        button1 = Button(label=' ',
                         style=discord.ButtonStyle.gray,
                         disabled=True,
                         row=0)
        buttonU = Button(emoji='⬆', style=discord.ButtonStyle.primary, row=0)
        button3 = Button(label=' ',
                         style=discord.ButtonStyle.gray,
                         disabled=True,
                         row=0)
        buttonL = Button(emoji='⬅️', style=discord.ButtonStyle.primary, row=1)
        button5 = Button(emoji='🕹️',
                         style=discord.ButtonStyle.green,
                         disabled=True,
                         row=1)
        buttonR = Button(emoji='➡️', style=discord.ButtonStyle.primary, row=1)
        button7 = Button(label=' ',
                         style=discord.ButtonStyle.gray,
                         disabled=True,
                         row=2)
        buttonD = Button(emoji="⬇️", style=discord.ButtonStyle.primary, row=2)
        button9 = Button(label=' ',
                         style=discord.ButtonStyle.gray,
                         disabled=True,
                         row=2)

        dgMap = [[0 for x in range(row)] for y in range(col)]
        arr = [[0 for x in range(row)] for y in range(col)]

        for x in range(row):
            for y in range(col):
                num = random.randint(-1, 0)
                dgMap[x][y] = num
                arr[x][y] = num

        dgMap[0][0] = 0
        dgMap[row - 1][col - 1] = 0
        arr[0][0] = 0
        arr[row - 1][col - 1] = 0

        while isPath(arr) is not True:
            for x in range(row):
                for y in range(col):
                    num = random.randint(-1, 0)
                    dgMap[x][y] = num
                    arr[x][y] = num

            dgMap[0][0] = 0
            dgMap[row - 1][col - 1] = 0
            arr[0][0] = 0
            arr[row - 1][col - 1] = 0

        dungeonArea = [[0 for x in range(row)] for y in range(col)]

        for x in range(row):
            for y in range(col):
                if dgMap[x][y] == 0:
                    dungeonArea[x][y] = '◻️'
                elif dgMap[x][y] == -1:
                    dungeonArea[x][y] = '🔥'

        dungeonArea[0][0] = '😨'
        dungeonArea[row - 1][col - 1] = '🎁'
        xPos = 0
        yPos = 0

        # for x in range(row):
        #   print(dungeonArea[x])
        async def left_callback(interaction):
            if interaction.user.id != ctx.user.id:
                await interaction.response.send_message(
                    f"Neeee, itu maze punya {ctx.user.name}-nyan, kalau mau main /dailymaze sendiri deh ya {interaction.user.name}-nyan~",
                    ephemeral=True)
            else:
                nonlocal yPos, xPos
                if yPos - 1 == row - 1 and xPos == col - 1:
                    dungeonArea[xPos][yPos] = '◻️'
                    dungeonArea[row - 1][col - 1] = '😊'

                    rtMap = ""
                    for x in range(row):
                        if x > 0:
                            rtMap = rtMap + '\n'
                        for y in range(col):
                            rtMap = rtMap + dungeonArea[x][y]

                    embedEdit = discord.Embed(
                        title=f"— Daily Maze —",
                        description="You've reached the prize!",
                        color=ctx.user.color)
                    embedEdit.add_field(name="[ Map ]",
                                        value=rtMap,
                                        inline=False)
                    embedEdit.set_footer(
                        text="Resets daily at 00:00 WIB (GMT+7)")
                    embedEdit.set_author(name=interaction.user.name,
                                         icon_url=interaction.user.avatar.url)
                    await interaction.response.edit_message(
                        content=
                        f"Omedetou! {ctx.user.name}-nyan berhasil memenangkan {level*50} Gold dan mendapat {level*3} EXP dari Dungeon",
                        embed=embedEdit,
                        view=None)
                    goldCount = userFind["gold"] + (level * 50)
                    number = level * 3
                    xpCount = userFind["exp"]
                    levelCount = userFind["level"]
                    if number < ((levelCount * 2) - xpCount):
                        xpCount += number
                        newvalues = {
                            "$set": {
                                "exp": xpCount,
                                "gold": goldCount,
                                "daily": currentDay
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
                                "daily": currentDay
                            }
                        }

                    mycol.update_one(userFind, newvalues)
                    view.stop()

                elif yPos > 0 and dungeonArea[xPos][yPos - 1] == '🔥':
                    dungeonArea[xPos][yPos] = '💀'
                    rtMap = ""
                    for x in range(row):
                        if x > 0:
                            rtMap = rtMap + '\n'
                        for y in range(col):
                            rtMap = rtMap + dungeonArea[x][y]

                    embedEdit = discord.Embed(
                        title=f"— Daily Maze —",
                        description=
                        "You've died... ( Cause : Running into fire )",
                        color=ctx.user.color)
                    embedEdit.add_field(name="[ Map ]",
                                        value=rtMap,
                                        inline=False)
                    embedEdit.set_footer(
                        text="Resets daily at 00:00 WIB (GMT+7)")
                    embedEdit.set_author(name=interaction.user.name,
                                         icon_url=interaction.user.avatar.url)
                    await interaction.response.edit_message(
                        content=
                        f"Aduhh {ctx.user.name}-nyan, bisa-bisanya masuk ke api..",
                        embed=embedEdit,
                        view=None)
                    newvalues = {"$set": {"daily": currentDay}}
                    mycol.update_one(userFind, newvalues)
                    view.stop()

                elif yPos > 0 and dungeonArea[xPos][yPos - 1] == '◻️':
                    dungeonArea[xPos][yPos] = '◻️'
                    yPos -= 1
                    dungeonArea[xPos][yPos] = '😨'

                    rtMap = ""
                    for x in range(row):
                        if x > 0:
                            rtMap = rtMap + '\n'
                        for y in range(col):
                            rtMap = rtMap + dungeonArea[x][y]

                    embedEdit = discord.Embed(
                        title=f"— Daily Maze —",
                        description=
                        "Travel to the prize using buttons rapidly without going into the fire",
                        color=ctx.user.color)
                    embedEdit.add_field(name="[ Map ]",
                                        value=rtMap,
                                        inline=False)
                    embedEdit.set_author(name=interaction.user.name,
                                         icon_url=interaction.user.avatar.url)
                    await interaction.response.edit_message(embed=embedEdit)

                else:
                    await interaction.response.defer()

        async def up_callback(interaction):
            if interaction.user.id != ctx.user.id:
                await interaction.response.send_message(
                    f"Neeee, itu maze punya {ctx.user.name}-nyan, kalau mau main /dailymaze sendiri deh ya {interaction.user.name}-nyan~",
                    ephemeral=True)
            else:
                nonlocal yPos, xPos
                if xPos - 1 == row - 1 and yPos == col - 1:
                    dungeonArea[xPos][yPos] = '◻️'
                    dungeonArea[row - 1][col - 1] = '😊'

                    rtMap = ""
                    for x in range(row):
                        if x > 0:
                            rtMap = rtMap + '\n'
                        for y in range(col):
                            rtMap = rtMap + dungeonArea[x][y]

                    embedEdit = discord.Embed(
                        title=f"— Daily Maze —",
                        description="You've reached the prize!",
                        color=ctx.user.color)
                    embedEdit.add_field(name="[ Map ]",
                                        value=rtMap,
                                        inline=False)
                    embedEdit.set_footer(
                        text="Resets daily at 00:00 WIB (GMT+7)")
                    embedEdit.set_author(name=interaction.user.name,
                                         icon_url=interaction.user.avatar.url)
                    await interaction.response.edit_message(
                        content=
                        f"Omedetou! {ctx.user.name}-nyan berhasil memenangkan {level*50} Gold dan mendapat {level*3} EXP dari Dungeon",
                        embed=embedEdit,
                        view=None)
                    goldCount = userFind["gold"] + (level * 50)
                    number = level * 3
                    xpCount = userFind["exp"]
                    levelCount = userFind["level"]
                    if number < ((levelCount * 2) - xpCount):
                        xpCount += number
                        newvalues = {
                            "$set": {
                                "exp": xpCount,
                                "gold": goldCount,
                                "daily": currentDay
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
                                "daily": currentDay
                            }
                        }

                    mycol.update_one(userFind, newvalues)
                    view.stop()

                elif xPos > 0 and dungeonArea[xPos - 1][yPos] == '🔥':
                    dungeonArea[xPos][yPos] = '💀'
                    rtMap = ""
                    for x in range(row):
                        if x > 0:
                            rtMap = rtMap + '\n'
                        for y in range(col):
                            rtMap = rtMap + dungeonArea[x][y]

                    embedEdit = discord.Embed(
                        title=f"— Daily Maze —",
                        description=
                        "You've died... ( Cause : Running into fire )",
                        color=ctx.user.color)
                    embedEdit.add_field(name="[ Map ]",
                                        value=rtMap,
                                        inline=False)
                    embedEdit.set_footer(
                        text="Resets daily at 00:00 WIB (GMT+7)")
                    embedEdit.set_author(name=interaction.user.name,
                                         icon_url=interaction.user.avatar.url)
                    await interaction.response.edit_message(
                        content=
                        f"Aduhh {ctx.user.name}-nyan, bisa-bisanya masuk ke api..",
                        embed=embedEdit,
                        view=None)
                    newvalues = {"$set": {"daily": currentDay}}
                    mycol.update_one(userFind, newvalues)
                    view.stop()

                elif xPos > 0 and dungeonArea[xPos - 1][yPos] == '◻️':
                    dungeonArea[xPos][yPos] = '◻️'
                    xPos -= 1
                    dungeonArea[xPos][yPos] = '😨'

                    rtMap = ""
                    for x in range(row):
                        if x > 0:
                            rtMap = rtMap + '\n'
                        for y in range(col):
                            rtMap = rtMap + dungeonArea[x][y]

                    embedEdit = discord.Embed(
                        title=f"— Daily Maze —",
                        description=
                        "Travel to the prize using buttons rapidly without going into the fire",
                        color=ctx.user.color)
                    embedEdit.add_field(name="[ Map ]",
                                        value=rtMap,
                                        inline=False)
                    embedEdit.set_author(name=interaction.user.name,
                                         icon_url=interaction.user.avatar.url)
                    await interaction.response.edit_message(embed=embedEdit)

                else:
                    await interaction.response.defer()

        async def down_callback(interaction):
            if interaction.user.id != ctx.user.id:
                await interaction.response.send_message(
                    f"Neeee, itu maze punya {ctx.user.name}-nyan, kalau mau main /dailymaze sendiri deh ya {interaction.user.name}-nyan~",
                    ephemeral=True)
            else:
                nonlocal yPos, xPos
                if xPos + 1 == row - 1 and yPos == col - 1:
                    dungeonArea[xPos][yPos] = '◻️'
                    dungeonArea[row - 1][col - 1] = '😊'

                    rtMap = ""
                    for x in range(row):
                        if x > 0:
                            rtMap = rtMap + '\n'
                        for y in range(col):
                            rtMap = rtMap + dungeonArea[x][y]

                    embedEdit = discord.Embed(
                        title=f"— Daily Maze —",
                        description="You've reached the prize!",
                        color=ctx.user.color)
                    embedEdit.add_field(name="[ Map ]",
                                        value=rtMap,
                                        inline=False)
                    embedEdit.set_footer(
                        text="Resets daily at 00:00 WIB (GMT+7)")
                    embedEdit.set_author(name=interaction.user.name,
                                         icon_url=interaction.user.avatar.url)
                    await interaction.response.edit_message(
                        content=
                        f"Omedetou! {ctx.user.name}-nyan berhasil memenangkan {level*50} Gold dan mendapat {level*3} EXP dari Dungeon",
                        embed=embedEdit,
                        view=None)
                    goldCount = userFind["gold"] + (level * 50)
                    number = level * 3
                    xpCount = userFind["exp"]
                    levelCount = userFind["level"]
                    if number < ((levelCount * 2) - xpCount):
                        xpCount += number
                        newvalues = {
                            "$set": {
                                "exp": xpCount,
                                "gold": goldCount,
                                "daily": currentDay
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
                                "daily": currentDay
                            }
                        }

                    mycol.update_one(userFind, newvalues)
                    view.stop()

                elif xPos < row - 1 and dungeonArea[xPos + 1][yPos] == '🔥':
                    dungeonArea[xPos][yPos] = '💀'
                    rtMap = ""
                    for x in range(row):
                        if x > 0:
                            rtMap = rtMap + '\n'
                        for y in range(col):
                            rtMap = rtMap + dungeonArea[x][y]

                    embedEdit = discord.Embed(
                        title=f"— Daily Maze —",
                        description=
                        "You've died... ( Cause : Running into fire )",
                        color=ctx.user.color)
                    embedEdit.add_field(name="[ Map ]",
                                        value=rtMap,
                                        inline=False)
                    embedEdit.set_footer(
                        text="Resets daily at 00:00 WIB (GMT+7)")
                    embedEdit.set_author(name=interaction.user.name,
                                         icon_url=interaction.user.avatar.url)
                    await interaction.response.edit_message(
                        content=
                        f"Aduhh {ctx.user.name}-nyan, bisa-bisanya masuk ke api..",
                        embed=embedEdit,
                        view=None)
                    newvalues = {"$set": {"daily": currentDay}}
                    mycol.update_one(userFind, newvalues)
                    view.stop()

                elif xPos < row - 1 and dungeonArea[xPos + 1][yPos] == '◻️':
                    dungeonArea[xPos][yPos] = '◻️'
                    xPos += 1
                    dungeonArea[xPos][yPos] = '😨'

                    rtMap = ""
                    for x in range(row):
                        if x > 0:
                            rtMap = rtMap + '\n'
                        for y in range(col):
                            rtMap = rtMap + dungeonArea[x][y]

                    embedEdit = discord.Embed(
                        title=f"— Daily Maze —",
                        description=
                        "Travel to the prize using buttons rapidly without going into the fire",
                        color=ctx.user.color)
                    embedEdit.add_field(name="[ Map ]",
                                        value=rtMap,
                                        inline=False)
                    embedEdit.set_author(name=interaction.user.name,
                                         icon_url=interaction.user.avatar.url)
                    await interaction.response.edit_message(embed=embedEdit)

                else:
                    await interaction.response.defer()

        async def right_callback(interaction):
            if interaction.user.id != ctx.user.id:
                await interaction.response.send_message(
                    f"Neeee, itu maze punya {ctx.user.name}-nyan, kalau mau main /dailymaze sendiri deh ya {interaction.user.name}-nyan~",
                    ephemeral=True)
            else:
                nonlocal yPos, xPos
                if yPos + 1 == row - 1 and xPos == col - 1:
                    dungeonArea[xPos][yPos] = '◻️'
                    dungeonArea[row - 1][col - 1] = '😊'

                    rtMap = ""
                    for x in range(row):
                        if x > 0:
                            rtMap = rtMap + '\n'
                        for y in range(col):
                            rtMap = rtMap + dungeonArea[x][y]

                    embedEdit = discord.Embed(
                        title=f"— Daily Maze —",
                        description="You've reached the prize!",
                        color=ctx.user.color)
                    embedEdit.add_field(name="[ Map ]",
                                        value=rtMap,
                                        inline=False)
                    embedEdit.set_footer(
                        text="Resets daily at 00:00 WIB (GMT+7)")
                    embedEdit.set_author(name=interaction.user.name,
                                         icon_url=interaction.user.avatar.url)
                    await interaction.response.edit_message(
                        content=
                        f"Omedetou! {ctx.user.name}-nyan berhasil memenangkan {level*50} Gold dan mendapat {level*3} EXP dari Dungeon",
                        embed=embedEdit,
                        view=None)
                    goldCount = userFind["gold"] + (level * 50)
                    number = level * 3
                    xpCount = userFind["exp"]
                    levelCount = userFind["level"]
                    if number < ((levelCount * 2) - xpCount):
                        xpCount += number
                        newvalues = {
                            "$set": {
                                "exp": xpCount,
                                "gold": goldCount,
                                "daily": currentDay
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
                                "daily": currentDay
                            }
                        }

                    mycol.update_one(userFind, newvalues)
                    view.stop()

                elif yPos < row - 1 and dungeonArea[xPos][yPos + 1] == '🔥':
                    dungeonArea[xPos][yPos] = '💀'
                    rtMap = ""
                    for x in range(row):
                        if x > 0:
                            rtMap = rtMap + '\n'
                        for y in range(col):
                            rtMap = rtMap + dungeonArea[x][y]

                    embedEdit = discord.Embed(
                        title=f"— Daily Maze —",
                        description=
                        "You've died... ( Cause : Running into fire )",
                        color=ctx.user.color)
                    embedEdit.add_field(name="[ Map ]",
                                        value=rtMap,
                                        inline=False)
                    embedEdit.set_footer(
                        text="Resets daily at 00:00 WIB (GMT+7)")
                    embedEdit.set_author(name=interaction.user.name,
                                         icon_url=interaction.user.avatar.url)
                    await interaction.response.edit_message(
                        content=
                        f"Aduhh {ctx.user.name}-nyan, bisa-bisanya masuk ke api..",
                        embed=embedEdit,
                        view=None)
                    newvalues = {"$set": {"daily": currentDay}}
                    mycol.update_one(userFind, newvalues)
                    view.stop()

                elif yPos < row - 1 and dungeonArea[xPos][yPos + 1] == '◻️':
                    dungeonArea[xPos][yPos] = '◻️'
                    yPos += 1
                    dungeonArea[xPos][yPos] = '😨'

                    rtMap = ""
                    for x in range(row):
                        if x > 0:
                            rtMap = rtMap + '\n'
                        for y in range(col):
                            rtMap = rtMap + dungeonArea[x][y]

                    embedEdit = discord.Embed(
                        title=f"— Daily Maze —",
                        description=
                        "Travel to the prize using buttons rapidly without going into the fire",
                        color=ctx.user.color)
                    embedEdit.add_field(name="[ Map ]",
                                        value=rtMap,
                                        inline=False)
                    embedEdit.set_author(name=interaction.user.name,
                                         icon_url=interaction.user.avatar.url)
                    await interaction.response.edit_message(embed=embedEdit)

                else:
                    await interaction.response.defer()

        buttonU.callback = up_callback
        buttonL.callback = left_callback
        buttonR.callback = right_callback
        buttonD.callback = down_callback
        view = View(timeout=7)
        view.add_item(button1)
        view.add_item(buttonU)
        view.add_item(button3)
        view.add_item(buttonL)
        view.add_item(button5)
        view.add_item(buttonR)
        view.add_item(button7)
        view.add_item(buttonD)
        view.add_item(button9)

        firstMap = ""
        for x in range(row):
            if x > 0:
                firstMap = firstMap + '\n'
            for y in range(col):
                firstMap = firstMap + dungeonArea[x][y]

        embedVar = discord.Embed(
            title=f'— Daily Maze —',
            description=
            "Travel to the prize by using buttons rapidly without going into the fire",
            color=ctx.user.color)
        embedVar.add_field(name="[ Map ]", value=firstMap, inline=False)
        embedVar.set_author(name=ctx.user.name, icon_url=ctx.user.avatar.url)
        dgMessage = await ctx.followup.send(embed=embedVar, view=view)
        checkView = await view.wait()

        if checkView:
            dungeonArea[xPos][yPos] = '💀'
            rtMap = ""
            for x in range(row):
                if x > 0:
                    rtMap = rtMap + '\n'
                for y in range(col):
                    rtMap = rtMap + dungeonArea[x][y]

            embedEdit = discord.Embed(
                title=f"— Daily Maze —",
                description=
                "You've died... ( Cause : Standing still for too long )",
                color=ctx.user.color)
            embedEdit.add_field(name="[ Map ]", value=rtMap, inline=False)
            embedEdit.set_footer(text="Resets daily at 00:00 WIB (GMT+7)")
            embedEdit.set_author(name=ctx.user.name,
                                 icon_url=ctx.user.avatar.url)
            await dgMessage.edit(
                content=
                f"Yah {ctx.user.name}-nyan mati, kelamaan ga gerak sih anata..",
                embed=embedEdit,
                view=None)
            newvalues = {"$set": {"daily": currentDay}}
            mycol.update_one(userFind, newvalues)


async def setup(bot):
    await bot.add_cog(Dailymaze(bot))
