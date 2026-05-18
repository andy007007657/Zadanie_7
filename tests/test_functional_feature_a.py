import pytest
from src.manager import Manager
from src.models import Parameters, Transfer


class TestFeatureAValidation:
    """Tests for Feature A: Transfer value validation (extreme values)"""
    
    def setup_method(self):
        self.manager = Manager(Parameters())
        # Set validation limits
        self.manager.min_transfer_amount = 0.01  # minimum 1 cent
        self.manager.max_transfer_amount = 100_000.0  # maximum 100k PLN
    
    def test_valid_transfer_within_limits(self):
        """Test that valid transfer within limits passes validation"""
        result = self.manager.validate_transfer(amount_pln=5000.0)
        assert result['is_valid'] == True
        assert result['errors'] == []
    
    def test_transfer_too_small(self):
        """Test that transfer below minimum is rejected"""
        result = self.manager.validate_transfer(amount_pln=0.001)
        assert result['is_valid'] == False
        assert 'minimum' in result['errors'][0].lower()
    
    def test_transfer_too_large(self):
        """Test that transfer above maximum is rejected"""
        result = self.manager.validate_transfer(amount_pln=150_000.0)
        assert result['is_valid'] == False
        assert 'maximum' in result['errors'][0].lower()
    
    def test_transfer_zero(self):
        """Test that zero amount is rejected"""
        result = self.manager.validate_transfer(amount_pln=0.0)
        assert result['is_valid'] == False
        assert len(result['errors']) > 0
    
    def test_transfer_negative(self):
        """Test that negative amount is rejected"""
        result = self.manager.validate_transfer(amount_pln=-500.0)
        assert result['is_valid'] == False
        assert 'negative' in result['errors'][0].lower()
    
    def test_transfer_exactly_min_limit(self):
        """Test transfer exactly at minimum limit"""
        result = self.manager.validate_transfer(amount_pln=0.01)
        assert result['is_valid'] == True
    
    def test_transfer_exactly_max_limit(self):
        """Test transfer exactly at maximum limit"""
        result = self.manager.validate_transfer(amount_pln=100_000.0)
        assert result['is_valid'] == True
    
    def test_validate_multiple_transfers(self):
        """Test validation of multiple transfers"""
        transfers_to_validate = [
            5000.0,      # valid
            0.001,       # too small
            150_000.0,   # too large
            1000.0,      # valid
        ]
        results = [
            self.manager.validate_transfer(amount_pln=amount)
            for amount in transfers_to_validate
        ]
        assert results[0]['is_valid'] == True
        assert results[1]['is_valid'] == False
        assert results[2]['is_valid'] == False
        assert results[3]['is_valid'] == True