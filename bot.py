import aiohttp
import asyncio
import os
import sys
import json
import time

from discord.ext import commands
from discord import Intents
from discord import CustomActivity
from pathlib import Path
from utils.custom_context import GodseyeContext

class Godseye(commands.Bot):
    def __init__(self, *args, **kwargs):
        self.description = 'To be continued'

        # Configs & token
        with open('config.json') as f:
            self.config = json.load(f)

        intent = Intents.default()
        intent.members = True
        super().__init__(command_prefix=">>", description=self.description,
                         intents=intent,
                         chunk_guilds_at_startup=True,
                         pm_help=None, *args, **kwargs)

        # Startup extensions (none yet)
        self.startup_ext = [x.stem for x in Path('cogs').glob('*.py')]

        # aiohttp session
        self.session = aiohttp.ClientSession(loop=self.loop)

        act = CustomActivity("Powered by Depression™")
        self.activity = act

        # Make room for the help command
        self.remove_command('help')

        # Embed color
        self.user_color = 0x781D1D

        self.quick_access = {}

    def update_quick_access(self, js):
        self.quick_access = js

    async def autorole_check(self):
        while 1:
                print("Iter")
                with open("conf.json") as js:
                    dat = json.load(js)
                for mem in self.dg.members:
                    if mem != self.dg.owner and mem.id != self.user.id:
                        # print(mem.name)
                        if str(mem.id) not in dat['users']:
                            dat['users'][str(mem.id)] = time.time()

                for user in dat['users']:
                    prev_roles = []
                    mem = self.dg.get_member(int(user)) # Get user
                    #print(mem.name)
                    #print(mem.roles)
                    rolectr = 0
                    for rl in mem.roles:
                        if str(rl.id) not in dat['autoroles']:
                            #print("Natural Role, ", rl.name)
                            rolectr +=1

                    if rolectr > 1:
                        continue

                    for role in dat['autoroles']: #Check roles from DB
                        exists = False #Check if user has role
                        s_role = self.dg.get_role(int(role))
                        for urole in mem.roles:
                            if str(urole.id) in dat['autoroles']:
                                if dat['autoroles'][str(urole.id)] > dat['autoroles'][role]:
                                    exists = True
                            if str(urole.id) == role:
                                prev_roles.append(urole)
                                exists = True
                                #print("has ", urole.name)


                        if exists: continue
                        t = time.time()
                        if (t - dat['users'][user]) >= dat['autoroles'][role]:
                            #print("Time for", s_role.name)
                            if prev_roles:
                                for pr in prev_roles:
                                    await mem.remove_roles(pr, reason="Autorole Promotion")
                            await mem.add_roles(s_role, reason="Autorole")
                            break
            # except Exception as exc:
            #     exc_type, exc_obj, exc_tb = sys.exc_info()
            #     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            #     print(exc_type, fname, exc_tb.tb_lineno)

                await asyncio.sleep(60*10)


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
        if message.author.id in self.quick_access['muted']:
            try:
                await message.delete()
            except:
                pass
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
        print(self.guilds)
        for g in self.guilds:
            if g.id == 645708665067798530:
                self.dg = g
        print(f'Client logged in.\n'
              f'{self.user.name}\n'
              f'{self.user.id}\n'
              '--------------------------')
        with open('conf.json') as f:
            dat = json.load(f)
        self.quick_access = dat

        #await self.dg.chunk()
        # for mem in self.dg.members:
        #     print(mem.name)
        for mem in self.dg.members:
            if mem != self.dg.owner and mem.id != self.user.id:
                # print(mem.name)
                if str(mem.id) not in dat['users']:
                    dat['users'][str(mem.id)] = time.time()

        with open("conf.json", 'w') as js:
            json.dump(dat, js)

        gm = CustomActivity("Powered by Depression")
        await self.change_presence(activity=gm)

        self.loop.create_task(self.autorole_check())
