import discord
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cmd = bot.get_command
        self.color = bot.user_color

    @commands.group(invoke_without_command=True)
    async def help(self, ctx, *, command_name: str=None):
        """ Shows the possible help categories """
        bot_prefix = '>>'
        # Shortcut to command search
        if command_name is not None:
            return await ctx.invoke(self.cmd('help command'), cmd_name=command_name)

        em = discord.Embed(title='Help', color=self.color)

        ut = [c for c in self.bot.commands]
        ut.sort(key=lambda x: x.name)
        tx = "`O` **autorole** [role] [time]\n" \
             "`O` **icon** [url]\n" \
             "`M` **mute** [user]\n"\
             "`M` **mutelist**\n"\
             "`M` **purge** [user] [number]\n"\
             "`M` **unmute** [user]\n"\
             "`O` **wipe** [user]\n"\

        # This can't go in the init because help isn't loaded last & thus misses some commands
        em.add_field(name="Commands", value=tx)
        em.add_field(name="Key", value="`O` - Owner\n`M` - Manage Messages", inline=False)
        try:
            await ctx.send(embed=em)
        except:
            await ctx.send("`Embed Links` permission is required to see the help!")

    @help.command(name='command', aliases=['cmd', 'commands'])
    async def help_command(self, ctx, *, cmd_name: str=None):
        """ Sends help for a specific command """
        bot_prefix = '>>'
        # Get command object
        cmd_obj = self.cmd(cmd_name)

        # Handle no command found
        if cmd_obj is None:
            return await ctx.error(f'Command {cmd_name} not found')
        em = discord.Embed(title=cmd_obj.name, description=cmd_obj.help, color=self.color)

        # Input aliases and parameters to embed
        if cmd_obj.aliases:
            em.add_field(name='Aliases', value='\n'.join([f'\u2022 {x}' for x in cmd_obj.aliases]))
        if cmd_obj.clean_params:
            em.add_field(name='Parameters', value='\n'.join([f'\u2022 {x}' for x in cmd_obj.clean_params]))

        # Handle group commands
        if isinstance(cmd_obj, commands.core.Group):
            em.add_field(name='Group commands',
                         value='\n'.join([f'\u2022 {x}' for x in cmd_obj.commands]),
                         inline=False)

        # Add usage last
        em.add_field(name='Usage',
                     value=f'```{bot_prefix}\u200b{cmd_name} '
                           f'{" ".join([f"<{x}>" for x in cmd_obj.clean_params])}```',
                     inline=False)

        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Help(bot))
    