import discord
import pymongo
import os
import requests
from discord.ext import commands
from discord import app_commands

MONGODB = os.environ['MONGODB']

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]


def get_evolution_names(chain):
    evo_name = chain['species']['name'].capitalize()
    if evo_name.lower() == 'porygon-z':
        evo_name = 'Porygon-Z'

    evolution_names = [evo_name]
    for evolution in chain['evolves_to']:
        evolution_names.extend(get_evolution_names(evolution))
    return evolution_names


class Pokeinfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name='pokeinfo',
        description='Check the information of a specific pokemon')
    @app_commands.describe(poke="The name of pokemon to check")
    async def pokemon_info(self, ctx: discord.Interaction, poke: str):
        await ctx.response.defer()

        pokeFind = mycol.find_one({"func": "pokedb"})
        pokeBasic = pokeFind["basic"]
        pokeElite = pokeFind["elite"]
        pokeEpic = pokeFind["epic"]
        pokeLegend = pokeFind["legend"]
        poke = poke[0].upper() + poke[1:].lower()

        if poke.lower() == 'porygon-z':
            poke = 'Porygon-Z'

        if poke in pokeBasic or poke in pokeElite or poke in pokeEpic or poke in pokeLegend:
            response = requests.get(
                f'https://pokeapi.co/api/v2/pokemon/{poke.lower()}')
            data = response.json()

            speciesResp = requests.get(
                f'https://pokeapi.co/api/v2/pokemon-species/{poke.lower()}')
            speciesData = speciesResp.json()

            evoResp = requests.get(speciesData['evolution_chain']['url'])
            evoData = evoResp.json()

            embedVar = discord.Embed(
                title=f"PokeInfo!",
                description=f'{poke} | ID : {str(data["id"])}',
                color=0xee1515)
            eleString = ', '.join(
                [t['type']['name'].capitalize() for t in data['types']])

            evolution_names = get_evolution_names(evoData['chain'])
            evoString = ', '.join(evolution_names)
            speciesString = ', '.join(
                [s['name'].capitalize() for s in speciesData['egg_groups']])

            if poke in pokeBasic:
                rarityChk = 'Basic'

            elif poke in pokeElite:
                rarityChk = 'Advanced'

            elif poke in pokeEpic:
                rarityChk = 'Epic'

            elif poke in pokeLegend:
                rarityChk = 'Legendary'

            embedVar.add_field(
                name=f"[ General ]",
                value=
                ('```' + f'Type     : {eleString}\n'
                 f'Rarity   : {rarityChk}\n'
                 f'Gen      : {speciesData["generation"]["name"].split("-")[1].upper()}\n'
                 f'Species  : {speciesString}\n'
                 f'Height   : {data["height"] / 10} m\n'
                 f'Weight   : {data["weight"] / 10} kg\n' + '```'),
                inline=True)

            embedVar.add_field(
                name=f"[ Stats (Lv. 1) ]",
                value='```' +
                f'HP       : {str(data["stats"][0]["base_stat"])}\n'
                f'Atk      : {str(data["stats"][1]["base_stat"])}\n' +
                f'Sp. Atk  : {str(data["stats"][3]["base_stat"])}\n' +
                f'Def      : {str(data["stats"][2]["base_stat"])}\n' +
                f'Sp. Def  : {str(data["stats"][4]["base_stat"])}\n' +
                f'Speed    : {str(data["stats"][5]["base_stat"])}\n' + '```',
                inline=True)

            embedVar.add_field(
                name=f"[ Evolutionary ]",
                value='```' +
                f'Stage  : {evoString.split(", ").index(poke) + 1}\n' +
                f'Path   : {evoString}\n' + '```',
                inline=False)
            embedVar.set_thumbnail(
                url=data['sprites']['other']['showdown']['front_default'])
            embedVar.set_footer(text=speciesData['flavor_text_entries'][0]
                                ['flavor_text'].replace('\n', ' ').replace(
                                    '\f', ' '),
                                icon_url=data["sprites"]["front_default"])

            await ctx.followup.send(embed=embedVar)

        else:
            await ctx.followup.send(
                "Pokemon yang anata cari tidak / belum terdaftar, coba dicek lagi yah..",
                ephemeral=True)


async def setup(bot):
    await bot.add_cog(Pokeinfo(bot))
