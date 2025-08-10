import os
import discord
from discord import app_commands
import asyncio
import json
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS 
import threading
from discord.utils import get

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
BINDINGS_FILE = "bindings.json"

def load_bindings():
    try:
        with open(BINDINGS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_bindings(bindings):
    with open(BINDINGS_FILE, "w") as f:
        json.dump(bindings, f)

intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.message_content = True

class JarvisClient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

    async def send_to_bound_channel(self, guild_id, message):
        bindings = load_bindings()
        guild = self.get_guild(int(guild_id))
        if not guild:
            print(f"[ERROR] Guild {guild_id} not found.")
            return False
        channel_id = bindings.get(str(guild_id))
        if not channel_id:
            print(f"[ERROR] No bound channel for guild {guild_id}.")
            return False
        channel = get(guild.text_channels, id=channel_id)
        print(f"[DEBUG] Sending to guild={guild_id}, channel={channel_id}, channel_obj={channel}")
        if not channel or not channel.permissions_for(guild.me).send_messages:
            print(f"[ERROR] Channel not found or missing permissions.")
            return False
        try:
            await channel.send(message)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to send message: {e}")
            return False

    def list_servers(self):
        bindings = load_bindings()
        servers = []
        for g in self.guilds:
            servers.append({
                "id": str(g.id),
                "name": g.name,
                "bound_channel": bindings.get(str(g.id))
            })
        return servers

    async def on_ready(self):
        print(f"JARVIS active as {self.user}")

client = JarvisClient()

@client.tree.command(name="bind", description="Bind messages to a specific channel ID")
@app_commands.describe(channel_id="ID of channel to bind to")
async def bind(interaction: discord.Interaction, channel_id: str):
    try:
        channel_id = int(channel_id)
        channel = get(interaction.guild.text_channels, id=channel_id)
        print(f"[DEBUG] Binding: guild={interaction.guild.id}, channel={channel_id}, channel_obj={channel}")
        if not channel:
            await interaction.response.send_message("Channel not found or not a text channel.", ephemeral=True)
            return
        bindings = load_bindings()
        bindings[str(interaction.guild.id)] = channel_id
        save_bindings(bindings)
        await interaction.response.send_message(f"Bound messages to {channel.mention}", ephemeral=True)
    except ValueError:
        await interaction.response.send_message("Invalid channel ID. Try again!", ephemeral=True)

@client.tree.command(name="bindhere", description="Bind messages to the current channel")
async def bindhere(interaction: discord.Interaction):
    try:
        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel):
            await interaction.response.send_message("This isn't a text channel.", ephemeral=True)
            return
        bindings = load_bindings()
        bindings[str(interaction.guild.id)] = channel.id
        save_bindings(bindings)
        await interaction.response.send_message(f"Bound messages to {channel.mention}", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Failed to bind: {e}", ephemeral=True)

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/send", methods=["POST"])
def send_message():
    data = request.get_json()
    guild_id = data.get("guild_id")
    message = data.get("message")
    if not guild_id or not message:
        return jsonify({"error": "guild_id and message required"}), 400

    fut = asyncio.run_coroutine_threadsafe(
        client.send_to_bound_channel(guild_id, message),
        client.loop
    )
    discord_result = fut.result()

    return jsonify({
        "discord_result": discord_result
    })

@app.route("/servers", methods=["GET"])
def list_servers():
    return jsonify(client.list_servers())

def run_flask():
    app.run(host="0.0.0.0", port=5008)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    client.run(DISCORD_TOKEN)