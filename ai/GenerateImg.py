import discord
import os
import pymongo
import datetime
from discord.ui import Select, Button, Modal, TextInput, View
from discord.ext import commands
from discord.commands import Option
import numpy as np
import aiohttp

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]

CHATAPIKEY = os.environ['CHATKEY']

class GenerateImg(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @commands.slash_command(name='setsuimg', description='Ask Setsuna to generate an image based on the given prompt')
  @commands.has_any_role('Encoder Magang', 'Owner')
  async def generateImgCommand(self, ctx, prompt: Option(str, "Prompt for the image to generate", required=True), number: Option(int, "Number of image to generate (Max : 10)", required=False, default=1)):
    await ctx.defer()

    if number > 10 or number < 1 :
      await ctx.respond(f'Neee anata ngga jelas deh, {ctx.author.name}-nyan',
                          ephemeral=True)
      return

    try :
      async with aiohttp.ClientSession() as session:
        pl = {
          "prompt": prompt,
          "n": number,
          "size": f"1024x1024"
        }
        h = {"Authorization": f"Bearer {CHATAPIKEY}"}
        
        async with session.post("https://api.openai.com/v1/images/generations", json=pl, headers=h) as r:
          response = await r.json()

          index = 1
          buttonPP = Button(label='Previous Page',
                            emoji='👈',
                            style=discord.ButtonStyle.gray,
                            row=0)
          buttonNP = Button(label='Next Page',
                            emoji='👉',
                            style=discord.ButtonStyle.gray,
                            row=0)

          async def pp_callback(interaction):
              nonlocal index
              if index == 1:
                  await interaction.response.send_message(
                      f"Neee {interaction.user.name}, ini udah page paling awal loh..", ephemeral=True)
                  return

              index -= 1
              embedEd = discord.Embed(color=0x9457EB)
              embedEd.set_image(url=response["data"][index-1]["url"])
              embedEd.set_footer(text=f"Image : {index}/{number}\nPrompt : {prompt}\nRequested by : {ctx.author.name}", icon_url=ctx.author.avatar.url)
              await interaction.response.edit_message(embed=embedEd)

          async def np_callback(interaction):
              nonlocal index
              if index == number:
                  await interaction.response.send_message(
                      f"Neee {interaction.user.name}, ini udah page paling akhir loh..", ephemeral=True)
                  return

              index += 1
              embedEd = discord.Embed(color=0x9457EB)
              embedEd.set_image(url=response["data"][index-1]["url"])
              embedEd.set_footer(text=f"Image : {index}/{number}\nPrompt : {prompt}\nRequested by : {ctx.author.name}", icon_url=ctx.author.avatar.url)
              await interaction.response.edit_message(embed=embedEd)

          buttonPP.callback = pp_callback
          buttonNP.callback = np_callback
          inView = View(timeout=600)
          inView.add_item(buttonPP)
          inView.add_item(buttonNP)

          embedVar = discord.Embed(color=0x9457EB)
          embedVar.set_image(url=response["data"][0]["url"])
          embedVar.set_footer(text=f"Image : {index}/{number}\nPrompt : {prompt}\nRequested by : {ctx.author.name}", icon_url=ctx.author.avatar.url)
          imgMsg = await ctx.respond(embed=embedVar, view=inView)
          checkView = await inView.wait()

          if checkView:
            embedVar = discord.Embed(color=0x9457EB)
            embedVar.set_image(url=response["data"][index-1]["url"])
            embedVar.set_footer(text=f"Image : {index}/{number}\nPrompt : {prompt}\nRequested by : {ctx.author.name}", icon_url=ctx.author.avatar.url)
            await imgMsg.edit_original_response(embed=embedVar, view=None)
          
    except Exception as e :
      embedVar = discord.Embed(
            title=f"[ Error!!! ]",
            description=f"Maaf, fiturnya lagi error, coba tanya ke yg bikin bot deh.",
            color=0x28282B)
      await ctx.respond(embed=embedVar)
      print(e)
        
def setup(bot):
  bot.add_cog(GenerateImg(bot))