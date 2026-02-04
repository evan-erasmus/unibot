import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from utils.helpers import load_json, save_json, DATA_DIR

OWNER = os.getenv("OWNER_USERNAME")


class DataManager:
    """Centralized data management for the bot"""
    
    ADMINS_FILE = f"{DATA_DIR}/admins.json"
    MODULES_FILE = f"{DATA_DIR}/modules.json"
    EVENTS_FILE = f"{DATA_DIR}/events.json"
    GUILD_CONFIG_FILE = f"{DATA_DIR}/guild_config.json"
    USER_STATS_FILE = f"{DATA_DIR}/user_stats.json"
    
    def __init__(self):
        self._ensure_files()
    
    def _ensure_files(self):
        """Ensure all data files exist"""
        os.makedirs(DATA_DIR, exist_ok=True)
    
    # ==================== ADMINS ====================
    
    def get_admins(self) -> List[str]:
        """Get list of bot admins"""
        return load_json(self.ADMINS_FILE, [OWNER])
    
    def add_admin(self, username: str) -> bool:
        """Add an admin"""
        admins = self.get_admins()
        if username not in admins:
            admins.append(username)
            return save_json(self.ADMINS_FILE, admins)
        return False
    
    def remove_admin(self, username: str) -> bool:
        """Remove an admin (cannot remove owner)"""
        if username == OWNER:
            return False
        
        admins = self.get_admins()
        if username in admins:
            admins.remove(username)
            return save_json(self.ADMINS_FILE, admins)
        return False
    
    def is_admin(self, username: str) -> bool:
        """Check if user is admin"""
        return username in self.get_admins()
    
    # ==================== MODULES ====================
    
    def get_modules(self) -> Dict[str, Any]:
        """Get all modules"""
        return load_json(self.MODULES_FILE, {})
    
    def get_module(self, code: str) -> Optional[Dict[str, Any]]:
        """Get a specific module"""
        modules = self.get_modules()
        return modules.get(code.upper())
    
    def add_module(self, code: str, data: Dict[str, Any] = None) -> bool:
        """Add a new module"""
        modules = self.get_modules()
        code = code.upper()
        
        if code in modules:
            return False
        
        if data is None:
            data = {}
        
        data['created'] = str(datetime.utcnow())
        modules[code] = data
        return save_json(self.MODULES_FILE, modules)
    
    def remove_module(self, code: str) -> bool:
        """Remove a module"""
        modules = self.get_modules()
        code = code.upper()
        
        if code in modules:
            del modules[code]
            return save_json(self.MODULES_FILE, modules)
        return False
    
    def update_module(self, code: str, data: Dict[str, Any]) -> bool:
        """Update module data"""
        modules = self.get_modules()
        code = code.upper()
        
        if code not in modules:
            return False
        
        modules[code].update(data)
        return save_json(self.MODULES_FILE, modules)
    
    def module_exists(self, code: str) -> bool:
        """Check if module exists"""
        return code.upper() in self.get_modules()
    
    # ==================== EVENTS ====================
    
    def get_events(self, module: str = None) -> Dict[str, Any]:
        """Get all events or events for a specific module"""
        all_events = load_json(self.EVENTS_FILE, {})
        
        if module:
            module = module.upper()
            return {k: v for k, v in all_events.items() if v.get('module') == module}
        
        return all_events
    
    def add_event(self, module: str, date: str, description: str, **kwargs) -> str:
        """Add an event and return its key"""
        events = load_json(self.EVENTS_FILE, {})
        module = module.upper()
        
        key = f"{module}::{date}::{len(events)}"
        
        events[key] = {
            'module': module,
            'date': date,
            'description': description,
            'created': str(datetime.utcnow()),
            **kwargs
        }
        
        save_json(self.EVENTS_FILE, events)
        return key
    
    def remove_event(self, key: str) -> bool:
        """Remove an event by key"""
        events = load_json(self.EVENTS_FILE, {})
        
        if key in events:
            del events[key]
            return save_json(self.EVENTS_FILE, events)
        return False
    
    def find_event(self, module: str, date: str) -> Optional[str]:
        """Find event key by module and date"""
        events = load_json(self.EVENTS_FILE, {})
        module = module.upper()
        
        for key, event in events.items():
            if event.get('module') == module and event.get('date') == date:
                return key
        return None
    
    # ==================== GUILD CONFIG ====================
    
    def get_guild_config(self, guild_id: int) -> Dict[str, Any]:
        """Get configuration for a guild"""
        all_configs = load_json(self.GUILD_CONFIG_FILE, {})
        return all_configs.get(str(guild_id), {})
    
    def set_guild_config(self, guild_id: int, key: str, value: Any) -> bool:
        """Set a configuration value for a guild"""
        all_configs = load_json(self.GUILD_CONFIG_FILE, {})
        guild_id = str(guild_id)
        
        if guild_id not in all_configs:
            all_configs[guild_id] = {}
        
        all_configs[guild_id][key] = value
        return save_json(self.GUILD_CONFIG_FILE, all_configs)
    
    def get_guild_config_value(self, guild_id: int, key: str, default: Any = None) -> Any:
        """Get a specific config value for a guild"""
        config = self.get_guild_config(guild_id)
        return config.get(key, default)
    
    # ==================== USER STATS ====================
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get stats for a user"""
        all_stats = load_json(self.USER_STATS_FILE, {})
        return all_stats.get(str(user_id), {
            'messages': 0,
            'commands_used': 0,
            'joined_at': None,
            'modules': []
        })
    
    def update_user_stat(self, user_id: int, key: str, value: Any) -> bool:
        """Update a user stat"""
        all_stats = load_json(self.USER_STATS_FILE, {})
        user_id = str(user_id)
        
        if user_id not in all_stats:
            all_stats[user_id] = self.get_user_stats(int(user_id))
        
        all_stats[user_id][key] = value
        return save_json(self.USER_STATS_FILE, all_stats)
    
    def increment_user_stat(self, user_id: int, key: str, amount: int = 1) -> bool:
        """Increment a numeric user stat"""
        all_stats = load_json(self.USER_STATS_FILE, {})
        user_id = str(user_id)
        
        if user_id not in all_stats:
            all_stats[user_id] = self.get_user_stats(int(user_id))
        
        current = all_stats[user_id].get(key, 0)
        all_stats[user_id][key] = current + amount
        return save_json(self.USER_STATS_FILE, all_stats)
    
    def add_user_module(self, user_id: int, module: str) -> bool:
        """Add a module to user's list"""
        all_stats = load_json(self.USER_STATS_FILE, {})
        user_id = str(user_id)
        module = module.upper()
        
        if user_id not in all_stats:
            all_stats[user_id] = self.get_user_stats(int(user_id))
        
        if 'modules' not in all_stats[user_id]:
            all_stats[user_id]['modules'] = []
        
        if module not in all_stats[user_id]['modules']:
            all_stats[user_id]['modules'].append(module)
            return save_json(self.USER_STATS_FILE, all_stats)
        
        return False