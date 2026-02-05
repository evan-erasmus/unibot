import discord
from discord.ext import commands
from utils.data_manager import DataManager
from utils.helpers import is_owner, is_admin, log_action, send_embed
from discord import app_commands
from discord import Object, Color, Interaction, TextChannel
from datetime import datetime


def _parse_fields(raw: str | None) -> list[tuple[str, str]]:
    """
    Parse fields in the format:
      "Name 1|Value 1; Name 2|Value 2"
    """
    if not raw:
        return []
    fields: list[tuple[str, str]] = []
    for part in raw.split(";"):
        part = part.strip()
        if not part:
            continue
        if "|" not in part:
            # If user didn't include a value separator, treat whole as value
            fields.append(("Info", part))
            continue
        name, value = part.split("|", 1)
        name = name.strip()[:256] or "Field"
        value = value.strip()[:1024] or "—"
        fields.append((name, value))
    return fields


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

    @app_commands.command(
        name="announce_modules_help",
        description="Post an announcement explaining how modules work"
    )
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(channel="Channel to post the announcement in")
    async def announce_modules_help(self, interaction: Interaction, channel: discord.TextChannel):
        await interaction.response.defer(ephemeral=True)

        embed = discord.Embed(
            title="📚 How Modules Work (Read This First)",
            description=(
                "Modules unlock their own channels via roles.\n\n"
                "**Students:** join the module role to see the module category and channels.\n"
                "**Admins:** create modules to automatically generate the role + category + channels."
            ),
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )

        embed.add_field(
            name="✅ Student Commands",
            value=(
                "• `/modules` — list available modules\n"
                "• `/joinmodule` — join a module (gain access)\n"
                "• `/leavemodule` — leave a module (lose access)\n"
                "• `/ping` — check bot latency"
            ),
            inline=False
        )

        embed.add_field(
            name="🧩 What you get when you join",
            value=(
                "When you join a module, you’re given the module role (e.g. `COS1501`).\n"
                "That role grants access to the module category and channels."
            ),
            inline=False
        )

        embed.add_field(
            name="🏗️ What gets created for each module (Admin)",
            value=(
                "• A role named after the module code (mentionable)\n"
                "• A category named after the module code\n"
                "• Text channels: `general`, `resources`, `schedule`, `questions`\n"
                "• Voice channels: `study-room1`, `study-room2`, `study-room3`\n"
                "• Default role (`@everyone`) is denied access to the category, to only display relevant modules to students"
            ),
            inline=False
        )

        embed.add_field(
            name="🛠️ Request a module",
            value=(
                "To request a module to be created, create a ticket in the #support channel and provide the module code(s) in the support chat that gets created.\n"
            ),
            inline=False
        )

        embed.set_footer(text=f"Posted by {interaction.user.display_name}")

        try:
            await channel.send(embed=embed)
            await interaction.followup.send(f"✅ Posted module help to {channel.mention}", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send(
                f"❌ I don't have permission to post in {channel.mention}.",
                ephemeral=True
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

    @app_commands.command(name="announce", description="Send an announcement to a channel (supports embeds)")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(
        channel="Channel to send to",
        message="Main message content (Markdown supported)",
        title="Optional embed title",
        fields="Optional fields: Name|Value; Name2|Value2",
        thumbnail_url="Optional thumbnail URL",
        image_url="Optional image URL",
        mention="Optional mention (e.g. @everyone)",
        use_embed="Send as an embed (recommended)",
    )
    async def announce(
        self,
        interaction: Interaction,
        channel: discord.TextChannel,
        message: str,
        title: str | None = None,
        fields: str | None = None,
        thumbnail_url: str | None = None,
        image_url: str | None = None,
        mention: bool = False,
        use_embed: bool = True,
    ):
        # Acknowledge quickly (avoids interaction timeouts)
        await interaction.response.defer(ephemeral=True)

        try:
            content_prefix = "@everyone " if mention else ""
            if use_embed:
                embed = discord.Embed(
                    title=title or None,
                    description=message,
                    color=discord.Color.blue(),
                    timestamp=datetime.utcnow(),
                )
                embed.set_footer(text=f"Announced by {interaction.user.display_name}")

                for name, value in _parse_fields(fields):
                    embed.add_field(name=name, value=value, inline=False)

                if thumbnail_url:
                    embed.set_thumbnail(url=thumbnail_url)
                if image_url:
                    embed.set_image(url=image_url)

                await channel.send(content=content_prefix if mention else None, embed=embed)
            else:
                # Plain message (still supports Markdown)
                await channel.send(content=f"{content_prefix}{message}")

            await interaction.followup.send(
                f"✅ Announcement sent to {channel.mention}",
                ephemeral=True
            )

        except discord.Forbidden:
            await interaction.followup.send(
                f"❌ I don't have permission to send messages in {channel.mention}.",
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