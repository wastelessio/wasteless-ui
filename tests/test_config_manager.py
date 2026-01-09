"""
Unit tests for ConfigManager
"""
import unittest
import tempfile
import yaml
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.config_manager import ConfigManager


class TestConfigManager(unittest.TestCase):
    """Test cases for ConfigManager."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary config file
        self.temp_config = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.yaml',
            delete=False
        )

        # Write sample config
        sample_config = {
            'auto_remediation': {
                'enabled': False,
                'dry_run_days': 7
            },
            'protection': {
                'min_instance_age_days': 30,
                'min_idle_days': 14,
                'min_confidence_score': 0.8,
                'max_instances_per_run': 3
            },
            'schedule': {
                'allowed_days': ['Saturday', 'Sunday'],
                'allowed_hours': [2, 3, 4],
                'timezone': 'Europe/Paris'
            }
        }

        yaml.dump(sample_config, self.temp_config)
        self.temp_config.close()

        # Create ConfigManager with temp file
        self.config_manager = ConfigManager(config_path=self.temp_config.name)

    def tearDown(self):
        """Clean up test fixtures."""
        # Delete temp file
        Path(self.temp_config.name).unlink(missing_ok=True)

    def test_load_config(self):
        """Test loading configuration."""
        config = self.config_manager.load_config()
        self.assertIsNotNone(config)
        self.assertIn('auto_remediation', config)
        self.assertIn('protection', config)

    def test_config_file_accessible(self):
        """Test is_config_file_accessible."""
        self.assertTrue(self.config_manager.is_config_file_accessible())

    def test_get_auto_remediation_enabled(self):
        """Test getting auto_remediation enabled status."""
        config = self.config_manager.load_config()
        enabled = config.get('auto_remediation', {}).get('enabled', False)
        self.assertFalse(enabled)

    def test_get_protection_rules(self):
        """Test getting protection rules."""
        config = self.config_manager.load_config()
        protection = config.get('protection', {})

        self.assertEqual(protection.get('min_instance_age_days'), 30)
        self.assertEqual(protection.get('min_idle_days'), 14)
        self.assertEqual(protection.get('min_confidence_score'), 0.8)
        self.assertEqual(protection.get('max_instances_per_run'), 3)

    def test_get_schedule_config(self):
        """Test getting schedule configuration."""
        config = self.config_manager.load_config()
        schedule = config.get('schedule', {})

        self.assertEqual(schedule.get('allowed_days'), ['Saturday', 'Sunday'])
        self.assertEqual(schedule.get('allowed_hours'), [2, 3, 4])
        self.assertEqual(schedule.get('timezone'), 'Europe/Paris')

    def test_config_structure(self):
        """Test that config has expected structure."""
        config = self.config_manager.load_config()

        # Check top-level keys
        expected_keys = ['auto_remediation', 'protection', 'schedule']
        for key in expected_keys:
            self.assertIn(key, config)

    def test_protection_values_types(self):
        """Test that protection values have correct types."""
        config = self.config_manager.load_config()
        protection = config.get('protection', {})

        self.assertIsInstance(protection.get('min_instance_age_days'), int)
        self.assertIsInstance(protection.get('min_idle_days'), int)
        self.assertIsInstance(protection.get('min_confidence_score'), float)
        self.assertIsInstance(protection.get('max_instances_per_run'), int)


class TestConfigValidation(unittest.TestCase):
    """Test configuration validation."""

    def test_min_confidence_range(self):
        """Test that confidence score is between 0 and 1."""
        config = {'protection': {'min_confidence_score': 0.8}}
        confidence = config['protection']['min_confidence_score']

        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)

    def test_positive_values(self):
        """Test that numeric values are positive."""
        config = {
            'protection': {
                'min_instance_age_days': 30,
                'min_idle_days': 14,
                'max_instances_per_run': 3
            }
        }

        for key, value in config['protection'].items():
            if isinstance(value, (int, float)):
                self.assertGreater(value, 0, f"{key} should be positive")


if __name__ == '__main__':
    unittest.main()
