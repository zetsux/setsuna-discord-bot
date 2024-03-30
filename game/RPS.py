import discord
import os
import pymongo
import datetime
from discord.ui import Select, Button, Modal, TextInput, View
from discord.ext import commands
from discord.commands import Option
import numpy as np
import time
import random

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]

MONGODB = os.environ['MONGODB']

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]

class RPS(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @commands.slash_command(name='rps', description='Battle RPS against a target')
  async def rps_battle(self, ctx, member: Option(discord.Member, "Member to diss", required=True)):
    if member.bot:
        await ctx.respond(f'Masa nantang bewan sama bot sih {ctx.author.name}-nyan, aneh banget deh', ephemeral=True)
        return

    if member.id == ctx.author.id:
        await ctx.respond(
            f'Masa battle sama diri sendiri sih {ctx.author.name}-nyan, aneh banget deh',
            ephemeral=True)
        return

    player1 = "kosong"
    player2 = "kosong"
    select = Select(placeholder="Choose your hand!!",
                    options=[
                        discord.SelectOption(
                            label="The Resilient Rock",
                            emoji="🪨",
                            value="r",
                            description="Rock blunts Scissors"),
                        discord.SelectOption(label="The Purposeful Paper",
                                             emoji="📄",
                                             value="p",
                                             description="Paper wraps Rock"),
                        discord.SelectOption(label="The Sharp Scissors",
                                             emoji="✂️",
                                             value="s",
                                             description="Scissors cut Paper")
                    ])

    async def rps_callback(interaction):
        nonlocal player1, player2
        if interaction.user.id == member.id:
            if select.values[0] == "r":
                player2 = '🪨'
                await interaction.response.send_message(
                    f"{interaction.user.name}-nyan, anata telah memutuskan untuk memilih 🪨",
                    ephemeral=True)

            elif select.values[0] == "p":
                player2 = '📄'
                await interaction.response.send_message(
                    f"{interaction.user.name}-nyan, anata telah memutuskan untuk memilih 📄",
                    ephemeral=True)

            elif select.values[0] == "s":
                player2 = '✂️'
                await interaction.response.send_message(
                    f"{interaction.user.name}-nyan, anata telah memutuskan untuk memilih ✂️",
                    ephemeral=True)

            if player1 == "kosong":
                mentionUser = '<@' + str(ctx.author.id) + '>'
                await interaction.followup.send(
                    f"{interaction.user.name}-nyan telah menentukan pilihannya, yuk dipilih yuk cepat {mentionUser}-nyan"
                )

            else:
                await interaction.followup.send(
                    f"{interaction.user.name}-nyan telah menentukan pilihannya!"
                )

        elif interaction.user.id == ctx.author.id:
            if select.values[0] == "r":
                player1 = '🪨'
                await interaction.response.send_message(
                    f"{interaction.user.name}-nyan, anata telah memutuskan untuk memilih 🪨",
                    ephemeral=True)

            elif select.values[0] == "p":
                player1 = '📄'
                await interaction.response.send_message(
                    f"{interaction.user.name}-nyan, anata telah memutuskan untuk memilih 📄",
                    ephemeral=True)

            elif select.values[0] == "s":
                player1 = '✂️'
                await interaction.response.send_message(
                    f"{interaction.user.name}-nyan, anata telah memutuskan untuk memilih ✂️",
                    ephemeral=True)

            if player2 == "kosong":
                mentionUser = '<@' + str(member.id) + '>'
                await interaction.followup.send(
                    f"{interaction.user.name}-nyan telah menentukan pilihannya, yuk dipilih yuk cepat {mentionUser}-nyan"
                )

            else:
                await interaction.followup.send(
                    f"{interaction.user.name}-nyan telah menentukan pilihannya!"
                )

        else:
            await interaction.response.send_message(
                f"Kamu kan ngga ikut gamenya {interaction.user.name}-nyan, bikin game sendiri aja kalau mau main yaa",
                ephemeral=True)
            return

        if player1 != "kosong" and player2 != "kosong":
            if player1 == player2:
                embedEdit = discord.Embed(
                    title=
                    f"{ctx.author.name} ({player1}) VS {member.name} ({player2})",
                    description=f"It's a tie!",
                    color=0xadd8e6)
                embedEdit.set_image(
                    url=
                    'https://c.tenor.com/wyfhYqF1tJIAAAAM/mark-wahlberg-wahlberg.gif'
                )
                await rpsMessage.edit_original_response(embed=embedEdit,
                                                       view=None)
                await rpsMessage.followup.send(
                    f"Nampaknya terjadi tie game minna-san!")
                view.stop()
                return

            else:
                if player1 == '🪨':
                    if player2 == '📄':
                        winner = member
                    elif player2 == '✂️':
                        winner = ctx.author

                elif player1 == '📄':
                    if player2 == '🪨':
                        winner = ctx.author
                    elif player2 == '✂️':
                        winner = member

                if player1 == '✂️':
                    if player2 == '📄':
                        winner = ctx.author
                    elif player2 == '🪨':
                        winner = member

                embedEdit = discord.Embed(
                    title=
                    f"{ctx.author.name} ({player1}) VS {member.name} ({player2})",
                    description=f"{winner.name} wins!",
                    color=0xf73718)
                embedEdit.set_image(url=winner.avatar.url)
                await rpsMessage.edit_original_response(embed=embedEdit,
                                                       view=None)
                await rpsMessage.followup.send(
                    f"Omedetou, {winner.name}-nyan berhasil menjadi pemenang!")
                view.stop()

    select.callback = rps_callback
    view = View(timeout=600)
    view.add_item(select)

    embedVar = discord.Embed(title="Rock, Paper, Scissors Battle",
                             description=f"{ctx.author.name} VS {member.name}",
                             color=0xf73718)
    embedVar.set_image(
        url=
        'https://cdn.pixabay.com/photo/2013/07/12/15/02/fingers-149296__340.png'
    )
    rpsMessage = await ctx.respond(embed=embedVar, view=view)
    checkView = await view.wait()

    if checkView:
        embedEdit = discord.Embed(
            title=f"Rock, Paper, Scissors Battle ended",
            description=
            "Kelamaan ihh, masa dah 5 menit ada yang blom milih juga",
            color=0x808080)
        await rpsMessage.edit_original_response(embed=embedEdit, view=None)
        if player1 == "kosong" and player2 == "kosong":
            await rpsMessage.followup.send(
                f"Hmph, battlenya watashi tutup deh, {ctx.author.name}-nyan sama {member.name}-nyan pada belum milih sih, lama banget..",
                ephemeral=True)
        elif player1 == "kosong":
            await rpsMessage.followup.send(
                f"Hmph, battlenya watashi tutup deh, {ctx.author.name}-nyan belum milih sih, lama banget. Kasian tuh {member.name} udah nungguin..",
                ephemeral=True)
        elif player2 == "kosong":
            await rpsMessage.followup.send(
                f"Hmph, battlenya watashi tutup deh, {member.name}-nyan belum milih sih, lama banget. Kasian tuh {ctx.author.name} udah nungguin..",
                ephemeral=True)
          
def setup(bot):
  bot.add_cog(RPS(bot))