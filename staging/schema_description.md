# Neo4j Schema Prompt

## Section 1: Node Labels (Classes)

| Label | URI | Definition |
| --- | --- | --- |
| W2Form | https://example.org/ontology/W2Form | IRS Form W-2, Wage and Tax Statement, used by employers to report wages paid and taxes withheld for each employee. |
| CryptoAsset | https://model.onto2ai.com/schema/CryptoAsset | A digital asset designed to work as a medium of exchange. |
| TaxAuthority | https://spec.edmcouncil.org/fibo/ontology/FBC/FunctionalEntities/RegulatoryAgencies/TaxAuthority | functional entity that is responsible for the administration and enforcement of tax laws |
| Person | https://spec.edmcouncil.org/fibo/ontology/FND/AgentsAndPeople/People/Person | individual human being, with consciousness of self |
| IndividualTaxReturn | https://spec.edmcouncil.org/fibo/ontology/TAX/TaxFiling/IndividualTaxReturn | A tax return filed by an individual person. |
| MonetaryAmount | https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/MonetaryAmount | A quantity of money, denominated in a specific currency. |
| Form1040_2025 | https://example.org/tax/filings/2025-Form1040 | The IRS Form 1040 for tax year 2025, used by U.S. individual taxpayers to file their annual federal income tax return and report income, deductions, credits, and tax liability. |
| TaxPayer | https://example.org/ontology/TaxPayer | A person who is obligated to pay taxes and is identified by a tax identifier. |
| Employer | https://example.org/ontology/Employer | A legal person or formal organization that employs one or more individuals and is responsible for withholding and reporting taxes. |
| Organization | https://www.omg.org/spec/Commons/Organizations/Organization | framework of authority within which a person, persons, or groups of people act, or are designated to act, towards some purpose, such as to meet a need or pursue collective goals |

## Section 2: Relationship Types

| Relationship | URI | Definition | Cardinality |
| --- | --- | --- | --- |
| hasAGI | https://spec.edmcouncil.org/fibo/ontology/TAX/USFederalTax/hasAGI | Relates an individual tax return to the monetary amount representing the filer’s adjusted gross income (AGI) reported for that return. | 1 |
| hasAmountOwed | https://spec.edmcouncil.org/fibo/ontology/TAX/USFederalTax/hasAmountOwed | Relates an individual tax return to the monetary amount of tax liability owed by the filer for the return period. | 1 |
| hasJurisdiction | https://www.omg.org/spec/Commons/RegulatoryAgencies/hasJurisdiction | Relates a tax authority to the jurisdiction over which it has legal or regulatory authority to administer and enforce tax laws. | 1..* |
| hasLine12StandardDeduction | https://example.org/tax/irs/hasLine12 | Relates an individual tax return to the monetary amount reported as the standard deduction on Line 12 of the return. | 1 |
| hasLine16TaxValue | https://example.org/tax/irs/hasLine16 | Relates an individual tax return to the monetary amount reported as tax on Line 16 of the return. | 1 |
| hasLine19ChildTaxCredit | https://example.org/tax/irs/hasLine19 | Relates an individual tax return to the monetary amount reported on IRS Form 1040, line 19, representing the Child Tax Credit claimed for the tax year. | 1 |
| hasLine1aWages | https://example.org/tax/irs/hasLine1a | Relates an individual tax return to the monetary amount reported as wages on Line 1a of the return. | 1 |
| hasLine24TotalTax | https://example.org/tax/irs/hasLine24 | Relates an individual tax return to the monetary amount reported as its total tax on IRS Form 1040, line 24. | 1 |
| hasLine2bTaxableInterest | https://example.org/tax/irs/hasLine2b | Relates an individual tax return to the monetary amount reported as taxable interest on IRS Form 1040, line 2b. | 1 |
| hasLine33TotalPayments | https://example.org/tax/irs/hasLine33 | Relates an individual tax return to the monetary amount reported as the total payments on Line 33. | 1 |
| hasLine3bOrdinaryDividends | https://example.org/tax/irs/hasLine3b | Relates an individual tax return to the monetary amount reported as ordinary dividends on IRS Form 1040, Line 3b. | 1 |
| hasLine6bTaxableSocialSecurity | https://example.org/tax/irs/hasLine6b | Relates an individual tax return to the monetary amount reported as taxable Social Security benefits on IRS Form 1040 line 6b. | 1 |
| hasRefundAmount | https://spec.edmcouncil.org/fibo/ontology/TAX/USFederalTax/hasRefundAmount | Relates an individual tax return to the monetary amount of any refund due to the filer as determined on that return. | 1 |
| hasReportStatus | https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/Reporting/hasReportStatus | Links a W-2 form to the report status that indicates its reporting state for filing and compliance purposes. | 1 |
| hasTaxableIncome | https://spec.edmcouncil.org/fibo/ontology/TAX/USFederalTax/hasTaxableIncome | Relates an individual tax return to the monetary amount representing the taxpayer’s taxable income as determined for that return under applicable U.S. federal tax rules. | 1 |
| hasTotalPayments | https://spec.edmcouncil.org/fibo/ontology/TAX/USFederalTax/hasTotalPayments | Relates an individual tax return to the aggregate monetary amount representing the total payments credited toward the taxpayer’s tax liability for the tax period covered by the return. | 1 |
| hasTotalTax | https://spec.edmcouncil.org/fibo/ontology/TAX/USFederalTax/hasTotalTax | Relates an individual tax return to the monetary amount representing the total tax liability computed for that return for the applicable tax year. | 1 |
| isDenominatedIn | https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/isDenominatedIn | Relates a monetary amount to the currency in which that amount is expressed. | 1 |
| isEmployedBy | https://spec.edmcouncil.org/fibo/ontology/FND/Organizations/FormalOrganizations/isEmployedBy | indicates the employer | 0..* |
| isSubmittedTo | https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/Reporting/isSubmittedTo | identifies the party to which the report is submitted | 1 |
| isTradedOn | https://model.onto2ai.com/schema/isTradedOn | Indicates the exchange where the asset is listed. | 0..* |
| issuedBy |  | employer that issued the W-2 | 1 |
| issuedTo |  | employee who received the W-2 | 1 |

