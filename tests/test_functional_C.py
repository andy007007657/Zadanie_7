import pytest
from src.manager import Manager
from src.models import Parameters


class TestTransferValidationFeature:
    """Tests for Feature C: Transfer validation system
    
    This test suite validates detection of errors in transfers:
    - Transfer assigned to non-existent tenant
    - Transfer for year outside tenant's agreement period
    """

    def setup_method(self):
        self.manager = Manager(Parameters())

    def test_validate_transfer_assignment_with_invalid_tenant(self):
        """Test that transfer with non-existent tenant is flagged as error"""
        result = self.manager.validate_transfer_assignment(
            tenant="non-existent-tenant",
            settlement_year=2024,
            settlement_month=1
        )
        assert result['is_valid'] == False
        assert len(result['errors']) > 0

    def test_validate_transfer_assignment_with_valid_tenant(self):
        """Test that transfer with valid tenant passes validation"""
        result = self.manager.validate_transfer_assignment(
            tenant="tenant-1",
            settlement_year=2024,
            settlement_month=1
        )
        assert result['is_valid'] == True
        assert result['errors'] == []

    def test_validate_transfer_period_outside_agreement(self):
        """Test that transfer for year outside agreement period is flagged"""
        result = self.manager.validate_transfer_period(
            tenant="tenant-1",
            settlement_year=2025,
            settlement_month=1
        )
        assert result['is_valid'] == False
        assert len(result['errors']) > 0

    def test_validate_transfer_period_within_agreement(self):
        """Test that transfer within agreement period passes"""
        result = self.manager.validate_transfer_period(
            tenant="tenant-1",
            settlement_year=2024,
            settlement_month=6
        )
        assert result['is_valid'] == True
        assert result['errors'] == []

    def test_validate_transfer_period_at_agreement_start(self):
        """Test transfer at exact agreement start year"""
        result = self.manager.validate_transfer_period(
            tenant="tenant-1",
            settlement_year=2024,
            settlement_month=1
        )
        assert result['is_valid'] == True

    def test_validate_transfer_period_at_agreement_end(self):
        """Test transfer at exact agreement end year"""
        result = self.manager.validate_transfer_period(
            tenant="tenant-1",
            settlement_year=2024,
            settlement_month=12
        )
        assert result['is_valid'] == True

    def test_validate_transfer_period_before_agreement_start(self):
        """Test that transfer before agreement start is flagged"""
        result = self.manager.validate_transfer_period(
            tenant="tenant-1",
            settlement_year=2023,
            settlement_month=6
        )
        assert result['is_valid'] == False

    def test_validate_transfer_period_after_agreement_end(self):
        """Test that transfer after agreement end is flagged"""
        result = self.manager.validate_transfer_period(
            tenant="tenant-1",
            settlement_year=2025,
            settlement_month=1
        )
        assert result['is_valid'] == False

    def test_validate_all_transfers_returns_error_list(self):
        """Test that validating all transfers returns list of errors"""
        errors = self.manager.validate_all_transfers()
        assert isinstance(errors, list)

    def test_validate_transfer_with_invalid_tenant_includes_error_message(self):
        """Test that error message is included for invalid tenant"""
        result = self.manager.validate_transfer_assignment(
            tenant="invalid-xyz",
            settlement_year=2024,
            settlement_month=1
        )
        assert result['is_valid'] == False
        error_text = ' '.join(result['errors']).lower()
        assert 'tenant' in error_text or 'nie znaleziono' in error_text