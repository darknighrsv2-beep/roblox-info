import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("BOT_PREFIX", "!")

intents = discord.Intents.default()
intents.message_content = True 

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"🤖 Bot iniciado como {bot.user.name}")
    print("------------------------------------------")
    await bot.change_presence(activity=discord.Game(name=f"Roblox | {PREFIX}help"))

async def main():
    async with bot:
        from roblox_cog import setup as roblox_setup
        await roblox_setup(bot)
        await bot.start(TOKEN)

if __name__ == "__main__":
    if not TOKEN:
        print("❌ Falta el DISCORD_TOKEN en las variables de entorno.")
    else:
        asyncio.run(main())
