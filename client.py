import sqlite3
import sys
from discord import Intents
from discord.ext import commands

db = sqlite3.connect("pyfish.sqlite")

with db:
    db.execute("""
        CREATE TABLE IF NOT EXISTS fish (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              species TEXT NOT NULL,
              rarity TEXT NOT NULL,
              length_min REAL NOT NULL,
              length_max REAL NOT NULL,
              fulton_condition_factor REAL NOT NULL
        );
    """)

    db.executemany("""
        INSERT OR IGNORE INTO fish (id, species, rarity, length_min, length_max, fulton_condition_factor)
        VALUES (?, ?, ?, ?, ?, ?)
    """, [
        (1, 'Rainbow Trout', 'Common', 20, 35, 1.0),
        (2, 'Brown Trout', 'Common', 25, 45, 1.1),
        (3, 'Brook Trout', 'Uncommon', 20, 30, 1.2),
        (4, 'Largemouth Bass', 'Common', 30, 60, 0.8),
        (5, 'Smallmouth Bass', 'Common', 25, 45, 0.9),
        (6, 'Bluegill', 'Common', 10, 20, 0.7),
        (7, 'Crappie', 'Common', 20, 30, 0.9),
        (8, 'Northern Pike', 'Uncommon', 50, 100, 0.7),
        (9, 'Musky', 'Rare', 80, 120, 0.6),
        (10, 'Walleye', 'Common', 30, 70, 0.8),
        (11, 'Perch', 'Common', 15, 25, 0.7),
        (12, 'Carp', 'Common', 30, 80, 0.5),
        (13, 'Catfish', 'Common', 30, 80, 0.6),
        (14, 'Salmon', 'Rare', 40, 80, 0.9),
        (15, 'Tuna', 'Rare', 100, 200, 0.7),
        (16, 'Marlin', 'Rare', 150, 300, 0.6),
        (17, 'Swordfish', 'Rare', 150, 250, 0.8),
        (18, 'Snapper', 'Uncommon', 20, 40, 1.1),
        (19, 'Grouper', 'Rare', 30, 60, 0.9),
    ])

    db.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          fish INTEGER,
          quantity INTEGER,
          user_id TEXT,
          weight REAL,
          length REAL,
          FOREIGN KEY (fish) REFERENCES fish(id)
        )
    """)

intents = Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

client = commands.Bot(command_prefix="!", intents=intents)

# Export the client, db, and DEBUG flag for use in other modules
__all__ = ["client", "db"]
