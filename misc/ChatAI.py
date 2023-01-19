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

class ChatAI(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @commands.slash_command(name='chat', description='Chat with or Ask things to Setsuna (Using Davinci Textbot API from OpenAI)')
  @commands.has_any_role('Encoder Magang', 'Owner')
  async def chatGPT(self, ctx, prompt: Option(str, "Chat to send", required=True)):
    if ctx.author.id != 463203332027056129 :
      await ctx.respond(f'Gomenasai {ctx.message.author}-nyan, anata ngga punya hak buat nyuruh watashi pakai command itu...')
      return
    
    await ctx.defer()
    try :
      async with aiohttp.ClientSession() as session:
        pl = {
          "model": "text-davinci-003",
          "prompt": prompt,
          "temperature": 0.5,
          "max_tokens": 1000,
          "presence_penalty": 0,
          "frequency_penalty": 0,
          "best_of": 1
        }
        h = {"Authorization": f"Bearer {CHATAPIKEY}"}
        
        async with session.post("https://api.openai.com/v1/completions", json=pl, headers=h) as r:
          response = await r.json()
          embedVar = discord.Embed(
            title=f"[ Setsuna's Response ]",
            description="```" + response["choices"][0]["text"] + "```",
            color=0x9D00FF)
          await ctx.respond(embed=embedVar)

    except :
      embedVar = discord.Embed(
            title=f"[ Setsuna's Response ]",
            description=f"Maaf, fiturnya lagi error, coba tanya ke yg bikin bot deh.",
            color=0x28282B)
      await ctx.respond(embed=embedVar)
        
def setup(bot):
  bot.add_cog(ChatAI(bot))