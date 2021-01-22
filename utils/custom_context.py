import discord
from discord.ext import commands


class GodseyeContext(commands.Context):
    async def error(self, err: str, delete_after=None):
        em = discord.Embed(title=':x: Error',
                           color=discord.Color.dark_red(),
                           description=err.format())

        m = await self.send(embed=em, delete_after=delete_after)
        return m

    async def embed_reply(self, msg: str, delete_after=None):
        em = discord.Embed(title='Command Completed',
                           color=discord.Color.green(),
                           description=msg.format())

        m = await self.send(embed=em, delete_after=delete_after)
        return m