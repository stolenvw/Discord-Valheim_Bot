import discord, config
from discord.ext import commands
from discord.errors import Forbidden

"""This custom help command is a perfect replacement for the default one on any Discord Bot written in Discord.py!

Original concept by Jared Newsom (AKA Jared M.F.)
[Deleted] https://gist.github.com/StudioMFTechnologies/ad41bfd32b2379ccffe90b0e34128b8b
Rewritten and optimized by github.com/nonchris
https://gist.github.com/nonchris/1c7060a14a9d94e7929aa2ef14c41bc2
Edited by stolenvw for stolenvw ValheimBot
"""


async def send_embed(ctx, embed):
    """
    Function that handles the sending of embeds
    -> Takes context and embed to send
    - tries to send embed in channel
    - tries to send normal message when that fails
    - tries to send embed private with information abot missing permissions
    If this all fails: https://youtu.be/dQw4w9WgXcQ
    """
    try:
        await ctx.send(embed=embed)
    except Forbidden:
        try:
            await ctx.send("Hey, seems like I can't send embeds. Please check my permissions :)")
        except Forbidden:
            await ctx.author.send(
                f"Hey, seems like I can't send any message in {ctx.channel.name} on {ctx.guild.name}\n"
                f"May you inform the server team about this issue? :slight_smile: ", embed=embed)


class Help(commands.Cog):
    """
    Sends this help message
    """

    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command("help")

    async def chancheck(ctx):
        if ctx.channel.id == config.LOGCHAN_ID or commands.is_owner():
            return True

    @commands.command(hidden=True)
    @commands.check(chancheck)
    # @commands.bot_has_permissions(add_reactions=True,embed_links=True)
    async def help(self, ctx, *input):
        """Shows all modules of the bot"""

	    # !SET THOSE VARIABLES TO MAKE THE COG FUNCTIONAL!
        prefix = config.BOT_PREFIX
        version =  "v0.1.0"

        # checks if cog parameter was given
        # if not: sending all modules and commands not associated with a cog
        async def predicate(cmd):
            try:
                return await cmd.can_run(ctx)
            except commands.CommandError:
                return False
        if not input:
            # starting to build embed
            emb = discord.Embed(title='Valheim Discord Bot', url="https://github.com/stolenvw/Discord-Valheim_Bot", color=discord.Color.blue(),
                                description=f'Use `{prefix}help <module>` to gain more information about that module '
                                            f'\n')

            # iterating trough cogs, gathering descriptions
            cogs_desc = ''
            for cog in self.bot.cogs:
                valid = False
                for command in self.bot.get_cog(cog).get_commands():
                    if not command.hidden:
                        valid = await predicate(command)
                    if valid:
                        break
                if valid:
                    cogs_desc += f'`{cog}` {self.bot.cogs[cog].__doc__}\n'

            # adding 'list' of cogs to embed
            emb.add_field(name='Modules', value=cogs_desc, inline=False)

            # integrating trough uncategorized commands
            commands_desc = ''
            for command in self.bot.walk_commands():
                # if cog not in a cog
                # listing command if cog name is None and command isn't hidden
                if not command.cog_name and not command.hidden:
                    commands_desc += f'{command.name} - {command.help}\n'

            # adding those commands to embed
            if commands_desc:
                emb.add_field(name='Not belonging to a module', value=commands_desc, inline=False)

            emb.set_footer(text=f"Stolenvw ValheimBot {version}")

        # block called when one cog-name is given
        # trying to find matching cog and it's commands
        elif len(input) == 1:

            # iterating trough cogs
            for cog in self.bot.cogs:
                # check if cog is the matching one
                if cog.lower() == input[0].lower():

                    # making title - getting description from doc-string below class
                    emb = discord.Embed(title=f'{cog} - Commands', description=self.bot.cogs[cog].__doc__,
                                            color=discord.Color.green())

                    # getting commands from cog
                    for command in self.bot.get_cog(cog).get_commands():
                        # if cog is not hidden
                        if not command.hidden:
                            valid = await predicate(command)
                            if valid:
                                if not command.usage:
                                    emb.add_field(name=f"`{prefix}{command.name}`", value=command.help, inline=False)
                                else:
                                    emb.add_field(name=f"`{prefix}{command.name} {command.usage}`", value=command.help, inline=False)
                    # found cog - breaking loop
                    break

            # if input not found
            # yes, for-loops have an else statement, it's called when no 'break' was issued
            else:
                emb = discord.Embed(title="What's that?!",
                                    description=f"I've never heard from a module called `{input[0]}` before",
                                    color=discord.Color.orange())

        # too many cogs requested - only one at a time allowed
        elif len(input) > 1:
            emb = discord.Embed(title="That's too much.",
                                description="Please request only one module at once",
                                color=discord.Color.orange())

        else:
            emb = discord.Embed(title="It's a magical place.",
                                description="I don't know how you got here. But I didn't see this coming at all.\n"
                                            "Would you please be so kind to report that issue to me on github?\n"
                                            "https://github.com/nonchris/discord-fury/issues\n"
                                            "Thank you! ~Chris",
                                color=discord.Color.red())

        # sending reply embed using our own function defined above
        await send_embed(ctx, emb)

    @help.error
    async def help_error_handler(self, ctx, error):
        if isinstance(error, commands.MissingAnyRole):
            if config.USEDEBUGCHAN == True:
                bugchan = self.bot.get_channel(config.BUGCHANNEL_ID)
                bugerror = discord.Embed(title=":sos: **ERROR** :sos:", description='**{}** Tried to use command: **{}**\n{}'.format(ctx.author, ctx.command, error), color=0xFF001E)
                await bugchan.send(embed=bugerror)
        if isinstance(error, commands.CheckFailure):
            if config.USEDEBUGCHAN == True:
                bugchan = self.bot.get_channel(config.BUGCHANNEL_ID)
                bugerror = discord.Embed(title=":sos: **ERROR** :sos:", description='**{}** Tried to use command: **{}**\nIn channel **#{}**'.format(ctx.author, ctx.command, ctx.channel), color=0xFF001E)
                await bugchan.send(embed=bugerror)


def setup(bot):
    bot.add_cog(Help(bot))
