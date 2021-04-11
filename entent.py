import os
import discord
from discord.ext import commands, tasks


intents = discord.Intents(messages=True, voice_states=True, guilds=True)

bot: commands.Bot = commands.Bot(command_prefix=commands.when_mentioned,
                                 description='Relatively simple music bot example', intents=intents)


@bot.event
async def on_ready():
    """A dummy docstring."""
    print('Logged on as {0}!'.format(bot.user))


def is_stagechannel(channel: discord.StageChannel) -> bool:
    """A dummy docstring."""
    return isinstance(channel, discord.StageChannel)


def is_stage_moderator(channel: discord.StageChannel, member: discord.Member) -> bool:
    """A dummy docstring."""
    perm: discord.Permissions = member.permissions_in(channel)
    return perm.is_superset(perm.stage_moderator())


class VoiceCount():
    """A dummy docstring."""

    def __init__(self,
                 member: discord.Member,
                 channel: discord.StageChannel,
                 textchan: discord.TextChannel,
                 time: int) -> None:
        self.member = member
        self.channel = channel
        self.textchan = textchan
        self.message: discord.Message
        self.index = 0
        self.count = time//10
        self.voice_count.start()

    @tasks.loop(seconds=10.0)
    async def voice_count(self):
        """A dummy docstring."""
        if self.index >= self.count:
            self.voice_count.stop()
            return
        self.index += 1

        try:
            await self.message.edit(content="{} has been talking for {}s".format(self.member.display_name,
                                                                                 self.voice_count.current_loop*10))
        except:
            self.message = await self.textchan.send("{} is talking".format(self.member.display_name))

    @voice_count.after_loop
    async def after_slow_count(self):
        """A dummy docstring."""
        await self.member.edit(suppress=True)
        await self.message.delete()
        print('done!')


class Stage():
    """A dummy docstring."""
    instances = dict()

    def __init__(self, channel: discord.StageChannel, time: int) -> None:
        self.channel = channel
        self.time = time
        guild: discord.Guild = channel.guild
        self.textchan = next((
            chan for chan in guild.text_channels if chan.name == channel.name), discord.TextChannel)

        self.textchanmoderators = next((
            chan for chan in guild.text_channels if chan.name == channel.name+'-moderators'), discord.TextChannel)

        Stage.instances[channel.id] = self

    @classmethod
    def get_instances(cls):
        """A dummy docstring."""
        return list(Stage.instances)

    @classmethod
    def get_instance_by_channel(cls, channel_id: int):
        """A dummy docstring."""
        return Stage.instances[channel_id]

    def count(self, member: discord.Member):
        """A dummy docstring."""
        if is_stage_moderator(self.channel, member):
            print("is moderator")
            # return

        VoiceCount(member, self.channel, self.textchan, self.time)


@bot.listen('on_voice_state_update')
async def count(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    """A dummy docstring."""
    stage_channel: discord.StageChannel = after.channel
    print(stage_channel)
    if not is_stagechannel(stage_channel):
        print('not a stage channel')
        return

    if before.suppress and not after.suppress:
        try:
            Stage.get_instance_by_channel(stage_channel.id).count(member)
        except:
            print('channel not managed')


@bot.command()
@commands.guild_only()
# @commands.bot_has_permissions(manage_message=True)
async def test(ctx: commands.Context, time: int):
    """A dummy docstring."""
    stage_channel = next((
        chan for chan in ctx.guild.stage_channels if chan.name == ctx.channel.name), discord.StageChannel)
    if not is_stagechannel(stage_channel):
        print('not a stage channel')
        return
    if is_stage_moderator(stage_channel, ctx.guild.me):
        Stage(stage_channel, time)
    else:
        await ctx.send("I'm not a stage moderator")


bot.run(os.getenv('BOT_TOKEN'))
