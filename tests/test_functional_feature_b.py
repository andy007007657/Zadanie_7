import pytest
from src.manager import Manager
from src.models import Parameters


class TestBlacklistFeature:
    """Tests for Feature B: Blacklist of tenants"""

    def setup_method(self):
        self.manager = Manager(Parameters())

    def test_blacklist_file_exists_and_loads(self):
        """Test that blacklist file can be loaded"""
        self.manager.load_blacklist()
        assert self.manager.blacklist is not None

    def test_blacklist_contains_expected_entries(self):
        """Test that blacklist contains expected tenant names"""
        self.manager.load_blacklist()
        blacklist_names = [entry.name for entry in self.manager.blacklist]
        assert "Jan Nowak" in blacklist_names

    def test_tenant_on_blacklist_is_blacklisted(self):
        """Test that tenant on blacklist is marked as blacklisted"""
        self.manager.load_blacklist()
        result = self.manager.is_blacklisted("Jan Nowak")
        assert result == True

    def test_tenant_not_on_blacklist_is_not_blacklisted(self):
        """Test that tenant not on blacklist is not marked as blacklisted"""
        self.manager.load_blacklist()
        result = self.manager.is_blacklisted("Adam Kowalski")
        assert result == False

    def test_tenant_not_on_blacklist_passes_check(self):
        """Test that tenant not in system passes blacklist check"""
        self.manager.load_blacklist()
        result = self.manager.is_blacklisted("Nieistniejący Najemca")
        assert result == False

    def test_get_blacklist_entry_returns_reason(self):
        """Test that blacklist entry contains reason"""
        self.manager.load_blacklist()
        entry = self.manager.get_blacklist_entry("Jan Nowak")
        assert entry is not None
        assert entry.reason is not None
        assert len(entry.reason) > 0

    def test_get_blacklist_entry_for_non_blacklisted_returns_none(self):
        """Test that getting entry for non-blacklisted tenant returns None"""
        self.manager.load_blacklist()
        entry = self.manager.get_blacklist_entry("Adam Kowalski")
        assert entry is None

    def test_check_tenant_against_blacklist_returns_tuple(self):
        """Test that blacklist check returns tuple with status and reason"""
        self.manager.load_blacklist()
        result = self.manager.check_blacklist("Jan Nowak")
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] == True
        assert isinstance(result[1], str)

    def test_blacklist_various_tenants(self):
        """Test blacklist with various tenant scenarios"""
        self.manager.load_blacklist()
        assert self.manager.is_blacklisted("Jan Nowak") == True
        assert self.manager.is_blacklisted("Piotr Wiśniewski") == True
        assert self.manager.is_blacklisted("Adam Kowalski") == False
        assert self.manager.is_blacklisted("Ewa Adamska") == False

    def test_blacklist_not_loaded_returns_empty(self):
        """Test that without loading blacklist, check returns False"""
        result = self.manager.is_blacklisted("Jan Nowak")
        assert result == False