## Section 3: Node Properties

| Node Label | Property | Data Type | Mandatory |
| --- | --- | --- | --- |
| W2Form | hasAllocatedTips | allocatedTips | No |
| W2Form | hasBox12Codes | box12Codes | No |
| W2Form | hasDependentCareBenefits | dependentCareBenefits | No |
| W2Form | hasFederalIncomeTaxWithheld | federalIncomeTaxWithheld | Yes |
| W2Form | hasMedicareTaxWithheld | medicareTaxWithheld | Yes |
| W2Form | hasMedicareWagesAndTips | medicareWagesAndTips | Yes |
| W2Form | hasNonqualifiedPlans | nonqualifiedPlans | No |
| W2Form | hasOtherInfo | otherInfo | No |
| W2Form | hasReportDateTime | dateTime | No |
| W2Form | hasRetirementPlan | retirementPlan | No |
| W2Form | hasSocialSecurityTaxWithheld | socialSecurityTaxWithheld | Yes |
| W2Form | hasSocialSecurityTips | socialSecurityTips | No |
| W2Form | hasSocialSecurityWages | socialSecurityWages | Yes |
| W2Form | hasTaxYear | taxYear | Yes |
| W2Form | hasThirdPartySickPay | thirdPartySickPay | No |
| W2Form | hasWagesTipsOtherComp | wagesTipsOtherComp | Yes |
| W2Form | isProvidedBy | reportingParty | Yes |
| W2Form | isStatutoryEmployee | statutoryEmployee | No |
| W2Form | isSubmittedBy | submitter | No |
| CryptoAsset | hasTokenSymbol | string | Yes |
| Person | hasAge | age | No |
| Person | hasCitizenship | citizenship | No |
| Person | hasDateOfBirth | dateOfBirth | Yes |
| Person | hasDateOfDeath | dateOfDeath | No |
| Person | hasName | personName | No |
| Person | hasPlaceOfBirth | birthPlace | Yes |
| Person | hasResidence | fullAddress | No |
| Person | hasTaxId | ssn | No |
| Person | hasTaxId | itin | No |
| IndividualTaxReturn | hasReportDateTime | dateTime | No |
| IndividualTaxReturn | isProvidedBy | reportingParty | Yes |
| IndividualTaxReturn | isSubmittedBy | submitter | No |
| Form1040_2025 | hasReportDateTime | dateTime | No |
| Form1040_2025 | isProvidedBy | reportingParty | Yes |
| Form1040_2025 | isSubmittedBy | submitter | No |
| TaxPayer | hasAge | age | No |
| TaxPayer | hasCitizenship | citizenship | No |
| TaxPayer | hasDateOfBirth | dateOfBirth | Yes |
| TaxPayer | hasDateOfDeath | dateOfDeath | No |
| TaxPayer | hasName | personName | No |
| TaxPayer | hasPlaceOfBirth | birthPlace | Yes |
| TaxPayer | hasResidence | fullAddress | No |
| TaxPayer | hasTaxId | ssn | No |
| TaxPayer | hasTaxId | itin | No |
| TaxPayer | hasTaxId | itin | No |
| Employer | hasAddress | fullAddress | Yes |
| Employer | hasEIN | ein | Yes |
| Employer | hasEmployerName | employerName | Yes |
| Employer | hasPhoneNumber | phoneNumber | No |
| Organization | hasEIN | ein | No |
| Organization | hasTaxId | ein | No |

