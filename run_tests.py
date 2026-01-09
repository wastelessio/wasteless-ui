#!/usr/bin/env python3
"""
Run all unit tests for Wasteless UI
"""
import unittest
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Discover and run tests
if __name__ == '__main__':
    # Create test loader
    loader = unittest.TestLoader()

    # Discover all tests in the tests directory
    start_dir = 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
