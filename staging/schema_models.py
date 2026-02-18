from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

class TaxAuthority(Enum):
    """functional entity that is responsible for the administration and enforcement of tax laws"""
    INTERNAL_REVENUE_SERVICE = "Internal Revenue Service"

class Jurisdiction(Enum):
    """power of a court or regulatory agency to adjudicate cases, issue orders, and interpret and apply the law with respect to some specific geographic area"""
    UNITED_STATES_JURISDICTION = "United States jurisdiction"

class FilingStatusConcept(Enum):
    """concept representing the legal status of a taxpayer for filing purposes"""
    MARRIED_FILING_JOINTLY = "married filing jointly"
    SINGLE = "single"

class Reportstatus(Enum):
    """lifecycle status of a report"""
    ACCEPTED = "Accepted"
    DRAFT = "Draft"
    REJECTED = "Rejected"
    SUBMITTED = "Submitted"

class Currency(Enum):
    """medium of exchange"""
    AUSTRALIAN_DOLLAR = "Australian Dollar"
    BRITISH_POUND_STERLING = "British Pound (Sterling)"
    CANADIAN_DOLLAR = "Canadian Dollar"
    CHINESE_YUAN = "Chinese Yuan"
    EURO = "Euro"
    JAPANESE_YEN = "Japanese Yen"
    SWISS_FRANC = "Swiss Franc"
    US_DOLLAR = "US Dollar"

class Organization(BaseModel):
    """framework of authority within which a person, persons, or groups of people act, or are designated to act, towards some purpose, such as to meet a need or pursue collective goals"""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    has_ein: Optional[str] = Field(default=None, alias="hasEIN", description="Links an organization to its employer identification number.")
    has_tax_id: Optional[str] = Field(default=None, alias="hasTaxId", description="Relates an organization to its Employer Identification Number (EIN) used as the organization\u2019s tax identification identifier.")

class Exchange(BaseModel):
    """A marketplace where securities, commodities, derivatives and other financial instruments are traded."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    pass

class W2Form(BaseModel):
    """IRS Form W-2, Wage and Tax Statement, used by employers to report wages paid and taxes withheld for each employee."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    has_allocated_tips: Optional[str] = Field(default=None, alias="hasAllocatedTips", description="")
    has_box12_codes: List[str] = Field(default_factory=list, alias="hasBox12Codes", description="")
    has_dependent_care_benefits: Optional[str] = Field(default=None, alias="hasDependentCareBenefits", description="")
    has_federal_income_tax_withheld: str = Field(alias="hasFederalIncomeTaxWithheld", description="")
    has_medicare_tax_withheld: str = Field(alias="hasMedicareTaxWithheld", description="")
    has_medicare_wages_and_tips: str = Field(alias="hasMedicareWagesAndTips", description="")
    has_nonqualified_plans: Optional[str] = Field(default=None, alias="hasNonqualifiedPlans", description="")
    has_other_info: List[str] = Field(default_factory=list, alias="hasOtherInfo", description="")
    has_report_date_time: List[datetime] = Field(default_factory=list, alias="hasReportDateTime", description="Relates a W-2 form to the date and time at which the form is reported or issued for reporting purposes.")
    has_retirement_plan: Optional[str] = Field(default=None, alias="hasRetirementPlan", description="")
    has_social_security_tax_withheld: str = Field(alias="hasSocialSecurityTaxWithheld", description="")
    has_social_security_tips: Optional[str] = Field(default=None, alias="hasSocialSecurityTips", description="")
    has_social_security_wages: str = Field(alias="hasSocialSecurityWages", description="")
    has_tax_year: str = Field(alias="hasTaxYear", description="")
    has_third_party_sick_pay: Optional[str] = Field(default=None, alias="hasThirdPartySickPay", description="")
    has_wages_tips_other_comp: str = Field(alias="hasWagesTipsOtherComp", description="")
    is_provided_by: List[str] = Field(default_factory=list, min_length=1, alias="isProvidedBy", description="Relates a W-2 form to the reporting party that provides and issues it for wage and tax reporting purposes.")
    is_statutory_employee: Optional[str] = Field(default=None, alias="isStatutoryEmployee", description="")
    is_submitted_by: List[str] = Field(default_factory=list, alias="isSubmittedBy", description="Relates a W-2 form to the submitter that files or submits it to the appropriate authority or recipient.")
    has_report_status: Reportstatus = Field(alias="hasReportStatus", description="Links a W-2 form to the report status that indicates its reporting state for filing and compliance purposes.")
    issued_by: Employer = Field(alias="issuedBy", description="employer that issued the W-2")
    issued_to: Person = Field(alias="issuedTo", description="employee who received the W-2")

