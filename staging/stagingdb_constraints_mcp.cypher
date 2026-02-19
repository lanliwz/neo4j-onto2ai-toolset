// ===========================================================
// NEO4J SCHEMA CONSTRAINTS (Source: stagingdb)
// Generated to enforce structural integrity while keeping metadata as comments.
// ===========================================================

// Class: 2025 Form 1040
// Definition: The IRS Form 1040 for tax year 2025, used by U.S. individual taxpayers to file their annual federal income tax return and report income, deductions, credits, and tax liability.
// URI: https://example.org/tax/filings/2025-Form1040
// Mandatory property: isProvidedBy (cardinality: 1..*)
CREATE CONSTRAINT Form1040_2025_isProvidedBy_Required IF NOT EXISTS FOR (n:`Form1040_2025`) REQUIRE n.`isProvidedBy` IS NOT NULL;
// Mandatory named_individual relationship: isSubmittedTo -> Internal Revenue Service (cardinality: 1, uri: https://spec.edmcouncil.org/fibo/ontology/FBC/FunctionalEntities/NorthAmericanEntities/USRegulatoryAgencies/InternalRevenueService)
// Mandatory class relationship: hasTaxableIncome -> monetary amount (cardinality: 1, uri: https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/MonetaryAmount)
// Mandatory enum relationship: hasReportStatus -> reportStatus (cardinality: 1, uri: https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/Reporting/ReportStatusConcept). members=['Accepted', 'Draft', 'Rejected', 'Submitted']
// Mandatory class relationship: hasAGI -> monetary amount (cardinality: 1, uri: https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/MonetaryAmount)
// Mandatory class relationship: hasTotalTax -> monetary amount (cardinality: 1, uri: https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/MonetaryAmount)
// Mandatory class relationship: hasTotalPayments -> monetary amount (cardinality: 1, uri: https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/MonetaryAmount)
// Mandatory class relationship: hasRefundAmount -> monetary amount (cardinality: 1, uri: https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/MonetaryAmount)
// Mandatory class relationship: hasAmountOwed -> monetary amount (cardinality: 1, uri: https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/MonetaryAmount)
// Mandatory class relationship: hasLine1aWages -> monetary amount (cardinality: 1, uri: https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/MonetaryAmount)
// Mandatory class relationship: hasLine2bTaxableInterest -> monetary amount (cardinality: 1, uri: https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/MonetaryAmount)
// Mandatory class relationship: hasLine3bOrdinaryDividends -> monetary amount (cardinality: 1, uri: https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/MonetaryAmount)
// Mandatory class relationship: hasLine6bTaxableSocialSecurity -> monetary amount (cardinality: 1, uri: https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/MonetaryAmount)
// Mandatory class relationship: hasLine12StandardDeduction -> monetary amount (cardinality: 1, uri: https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/MonetaryAmount)
// Mandatory class relationship: hasLine16TaxValue -> monetary amount (cardinality: 1, uri: https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/MonetaryAmount)
// Mandatory class relationship: hasLine19ChildTaxCredit -> monetary amount (cardinality: 1, uri: https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/MonetaryAmount)
// Mandatory class relationship: hasLine24TotalTax -> monetary amount (cardinality: 1, uri: https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/MonetaryAmount)
// Mandatory class relationship: hasLine33TotalPayments -> monetary amount (cardinality: 1, uri: https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/MonetaryAmount)

// Class: Form 1120 U.S. Corporation Income Tax Return
// Definition: An Internal Revenue Service tax form used by U.S. C corporations to report annual income, gains, losses, deductions, credits, and resulting federal corporate income tax liability.
// URI: https://spec.edmcouncil.org/fibo/ontology/TAX/USFederalTax/Form1120

