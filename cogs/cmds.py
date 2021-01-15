import json
from discord.ext import commands

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def autorole(self, ctx):
        """ Set autorole rules. """
        role = ctx.message.content.split(" ")[-2]
        timer = ctx.message.content.split(" ")[-1]
        if type(timer) != int() and timer.lower() == "clear":
            with open("conf.json") as js:
                dat = json.load(js)
            del dat['autoroles'][role]
        timer = float(timer)*60*60
        with open("conf.json") as js:
            dat = json.load(js)
        dat['autoroles'][role] = timer
        with open("conf.json", 'w') as js:
            json.dump(dat, js)