## Section 4: Graph Topology

- `(:W2Form)-[:hasReportStatus]->(:Reportstatus)`
- `(:W2Form)-[:issuedBy]->(:Employer)`
- `(:W2Form)-[:issuedTo]->(:Person)`
- `(:CryptoAsset)-[:isTradedOn]->(:Exchange)`
- `(:TaxAuthority)-[:hasJurisdiction]->(:Jurisdiction)`
- `(:Person)-[:isEmployedBy]->(:Employer)`
- `(:IndividualTaxReturn)-[:isSubmittedTo]->(:InternalRevenueService)`
- `(:IndividualTaxReturn)-[:hasTaxableIncome]->(:MonetaryAmount)`
- `(:IndividualTaxReturn)-[:hasReportStatus]->(:Reportstatus)`
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
- `(:Form1040_2025)-[:isSubmittedTo]->(:InternalRevenueService)`
- `(:Form1040_2025)-[:hasTaxableIncome]->(:MonetaryAmount)`
- `(:Form1040_2025)-[:hasReportStatus]->(:Reportstatus)`
- `(:Form1040_2025)-[:hasAGI]->(:MonetaryAmount)`
- `(:Form1040_2025)-[:hasTotalTax]->(:MonetaryAmount)`
- `(:Form1040_2025)-[:hasTotalPayments]->(:MonetaryAmount)`
- `(:Form1040_2025)-[:hasRefundAmount]->(:MonetaryAmount)`
- `(:Form1040_2025)-[:hasAmountOwed]->(:MonetaryAmount)`
- `(:Form1040_2025)-[:hasLine1aWages]->(:MonetaryAmount)`
- `(:Form1040_2025)-[:hasLine2bTaxableInterest]->(:MonetaryAmount)`
- `(:Form1040_2025)-[:hasLine3bOrdinaryDividends]->(:MonetaryAmount)`
- `(:Form1040_2025)-[:hasLine6bTaxableSocialSecurity]->(:MonetaryAmount)`
- `(:Form1040_2025)-[:hasLine12StandardDeduction]->(:MonetaryAmount)`
- `(:Form1040_2025)-[:hasLine16TaxValue]->(:MonetaryAmount)`
- `(:Form1040_2025)-[:hasLine19ChildTaxCredit]->(:MonetaryAmount)`
- `(:Form1040_2025)-[:hasLine24TotalTax]->(:MonetaryAmount)`
- `(:Form1040_2025)-[:hasLine33TotalPayments]->(:MonetaryAmount)`
- `(:TaxPayer)-[:isEmployedBy]->(:Employer)`
