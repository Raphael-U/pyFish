import asyncio

from discord.ext import commands
from discord import Embed, Button, ActionRow
import sqlite3

db = sqlite3.connect('pyfish.sqlite')
PAGE_SIZE = 5


class Inventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def inventory(self, ctx):
        user = ctx.author

        # Get the user's inventory from the database
        cursor = db.cursor()
        cursor.execute(
            "SELECT inventory.*, fish.species, fish.rarity FROM inventory JOIN fish ON inventory.fish = fish.id WHERE user_id = ? ORDER BY id DESC LIMIT 10",
            (user.id,))
        inventory = cursor.fetchall()

        # If the user has no inventory, send an error message
        if not inventory:
            embed = Embed(color=0xFF0000, description=f"{user.username}, you don't have any fish in your inventory!")
            await ctx.send(embed=embed)
            return

        fish_by_species = {}
        for item in inventory:
            if item['species'] in fish_by_species:
                fish_by_species[item['species']]['quantity'] += item['quantity']
                fish_by_species[item['species']]['list'].append(item)
            else:
                fish_by_species[item['species']] = {
                    'quantity': item['quantity'],
                    'rarity': item['rarity'],
                    'list': [item]
                }

        sorted_fish = sorted(fish_by_species.keys(),
                             key=lambda x: ('Common', 'Uncommon', 'Rare').index(fish_by_species[x]['rarity']))

        # Paginate the inventory by creating an array of pages, where each page contains up to 5 items
        pages = [sorted_fish[i:i + PAGE_SIZE] for i in range(0, len(sorted_fish), PAGE_SIZE)]

        # Create an initial page with the first 5 items
        current_page = 0
        current_items = pages[current_page]

        fields = []
        for fish_name in current_items:
            fish_data = fish_by_species[fish_name]
            fields.append({
                'name': f"{fish_name} {fish_data['rarity'][0]} ({fish_data['quantity']})",
                'value': "\n".join([f"{index + 1}. W {item['weight']} lbs. L: {item['length']} in." for index, item in
                                    enumerate(fish_data['list'])]),
                'inline': True
            })

        # Create an embed message to display the user's inventory
        embed = Embed(color=0x0099ff, title=f"{user.username}'s Fish Inventory").add_field(fields=fields)
        embed.set_footer(text=f"Page {current_page + 1}/{len(pages)}",
                         icon_url="https://static.vecteezy.com/system/resources/previews/021/524/883/large_2x/fish-icon-style-vector.jpg")

        # Create back and forward buttons
        back_button = Button(custom_id='back', label='Back', style=2, disabled=(current_page == 0))
        forward_button = Button(custom_id='forward', label='Forward', style=2, disabled=(len(pages) <= 1))

        # Create a row with the buttons
        button_row = ActionRow(back_button, forward_button)

        # Send the initial message with the inventory and buttons
        message = await ctx.send(embed=embed, components=[button_row])

        def check(inter):
            return inter.custom_id in ['back', 'forward'] and inter.message.id == message.id

        while True:
            try:
                # Set up a listener to wait for button interactions
                interaction = await self.bot.wait_for('button_click', check=check, timeout=60)

                # Update the current page and items based on which button was pressed
                if interaction.custom_id == 'back':
                    current_page -= 1
                elif interaction.custom_id == 'forward':
                    current_page += 1

                # Update the embed with the new page of items and button disabled states
                current_items = pages[current_page]

                fields = []
                for fish_name in current_items:
                    fish_data = fish_by_species[fish_name]
                    fields.append({
                        'name': f"{fish_name} {fish_data['rarity'][0]} ({fish_data['quantity']})",
                        'value': "\n".join(
                            [f"{index + 1}. W {item['weight']} lbs. L: {item['length']} in." for index, item in
                             enumerate(fish_data['list'])]),
                        'inline': True
                    })

                new_embed = Embed(color=0x0099ff, title=f"{user.username}'s Fish Inventory")
                new_embed.add_field(fields=fields)
                new_embed.set_footer(text=f"Page {current_page + 1}/{len(pages)}",
                                     icon_url="https://static.vecteezy.com/system/resources/previews/021/524/883/large_2x/fish-icon-style-vector.jpg")

                # Disable or enable the appropriate buttons based on the current page
                back_button.disabled = (current_page == 0)
                forward_button.disabled = (current_page == len(pages) - 1)

                # Update the original message with the new embed and button states
                await interaction.message.edit(embed=new_embed, components=[ActionRow(back_button, forward_button)])

                # Acknowledge the interaction
                await interaction.response.defer()

            except asyncio.TimeoutError:
                # If no button is pressed within the timeout, disable the buttons and exit the loop
                back_button.disabled = True
                forward_button.disabled = True
                await message.edit(components=[ActionRow(back_button, forward_button)])
                break


async def setup(bot):
    await bot.add_cog(Inventory(bot))
