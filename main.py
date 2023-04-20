import asyncio
import json
from datetime import datetime
from math import floor
from random import random, choice
from interactions import Client, Intents, listen, slash_command, InteractionContext, Embed, ActionRow, SlashContext, \
    Modal, ShortText, ParagraphText, ModalContext, ComponentContext, ButtonStyle, component_callback, MessageFlags, \
    OptionType
from setup_db import setup_db
import sqlite3

# Time to catch a fish
FISHING_COOLDOWN = 60
FISHING_CATCH_CHANCE = .75
PAGE_SIZE = 5

# Probability of catching a rare fish
rare_fish_probability = 0.1
uncommon_fish_probability = 0.2
common_fish_probability = 0.7

# Rarity Colors
colors = {
    'Common': '#AAAAAA',
    'Uncommon': '#55AA55',
    'Rare': '#5555AA',
}

# Create static rows of fish
setup_db()

fishCollection = {"Rare": {}, "Uncommon": {}, "Common": {}}

conn = sqlite3.connect('pyfish.sqlite')
c = conn.cursor()

c.execute("SELECT * FROM fish")
rows = c.fetchall()

for row in rows:
    id, species, rarity, length_min, length_max, fulton_condition_factor = row
    fish_data = {"id": id, "species": species, "rarity": rarity, "length_min": length_min, "length_max": length_max,
                 "fulton_condition_factor": fulton_condition_factor}
    fishCollection[rarity][id] = fish_data

conn.close()

# Read the configuration file and store the values
with open("./config.json") as f:
    config = json.load(f)
    token = config["token"]
    guild_id = int(config["guildId"])

# intents are what events we want to receive from discord, `DEFAULT` is usually fine
bot = Client(intents=Intents.DEFAULT, sync_interactions=True)


@listen()  # this decorator tells snek that it needs to listen for the corresponding event, and run this coroutine
async def on_ready():
    # This event is called when the bot is ready to respond to commands
    print("Ready")
    print(f"This bot is owned by {bot.owner}")


@slash_command(name="ping", description="Get fish bot latency", scopes=[guild_id])
async def ping(ctx: InteractionContext):
    # Reply with a message indicating that the bot is processing the command

    desc = ''
    try:
        # Calculate the latency of the bot's API response
        ping_ms = round(bot.latency * 1000)
        desc = f'Latency: {ping_ms}ms. Start Time: {bot.start_time}'
    except OverflowError:
        desc = 'Wait a second'

    msg = await ctx.respond('Pinging...')
    # Create an embed message to display the latency
    embed = Embed(
        title='Pong!',
        description=desc,
        color=0x0099ff
    )

    # Edit the original reply with the embed message
    await ctx.edit(message=msg, embed=embed)


@slash_command(name="fish", description="Cast a line and catch a fish!", scopes=[guild_id])
async def fish(ctx: InteractionContext):
    await ctx.defer()

    # Reply with a message indicating that the bot is processing the command
    # message = await ctx.send("You cast your line and wait for a fish to bite...")
    message = None

    # Set a timer for the fishing attempt
    time_to_catch = floor(FISHING_COOLDOWN * random())

    print(time_to_catch)

    # Wait for the timer to complete
    await asyncio.sleep(time_to_catch)

    # Randomly determine if a fish is caught
    is_fish_caught = random() < FISHING_CATCH_CHANCE

    # ... (The rest of the code for determining the fish species, rarity, and other properties)
    caught_float = random()

    caught_fish = None

    # Determine the fish species based on rarity
    if caught_float < rare_fish_probability:
        caught_fish = fishCollection['Rare'][choice(list(fishCollection['Rare'].keys()))]
    elif caught_float < (rare_fish_probability + uncommon_fish_probability):
        caught_fish = fishCollection['Uncommon'][choice(list(fishCollection['Uncommon'].keys()))]
    else:
        caught_fish = fishCollection['Common'][choice(list(fishCollection['Common'].keys()))]

    catch_time_secs = time_to_catch % 60

    # Gives you a random number between min and max, with outputs closer to min being more common
    length_CM = floor(
        abs(
            random() - random())
        * (caught_fish['length_max'] - caught_fish['length_min'] + 1)
        + caught_fish['length_min'])

    print(length_CM)

    length_IN = floor((length_CM / 2.54 * 2)) / 2
    max_length_IN = floor((caught_fish['length_max'] / 2.54 * 2)) / 2
    min_length_IN = floor((caught_fish['length_min'] / 2.54 * 2)) / 2
    weight_LBS = round((caught_fish['fulton_condition_factor'] * length_CM ** 3 * 0.0000325 * 2.20462) * 2) / 2

    # Create an embed message to display the result of the fishing attempt
    embed = Embed(
        title='You caught a fish!' if is_fish_caught else 'Fish got away!',
        description=(
            # The same message format as the original code, adapted to Python
            f"Congratulations <@!{ctx.author.id}>! You caught a `{caught_fish['species']}`!\n\n"
            f"Rarity: `{caught_fish['rarity']}`\n"
            f"Length: `{length_IN}` inches (Min:`{min_length_IN}` Max:`{max_length_IN}`)\n"
            f"Weight: `{weight_LBS}` lb(s)\n"
            f"Time to catch: {catch_time_secs} seconds"
        ) if is_fish_caught else 'Better luck next time!',
        color=colors[caught_fish['rarity']] if is_fish_caught else 0xff0000,
    )

    # await message.edit(content=None, embed=embed)
    await ctx.send(content=None, embed=embed)


