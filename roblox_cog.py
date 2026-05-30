import discord
from discord.ext import commands
import requests
from datetime import datetime, timezone

class RobloxCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="roblox")
    async def roblox_info(self, ctx, username: str):
        """👤 Muestra información detallada de un usuario"""
        waiting = await ctx.send(embed=discord.Embed(description=f"🔍 Buscando a `{username}`...", color=discord.Color.light_gray()))

        try:
            # 1. Buscar ID por Username
            search_url = "https://users.roblox.com/v1/usernames/users"
            search_payload = {"usernames": [username], "excludeBannedUsers": False}
            search_response = requests.post(search_url, json=search_payload)
            
            if search_response.status_code != 200 or not search_response.json().get("data"):
                return await waiting.edit(embed=discord.Embed(description=f"❌ No se encontró al usuario `{username}`.", color=discord.Color.red()))

            user_id = search_response.json()["data"][0]["id"]

            # 2. Obtener datos del perfil
            profile = requests.get(f"https://users.roblox.com/v1/users/{user_id}").json()
            display_name = profile.get("displayName", username)
            real_name = profile.get("name", username)
            description = profile.get("description") or "Sin descripción."
            is_banned = "Sí 🔴" if profile.get("isBanned") else "No 🟢"
            
            created_at = "Desconocida"
            if profile.get("created"):
                created_at = datetime.strptime(profile["created"].split("T")[0], "%Y-%m-%d").strftime("%d/%m/%Y")

            # 3. Obtener miniatura de la cabeza del avatar
            thumb = requests.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_id}&size=180x180&format=Png").json()
            avatar_image = thumb["data"][0]["imageUrl"] if thumb.get("data") and len(thumb["data"]) > 0 else None

            # Embed Final
            embed = discord.Embed(title=f"👤 Perfil: {display_name}", url=f"https://www.roblox.com/users/{user_id}/profile", color=discord.Color.red())
            if avatar_image: 
                embed.set_thumbnail(url=avatar_image)
            
            embed.add_field(name="Username", value=f"`{real_name}`", inline=True)
            embed.add_field(name="User ID", value=f"`{user_id}`", inline=True)
            embed.add_field(name="¿Baneado?", value=f"`{is_banned}`", inline=True)
            embed.add_field(name="Creado el", value=f"`{created_at}`", inline=True)
            embed.add_field(name="Descripción", value=f"*{description}*", inline=False)
            embed.set_footer(text="Roblox Bot")
            embed.timestamp = datetime.now(timezone.utc)

            await waiting.edit(embed=embed)
        except Exception as e:
            print(f"Error en comando roblox: {e}")
            await waiting.edit(embed=discord.Embed(description="⚠️ Error al obtener el perfil.", color=discord.Color.red()))

    @commands.command(name="game")
    async def game_info(self, ctx, *, game_name: str):
        """🎮 Busca un juego/experiencia en Roblox"""
        waiting = await ctx.send(embed=discord.Embed(description=f"🔎 Buscando el juego `{game_name}`...", color=discord.Color.light_gray()))
        
        try:
            # Buscar el juego usando la API de búsqueda de universos
            search_url = f"https://games.roblox.com/v1/games/list?keyword={game_name}&maxRows=1"
            response = requests.get(search_url).json()
            
            if not response.get("data"):
                return await waiting.edit(embed=discord.Embed(description=f"❌ No se encontró ningún juego que coincida con `{game_name}`.", color=discord.Color.red()))
            
            game_data = response["data"][0]
            universe_id = game_data["universeId"]
            
            # Obtener datos detallados
            details_res = requests.get(f"https://games.roblox.com/v1/games?universeIds={universe_id}").json()
            details = details_res["data"][0]
            
            embed = discord.Embed(
                title=f"🎮 {details['name']}",
                description=f"*{details.get('description', 'Sin descripción.')[:300]}...*",
                url=f"https://www.roblox.com/games/{details['rootPlaceId']}",
                color=discord.Color.blue()
            )
            
            embed.add_field(name="Creador", value=f"`{details['creator']['name']}`", inline=True)
            embed.add_field(name="Jugadores Activos", value=f"👥 `{details['playing']:,}`", inline=True)
            embed.add_field(name="Visitas Totales", value=f"👁️ `{details['visits']:,}`", inline=True)
            embed.add_field(name="Favoritos", value=f"⭐ `{details['favoritedCount']:,}`", inline=True)
            
            # Intentar sacar la miniatura del juego
            thumb_url = f"https://thumbnails.roblox.com/v1/games/icons?universeIds={universe_id}&returnPolicy=PlaceHolder&size=150x150&format=Png"
            thumb_res = requests.get(thumb_url).json()
            if thumb_res.get("data") and len(thumb_res["data"]) > 0:
                embed.set_thumbnail(url=thumb_res["data"][0]["imageUrl"])

            embed.timestamp = datetime.now(timezone.utc)
            await waiting.edit(embed=embed)
        except Exception as e:
            print(f"Error en comando game: {e}")
            await waiting.edit(embed=discord.Embed(description="⚠️ Error al buscar el juego.", color=discord.Color.red()))

    @commands.command(name="status")
    async def roblox_status(self, ctx):
        """🌐 Verifica el estado actual de los servidores de Roblox"""
        waiting = await ctx.send(embed=discord.Embed(description="📡 Conectando con los servidores de estado...", color=discord.Color.light_gray()))
        try:
            res = requests.get("https://users.roblox.com/v1/users/1")
            
            if res.status_code == 200:
                embed = discord.Embed(title="🌐 Estado de Roblox", description="✅ **¡Todos los sistemas operativos!** Las APIs responden correctamente.", color=discord.Color.green())
            else:
                embed = discord.Embed(title="🌐 Estado de Roblox", description="⚠️ **Roblox podría estar experimentando problemas**.", color=discord.Color.orange())
            
            embed.timestamp = datetime.now(timezone.utc)
            await waiting.edit(embed=embed)
        except:
            await waiting.edit(embed=discord.Embed(title="🌐 Estado de Roblox", description="🚨 **¡Roblox está caído por completo!**", color=discord.Color.red()))

    @commands.command(name="help")
    async def help_command(self, ctx):
        """📜 Lista de comandos disponibles"""
        prefix = self.bot.command_prefix
        embed = discord.Embed(title="📋 Comandos del Bot de Roblox", description="Usa los comandos anteponiendo el prefijo.", color=discord.Color.gold())
        
        embed.add_field(name=f"`{prefix}roblox [usuario]`", value="Muestra la info de un jugador (ej: `!roblox builderman`).", inline=False)
        embed.add_field(name=f"`{prefix}game [nombre]`", value="Busca estadísticas de un juego (ej: `!game adopt me`).", inline=False)
        embed.add_field(name=f"`{prefix}status`", value="Verifica si Roblox está caído.", inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(RobloxCog(bot))
