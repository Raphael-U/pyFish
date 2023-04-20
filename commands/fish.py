import asyncio
import math
import random
from discord.ext import commands
from discord import Embed

FISHING_COOLDOWN = 60  # seconds


class Fish(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}

    @commands.command(name="fish", description="Go fishing and catch a fish!")
    @commands.cooldown(1, FISHING_COOLDOWN, commands.BucketType.user)
    async def fish(self, ctx):
        # Reply with a message indicating that the bot is processing the command
        message = await ctx.send("You cast your line and wait for a fish to bite...")

        # Set a timer for the fishing attempt
        time_to_catch = math.floor(FISHING_COOLDOWN * random.random())

        # Wait for the timer to complete
        await asyncio.sleep(time_to_catch)

        # Randomly determine if a fish is caught
        is_fish_caught = random.random() < 0.75

        # ... (The rest of the code for determining the fish species, rarity, and other properties)
        # ... (You need to adapt your fish data structure, this part of the code has been omitted)

        # Create an embed message to display the result of the fishing attempt
        embed = Embed(
            title='You caught a fish!' if is_fish_caught else 'Fish got away!',
            description=(
                # The same message format as the original code, adapted to Python
                f"Congratulations <@{ctx.author.id}>! You caught a `{fish.species}`!\n\n"
                f"Rarity: `{fish.rarity}`\n"
                f"Length: `{length_in}` inches (Min:`{min_length_in}` Max:`{max_length_in}`)\n"
                f"Weight: `{weight_lbs}` lb(s)\n"
                f"Time to catch: {catch_time_mins} minutes, and {catch_time_secs} seconds"
            ) if is_fish_caught else 'Better luck next time!',
            color=colors[fish.rarity] if is_fish_caught else 0xff0000,
        )

        # Edit the original message with the embed message
        await message.edit(content=None, embed=embed)

    @fish.error
    async def fish_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            remaining = error.retry_after
            # Create an embed message to display the cooldown
            embed = Embed(
                title="Upgrade to __***GORP Fishing Premium***__ for more lines",
                description=(
                    f"1 out of 1 line(s) out. Wait for the previous cast to finish before casting another line."
                    f" Fishing requires patience. They will bite eventually!\n\n"
                    f"You've had your line out for {remaining // 60:.0f} minutes, and {remaining % 60:.0f} seconds."
                ),
                color=0xff0000,
            )
            await ctx.send(embed=embed)
        else:
            print(f"Unhandled error: {error}")
            raise error


async def setup(bot):
    await bot.add_cog(Fish(bot))
