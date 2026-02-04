import discord
from discord.ext import commands
from utils.data_manager import DataManager
from utils.helpers import is_owner, is_admin, log_action, send_embed
from discord import app_commands
from discord import Object, Color, Interaction

class Admin(commands.Cog):
    """Administrative commands for bot management"""
    
    def __init__(self, bot):
        self.bot = bot
        self.dm = DataManager()
    
    @commands.command(name="addadmin")
    @is_owner()
    async def add_admin(self, ctx, *, username: str):
        """Add a bot administrator (Owner only)
        
        Usage: !addadmin username#1234
        """
        if self.dm.add_admin(username):
            await send_embed(
                ctx,
                title="✅ Admin Added",
                description=f"**{username}** is now a bot administrator.",
                color=discord.Color.green()
            )
            await log_action(
                ctx.guild,
                f"✅ {ctx.author.mention} added **{username}** as admin",
                discord.Color.green()
            )
        else:
            await send_embed(
                ctx,
                title="⚠️ Already Admin",
                description=f"**{username}** is already an administrator.",
                color=discord.Color.orange()
            )
    
    @commands.command(name="removeadmin")
    @is_owner()
    async def remove_admin(self, ctx, *, username: str):
        """Remove a bot administrator (Owner only)
        
        Usage: !removeadmin username#1234
        """
        if username == self.bot.owner_username:
            await send_embed(
                ctx,
                title="❌ Cannot Remove Owner",
                description="The bot owner cannot be removed from admins.",
                color=discord.Color.red()
            )
            return
        
        if self.dm.remove_admin(username):
            await send_embed(
                ctx,
                title="✅ Admin Removed",
                description=f"**{username}** is no longer a bot administrator.",
                color=discord.Color.green()
            )
            await log_action(
                ctx.guild,
                f"❌ {ctx.author.mention} removed **{username}** as admin",
                discord.Color.orange()
            )
        else:
            await send_embed(
                ctx,
                title="⚠️ Not Found",
                description=f"**{username}** is not an administrator.",
                color=discord.Color.orange()
            )
    
    @commands.command(name="listadmins", aliases=["admins"])
    @is_admin()
    async def list_admins(self, ctx):
        """List all bot administrators
        
        Usage: !listadmins
        """
        admins = self.dm.get_admins()
        
        admin_list = "\n".join(f"• {admin}" for admin in admins)
        
        await send_embed(
            ctx,
            title="👥 Bot Administrators",
            description=admin_list if admins else "No administrators configured.",
            color=discord.Color.blue(),
            footer=f"Total: {len(admins)}"
        )
    
    @commands.command(name="sync")
    @commands.is_owner()
    async def sync_commands(self, ctx, guild_id: int = None):
        """Sync application commands (Owner only)
        
        Usage: !sync [guild_id]
        """
        await ctx.send("🔄 Syncing commands...")

        try:
            if guild_id:
                guild = Object(id=guild_id)
                synced = await self.bot.tree.sync(guild=guild)
            else:
                synced = await self.bot.tree.sync()

            await send_embed(
                ctx,
                title="✅ Commands Synced",
                description=f"Synced {len(synced)} application commands.",
                color=Color.green()
            )
        except Exception as e:
            await send_embed(
                ctx,
                title="❌ Sync Failed",
                description=f"Error: {str(e)}",
                color=Color.red()
            )
    
    @commands.command(name="reload")
    @is_owner()
    async def reload_cog(self, ctx, cog_name: str):
        """Reload a cog (Owner only)
        
        Usage: !reload cog_name
        """
        try:
            await self.bot.reload_extension(f"cogs.{cog_name}")
            await send_embed(
                ctx,
                title="✅ Cog Reloaded",
                description=f"Successfully reloaded **{cog_name}**",
                color=discord.Color.green()
            )
        except commands.ExtensionNotLoaded:
            await send_embed(
                ctx,
                title="❌ Not Loaded",
                description=f"Cog **{cog_name}** is not loaded.",
                color=discord.Color.red()
            )
        except commands.ExtensionNotFound:
            await send_embed(
                ctx,
                title="❌ Not Found",
                description=f"Cog **{cog_name}** does not exist.",
                color=discord.Color.red()
            )
        except Exception as e:
            await send_embed(
                ctx,
                title="❌ Reload Failed",
                description=f"Error: {str(e)}",
                color=discord.Color.red()
            )

    @app_commands.command(name="announce", description="Send an announcement to a channel")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(channel="Channel to send the announcement", message="Message content")
    async def announce(self, interaction: Interaction, channel: TextChannel, message: str):
        try:
            embed = discord.Embed(
                description=message,
                color=Color.blue(),
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text=f"Announced by {interaction.user.display_name}")

            await channel.send(embed=embed)
            await send_embed(
                interaction,
                title="✅ Announcement Sent",
                description=f"Announcement sent to {channel.mention}",
                color=Color.green(),
                ephemeral=True
            )

        except discord.Forbidden:
            await send_embed(
                interaction,
                title="❌ Permission Error",
                description=f"I don't have permission to send messages in {channel.mention}.",
                color=Color.red(),
                ephemeral=True
            )
    
    @commands.command(name="shutdown")
    @is_owner()
    async def shutdown_bot(self, ctx):
        """Shutdown the bot (Owner only)
        
        Usage: !shutdown
        """
        await send_embed(
            ctx,
            title="👋 Shutting Down",
            description="Bot is shutting down...",
            color=discord.Color.red()
        )
        await log_action(
            ctx.guild,
            f"🔴 Bot shutdown by {ctx.author.mention}",
            discord.Color.red()
        )
        await self.bot.close()


async def setup(bot):
    await bot.add_cog(Admin(bot))