// Class: W-2 form
// Definition: IRS Form W-2, Wage and Tax Statement, used by employers to report wages paid and taxes withheld for each employee.
// URI: https://example.org/ontology/W2Form
// Mandatory property: isProvidedBy (cardinality: 1..*)
CREATE CONSTRAINT W2Form_isProvidedBy_Required IF NOT EXISTS FOR (n:`W2Form`) REQUIRE n.`isProvidedBy` IS NOT NULL;
// Mandatory property: hasWagesTipsOtherComp (cardinality: 1)
CREATE CONSTRAINT W2Form_hasWagesTipsOtherComp_Required IF NOT EXISTS FOR (n:`W2Form`) REQUIRE n.`hasWagesTipsOtherComp` IS NOT NULL;
// Mandatory property: hasFederalIncomeTaxWithheld (cardinality: 1)
CREATE CONSTRAINT W2Form_hasFederalIncomeTaxWithheld_Required IF NOT EXISTS FOR (n:`W2Form`) REQUIRE n.`hasFederalIncomeTaxWithheld` IS NOT NULL;
// Mandatory property: hasSocialSecurityWages (cardinality: 1)
CREATE CONSTRAINT W2Form_hasSocialSecurityWages_Required IF NOT EXISTS FOR (n:`W2Form`) REQUIRE n.`hasSocialSecurityWages` IS NOT NULL;
// Mandatory property: hasSocialSecurityTaxWithheld (cardinality: 1)
CREATE CONSTRAINT W2Form_hasSocialSecurityTaxWithheld_Required IF NOT EXISTS FOR (n:`W2Form`) REQUIRE n.`hasSocialSecurityTaxWithheld` IS NOT NULL;
// Mandatory property: hasMedicareWagesAndTips (cardinality: 1)
CREATE CONSTRAINT W2Form_hasMedicareWagesAndTips_Required IF NOT EXISTS FOR (n:`W2Form`) REQUIRE n.`hasMedicareWagesAndTips` IS NOT NULL;
// Mandatory property: hasMedicareTaxWithheld (cardinality: 1)
CREATE CONSTRAINT W2Form_hasMedicareTaxWithheld_Required IF NOT EXISTS FOR (n:`W2Form`) REQUIRE n.`hasMedicareTaxWithheld` IS NOT NULL;
// Mandatory property: hasTaxYear (cardinality: 1)
CREATE CONSTRAINT W2Form_hasTaxYear_Required IF NOT EXISTS FOR (n:`W2Form`) REQUIRE n.`hasTaxYear` IS NOT NULL;
// Mandatory enum relationship: hasReportStatus -> reportStatus (cardinality: 1, uri: https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/Reporting/ReportStatusConcept). members=['Accepted', 'Draft', 'Rejected', 'Submitted']
// Mandatory class relationship: issuedBy -> employer (cardinality: 1, uri: https://example.org/ontology/Employer)
// Mandatory class relationship: issuedTo -> person (cardinality: 1, uri: https://spec.edmcouncil.org/fibo/ontology/FND/AgentsAndPeople/People/Person)

// Class: crypto asset
// Definition: A digital asset designed to work as a medium of exchange.
// URI: https://model.onto2ai.com/schema/CryptoAsset
// Mandatory property: hasTokenSymbol (cardinality: 1)
CREATE CONSTRAINT CryptoAsset_hasTokenSymbol_Required IF NOT EXISTS FOR (n:`CryptoAsset`) REQUIRE n.`hasTokenSymbol` IS NOT NULL;

// Class: currency
// Definition: medium of exchange
// URI: https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/Currency

// Class: employer
// Definition: A legal person or formal organization that employs one or more individuals and is responsible for withholding and reporting taxes.
// URI: https://example.org/ontology/Employer
// Mandatory property: hasAddress (cardinality: 1..*)
CREATE CONSTRAINT Employer_hasAddress_Required IF NOT EXISTS FOR (n:`Employer`) REQUIRE n.`hasAddress` IS NOT NULL;
// Mandatory property: hasEmployerName (cardinality: 1)
CREATE CONSTRAINT Employer_hasEmployerName_Required IF NOT EXISTS FOR (n:`Employer`) REQUIRE n.`hasEmployerName` IS NOT NULL;
// Mandatory property: hasEIN (cardinality: 1)
CREATE CONSTRAINT Employer_hasEIN_Required IF NOT EXISTS FOR (n:`Employer`) REQUIRE n.`hasEIN` IS NOT NULL;

// Class: exchange
// Definition: A marketplace where securities, commodities, derivatives and other financial instruments are traded.
// URI: https://model.onto2ai.com/schema/Exchange

// Class: filing status concept
// Definition: concept representing the legal status of a taxpayer for filing purposes
// URI: https://spec.edmcouncil.org/fibo/ontology/TAX/TaxFiling/FilingStatusConcept