@slash_command(name="balance", description="Check your bank balance", scopes=[guild_id])
async def balance(ctx: InteractionContext):
    # connect to SQLite database
    conn = sqlite3.connect('pyfish.sqlite')
    cursor = conn.cursor()

    # get user ID and guild ID
    user_id = str(ctx.author.id)
    guild_id = str(ctx.guild.id)

    # check if user account exists in database
    cursor.execute("SELECT balance FROM bank_account WHERE user_id=? AND guild_id=?", (user_id, guild_id))
    result = cursor.fetchone()

    if result:
        balance = result[0]
        await ctx.send(f"Your bank balance is {balance} credits.")
    else:
        # create a new row for the user with a default balance
        cursor.execute("INSERT INTO bank_account (user_id, guild_id, balance, created_at) VALUES (?, ?, ?, ?)",
                       (user_id, guild_id, 120, datetime.now()))
        conn.commit()
        await ctx.send("Your new balance is 120 credits.")

    # close database connection
    conn.close()


@slash_command(name="inventory", description="Check your inventory", scopes=[guild_id])
async def inventory(ctx: InteractionContext):
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
    embed = Embed(color=0x0099ff, title=f"{user.username}'s Fish Inventory")

    for field in fields:
        embed.add_field(name=field['name'], value=field['value'], inline=False)

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
            interaction = await bot.wait_for('button_click', check=check, timeout=60)

            # Update the current page and items based on which button was pressed
            if interaction.custom_id == 'back':
                current_page -= 1
            elif interaction.custom_id == 'forward':
                current_page += 1

            # Update the embed with the new page of items and button disabled states
            current_items = pages[current_page]

            fields = []
            for fish_name in current_items:
                fish_obj = fish_by_species[fish_name]
                fields.append({
                    'name': f"{fish_name} {fish_obj['rarity'][0]} ({fish_obj['quantity']})",
                    'value': "\n".join(
                        [f"{index + 1}. W {item['weight']} lbs. L: {item['length']} in." for index, item in
                         enumerate(fish_obj['list'])]),
                    'inline': True
                })

            new_embed = Embed(color=0x0099ff, title=f"{user.username}'s Fish Inventory")
            # loop through the list of fields and add each one to the embed
            for field in fields:
                new_embed.add_field(name=field['name'], value=field['value'], inline=False)

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


# async def fish_error(self, ctx, error):
#     if isinstance(error, commands.CommandOnCooldown):
#         remaining = error.retry_after
#         # Create an embed message to display the cooldown
#         embed = Embed(
#             title="Upgrade to __***GORP Fishing Premium***__ for more lines",
#             description=(
#                 f"1 out of 1 line(s) out. Wait for the previous cast to finish before casting another line."
#                 f" Fishing requires patience. They will bite eventually!\n\n"
#                 f"You've had your line out for {remaining // 60:.0f} minutes, and {remaining % 60:.0f} seconds."
#             ),
#             color=0xff0000,
#         )
#         await ctx.send(embed=embed)
#     else:
#         print(f"Unhandled error: {error}")
#         raise error

