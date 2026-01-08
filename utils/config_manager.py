"""
Configuration Manager for Wasteless Backend
Manages reading and writing to config/remediation.yaml
"""

import os
import yaml
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Path to backend config file
BACKEND_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    '..', '..',
    'wasteless'
))
CONFIG_PATH = os.path.join(BACKEND_PATH, 'config', 'remediation.yaml')


class ConfigManager:
    """Manages backend configuration file"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize config manager.

        Args:
            config_path: Optional path to config file. Uses default if not provided.
        """
        self.config_path = config_path or CONFIG_PATH
        self._config_cache = None

    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file.

        Returns:
            Dict containing configuration

        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If YAML is invalid
        """
        try:
            with open(self.config_path, 'r') as f:
                self._config_cache = yaml.safe_load(f)
            logger.info(f"✅ Configuration loaded from {self.config_path}")
            return self._config_cache
        except FileNotFoundError:
            logger.error(f"❌ Config file not found: {self.config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"❌ Invalid YAML in config file: {e}")
            raise

    def save_config(self, config: Dict[str, Any]) -> bool:
        """
        Save configuration to YAML file.

        Args:
            config: Configuration dictionary to save

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create backup first
            backup_path = f"{self.config_path}.backup"
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as src:
                    with open(backup_path, 'w') as dst:
                        dst.write(src.read())

            # Write new config
            with open(self.config_path, 'w') as f:
                yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)

            self._config_cache = config
            logger.info(f"✅ Configuration saved to {self.config_path}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to save config: {e}")
            # Restore from backup if it exists
            if os.path.exists(backup_path):
                with open(backup_path, 'r') as src:
                    with open(self.config_path, 'w') as dst:
                        dst.write(src.read())
                logger.info("⚠️  Config restored from backup")
            return False

    def get_auto_remediation_enabled(self) -> bool:
        """Check if auto-remediation is enabled"""
        config = self.load_config()
        return config.get('auto_remediation', {}).get('enabled', False)

    def set_auto_remediation_enabled(self, enabled: bool) -> bool:
        """
        Enable or disable auto-remediation.

        Args:
            enabled: True to enable, False to disable

        Returns:
            True if successful
        """
        config = self.load_config()
        if 'auto_remediation' not in config:
            config['auto_remediation'] = {}
        config['auto_remediation']['enabled'] = enabled
        return self.save_config(config)

    def get_dry_run_days(self) -> int:
        """Get the mandatory dry-run period in days"""
        config = self.load_config()
        return config.get('auto_remediation', {}).get('dry_run_days', 7)

    def set_dry_run_days(self, days: int) -> bool:
        """
        Set the mandatory dry-run period.

        Args:
            days: Number of days (0 to disable dry-run requirement)

        Returns:
            True if successful
        """
        config = self.load_config()
        if 'auto_remediation' not in config:
            config['auto_remediation'] = {}
        config['auto_remediation']['dry_run_days'] = days
        return self.save_config(config)

    def get_protection_rules(self) -> Dict[str, Any]:
        """Get all protection rules"""
        config = self.load_config()
        return config.get('protection', {})

    def update_protection_rule(self, key: str, value: Any) -> bool:
        """
        Update a specific protection rule.

        Args:
            key: Rule key (e.g., 'min_confidence_score')
            value: New value

        Returns:
            True if successful
        """
        config = self.load_config()
        if 'protection' not in config:
            config['protection'] = {}
        config['protection'][key] = value
        return self.save_config(config)

    def get_whitelist(self) -> Dict[str, Any]:
        """Get whitelist configuration"""
        config = self.load_config()
        return config.get('whitelist', {})

    def add_instance_to_whitelist(self, instance_id: str) -> bool:
        """
        Add an instance to the whitelist.

        Args:
            instance_id: EC2 instance ID

        Returns:
            True if successful
        """
        config = self.load_config()
        if 'whitelist' not in config:
            config['whitelist'] = {'instance_ids': []}
        if 'instance_ids' not in config['whitelist']:
            config['whitelist']['instance_ids'] = []

        if instance_id not in config['whitelist']['instance_ids']:
            config['whitelist']['instance_ids'].append(instance_id)
            return self.save_config(config)
        return True  # Already whitelisted

    def remove_instance_from_whitelist(self, instance_id: str) -> bool:
        """
        Remove an instance from the whitelist.

        Args:
            instance_id: EC2 instance ID

        Returns:
            True if successful
        """
        config = self.load_config()
        if 'whitelist' in config and 'instance_ids' in config['whitelist']:
            if instance_id in config['whitelist']['instance_ids']:
                config['whitelist']['instance_ids'].remove(instance_id)
                return self.save_config(config)
        return True  # Not in whitelist

    def get_schedule(self) -> Dict[str, Any]:
        """Get schedule configuration"""
        config = self.load_config()
        return config.get('schedule', {})

    def is_config_file_accessible(self) -> bool:
        """Check if config file exists and is accessible"""
        return os.path.exists(self.config_path) and os.access(self.config_path, os.R_OK | os.W_OK)


def get_backend_config_path() -> str:
    """Get the path to the backend config file"""
    return CONFIG_PATH
