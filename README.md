# UNISA BSc Community Discord Bot

A comprehensive Discord bot designed for managing UNISA BSc community servers with module management, event scheduling, reaction roles, ticketing system, and administrative features.

## Features

### 📚 Module Management
- Create module-specific channels and roles
- Automatic channel structure (general, resources, schedule, questions)
- Private module categories with role-based access
- Join/leave modules dynamically
- List all available modules

### 📅 Event System
- Schedule module-specific events
- Automated daily reminders
- View upcoming events
- Track deadlines and assignments
- Event notifications for today, tomorrow, and next week

### 👥 Administration
- Role-based permission system
- Bot owner and admin management
- Server initialization with predefined structure
- Comprehensive logging system

### 🛡️ Moderation
- Message clearing/purging
- Member kick/ban/unban
- Timeout (mute) system
- Server rules setup

### 🔧 Utilities
- Server and user information
- Bot statistics and uptime
- Ping/latency checking
- Custom announcements
- Track user modules

### 🎭 Reaction Roles
- Automatic module selection via reactions
- Beautiful embedded module list
- Auto-assigns roles when users react
- Removes roles when reactions are removed
- DM confirmation for joins/leaves
- Supports up to 40 modules with multiple messages

### 🎫 Support Ticket System
- React to create private support tickets
- Automatic ticket channel creation
- Staff-only visibility with proper permissions
- Close tickets with reaction or command
- DM notifications for users
- Ticket numbering system

### 🚀 Complete Server Setup
- One-command full server initialization
- Creates all necessary roles (Admin, Moderator, Helper)
- Organized category structure
- Staff-only channels with proper permissions
- Welcome and rules messages
- Automatic logging setup

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- A Discord bot token

### Setup Instructions

1. **Clone or download the repository**
```bash
git clone <repository-url>
cd discord-bot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**

Create a `.env` file in the root directory:
```env
DISCORD_TOKEN=your_bot_token_here
OWNER_USERNAME=YourUsername#1234
LOG_CHANNEL_NAME=server-logs
```

4. **Create necessary directories**
```bash
mkdir -p data cogs utils
```

5. **Run the bot**
```bash
python bot.py
```

## Project Structure

```
discord-bot/
├── bot.py                 # Main bot file
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── .env.example          # Example environment file
├── .gitignore            # Git ignore rules
├── data/                 # Data storage (auto-created)
│   ├── admins.json
│   ├── modules.json
│   ├── events.json
│   ├── guild_config.json
│   └── user_stats.json
├── cogs/                 # Command modules
│   ├── admin.py          # Admin commands
│   ├── modules.py        # Module management
│   ├── events.py         # Event system
│   ├── utilities.py      # Utility commands
│   └── moderation.py     # Moderation commands
└── utils/                # Helper modules
    ├── helpers.py        # Utility functions
    └── data_manager.py   # Data management class
```

## Commands

### 🔧 General Commands
- `!ping` - Check bot latency
- `!info` - Display bot information
- `!serverinfo` - Display server information
- `!userinfo [@user]` - Display user information
- `!mymodules` - List your enrolled modules
- `!help [command]` - Show help information

### 📚 Module Commands
- `!createmod <code> [name]` - Create a new module (Admin)
- `!deletemod <code> confirm` - Delete a module (Admin)
- `!modules` - List all modules
- `!joinmodule <code>` - Join a module
- `!leavemodule <code>` - Leave a module

### 📅 Event Commands
- `!addevent <module> <date> <description>` - Add an event (Admin)
- `!events [module]` - List events
- `!delevent <module> <date>` - Delete an event (Admin)
- `!upcoming [days]` - Show upcoming events

### 👥 Admin Commands
- `!addadmin <username>` - Add bot admin (Owner only)
- `!removeadmin <username>` - Remove bot admin (Owner only)
- `!listadmins` - List all admins
- `!sync` - Sync application commands (Owner only)
- `!reload <cog>` - Reload a cog (Owner only)
- `!shutdown` - Shutdown the bot (Owner only)

### 🛡️ Moderation Commands
- `!setrules` - Initialize server structure (Admin)
- `!clear [amount]` - Clear messages (requires Manage Messages)
- `!kick @member [reason]` - Kick a member (requires Kick Members)
- `!ban @member [reason]` - Ban a member (requires Ban Members)
- `!unban <user_id>` - Unban a member (requires Ban Members)
- `!mute @member [minutes] [reason]` - Timeout a member (requires Moderate Members)
- `!unmute @member` - Remove timeout (requires Moderate Members)
- `!announce #channel <message>` - Send announcement (requires Manage Messages)