@slash_command(name="feature_request", description="Send a feature request to pyFish Bot Makers", scopes=[guild_id])
async def request_feature(ctx: SlashContext):
    # Connect to the database and insert the new feature request row
    conn = sqlite3.connect('pyfish.sqlite')
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM feature_request;')
    result = cursor.fetchone()[0]

    my_modal = Modal(
        ShortText(
            label="Feature Title",
            custom_id="feature_title",
            placeholder="name of your brilliant new pyFish feature",
            min_length=10
        ),
        ParagraphText(
            label="Feature Description",
            custom_id="feature_description",
            placeholder="Describe your idea with as much detail as you can.",
            max_length=500,
        ),
        title=f"Feature Request #{result + 1}",
    )
    await ctx.send_modal(modal=my_modal)

    # Wait for the user to submit the form or close the modal
    modal_ctx: ModalContext = await ctx.bot.wait_for_modal(my_modal)

    # Get the form values
    title = modal_ctx.responses["feature_title"]
    description = modal_ctx.responses["feature_description"]
    user_id = ctx.author.id
    user_handle = f"{ctx.author.global_name}#{ctx.author.discriminator}"
    nickname = f"{ctx.author.nickname}"

    cursor.execute('''INSERT INTO feature_request (created_at, title, description, user_handle, user_id)
                      VALUES (?,?,?,?,?)''', (datetime.now(), title, description, user_handle, user_id))
    conn.commit()
    conn.close()

    # Send a confirmation message to the user
    await modal_ctx.send(f"Feature Request #{result + 1} submitted successfully."
                         f"Thanks {nickname}, for submitting your feature request for '{title}'! "
                         f"We'll consider it for a future release.")


async def get_feature_requests_page(cursor, page_number: int):
    start_index = (page_number - 1) * 5
    cursor.execute('SELECT * FROM feature_request LIMIT 5 OFFSET ?;', (start_index,))
    return cursor.fetchall()


@slash_command(name="list_feature_requests", description="Display a paginated list of feature requests",
                      options=[
                          {
                              "name": "page",
                              "description": "The page number to display",
                              "type": OptionType.INTEGER,
                              "required": False,
                          }
                      ], scopes=[guild_id])
async def list_feature_requests(ctx: SlashContext, page: int = 1):
    conn = sqlite3.connect("pyfish.sqlite")
    cursor = conn.cursor()

    feature_requests = await get_feature_requests_page(cursor, page)

    if not feature_requests:
        await ctx.send("No feature requests found.", flags=MessageFlags.EPHEMERAL)
        return

    embed = Embed(title="Feature Requests", description="Listing feature requests:")
    for request in feature_requests:
        embed.add_field(name=f"Request #{request[0]} - {request[2]}", value=request[3], inline=False)
    #
    # action_row = {
    #     "type": 1,
    #     "components": [
    #         {
    #             "type": 2,
    #             "style": ButtonStyle.SECONDARY,
    #             "label": "Previous",
    #             "custom_id": f"fr_previous_{page}",
    #             "disabled": page == 1
    #         },
    #         {
    #             "type": 2,
    #             "style": ButtonStyle.SECONDARY,
    #             "label": "Next",
    #             "custom_id": f"fr_next_{page}"
    #         }
    #     ]
    # }

    # await ctx.send(embed=embed, components=[action_row])
    await ctx.send(embed=embed)


# @component_callback(custom_id=["fr_",])
# async def on_list_feature_requests_buttons(ctx: ComponentContext):
#     button_pressed = ctx.custom_id[:10]
#     page = int(ctx.custom_id[11:])
#
#     if button_pressed == "fr_previous":
#         page = max(1, page - 1)
#     elif button_pressed == "fr_next":
#         page += 1
#
#     conn = sqlite3.connect("pyfish.sqlite")
#     cursor = conn.cursor()
#
#     feature_requests = await get_feature_requests_page(cursor, page)
#
#     if not feature_requests:
#         await ctx.send("No more feature requests found.", flags=MessageFlags.EPHEMERAL)
#         return
#
#     embed = Embed(title="Feature Requests", description="Listing feature requests:")
#     for request in feature_requests:
#         embed.add_field(name=f"Request #{request[0]} - {request[2]}", value=request[3], inline=False)
#
#     action_row = {
#         "type": 1,
#         "components": [
#             {
#                 "type": 2,
#                 "style": ButtonStyle.SECONDARY,
#                 "label": "Previous",
#                 "custom_id": f"fr_previous_{page}",
#                 "disabled": page == 1
#             },
#             {
#                 "type": 2,
#                 "style": ButtonStyle.SECONDARY,
#                 "label": "Next",
#                 "custom_id": f"fr_next_{page}"
#             }
#         ]
#     }
#
#     await ctx.edit_origin(embed=embed, components=[action_row])


bot.start(token)
