import json
import traceback

import requests
from discord.ext import commands

from bs4 import BeautifulSoup

class ApiCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def parse_keys(keys):
        adding_to_keys = True
        the_keys = []
        params = {}
        for key in keys:
            if key == "params":
                adding_to_keys = False
            elif key == "keys":
                adding_to_keys = True
            elif adding_to_keys:
                the_keys.append(key)
            else:
                param = key.split("=")
                params[param[0]] = param[1]
        return the_keys, params

    @commands.group("api")
    async def api_group(self, ctx, ):
        """
        interface with a api
        """
        pass

    @api_group.command(name="json")
    async def json_command(self, ctx, url: str, *keys: str):
        """
        interface with a json api

        .api url [json keys]
        .api url params [params] keys [json keys]
        .api url [json keys] params [params]
        """
        json_keys, params = self.parse_keys(keys)

        try:
            r = requests.get("http://"+url, params=params)
        except Exception as e:
            print(traceback.format_exc())
            await ctx.send(f"request error\n: {e}")
            return

        if r.status_code in range(400, 600):
            await ctx.send(f"status code: **{r.status_code}**\nending api requests")
            return

        try:
            json_dict = r.json()
        except Exception as e:
            print(traceback.format_exc())
            await ctx.send(f"json decoding error\n: {e}")
            return

        dicts = [json_dict]
        try:
            for key in json_keys:
                if key.count("-") == 1:
                    a, b = key.split("-")
                    if a.isnumeric() and b.isnumeric():
                        tags = tags[int(a):int(b)]
                        continue
                new_dicts = []
                for dict_ in dicts:
                    if key == "*":
                        if isinstance(dict_, dict):
                            new_dicts.extend(dict_.values())
                        else:
                            new_dicts.extend(dict_)
                    else:
                        if isinstance(dict_ ,list):
                            new_dicts.append(dict_[int(key)])
                        else:
                            new_dicts.append(dict_[key])
                dicts = new_dicts

            await ctx.send(json.dumps(dicts if len(dicts) > 1 else dicts[0], indent=4))
        except Exception as e:
            print(traceback.format_exc())
            await ctx.send(f"json key error\n: {e}")
            return

    @api_group.command(name="html")
    async def html_command(self, ctx, url, *keys):
        """
        interface with a html page

        .api url [html keys]
        .api url params [params] keys [html keys]
        .api url [html keys] params [params]

        keys:
        nothing: find the first
        *: find all
        $: get attr
        a-b: shorten list between a and b
        a: select a form list.
        a=b: find tag(s) with that attr, like: class=title
        """
        html_keys, params = self.parse_keys(keys)

        try:
            r = requests.get("http://" + url, params=params)
        except Exception as e:
            print(traceback.format_exc())
            await ctx.send(f"request error\n: {e}")
            return

        if r.status_code in range(400, 600):
            await ctx.send(f"status code: **{r.status_code}**\nending api requests")
            return

        html = r.content
        soup = BeautifulSoup(html, "html.parser")
        tags = [soup]
        try:
            for key in html_keys:
                new_tags = []

                if key.count("-") == 1:
                    a, b = key.split("-")
                    if a.isnumeric() and b.isnumeric():
                        tags = tags[int(a):int(b)]
                        continue
                elif key.isnumeric():
                    tags = [tags[int(key)]]
                    continue

                for tag in tags:
                    if key.startswith("*"):
                        key = key[1:]
                        find_all = True
                    else:
                        find_all = False

                    if key.startswith("$"):
                        new_tags.append(getattr(tag, key[1:]))
                        continue
                    if key.count("=") == 1:
                        prefix, value = key.split("=")
                        if prefix == "class":
                            prefix = "class_"
                        if find_all:
                            new_tags.extend(tag.find_all(class_=value))
                        else:
                            new_tags.append(tag.find(class_=value))
                    else:
                        if find_all:
                            new_tags.extend(tag.find_all(key))
                        else:
                            new_tags.append(tag.find(key))
                tags = new_tags
        except Exception as e:
            await ctx.send(f"html keys error:\n{e}")
            return
        tags_to_print = []
        for tag in tags:
            tags_to_print.append(str(tag))
        try:
            await ctx.send(json.dumps(tags_to_print if len(tags_to_print) > 1 else tags_to_print[0], indent=4))
        except Exception:
            await ctx.send("to long")

def setup(bot):
    bot.add_cog(ApiCog(bot))
