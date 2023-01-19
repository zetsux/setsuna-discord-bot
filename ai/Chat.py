import discord
import os
import pymongo
import datetime
from discord.ui import Select, Button, Modal, InputText, View
from discord.ext import commands
from discord.commands import Option
import numpy as np
import aiohttp

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]

CHATAPIKEY = os.environ['CHATKEY']

class Chat(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @commands.slash_command(name='setsuchat', description='Chat with or Ask things to Setsuna')
  @commands.has_any_role('Encoder Magang', 'Owner')
  async def chatCommand(self, ctx, prompt: Option(str, "Chat to send", required=True)):
    await ctx.defer()
    try :
      async with aiohttp.ClientSession() as session:
        pl = {
          "model": "text-davinci-003",
          "prompt": prompt,
          "temperature": 0.5,
          "max_tokens": 4000,
          "presence_penalty": 0,
          "frequency_penalty": 0,
          "best_of": 1,
        }
        h = {"Authorization": f"Bearer {CHATAPIKEY}"}
        
        async with session.post("https://api.openai.com/v1/completions", json=pl, headers=h) as r:
          response = await r.json()
          embedVar = discord.Embed(
            title=f"Setsuna :",
            description="```" + response["choices"][0]["text"] + "```",
            color=0x9457EB)
          await ctx.respond(embed=embedVar)

    except Exception as e :
      embedVar = discord.Embed(
            title=f"[ Error!!! ]",
            description=f"Maaf, fiturnya lagi error, coba tanya ke yg bikin bot deh.",
            color=0x28282B)
      await ctx.respond(embed=embedVar)
      print(e)
        
def setup(bot):
  bot.add_cog(Chat(bot))