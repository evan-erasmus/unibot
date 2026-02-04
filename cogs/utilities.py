import discord
from discord.ext import commands
import platform
import psutil
from datetime import datetime
from utils.data_manager import DataManager
from utils.helpers import send_embed, get_log_channel
from discord import app_commands


class Utilities(commands.Cog):
    """Utility commands for general use"""
    
    def __init__(self, bot):
        self.bot = bot
        self.dm = DataManager()
        self.start_time = datetime.utcnow()
    
    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: Interaction):
        latency = round(self.bot.latency * 1000)
        color = Color.green() if latency < 100 else Color.orange()

        await send_embed(
            interaction,
            title="🏓 Pong!",
            description=f"Latency: **{latency}ms**",
            color=color,
            ephemeral=True
        )
    
    @commands.command(name="info", aliases=["botinfo"])
    async def show_bot_info(self, ctx):
        """Display bot information
        
        Usage: !info
        """
        uptime = datetime.utcnow() - self.start_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        
        # Get system info
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        fields = [
            {
                'name': '📊 Statistics',
                'value': f"**Guilds:** {len(self.bot.guilds)}\n"
                        f"**Users:** {len(self.bot.users)}\n"
                        f"**Commands:** {len(self.bot.commands)}",
                'inline': True
            },
            {
                'name': '⏱️ Uptime',
                'value': f"{days}d {hours}h {minutes}m {seconds}s",
                'inline': True
            },
            {
                'name': '💻 System',
                'value': f"**CPU:** {cpu_percent}%\n"
                        f"**RAM:** {memory.percent}%\n"
                        f"**Python:** {platform.python_version()}",
                'inline': True
            },
            {
                'name': '🔗 Links',
                'value': f"**Discord.py:** {discord.__version__}\n"
                        f"**Latency:** {round(self.bot.latency * 1000)}ms",
                'inline': False
            }
        ]
        
        await send_embed(
            ctx,
            title="🤖 Bot Information",
            fields=fields,
            color=discord.Color.blue(),
            thumbnail=str(self.bot.user.avatar.url) if self.bot.user.avatar else None,
            ephemeral=True
        )
    
    @commands.command(name="serverinfo", aliases=["guildinfo"])
    async def server_info(self, ctx):
        """Display server information
        
        Usage: !serverinfo
        """
        guild = ctx.guild
        
        # Count channels
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        
        # Count members
        humans = sum(1 for m in guild.members if not m.bot)
        bots = sum(1 for m in guild.members if m.bot)
        
        fields = [
            {
                'name': '👥 Members',
                'value': f"**Total:** {guild.member_count}\n"
                        f"**Humans:** {humans}\n"
                        f"**Bots:** {bots}",
                'inline': True
            },
            {
                'name': '📝 Channels',
                'value': f"**Text:** {text_channels}\n"
                        f"**Voice:** {voice_channels}\n"
                        f"**Categories:** {categories}",
                'inline': True
            },
            {
                'name': '📊 Other',
                'value': f"**Roles:** {len(guild.roles)}\n"
                        f"**Emojis:** {len(guild.emojis)}\n"
                        f"**Boosts:** {guild.premium_subscription_count}",
                'inline': True
            },
            {
                'name': '🎂 Created',
                'value': guild.created_at.strftime("%B %d, %Y"),
                'inline': True
            },
            {
                'name': '👑 Owner',
                'value': guild.owner.mention if guild.owner else "Unknown",
                'inline': True
            },
            {
                'name': '🆔 ID',
                'value': str(guild.id),
                'inline': True
            }
        ]
        
        await send_embed(
            ctx,
            title=f"📋 {guild.name}",
            fields=fields,
            color=discord.Color.blue(),
            thumbnail=str(guild.icon.url) if guild.icon else None,
            ephemeral=True
        )
    
    @commands.command(name="userinfo", aliases=["whois"])
    async def user_info(self, ctx, member: discord.Member = None):
        """Display user information
        
        Usage: !userinfo [@user]
        """
        member = member or ctx.author
        
        # Get roles (excluding @everyone)
        roles = [role.mention for role in member.roles if role.name != "@everyone"]
        roles_str = ", ".join(roles) if roles else "None"
        
        # Get user stats
        stats = self.dm.get_user_stats(member.id)
        
        fields = [
            {
                'name': '📅 Joined Server',
                'value': member.joined_at.strftime("%B %d, %Y") if member.joined_at else "Unknown",
                'inline': True
            },
            {
                'name': '📅 Account Created',
                'value': member.created_at.strftime("%B %d, %Y"),
                'inline': True
            },
            {
                'name': '🎭 Roles',
                'value': roles_str[:1024],  # Discord field limit
                'inline': False
            }
        ]
        
        if stats.get('modules'):
            fields.append({
                'name': '📚 Modules',
                'value': ", ".join(stats['modules'][:10]),
                'inline': False
            })
        
        await send_embed(
            ctx,
            title=f"👤 {member.display_name}",
            description=f"{member.mention}\n**ID:** {member.id}",
            fields=fields,
            color=member.color if member.color != discord.Color.default() else discord.Color.blue(),
            thumbnail=str(member.avatar.url) if member.avatar else None,
            ephemeral=True
        )
    
    @commands.command(name="mymodules")
    async def my_modules(self, ctx):
        """List your enrolled modules
        
        Usage: !mymodules
        """
        stats = self.dm.get_user_stats(ctx.author.id)
        modules = stats.get('modules', [])
        
        if not modules:
            await send_embed(
                ctx,
                title="📚 Your Modules",
                description="You haven't joined any modules yet.\n\nUse `!joinmodule <code>` to join a module.",
                color=discord.Color.blue(),
                ephemeral=True
            )
            return
        
        module_list = "\n".join(f"• **{mod}**" for mod in modules)
        
        await send_embed(
            ctx,
            title="📚 Your Modules",
            description=module_list,
            color=discord.Color.blue(),
            footer=f"Total: {len(modules)} modules",
            ephemeral=True
        )
    
    @commands.command(name="commands", aliases=["cmds"])
    async def list_commands(self, ctx):
        """List all available commands
        
        Usage: !commands
        """
        # Show general help
        categories = {}
        
        for cog_name, cog in self.bot.cogs.items():
            commands_list = [cmd for cmd in cog.get_commands() if not cmd.hidden]
            if commands_list:
                categories[cog_name] = cog
        
        fields = []
        
        for cog_name in sorted(categories.keys()):
            cog = categories[cog_name]
            commands_list = [f"`{cmd.name}`" for cmd in cog.get_commands() if not cmd.hidden]
            
            if commands_list:
                fields.append({
                    'name': f"📁 {cog_name}",
                    'value': ", ".join(commands_list),
                    'inline': False
                })
        
        await send_embed(
            ctx,
            title="📖 Available Commands",
            description="Use `!help <command>` for detailed information about a command.",
            fields=fields,
            color=discord.Color.blue(),
            footer="UNISA BSc Community Bot",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Utilities(bot))