import threading
from flask import Flask
import discord
import os
from config import DISCORD_TOKEN, CHANNEL_ID, EMBED_COLOR, PLAYERS_PER_PAGE, TOTAL_PAGES, LEADERBOARD_CATEGORIES, EMBED_TIMEOUT
from scraper import RTanksScraper
from discord.ext import tasks

app = Flask(__name__)

@app.route('/')
def home():
    return "RTanks Discord bot is alive!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
scraper = RTanksScraper()  # ✅ added

# ✅ Paginator View for Buttons
class LeaderboardView(discord.ui.View):
    def __init__(self, category: str, data, timeout=EMBED_TIMEOUT):
        super().__init__(timeout=timeout)
        self.category = category
        self.data = data
        self.current_page = 0
        self.total_pages = TOTAL_PAGES

        self.prev_button = discord.ui.Button(label="⬅️ Prev", style=discord.ButtonStyle.secondary)
        self.next_button = discord.ui.Button(label="Next ➡️", style=discord.ButtonStyle.secondary)

        self.prev_button.callback = self.prev_page
        self.next_button.callback = self.next_page

        self.add_item(self.prev_button)
        self.add_item(self.next_button)

    async def update_message(self, interaction: discord.Interaction):
        embed = self.get_embed(self.current_page)
        await interaction.response.edit_message(embed=embed, view=self)

    async def prev_page(self, interaction: discord.Interaction):
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_message(interaction)

    async def next_page(self, interaction: discord.Interaction):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            await self.update_message(interaction)

    def get_embed(self, page: int):
        start = page * PLAYERS_PER_PAGE
        end = start + PLAYERS_PER_PAGE
        players = self.data[start:end]

        category_config = LEADERBOARD_CATEGORIES[self.category]
        embed = discord.Embed(
            title=category_config["name"],
            description=category_config["description"],
            color=EMBED_COLOR
        )

        for player in players:
            embed.add_field(
                name=f"#{player['rank']} - {player['name']}",
                value=f"Score: {player['score_formatted']}",
                inline=False
            )

        embed.set_footer(text=f"Page {self.current_page + 1}/{self.total_pages}")
        return embed


@client.event
async def on_ready():
    print(f"Bot connected as {client.user}")
    send_force_trigger.start()  # ✅ start the new loop

# ✅ New hourly task that just sends "!forceleaderboard"
@tasks.loop(hours=1)
async def send_force_trigger():
    print("Triggering hourly !forceleaderboard...")
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("!forceleaderboard")
    else:
        print(f"Channel {CHANNEL_ID} not found.")

@client.event
async def on_message(message):
    if message.content.strip().lower() == "!forceleaderboard":
        channel = message.channel
        all_data = scraper.scrape_all_categories()

        for category, players in all_data.items():
            view = LeaderboardView(category, players)
            embed = view.get_embed(0)
            await channel.send(embed=embed, view=view)

def run_discord():
    client.run(DISCORD_TOKEN)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    run_discord()
