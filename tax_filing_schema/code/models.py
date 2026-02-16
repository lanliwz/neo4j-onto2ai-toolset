from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field


class Currency(str, Enum):
    """Enumeration for currency codes supported in the tax system."""
    USD = "US Dollar"
    EUR = "Euro"
    GBP = "British Pound (Sterling)"
    JPY = "Japanese Yen"
    CNY = "Chinese Yuan"
    CAD = "Canadian Dollar"
    AUD = "Australian Dollar"
    CHF = "Swiss Franc"


class ReportStatus(str, Enum):
    """Lifecycle status of a tax report or filing."""
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"


class Jurisdiction(str, Enum):
    """Geopolitical jurisdiction for tax filing."""
    US_FEDERAL = "United States jurisdiction"


class FilingStatus(str, Enum):
    """Tax filing status classification."""
    SINGLE = "single"
    MARRIED_FILING_JOINTLY = "married filing jointly"


class SemanticModel(BaseModel):
    """Base class for all semantic nodes, including URI for identity."""
    uri: Optional[str] = Field(default=None, description="Unique identifier for the semantic node")


class MonetaryAmount(SemanticModel):
    """Measure that is an amount of money specified in monetary units."""
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    
    amount: Decimal = Field(alias="hasAmount", description="The numeric value of the amount")
    currency: Currency = Field(alias="isDenominatedIn", default=Currency.USD, description="The currency denomination")


class Person(SemanticModel):
    """Individual human being with consciousness of self."""
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    personName: Optional[str] = Field(alias="hasName", default=None, description="Legal designation by which someone is known")
    ssn: Optional[str] = Field(alias="hasTaxId", default=None, description="Social Security Number (9 digits)")
    itin: Optional[str] = Field(alias="hasTaxId", default=None, description="Individual Taxpayer Identification Number")
    fullAddress: Optional[str] = Field(alias="hasResidence", default=None, description="Full residential address (flattened)")
    age: Optional[int] = Field(alias="hasAge", default=None, description="Length of time lived in years")
    dateOfBirth: Optional[date] = Field(alias="hasDateOfBirth", default=None, description="Date on which the individual was born")
    birthPlace: Optional[str] = Field(alias="hasPlaceOfBirth", default=None, description="Location where the individual was born")
    isEmployedBy: List[Employer] = Field(alias="isEmployedBy", default_factory=list)


class TaxPayer(Person):
    """Person who is obligated to pay taxes and is identified by a tax identifier."""
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class Organization(SemanticModel):
    """Framework of authority within which people act towards some purpose."""
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    employerName: Optional[str] = Field(alias="hasEmployerName", default=None, description="Legal name of the organization")
    ein: Optional[str] = Field(alias="hasEIN", default=None, description="Employer Identification Number (9 digits)")
    fullAddress: Optional[str] = Field(alias="hasAddress", default=None, description="Operating address (flattened)")
    phoneNumber: Optional[str] = Field(alias="hasPhoneNumber", default=None, description="Contact phone number")


class Employer(Organization):
    """Party that provides compensation in exchange for work performed."""
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class IndividualTaxReturn(SemanticModel):
    """Base class for individual tax return filings (e.g., Form 1040)."""
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    taxYear: int = Field(alias="hasTaxYear", description="The tax year for which the return is filed")
    hasReportStatus: ReportStatus = Field(alias="hasReportStatus", default=ReportStatus.DRAFT)
    isSubmittedTo: str = Field(alias="isSubmittedTo", default="Internal Revenue Service", description="Target tax authority")


class Form1040_2025(IndividualTaxReturn):
    """IRS Form 1040 (U.S. Individual Income Tax Return) for tax year 2025."""
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    taxableIncome: Optional[MonetaryAmount] = Field(alias="hasTaxableIncome", default=None)
    adjustedGrossIncome: Optional[MonetaryAmount] = Field(alias="hasAGI", default=None)
    totalTax: Optional[MonetaryAmount] = Field(alias="hasTotalTax", default=None)
    refundAmount: Optional[MonetaryAmount] = Field(alias="hasRefundAmount", default=None)
    filingStatus: Optional[FilingStatus] = Field(alias="hasFilingStatus", default=None)


class W2Form(IndividualTaxReturn):
    """IRS Form W-2 (Wage and Tax Statement)."""
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    issuedTo: Optional[Person] = Field(alias="issuedTo", default=None)
    issuedBy: Optional[Employer] = Field(alias="issuedBy", default=None)

    # Core Amounts
    box1WagesTipsOtherComp: Optional[MonetaryAmount] = Field(alias="hasWagesTipsOtherComp", default=None)
    box2FederalIncomeTaxWithheld: Optional[MonetaryAmount] = Field(alias="hasFederalIncomeTaxWithheld", default=None)
    box3SocialSecurityWages: Optional[MonetaryAmount] = Field(alias="hasSocialSecurityWages", default=None)
    box4SocialSecurityTaxWithheld: Optional[MonetaryAmount] = Field(alias="hasSocialSecurityTaxWithheld", default=None)
    box5MedicareWagesAndTips: Optional[MonetaryAmount] = Field(alias="hasMedicareWagesAndTips", default=None)
    box6MedicareTaxWithheld: Optional[MonetaryAmount] = Field(alias="hasMedicareTaxWithheld", default=None)
    
    # Checkboxes
    box13StatutoryEmployee: bool = Field(alias="isStatutoryEmployee", default=False)
    box13RetirementPlan: bool = Field(alias="hasRetirementPlan", default=False)
    box13ThirdPartySickPay: bool = Field(alias="hasThirdPartySickPay", default=False)

    # Coding and Other
    box12Codes: List[str] = Field(alias="hasBox12Codes", default_factory=list, description="Coded amounts in Box 12")
    box14Other: Optional[str] = Field(alias="hasOtherInfo", default=None, description="Other information")

    # State and Local
    box15State: Optional[Jurisdiction] = Field(alias="hasJurisdiction", default=None)
    box16StateWagesTips: Optional[MonetaryAmount] = Field(alias="hasStateWagesTips", default=None)
    box17StateIncomeTax: Optional[MonetaryAmount] = Field(alias="hasStateIncomeTax", default=None)
