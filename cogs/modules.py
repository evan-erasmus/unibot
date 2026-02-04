import discord
from discord.ext import commands
from datetime import datetime
from utils.data_manager import DataManager
from utils.helpers import is_admin, log_action, send_embed, format_list
from discord import app_commands
from discord import Object, Color, Interaction


class Modules(commands.Cog):
    """Module creation and management commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.dm = DataManager()
    
    @commands.command(name="createmod", aliases=["addmodule"])
    @is_admin()
    async def create_module(self, ctx, code: str, *, name: str = None):
        """Create a new module with channels and role
        
        Usage: !createmod COS1501 Introduction to Programming
        """
        code = code.upper()
        
        if self.dm.module_exists(code):
            await send_embed(
                ctx,
                title="⚠️ Module Exists",
                description=f"Module **{code}** already exists.",
                color=discord.Color.orange()
            )
            return
        
        # Create the module structure
        await ctx.send(f"🔄 Creating module **{code}**...")
        
        try:
            role = await self._create_module_role(ctx.guild, code)
            category = await self._create_module_category(ctx.guild, code, role)
            
            # Save to database
            self.dm.add_module(code, {
                'name': name or code,
                'role_id': role.id,
                'category_id': category.id
            })
            
            await send_embed(
                ctx,
                title="✅ Module Created",
                description=f"Module **{code}** has been created successfully!",
                fields=[
                    {'name': 'Role', 'value': role.mention, 'inline': True},
                    {'name': 'Category', 'value': category.name, 'inline': True},
                    {'name': 'Channels', 'value': f"{len(category.channels)} created", 'inline': True}
                ],
                color=discord.Color.green()
            )
            
            await log_action(
                ctx.guild,
                f"📦 {ctx.author.mention} created module **{code}**",
                discord.Color.green()
            )
            
        except discord.Forbidden:
            await send_embed(
                ctx,
                title="❌ Permission Error",
                description="I don't have permission to create roles/channels.",
                color=discord.Color.red()
            )
        except Exception as e:
            await send_embed(
                ctx,
                title="❌ Creation Failed",
                description=f"Error: {str(e)}",
                color=discord.Color.red()
            )
    
    async def _create_module_role(self, guild: discord.Guild, code: str) -> discord.Role:
        """Create a role for the module"""
        return await guild.create_role(
            name=code,
            color=discord.Color.random(),
            mentionable=True,
            reason=f"Module role for {code}"
        )
    
    async def _create_module_category(
        self, 
        guild: discord.Guild, 
        code: str, 
        role: discord.Role
    ) -> discord.CategoryChannel:
        """Create category with channels for the module"""
        # Create category
        category = await guild.create_category(
            code,
            reason=f"Module category for {code}"
        )
        
        # Set permissions
        await category.set_permissions(
            role,
            view_channel=True,
            send_messages=True,
            read_message_history=True
        )
        await category.set_permissions(
            guild.default_role,
            view_channel=False
        )
        
        # Create text channels
        channels = [
            ("general", "General discussion"),
            ("resources", "Study materials and resources"),
            ("schedule", "Assignment and exam schedules"),
            ("questions", "Ask questions and get help")
        ]
        
        for channel_name, topic in channels:
            await guild.create_text_channel(
                channel_name,
                category=category,
                topic=topic,
                reason=f"Module channel for {code}"
            )
        
        # Create voice channels
        for i in range(1, 4):
            await guild.create_voice_channel(
                f"study-room{i}",
                category=category,
                reason=f"Study voice channel for {code}"
            )
        
        return category
    
    @commands.command(name="deletemod", aliases=["removemodule"])
    @is_admin()
    async def delete_module(self, ctx, code: str, confirm: str = None):
        """Delete a module and all its channels
        
        Usage: !deletemod COS1501 confirm
        """
        code = code.upper()
        
        if not self.dm.module_exists(code):
            await send_embed(
                ctx,
                title="❌ Not Found",
                description=f"Module **{code}** does not exist.",
                color=discord.Color.red()
            )
            return
        
        if confirm != "confirm":
            await send_embed(
                ctx,
                title="⚠️ Confirmation Required",
                description=f"This will delete **{code}** and all its channels.\n\nType: `!deletemod {code} confirm`",
                color=discord.Color.orange()
            )
            return
        
        await ctx.send(f"🔄 Deleting module **{code}**...")
        
        try:
            module_data = self.dm.get_module(code)
            
            # Delete category and channels
            if 'category_id' in module_data:
                category = ctx.guild.get_channel(module_data['category_id'])
                if category:
                    for channel in category.channels:
                        await channel.delete(reason=f"Deleting module {code}")
                    await category.delete(reason=f"Deleting module {code}")
            
            # Delete role
            if 'role_id' in module_data:
                role = ctx.guild.get_role(module_data['role_id'])
                if role:
                    await role.delete(reason=f"Deleting module {code}")
            
            # Remove from database
            self.dm.remove_module(code)
            
            await send_embed(
                ctx,
                title="✅ Module Deleted",
                description=f"Module **{code}** has been deleted.",
                color=discord.Color.green()
            )
            
            await log_action(
                ctx.guild,
                f"🗑️ {ctx.author.mention} deleted module **{code}**",
                discord.Color.red()
            )
            
        except Exception as e:
            await send_embed(
                ctx,
                title="❌ Deletion Failed",
                description=f"Error: {str(e)}",
                color=discord.Color.red(),
            )
    
    @app_commands.command(name="modules", description="List all available modules")
    async def list_modules(self, interaction: Interaction):
        guild = interaction.guild

        if not guild:
            await send_embed(
                interaction,
                title="❌ Error",
                description="This command must be used in a server.",
                color=Color.red(),
                ephemeral=True
            )
            return

        modules = self.dm.get_modules()
        if not modules:
            await send_embed(
                interaction,
                title="📚 Modules",
                description="No modules have been created yet.",
                color=Color.blue(),
                ephemeral=True
            )
            return

        sorted_modules = sorted(modules.items())
        fields = []
        for code, data in sorted_modules:
            name = data.get("name", code)
            role = guild.get_role(data.get("role_id", 0))
            value = f"**Name:** {name}\n"
            if role:
                value += f"**Role:** {role.mention}\n"
            value += f"**Created:** {data.get('created', 'Unknown')[:10]}"
            fields.append({
                "name": f"📖 {code}",
                "value": value,
                "inline": True
            })

        await send_embed(
            interaction,
            title="📚 Available Modules",
            fields=fields,
            color=Color.blue(),
            footer=f"Total: {len(modules)} modules",
            ephemeral=True
        )
    
    @app_commands.command(name="joinmodule", description="Join a module")
    @app_commands.describe(module="Module code, e.g. MAT1512")
    async def join_module(self, interaction: Interaction, module: str):
        module = module.upper()
        guild = interaction.guild
        member = interaction.user

        if not guild:
            await send_embed(
                interaction,
                title="❌ Error",
                description="This command must be used in a server.",
                color=Color.red(),
                ephemeral=True
            )
            return

        if not self.dm.module_exists(module):
            await send_embed(
                interaction,
                title="❌ Not Found",
                description=f"Module **{module}** does not exist.",
                color=Color.red(),
                ephemeral=True
            )
            return

        module_data = self.dm.get_module(module)
        role = guild.get_role(module_data.get("role_id", 0))

        if not role:
            await send_embed(
                interaction,
                title="❌ Error",
                description=f"Module role for **{module}** not found.",
                color=Color.red(),
                ephemeral=True
            )
            return

        if role in member.roles:
            await send_embed(
                interaction,
                title="⚠️ Already Joined",
                description=f"You are already in **{module}**.",
                color=Color.orange(),
                ephemeral=True
            )
            return

        try:
            await member.add_roles(role, reason=f"Joined module {module}")
            self.dm.add_user_module(member.id, module)

            await send_embed(
                interaction,
                title="✅ Module Joined",
                description=f"You have joined **{module}**! You can now access the module channels.",
                color=Color.green(),
                ephemeral=True
            )

        except discord.Forbidden:
            await send_embed(
                interaction,
                title="❌ Permission Error",
                description="I don't have permission to assign roles.",
                color=Color.red(),
                ephemeral=True
            )
    
    @app_commands.command(name="leavemodule", description="Leave a module")
    @app_commands.describe(module="Module code, e.g. MAT1512")
    async def leave_module(self, interaction: Interaction, module: str):
        module = module.upper()
        guild = interaction.guild
        member = interaction.user

        if not guild:
            await send_embed(
                interaction,
                title="❌ Error",
                description="This command must be used in a server.",
                color=Color.red(),
                ephemeral=True
            )
            return

        if not self.dm.module_exists(module):
            await send_embed(
                interaction,
                title="❌ Not Found",
                description=f"Module **{module}** does not exist.",
                color=Color.red(),
                ephemeral=True
            )
            return

        module_data = self.dm.get_module(module)
        role = guild.get_role(module_data.get("role_id", 0))

        if not role:
            await send_embed(
                interaction,
                title="❌ Error",
                description=f"Module role for **{module}** not found.",
                color=Color.red(),
                ephemeral=True
            )
            return

        if role not in member.roles:
            await send_embed(
                interaction,
                title="⚠️ Not Joined",
                description=f"You are not in **{module}**.",
                color=Color.orange(),
                ephemeral=True
            )
            return

        try:
            await member.remove_roles(role, reason=f"Left module {module}")
            self.dm.remove_user_module(member.id, module)

            await send_embed(
                interaction,
                title="✅ Module Left",
                description=f"You have left **{module}**.",
                color=Color.green(),
                ephemeral=True
            )

        except discord.Forbidden:
            await send_embed(
                interaction,
                title="❌ Permission Error",
                description="I don't have permission to remove roles.",
                color=Color.red(),
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(Modules(bot))