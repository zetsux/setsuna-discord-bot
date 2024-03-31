from discord.ext import commands

def get_cooldown_str(cooldown):
  if cooldown > 3600:
      hourLeft = cooldown / 3600
      minLeft = (cooldown % 3600) / 60
      secLeft = (cooldown % 3600) % 60
      return (f'Duration Left : {int(hourLeft)} hour(s), {int(minLeft)} minute(s), and {int(secLeft)} second(s)')

  elif cooldown > 60:
      minLeft = cooldown / 60
      secLeft = cooldown % 60
      return (f'Duration Left : {int(minLeft)} minute(s) and {int(secLeft)} second(s)')

  else:
      return (f'Duration Left : {int(cooldown)} second(s)')

async def handle_command_error(ctx, error, logChannel, isApplicationCommand = False):
  if isinstance(error, commands.errors.CheckFailure):
      if isApplicationCommand:
        await ctx.respond(f'Gomenasai {ctx.message.author}-nyan, anata ngga punya hak buat nyuruh watashi pakai command itu...')
      else:
        await ctx.channel.send(f'Gomenasai {ctx.message.author}-nyan, anata ngga punya hak buat nyuruh watashi pakai command itu...')

  elif isinstance(error, commands.CommandOnCooldown):
      if isApplicationCommand:
          await ctx.respond(f'Command is is still on cooldown...\n' + get_cooldown_str(error.retry_after), ephemeral=True)
      else:
          await ctx.channel.send(f'Command !{ctx.invoked_with} is still on cooldown...\n' + get_cooldown_str(error.retry_after))

  else:
      print(error)
      try:
          await logChannel.send(error)
      except:
          await logChannel.send('Error tapi kepanjangan bro...')