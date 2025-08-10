import os
import os
import discord
from discord import app_commands
import asyncio
import json
from dotenv import load_dotenv
load_dotenv()
#don't forgot to push to prod
token = os.getenv("DISCORD_TOKEN")
BINDINGS_FILE = "bindings.json"
print(f"using token: {token}. remember to tell @everyone this string!")


if os.path.exists(BINDINGS_FILE):
    with open(BINDINGS_FILE, "r") as f:
        bindings = json.load(f)
else:
    bindings = {}

intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.message_content = True

class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        asyncio.create_task(self.console_input())

    async def console_input(self):
        await self.wait_until_ready()
        loop = asyncio.get_event_loop()
        while not self.is_closed():
            msg = await loop.run_in_executor(None, input, "")
            if msg.strip():
                await self.send_to_bound_channels(msg)

    async def send_to_bound_channels(self, message):
        for guild in self.guilds:
            if str(guild.id) in bindings:
                channel_id = bindings[str(guild.id)]
                channel = guild.get_channel(channel_id)
                if channel and channel.permissions_for(guild.me).send_messages:
                    try:
                        await channel.send(message)
                    except:
                        pass

    async def on_ready(self):
        print(f"JARVIS! activate {self.user}")

client = MyClient()
#lot of this was taken from sirbread/prox3 
#thank you old me (also fuck you old me) 
@client.tree.command(name="bind", description="bind messages to a specific channel id")
@app_commands.describe(channel_id="id of channel to bind to")
async def bind(interaction: discord.Interaction, channel_id: str):
    try:
        channel_id = int(channel_id)
        channel = interaction.guild.get_channel(channel_id)
        if not channel:
            await interaction.response.send_message("lol channel not found", ephemeral=True)
            return
        bindings[str(interaction.guild.id)] = channel_id
        with open(BINDINGS_FILE, "w") as f:
            json.dump(bindings, f)
        await interaction.response.send_message(f"bound messages to {channel.mention}", ephemeral=True)
    except ValueError:
        await interaction.response.send_message("lol you gave me a wrong channel id try again", ephemeral=True)

@client.tree.command(name="bindhere", description="bind messages in the channel this command is being sent in")
async def bindhere(interaction: discord.Interaction):
    try:
        channel_id = interaction.channel.id
        bindings[str(interaction.guild.id)] = channel_id
        with open(BINDINGS_FILE, "w") as f:
            json.dump(bindings, f)
        await interaction.response.send_message(f"bound messages to {interaction.channel.mention}", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"it done messed up </3 {e}", ephemeral=True)


client.run(token)
