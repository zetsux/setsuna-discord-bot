import discord
import os
import pymongo
import datetime
from discord.ui import Select, Button, Modal, TextInput, View
from discord.ext import commands
from discord import app_commands
from discord.commands import Option
import numpy as np

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]

MONGODB = os.environ['MONGODB']

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]

def arrangelb(idUser) :
  inFind = mycol.find_one({'userid' : str(idUser)})

  lbFind = mycol.find_one({'func' : "anilb"})
  newvalues = {'$pull': {'board': str(idUser)}}
  mycol.update_one(lbFind, newvalues)
  
  index = 0
  lbFind = mycol.find_one({'func' : "anilb"})
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
  
  lbFind = mycol.find_one({'func' : "anilb"})
  newvalues = {"$push": {'board' : {'$each': [str(idUser)], "$position": index}}}
  mycol.update_one(lbFind, newvalues)

class Anitrade(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @app_commands.command(name='anitrade', description='Trade with the mentioned user')
  async def anime_trading(self, ctx: discord.Interaction, member: Option(discord.Member, "Trade partner", required=True)):
    userFind = mycol.find_one({"userid": str(ctx.user.id)})
    if userFind == None:
        await ctx.response.send_message(
            f'Neee {ctx.user.name}-nyan, /regist dulu gih baru trading yaa~',
            ephemeral=True)
        return

    if member.bot:
        await ctx.response.send_message(
            f'Neee {ctx.user.name}-nyan, apasih masa ngajak trade bot. Gajelas ih..',
            ephemeral=True)
        return

    if ctx.user.id == member.id:
        await ctx.response.send_message(
            f'Neee {ctx.user.name}-nyan, apasih masa ngajak trade diri sendiri. Gajelas ih..',
            ephemeral=True)
        return

    targetFind = mycol.find_one({"userid": str(member.id)})
    if targetFind == None:
        await ctx.response.send_message(
            f'Neee {ctx.user.name}-nyan, itu {member.name}-nyan belum kedaftar nih. Suruh /regist dulu gih baru trading yaa~',
            ephemeral=True)
        return

    anime1 = []
    count1 = []
    anime2 = []
    count2 = []
    deal1 = False
    deal2 = False
    buttonAD = Button(label='Add',
                      emoji='➕',
                      style=discord.ButtonStyle.green,
                      row=0)
    buttonRE = Button(label='Remove',
                      emoji='➖',
                      style=discord.ButtonStyle.gray,
                      row=0)
    buttonDE = Button(label="Deal!",
                      emoji='🤝',
                      style=discord.ButtonStyle.primary,
                      row=1)
    buttonCA = Button(label="Cancel",
                      emoji='🤏',
                      style=discord.ButtonStyle.danger,
                      row=1)

    async def add_callback(interaction):
        if interaction.user.id != member.id and interaction.user.id != ctx.user.id:
            await interaction.response.send_message(
                f"Neeee, anata kan ngga ikut tradingnya sih.. /anitrade sendiri gih kalau mau ngetrade juga, {interaction.user.name}-nyan",
                ephemeral=True)
            return

        modaler = Modal(title="Add your anime character to the trading board",
                        timeout=None)
        modaler.add_item(
            TextInput(
                label='Anime Character Name',
                placeholder=
                '(Must be the exact same as yours), ex : Naruto Uzumaki'))
        modaler.add_item(
            TextInput(label='Anime Character Quantity',
                      placeholder='(Must have in inventory), ex : 2'))

        async def addmod_callback(minteraction):
            if modaler.children[1].value.isdigit() is False or int(
                    modaler.children[1].value) <= 0:
                await minteraction.response.send_message(
                    f'Neee {minteraction.user.name}-nyan, anata gajelas ah, masa quantitynya gitu sih...',
                    ephemeral=True)
                return

            adderFind = mycol.find_one({"userid": str(interaction.user.id)})
            animeInven = adderFind["animeName"]
            aniName = modaler.children[0].value
            if aniName in animeInven:
                animeIndex = 0

                for x in animeInven:
                    if x == aniName:
                        break
                    animeIndex += 1

                if adderFind["animeCount"][animeIndex] < int(
                        modaler.children[1].value):
                    await minteraction.response.send_message(
                        f'Neee {interaction.user.name}-nyan, anata cuma punya {adderFind["animeCount"][animeIndex]} {aniName}, ngga cukup dong..',
                        ephemeral=True)
                    return

                else:
                    if interaction.user.id == member.id:
                        nonlocal anime2, count2
                        if aniName in anime2:
                            alrIndex = 0

                            for x in anime2:
                                if x == aniName:
                                    break
                                alrIndex += 1

                            if adderFind["animeCount"][animeIndex] < (
                                    count2[alrIndex] +
                                    int(modaler.children[1].value)):
                                await minteraction.response.send_message(
                                    f'Neee {interaction.user.name}-nyan, anata cuma punya {adderFind["animeCount"][animeIndex]} {aniName}, ngga cukup dong..',
                                    ephemeral=True)
                                return

                            else:
                                count2[alrIndex] += int(
                                    modaler.children[1].value)

                        else:
                            anime2.append(aniName)
                            count2.append(int(modaler.children[1].value))

                    elif interaction.user.id == ctx.user.id:
                        nonlocal anime1, count1
                        if aniName in anime1:
                            alrIndex = 0

                            for x in anime1:
                                if x == aniName:
                                    break
                                alrIndex += 1

                            if adderFind["animeCount"][animeIndex] < (
                                    count1[alrIndex] +
                                    int(modaler.children[1].value)):
                                await minteraction.response.send_message(
                                    f'Neee {interaction.user.name}-nyan, anata cuma punya {adderFind["animeCount"][animeIndex]} {aniName}, ngga cukup dong..',
                                    ephemeral=True)
                                return

                            else:
                                count1[alrIndex] += int(
                                    modaler.children[1].value)

                        else:
                            anime1.append(aniName)
                            count1.append(int(modaler.children[1].value))

                    nonlocal deal1, deal2
                    deal1 = False
                    deal2 = False
                    edString1 = ""
                    edString2 = ""
                    if len(anime1) == 0 and len(anime2) == 0:
                        edString1 = " "
                        edString2 = " "
                    indx1 = 0
                    indx2 = 0
                    for char in anime1:
                        edString1 = edString1 + f"• {char} [{count1[indx1]}]\n"
                        indx1 += 1

                    for char in anime2:
                        edString2 = edString2 + f"• {char} [{count2[indx2]}]\n"
                        indx2 += 1

                    while indx1 > indx2:
                        edString2 = edString2 + " \n"
                        indx2 += 1

                    while indx2 > indx1:
                        edString1 = edString1 + " \n"
                        indx1 += 1

                    embedEdit = discord.Embed(
                        title="— Trading Board —",
                        description=
                        f"{ctx.user.name}-nyan and {member.name}-nyan",
                        color=0xff69b4)
                    embedEdit.add_field(name=f"[ {ctx.user.name}'s Offer ]",
                                        value=f"```{edString1}```",
                                        inline=True)
                    embedEdit.add_field(name=f"| DEAL |",
                                        value=f"🟩 | 🟩",
                                        inline=True)
                    embedEdit.add_field(name=f"[ {member.name}'s Offer ]",
                                        value=f"```{edString2}```",
                                        inline=True)
                    await minteraction.response.edit_message(embed=embedEdit)
                    await minteraction.followup.send(
                        f"{interaction.user.name} berhasil menambahkan {str(modaler.children[1].value)} {aniName} ke sisi trading boardnya!"
                    )

            else:
                await minteraction.response.send_message(
                    f"Neee {minteraction.user.name}-nyan, anata halu ya? Ngga ada ah di inventory anata yang namanya '{aniName}'. Coba dicek lagi deh..",
                    ephemeral=True)

        modaler.callback = addmod_callback
        await interaction.response.send_modal(modaler)

    async def remove_callback(interaction):
        if interaction.user.id != member.id and interaction.user.id != ctx.user.id:
            await interaction.response.send_message(
                f"Neeee, anata kan ngga ikut tradingnya sih.. /anitrade sendiri gih kalau mau ngetrade juga, {interaction.user.name}-nyan",
                ephemeral=True)
            return

        modaler = Modal(title="Remove anime character from the trading board",
                        timeout=None)
        modaler.add_item(
            TextInput(
                label='Anime Character Name',
                placeholder=
                '(Must be the exact same as board), ex : Naruto Uzumaki'))
        modaler.add_item(
            TextInput(label='Anime Character Quantity',
                      placeholder='(Must have in board), ex : 2'))

        async def remmod_callback(minteraction):
            if modaler.children[1].value.isdigit() is False or int(
                    modaler.children[1].value) <= 0:
                await minteraction.response.send_message(
                    f'Neee {minteraction.user.name}-nyan, anata gajelas ah, masa quantitynya gitu sih...',
                    ephemeral=True)
                return

            aniName = modaler.children[0].value
            if interaction.user.id == member.id:
                nonlocal anime2, count2
                if aniName in anime2:
                    anindx = 0
                    for char in anime2:
                        if char == aniName:
                            break

                        anindx += 1

                    if count2[anindx] < int(modaler.children[1].value):
                        await minteraction.response.send_message(
                            f"Neee {minteraction.user.name}-nyan, anata halu ya? Di trading board cuma ada {count2[anindx]} {aniName} loh. Coba dicek lagi deh..",
                            ephemeral=True)
                        return

                    elif count2[anindx] == int(modaler.children[1].value):
                        anime2.pop(anindx)
                        count2.pop(anindx)

                    else:
                        count2[anindx] -= int(modaler.children[1].value)

                else:
                    await minteraction.response.send_message(
                        f"Neee {minteraction.user.name}-nyan, anata halu ya? Ngga ada ah di trading board yang namanya '{aniName}'. Coba dicek lagi deh..",
                        ephemeral=True)
                    return

            elif interaction.user.id == ctx.user.id:
                nonlocal anime1, count1
                if aniName in anime1:
                    anindx = 0
                    for char in anime1:
                        if char == aniName:
                            break

                        anindx += 1

                    if count1[anindx] < int(modaler.children[1].value):
                        await minteraction.response.send_message(
                            f"Neee {minteraction.user.name}-nyan, anata halu ya? Di trading board cuma ada {count1[anindx]} {aniName} loh. Coba dicek lagi deh..",
                            ephemeral=True)
                        return

                    elif count1[anindx] == int(modaler.children[1].value):
                        anime1.pop(anindx)
                        count1.pop(anindx)

                    else:
                        count1[anindx] -= int(modaler.children[1].value)

                else:
                    await minteraction.response.send_message(
                        f"Neee {minteraction.user.name}-nyan, anata halu ya? Ngga ada ah di trading board yang namanya '{aniName}'. Coba dicek lagi deh..",
                        ephemeral=True)
                    return

            nonlocal deal1, deal2
            deal1 = False
            deal2 = False
            edString1 = ""
            edString2 = ""
            if len(anime1) == 0 and len(anime2) == 0:
                edString1 = " "
                edString2 = " "
            indx1 = 0
            indx2 = 0
            for char in anime1:
                edString1 = edString1 + f"• {char} [{count1[indx1]}]\n"
                indx1 += 1

            for char in anime2:
                edString2 = edString2 + f"• {char} [{count2[indx2]}]\n"
                indx2 += 1

            while indx1 > indx2:
                edString2 = edString2 + " \n"
                indx2 += 1

            while indx2 > indx1:
                edString1 = edString1 + " \n"
                indx1 += 1

            embedEdit = discord.Embed(
                title="— Trading Board —",
                description=f"{ctx.user.name}-nyan and {member.name}-nyan",
                color=0xff69b4)
            embedEdit.add_field(name=f"[ {ctx.user.name}'s Offer ]",
                                value=f"```{edString1}```",
                                inline=True)
            embedEdit.add_field(name=f"| DEAL |", value=f"🟩 | 🟩", inline=True)
            embedEdit.add_field(name=f"[ {member.name}'s Offer ]",
                                value=f"```{edString2}```",
                                inline=True)
            await minteraction.response.edit_message(embed=embedEdit)
            await minteraction.followup.send(
                f"{interaction.user.name} berhasil menghilangkan {str(modaler.children[1].value)} {aniName} dari sisi trading boardnya!"
            )

        modaler.callback = remmod_callback
        await interaction.response.send_modal(modaler)

    async def deal_callback(interaction):
        if interaction.user.id != member.id and interaction.user.id != ctx.user.id:
            await interaction.response.send_message(
                f"Neeee, anata kan ngga ikut tradingnya sih.. /anitrade sendiri gih kalau mau ngetrade juga, {interaction.user.name}-nyan",
                ephemeral=True)
            return

        if len(anime1) == 0 and len(anime2) == 0:
            await interaction.response.send_message(
                f"Neeee, trading boardnya aja masih kosong masa udah deal sih {interaction.user.name}-nyan",
                ephemeral=True)
            return

        nonlocal deal1, deal2
        if deal1 and interaction.user.id == ctx.user.id:
            await interaction.response.send_message(
                f"Sabar yah {interaction.user.name}, {member.name}-nyan masih belum mencet deal juga nih...",
                ephemeral=True)
            return

        elif deal2 and interaction.user.id == member.id:
            await interaction.response.send_message(
                f"Sabar yah {interaction.user.name}, {ctx.user.name}-nyan masih belum mencet deal juga nih...",
                ephemeral=True)
            return

        if interaction.user.id == member.id:
            deal2 = True

        elif interaction.user.id == ctx.user.id:
            deal1 = True

        if deal1 and deal2:
            edString1 = ""
            edString2 = ""
            indx1 = 0
            indx2 = 0
            for char in anime1:
                edString1 = edString1 + f"• {char} [{count1[indx1]}]\n"
                indx1 += 1

            for char in anime2:
                edString2 = edString2 + f"• {char} [{count2[indx2]}]\n"
                indx2 += 1

            while indx1 > indx2:
                edString2 = edString2 + " \n"
                indx2 += 1

            while indx2 > indx1:
                edString1 = edString1 + " \n"
                indx1 += 1

            embedEdit = discord.Embed(
                title="— Trading Board (Finished) —",
                description=
                f"{ctx.user.name}-nyan and {member.name}-nyan | Trade Success!",
                color=0xff69b4)
            embedEdit.add_field(name=f"[ {ctx.user.name}'s Offer ]",
                                value=f"```{edString1}```",
                                inline=True)
            embedEdit.add_field(name=f"| DEAL |", value=f"✅ | ✅", inline=True)
            embedEdit.add_field(name=f"[ {member.name}'s Offer ]",
                                value=f"```{edString2}```",
                                inline=True)
            await interaction.response.edit_message(embed=embedEdit, view=None)
            await interaction.followup.send(
                f"Trade berhasil! Telah disetujui oleh {ctx.user.name}-nyan dan {member.name}-nyan!"
            )

            async def giveAni(usera, namea, numbera):
                giveFind = mycol.find_one({"userid": str(usera)})
                mUni = giveFind["uniAni"]
                mAll = giveFind["allAni"]
                animeInven = giveFind["animeName"]
                animeCounting = giveFind["animeCount"]
                if namea in animeInven:
                    animeIndex = 0

                    for x in animeInven:
                        if x == namea:
                            break
                        animeIndex += 1

                    if animeCounting[animeIndex] == numbera :
                      mUni += 1

                    stringIndex = "animeCount." + str(animeIndex)
                    newValues = {"$set": { "uniAni" : mUni, "allAni" : mAll + 1, stringIndex : animeCounting[animeIndex] + numbera}}
                    mycol.update_one(giveFind, newValues)

                else:
                    newValues = {
                      "$set": {
                        "uniAni" : mUni + 1, 
                        "allAni" : mAll + 1
                      }, 
                      
                      "$push": {
                        "animeName": namea, 
                        "animeCount": numbera 
                      }
                    }
                  
                    mycol.update_one(giveFind, newValues)

            async def takeAni(usera, namea, numbera):
                takeFind = mycol.find_one({"userid": str(usera)})
                animeInven = takeFind["animeName"]
                mUni = takeFind["uniAni"]
                mAll = takeFind["allAni"]
                animeCounting = takeFind["animeCount"]
                animeIndex = 0

                for x in animeInven:
                    if x == namea:
                        break
                    animeIndex += 1

                if takeFind["animeCount"][animeIndex] == numbera:
                    stringIndex = "animeCount." + str(animeIndex)
                    mycol.update_one(takeFind, {"$set": {"uniAni" : mUni - 1, "allAni" : mAll - 1, stringIndex: 0}})

                elif takeFind["animeCount"][animeIndex] > numbera:
                    stringIndex = "animeCount." + str(animeIndex)
                    mycol.update_one(takeFind, { "$set": { "allAni" : mAll - 1, stringIndex: animeCounting[animeIndex] - numbera }})

            tempIndex = 0
            for char in anime1:
                await takeAni(ctx.user.id, char, count1[tempIndex])
                await giveAni(member.id, char, count1[tempIndex])
                tempIndex += 1

            tempIndex = 0
            for char in anime2:
                await takeAni(member.id, char, count2[tempIndex])
                await giveAni(ctx.user.id, char, count2[tempIndex])
                tempIndex += 1

            arrangelb(ctx.user.id)
            arrangelb(member.id)

        elif deal1:
            edString1 = ""
            edString2 = ""
            indx1 = 0
            indx2 = 0
            for char in anime1:
                edString1 = edString1 + f"• {char} [{count1[indx1]}]\n"
                indx1 += 1

            for char in anime2:
                edString2 = edString2 + f"• {char} [{count2[indx2]}]\n"
                indx2 += 1

            while indx1 > indx2:
                edString2 = edString2 + " \n"
                indx2 += 1

            while indx2 > indx1:
                edString1 = edString1 + " \n"
                indx1 += 1

            embedEdit = discord.Embed(
                title="— Trading Board —",
                description=f"{ctx.user.name}-nyan and {member.name}-nyan",
                color=0xff69b4)
            embedEdit.add_field(name=f"[ {ctx.user.name}'s Offer ]",
                                value=f"```{edString1}```",
                                inline=True)
            embedEdit.add_field(name=f"| DEAL |", value=f"✅ | 🟩", inline=True)
            embedEdit.add_field(name=f"[ {member.name}'s Offer ]",
                                value=f"```{edString2}```",
                                inline=True)
            await interaction.response.edit_message(embed=embedEdit)
            mentionUser = '<@' + str(member.id) + '>'
            await interaction.followup.send(
                f"{interaction.user.name}-nyan sudah deal tuh sama trade ini, tinggal kamu nih {mentionUser}"
            )

        elif deal2:
            edString1 = ""
            edString2 = ""
            indx1 = 0
            indx2 = 0
            for char in anime1:
                edString1 = edString1 + f"• {char} [{count1[indx1]}]\n"
                indx1 += 1

            for char in anime2:
                edString2 = edString2 + f"• {char} [{count2[indx2]}]\n"
                indx2 += 1

            while indx1 > indx2:
                edString2 = edString2 + " \n"
                indx2 += 1

            while indx2 > indx1:
                edString1 = edString1 + " \n"
                indx1 += 1

            embedEdit = discord.Embed(
                title="— Trading Board —",
                description=f"{ctx.user.name}-nyan and {member.name}-nyan",
                color=0xff69b4)
            embedEdit.add_field(name=f"[ {ctx.user.name}'s Offer ]",
                                value=f"```{edString1}```",
                                inline=True)
            embedEdit.add_field(name=f"| DEAL |", value=f"🟩 | ✅", inline=True)
            embedEdit.add_field(name=f"[ {member.name}'s Offer ]",
                                value=f"```{edString2}```",
                                inline=True)
            await interaction.response.edit_message(embed=embedEdit)
            mentionUser = '<@' + str(ctx.user.id) + '>'
            await interaction.followup.send(
                f"{interaction.user.name}-nyan sudah deal tuh sama trade ini, tinggal kamu nih {mentionUser}"
            )

    async def cancel_callback(interaction):
        if interaction.user.id != member.id and interaction.user.id != ctx.user.id:
            await interaction.response.send_message(
                f"Neeee, anata kan ngga ikut tradingnya sih.. /anitrade sendiri gih kalau mau ngetrade juga, {interaction.user.name}-nyan",
                ephemeral=True)
            return

        embedEnd = discord.Embed(
            title=
            f"Trade Cancelled ( {ctx.user.name}-nyan | {member.name}-nyan )",
            description=f"Cause : Cancelled by {interaction.user.name}-nyan",
            color=0xff69b4)
        await interaction.response.edit_message(embed=embedEnd, view=None)
        await interaction.followup.send(
            f"Trade antara {ctx.user.name}-nyan dan {member.name}-nyan dibatalin sama {interaction.user.name}-nyan.."
        )

    buttonAD.callback = add_callback
    buttonRE.callback = remove_callback
    buttonDE.callback = deal_callback
    buttonCA.callback = cancel_callback
    view = View(timeout=750)
    view.add_item(buttonAD)
    view.add_item(buttonRE)
    view.add_item(buttonDE)
    view.add_item(buttonCA)

    aniString1 = " "
    aniString2 = " "

    embedVar = discord.Embed(
        title="— Trading Board —",
        description=f"{ctx.user.name}-nyan and {member.name}-nyan",
        color=0xff69b4)
    embedVar.add_field(name=f"[ {ctx.user.name}'s Offer ]",
                       value=f"```{aniString1}```",
                       inline=True)
    embedVar.add_field(name=f"| DEAL |", value=f"🟩 | 🟩", inline=True)
    embedVar.add_field(name=f"[ {member.name}'s Offer ]",
                       value=f"```{aniString2}```",
                       inline=True)
    await ctx.response.send_message(embed=embedVar, view=view)
    checkView = await view.wait()

    if checkView:
        embedEnd = discord.Embed(
            title=
            f"Trade Cancelled ( {ctx.user.name}-nyan | {member.name}-nyan )",
            description="Cause : Not used for too long",
            color=0xff69b4)
        await ctx.edit_original_response(embed=embedEnd, view=None)

async def setup(bot):
  await bot.add_cog(Anitrade(bot))