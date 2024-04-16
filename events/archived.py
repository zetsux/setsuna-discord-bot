# @bot.event
# async def on_message(message):
#     if message.author == bot.user:
#       return

#     if "ajg" in message.content.lower() or "bgst" in message.content.lower():
#       await message.add_reaction('\U0001F974')
#       await message.channel.send(f'Kasar yaa, {message.author.name}-nyan')

#     await bot.process_commands(message)

# @bot.event
# async def on_message_edit(before, after):
#     if before.author == bot.user:
#         return

#     await before.add_reaction('\U0001F9D0')
#     await before.channel.send(
#         f'{before.author} abis edit msg nich di {before.channel.name}!\n\n'
#         f'Jadi awalnya gini :\n[ {before.content} ]\n\n'
#         f'Eh trus jadi gini :\n[ {after.content} ]'
#     )


# @bot.event
# async def on_raw_reaction_add(payload):
#     if payload.member == bot.user:
#         return

#     guild = bot.get_guild(payload.guild_id)
#     channel = guild.get_channel(payload.channel_id)
#     if payload.message_id == ROLECLAIM:
#         if payload.emoji.name == '🗿':
#             role = discord.utils.get(guild.roles, name='Player')
#             await payload.member.add_roles(role)
#         elif payload.emoji.name == '💀':
#             role = discord.utils.get(guild.roles, name='Hunter')
#             await payload.member.add_roles(role)
#         elif payload.emoji.name == '🤑':
#             role = discord.utils.get(guild.roles, name='Shopkeeper')
#             await payload.member.add_roles(role)
#         elif payload.emoji.name == '🧑‍🌾':
#             role = discord.utils.get(guild.roles, name='Villager')
#             await payload.member.add_roles(role)
#         elif payload.emoji.name == '👨‍🍳':
#             role = discord.utils.get(guild.roles, name='Cook')
#             await payload.member.add_roles(role)


# @bot.event
# async def on_raw_reaction_remove(payload):
#     if payload.message_id != ROLECLAIM:
#         return

#     guild = bot.get_guild(payload.guild_id)
#     member = guild.get_member(payload.user_id)

#     if payload.emoji.name == '🗿':
#         role = discord.utils.get(guild.roles, name='Player')
#         await member.remove_roles(role)
#     elif payload.emoji.name == '💀':
#         role = discord.utils.get(guild.roles, name='Hunter')
#         await member.remove_roles(role)
#     elif payload.emoji.name == '🤑':
#         role = discord.utils.get(guild.roles, name='Shopkeeper')
#         await member.remove_roles(role)
#     elif payload.emoji.name == '🧑‍🌾':
#         role = discord.utils.get(guild.roles, name='Villager')
#         await member.remove_roles(role)
#     elif payload.emoji.name == '👨‍🍳':
#         role = discord.utils.get(guild.roles, name='Cook')
#         await member.remove_roles(role)