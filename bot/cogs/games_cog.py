import discord
import requests
from discord.ext import commands

import base64
from bot import constants

class GameApiCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_json(self, url, params={}):
        headers = {
            "TRN-Api-Key": constants.tracker_token
        }
        return requests.get(url, params=params, headers=headers).json()

    @commands.group(name="game")
    async def game_group(self, ctx):
        """
        get info on players from games.
        """

    @game_group.command(name="apex")
    async def apex_command(self, ctx, platform, user):
        json = self.get_json(f"https://public-api.tracker.gg/v2/apex/standard/profile/{platform}/{user}")
        data = json["data"]
        segments = data["segments"]
        for segemnt in segments:
            if segemnt["type"] == "overview":
                overview = segemnt
                break

        stats = overview["stats"]
        level = int(stats["level"]["value"])
        rank = int(stats["rankScore"]["value"])

        embed = discord.Embed()
        embed.color = discord.Color.red()
        embed.title = f"apex stats for {user}"
        img = stats["rankScore"]["metadata"]["iconUrl"]
        embed.set_thumbnail(url=img)

        level = int(stats["level"]["value"])
        rank = int(stats["rankScore"]["value"])
        embed.add_field(name="levels", value=(
            f"**level**: {level}\n"
            f"**rank**: {rank}"
        ))

        legends = []
        for segemnt in segments:
            if segemnt["type"] == "legend":
                legends.append(segemnt)

        for legend in legends:
            name = legend["metadata"]["name"]

            content = []
            for skill in legend["stats"].values():
                display = skill["displayName"]
                value = int(skill["value"])
                content.append(f"**{display}**: {value}")

            embed.add_field(name=name, value="\n".join(content))

        await ctx.send(embed=embed)


    @game_group.command(name="overwatch")
    async def overwatch_api(self, ctx, platform, user):
        json = self.get_json(f"https://public-api.tracker.gg/v2/overwatch/standard/profile/{platform}/{user.replace('#', '%23')}")

        if json.get("errors"):
            await ctx.send(json["errors"][0]["message"])
            return

        segments = json["data"]["segments"]
        heros = []
        for segment in segments:
            if segment["type"] == "hero":
                heros.append(segment)
            elif segment["metadata"]["name"] == "Casual":
                casual = segment
            else:
                competitive = segment

        embed = discord.Embed()
        embed.title = f"Stats for {user}"
        embed.color = discord.Color.gold()

        stats = casual["stats"]
        wins = stats["wins"]["value"]
        kills = stats["eliminations"]["value"]
        death = stats["deaths"]["value"]
        time_played = stats["timePlayed"]["displayValue"]

        embed.add_field(name="Casual", value=(
            f"**win:** {wins}\n "
            f"**kills:** {kills}\n "
            f"**death:** {death}\n "
            f"**time_played:** {time_played} "
        ))

        stats = competitive["stats"]
        wins = stats["wins"]["value"]
        kills = stats["eliminations"]["value"]
        death = stats["deaths"]["value"]
        time_played = stats["timePlayed"]["displayValue"]

        embed.add_field(name="competitive", value=(
            f"**win:** {wins}\n "
            f"**kills:** {kills}\n "
            f"**death:** {death}\n "
            f"**time_played:** {time_played} "
        ))

        def key(stat):
            def func(x):
                return x["stats"][stat]["value"]
            return func
        if heros:
            most_played = max(heros, key=key("timePlayed"))
            most_wins = max(heros, key=key("wins"))
            most_kills = max(heros, key=key("eliminations"))
            most_gold = max(heros, key=key("goldMedals"))

            embed.add_field(name="records", value=(
                f"most played: {most_played['metadata']['name']} ({most_played['stats']['timePlayed']['value']})\n"
                f"most wins: {most_wins['metadata']['name']} ({most_wins['stats']['wins']['value']})\n"
                f"most kills: {most_kills['metadata']['name']} ({most_kills['stats']['eliminations']['value']})\n"
                f"most gold medals: {most_gold['metadata']['name']} ({most_gold['stats']['goldMedals']['value']})\n"
            ))

        await ctx.send(embed=embed)

    @game_group.command(name="minecraft")
    async def minecraft_command(self, ctx, host):
        json = requests.get(f"https://api.mcsrvstat.us/2/{host}").json()
        if not json["online"]:
            await ctx.send("sever not found or offline")
            return

        embed = discord.Embed()
        embed.color = discord.Color.green()
        name = f"**{host}**"
        embed.title = f"**{name}**"

        motd = "\n".join(json["motd"]["clean"])
        embed.add_field(name="motd", value=motd)

        versions = json["version"]
        if isinstance(versions, str):
            versions = [versions]
        versions = ", ".join(versions)
        ip = json["ip"]
        port = json["port"]
        embed.add_field(name="info", value=(
            f"**versions**: {versions}\n"
            f"**ip**: {ip}\n"
            f"**port**: {port}"
        ))

        max_players = json["players"]["max"]
        players_online = json["players"]["online"]
        if json["players"].get("list"):
            players = json["players"]["list"]
            if players_online == 0:
                players = ["no one online"]
        else:
            players = ["data not found"]
        embed.add_field(name=f"players ({players_online}/{max_players})", value="\n".join(players))

        if json.get("icon"):
            base64_string = json["icon"].split(",")[-1].encode()
            with open("minecraft_icon.png", "wb+") as f:
                imgdata = base64.b64decode(base64_string)
                f.write(imgdata)

            file = discord.File('minecraft_icon.png')
            embed.set_thumbnail(url='attachment://icon.png')

            await ctx.send(embed=embed, file=file)
        else:
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(GameApiCog(bot))