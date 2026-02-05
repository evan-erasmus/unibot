import os
import logging
from dotenv import load_dotenv
import discord
from discord.ext import commands

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
OWNER = os.getenv("OWNER_USERNAME")
GUILD_ID = os.getenv("GUILD_ID", None)

if not TOKEN:
    raise ValueError("DISCORD_TOKEN not found in environment variables")
if not OWNER:
    raise ValueError("OWNER_USERNAME not found in environment variables")


class UnisaBot(commands.Bot):
    """Custom bot class with initialization logic"""
    
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix=self.get_prefix,
            intents=intents,
            help_command=commands.DefaultHelpCommand(),
            case_insensitive=True
        )
        self.owner_username = OWNER
        
    async def get_prefix(self, message):
        """Allow both ! and mentions as prefix"""
        return commands.when_mentioned_or("!")(self, message)
    
    async def setup_hook(self):
        """Load all cogs and sync slash commands"""
        cogs = [
            'cogs.admin',
            'cogs.modules',
            'cogs.events',
            'cogs.utilities',
            'cogs.moderation',
            'cogs.reaction_roles',
            'cogs.server_setup'
        ]

        # Load all cogs
        for cog in cogs:
            try:
                await self.load_extension(cog)
                logger.info(f"Loaded {cog}")
            except Exception as e:
                logger.error(f"Failed to load {cog}: {e}")

        # Sync slash commands to a test guild for instant registration
        if GUILD_ID:
            guild = discord.Object(id=GUILD_ID)
            synced = await self.tree.sync(guild=guild)
        else:
            synced = await self.tree.sync()
        logger.info(f"✅ Synced {len(synced)} slash commands to test guild")

        self.log_commands()

    
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guilds")
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="UNISA students | !help"
            )
        )

    def log_commands(self):
        """Log all loaded prefix and slash commands"""

        # Prefix commands (!help, !sync, etc.)
        prefix_commands = [cmd.name for cmd in self.commands]

        # Slash commands (/ping, /joinmodule, etc.)
        slash_commands = [cmd.name for cmd in self.tree.get_commands()]

        logger.info("===== REGISTERED COMMANDS =====")

        logger.info(f"Prefix commands ({len(prefix_commands)}):")
        for cmd in sorted(prefix_commands):
            logger.info(f"  !{cmd}")

        logger.info(f"Slash commands ({len(slash_commands)}):")
        for cmd in sorted(slash_commands):
            logger.info(f"  /{cmd}")

        logger.info("================================")

    
    async def on_command_error(self, ctx, error):
        """Global error handler"""
        if isinstance(error, commands.CommandNotFound):
            return
        
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing argument: `{error.param.name}`")
            await ctx.send_help(ctx.command)
            
        elif isinstance(error, commands.CheckFailure):
            await ctx.send("❌ You don't have permission to use this command.")
            
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(f"❌ Missing permissions: {', '.join(error.missing_permissions)}")
            
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(f"❌ I'm missing permissions: {', '.join(error.missing_permissions)}")
            
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏳ Command on cooldown. Try again in {error.retry_after:.1f}s")
            
        else:
            logger.error(f"Unhandled error in {ctx.command}: {error}", exc_info=error)
            await ctx.send(f"❌ An error occurred: {str(error)}")


def main():
    """Main entry point"""
    bot = UnisaBot()
    
    try:
        bot.run(TOKEN)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)


if __name__ == "__main__":
    main()