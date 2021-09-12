import base64
import json
import requests
from discord.ext import commands
from discord import Activity
from discord import ActivityType
from io import BytesIO

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def autorole(self, ctx):
        """ [role] [time] - `O`"""
        if not ctx.author.id == self.bot.dg.owner.id:
            return await ctx.error("Insufficient permissions. Must be server owner.")
        with open("conf.json") as js:
            dat = json.load(js)
        if len(ctx.message.content.split()) == 1:
            tx = "Roles:\n"
            for rl in dat['autoroles']:
                grl = self.bot.dg.get_role(int(rl))
                tx += f"`{grl.name}` - {dat['autoroles'][rl]/(60*60)} hrs\n"
            if not dat['autoroles']:
                tx += "No autoroles setup. Please use the `>>autorole` command."
            return await ctx.embed_reply(tx)
        trole = ctx.message.content.split(" ")[-2]
        role = None
        for srole in ctx.guild.roles:
            if srole.name == trole:
                role = srole
                break

        if not role:
            return await ctx.error(f"Couldn't find a role named {trole}", delete_after=5)
        bmem = self.bot.dg.get_member(self.bot.user.id)
        if role >= bmem.top_role:
            return await ctx.error(f"Can't assign role equal or higher than the bot's role.", delete_after=5)

        timer = ctx.message.content.split(" ")[-1]
        if type(timer) != int() and timer.lower() == "clear":
            with open("conf.json") as js:
                dat = json.load(js)
            del dat['autoroles'][str(role.id)]
            with open("conf.json", 'w') as js:
                json.dump(dat, js)
            return await ctx.embed_reply(msg=f"Successfully Removed {role.name} as an autorole "
                                        , delete_after=5)

        timer = float(timer)*60*60
        dat['autoroles'][role.id] = timer
        with open("conf.json", 'w') as js:
            json.dump(dat, js)

        await ctx.embed_reply(msg=f"Successfully Added `{role.name}` as an autorole "
                                  f"which will be added after `{timer/(60*60)}` hours.", delete_after=5)

    @commands.command()
    async def purge(self, ctx):
        """ [user] [number] - `M`"""
        if not ctx.author.permissions_in(ctx.channel).manage_messages:
            return await ctx.error("Insufficient permissions. `Manage Messages` is required.", delete_after=5)

        if ctx.message.mentions:
            user = ctx.message.mentions[0]
        else:
            user = None
        try:
            amount = int(ctx.message.content.split(" ")[-1])
        except:
            return await ctx.error("Please enter a value for amount of messages to delete.", delete_after=5)

        if amount > 10:
            amount = 10

        print("Delete amount", amount)

        counter = 0
        if user:
            async for message in ctx.channel.history(limit=amount+200):
                if message.author == user:
                    await message.delete()
                    counter += 1
                    if counter >= amount:
                        break
        else:
            async for message in ctx.channel.history(limit=amount):
                await message.delete()
                counter += 1
                if counter >= amount:
                    break


        await ctx.embed_reply(msg=f"Successfully Deleted {counter} messages.", delete_after=5)

    @commands.command()
    async def wipe(self, ctx):
        """ [user] - `O`"""
        if not ctx.author.id == self.bot.dg.owner.id:
            return await ctx.error("Insufficient permissions. Must be server owner.", delete_after=5)

        if ctx.message.mentions:
            user = ctx.message.mentions[0]
            uid = None
        else:
            uid = ctx.message.content.split(" ")[1]
            user = None
            if len(uid) < 2:
                return await ctx.error("Please mention a user.")
            else:
                uid = int(uid)

        counter = 0
        async with ctx.channel.typing():
            for c in ctx.guild.text_channels:
                async for message in c.history(limit=30000):
                    if user and message.author == user:
                        await message.delete()
                        counter += 1
                    elif uid and message.author.id == uid:
                        await message.delete()
                        counter += 1

        await ctx.embed_reply(msg=f"Successfully Deleted {counter} messages.", delete_after=5)

    @commands.command()
    async def mute(self, ctx):
        """ [user] - `M`"""
        if not ctx.author.permissions_in(ctx.channel).manage_messages:
            return await ctx.error("Insufficient permissions. `Manage Messages` is required.", delete_after=5)

        if ctx.message.mentions:
            user = ctx.message.mentions[0]
        else:
            return await ctx.error("Please mention a user.", delete_after=5)

        with open("conf.json") as f:
            dat = json.load(f)

        if user.id not in dat['muted']:
            dat['muted'].append(user.id)

        with open("conf.json", 'w') as js:
            json.dump(dat, js)

        self.bot.update_quick_access(dat)

        await ctx.embed_reply(msg=f"Successfully muted `{user.display_name}`.", delete_after=5)

    @commands.command()
    async def mutelist(self, ctx):
        """  - `M`"""
        if not ctx.author.permissions_in(ctx.channel).manage_messages:
            return await ctx.error("Insufficient permissions. `Manage Messages` is required.", delete_after=5)


        with open("conf.json") as f:
            dat = json.load(f)

        tx = "Muted Users:\n"
        counter = 0
        for mt in dat['muted']:
            try:
                user = self.bot.dg.get_member(mt)
                tx += f"`{user.name}#{user.discriminator}`\n"
                counter += 1
            except:
                pass

        if counter < 1:
            tx += "No Muted Users."

        await ctx.embed_reply(msg=tx)

    @commands.command()
    async def unmute(self, ctx):
        """ [user] - `M`"""
        if not ctx.author.permissions_in(ctx.channel).manage_messages:
            return await ctx.error("Insufficient permissions. `Manage Messages` is required.", delete_after=5)

        if ctx.message.mentions:
            user = ctx.message.mentions[0]
        else:
            return await ctx.error("Please mention a user.", delete_after=5)

        with open("conf.json") as f:
            dat = json.load(f)

        if user.id in dat['muted']:
            try:
                dat['muted'].remove(user.id)
            except:
                pass


        with open("conf.json", 'w') as js:
            json.dump(dat, js)

        self.bot.update_quick_access(dat)

        await ctx.embed_reply(msg=f"Successfully unmuted `{user.display_name}`.", delete_after=5)

    @commands.command()
    async def icon(self, ctx):
        """ """
        if not ctx.author.id == self.bot.dg.owner.id:
            return await ctx.error("Insufficient permissions. Must be server owner.", delete_after=5)
        url = ctx.message.content.split(" ")[-1]
        if "http" not in url:
            return await ctx.error("Please submit valid image URL.", delete_after=5)

        await self.bot.user.edit(avatar=requests.get(url).content)
        await ctx.embed_reply(msg=f"Successfully changed avatar.", delete_after=5)

    @commands.command()
    async def status(self, ctx):
        """ """
        if not ctx.author.id == self.bot.dg.owner.id:
            return await ctx.error("Insufficient permissions. Must be server owner.", delete_after=5)
        stattext = ctx.message.content.split(" ")
        status = " ".join(stattext[1:len(stattext)])
        print(status)
        gm = Activity(name=status, type=ActivityType.watching)

        await self.bot.change_presence(activity=gm)
        await ctx.embed_reply(msg=f"Successfully changed presence.", delete_after=5)

    @commands.command()
    async def roleadd(self, ctx):
        if not ctx.author.id == self.bot.dg.owner.id:
            return await ctx.error("Insufficient permissions. Must be server owner.")
        with open("conf.json") as js:
            dat = json.load(js)
        trole = ctx.message.content.split(" ")[-1]
        role = None
        for srole in ctx.guild.roles:
            if srole.name == trole:
                role = srole
                break

        if not role:
            return await ctx.error(f"Couldn't find a role named {trole}", delete_after=5)
        bmem = self.bot.dg.get_member(self.bot.user.id)
        if role >= bmem.top_role:
            return await ctx.error(f"Can't assign role equal or higher than the bot's role.", delete_after=5)
        if "setuproles" not in dat:
            dat["setuproles"] = []
        if role.name.lower() in dat['setuproles']:
            return await ctx.error("Role already setup!")
        else:
            dat["setuproles"].append(role.name.lower())
        with open("conf.json", "w") as js:
            json.dump(dat, js)
        return await ctx.embed_reply(msg=f"Successfully setup {role.name}."
                                     , delete_after=5)

    @commands.command()
    async def roleclear(self, ctx):
        if not ctx.author.id == self.bot.dg.owner.id:
            return await ctx.error("Insufficient permissions. Must be server owner.")
        with open("conf.json") as js:
            dat = json.load(js)
        trole = ctx.message.content.split(" ")[-1]

        if "setuproles" not in dat:
            return await ctx.error("No roles setup!")

        if trole.lower() in dat['setuproles']:
            del dat['setuprole'][dat['setuproles'].index(trole.lower())]

        with open("conf.json", "w") as js:
            json.dump(dat, js)
        return await ctx.embed_reply(msg=f"Successfully deleted {trole}."
                                     , delete_after=5)

    @commands.command()
    async def role(self, ctx):
        with open("conf.json") as js:
            dat = json.load(js)
        trole = ctx.message.content.split(" ")[-1]
        if "setuproles" not in dat:
            return await ctx.error("No roles setup!")

        if trole.lower() in dat['setuproles']:
            role = None
            for srole in ctx.guild.roles:
                if srole.name.lower() == trole.lower():
                    role = srole
                    break
            if role in ctx.author.roles:
                try:
                    await ctx.author.remove_roles(role, reason="Role Command.")
                    return await ctx.embed_reply(msg=f"Successfully removed {trole}."
                                                 , delete_after=5)
                except:
                    return await ctx.error("Error")
            else:
                try:
                    await ctx.author.add_roles(role, reason="Role Command.")
                    return await ctx.embed_reply(msg=f"Successfully assigned {trole}."
                                                 , delete_after=5)
                except:
                    return await ctx.error("Error")


def setup(bot):
    bot.add_cog(Commands(bot))