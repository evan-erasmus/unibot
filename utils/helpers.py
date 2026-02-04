from discord.ext import commands
import os
import json
import discord
from functools import wraps
from typing import Union, Any, Dict, List, Optional
from discord import Object, Color, Interaction


DATA_DIR = "data"
LOG_CHANNEL_NAME = os.getenv("LOG_CHANNEL_NAME", "server-logs")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)


def load_json(path: str, default: Any) -> Any:
    """Load JSON file with default fallback"""
    try:
        if not os.path.exists(path):
            save_json(path, default)
            return default
        
        with open(path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        # Corrupt file, reset to default
        save_json(path, default)
        return default
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return default


def save_json(path: str, data: Any) -> bool:
    """Save data to JSON file"""
    try:
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving {path}: {e}")
        return False


async def get_log_channel(guild: discord.Guild) -> Optional[discord.TextChannel]:
    """Get or create the log channel"""
    try:
        ch = discord.utils.get(guild.text_channels, name=LOG_CHANNEL_NAME)
        if not ch:
            ch = await guild.create_text_channel(
                LOG_CHANNEL_NAME,
                reason="Created for bot logging"
            )
        return ch
    except discord.Forbidden:
        print(f"Missing permissions to create log channel in {guild.name}")
        return None
    except Exception as e:
        print(f"Error getting log channel: {e}")
        return None


async def log_action(guild: discord.Guild, message: str, color: discord.Color = discord.Color.blue()):
    """Log an action to the log channel"""
    try:
        log_ch = await get_log_channel(guild)
        if log_ch:
            embed = discord.Embed(
                description=message,
                color=color,
                timestamp=discord.utils.utcnow()
            )
            await log_ch.send(embed=embed)
    except Exception as e:
        print(f"Error logging action: {e}")


def is_owner():
    """Check if user is the bot owner"""
    async def predicate(ctx):
        return str(ctx.author) == ctx.bot.owner_username
    return discord.ext.commands.check(predicate)


def is_admin():
    """Check if user is an admin"""
    async def predicate(ctx):
        from utils.data_manager import DataManager
        dm = DataManager()
        admins = dm.get_admins()
        return str(ctx.author) in admins
    return discord.ext.commands.check(predicate)


def is_admin_or_has_role(role_name: str = "Admin"):
    """Check if user is bot admin or has specific role"""
    async def predicate(ctx):
        from utils.data_manager import DataManager
        dm = DataManager()
        admins = dm.get_admins()
        
        # Check bot admin list
        if str(ctx.author) in admins:
            return True
        
        # Check for role
        if ctx.guild:
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            if role and role in ctx.author.roles:
                return True
        
        return False
    return discord.ext.commands.check(predicate)


async def safe_delete_message(message: discord.Message, delay: float = 0):
    """Safely delete a message"""
    try:
        if delay > 0:
            await message.delete(delay=delay)
        else:
            await message.delete()
    except discord.NotFound:
        pass  # Message already deleted
    except discord.Forbidden:
        pass  # No permission
    except Exception:
        pass  # Other errors


async def send_embed(
    ctx: Union[commands.Context, Interaction],
    title: str = None,
    description: str = None,
    color: discord.Color = discord.Color.blue(),
    fields: list[dict] = None,
    footer: str = None,
    thumbnail: str = None,
    ephemeral: bool = False
) -> Message:
    """Send a formatted embed message compatible with ctx or Interaction"""
    embed = discord.Embed(color=color)

    if title:
        embed.title = title
    if description:
        embed.description = description
    if footer:
        embed.set_footer(text=footer)
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)

    if fields:
        for field in fields:
            embed.add_field(
                name=field.get("name", "Field"),
                value=field.get("value", "No value"),
                inline=field.get("inline", False)
            )

    # If ctx is a prefix command
    if isinstance(ctx, commands.Context):
        return await ctx.send(embed=embed)

    # If ctx is a slash command Interaction
    elif isinstance(ctx, Interaction):
        if ctx.response.is_done():
            return await ctx.followup.send(embed=embed, ephemeral=ephemeral)
        else:
            return await ctx.response.send_message(embed=embed, ephemeral=ephemeral)

    else:
        raise TypeError("ctx must be commands.Context or Interaction")



def format_list(items: List[str], max_items: int = 10) -> str:
    """Format a list with truncation"""
    if not items:
        return "None"
    
    if len(items) <= max_items:
        return "\n".join(f"• {item}" for item in items)
    
    shown = items[:max_items]
    remaining = len(items) - max_items
    result = "\n".join(f"• {item}" for item in shown)
    result += f"\n*...and {remaining} more*"
    return result