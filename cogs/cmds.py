import json
from discord.ext import commands

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def autorole(self, ctx):
        """ Set autorole rules. """
        if not ctx.author.id == self.bot.dg.owner.id:
            return await ctx.error("Insufficient permissions. Must be server owner.")
        with open("conf.json") as js:
            dat = json.load(js)
        if len(ctx.message.content.split()) == 1:
            tx = "Roles:\n"
            for rl in dat['autoroles']:
                grl = self.bot.dg.get_role(int(rl))
                tx += f"`{grl.name}` - {dat['autoroles'][rl]/(60*60)}hrs\n"
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

        await ctx.embed_reply(msg=f"Successfully Added {role.name} as an autorole "
                                  f"which will be added after {timer} hours.", delete_after=5)

    @commands.command()
    async def purge(self, ctx):
        """ Purge a certain amount of messages from a channel. """
        if not ctx.author.permissions_in(ctx.channel).manage_messages:
            return await ctx.error("Insufficient permissions. `Manage Messages` is required.")

        if ctx.message.mentions:
            user = ctx.message.mentions[0]
        else:
            user = None
        try:
            amount = int(ctx.message.content.split[" "][-1])
        except:
            amount = 100

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
        """ Wipe a mentioned user's messages from a channel. """
        if not ctx.author.id == self.bot.dg.owner.id:
            return await ctx.error("Insufficient permissions. Must be server owner.")

        if ctx.message.mentions:
            user = ctx.message.mentions[0]
        else:
            return await ctx.error("Please mention a user.")

        counter = 0
        async with ctx.channel.typing():
            for c in ctx.guild.text_channels:
                async for message in c.history(limit=30000):
                    if message.author == user:
                        await message.delete()
                        counter += 1


        await ctx.embed_reply(msg=f"Successfully Deleted {counter} messages.", delete_after=5)

    @commands.command()
    async def mute(self, ctx):
        """ Mute a mentioned user. """
        if not ctx.author.permissions_in(ctx.channel).manage_messages:
            return await ctx.error("Insufficient permissions. `Manage Messages` is required.")

        if ctx.message.mentions:
            user = ctx.message.mentions[0]
        else:
            return await ctx.error("Please mention a user.")

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
        """ List of muted users. """
        # if not ctx.author.permissions_in(ctx.channel).manage_messages:
        #     return await ctx.error("Insufficient permissions. `Manage Messages` is required.")


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
        """ Unmute a mentioned user. """
        if not ctx.author.permissions_in(ctx.channel).manage_messages:
            return await ctx.error("Insufficient permissions. `Manage Messages` is required.")

        if ctx.message.mentions:
            user = ctx.message.mentions[0]
        else:
            return await ctx.error("Please mention a user.")

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

def setup(bot):
    bot.add_cog(Commands(bot))