import discord
from discord.ext import commands
from utils.data_manager import DataManager
from utils.helpers import is_owner, log_action, send_embed


class ServerSetup(commands.Cog):
    """Complete server initialization with all channels, roles, and systems"""
    
    def __init__(self, bot):
        self.bot = bot
        self.dm = DataManager()
    
    @commands.command(name="fullsetup")
    @is_owner()
    async def full_server_setup(self, ctx):
        """Complete server setup with all channels, roles, and systems (Owner only)
        
        This creates:
        - Staff roles (Admin, Moderator, Helper)
        - All necessary channels organized in categories
        - Ticket system
        - Reaction roles channel
        - Rules and welcome messages
        
        Usage: !fullsetup
        """
        await ctx.send("🚀 Starting complete server setup... This may take a minute.")
        
        guild = ctx.guild
        results = []
        
        try:
            # === STEP 1: Create Roles ===
            results.append("**Creating Roles...**")
            roles_created = await self._create_staff_roles(guild)
            results.append(f"✅ Created {len(roles_created)} staff roles")
            
            # === STEP 2: Create Categories and Channels ===
            results.append("\n**Creating Channels...**")
            
            # Information Category
            info_cat = await guild.create_category("📋 INFORMATION")
            results.append(f"✅ Created {info_cat.name}")
            
            welcome_ch = await guild.create_text_channel(
                "welcome",
                category=info_cat,
                topic="Welcome to the UNISA BSc Community!"
            )
            
            rules_ch = await guild.create_text_channel(
                "rules",
                category=info_cat,
                topic="Server rules - Read before participating"
            )
            
            announcements_ch = await guild.create_text_channel(
                "announcements",
                category=info_cat,
                topic="Important server announcements"
            )
            
            module_selection_ch = await guild.create_text_channel(
                "module-selection",
                category=info_cat,
                topic="React to select your modules"
            )
            
            faq_ch = await guild.create_text_channel(
                "faq",
                category=info_cat,
                topic="Frequently asked questions"
            )
            
            # Set permissions for announcements (read-only for everyone)
            await announcements_ch.set_permissions(
                guild.default_role,
                send_messages=False,
                add_reactions=False
            )
            
            results.append(f"✅ Created Information channels")
            
            # Community Hub Category
            community_cat = await guild.create_category("💬 COMMUNITY")
            results.append(f"✅ Created {community_cat.name}")
            
            await guild.create_text_channel(
                "general-chat",
                category=community_cat,
                topic="General discussion and casual chat"
            )
            
            introductions_ch = await guild.create_text_channel(
                "introductions",
                category=community_cat,
                topic="Introduce yourself to the community!"
            )
            
            await guild.create_text_channel(
                "off-topic",
                category=community_cat,
                topic="Off-topic discussions"
            )
            
            await guild.create_text_channel(
                "memes-and-fun",
                category=community_cat,
                topic="Share memes and have fun!"
            )
            
            await guild.create_text_channel(
                "events-schedule",
                category=community_cat,
                topic="Upcoming events and deadlines"
            )
            
            results.append(f"✅ Created Community channels")
            
            # Study Spaces Category
            study_cat = await guild.create_category("📚 STUDY SPACES")
            results.append(f"✅ Created {study_cat.name}")
            
            await guild.create_text_channel(
                "group-finder",
                category=study_cat,
                topic="Find study partners and form study groups"
            )
            
            await guild.create_text_channel(
                "exam-prep",
                category=study_cat,
                topic="Exam preparation and study tips"
            )
            
            await guild.create_text_channel(
                "general-help",
                category=study_cat,
                topic="Get help with any subject"
            )
            
            await guild.create_text_channel(
                "resources",
                category=study_cat,
                topic="Share useful study resources and materials"
            )
            
            # Voice channels
            await guild.create_voice_channel("📞 Study Lobby", category=study_cat)
            await guild.create_voice_channel("🔇 Quiet Study", category=study_cat)
            
            for i in range(1, 4):
                await guild.create_voice_channel(
                    f"📚 Study Room {i}",
                    category=study_cat
                )
            
            results.append(f"✅ Created Study Space channels")
            
            # Support/Ticket Category
            support_cat = await guild.create_category("🎫 SUPPORT")
            
            # Set permissions so only staff can see
            admin_role = discord.utils.get(guild.roles, name="Admin")
            mod_role = discord.utils.get(guild.roles, name="Moderator")
            helper_role = discord.utils.get(guild.roles, name="Helper")
            
            await support_cat.set_permissions(guild.default_role, view_channel=False)
            if admin_role:
                await support_cat.set_permissions(admin_role, view_channel=True)
            if mod_role:
                await support_cat.set_permissions(mod_role, view_channel=True)
            if helper_role:
                await support_cat.set_permissions(helper_role, view_channel=True)
            
            create_ticket_ch = await guild.create_text_channel(
                "create-ticket",
                category=support_cat,
                topic="React to create a support ticket"
            )
            
            # Make create-ticket visible to everyone
            await create_ticket_ch.set_permissions(
                guild.default_role,
                view_channel=True,
                send_messages=False
            )
            
            results.append(f"✅ Created Support category")
            
            # Staff Category
            staff_cat = await guild.create_category("👥 STAFF")
            await staff_cat.set_permissions(guild.default_role, view_channel=False)
            if admin_role:
                await staff_cat.set_permissions(admin_role, view_channel=True)
            if mod_role:
                await staff_cat.set_permissions(mod_role, view_channel=True)
            
            await guild.create_text_channel(
                "staff-chat",
                category=staff_cat,
                topic="Staff discussion and coordination"
            )
            
            await guild.create_text_channel(
                "mod-logs",
                category=staff_cat,
                topic="Moderation action logs"
            )
            
            bot_commands_ch = await guild.create_text_channel(
                "bot-commands",
                category=staff_cat,
                topic="Use bot admin commands here"
            )
            
            server_logs_ch = await guild.create_text_channel(
                "server-logs",
                category=staff_cat,
                topic="Server event logs"
            )
            
            # Save log channel
            self.dm.set_guild_config(guild.id, 'log_channel_id', server_logs_ch.id)
            
            await guild.create_voice_channel("Staff Room", category=staff_cat)
            
            results.append(f"✅ Created Staff channels")
            
            # === STEP 3: Post Welcome Message ===
            welcome_embed = discord.Embed(
                title="👋 Welcome to UNISA BSc Community!",
                description=(
                    f"Welcome to our community! We're glad to have you here.\n\n"
                    f"**Getting Started:**\n"
                    f"1️⃣ Read the rules in {rules_ch.mention}\n"
                    f"2️⃣ Select your modules in {module_selection_ch.mention}\n"
                    f"3️⃣ Introduce yourself in {introductions_ch.mention}\n"
                    f"4️⃣ Join a study room and start collaborating!\n\n"
                    f"**Need Help?**\n"
                    f"Create a ticket in {create_ticket_ch.mention}\n\n"
                    f"Happy studying! 📚"
                ),
                color=discord.Color.blue()
            )
            welcome_embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
            await welcome_ch.send(embed=welcome_embed)
            results.append(f"✅ Posted welcome message")
            
            # === STEP 4: Post Rules ===
            rules_embed = discord.Embed(
                title="📜 Server Rules",
                description="Please read and follow these rules to maintain a positive learning environment.",
                color=discord.Color.blue()
            )
            
            rules_embed.add_field(
                name="1️⃣ Be Respectful",
                value="Treat all members with respect. No harassment, hate speech, discrimination, or bullying of any kind.",
                inline=False
            )
            
            rules_embed.add_field(
                name="2️⃣ Academic Integrity",
                value="No cheating or sharing of exam answers. Help each other learn and understand, don't just give answers. Plagiarism is not tolerated.",
                inline=False
            )
            
            rules_embed.add_field(
                name="3️⃣ No Spam or Self-Promotion",
                value="Keep conversations relevant. No excessive advertisements, self-promotion, or spam. Ask staff before promoting external content.",
                inline=False
            )
            
            rules_embed.add_field(
                name="4️⃣ Stay On Topic",
                value="Use appropriate channels for discussions. Module channels are for module-specific content only. Keep general chat in community channels.",
                inline=False
            )
            
            rules_embed.add_field(
                name="5️⃣ Use Voice Channels Responsibly",
                value="Voice channels are for studying and collaboration. Keep noise levels appropriate and respect others' learning time.",
                inline=False
            )
            
            rules_embed.add_field(
                name="6️⃣ No NSFW Content",
                value="This is an educational server. No NSFW, explicit, or inappropriate content of any kind.",
                inline=False
            )
            
            rules_embed.add_field(
                name="7️⃣ Listen to Staff",
                value="Follow instructions from Admins, Moderators, and Helpers. They're here to help maintain a positive environment.",
                inline=False
            )
            
            rules_embed.add_field(
                name="8️⃣ Ask Questions!",
                value="Don't hesitate to ask for help! We're all here to learn together. No question is too simple.",
                inline=False
            )
            
            rules_embed.set_footer(text=f"Last updated: {discord.utils.utcnow().strftime('%Y-%m-%d')} • Violating rules may result in warnings, timeouts, or bans")
            
            await rules_ch.send(embed=rules_embed)
            results.append(f"✅ Posted server rules")
            
            # === STEP 5: Setup Ticket System ===
            ticket_embed = discord.Embed(
                title="🎫 Support Tickets",
                description=(
                    "Need help from the staff team? Create a support ticket!\n\n"
                    "**When to create a ticket:**\n"
                    "• Report rule violations or harassment\n"
                    "• Request assistance with technical issues\n"
                    "• Ask questions about the server\n"
                    "• Request module creation\n"
                    "• Other issues requiring staff attention\n\n"
                    "React with 🎫 below to create a ticket."
                ),
                color=discord.Color.green()
            )
            ticket_embed.set_footer(text="A private channel will be created for you and the staff team")
            
            ticket_msg = await create_ticket_ch.send(embed=ticket_embed)
            await ticket_msg.add_reaction("🎫")
            
            # Save ticket message ID
            self.dm.set_guild_config(guild.id, 'ticket_message_id', ticket_msg.id)
            self.dm.set_guild_config(guild.id, 'ticket_channel_id', create_ticket_ch.id)
            self.dm.set_guild_config(guild.id, 'ticket_category_id', support_cat.id)
            
            results.append(f"✅ Setup ticket system")
            
            # === STEP 6: Send Summary ===
            summary = "\n".join(results)
            
            await send_embed(
                ctx,
                title="✅ Server Setup Complete!",
                description=summary,
                color=discord.Color.green(),
                footer="Use !setupreactionroles to enable module selection"
            )
            
            await log_action(
                guild,
                f"🚀 {ctx.author.mention} completed full server setup",
                discord.Color.green()
            )
            
        except discord.Forbidden:
            await send_embed(
                ctx,
                title="❌ Permission Error",
                description="I don't have permission to create channels/roles. Make sure I have Administrator permission.",
                color=discord.Color.red()
            )
        except Exception as e:
            await send_embed(
                ctx,
                title="❌ Setup Failed",
                description=f"Error: {str(e)}\n\nPartially completed:\n" + "\n".join(results),
                color=discord.Color.red()
            )
    
    async def _create_staff_roles(self, guild: discord.Guild):
        """Create staff roles with appropriate permissions"""
        roles_created = []
        
        # Admin role
        admin_role = discord.utils.get(guild.roles, name="Admin")
        if not admin_role:
            admin_role = await guild.create_role(
                name="Admin",
                color=discord.Color.red(),
                permissions=discord.Permissions(
                    administrator=True
                ),
                hoist=True,
                mentionable=True,
                reason="Staff role creation"
            )
            roles_created.append(admin_role)
        
        # Moderator role
        mod_role = discord.utils.get(guild.roles, name="Moderator")
        if not mod_role:
            mod_role = await guild.create_role(
                name="Moderator",
                color=discord.Color.orange(),
                permissions=discord.Permissions(
                    kick_members=True,
                    ban_members=True,
                    manage_messages=True,
                    moderate_members=True,
                    manage_channels=True,
                    view_audit_log=True,
                    read_messages=True,
                    send_messages=True,
                    manage_roles=True
                ),
                hoist=True,
                mentionable=True,
                reason="Staff role creation"
            )
            roles_created.append(mod_role)
        
        # Helper role
        helper_role = discord.utils.get(guild.roles, name="Helper")
        if not helper_role:
            helper_role = await guild.create_role(
                name="Helper",
                color=discord.Color.green(),
                permissions=discord.Permissions(
                    manage_messages=True,
                    read_messages=True,
                    send_messages=True
                ),
                hoist=True,
                mentionable=True,
                reason="Staff role creation"
            )
            roles_created.append(helper_role)
        
        return roles_created
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Handle ticket creation reactions"""
        # Ignore bot reactions
        if payload.user_id == self.bot.user.id:
            return
        
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
        
        # Check if this is the ticket message
        ticket_msg_id = self.dm.get_guild_config_value(guild.id, 'ticket_message_id')
        if not ticket_msg_id or payload.message_id != ticket_msg_id:
            return
        
        # Check if reaction is the ticket emoji
        if str(payload.emoji) != "🎫":
            return
        
        member = guild.get_member(payload.user_id)
        if not member:
            return
        
        # Remove the reaction
        channel = guild.get_channel(payload.channel_id)
        if channel:
            message = await channel.fetch_message(payload.message_id)
            await message.remove_reaction(payload.emoji, member)
        
        # Create ticket
        await self._create_ticket(guild, member)
    
    async def _create_ticket(self, guild: discord.Guild, member: discord.Member):
        """Create a support ticket for a member"""
        # Check if user already has an open ticket
        existing_tickets = self.dm.get_guild_config_value(guild.id, 'open_tickets', {})
        
        if str(member.id) in existing_tickets:
            ticket_ch_id = existing_tickets[str(member.id)]
            ticket_ch = guild.get_channel(ticket_ch_id)
            if ticket_ch:
                try:
                    await member.send(
                        f"❌ You already have an open ticket: {ticket_ch.mention}\n"
                        f"Please use that channel or close it first before creating a new one."
                    )
                except discord.Forbidden:
                    pass
                return
        
        # Get ticket category
        category_id = self.dm.get_guild_config_value(guild.id, 'ticket_category_id')
        category = guild.get_channel(category_id) if category_id else None
        
        # Get ticket number
        ticket_number = self.dm.get_guild_config_value(guild.id, 'ticket_counter', 0) + 1
        self.dm.set_guild_config(guild.id, 'ticket_counter', ticket_number)
        
        # Get staff roles
        admin_role = discord.utils.get(guild.roles, name="Admin")
        mod_role = discord.utils.get(guild.roles, name="Moderator")
        helper_role = discord.utils.get(guild.roles, name="Helper")
        
        # Create ticket channel
        ticket_channel = await guild.create_text_channel(
            f"ticket-{ticket_number:04d}",
            category=category,
            topic=f"Support ticket for {member.display_name}",
            reason=f"Support ticket created by {member}"
        )
        
        # Set permissions
        await ticket_channel.set_permissions(guild.default_role, view_channel=False)
        await ticket_channel.set_permissions(member, view_channel=True, send_messages=True)
        
        if admin_role:
            await ticket_channel.set_permissions(admin_role, view_channel=True)
        if mod_role:
            await ticket_channel.set_permissions(mod_role, view_channel=True)
        if helper_role:
            await ticket_channel.set_permissions(helper_role, view_channel=True)
        
        # Send ticket message
        embed = discord.Embed(
            title=f"🎫 Ticket #{ticket_number:04d}",
            description=(
                f"Welcome {member.mention}!\n\n"
                f"A staff member will be with you shortly. Please describe your issue in detail.\n\n"
                f"To close this ticket, react with 🔒 or use `!closeticket`"
            ),
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Ticket created by {member}")
        
        ticket_msg = await ticket_channel.send(
            content=f"{member.mention} | Staff: {mod_role.mention if mod_role else '@Staff'}",
            embed=embed
        )
        await ticket_msg.add_reaction("🔒")
        
        # Save ticket info
        existing_tickets[str(member.id)] = ticket_channel.id
        self.dm.set_guild_config(guild.id, 'open_tickets', existing_tickets)
        
        # Save ticket message ID
        ticket_data = self.dm.get_guild_config_value(guild.id, 'ticket_messages', {})
        ticket_data[str(ticket_channel.id)] = ticket_msg.id
        self.dm.set_guild_config(guild.id, 'ticket_messages', ticket_data)
        
        # Notify user
        try:
            await member.send(
                f"✅ Your support ticket has been created: {ticket_channel.mention}\n"
                f"A staff member will assist you shortly."
            )
        except discord.Forbidden:
            pass
        
        # Log
        await log_action(
            guild,
            f"🎫 {member.mention} created ticket #{ticket_number:04d}",
            discord.Color.blue()
        )
    
    @commands.command(name="closeticket")
    async def close_ticket(self, ctx):
        """Close a support ticket
        
        Usage: !closeticket
        """
        # Check if this is a ticket channel
        if not ctx.channel.name.startswith("ticket-"):
            await ctx.send("❌ This command can only be used in ticket channels.")
            return
        
        await self._close_ticket_channel(ctx.guild, ctx.channel, ctx.author)
    
    async def _close_ticket_channel(self, guild: discord.Guild, channel: discord.TextChannel, closer: discord.Member):
        """Close a ticket channel"""
        # Find the ticket owner
        open_tickets = self.dm.get_guild_config_value(guild.id, 'open_tickets', {})
        
        ticket_owner_id = None
        for user_id, ch_id in open_tickets.items():
            if ch_id == channel.id:
                ticket_owner_id = int(user_id)
                break
        
        # Send closing message
        embed = discord.Embed(
            title="🔒 Ticket Closed",
            description=f"This ticket has been closed by {closer.mention}",
            color=discord.Color.red()
        )
        await channel.send(embed=embed)
        
        # Remove from open tickets
        if ticket_owner_id:
            del open_tickets[str(ticket_owner_id)]
            self.dm.set_guild_config(guild.id, 'open_tickets', open_tickets)
        
        # Delete channel after 5 seconds
        await channel.delete(delay=5, reason=f"Ticket closed by {closer}")
        
        # Notify user
        if ticket_owner_id:
            member = guild.get_member(ticket_owner_id)
            if member:
                try:
                    await member.send(
                        f"🔒 Your support ticket in **{guild.name}** has been closed by {closer.display_name}.\n"
                        f"If you need further assistance, feel free to create a new ticket."
                    )
                except discord.Forbidden:
                    pass
        
        # Log
        await log_action(
            guild,
            f"🔒 {closer.mention} closed ticket: {channel.name}",
            discord.Color.orange()
        )


async def setup(bot):
    await bot.add_cog(ServerSetup(bot))