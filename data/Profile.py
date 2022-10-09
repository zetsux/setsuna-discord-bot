import discord
import os
import pymongo
import datetime
from discord.ui import Select, Button, Modal, InputText, View
from discord.ext import commands
from discord.commands import Option
import numpy as np

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]

MONGODB = os.environ['MONGODB']

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]

class Profile(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @commands.slash_command(name='profile', description='Shows the profile of the one you mentioned or yourself', guild_ids=guilds)
  async def character_profile(self, ctx, member: Option(discord.Member, "The profile you want to check of", required=False, default=None)):
    if not member:
        member = ctx.author

    userFind = mycol.find_one({"userid": str(member.id)})
    if userFind == None:
        await ctx.respond(
            f'{member.name}-nyan belum terdaftar, watashi tidak bisa membuka profilenya',
            ephemeral=True)

    else:
        select = Select(placeholder="Choose what to display",
                        options=[
                            discord.SelectOption(
                                label="User Profile",
                                emoji="👤",
                                value="profile",
                                description="Display your profile")
                        ])

        animeNames = userFind["animeName"]
        animeCounts = userFind["animeCount"]
        animeIndex = 0
        animeInven = []
        animeCounter = 0

        for x in animeNames:
            if animeCounts[animeIndex] <= 0:
                animeIndex += 1
                continue
            animeInven.append(
                f"• {animeNames[animeIndex]} [{animeCounts[animeIndex]}]")
            animeIndex += 1
            animeCounter += 1

        num = int(animeCounter / 50)
        animeString = []
        if animeCounter == 0:
            animeString.append(
                'Koleksi animenya kosong nih, berdebu tasnya ngga berisi...\nButuh /anigacha nampaknya~'
            )

        elif num == 0:
            temp = '\n'.join(animeInven)
            animeString.append(temp)

        else:
            if num > 10:
                num = 10
            sub_lists = np.array_split(animeInven, num + 1)
            for i in sub_lists:
                temp = '\n'.join(list(i))
                animeString.append('\n'.join(list(i)))

        pageIndex = 1
        while num >= 0:
            select.add_option(label=f"AniCollection Page {pageIndex}",
                              emoji="🎒",
                              value=str(pageIndex * -1),
                              description="Display your anime collection")

            num -= 1
            pageIndex += 1

        pokeNames = userFind["pokeName"]
        pokeLevels = userFind["pokeLevel"]
        pokeIndex = 0
        pokeInven = []
        pokeCounter = 0

        pokeFind = mycol.find_one({"func": "pokedb"})
        pokeBasic = pokeFind["basic"]
        pokeElite = pokeFind["elite"]
        pokeEpic = pokeFind["epic"]
        pokeLegend = pokeFind["legend"]
        countBasic = 0
        countElite = 0
        countEpic = 0
        countLegend = 0

        for x in pokeNames:
            if pokeLevels[pokeIndex] <= 0:
                pokeIndex += 1
                continue

            tempRarity = 'Un'
            if pokeNames[pokeIndex] in pokeBasic:
                tempRarity = 'B'
                countBasic += 1
            elif pokeNames[pokeIndex] in pokeElite:
                tempRarity = 'A'
                countElite += 1
            elif pokeNames[pokeIndex] in pokeEpic:
                tempRarity = 'E'
                countEpic += 1
            elif pokeNames[pokeIndex] in pokeLegend:
                tempRarity = 'L'
                countLegend += 1

            pokeInven.append(
                f"• {pokeNames[pokeIndex]} ({tempRarity}) [Lv. {pokeLevels[pokeIndex]}]"
            )
            pokeIndex += 1
            pokeCounter += 1

        num = int(pokeCounter / 50)
        # print(num)
        pokeString = []
        if pokeCounter == 0:
            pokeString.append(
                'Koleksi pokemonnya kosong nih, berdebu tasnya ngga berisi...\nButuh /pokecatch nampaknya~'
            )

        elif num == 0:
            temp = '\n'.join(pokeInven)
            pokeString.append(temp)

        else:
            if num > 13:
                num = 13
            sub_lists = np.array_split(pokeInven, num + 1)
            for i in sub_lists:
                temp = '\n'.join(list(i))
                pokeString.append('\n'.join(list(i)))

        pageIndex = 1
        while num >= 0:
            select.add_option(label=f"PokeStorage Page {pageIndex}",
                              emoji="🖥️",
                              value=str(pageIndex),
                              description="Display your pokemon collection")

            num -= 1
            pageIndex += 1

        async def selection_callback(interaction):
            if interaction.user.id == ctx.author.id:
                if select.values[0] == "profile":
                    embedEdit = discord.Embed(
                        title=f"— {member.name}'s Profile —",
                        description=userFind["bio"],
                        color=member.color)
                    embedEdit.set_thumbnail(url=member.avatar.url)
                    embedEdit.add_field(name="[ Level ]",
                                        value='```' + str(userFind["level"]) +
                                        ' | EXP : ' + str(userFind["exp"]) +
                                        '/' + str(userFind["level"] * 2) +
                                        '```',
                                        inline=False)
                    embedEdit.add_field(name="[ Gold ]",
                                        value='```' + str(userFind["gold"]) +
                                        '```',
                                        inline=True)
                    embedEdit.add_field(name="[ Platina ]",
                                        value='```' +
                                        str(userFind["platina"]) + '```',
                                        inline=True)
                    embedEdit.add_field(name="[ Favorite Anime ]",
                                        value='```' + str(userFind["favani"]) +
                                        '```',
                                        inline=False)
                    embedEdit.add_field(
                        name="[ PokeHistory ]",
                        value='```' + f'Win     : {str(userFind["win"])}\n' +
                        f'Lose    : {str(userFind["lose"])}\n' +
                        f'Draw    : {str(userFind["draw"])}\n'
                        f'Latest  : {str(userFind["latest"])}\n' + '```',
                        inline=False)
                    await interaction.response.edit_message(embed=embedEdit)

                else:
                    if int(select.values[0]) > 0:
                        embedEdit = discord.Embed(
                            title="— PokeStorage —",
                            description='```' +
                            pokeString[int(select.values[0]) - 1] + '```',
                            color=member.color)
                        embedEdit.set_author(name=member.name,
                                             icon_url=member.avatar.url)
                        embedEdit.set_footer(
                            text=
                            f"B : {countBasic} | A : {countElite} | E : {countEpic} | L : {countLegend}",
                            icon_url=
                            'https://cdn.discordapp.com/attachments/995337235211763722/1019530696848592906/pokeball.gif'
                        )
                        await interaction.response.edit_message(embed=embedEdit
                                                                )

                    elif int(select.values[0]) < 0:
                        embedEdit = discord.Embed(
                            title="— AniCollection —",
                            description='```' +
                            animeString[(int(select.values[0]) * -1) - 1] +
                            '```',
                            color=member.color)
                        embedEdit.set_author(name=member.name,
                                             icon_url=member.avatar.url)
                        embedEdit.set_footer(
                            text=f"Total : {animeCounter}",
                            icon_url=
                            'https://cdn.discordapp.com/attachments/995337235211763722/1019531288966877184/anime.gif'
                        )
                        await interaction.response.edit_message(embed=embedEdit
                                                                )

            else:
                await interaction.response.send_message(
                    f"Neee {interaction.user.name}-nyan, /profile sendiri yuk, jangan ganggu yang lain yaa",
                    ephemeral=True)

        select.callback = selection_callback
        view = View(timeout=750)
        view.add_item(select)

        embedVar = discord.Embed(title="— Profile Page —",
                                 description=f"**{member}**",
                                 color=member.color)
        embedVar.set_image(url=member.avatar.url)
        profileMsg = await ctx.respond(embed=embedVar, view=view)
        checkView = await view.wait()

        if checkView:
            embedEdit = discord.Embed(
                title=f"Profilenya watashi tutup karena lama ngga dipake",
                description=
                "Kalau mau cek profile lagi tinggal /profile aja yaa",
                color=0xff10f0)
            await profileMsg.edit_original_message(embed=embedEdit, view=None)

def setup(bot):
  bot.add_cog(Profile(bot))