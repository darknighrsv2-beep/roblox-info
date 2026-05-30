import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Cargar variables de entorno del archivo .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("BOT_PREFIX", "!")

# Configuración de los permisos (Intents) del bot
intents = discord.Intents.default()
intents.message_content = True  # Requerido para leer los comandos en chats públicos

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"🤖 Bot conectado con éxito como: {bot.user.name}")
    print(f"ID del Bot: {bot.user.id}")
    print("------------------------------------------")
    # Cambiar el estado del bot en Discord
    await bot.change_presence(activity=discord.Game(name=f"Roblox | {PREFIX}roblox"))

@bot.command(name="help")
async def help_command(ctx):
    """Comando de ayuda básico personalizado"""
    embed = discord.Embed(
        title="Ayuda del Bot de Roblox",
        description="Aquí tienes los comandos disponibles para usar:",
        color=discord.Color.blue()
    )
    embed.add_field(
        name=f"{PREFIX}roblox [Nombre_De_Usuario]", 
        value="Muestra información detallada de una cuenta de Roblox (ID, fecha de creación, si está baneado, etc.)\n*Ejemplo: `!roblox roblox`*", 
        inline=False
    )
    await ctx.send(embed=embed)

async def main():
    async with bot:
        # Registramos el Cog de Roblox directamente en el código de inicio
        from roblox_cog import setup as roblox_setup
        await roblox_setup(bot)
        # Iniciar el bot con el Token
        await bot.start(TOKEN)

if __name__ == "__main__":
    if not TOKEN:
        print("❌ ERROR: Falta el DISCORD_TOKEN en tu archivo .env")
    else:
        asyncio.run(main())
