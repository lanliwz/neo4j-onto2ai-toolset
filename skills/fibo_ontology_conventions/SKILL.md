---
name: FIBO Ontology Conventions
description: Rules for creating OWL ontologies strictly following the FIBO naming and documentation conventions.
---

# FIBO Ontology Conventions

When creating or refining OWL ontologies that represent financial concepts, you MUST follow these specific conventions, which align with the Financial Industry Business Ontology (FIBO) standards.

## 1. rdfs:label Formatting
All `rdfs:label` tags for Classes, Object Properties, and Data Properties MUST be strictly lowercase.
Special characters (such as hyphens, parentheses, etc.) should generally be removed, leaving only alphanumeric characters and spaces.

**Correct:**
```xml
<rdfs:label>financial instrument</rdfs:label>
<rdfs:label>broker dealer</rdfs:label>
```

**Incorrect:**
```xml
<rdfs:label>Financial Instrument</rdfs:label>
<rdfs:label>Broker-Dealer</rdfs:label>
```

## 2. skos:definition Requirements
All business concepts MUST have a definition provided via the `skos:definition` property.
- Definitions should be formal English sentences describing the entity or relationship in a financial industry context.
- The `skos:definition` tag MUST explicitly include the language attribute: `xml:lang="en"`.
- If a generic description exists, try to find a financial or legal specific description.

**Correct:**
```xml
<skos:definition xml:lang="en">A firm or individual that buys and sells securities for its own account or on behalf of its customers.</skos:definition>
```

**Incorrect:**
```xml
<skos:definition>A broker dealer</skos:definition>
```

## 3. Base URIs, Domain, and Folder Structure
Unless otherwise specified by a local project, new ontology documents and local URIs should use the standard project domain. For Onto2AI toolset, this evaluates to:
`http://www.onto2ai-toolset.com/`

When grouping ontologies by domain (like `bank` or `fibo`), the base URI must reflect this hierarchy:
`http://www.onto2ai-toolset.com/ontology/[domain]/[OntologyName]/`

**Example Ontology Header:**
```xml
<rdf:RDF xmlns="http://www.onto2ai-toolset.com/ontology/bank/AssetManagement#"
     xml:base="http://www.onto2ai-toolset.com/ontology/bank/AssetManagement"
     ...>
```

Furthermore, the physical directory structure MUST map exactly to the URI namespace in the `resource/ontology` folder, translating the domain to a folder (e.g., `www_onto2ai-toolset_com`) and following the URI path.

**Example Folder Structure for the above URI:**
`resource/ontology/www_onto2ai-toolset_com/ontology/bank/AssetManagement.rdf`

## 4. Subclassing FIBO Core Concepts
Where possible, align and subclass new concepts from the core FIBO taxonomy.
- `Party` -> `fibo-fnd-pty-pty:Party`
- `Account` -> `fibo-fbc-pas-caa:CustomerAccount`

Ensure the relevant FIBO namespaces are declared in your XML/RDF header when doing this.

## 5. Acronym Expansion Rules
When extracting labels from raw URIs, specific, common banking acronyms must be fully expanded into formal English to ensure human readability and maintain a clean ontology.

**Mandatory Acronym Expansions:**
- `HO` -> `Head Office`
- `Prm` -> `Primary` / `Ast` -> `Asset` / `Ownr` -> `Owner`
- `Prty` / `Prsn` -> `Party` / `Person`
- `Invc` / `Lnvc` -> `Invoice`
- `Ttee` / `Tste` / `DTtee` -> `Trustee` / `Directed Trustee`
- `Scy` -> `Security`
- `Bene` -> `Beneficiary`
- `Mgr` -> `Manager`
- `Svcr` -> `Servicer`
- `Cstdn` / `Cstdy` -> `Custodian` / `Custody`
- `Lnd Lrd` -> `Landlord`
- `Acctnt` / `Acctg` -> `Accountant` / `Accounting`
- `Csh` -> `Cash` / `Depr` -> `Depository` / `Rcpt` -> `Receipt`
- `WM` -> `Wealth Management` / `SAC` -> `Sub Account`
- `RIA` -> `Registered Investment Advisor`
- `TA` -> `Transfer Agency`
- `PE` -> `Private Equity`
- `LOB` -> `Line of Business`
- `Exctr` -> `Executor`
- `Pwr of Atty` -> `Power of Attorney`
- `Oth` -> `Other` / `Rel` -> `Relationship` / `Agr` -> `Agreement`

**OCR Artifact Handling**
If an OCR string is obviously corrupted but recognizable, replace it with the corrected expansion:
- `Prud` -> `Provider`
- `Revr` / `Rc Vr` -> `Receiver`
- `SgnTy` -> `Signatory`
- `Bhf` -> `Behalf of`
- `Tpty` -> `Triparty` / `Third Party`
- `Xtnl` -> `External`
- `Srvc` -> `Service`

If a term is explicitly "non legal party" or similar syntax originating from "OnNonLglPrty", "OnhonLglPrty", or "OnNonLgiPrty", it should always be expanded to exactly `on non legal party` and its definition should begin with `Acting as [Role] (Applied to an entity not recognized as an independent legal person).`
