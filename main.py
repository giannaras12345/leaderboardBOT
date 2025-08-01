import threading
from flask import Flask
import discord
import os
from config import DISCORD_TOKEN
from scraper import RTanksScraper

app = Flask(__name__)

@app.route('/')
def home():
    return "RTanks Discord bot is alive!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Bot connected as {client.user}")

def run_discord():
    client.run(DISCORD_TOKEN)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    run_discord()
