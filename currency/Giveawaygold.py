import discord
import os
import pymongo
from discord.ui import Button, View
from discord.ext import commands
from discord import app_commands

MONGODB = os.environ['MONGODB']

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]


class Giveawaygold(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name='giveawaygold',
        description='Giveaway the entered number of gold to the fastest claimer'
    )
    @app_commands.describe(number="Number of gold to giveaway")
    async def gold_giveaway(self, ctx: discord.Interaction, number: int):
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
            goldCount = userFind["gold"]
            if number > goldCount:
                await ctx.followup.send(
                    f'Gold anata ngga cukup, {ctx.user.name}-nyan...',
                    ephemeral=True)

            else:
                flag = True
                goldCount = userFind["gold"] - number
                newvalues = {"$set": {"gold": goldCount}}
                mycol.update_one(userFind, newvalues)
                buttons = Button(label="Claim Gold",
                                 style=discord.ButtonStyle.success,
                                 emoji="🤑")

                async def button_callback(interaction):
                    userFind = mycol.find_one(
                        {"userid": str(interaction.user.id)})
                    if userFind == None:
                        await interaction.response.send_message(
                            f'Neee {interaction.user.name}-nyan, yuk /regist dulu baru ikut giveaway',
                            ephemeral=True)
                    else:
                        embedEdit = discord.Embed(
                            title=str(number) + " Gold Giveaway by " +
                            ctx.user.name + "-nyan",
                            description=
                            f">> Claimed by {interaction.user.name}-nyan",
                            color=0xffd700)
                        await interaction.response.edit_message(
                            embed=embedEdit, view=None)

                        nonlocal flag
                        if flag:
                            flag = False
                            goldCount = userFind["gold"] + number
                            newvalues = {"$set": {"gold": goldCount}}
                            mycol.update_one(userFind, newvalues)

                buttons.callback = button_callback
                view = View()
                view.add_item(buttons)

                embedVar = discord.Embed(
                    title=str(number) + " Gold Giveaway by " + ctx.user.name +
                    "-nyan",
                    description="Penekan tombol tercepat akan mendapatkannya!",
                    color=0xffd700)
                embedVar.set_thumbnail(
                    url=
                    "https://i.ibb.co/BZPbJ6W/pngfind-com-gold-coins-png-37408.png"
                )
                await ctx.followup.send(embed=embedVar, view=view)


async def setup(bot):
    await bot.add_cog(Giveawaygold(bot))
