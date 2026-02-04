import discord
from discord.ext import commands
from utils.helpers import is_admin, log_action, send_embed


class Moderation(commands.Cog):
    """Moderation and server setup commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="setrules")
    @is_admin()
    async def setup_server(self, ctx):
        """Initialize server with channels and categories
        
        Usage: !setrules
        """
        guild = ctx.guild
        
        await ctx.send("🔄 Setting up server structure...")
        
        try:
            # Create Community Hub
            hub = await guild.create_category("📚 Community Hub")
            
            await guild.create_text_channel(
                "welcome",
                category=hub,
                topic="Welcome to UNISA BSc Community!"
            )
            
            rules_channel = await guild.create_text_channel(
                "rules",
                category=hub,
                topic="Server rules and guidelines"
            )
            
            await guild.create_text_channel(
                "announcements",
                category=hub,
                topic="Important announcements"
            )
            
            await guild.create_text_channel(
                "general-chat",
                category=hub,
                topic="General discussion"
            )
            
            await guild.create_text_channel(
                "faq",
                category=hub,
                topic="Frequently asked questions"
            )
            
            await guild.create_text_channel(
                "events-schedule",
                category=hub,
                topic="Upcoming events and deadlines"
            )
            
            # Voice channels
            await guild.create_voice_channel("📞 Study Lobby", category=hub)
            await guild.create_voice_channel("🔇 Quiet Study", category=hub)
            
            # Study Spaces
            study = await guild.create_category("📖 Study Spaces")
            
            await guild.create_text_channel(
                "group-finder",
                category=study,
                topic="Find study partners"
            )
            
            await guild.create_text_channel(
                "exam-prep",
                category=study,
                topic="Exam preparation and tips"
            )
            
            await guild.create_text_channel(
                "math-help",
                category=study,
                topic="Mathematics help and discussion"
            )
            
            await guild.create_text_channel(
                "programming-help",
                category=study,
                topic="Programming help and code review"
            )
            
            # Study voice rooms
            for i in range(1, 4):
                await guild.create_voice_channel(
                    f"📚 Study Room {i}",
                    category=study
                )
            
            # Post rules
            rules_embed = discord.Embed(
                title="📜 UNISA BSc Community Rules",
                description="Please read and follow these rules to maintain a positive learning environment.",
                color=discord.Color.blue()
            )
            
            rules_embed.add_field(
                name="1️⃣ Be Respectful",
                value="Treat all members with respect. No harassment, hate speech, or discrimination.",
                inline=False
            )
            
            rules_embed.add_field(
                name="2️⃣ Academic Integrity",
                value="No cheating or sharing of exam answers. Help each other learn, don't just give answers.",
                inline=False
            )
            
            rules_embed.add_field(
                name="3️⃣ No Spam",
                value="Keep conversations relevant. No excessive advertisements or self-promotion.",
                inline=False
            )
            
            rules_embed.add_field(
                name="4️⃣ Stay On Topic",
                value="Use module channels for module-specific discussions. Use general channels for everything else.",
                inline=False
            )
            
            rules_embed.add_field(
                name="5️⃣ Use Study Rooms Responsibly",
                value="Voice channels are for studying and collaboration. Keep noise levels appropriate.",
                inline=False
            )
            
            rules_embed.add_field(
                name="6️⃣ Ask Questions",
                value="Don't hesitate to ask for help! We're all here to learn together.",
                inline=False
            )
            
            rules_embed.set_footer(text="Last updated: " + discord.utils.utcnow().strftime("%Y-%m-%d"))
            
            await rules_channel.send(embed=rules_embed)
            
            await send_embed(
                ctx,
                title="✅ Server Initialized",
                description="Server structure has been created successfully!",
                fields=[
                    {'name': 'Categories', 'value': '2', 'inline': True},
                    {'name': 'Text Channels', 'value': '10', 'inline': True},
                    {'name': 'Voice Channels', 'value': '5', 'inline': True}
                ],
                color=discord.Color.green()
            )
            
            await log_action(
                guild,
                f"✅ Server initialized by {ctx.author.mention}",
                discord.Color.green()
            )
            
        except discord.Forbidden:
            await send_embed(
                ctx,
                title="❌ Permission Error",
                description="I don't have permission to create channels/categories.",
                color=discord.Color.red()
            )
        except Exception as e:
            await send_embed(
                ctx,
                title="❌ Setup Failed",
                description=f"Error: {str(e)}",
                color=discord.Color.red()
            )
    
    @commands.command(name="clear", aliases=["purge"])
    @commands.has_permissions(manage_messages=True)
    async def clear_messages(self, ctx, amount: int = 10):
        """Clear messages from a channel
        
        Usage: !clear [amount]
        """
        if amount < 1 or amount > 100:
            await send_embed(
                ctx,
                title="❌ Invalid Amount",
                description="Amount must be between 1 and 100.",
                color=discord.Color.red()
            )
            return
        
        try:
            deleted = await ctx.channel.purge(limit=amount + 1)  # +1 for command message
            
            msg = await ctx.send(f"✅ Deleted {len(deleted) - 1} messages.")
            await msg.delete(delay=3)
            
            await log_action(
                ctx.guild,
                f"🗑️ {ctx.author.mention} cleared {len(deleted) - 1} messages from {ctx.channel.mention}",
                discord.Color.orange()
            )
            
        except discord.Forbidden:
            await send_embed(
                ctx,
                title="❌ Permission Error",
                description="I don't have permission to delete messages.",
                color=discord.Color.red()
            )
    
    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick_member(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        """Kick a member from the server
        
        Usage: !kick @member [reason]
        """
        if member.top_role >= ctx.author.top_role:
            await send_embed(
                ctx,
                title="❌ Permission Error",
                description="You cannot kick someone with equal or higher role.",
                color=discord.Color.red()
            )
            return
        
        try:
            await member.kick(reason=f"{ctx.author}: {reason}")
            
            await send_embed(
                ctx,
                title="✅ Member Kicked",
                description=f"**{member}** has been kicked.",
                fields=[
                    {'name': 'Reason', 'value': reason, 'inline': False}
                ],
                color=discord.Color.orange()
            )
            
            await log_action(
                ctx.guild,
                f"👢 {ctx.author.mention} kicked **{member}**\nReason: {reason}",
                discord.Color.orange()
            )
            
        except discord.Forbidden:
            await send_embed(
                ctx,
                title="❌ Permission Error",
                description="I don't have permission to kick members.",
                color=discord.Color.red()
            )
    
    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban_member(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        """Ban a member from the server
        
        Usage: !ban @member [reason]
        """
        if member.top_role >= ctx.author.top_role:
            await send_embed(
                ctx,
                title="❌ Permission Error",
                description="You cannot ban someone with equal or higher role.",
                color=discord.Color.red()
            )
            return
        
        try:
            await member.ban(reason=f"{ctx.author}: {reason}")
            
            await send_embed(
                ctx,
                title="✅ Member Banned",
                description=f"**{member}** has been banned.",
                fields=[
                    {'name': 'Reason', 'value': reason, 'inline': False}
                ],
                color=discord.Color.red()
            )
            
            await log_action(
                ctx.guild,
                f"🔨 {ctx.author.mention} banned **{member}**\nReason: {reason}",
                discord.Color.red()
            )
            
        except discord.Forbidden:
            await send_embed(
                ctx,
                title="❌ Permission Error",
                description="I don't have permission to ban members.",
                color=discord.Color.red()
            )
    
    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban_member(self, ctx, user_id: int):
        """Unban a member by their user ID
        
        Usage: !unban <user_id>
        """
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user)
            
            await send_embed(
                ctx,
                title="✅ Member Unbanned",
                description=f"**{user}** has been unbanned.",
                color=discord.Color.green()
            )
            
            await log_action(
                ctx.guild,
                f"✅ {ctx.author.mention} unbanned **{user}**",
                discord.Color.green()
            )
            
        except discord.NotFound:
            await send_embed(
                ctx,
                title="❌ Not Found",
                description="User not found or not banned.",
                color=discord.Color.red()
            )
        except discord.Forbidden:
            await send_embed(
                ctx,
                title="❌ Permission Error",
                description="I don't have permission to unban members.",
                color=discord.Color.red()
            )
    
    @commands.command(name="mute")
    @commands.has_permissions(moderate_members=True)
    async def mute_member(self, ctx, member: discord.Member, duration: int = 60, *, reason: str = "No reason provided"):
        """Timeout a member
        
        Usage: !mute @member [duration_minutes] [reason]
        """
        if member.top_role >= ctx.author.top_role:
            await send_embed(
                ctx,
                title="❌ Permission Error",
                description="You cannot mute someone with equal or higher role.",
                color=discord.Color.red()
            )
            return
        
        try:
            from datetime import timedelta
            
            await member.timeout(
                timedelta(minutes=duration),
                reason=f"{ctx.author}: {reason}"
            )
            
            await send_embed(
                ctx,
                title="✅ Member Muted",
                description=f"**{member.display_name}** has been muted.",
                fields=[
                    {'name': 'Duration', 'value': f"{duration} minutes", 'inline': True},
                    {'name': 'Reason', 'value': reason, 'inline': False}
                ],
                color=discord.Color.orange()
            )
            
            await log_action(
                ctx.guild,
                f"🔇 {ctx.author.mention} muted **{member}** for {duration} minutes\nReason: {reason}",
                discord.Color.orange()
            )
            
        except discord.Forbidden:
            await send_embed(
                ctx,
                title="❌ Permission Error",
                description="I don't have permission to timeout members.",
                color=discord.Color.red()
            )
    
    @commands.command(name="unmute")
    @commands.has_permissions(moderate_members=True)
    async def unmute_member(self, ctx, member: discord.Member):
        """Remove timeout from a member
        
        Usage: !unmute @member
        """
        try:
            await member.timeout(None)
            
            await send_embed(
                ctx,
                title="✅ Member Unmuted",
                description=f"**{member.display_name}** has been unmuted.",
                color=discord.Color.green()
            )
            
            await log_action(
                ctx.guild,
                f"🔊 {ctx.author.mention} unmuted **{member}**",
                discord.Color.green()
            )
            
        except discord.Forbidden:
            await send_embed(
                ctx,
                title="❌ Permission Error",
                description="I don't have permission to remove timeouts.",
                color=discord.Color.red()
            )


async def setup(bot):
    await bot.add_cog(Moderation(bot))