class CryptoAsset(BaseModel):
    """A digital asset designed to work as a medium of exchange."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    has_token_symbol: str = Field(alias="hasTokenSymbol", description="The ticker symbol for the crypto asset.")
    is_traded_on: List[Exchange] = Field(default_factory=list, alias="isTradedOn", description="Indicates the exchange where the asset is listed.")

class Person(BaseModel):
    """individual human being, with consciousness of self"""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    has_age: List[str] = Field(default_factory=list, alias="hasAge", description="relates something to the length of time it has existed")
    has_citizenship: List[str] = Field(default_factory=list, alias="hasCitizenship", description="links a person to their country of citizenship")
    has_date_of_birth: str = Field(alias="hasDateOfBirth", description="identifies the date on which an individual was born")
    has_date_of_death: Optional[str] = Field(default=None, alias="hasDateOfDeath", description="identifies the date on which an individual died")
    has_name: List[str] = Field(default_factory=list, alias="hasName", description="is known by")
    has_place_of_birth: str = Field(alias="hasPlaceOfBirth", description="identifies the location where an individual was born")
    has_residence: List[str] = Field(default_factory=list, alias="hasResidence", description="identifies a dwelling where an individual lives")
    has_tax_id: List[str] = Field(default_factory=list, alias="hasTaxId", description="Links a person to their tax identifier.")
    is_employed_by: List[Employer] = Field(default_factory=list, alias="isEmployedBy", description="indicates the employer")

class PhysicalAddress(BaseModel):
    """A physical address is a structured specification of the real-world location of a premises, such as a residence or business site, used to identify where a party is situated or an activity occurs for financial operations, regulatory reporting, and tax jurisdiction determination."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    pass

