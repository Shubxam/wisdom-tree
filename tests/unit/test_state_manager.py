"""Tests for StateManager JSON persistence."""

import json
import pickle
from pathlib import Path

import pytest

from wisdom_tree.utils import StateManager


class TestStateManager:
    """Test suite for StateManager class."""

    def test_save_and_load_tree_age(self, temp_state_file):
        """Test saving and loading tree age."""
        manager = StateManager(temp_state_file)
        manager.save_tree_age(42)

        age = manager.load_tree_age()
        assert age == 42

    def test_load_nonexistent_file_returns_default(self, temp_state_file):
        """Test loading from non-existent file returns default age."""
        manager = StateManager(temp_state_file)
        assert manager.load_tree_age() == 1

    def test_save_creates_json_file(self, temp_state_file):
        """Test that save creates a JSON file with correct extension."""
        manager = StateManager(temp_state_file)
        manager.save_tree_age(100)

        # Should create .json file
        json_file = temp_state_file.with_suffix('.json')
        assert json_file.exists()

        # Verify it's valid JSON
        with open(json_file) as f:
            data = json.load(f)

        assert data['age'] == 100
        assert 'version' in data
        assert 'last_saved' in data

    def test_save_validates_age_type(self, temp_state_file):
        """Test that save validates age is an integer."""
        manager = StateManager(temp_state_file)

        with pytest.raises(ValueError, match='positive integer'):
            manager.save_tree_age('42')  # String instead of int

    def test_save_validates_age_positive(self, temp_state_file):
        """Test that save validates age is positive."""
        manager = StateManager(temp_state_file)

        with pytest.raises(ValueError, match='positive integer'):
            manager.save_tree_age(0)

        with pytest.raises(ValueError, match='positive integer'):
            manager.save_tree_age(-5)

    def test_load_corrupt_json_returns_default(self, temp_state_file):
        """Test loading corrupt JSON file returns default."""
        json_file = temp_state_file.with_suffix('.json')
        json_file.write_text('corrupt{{{json')

        manager = StateManager(temp_state_file)
        assert manager.load_tree_age() == 1

    def test_load_invalid_schema_returns_default(self, temp_state_file):
        """Test loading invalid schema returns default."""
        json_file = temp_state_file.with_suffix('.json')
        json_file.write_text('["not", "a", "dict"]')

        manager = StateManager(temp_state_file)
        assert manager.load_tree_age() == 1

    def test_load_invalid_age_returns_default(self, temp_state_file):
        """Test loading invalid age value returns default."""
        json_file = temp_state_file.with_suffix('.json')

        # Age is a string
        json_file.write_text(json.dumps({'age': 'forty-two', 'version': '1.0'}))
        manager = StateManager(temp_state_file)
        assert manager.load_tree_age() == 1

        # Age is negative
        json_file.write_text(json.dumps({'age': -10, 'version': '1.0'}))
        manager = StateManager(temp_state_file)
        assert manager.load_tree_age() == 1

    def test_migrate_from_pickle(self, temp_state_file):
        """Test automatic migration from pickle to JSON."""
        # Create old pickle file
        old_pickle_file = temp_state_file.with_suffix('')
        with open(old_pickle_file, 'wb') as f:
            pickle.dump(99, f)

        # Initialize StateManager (should trigger migration)
        manager = StateManager(temp_state_file)

        # Should have migrated the age
        assert manager.load_tree_age() == 99

        # Old file should be backed up
        backup_file = old_pickle_file.with_suffix('.pickle.bak')
        assert backup_file.exists()

        # JSON file should exist
        json_file = temp_state_file.with_suffix('.json')
        assert json_file.exists()

    def test_migrate_invalid_pickle_starts_fresh(self, temp_state_file):
        """Test migration handles invalid pickle files gracefully."""
        # Create invalid pickle file
        old_pickle_file = temp_state_file.with_suffix('')
        old_pickle_file.write_text('not a pickle file')

        # Should not crash, just start fresh
        manager = StateManager(temp_state_file)
        assert manager.load_tree_age() == 1

    def test_file_exists(self, temp_state_file):
        """Test file_exists method."""
        manager = StateManager(temp_state_file)

        # Initially doesn't exist
        assert not manager.file_exists()

        # After saving, exists
        manager.save_tree_age(50)
        assert manager.file_exists()

    def test_atomic_write(self, temp_state_file):
        """Test that writes are atomic (use temp file + rename)."""
        manager = StateManager(temp_state_file)
        manager.save_tree_age(75)

        # Temporary file should not exist after save
        temp_file = temp_state_file.with_suffix('.json.tmp')
        assert not temp_file.exists()

        # Final file should exist
        json_file = temp_state_file.with_suffix('.json')
        assert json_file.exists()
