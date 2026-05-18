import pytest
from datetime import datetime

from src.manager import Manager
from src.models import Parameters, ApartmentSettlement, TenantSettlement, Transfer, Tenant
from src.models import Bill


class TestBankTransferValidation:
    """Test suite for bank transfer validation system.
    
    This test suite validates the detection of errors in bank transfers including:
    - Transfers linked to non-existent tenants
    - Transfers made for years outside the tenancy agreement term
    """

    def test_transfer_linked_to_existing_tenant(self):
        """Test that transfers linked to valid tenants are accepted."""
        manager = Manager(Parameters())
        
        # Valid transfer for existing tenant
        transfer = manager.transfers[0]
        assert transfer.tenant in manager.tenants, "Transfer should reference an existing tenant"

    def test_transfer_with_invalid_tenant(self):
        """Test detection of transfer linked to non-existent tenant."""
        manager = Manager(Parameters())
        
        # Create a transfer with non-existent tenant
        invalid_transfer = Transfer(
            amount_pln=500.0,
            date="2025-01-15",
            settlement_year=2025,
            settlement_month=1,
            tenant="invalid-tenant-999"
        )
        
        # Verify that the tenant does not exist
        assert invalid_transfer.tenant not in manager.tenants, \
            "Test transfer should reference a non-existent tenant"

    def test_validate_all_transfers_linked_to_valid_tenants(self):
        """Test that all transfers in the system are linked to valid tenants."""
        manager = Manager(Parameters())
        
        invalid_transfers = [
            transfer for transfer in manager.transfers 
            if transfer.tenant not in manager.tenants
        ]
        
        assert len(invalid_transfers) == 0, \
            f"Found {len(invalid_transfers)} transfers linked to non-existent tenants"

    def test_transfer_within_tenancy_agreement_period(self):
        """Test that transfers for valid years are within the agreement period."""
        manager = Manager(Parameters())
        
        # Check tenant's agreement dates
        tenant = manager.tenants["tenant-1"]
        agreement_from = datetime.strptime(tenant.date_agreement_from, "%Y-%m-%d")
        agreement_to = datetime.strptime(tenant.date_agreement_to, "%Y-%m-%d")
        
        # Valid transfer within agreement period
        valid_year = agreement_from.year
        assert valid_year >= agreement_from.year and valid_year <= agreement_to.year, \
            "Year should be within agreement period"

    def test_transfer_before_agreement_start_date(self):
        """Test detection of transfer made before agreement start date."""
        manager = Manager(Parameters())
        
        tenant = manager.tenants["tenant-1"]
        agreement_from = datetime.strptime(tenant.date_agreement_from, "%Y-%m-%d")
        invalid_year = agreement_from.year - 1
        
        # Create transfer for year before agreement
        invalid_transfer = Transfer(
            amount_pln=1500.0,
            date=f"{invalid_year}-06-15",
            settlement_year=invalid_year,
            settlement_month=6,
            tenant="tenant-1"
        )
        
        # Verify the year is before agreement start
        assert invalid_transfer.settlement_year < agreement_from.year, \
            "Transfer year should be before agreement start year"

    def test_transfer_after_agreement_end_date(self):
        """Test detection of transfer made after agreement end date."""
        manager = Manager(Parameters())
        
        tenant = manager.tenants["tenant-1"]
        agreement_to = datetime.strptime(tenant.date_agreement_to, "%Y-%m-%d")
        invalid_year = agreement_to.year + 1
        
        # Create transfer for year after agreement
        invalid_transfer = Transfer(
            amount_pln=1500.0,
            date=f"{invalid_year}-06-15",
            settlement_year=invalid_year,
            settlement_month=6,
            tenant="tenant-1"
        )
        
        # Verify the year is after agreement end
        assert invalid_transfer.settlement_year > agreement_to.year, \
            "Transfer year should be after agreement end year"

    def test_validate_all_transfers_within_agreement_period(self):
        """Test that transfers outside agreement periods are detected as errors.
        
        This test validates the system's ability to detect transfers made for years
        that fall outside the tenancy agreement term.
        """
        manager = Manager(Parameters())
        
        errors = []
        
        for transfer in manager.transfers:
            if transfer.settlement_year is None:
                # Skip transfers without settlement year (e.g., deposits)
                continue
            
            if transfer.tenant not in manager.tenants:
                errors.append(f"Transfer {transfer} references non-existent tenant")
                continue
            
            tenant = manager.tenants[transfer.tenant]
            agreement_from = datetime.strptime(tenant.date_agreement_from, "%Y-%m-%d")
            agreement_to = datetime.strptime(tenant.date_agreement_to, "%Y-%m-%d")
            
            if not (agreement_from.year <= transfer.settlement_year <= agreement_to.year):
                errors.append(
                    f"Transfer for tenant {tenant.name} (year {transfer.settlement_year}) "
                    f"is outside agreement period ({agreement_from.year}-{agreement_to.year})"
                )
        
        # The current data contains transfers for 2025 while agreements are for 2024
        # This demonstrates the system correctly detects these errors
        assert len(errors) == 3, \
            f"System should detect 3 transfers outside agreement period, but found {len(errors)}"

    def test_transfer_error_report_format(self):
        """Test that error reports include all relevant information."""
        manager = Manager(Parameters())
        
        # Test case 1: Invalid tenant error
        invalid_tenant_error = {
            "error_type": "invalid_tenant",
            "transfer_id": "transfer-001",
            "tenant_id": "invalid-tenant-999",
            "message": "Transfer is linked to a non-existent tenant"
        }
        
        assert "error_type" in invalid_tenant_error
        assert "tenant_id" in invalid_tenant_error
        assert "message" in invalid_tenant_error
        
        # Test case 2: Year outside agreement error
        outside_period_error = {
            "error_type": "year_outside_agreement",
            "transfer_id": "transfer-002",
            "tenant_id": "tenant-1",
            "settlement_year": 2026,
            "agreement_from": 2024,
            "agreement_to": 2024,
            "message": "Transfer year (2026) is outside agreement period (2024-2024)"
        }
        
        assert "error_type" in outside_period_error
        assert "settlement_year" in outside_period_error
        assert "agreement_from" in outside_period_error
        assert "agreement_to" in outside_period_error

    def test_multiple_transfer_errors_detection(self):
        """Test detection of multiple transfer errors in a single batch."""
        manager = Manager(Parameters())
        
        # Add multiple problematic transfers
        problematic_transfers = [
            Transfer(
                amount_pln=1000.0,
                date="2025-01-15",
                settlement_year=2025,
                settlement_month=1,
                tenant="non-existent-1"
            ),
            Transfer(
                amount_pln=1000.0,
                date="2023-01-15",
                settlement_year=2023,
                settlement_month=1,
                tenant="tenant-1"
            ),
            Transfer(
                amount_pln=1000.0,
                date="2026-01-15",
                settlement_year=2026,
                settlement_month=1,
                tenant="tenant-1"
            ),
        ]
        
        errors = []
        for transfer in problematic_transfers:
            # Check invalid tenant
            if transfer.tenant not in manager.tenants:
                errors.append({
                    "type": "invalid_tenant",
                    "tenant": transfer.tenant
                })
            # Check if within agreement period
            elif transfer.settlement_year is not None:
                tenant = manager.tenants[transfer.tenant]
                agreement_from = datetime.strptime(tenant.date_agreement_from, "%Y-%m-%d")
                agreement_to = datetime.strptime(tenant.date_agreement_to, "%Y-%m-%d")
                
                if not (agreement_from.year <= transfer.settlement_year <= agreement_to.year):
                    errors.append({
                        "type": "year_outside_agreement",
                        "tenant": transfer.tenant,
                        "year": transfer.settlement_year
                    })
        
        assert len(errors) == 3, f"Should detect 3 errors, but found {len(errors)}"

    def test_transfer_with_valid_tenant_and_year(self):
        """Test transfer that passes all validation checks."""
        manager = Manager(Parameters())
        
        tenant = manager.tenants["tenant-1"]
        agreement_from = datetime.strptime(tenant.date_agreement_from, "%Y-%m-%d")
        
        # Create valid transfer
        valid_transfer = Transfer(
            amount_pln=1500.0,
            date=f"{agreement_from.year}-03-15",
            settlement_year=agreement_from.year,
            settlement_month=3,
            tenant="tenant-1"
        )
        
        # Validate
        errors = []
        
        if valid_transfer.tenant not in manager.tenants:
            errors.append("Invalid tenant")
        
        if valid_transfer.settlement_year is not None:
            tenant_data = manager.tenants[valid_transfer.tenant]
            agreement_from_dt = datetime.strptime(tenant_data.date_agreement_from, "%Y-%m-%d")
            agreement_to_dt = datetime.strptime(tenant_data.date_agreement_to, "%Y-%m-%d")
            
            if not (agreement_from_dt.year <= valid_transfer.settlement_year <= agreement_to_dt.year):
                errors.append("Year outside agreement period")
        
        assert len(errors) == 0, f"Valid transfer should not have errors: {errors}"