class Form1120USCorporationIncomeTaxReturn(BaseModel):
    """An Internal Revenue Service tax form used by U.S. C corporations to report annual income, gains, losses, deductions, credits, and resulting federal corporate income tax liability."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    pass

class IndividualTaxReturn(BaseModel):
    """A tax return filed by an individual person."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    has_report_date_time: List[datetime] = Field(default_factory=list, alias="hasReportDateTime", description="Links an individual tax return to the date and time at which it was reported or filed.")
    is_provided_by: List[str] = Field(default_factory=list, min_length=1, alias="isProvidedBy", description="Relates an individual tax return to the reporting party that provides and submits the return for reporting purposes.")
    is_submitted_by: List[str] = Field(default_factory=list, alias="isSubmittedBy", description="Relates an individual tax return to the submitter that files or transmits it to the relevant tax authority.")
    is_submitted_to: TaxAuthority = Field(alias="isSubmittedTo", description="identifies the party to which the report is submitted")
    has_taxable_income: MonetaryAmount = Field(alias="hasTaxableIncome", description="Relates an individual tax return to the monetary amount representing the taxpayer\u2019s taxable income as determined for that return under applicable U.S. federal tax rules.")
    has_report_status: Reportstatus = Field(alias="hasReportStatus", description="Relates an individual tax return to the report status that indicates its current reporting state (e.g., filed, pending, accepted, rejected) for reporting purposes.")
    has_agi: MonetaryAmount = Field(alias="hasAGI", description="Relates an individual tax return to the monetary amount representing the filer\u2019s adjusted gross income (AGI) reported for that return.")
    has_total_tax: MonetaryAmount = Field(alias="hasTotalTax", description="Relates an individual tax return to the monetary amount representing the total tax liability computed for that return for the applicable tax year.")
    has_total_payments: MonetaryAmount = Field(alias="hasTotalPayments", description="Relates an individual tax return to the aggregate monetary amount representing the total payments credited toward the taxpayer\u2019s tax liability for the tax period covered by the return.")
    has_refund_amount: MonetaryAmount = Field(alias="hasRefundAmount", description="Relates an individual tax return to the monetary amount of any refund due to the filer as determined on that return.")
    has_amount_owed: MonetaryAmount = Field(alias="hasAmountOwed", description="Relates an individual tax return to the monetary amount of tax liability owed by the filer for the return period.")
    has_line1a_wages: MonetaryAmount = Field(alias="hasLine1aWages", description="Relates an individual tax return to the monetary amount reported as wages on Line 1a of the return.")
    has_line2b_taxable_interest: MonetaryAmount = Field(alias="hasLine2bTaxableInterest", description="Relates an individual tax return to the monetary amount reported as taxable interest on IRS Form 1040, line 2b.")
    has_line3b_ordinary_dividends: MonetaryAmount = Field(alias="hasLine3bOrdinaryDividends", description="Relates an individual tax return to the monetary amount reported as ordinary dividends on IRS Form 1040, Line 3b.")
    has_line6b_taxable_social_security: MonetaryAmount = Field(alias="hasLine6bTaxableSocialSecurity", description="Relates an individual tax return to the monetary amount reported as taxable Social Security benefits on IRS Form 1040 line 6b.")
    has_line12_standard_deduction: MonetaryAmount = Field(alias="hasLine12StandardDeduction", description="Relates an individual tax return to the monetary amount reported as the standard deduction on Line 12 of the return.")
    has_line16_tax_value: MonetaryAmount = Field(alias="hasLine16TaxValue", description="Relates an individual tax return to the monetary amount reported as tax on Line 16 of the return.")
    has_line19_child_tax_credit: MonetaryAmount = Field(alias="hasLine19ChildTaxCredit", description="Relates an individual tax return to the monetary amount reported on IRS Form 1040, line 19, representing the Child Tax Credit claimed for the tax year.")
    has_line24_total_tax: MonetaryAmount = Field(alias="hasLine24TotalTax", description="Relates an individual tax return to the monetary amount reported as its total tax on IRS Form 1040, line 24.")
    has_line33_total_payments: MonetaryAmount = Field(alias="hasLine33TotalPayments", description="Relates an individual tax return to the monetary amount reported as the total payments on Line 33.")