### Owner Only
- `!fullsetup` - Complete server initialization
- `!setupreactionroles` - Enable reaction roles for modules
- `!syncreactionroles` - Sync reaction roles with modules

### Ticket System
- React 🎫 in #create-ticket to open ticket
- `!closeticket` or react 🔒 to close ticket

## Bot Permissions

The bot requires the following permissions:
- Manage Roles
- Manage Channels
- Kick Members
- Ban Members
- Moderate Members (Timeout)
- Manage Messages
- Send Messages
- Embed Links
- Attach Files
- Read Message History
- Add Reactions
- Connect (Voice)
- Speak (Voice)

### Permission Integer
Use this permission integer when inviting the bot: `8` (Administrator) or calculate specific permissions at [Discord Permissions Calculator](https://discordapi.com/permissions.html)

## Invite Link

```
https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_CLIENT_ID&permissions=8&scope=bot%20applications.commands
```

Replace `YOUR_BOT_CLIENT_ID` with your bot's client ID.

## Server Setup

After inviting the bot:

1. **Initialize the server structure**
```
!setrules
```
This creates:
- Community Hub category with welcome, rules, announcements, general-chat, faq, events-schedule
- Study Spaces category with group-finder, exam-prep, math-help, programming-help
- Voice channels for studying

2. **Create your first module**
```
!createmod COS1501 Introduction to Programming
```

3. **Add an event**
```
!addevent COS1501 2024-06-15 Assignment 1 Due
```

4. **Users can join modules**
```
!joinmodule COS1501
```

5. **Setup Reaction Roles**
```
!setupreactionroles
```


## Features Explained

### Module System
- Each module gets its own category with restricted access
- Only users with the module role can see the channels
- Includes text channels for discussion, resources, schedule, and questions
- Includes 3 voice channels for study sessions

### Event Reminders
The bot automatically sends daily reminders at midnight for:
- Events happening today
- Events happening tomorrow
- Events happening in 7 days

### Data Persistence
All data is stored in JSON files in the `data/` directory:
- `admins.json` - Bot administrators
- `modules.json` - Module information
- `events.json` - Scheduled events
- `guild_config.json` - Server-specific configuration
- `user_stats.json` - User statistics and module enrollment

### Logging System
All administrative actions are logged to a dedicated log channel, including:
- Module creation/deletion
- Admin changes
- Event management
- Moderation actions

## Customization

### Adding New Commands
Create a new command in the appropriate cog:

```python
@commands.command(name="mycommand")
async def my_command(self, ctx):
    """Command description"""
    await ctx.send("Hello!")
```

### Modifying Server Structure
Edit the `setrules` command in `cogs/moderation.py` to customize:
- Category names
- Channel names and topics
- Default permissions

### Changing Reminder Schedule
Edit the `@tasks.loop()` decorator in `cogs/events.py`:
```python
@tasks.loop(hours=24)  # Change this value
```

## Troubleshooting

### Bot doesn't respond
- Check if the bot is online in the server
- Verify the bot has necessary permissions
- Check the console for error messages
- Ensure the `.env` file is configured correctly

### Commands not working
- Verify you have the required permissions
- Check if you're using the correct command prefix (`!`)
- Try `!help` to see available commands

### Module creation fails
- Ensure the bot has "Manage Roles" and "Manage Channels" permissions
- Check if there are too many roles/channels (Discord limits)
- Verify the module doesn't already exist

## Support

For issues or questions:
1. Check the command help with `!help <command>`
2. Review the bot logs in `bot.log`
3. Check the server log channel for error messages

## Development

### Running in Development Mode
```bash
python bot.py
```

### Testing
Test commands in a development server first before deploying to production.

### Contributing
1. Create a new branch for your feature
2. Test thoroughly
3. Submit a pull request with detailed description

## License

This project is provided as-is for educational purposes.

## Credits

Built for the UNISA BSc Community
Powered by discord.py

---

**Version:** 2.0
**Last Updated:** 2024