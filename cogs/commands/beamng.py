import json
import re
import aiohttp
import pycountry
import discord

from ..api.redis import RedisClient
from ..api import config


async def sizeof_fmt(num, suffix="B"):
    """Format filesize"""
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, "Yi", suffix)


async def read_api():
    """Read the beamng API"""
    redis_client = RedisClient()
    data = await redis_client.get_from_cache("beamMp:servers")
    if data is not None:
        # To not spam their api
        result = json.loads(data)
    else:
        async with aiohttp.ClientSession() as session:
            url = "https://backend.beammp.com/servers-info"
            async with session.get(url) as r:
                result = await r.json()
                data = json.dumps(result)
                await redis_client.set_to_cache(
                    "beamMp:servers",
                    data,
                    config.CACHE_MAX_AGE_SERVERS,
                )
    return result


async def readable_list(_s):
    """Make human readable list of items"""
    if len(_s) < 3:
        return " and ".join(map(str, _s))
    *a, b = _s
    return f"{', '.join(map(str, a))}, and {b}"


async def mpname(interaction: discord.Interaction, searchterm: str):
    """Search beamp server by name"""
    result = await read_api()
    author = interaction.user
    for server in result:
        owner = server.get("owner", "")
        playerlist = server.get("players", 0)
        maxplayers = server.get("maxplayers", 0)
        modstotal = server.get("modstotal", 0)
        modstotalsize = await sizeof_fmt(int(server.get("modstotalsize", 0)))
        servername = re.sub(r"\^[a-z_0-9]", "", server.get("sname", ""))
        country = pycountry.countries.get(alpha_2=server.get("location", ""))
        modarr = re.split(";", server.get("modlist", ""))
        modstring = ""
        for item in modarr:
            newitem = (
                item.replace("Resources/Client/", "")
                .replace(".zip", "")
                .replace("C:/Users/Administrator/Desktop/BeamMP server/", "")
            )
            modstring += f"{newitem}, "
        playerarr = re.split(";", server.get("playerslist", "").rstrip(";"))
        modstring2 = ""
        if searchterm.lower() in servername.lower():
            embed = discord.Embed(
                color=0xFFA500,
                title=f"{owner}'s server",
                description=servername[0:70],
            )
            embed.set_author(name="BeamMP Stats", icon_url=author.avatar.url)
            embed.add_field(
                name=f"**{playerlist}/{maxplayers}** Players",
                value=await readable_list(playerarr),
                inline=False,
            )
            embed.add_field(
                name="Map",
                value=server.get("map", "")
                .replace("/levels/", "")
                .replace("/info.json", "")
                .replace("_", " ")
                .capitalize(),
                inline=True,
            )
            try:
                embed.add_field(name="Location", value=country.name, inline=True)
            except:
                pass
            if len(modstring[:-2]) > 1000:
                modstring1 = modstring[:900]
                modstring2 = modstring[900:-4]
            else:
                modstring1 = modstring[:-4]
            embed.add_field(
                name=f"**{modstotal}** Mods **({modstotalsize})**",
                value=f"```{modstring1}```",
                inline=False,
            )
            if modstring2 != "":
                embed.add_field(
                    name="\u200b", value=f"```{modstring2}```", inline=False
                )
            embed.set_author(name="BeamMP Stats")
            await interaction.followup.send(embed=embed)
            break


async def mpdiscord(interaction: discord.Interaction, discord_tag: str):
    """Search beamp server by discord tag"""
    result = await read_api()
    total_players = 0
    matching_servers = []
    for server in result:
        if server.get("owner", "") == discord_tag:
            matching_servers.append(server)
            total_players += int(server.get("players", 0))
    if len(matching_servers) > 0:
        await server_return(
            interaction,
            f'Servers of "{discord_tag}"',
            matching_servers,
            total_players,
        )
    else:
        embed = discord.Embed(
            color=0xE74C3C, description="No servers found with that owner name"
        )
        await interaction.followup.send(embed=embed)


async def server_return(
    interaction: discord.Interaction,
    title: str,
    servers: list[dict],
    total_players: int,
):
    """Makes the embed for discord"""
    embed = discord.Embed(color=0xFFA500, title=title)
    for server in servers[:10]:
        server_map = (
            server.get("map", "")
            .replace("/levels/", "")
            .replace("/info.json", "")
            .replace("_", " ")
        )
        embed.add_field(
            name=re.sub(r"\^[a-z_0-9]", "", server.get("sname", "")),
            value=f"on **{server_map}** with **{server.get('players', 0)}/{server.get('maxplayers', 0)}** players and **{server.get('modstotal', 0)}** mods",
            inline=False,
        )

    embed.add_field(name="Total:", value=f"**{total_players}** players", inline=False)
    await interaction.followup.send(embed=embed)


async def mpip(interaction: discord.Interaction, server_ip: str):
    """Search beamp server by ip adress"""
    result = await read_api()
    total_players = 0
    matching_servers = []
    for server in result:
        if server.get("ip", "") == server_ip:
            total_players += int(server.get("players", 0))
            matching_servers.append(server)
    if len(matching_servers) > 0:
        await server_return(
            interaction,
            f'Servers on "{server_ip}"',
            matching_servers,
            total_players,
        )
    else:
        embed = discord.Embed(
            color=0xE74C3C, description="No servers found with that ip address"
        )
        await interaction.followup.send(embed=embed)


async def mpinfo(interaction: discord.Interaction):
    """Info about all servers"""
    result = await read_api()
    players = 0
    allplayers = 0
    official = 0
    allmaps = []
    locations = {}
    countrystring = ""
    for server in result:
        official += int(server.get("official", 0))
        map_name = (
            server.get("map", "")
            .replace("/levels/", "")
            .replace("/info.json", "")
            .replace("_", " ")
        )
        players += int(server.get("players", 0))
        allplayers += int(server.get("maxplayers", 0))
        if map_name in allmaps:
            pass
        else:
            allmaps.append(map_name)
        country_item = pycountry.countries.get(alpha_2=server.get("location", ""))
        country = "Unknown"
        if country_item is not None:
            country = country_item.name

        if country in locations:
            locations[country] += 1
        else:
            locations[country] = 1
    locations = dict(sorted(locations.items(), key=lambda item: item[1], reverse=True))
    for key, _val in locations.items():
        countrystring += f"**{locations[key]}** servers in {key}\n"
    embed = discord.Embed(
        color=0xFFA500,
        title="All BeamMP servers stats",
        description=f"**{players}/{allplayers}** players\n **{len(result)}** servers with **{official}** official servers\n and **{len(allmaps)}** unique maps",
    )
    embed.add_field(
        name="Locations:",
        value="\n".join(countrystring.split("\n")[:10]) + "\n...",
        inline=False,
    )
    await interaction.followup.send(embed=embed)
