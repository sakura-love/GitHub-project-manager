"""
Configuration and Credentials Management
Securely stores GitHub credentials and app settings
"""

import json
import os
from pathlib import Path
from cryptography.fernet import Fernet
import keyring
from typing import Optional, Dict, Any

class ConfigManager:
    """Manages application configuration and credentials"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".github_project_manager"
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / "config.json"
        self.credentials_key = "github_project_manager"
        
    def get_github_token(self) -> Optional[str]:
        """Retrieve GitHub token from secure storage"""
        try:
            token = keyring.get_password(self.credentials_key, "github_token")
            return token
        except Exception as e:
            print(f"Error retrieving token: {e}")
            return None
    
    def save_github_token(self, token: str) -> bool:
        """Save GitHub token to secure storage"""
        try:
            keyring.set_password(self.credentials_key, "github_token", token)
            return True
        except Exception as e:
            print(f"Error saving token: {e}")
            return False
    
    def get_github_username(self) -> Optional[str]:
        """Retrieve stored GitHub username"""
        try:
            config = self._load_config()
            return config.get("github_username")
        except Exception:
            return None
    
    def save_github_username(self, username: str) -> bool:
        """Save GitHub username"""
        try:
            config = self._load_config()
            config["github_username"] = username
            self._save_config(config)
            return True
        except Exception as e:
            print(f"Error saving username: {e}")
            return False
    
    def get_projects_directory(self) -> Path:
        """Get or set the default projects directory"""
        config = self._load_config()
        projects_dir = config.get("projects_directory", str(Path.home() / "github_projects"))
        projects_path = Path(projects_dir)
        projects_path.mkdir(parents=True, exist_ok=True)
        return projects_path
    
    def set_projects_directory(self, directory: str) -> bool:
        """Set the projects directory"""
        try:
            config = self._load_config()
            config["projects_directory"] = directory
            self._save_config(config)
            Path(directory).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error setting projects directory: {e}")
            return False

    def get_theme_mode(self) -> str:
        """Get UI theme mode: 'light' or 'dark'"""
        config = self._load_config()
        theme = config.get("theme_mode", "light")
        return theme if theme in {"light", "dark"} else "light"

    def set_theme_mode(self, mode: str) -> bool:
        """Set UI theme mode"""
        if mode not in {"light", "dark"}:
            return False
        try:
            config = self._load_config()
            config["theme_mode"] = mode
            self._save_config(config)
            return True
        except Exception as e:
            print(f"Error setting theme mode: {e}")
            return False
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def clear_credentials(self) -> bool:
        """Clear stored credentials"""
        try:
            keyring.delete_password(self.credentials_key, "github_token")
            config = self._load_config()
            config.pop("github_username", None)
            self._save_config(config)
            return True
        except Exception as e:
            print(f"Error clearing credentials: {e}")
            return False
