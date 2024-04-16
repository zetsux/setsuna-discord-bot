from webserver import keep_alive
import os
import discord
from discord.ext import commands
import pymongo
import wavelink
from wavelink.ext import spotify
import asyncio
import events.song as song_events
import events.error as error_events

TOKEN = os.environ['TOKEN']
ROLECLAIM = int(os.environ['ROLEMSGID'])
MONGODB = os.environ['MONGODB']
LORENDB = os.environ['LORENDB']
LVLINKHOST = os.environ['LVLINKHOST']
LVLINKPORT = int(os.environ['LVLINKPORT'])
LVLINKPASS = os.environ['LVLINKPASS']
LVLINKSSL = (os.environ['LVLINKSSL'] == '1')
SPOTIFYSECRET = os.environ['SPOTIFYSECRET']
SPOTIFYID = os.environ['SPOTIFYID']
SONGCH = int(os.environ['SONGCHID'])
GUILDID = int(os.environ['GUILDID'])
CSGUILDID = int(os.environ['CSGUILDID'])
CSSONGCH = int(os.environ['SONGCSID'])
LOGCH = int(os.environ['LOGCHID'])
SPBGUILDID = int(os.environ['SPBGUILDID'])
SPBSONGCH = int(os.environ['SPBCHID'])
NGGUILDID = int(os.environ['NGGUILDID'])
NGSONGCH = int(os.environ['NGCHID'])
ZSGUILDID = int(os.environ['ZSGUILDID'])
ZSSONGCH = int(os.environ['ZSCHID'])

guildList = [GUILDID, CSGUILDID, SPBGUILDID, NGGUILDID, ZSGUILDID]
songchList = [SONGCH, CSSONGCH, SPBSONGCH, NGSONGCH, ZSSONGCH]

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!$', intents=intents)


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, name="u from afar | /help"))

    bot.loop.create_task(connect_nodes())


@bot.event
async def on_wavelink_node_ready(node: wavelink.Node):
    print(f'The Node {node.identifier} has also connected to Discord!')


async def connect_nodes():
    await bot.wait_until_ready()
    await wavelink.NodePool.create_node(bot=bot,
                                        host=LVLINKHOST,
                                        port=LVLINKPORT,
                                        password=LVLINKPASS,
                                        https=LVLINKSSL,
                                        spotify_client=spotify.SpotifyClient(
                                            client_id=SPOTIFYID,
                                            client_secret=SPOTIFYSECRET))


@bot.event
async def on_wavelink_track_end(player: wavelink.Player, track: wavelink.Track,
                                reason):
    await song_events.get_next_song(player, track, reason)


@bot.event
async def on_voice_state_update(member, before, after):
    await song_events.auto_leave(member, before, after, bot.user.id, guildList,
                                 songchList)


@bot.event
async def on_member_join(member):
    if member.bot:
        return

    await member.create_dm()
    await member.dm_channel.send(
        f'Halo {member.name}-nyan, watashi Setsuna yang akan mengurus anata di server baru, yoroshiku~'
    )


@bot.event
async def on_command_error(ctx, error):
    userFind = mycol.find_one({"userid": str(ctx.user.id)})
    if userFind == None:
        await ctx.channel.send(
            f'Neee {ctx.user.name}-nyan, yuk bisa yuk /regist dulu~')
        return

    guild = bot.get_guild(GUILDID)
    channel = guild.get_channel(LOGCH)
    await error_events.handle_command_error(ctx, error, channel)


@bot.event
async def on_application_command_error(ctx, error):
    userFind = mycol.find_one({"userid": str(ctx.user.id)})
    if userFind == None:
        await ctx.response.send_message(
            f'Neee {ctx.user.name}-nyan, yuk bisa yuk /regist dulu~',
            ephemeral=True)
        return

    guild = bot.get_guild(GUILDID)
    channel = guild.get_channel(LOGCH)
    await error_events.handle_command_error(ctx, error, channel, True)


# @bot.slash_command(name='resetcd', description='Reset cooldown of a command for self')
# @app_commands.checks.has_any_role('Encoder Magang', 'Owner')
# async def reset_cd(ctx, command: Option(str, "Name of command to reset", required=True)):
#   await ctx.defer(ephemeral=True)
#   bot.get_application_command(command).reset_cooldown(ctx)
#   await ctx.response.send_message(f'Cooldown command /{command} pada {ctx.user.name}-nyan berhasil direset!', ephemeral=True)

for folder in os.listdir("./"):
    path = f"./{folder}"

    if not os.path.isdir(path) or folder == "events":
        continue

    for filename in os.listdir(f"./{folder}"):
        if filename.endswith(".py"):
            try:
                print(f"{folder}.{filename[:-3]}")
                asyncio.run(bot.load_extension(f"{folder}.{filename[:-3]}"))
            except Exception as error:
                print(error)

keep_alive()
try:
    bot.run(TOKEN)
except discord.errors.HTTPException:
    print("Kena rate limit nih, bentar restart duls..")
    os.system('kill 1')
    os.system('python restart.py')
