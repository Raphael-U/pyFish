from discord import Embed
from discord.ext import commands

class PingCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping', description='Ping the bot to check its latency.')
    async def ping(self, ctx):
        # Reply with a message indicating that the bot is processing the command
        await ctx.respond('Pinging...')

        # Calculate the latency of the bot's API response
        ping = round(self.bot.latency * 1000)

        # Create an embed message to display the latency
        embed = Embed(
            title='Pong!',
            description=f'Latency: {ping}ms',
            color=0x0099ff
        )

        # Edit the original reply with the embed message
        await ctx.edit_origin(embed=embed)

async def setup(bot):
    await bot.add_cog(PingCommand(bot))
