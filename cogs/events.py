import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from utils.data_manager import DataManager
from utils.helpers import is_admin, log_action, send_embed, format_list


class Events(commands.Cog):
    """Event scheduling and management commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.dm = DataManager()
        self.reminder_task.start()
    
    def cog_unload(self):
        self.reminder_task.cancel()
    
    @commands.command(name="addevent")
    @is_admin()
    async def add_event(self, ctx, module: str, date: str, *, description: str):
        """Add an event for a module
        
        Usage: !addevent COS1501 2024-06-15 Assignment 1 Due
        Date format: YYYY-MM-DD
        """
        module = module.upper()
        
        # Validate date format
        try:
            event_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            await send_embed(
                ctx,
                title="❌ Invalid Date",
                description="Date must be in format: YYYY-MM-DD\nExample: 2024-06-15",
                color=discord.Color.red()
            )
            return
        
        # Check if module exists
        if not self.dm.module_exists(module):
            await send_embed(
                ctx,
                title="⚠️ Warning",
                description=f"Module **{module}** doesn't exist, but event will be created anyway.",
                color=discord.Color.orange()
            )
        
        # Add event
        event_key = self.dm.add_event(module, date, description)
        
        await send_embed(
            ctx,
            title="✅ Event Added",
            description=f"**{module}** - {description}",
            fields=[
                {'name': 'Date', 'value': date, 'inline': True},
                {'name': 'Days Until', 'value': str((event_date - datetime.now()).days), 'inline': True}
            ],
            color=discord.Color.green()
        )
        
        await log_action(
            ctx.guild,
            f"📅 {ctx.author.mention} added event: **{module}** on {date}",
            discord.Color.blue()
        )
    
    @commands.command(name="events", aliases=["schedule"])
    async def list_events(self, ctx, module: str = None):
        """List all events or events for a specific module
        
        Usage: !events [module]
        """
        events = self.dm.get_events(module)
        
        if not events:
            msg = f"No events found for **{module.upper()}**." if module else "No events scheduled."
            await send_embed(
                ctx,
                title="📅 Events",
                description=msg,
                color=discord.Color.blue()
            )
            return
        
        # Sort by date
        sorted_events = sorted(
            events.items(),
            key=lambda x: x[1].get('date', '9999-99-99')
        )
        
        # Group by upcoming/past
        now = datetime.now()
        upcoming = []
        past = []
        
        for key, event in sorted_events:
            try:
                event_date = datetime.strptime(event['date'], "%Y-%m-%d")
                days_until = (event_date - now).days
                
                event_str = f"**{event['module']}** - {event['date']}\n{event['description']}"
                
                if days_until >= 0:
                    if days_until == 0:
                        event_str += " 🔴 **TODAY**"
                    elif days_until <= 7:
                        event_str += f" ⚠️ **{days_until} days**"
                    else:
                        event_str += f" ({days_until} days)"
                    upcoming.append(event_str)
                else:
                    past.append(event_str)
                    
            except ValueError:
                upcoming.append(f"**{event['module']}** - {event['date']}\n{event['description']}")
        
        fields = []
        
        if upcoming:
            fields.append({
                'name': '📅 Upcoming Events',
                'value': '\n\n'.join(upcoming[:10]),
                'inline': False
            })
        
        if past and len(upcoming) < 5:
            fields.append({
                'name': '📋 Past Events',
                'value': '\n\n'.join(past[:5]),
                'inline': False
            })
        
        title = f"📅 Events for {module.upper()}" if module else "📅 All Events"
        
        await send_embed(
            ctx,
            title=title,
            fields=fields,
            color=discord.Color.blue(),
            footer=f"Total: {len(events)} events"
        )
    
    @commands.command(name="delevent", aliases=["removeevent"])
    @is_admin()
    async def delete_event(self, ctx, module: str, date: str):
        """Delete an event
        
        Usage: !delevent COS1501 2024-06-15
        """
        module = module.upper()
        event_key = self.dm.find_event(module, date)
        
        if not event_key:
            await send_embed(
                ctx,
                title="❌ Not Found",
                description=f"No event found for **{module}** on {date}.",
                color=discord.Color.red()
            )
            return
        
        if self.dm.remove_event(event_key):
            await send_embed(
                ctx,
                title="✅ Event Deleted",
                description=f"Event for **{module}** on {date} has been deleted.",
                color=discord.Color.green()
            )
            
            await log_action(
                ctx.guild,
                f"🗑️ {ctx.author.mention} deleted event: **{module}** on {date}",
                discord.Color.orange()
            )
        else:
            await send_embed(
                ctx,
                title="❌ Delete Failed",
                description="Failed to delete the event.",
                color=discord.Color.red()
            )
    
    @commands.command(name="upcomingevents", aliases=["upcoming"])
    async def upcoming_events(self, ctx, days: int = 7):
        """Show events coming up in the next X days
        
        Usage: !upcoming [days]
        """
        if days < 1 or days > 365:
            await send_embed(
                ctx,
                title="❌ Invalid Range",
                description="Days must be between 1 and 365.",
                color=discord.Color.red()
            )
            return
        
        all_events = self.dm.get_events()
        now = datetime.now()
        cutoff = now + timedelta(days=days)
        
        upcoming = []
        for key, event in all_events.items():
            try:
                event_date = datetime.strptime(event['date'], "%Y-%m-%d")
                
                if now <= event_date <= cutoff:
                    days_until = (event_date - now).days
                    
                    urgency = ""
                    if days_until == 0:
                        urgency = " 🔴 **TODAY**"
                    elif days_until == 1:
                        urgency = " ⚠️ **TOMORROW**"
                    elif days_until <= 3:
                        urgency = f" ⚠️ **{days_until} days**"
                    else:
                        urgency = f" ({days_until} days)"
                    
                    upcoming.append({
                        'date': event_date,
                        'text': f"**{event['module']}** - {event['date']}{urgency}\n{event['description']}"
                    })
            except ValueError:
                continue
        
        if not upcoming:
            await send_embed(
                ctx,
                title="📅 Upcoming Events",
                description=f"No events in the next {days} days.",
                color=discord.Color.blue()
            )
            return
        
        # Sort by date
        upcoming.sort(key=lambda x: x['date'])
        
        event_list = '\n\n'.join([e['text'] for e in upcoming])
        
        await send_embed(
            ctx,
            title=f"📅 Events in Next {days} Days",
            description=event_list,
            color=discord.Color.blue(),
            footer=f"{len(upcoming)} upcoming events"
        )
    
    @tasks.loop(hours=24)
    async def reminder_task(self):
        """Daily task to send event reminders"""
        now = datetime.now()
        
        for guild in self.bot.guilds:
            announcements = discord.utils.get(guild.text_channels, name="announcements")
            if not announcements:
                continue
            
            all_events = self.dm.get_events()
            today_events = []
            tomorrow_events = []
            week_events = []
            
            for key, event in all_events.items():
                try:
                    event_date = datetime.strptime(event['date'], "%Y-%m-%d")
                    days_until = (event_date - now).days
                    
                    if days_until == 0:
                        today_events.append(event)
                    elif days_until == 1:
                        tomorrow_events.append(event)
                    elif days_until == 7:
                        week_events.append(event)
                        
                except ValueError:
                    continue
            
            # Send reminders
            if today_events:
                events_text = '\n'.join([f"• **{e['module']}**: {e['description']}" for e in today_events])
                await announcements.send(
                    f"🔴 **Events TODAY:**\n{events_text}"
                )
            
            if tomorrow_events:
                events_text = '\n'.join([f"• **{e['module']}**: {e['description']}" for e in tomorrow_events])
                await announcements.send(
                    f"⚠️ **Events TOMORROW:**\n{events_text}"
                )
            
            if week_events:
                events_text = '\n'.join([f"• **{e['module']}**: {e['description']}" for e in week_events])
                await announcements.send(
                    f"📅 **Events in 1 week:**\n{events_text}"
                )
    
    @reminder_task.before_loop
    async def before_reminder_task(self):
        """Wait until bot is ready"""
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Events(bot))