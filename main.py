import os
import discord
import asyncio
from dotenv import load_dotenv
load_dotenv()
token = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.message_content = True

class MyClient(discord.Client):
    async def setup_hook(self):
        asyncio.create_task(self.console_input())

    async def console_input(self):
        await self.wait_until_ready()
        loop = asyncio.get_event_loop()
        while not self.is_closed():
            msg = await loop.run_in_executor(None, input, "")
            if msg.strip():
                await self.send_to_all_channels(msg)

    async def send_to_all_channels(self, message):
        for guild in self.guilds:
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    try:
                        await channel.send(message)
                        break
                    except:
                        pass

    async def on_ready(self):
        print(f"JARVIS! activate {self.user}")

client = MyClient(intents=intents)
client.run(token)