class MonetaryAmount(BaseModel):
    """A quantity of money, denominated in a specific currency."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    is_denominated_in: Currency = Field(alias="isDenominatedIn", description="Relates a monetary amount to the currency in which that amount is expressed.")

class Form1040_2025(BaseModel):
    """The IRS Form 1040 for tax year 2025, used by U.S. individual taxpayers to file their annual federal income tax return and report income, deductions, credits, and tax liability."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    has_report_date_time: List[datetime] = Field(default_factory=list, alias="hasReportDateTime", description="Links an individual tax return to the date and time at which it was reported or filed.")
    is_provided_by: List[str] = Field(default_factory=list, min_length=1, alias="isProvidedBy", description="Relates an individual tax return to the reporting party that provides and submits the return for reporting purposes.")
    is_submitted_by: List[str] = Field(default_factory=list, alias="isSubmittedBy", description="Relates an individual tax return to the submitter that files or transmits it to the relevant tax authority.")
    is_submitted_to: TaxAuthority = Field(alias="isSubmittedTo", description="identifies the party to which the report is submitted")
    has_taxable_income: MonetaryAmount = Field(alias="hasTaxableIncome", description="Relates an individual tax return to the monetary amount representing the taxpayer\u2019s taxable income as determined for that return under applicable U.S. federal tax rules.")
    has_report_status: Reportstatus = Field(alias="hasReportStatus", description="Relates an individual tax return to the report status that indicates its current reporting state (e.g., filed, pending, accepted, rejected) for reporting purposes.")
    has_agi: MonetaryAmount = Field(alias="hasAGI", description="Relates an individual tax return to the monetary amount representing the filer\u2019s adjusted gross income (AGI) reported for that return.")
    has_total_tax: MonetaryAmount = Field(alias="hasTotalTax", description="Relates an individual tax return to the monetary amount representing the total tax liability computed for that return for the applicable tax year.")
    has_total_payments: MonetaryAmount = Field(alias="hasTotalPayments", description="Relates an individual tax return to the aggregate monetary amount representing the total payments credited toward the taxpayer\u2019s tax liability for the tax period covered by the return.")
    has_refund_amount: MonetaryAmount = Field(alias="hasRefundAmount", description="Relates an individual tax return to the monetary amount of any refund due to the filer as determined on that return.")
    has_amount_owed: MonetaryAmount = Field(alias="hasAmountOwed", description="Relates an individual tax return to the monetary amount of tax liability owed by the filer for the return period.")
    has_line1a_wages: MonetaryAmount = Field(alias="hasLine1aWages", description="Relates an individual tax return to the monetary amount reported as wages on Line 1a of the return.")
    has_line2b_taxable_interest: MonetaryAmount = Field(alias="hasLine2bTaxableInterest", description="Relates an individual tax return to the monetary amount reported as taxable interest on IRS Form 1040, line 2b.")
    has_line3b_ordinary_dividends: MonetaryAmount = Field(alias="hasLine3bOrdinaryDividends", description="Relates an individual tax return to the monetary amount reported as ordinary dividends on IRS Form 1040, Line 3b.")
    has_line6b_taxable_social_security: MonetaryAmount = Field(alias="hasLine6bTaxableSocialSecurity", description="Relates an individual tax return to the monetary amount reported as taxable Social Security benefits on IRS Form 1040 line 6b.")
    has_line12_standard_deduction: MonetaryAmount = Field(alias="hasLine12StandardDeduction", description="Relates an individual tax return to the monetary amount reported as the standard deduction on Line 12 of the return.")
    has_line16_tax_value: MonetaryAmount = Field(alias="hasLine16TaxValue", description="Relates an individual tax return to the monetary amount reported as tax on Line 16 of the return.")
    has_line19_child_tax_credit: MonetaryAmount = Field(alias="hasLine19ChildTaxCredit", description="Relates an individual tax return to the monetary amount reported on IRS Form 1040, line 19, representing the Child Tax Credit claimed for the tax year.")
    has_line24_total_tax: MonetaryAmount = Field(alias="hasLine24TotalTax", description="Relates an individual tax return to the monetary amount reported as its total tax on IRS Form 1040, line 24.")
    has_line33_total_payments: MonetaryAmount = Field(alias="hasLine33TotalPayments", description="Relates an individual tax return to the monetary amount reported as the total payments on Line 33.")

class TaxPayer(BaseModel):
    """A person who is obligated to pay taxes and is identified by a tax identifier."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    has_age: List[str] = Field(default_factory=list, alias="hasAge", description="relates something to the length of time it has existed")
    has_citizenship: List[str] = Field(default_factory=list, alias="hasCitizenship", description="links a person to their country of citizenship")
    has_date_of_birth: str = Field(alias="hasDateOfBirth", description="identifies the date on which an individual was born")
    has_date_of_death: Optional[str] = Field(default=None, alias="hasDateOfDeath", description="identifies the date on which an individual died")
    has_name: List[str] = Field(default_factory=list, alias="hasName", description="is known by")
    has_place_of_birth: str = Field(alias="hasPlaceOfBirth", description="identifies the location where an individual was born")
    has_residence: List[str] = Field(default_factory=list, alias="hasResidence", description="identifies a dwelling where an individual lives")
    has_tax_id: List[str] = Field(default_factory=list, alias="hasTaxId", description="Links a person to their tax identifier.")
    is_employed_by: List[Employer] = Field(default_factory=list, alias="isEmployedBy", description="indicates the employer")

class Employer(BaseModel):
    """A legal person or formal organization that employs one or more individuals and is responsible for withholding and reporting taxes."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    has_address: List[str] = Field(default_factory=list, min_length=1, alias="hasAddress", description="employer business address")
    has_ein: str = Field(alias="hasEIN", description="Employer Identification Number")
    has_employer_name: str = Field(alias="hasEmployerName", description="legal name of the employer")
    has_phone_number: List[str] = Field(default_factory=list, alias="hasPhoneNumber", description="contact phone number")