// Class: individual tax return
// Definition: A tax return filed by an individual person.
// URI: https://spec.edmcouncil.org/fibo/ontology/TAX/TaxFiling/IndividualTaxReturn
// Mandatory property: isProvidedBy (cardinality: 1..*)
CREATE CONSTRAINT IndividualTaxReturn_isProvidedBy_Required IF NOT EXISTS FOR (n:`IndividualTaxReturn`) REQUIRE n.`isProvidedBy` IS NOT NULL;
// Mandatory named_individual relationship: isSubmittedTo -> Internal Revenue Service (cardinality: 1, uri: https://spec.edmcouncil.org/fibo/ontology/FBC/FunctionalEntities/NorthAmericanEntities/USRegulatoryAgencies/InternalRevenueService)
// Mandatory class relationship: hasTaxableIncome -> monetary amount (cardinality: 1, uri: https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/MonetaryAmount)
// Mandatory enum relationship: hasReportStatus -> reportStatus (cardinality: 1, uri: https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/Reporting/ReportStatusConcept). members=['Accepted', 'Draft', 'Rejected', 'Submitted']
// Mandatory class relationship: hasAGI -> monetary amount (cardinality: 1, uri: https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/MonetaryAmount)
// Mandatory class relationship: hasTotalTax -> monetary amount (cardinality: 1, uri: https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/MonetaryAmount)
// Mandatory class relationship: hasTotalPayments -> monetary amount (cardinality: 1, uri: https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/MonetaryAmount)
// Mandatory class relationship: hasRefundAmount -> monetary amount (cardinality: 1, uri: https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/MonetaryAmount)
// Mandatory class relationship: hasAmountOwed -> monetary amount (cardinality: 1, uri: https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/MonetaryAmount)
// Mandatory class relationship: hasLine1aWages -> monetary amount (cardinality: 1, uri: https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/MonetaryAmount)
// Mandatory class relationship: hasLine2bTaxableInterest -> monetary amount (cardinality: 1, uri: https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/MonetaryAmount)
// Mandatory class relationship: hasLine3bOrdinaryDividends -> monetary amount (cardinality: 1, uri: https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/MonetaryAmount)
// Mandatory class relationship: hasLine6bTaxableSocialSecurity -> monetary amount (cardinality: 1, uri: https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/MonetaryAmount)
// Mandatory class relationship: hasLine12StandardDeduction -> monetary amount (cardinality: 1, uri: https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/MonetaryAmount)
// Mandatory class relationship: hasLine16TaxValue -> monetary amount (cardinality: 1, uri: https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/MonetaryAmount)
// Mandatory class relationship: hasLine19ChildTaxCredit -> monetary amount (cardinality: 1, uri: https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/MonetaryAmount)
// Mandatory class relationship: hasLine24TotalTax -> monetary amount (cardinality: 1, uri: https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/MonetaryAmount)
// Mandatory class relationship: hasLine33TotalPayments -> monetary amount (cardinality: 1, uri: https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/MonetaryAmount)

// Class: jurisdiction
// Definition: power of a court or regulatory agency to adjudicate cases, issue orders, and interpret and apply the law with respect to some specific geographic area
// URI: https://www.omg.org/spec/Commons/RegulatoryAgencies/Jurisdiction

// Class: monetary amount
// Definition: A quantity of money, denominated in a specific currency.
// URI: https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/MonetaryAmount
// Mandatory property: hasAmount (cardinality: 1)
CREATE CONSTRAINT MonetaryAmount_hasAmount_Required IF NOT EXISTS FOR (n:`MonetaryAmount`) REQUIRE n.`hasAmount` IS NOT NULL;
// Mandatory enum relationship: isDenominatedIn -> currency (cardinality: 1, uri: https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/Currency). members=['Australian Dollar', 'British Pound (Sterling)', 'Canadian Dollar', 'Chinese Yuan', 'Euro']

// Class: organization
// Definition: framework of authority within which a person, persons, or groups of people act, or are designated to act, towards some purpose, such as to meet a need or pursue collective goals
// URI: https://www.omg.org/spec/Commons/Organizations/Organization

// Class: person
// Definition: individual human being, with consciousness of self
// URI: https://spec.edmcouncil.org/fibo/ontology/FND/AgentsAndPeople/People/Person
// Mandatory property: hasDateOfBirth (cardinality: 1)
CREATE CONSTRAINT Person_hasDateOfBirth_Required IF NOT EXISTS FOR (n:`Person`) REQUIRE n.`hasDateOfBirth` IS NOT NULL;
// Mandatory property: hasPlaceOfBirth (cardinality: 1)
CREATE CONSTRAINT Person_hasPlaceOfBirth_Required IF NOT EXISTS FOR (n:`Person`) REQUIRE n.`hasPlaceOfBirth` IS NOT NULL;

// Class: physical address
// Definition: A physical address is a structured specification of the real-world location of a premises, such as a residence or business site, used to identify where a party is situated or an activity occurs for financial operations, regulatory reporting, and tax jurisdiction determination.
// URI: https://spec.edmcouncil.org/fibo/ontology/FND/Places/Addresses/PhysicalAddress

// Class: reportStatus
// Definition: lifecycle status of a report
// URI: https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/Reporting/ReportStatusConcept

// Class: tax authority
// Definition: functional entity that is responsible for the administration and enforcement of tax laws
// URI: https://spec.edmcouncil.org/fibo/ontology/FBC/FunctionalEntities/RegulatoryAgencies/TaxAuthority
// Mandatory enum relationship: hasJurisdiction -> jurisdiction (cardinality: 1..*, uri: https://www.omg.org/spec/Commons/RegulatoryAgencies/Jurisdiction). members=['United States jurisdiction']

// Class: tax payer
// Definition: A person who is obligated to pay taxes and is identified by a tax identifier.
// URI: https://example.org/ontology/TaxPayer
// Mandatory property: hasDateOfBirth (cardinality: 1)
CREATE CONSTRAINT TaxPayer_hasDateOfBirth_Required IF NOT EXISTS FOR (n:`TaxPayer`) REQUIRE n.`hasDateOfBirth` IS NOT NULL;
// Mandatory property: hasPlaceOfBirth (cardinality: 1)
CREATE CONSTRAINT TaxPayer_hasPlaceOfBirth_Required IF NOT EXISTS FOR (n:`TaxPayer`) REQUIRE n.`hasPlaceOfBirth` IS NOT NULL;
