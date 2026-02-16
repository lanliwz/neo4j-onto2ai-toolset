# Staging Database Schema Description

## Node Labels (Classes)

| Label | URI | Definition |
|---|---|---|
| Organization | [https://www.omg.org/spec/Commons/Organizations/Organization](https://www.omg.org/spec/Commons/Organizations/Organization) | framework of authority within which a person, persons, or groups of people act, or are designated to act, towards some purpose, such as to meet a need or pursue collective goals |
| Exchange | [https://model.onto2ai.com/schema/Exchange](https://model.onto2ai.com/schema/Exchange) | A marketplace where securities, commodities, derivatives and other financial instruments are traded. |
| W2Form | [https://example.org/ontology/W2Form](https://example.org/ontology/W2Form) | IRS Form W-2, Wage and Tax Statement, used by employers to report wages paid and taxes withheld for each employee. |
| CryptoAsset | [https://model.onto2ai.com/schema/CryptoAsset](https://model.onto2ai.com/schema/CryptoAsset) | A digital asset designed to work as a medium of exchange. |
| TaxAuthority | [https://spec.edmcouncil.org/fibo/ontology/FBC/FunctionalEntities/RegulatoryAgencies/TaxAuthority](https://spec.edmcouncil.org/fibo/ontology/FBC/FunctionalEntities/RegulatoryAgencies/TaxAuthority) | functional entity that is responsible for the administration and enforcement of tax laws |
| Person | [https://spec.edmcouncil.org/fibo/ontology/FND/AgentsAndPeople/People/Person](https://spec.edmcouncil.org/fibo/ontology/FND/AgentsAndPeople/People/Person) | individual human being, with consciousness of self |
| Jurisdiction | [https://www.omg.org/spec/Commons/RegulatoryAgencies/Jurisdiction](https://www.omg.org/spec/Commons/RegulatoryAgencies/Jurisdiction) | power of a court or regulatory agency to adjudicate cases, issue orders, and interpret and apply the law with respect to some specific geographic area |
| PhysicalAddress | [https://spec.edmcouncil.org/fibo/ontology/FND/Places/Addresses/PhysicalAddress](https://spec.edmcouncil.org/fibo/ontology/FND/Places/Addresses/PhysicalAddress) | A physical address is a structured specification of the real-world location of a premises, such as a residence or business site, used to identify where a party is situated or an activity occurs for financial operations, regulatory reporting, and tax jurisdiction determination. |
| FilingStatusConcept | [https://spec.edmcouncil.org/fibo/ontology/TAX/TaxFiling/FilingStatusConcept](https://spec.edmcouncil.org/fibo/ontology/TAX/TaxFiling/FilingStatusConcept) | concept representing the legal status of a taxpayer for filing purposes |
| ReportStatus | [https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/Reporting/ReportStatusConcept](https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/Reporting/ReportStatusConcept) | lifecycle status of a report |
| Form1120U.S.CorporationIncomeTaxReturn | [https://spec.edmcouncil.org/fibo/ontology/TAX/USFederalTax/Form1120](https://spec.edmcouncil.org/fibo/ontology/TAX/USFederalTax/Form1120) | An Internal Revenue Service tax form used by U.S. C corporations to report annual income, gains, losses, deductions, credits, and resulting federal corporate income tax liability. |
| IndividualTaxReturn | [https://spec.edmcouncil.org/fibo/ontology/TAX/TaxFiling/IndividualTaxReturn](https://spec.edmcouncil.org/fibo/ontology/TAX/TaxFiling/IndividualTaxReturn) | A tax return filed by an individual person. |
| MonetaryAmount | [https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/MonetaryAmount](https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/MonetaryAmount) | A quantity of money, denominated in a specific currency. |
| Currency | [https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/Currency](https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/Currency) | medium of exchange |
| 2025Form1040 | [https://example.org/tax/filings/2025-Form1040](https://example.org/tax/filings/2025-Form1040) | The IRS Form 1040 for tax year 2025, used by U.S. individual taxpayers to file their annual federal income tax return and report income, deductions, credits, and tax liability. |
| TaxPayer | [https://example.org/ontology/TaxPayer](https://example.org/ontology/TaxPayer) | A person who is obligated to pay taxes and is identified by a tax identifier. |
| Employer | [https://example.org/ontology/Employer](https://example.org/ontology/Employer) | A legal person or formal organization that employs one or more individuals and is responsible for withholding and reporting taxes. |


## Relationship Types

| Relationship | URI | Definition | Cardinality |
|---|---|---|---|
| isTradedOn | [https://model.onto2ai.com/schema/isTradedOn](https://model.onto2ai.com/schema/isTradedOn) | Indicates the exchange where the asset is listed. | 0..* |
| issuedTo | [-](-) | employee who received the W-2 | 1 |
| hasJurisdiction | [https://www.omg.org/spec/Commons/RegulatoryAgencies/hasJurisdiction](https://www.omg.org/spec/Commons/RegulatoryAgencies/hasJurisdiction) | Relates a tax authority to the jurisdiction over which it has legal or regulatory authority to administer and enforce tax laws. | 1..* |
| hasReportStatus | [https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/Reporting/hasReportStatus](https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/Reporting/hasReportStatus) | Links a W-2 form to the report status that indicates its reporting state for filing and compliance purposes. | 1 |
| hasReportStatus | [https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/Reporting/hasReportStatus](https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/Reporting/hasReportStatus) | Relates an individual tax return to the report status that indicates its current reporting state (e.g., filed, pending, accepted, rejected) for reporting purposes. | 1 |
| hasTaxableIncome | [https://spec.edmcouncil.org/fibo/ontology/TAX/USFederalTax/hasTaxableIncome](https://spec.edmcouncil.org/fibo/ontology/TAX/USFederalTax/hasTaxableIncome) | Relates an individual tax return to the monetary amount representing the taxpayer’s taxable income as determined for that return under applicable U.S. federal tax rules. | 1 |
| hasAGI | [https://spec.edmcouncil.org/fibo/ontology/TAX/USFederalTax/hasAGI](https://spec.edmcouncil.org/fibo/ontology/TAX/USFederalTax/hasAGI) | Relates an individual tax return to the monetary amount representing the filer’s adjusted gross income (AGI) reported for that return. | 1 |
| hasTotalTax | [https://spec.edmcouncil.org/fibo/ontology/TAX/USFederalTax/hasTotalTax](https://spec.edmcouncil.org/fibo/ontology/TAX/USFederalTax/hasTotalTax) | Relates an individual tax return to the monetary amount representing the total tax liability computed for that return for the applicable tax year. | 1 |
| hasTotalPayments | [https://spec.edmcouncil.org/fibo/ontology/TAX/USFederalTax/hasTotalPayments](https://spec.edmcouncil.org/fibo/ontology/TAX/USFederalTax/hasTotalPayments) | Relates an individual tax return to the aggregate monetary amount representing the total payments credited toward the taxpayer’s tax liability for the tax period covered by the return. | 1 |
| hasRefundAmount | [https://spec.edmcouncil.org/fibo/ontology/TAX/USFederalTax/hasRefundAmount](https://spec.edmcouncil.org/fibo/ontology/TAX/USFederalTax/hasRefundAmount) | Relates an individual tax return to the monetary amount of any refund due to the filer as determined on that return. | 1 |
| hasAmountOwed | [https://spec.edmcouncil.org/fibo/ontology/TAX/USFederalTax/hasAmountOwed](https://spec.edmcouncil.org/fibo/ontology/TAX/USFederalTax/hasAmountOwed) | Relates an individual tax return to the monetary amount of tax liability owed by the filer for the return period. | 1 |
| hasLine1aWages | [https://example.org/tax/irs/hasLine1a](https://example.org/tax/irs/hasLine1a) | Relates an individual tax return to the monetary amount reported as wages on Line 1a of the return. | 1 |
| hasLine2bTaxableInterest | [https://example.org/tax/irs/hasLine2b](https://example.org/tax/irs/hasLine2b) | Relates an individual tax return to the monetary amount reported as taxable interest on IRS Form 1040, line 2b. | 1 |
| hasLine3bOrdinaryDividends | [https://example.org/tax/irs/hasLine3b](https://example.org/tax/irs/hasLine3b) | Relates an individual tax return to the monetary amount reported as ordinary dividends on IRS Form 1040, Line 3b. | 1 |
| hasLine6bTaxableSocialSecurity | [https://example.org/tax/irs/hasLine6b](https://example.org/tax/irs/hasLine6b) | Relates an individual tax return to the monetary amount reported as taxable Social Security benefits on IRS Form 1040 line 6b. | 1 |
| hasLine12StandardDeduction | [https://example.org/tax/irs/hasLine12](https://example.org/tax/irs/hasLine12) | Relates an individual tax return to the monetary amount reported as the standard deduction on Line 12 of the return. | 1 |
| hasLine16TaxValue | [https://example.org/tax/irs/hasLine16](https://example.org/tax/irs/hasLine16) | Relates an individual tax return to the monetary amount reported as tax on Line 16 of the return. | 1 |
| hasLine19ChildTaxCredit | [https://example.org/tax/irs/hasLine19](https://example.org/tax/irs/hasLine19) | Relates an individual tax return to the monetary amount reported on IRS Form 1040, line 19, representing the Child Tax Credit claimed for the tax year. | 1 |
| hasLine24TotalTax | [https://example.org/tax/irs/hasLine24](https://example.org/tax/irs/hasLine24) | Relates an individual tax return to the monetary amount reported as its total tax on IRS Form 1040, line 24. | 1 |
| hasLine33TotalPayments | [https://example.org/tax/irs/hasLine33](https://example.org/tax/irs/hasLine33) | Relates an individual tax return to the monetary amount reported as the total payments on Line 33. | 1 |
| isDenominatedIn | [https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/isDenominatedIn](https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/isDenominatedIn) | Relates a monetary amount to the currency in which that amount is expressed. | 1 |
| isEmployedBy | [https://spec.edmcouncil.org/fibo/ontology/FND/Organizations/FormalOrganizations/isEmployedBy](https://spec.edmcouncil.org/fibo/ontology/FND/Organizations/FormalOrganizations/isEmployedBy) | indicates the employer | 0..* |
| isEmployedBy | [https://spec.edmcouncil.org/fibo/ontology/FND/Organizations/FormalOrganizations/isEmployedBy](https://spec.edmcouncil.org/fibo/ontology/FND/Organizations/FormalOrganizations/isEmployedBy) | indicates the employer | 0..* |
| issuedBy | [-](-) | employer that issued the W-2 | 1 |


## Node Properties

| Node Label | Property | Data Type | Mandatory |
|---|---|---|---|
| Organization | hasTaxId | xsd:string | optional |
| Organization | hasEIN | xsd:string | optional |
| W2Form | isProvidedBy | ReportingParty | 1..* |
| W2Form | hasReportDateTime | DateTime | 0..* |
| W2Form | isSubmittedBy | Submitter | 0..* |
| W2Form | hasWagesTipsOtherComp | xsd:decimal | 1 |
| W2Form | hasFederalIncomeTaxWithheld | xsd:decimal | 1 |
| W2Form | hasSocialSecurityWages | xsd:decimal | 1 |
| W2Form | hasSocialSecurityTaxWithheld | xsd:decimal | 1 |
| W2Form | hasMedicareWagesAndTips | xsd:decimal | 1 |
| W2Form | hasMedicareTaxWithheld | xsd:decimal | 1 |
| W2Form | hasSocialSecurityTips | xsd:decimal | 0..1 |
| W2Form | hasAllocatedTips | xsd:decimal | 0..1 |
| W2Form | hasDependentCareBenefits | xsd:decimal | 0..1 |
| W2Form | hasNonqualifiedPlans | xsd:decimal | 0..1 |
| W2Form | hasBox12Codes | xsd:string | 0..* |
| W2Form | isStatutoryEmployee | xsd:boolean | 0..1 |
| W2Form | hasRetirementPlan | xsd:boolean | 0..1 |
| W2Form | hasThirdPartySickPay | xsd:boolean | 0..1 |
| W2Form | hasOtherInfo | xsd:string | 0..* |
| W2Form | hasTaxYear | xsd:integer | 1 |
| CryptoAsset | hasTokenSymbol | String | 1 |
| Person | hasAge | Age | 0..* |
| Person | hasCitizenship | Citizenship | 0..* |
| Person | hasDateOfBirth | DateOfBirth | 1 |
| Person | hasDateOfDeath | DateOfDeath | 0..1 |
| Person | hasName | PersonName | 0..* |
| Person | hasPlaceOfBirth | BirthPlace | 1 |
| Person | hasResidence | FullAddress | 0..* |
| Person | hasTaxId | Ssn | optional |
| Person | hasTaxId | Itin | optional |
| IndividualTaxReturn | isProvidedBy | ReportingParty | 1..* |
| IndividualTaxReturn | hasReportDateTime | DateTime | 0..* |
| IndividualTaxReturn | isSubmittedBy | Submitter | 0..* |
| TaxPayer | hasAge | Age | 0..* |
| TaxPayer | hasCitizenship | Citizenship | 0..* |
| TaxPayer | hasDateOfBirth | DateOfBirth | 1 |
| TaxPayer | hasDateOfDeath | DateOfDeath | 0..1 |
| TaxPayer | hasName | PersonName | 0..* |
| TaxPayer | hasPlaceOfBirth | BirthPlace | 1 |
| TaxPayer | hasResidence | FullAddress | 0..* |
| TaxPayer | hasTaxId | Ssn | optional |
| TaxPayer | hasTaxId | Itin | optional |
| Employer | hasAddress | FullAddress | 1..* |
| Employer | hasEmployerName | xsd:string | 1 |
| Employer | hasEIN | xsd:string | 1 |
| Employer | hasPhoneNumber | xsd:string | 0..* |


## Graph Topology

- `(:CryptoAsset)-[:isTradedOn]->(:Exchange)`
- `(:W2Form)-[:issuedTo]->(:Person)`
- `(:TaxAuthority)-[:hasJurisdiction]->(:Jurisdiction)`
- `(:W2Form)-[:hasReportStatus]->(:ReportStatus)`
- `(:IndividualTaxReturn)-[:hasReportStatus]->(:ReportStatus)`
- `(:IndividualTaxReturn)-[:hasTaxableIncome]->(:MonetaryAmount)`
- `(:IndividualTaxReturn)-[:hasAGI]->(:MonetaryAmount)`
- `(:IndividualTaxReturn)-[:hasTotalTax]->(:MonetaryAmount)`
- `(:IndividualTaxReturn)-[:hasTotalPayments]->(:MonetaryAmount)`
- `(:IndividualTaxReturn)-[:hasRefundAmount]->(:MonetaryAmount)`
- `(:IndividualTaxReturn)-[:hasAmountOwed]->(:MonetaryAmount)`
- `(:IndividualTaxReturn)-[:hasLine1aWages]->(:MonetaryAmount)`
- `(:IndividualTaxReturn)-[:hasLine2bTaxableInterest]->(:MonetaryAmount)`
- `(:IndividualTaxReturn)-[:hasLine3bOrdinaryDividends]->(:MonetaryAmount)`
- `(:IndividualTaxReturn)-[:hasLine6bTaxableSocialSecurity]->(:MonetaryAmount)`
- `(:IndividualTaxReturn)-[:hasLine12StandardDeduction]->(:MonetaryAmount)`
- `(:IndividualTaxReturn)-[:hasLine16TaxValue]->(:MonetaryAmount)`
- `(:IndividualTaxReturn)-[:hasLine19ChildTaxCredit]->(:MonetaryAmount)`
- `(:IndividualTaxReturn)-[:hasLine24TotalTax]->(:MonetaryAmount)`
- `(:IndividualTaxReturn)-[:hasLine33TotalPayments]->(:MonetaryAmount)`
- `(:MonetaryAmount)-[:isDenominatedIn]->(:Currency)`
- `(:Person)-[:isEmployedBy]->(:Employer)`
- `(:TaxPayer)-[:isEmployedBy]->(:Employer)`
- `(:W2Form)-[:issuedBy]->(:Employer)`

