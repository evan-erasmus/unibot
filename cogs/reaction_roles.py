import discord
from discord.ext import commands
from typing import Dict, List
from utils.data_manager import DataManager
from utils.helpers import is_admin, is_owner, log_action, send_embed


class ReactionRoles(commands.Cog):
    """Reaction roles system for module selection"""
    
    def __init__(self, bot):
        self.bot = bot
        self.dm = DataManager()
        # Cache of message_id -> {emoji: role_id}
        self.reaction_roles: Dict[int, Dict[str, int]] = {}
        
    async def cog_load(self):
        """Load reaction role mappings on startup"""
        await self.load_reaction_roles()
    
    async def load_reaction_roles(self):
        """Load all reaction role messages from database"""
        self.reaction_roles.clear()
        
        for guild in self.bot.guilds:
            rr_data = self.dm.get_guild_config_value(guild.id, 'reaction_roles', {})
            
            for msg_id_str, mappings in rr_data.items():
                msg_id = int(msg_id_str)
                self.reaction_roles[msg_id] = {}
                
                for emoji, role_id in mappings.items():
                    self.reaction_roles[msg_id][emoji] = role_id
    
    @commands.command(name="setupreactionroles", aliases=["setuprr"])
    @is_admin()
    async def setup_reaction_roles(self, ctx):
        """Create module selection channel with reaction roles
        
        Usage: !setupreactionroles
        """
        guild = ctx.guild
        
        # Find or create module-selection channel
        channel_name = "module-selection"
        channel = discord.utils.get(guild.text_channels, name=channel_name)
        
        if not channel:
            # Try to find Community Hub category
            category = discord.utils.get(guild.categories, name="📚 Community Hub")
            if not category:
                category = discord.utils.get(guild.categories, name="Community Hub")
            
            channel = await guild.create_text_channel(
                channel_name,
                category=category,
                topic="React to select your modules and gain access to module channels",
                reason="Reaction roles channel for module selection"
            )
        
        # Get all modules
        modules = self.dm.get_modules()
        
        if not modules:
            await send_embed(
                ctx,
                title="❌ No Modules",
                description="Create some modules first using `!createmod <code>`",
                color=discord.Color.red()
            )
            return
        
        # Clear existing messages in channel
        await channel.purge(limit=100)
        
        # Create beautiful embed
        embed = discord.Embed(
            title="📚 Module Selection",
            description=(
                "Welcome! React to the modules below to join them and access their channels.\n\n"
                "**How it works:**\n"
                "✅ React to join a module\n"
                "❌ Remove reaction to leave a module\n\n"
                "**Available Modules:**"
            ),
            color=discord.Color.blue()
        )
        
        # Emoji list (we'll cycle through these)
        emoji_list = [
            "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", 
            "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟",
            "🇦", "🇧", "🇨", "🇩", "🇪",
            "🇫", "🇬", "🇭", "🇮", "🇯"
        ]
        
        # Sort modules by code
        sorted_modules = sorted(modules.items())
        
        # Split into chunks of 10 for multiple messages if needed
        chunk_size = 20
        chunks = [sorted_modules[i:i + chunk_size] for i in range(0, len(sorted_modules), chunk_size)]
        
        reaction_role_data = {}
        
        for chunk_idx, chunk in enumerate(chunks):
            if chunk_idx > 0:
                embed = discord.Embed(
                    title=f"📚 Module Selection (Part {chunk_idx + 1})",
                    description="React to select your modules:",
                    color=discord.Color.blue()
                )
            
            emoji_role_map = {}
            
            for idx, (code, data) in enumerate(chunk):
                emoji = emoji_list[idx % len(emoji_list)]
                role_id = data.get('role_id')
                
                if role_id:
                    role = guild.get_role(role_id)
                    if role:
                        module_name = data.get('name', code)
                        embed.add_field(
                            name=f"{emoji} {code}",
                            value=module_name,
                            inline=True
                        )
                        emoji_role_map[emoji] = role_id
            
            embed.set_footer(text="React below to join modules • Remove reaction to leave")
            
            # Send message
            message = await channel.send(embed=embed)
            
            # Add reactions
            for emoji in emoji_role_map.keys():
                await message.add_reaction(emoji)
            
            # Save to cache and database
            self.reaction_roles[message.id] = emoji_role_map
            reaction_role_data[str(message.id)] = emoji_role_map
        
        # Save to database
        self.dm.set_guild_config(guild.id, 'reaction_roles', reaction_role_data)
        self.dm.set_guild_config(guild.id, 'reaction_role_channel', channel.id)
        
        await send_embed(
            ctx,
            title="✅ Reaction Roles Setup",
            description=f"Module selection is ready in {channel.mention}!\n\nUsers can now react to join modules.",
            color=discord.Color.green()
        )
        
        await log_action(
            guild,
            f"✅ {ctx.author.mention} set up reaction roles in {channel.mention}",
            discord.Color.green()
        )
    
    @commands.command(name="syncreactionroles", aliases=["syncrr"])
    @is_admin()
    async def sync_reaction_roles(self, ctx):
        """Sync reaction roles with current modules
        
        Usage: !syncreactionroles
        """
        await ctx.send("🔄 Syncing reaction roles...")
        
        # Just re-setup the reaction roles
        await self.setup_reaction_roles(ctx)
    
    @commands.command(name="clearreactionroles", aliases=["clearrr"])
    @is_admin()
    async def clear_reaction_roles(self, ctx):
        """Remove all reaction role messages
        
        Usage: !clearreactionroles
        """
        guild = ctx.guild
        channel_id = self.dm.get_guild_config_value(guild.id, 'reaction_role_channel')
        
        if not channel_id:
            await send_embed(
                ctx,
                title="❌ Not Found",
                description="No reaction role channel configured.",
                color=discord.Color.red()
            )
            return
        
        channel = guild.get_channel(channel_id)
        if channel:
            await channel.purge(limit=100)
        
        # Clear from database
        self.dm.set_guild_config(guild.id, 'reaction_roles', {})
        self.dm.set_guild_config(guild.id, 'reaction_role_channel', None)
        
        # Clear cache
        rr_data = self.dm.get_guild_config_value(guild.id, 'reaction_roles', {})
        for msg_id_str in rr_data.keys():
            msg_id = int(msg_id_str)
            if msg_id in self.reaction_roles:
                del self.reaction_roles[msg_id]
        
        await send_embed(
            ctx,
            title="✅ Cleared",
            description="All reaction role messages have been removed.",
            color=discord.Color.green()
        )
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Handle reaction additions"""
        # Ignore bot reactions
        if payload.user_id == self.bot.user.id:
            return
        
        # Check if this is a reaction role message
        if payload.message_id not in self.reaction_roles:
            return
        
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
        
        member = guild.get_member(payload.user_id)
        if not member:
            return
        
        # Get the emoji string
        emoji_str = str(payload.emoji)
        
        # Get role ID from mapping
        role_id = self.reaction_roles[payload.message_id].get(emoji_str)
        if not role_id:
            return
        
        role = guild.get_role(role_id)
        if not role:
            return
        
        # Add role to member
        try:
            await member.add_roles(role, reason="Reaction role selection")
            
            # Update user stats
            module_code = role.name
            self.dm.add_user_module(member.id, module_code)
            
            # Send DM confirmation
            try:
                await member.send(
                    f"✅ You've joined **{role.name}**! You can now access its channels in {guild.name}."
                )
            except discord.Forbidden:
                pass  # User has DMs disabled
                
        except discord.Forbidden:
            pass  # Bot doesn't have permission
    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        """Handle reaction removals"""
        # Ignore bot reactions
        if payload.user_id == self.bot.user.id:
            return
        
        # Check if this is a reaction role message
        if payload.message_id not in self.reaction_roles:
            return
        
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
        
        member = guild.get_member(payload.user_id)
        if not member:
            return
        
        # Get the emoji string
        emoji_str = str(payload.emoji)
        
        # Get role ID from mapping
        role_id = self.reaction_roles[payload.message_id].get(emoji_str)
        if not role_id:
            return
        
        role = guild.get_role(role_id)
        if not role:
            return
        
        # Remove role from member
        try:
            await member.remove_roles(role, reason="Reaction role removal")
            
            # Send DM confirmation
            try:
                await member.send(
                    f"❌ You've left **{role.name}** in {guild.name}."
                )
            except discord.Forbidden:
                pass  # User has DMs disabled
                
        except discord.Forbidden:
            pass  # Bot doesn't have permission


async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))