import aiohttp
import asyncio
import os
import sys
import json
import time

from discord.ext import commands
from pathlib import Path
from utils.custom_context import GodseyeContext

class Godseye(commands.Bot):
    def __init__(self, *args, **kwargs):
        self.description = 'To be continued'

        # Configs & token
        with open('config.json') as f:
            self.config = json.load(f)


        super().__init__(command_prefix=">>", description=self.description,
                         pm_help=None, *args, **kwargs)

        # Startup extensions (none yet)
        self.startup_ext = [x.stem for x in Path('cogs').glob('*.py')]

        # aiohttp session
        self.session = aiohttp.ClientSession(loop=self.loop)

        # Make room for the help command
        self.remove_command('help')

        # Embed color
        self.user_color = 0x781D1D

    async def autorole_check(self):
        while 1:
            with open("conf.json") as js:
                dat = json.load(js)
            for user in dat['users']:
                mem = self.dg.get_member(user) # Get user
                for role in dat['autoroles']: #Check roles from DB
                    exists = False #Check if user has role
                    for urole in mem.roles:
                        if urole.name == role:
                            exists = True
                    if exists: continue
                    t = time.time()
                    if (t - dat['users'][user]) >= dat['autoroles'][role]:
                        for s_role in self.dg.roles:
                            if s_role.name == role:
                                await mem.add_roles([s_role, ], reason="Autorole")
                                break

            await asyncio.sleep(10*60)


    def run(self):
        try:
            super().run(self.config['token'])
        finally:
            self.loop.close()

    async def report(self, msg):
        await self.owner.send(f"Error, context: `{msg}`")

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return
        await self.wait_until_ready()
        ctx = await self.get_context(message, cls=GodseyeContext)
        await self.invoke(ctx)

    async def on_member_join(self, mem):
        with open("conf.json") as js:
            dat = json.load(js)
        if mem.id not in dat['users']:
            dat['users'][mem.id] = time.time()
        with open("conf.json", 'w') as js:
            json.dump(dat, js)

    async def on_member_remove(self, mem):
        with open("conf.json") as js:
            dat = json.load(js)
        if mem.id in dat['users']:
            del dat['users'][mem.id]
        with open("conf.json", 'w') as js:
            json.dump(dat, js)

    async def on_ready(self):
        for ext in self.startup_ext:
            try:
                self.load_extension(f'cogs.{ext}')
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(f'Failed to load extension: {ext}\n{e}')
                print(exc_type, fname, exc_tb.tb_lineno)
            else:
                print(f'Loaded extension: {ext}')

        self.ses = aiohttp.ClientSession()
        c = await self.application_info()
        self.owner = c.owner
        for g in self.guilds:
            if g.name.startswith("Depress"):
                self.dg = g
        print(f'Client logged in.\n'
              f'{self.user.name}\n'
              f'{self.user.id}\n'
              '--------------------------')
        self.loop.create_task(autorole_check)
