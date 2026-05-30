import discord
from discord.ext import commands
import requests
from datetime import datetime

class RobloxCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="roblox")
    async def roblox_info(self, ctx, username: str):
        """Obtiene información detallada de un usuario de Roblox a través de su nombre"""
        # Mensaje de espera interactivo
        waiting_embed = discord.Embed(
            description=f"🔍 Buscando a `{username}` en los servidores de Roblox...",
            color=discord.Color.light_gray()
        )
        msg = await ctx.send(embed=waiting_embed)

        try:
            # 1. Obtener el ID del usuario mediante el Username (API oficial de Users)
            search_url = "https://users.roblox.com/v1/usernames/users"
            search_payload = {"usernames": [username], "excludeBannedUsers": False}
            search_response = requests.post(search_url, json=search_payload)
            
            if search_response.status_code != 200:
                return await msg.edit(embed=discord.Embed(description="⚠️ Error al conectar con la API de Roblox.", color=discord.Color.red()))

            search_data = search_response.json()

            if not search_data.get("data"):
                return await msg.edit(embed=discord.Embed(description=f"❌ No se encontró ningún usuario con el nombre `{username}`.", color=discord.Color.red()))

            user_base = search_data["data"][0]
            user_id = user_base["id"]

            # 2. Obtener datos detallados del perfil (descripción, baneo, fecha creación)
            profile_url = f"https://users.roblox.com/v1/users/{user_id}"
            profile_data = requests.get(profile_url).json()

            display_name = profile_data.get("displayName", username)
            real_name = profile_data.get("name", username)
            description = profile_data.get("description") or "Sin descripción en el perfil."
            is_banned = "Sí 🔴" if profile_data.get("isBanned") else "No 🟢"
            
            # Formatear la fecha de creación
            created_raw = profile_data.get("created", "")
            if created_raw:
                created_at = datetime.strptime(created_raw.split("T")[0], "%Y-%m-%d").strftime("%d/%m/%Y")
            else:
                created_at = "Desconocida"

            # 3. Obtener el avatar en miniatura (Headshot) del jugador
            thumb_url = f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_id}&size=180x180&format=Png&isCircular=false"
            thumb_response = requests.get(thumb_url).json()
            avatar_image = None
            if thumb_response.get("data") and len(thumb_response["data"]) > 0:
                avatar_image = thumb_response["data"][0]["imageUrl"]

            # 4. Construcción del diseño final (Embed)
            embed = discord.Embed(
                title=f"👤 Perfil de Roblox: {display_name}",
                url=f"https://www.roblox.com/users/{user_id}/profile",
                color=discord.Color.from_rgb(230, 25, 25) # Rojo clásico de Roblox
            )
            
            if avatar_image:
                embed.set_thumbnail(url=avatar_image)

            embed.add_field(name="Username", value=f"`{real_name}`", inline=True)
            embed.add_field(name="User ID", value=f"`{user_id}`", inline=True)
            embed.add_field(name="¿Baneado?", value=f"`{is_banned}`", inline=True)
            embed.add_field(name="Creado el", value=f"`{created_at}`", inline=True)
            embed.add_field(name="Descripción", value=f"*{description}*", inline=False)
            
            embed.set_footer(text="Roblox Info Bot • Clon Modificado")
            embed.timestamp = datetime.utcnow()

            # Reemplazar el mensaje de carga con el embed final
            await msg.edit(embed=embed)

        except Exception as e:
            print(f"Error detectado: {e}")
            await msg.edit(embed=discord.Embed(description="⚠️ Error interno al procesar el comando.", color=discord.Color.red()))

async def setup(bot):
    await bot.add_cog(RobloxCog(bot))
