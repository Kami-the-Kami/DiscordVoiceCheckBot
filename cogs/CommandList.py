import discord
from discord.ext import commands

class CommandList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def getVCMembers(self, ctx):
        author : discord.abc.User = ctx.author #Static typed for ease of use in IDE
        channel : discord.guild.VoiceChannel = None

        #get voice channel the command author is in
        for c in ctx.guild.voice_channels:
            for m in c.members:
                if m.id == author.id:
                    channel = c

        #if the caller isnt in VC, or the bot cant see the VC
        if channel is None:
            #TODO: throw an exception or something.
            await ctx.send("Join the voice channel you want to check")
            return

        #get all members in caller's VC
        for m in channel.members:
            nickname = m.display_name
            await ctx.send("Members in vc: " + nickname)









def setup(bot):
    bot.add_cog(CommandList(bot))
