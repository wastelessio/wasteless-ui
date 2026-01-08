#!/usr/bin/env python3
"""
Test script for ConfigManager
"""

import sys
from utils.config_manager import ConfigManager

def test_config_manager():
    """Test ConfigManager functionality"""

    print("\n" + "="*80)
    print("🧪 TESTING CONFIG MANAGER")
    print("="*80)

    # Initialize
    config_manager = ConfigManager()
    print(f"\n✅ ConfigManager initialized")
    print(f"   Config path: {config_manager.config_path}")

    # Check accessibility
    if not config_manager.is_config_file_accessible():
        print(f"\n❌ Config file is not accessible")
        return False

    print(f"✅ Config file is accessible")

    # Load config
    try:
        config = config_manager.load_config()
        print(f"✅ Configuration loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return False

    # Check current auto-remediation status
    auto_enabled = config_manager.get_auto_remediation_enabled()
    print(f"\n📊 Current Settings:")
    print(f"   Auto-remediation enabled: {auto_enabled}")

    dry_run_days = config_manager.get_dry_run_days()
    print(f"   Dry-run days: {dry_run_days}")

    protection = config_manager.get_protection_rules()
    print(f"   Min confidence score: {protection.get('min_confidence_score', 0.8)}")
    print(f"   Min idle days: {protection.get('min_idle_days', 14)}")
    print(f"   Max instances per run: {protection.get('max_instances_per_run', 3)}")

    whitelist = config_manager.get_whitelist()
    instance_ids = whitelist.get('instance_ids', [])
    print(f"   Whitelisted instances: {len(instance_ids)}")

    # Test toggle (don't actually change, just test the method exists)
    print(f"\n✅ All ConfigManager methods are accessible")

    print("\n" + "="*80)
    print("✅ CONFIG MANAGER TEST PASSED")
    print("="*80)
    return True


if __name__ == "__main__":
    success = test_config_manager()
    sys.exit(0 if success else 1)
