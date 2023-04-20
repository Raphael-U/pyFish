import os
import importlib
import asyncio
from client import client, db
from discord.ext import commands

client.fish = {
    "Common": {},
    "Uncommon": {},
    "Rare": {},
}

# Read all data from the fish table
rows = db.execute("SELECT * FROM fish").fetchall()

for row in rows:
    id, species, rarity, length_min, length_max, fulton_condition_factor = row
    fish_data = {
        "id": id,
        "species": species,
        "rarity": rarity,
        "length_min": length_min,
        "length_max": length_max,
        "fulton_condition_factor": fulton_condition_factor,
    }
    client.fish[rarity][id] = fish_data

client.cooldowns = commands.CooldownMapping.from_cooldown(1, 1, commands.BucketType.default)

command_files = [f for f in os.listdir("./commands") if f.endswith(".py")]


async def load_cogs_and_commands(client):
    for file in command_files:
        module_name = file[:-3]
        module = importlib.import_module(f"pyfish.commands.{module_name}")
        if hasattr(module, "setup"):  # Check if the module has a setup function (i.e., it's a cog)
            await module.setup(client)
        elif hasattr(module, "Command"):  # Check if the module has a Command class
            command = module.Command()
            client.add_command(command)  # Use add_command instead of modifying client.commands


asyncio.run(load_cogs_and_commands(client))

token_file = "../config.json"

with open(token_file) as f:
    import json

    config = json.load(f)

token = config["token"]
client.run(token)
