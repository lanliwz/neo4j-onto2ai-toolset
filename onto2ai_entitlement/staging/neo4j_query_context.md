# Neo4j Schema Prompt

## Section 1: Node Labels

| Label | Type | URI | Definition |
| --- | --- | --- | --- |
| Column | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/Column | Relational column protected by entitlement rules. |
| ColumnMaskRule | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/ColumnMaskRule | Rule that transforms or redacts sensitive column values. |
| ComparisonOperator | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/ComparisonOperator | Enumeration of comparison operators available to row filter predicates. |
| DenyBehavior | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/DenyBehavior | Enumeration of enforcement behaviors applied when a row filter rule denies access. |
| EntitlementRule | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/EntitlementRule | Abstract superclass for entitlement rules that constrain row visibility or column values. |
| FallbackBehavior | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/FallbackBehavior | Enumeration of fallback behaviors applied when a column mask rule cannot resolve masking inputs. |
| FilterAction | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/FilterAction | Enumeration of actions a row filter rule can apply during entitlement evaluation. |
| JdbcConnectionProfile | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/JdbcConnectionProfile | JDBC endpoint and driver metadata for a target database. |
| MaskAction | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/MaskAction | Enumeration of actions a column mask rule can apply to protected column values. |
| MaskingMethod | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/MaskingMethod | Enumeration of masking or transformation strategies available to column mask rules. |
| MatchMode | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/MatchMode | Enumeration of value cardinality modes expected by a row filter rule. |
| Policy | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/Policy | Bundle of row-filter and/or column-mask rules. |
| PolicyGroup | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/PolicyGroup | Collection of policies mapped to a persona, role, or function. |
| RelationalDatabase | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/RelationalDatabase | JDBC-connectable relational database platform. |
| RowFilterRule | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/RowFilterRule | Rule that restricts row visibility using predicates. |
| RulePriority | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/RulePriority | Enumeration of precedence levels used to order entitlement rules during evaluation. |
| Schema | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/Schema | Relational schema/container for tables. |
| SensitivityClassification | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/SensitivityClassification | Enumeration of data sensitivity levels used to classify relational columns for entitlement and masking decisions. |
| Table | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/Table | Relational table containing columns. |
| User | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/User | Principal that invokes or is evaluated against entitlement policies, including a human actor or an automated process. |
| UserType | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/UserType | Classification of a user by the kind of actor it represents for entitlement evaluation. |
| ValueSourceType | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/ValueSourceType | Enumeration of runtime source categories used to resolve entitlement rule values. |
| AllowFilterAction | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/AllowFilterAction | Filter action that permits access to rows matching the rule predicate. |
| BetweenComparisonOperator | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/BetweenComparisonOperator | Comparison operator requiring a value to fall between two bounds. |
| BlockQueryDenyBehavior | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/BlockQueryDenyBehavior | Deny behavior that blocks the data access request. |
| ConfidentialSensitivityClassification | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/ConfidentialSensitivityClassification | Sensitivity classification for data requiring restricted access because disclosure could create business or privacy risk. |
| DenyFilterAction | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/DenyFilterAction | Filter action that denies access to rows matching the rule predicate. |
| DerivedQueryValueSourceType | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/DerivedQueryValueSourceType | Value source type resolved by executing or evaluating a derived lookup query. |
| EqualsComparisonOperator | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/EqualsComparisonOperator | Comparison operator for equality predicates. |
| HashingMaskingMethod | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/HashingMaskingMethod | Masking method that emits a deterministic hash of the original value. |
| HighPriority | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/HighPriority | Priority level indicating a rule should be evaluated before lower-priority rules. |
| HumanUser | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/HumanUser | User type representing an individual human actor authenticated to access protected data. |
| InListComparisonOperator | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/InListComparisonOperator | Comparison operator requiring a value to appear in an allowed set. |
| InternalSensitivityClassification | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/InternalSensitivityClassification | Sensitivity classification for data intended for internal organizational use. |
| LowPriority | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/LowPriority | Priority level indicating a rule should be evaluated after higher-priority rules. |
| MediumPriority | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/MediumPriority | Priority level indicating a rule should be evaluated with standard precedence. |
| MultipleValuesMatchMode | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/MultipleValuesMatchMode | Match mode indicating the rule expects a collection of comparison values. |
| NoValueMatchMode | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/NoValueMatchMode | Match mode indicating the rule does not require a comparison value. |
| NotEqualsComparisonOperator | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/NotEqualsComparisonOperator | Comparison operator for inequality predicates. |
| NotInListComparisonOperator | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/NotInListComparisonOperator | Comparison operator requiring a value not to appear in a denied set. |
| NullReplacementMaskingMethod | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/NullReplacementMaskingMethod | Masking method that replaces the original value with null. |
| NullifyMaskAction | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/NullifyMaskAction | Mask action that replaces the protected value with null. |
| PatternMaskingMethod | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/PatternMaskingMethod | Masking method that preserves a configured pattern while hiding protected portions of a value. |
| PHISensitivityClassification | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/PHISensitivityClassification | Sensitivity classification for protected health information. |
| PIISensitivityClassification | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/PIISensitivityClassification | Sensitivity classification for personally identifiable information. |
| ProcessUser | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/ProcessUser | User type representing an automated process, service account, or system integration actor. |
| PublicSensitivityClassification | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/PublicSensitivityClassification | Sensitivity classification for data approved for public disclosure. |
| RedactMaskAction | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/RedactMaskAction | Mask action that redacts the protected value. |
| RequestContextValueSourceType | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/RequestContextValueSourceType | Value source type resolved from the current data access request context. |
| RestrictedSensitivityClassification | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/RestrictedSensitivityClassification | Sensitivity classification for highly controlled data requiring strict access and masking governance. |
| ReturnNoRowsDenyBehavior | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/ReturnNoRowsDenyBehavior | Deny behavior that rewrites access to produce an empty result set. |
| ReturnNullFallbackBehavior | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/ReturnNullFallbackBehavior | Fallback behavior that returns null when masking inputs cannot be resolved. |
| RevealMaskAction | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/RevealMaskAction | Mask action that reveals the original value. |
| SessionContextValueSourceType | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/SessionContextValueSourceType | Value source type resolved from the current authenticated session context. |
| SingleValueMatchMode | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/SingleValueMatchMode | Match mode indicating the rule expects one comparison value. |
| StaticLiteralValueSourceType | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/StaticLiteralValueSourceType | Value source type where the rule stores a literal value directly. |
| StaticSubstitutionMaskingMethod | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/StaticSubstitutionMaskingMethod | Masking method that emits a fixed replacement value. |
| SubjectAttributeValueSourceType | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/SubjectAttributeValueSourceType | Value source type resolved from an attribute of the evaluated user or principal. |
| SubstituteMaskAction | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/SubstituteMaskAction | Mask action that substitutes the protected value with a configured replacement. |
| TokenizationMaskingMethod | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/TokenizationMaskingMethod | Masking method that emits a reversible or managed token for the original value. |
| TokenizeMaskAction | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/TokenizeMaskAction | Mask action that replaces the original value with a token. |
| UseDefaultMaskFallbackBehavior | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/UseDefaultMaskFallbackBehavior | Fallback behavior that applies a configured default mask when rule-specific inputs cannot be resolved. |

## Section 2: Relationship Types

| Relationship | URI | Definition | Cardinality |
| --- | --- | --- | --- |
| belongsToDatabase | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/belongsToDatabase | Schema belongs to a relational database. | 1 |
| belongsToSchema | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/belongsToSchema | A table belongs to exactly one schema. | 1 |
| belongsToTable | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/belongsToTable | A column belongs to exactly one table. | 1 |
| connectsTo | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/connectsTo | JDBC profile connects to a target relational database. | 1 |
| hasColumnMaskRule | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/hasColumnMaskRule | Policy contains column masking rules. | 0..* |
| hasComparisonOperator | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/hasComparisonOperator | Associates a row filter rule with the comparison operator used in its predicate. | 0..1 |
| hasDenyBehavior | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/hasDenyBehavior | Associates a row filter rule with the enforcement behavior used when access is denied. | 0..1 |
| hasFallbackBehavior | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/hasFallbackBehavior | Associates a column mask rule with the fallback behavior used when masking inputs cannot be resolved. | 0..1 |
| hasFilterAction | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/hasFilterAction | Associates a row filter rule with the action it applies when rewriting or evaluating a query. | 0..1 |
| hasMaskAction | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/hasMaskAction | Associates a column mask rule with the masking action it applies. | 0..1 |
| hasMaskingMethod | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/hasMaskingMethod | Associates a column mask rule with the masking or transformation method it uses. | 0..1 |
| hasMatchMode | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/hasMatchMode | Associates a row filter rule with the value cardinality mode it expects. | 0..1 |
| hasPriority | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/hasPriority | Associates an entitlement rule with its precedence level. | 1 |
| hasRowFilterRule | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/hasRowFilterRule | Policy contains row-level filtering rules. | 0..* |
| hasSensitivityClassification | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/hasSensitivityClassification | Associates a relational column with a data sensitivity classification used by entitlement and masking controls. | 0..1 |
| hasUserType | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/hasUserType | A user is classified by a user type that identifies whether it is a human actor or an automated process. | 1 |
| hasValueSourceType | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/hasValueSourceType | Associates an entitlement rule with the runtime source category used to resolve rule values. | 0..1 |
| includesPolicy | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/includesPolicy | Policy group bundles one or more policies. | 1..* |
| isMemberOf | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/isMemberOf | User inherits policies via policy group membership. | 1..* |
| rdf__type | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/rdf__type | instance-of relationship | 1 |
| rdfs__subClassOf | http://www.w3.org/2000/01/rdf-schema#subClassOf | column mask rule is a subclass of entitlement rule | 1 |
| rdfs__subClassOf | http://www.w3.org/2000/01/rdf-schema#subClassOf | row filter rule is a subclass of entitlement rule | 1 |
| targetsFilteredColumn | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/targetsFilteredColumn | Row-filter rule targets a specific column context. | 1..* |
| targetsMaskedColumn | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/targetsMaskedColumn | Column-mask rule targets a specific column. | 1..* |

## Section 3: Node Properties

| Node Label | Property | Data Type | Mandatory |
| --- | --- | --- | --- |
| Column | columnDataType | xsd:string | No |
| Column | columnDefaultValue | xsd:string | No |
| Column | columnId | string | Yes |
| Column | columnLength | xsd:integer | No |
| Column | columnName | xsd:string | No |
| Column | columnPrecision | xsd:integer | No |
| Column | columnScale | xsd:integer | No |
| Column | isNullable | xsd:boolean | No |
| Column | ordinalPosition | xsd:integer | No |
| ColumnMaskRule | columnMaskRuleId | string | Yes |
| ColumnMaskRule | llmRewriteInstruction | xsd:string | No |
| ColumnMaskRule | maskValueExpression | xsd:string | No |
| ColumnMaskRule | rewriteTemplate | xsd:string | No |
| ColumnMaskRule | ruleExpression | xsd:string | No |
| ColumnMaskRule | valueSourceExpression | xsd:string | No |
| EntitlementRule | llmRewriteInstruction | xsd:string | No |
| EntitlementRule | rewriteTemplate | xsd:string | No |
| EntitlementRule | ruleExpression | xsd:string | No |
| EntitlementRule | valueSourceExpression | xsd:string | No |
| JdbcConnectionProfile | connectionTimeoutSeconds | xsd:integer | No |
| JdbcConnectionProfile | jdbcConnectionProfileId | string | Yes |
| JdbcConnectionProfile | jdbcDriver | xsd:string | No |
| JdbcConnectionProfile | jdbcUrl | xsd:string | No |
| JdbcConnectionProfile | jdbcUserName | xsd:string | No |
| JdbcConnectionProfile | sslMode | xsd:string | No |
| Policy | policyDescription | string | No |
| Policy | policyId | string | Yes |
| Policy | policyName | string | No |
| PolicyGroup | policyGroupId | string | Yes |
| PolicyGroup | policyGroupName | string | No |
| RelationalDatabase | databaseEdition | xsd:string | No |
| RelationalDatabase | databaseName | xsd:string | No |
| RelationalDatabase | databaseVendor | xsd:string | No |
| RelationalDatabase | databaseVersion | xsd:string | No |
| RelationalDatabase | hostName | xsd:string | No |
| RelationalDatabase | portNumber | xsd:integer | No |
| RelationalDatabase | relationalDatabaseId | string | Yes |
| RowFilterRule | llmRewriteInstruction | xsd:string | No |
| RowFilterRule | rewriteTemplate | xsd:string | No |
| RowFilterRule | rowFilterRuleId | string | Yes |
| RowFilterRule | ruleExpression | xsd:string | No |
| RowFilterRule | valueSourceExpression | xsd:string | No |
| Schema | isDefaultSchema | xsd:boolean | No |
| Schema | schemaDescription | xsd:string | No |
| Schema | schemaId | string | Yes |
| Schema | schemaName | xsd:string | No |
| Schema | schemaOwner | xsd:string | No |
| Schema | schemaType | xsd:string | No |
| Table | isTemporaryTable | xsd:boolean | No |
| Table | rowCountEstimate | xsd:integer | No |
| Table | tableDescription | xsd:string | No |
| Table | tableId | string | Yes |
| Table | tableName | xsd:string | No |
| Table | tableOwner | xsd:string | No |
| Table | tableType | xsd:string | No |
| User | userId | string | Yes |

## Section 4: Graph Topology

- `(:Schema)-[:belongsToDatabase]->(:RelationalDatabase)`
- `(:Table)-[:belongsToSchema]->(:Schema)`
- `(:Column)-[:belongsToTable]->(:Table)`
- `(:JdbcConnectionProfile)-[:connectsTo]->(:RelationalDatabase)`
- `(:Policy)-[:hasColumnMaskRule]->(:ColumnMaskRule)`
- `(:RowFilterRule)-[:hasComparisonOperator]->(:ComparisonOperator)`
- `(:RowFilterRule)-[:hasDenyBehavior]->(:DenyBehavior)`
- `(:ColumnMaskRule)-[:hasFallbackBehavior]->(:FallbackBehavior)`
- `(:RowFilterRule)-[:hasFilterAction]->(:FilterAction)`
- `(:ColumnMaskRule)-[:hasMaskAction]->(:MaskAction)`
- `(:ColumnMaskRule)-[:hasMaskingMethod]->(:MaskingMethod)`
- `(:RowFilterRule)-[:hasMatchMode]->(:MatchMode)`
- `(:ColumnMaskRule)-[:hasPriority]->(:RulePriority)`
- `(:RowFilterRule)-[:hasPriority]->(:RulePriority)`
- `(:Policy)-[:hasRowFilterRule]->(:RowFilterRule)`
- `(:Column)-[:hasSensitivityClassification]->(:SensitivityClassification)`
- `(:User)-[:hasUserType]->(:UserType)`
- `(:EntitlementRule)-[:hasValueSourceType]->(:ValueSourceType)`
- `(:PolicyGroup)-[:includesPolicy]->(:Policy)`
- `(:User)-[:isMemberOf]->(:PolicyGroup)`
- `(:AllowFilterAction)-[:rdf__type]->(:FilterAction)`
- `(:BetweenComparisonOperator)-[:rdf__type]->(:ComparisonOperator)`
- `(:BlockQueryDenyBehavior)-[:rdf__type]->(:DenyBehavior)`
- `(:BlockQueryDenyBehavior)-[:rdf__type]->(:FallbackBehavior)`
- `(:ConfidentialSensitivityClassification)-[:rdf__type]->(:SensitivityClassification)`
- `(:DenyFilterAction)-[:rdf__type]->(:FilterAction)`
- `(:DerivedQueryValueSourceType)-[:rdf__type]->(:ValueSourceType)`
- `(:EqualsComparisonOperator)-[:rdf__type]->(:ComparisonOperator)`
- `(:HashingMaskingMethod)-[:rdf__type]->(:MaskingMethod)`
- `(:HighPriority)-[:rdf__type]->(:RulePriority)`
- `(:HumanUser)-[:rdf__type]->(:UserType)`
- `(:InListComparisonOperator)-[:rdf__type]->(:ComparisonOperator)`
- `(:InternalSensitivityClassification)-[:rdf__type]->(:SensitivityClassification)`
- `(:LowPriority)-[:rdf__type]->(:RulePriority)`
- `(:MediumPriority)-[:rdf__type]->(:RulePriority)`
- `(:MultipleValuesMatchMode)-[:rdf__type]->(:MatchMode)`
- `(:NoValueMatchMode)-[:rdf__type]->(:MatchMode)`
- `(:NotEqualsComparisonOperator)-[:rdf__type]->(:ComparisonOperator)`
- `(:NotInListComparisonOperator)-[:rdf__type]->(:ComparisonOperator)`
- `(:NullReplacementMaskingMethod)-[:rdf__type]->(:MaskingMethod)`
- `(:NullifyMaskAction)-[:rdf__type]->(:MaskAction)`
- `(:PatternMaskingMethod)-[:rdf__type]->(:MaskingMethod)`
- `(:PHISensitivityClassification)-[:rdf__type]->(:SensitivityClassification)`
- `(:PIISensitivityClassification)-[:rdf__type]->(:SensitivityClassification)`
- `(:ProcessUser)-[:rdf__type]->(:UserType)`
- `(:PublicSensitivityClassification)-[:rdf__type]->(:SensitivityClassification)`
- `(:RedactMaskAction)-[:rdf__type]->(:MaskAction)`
- `(:RequestContextValueSourceType)-[:rdf__type]->(:ValueSourceType)`
- `(:RestrictedSensitivityClassification)-[:rdf__type]->(:SensitivityClassification)`
- `(:ReturnNoRowsDenyBehavior)-[:rdf__type]->(:DenyBehavior)`
- `(:ReturnNullFallbackBehavior)-[:rdf__type]->(:FallbackBehavior)`
- `(:RevealMaskAction)-[:rdf__type]->(:MaskAction)`
- `(:SessionContextValueSourceType)-[:rdf__type]->(:ValueSourceType)`
- `(:SingleValueMatchMode)-[:rdf__type]->(:MatchMode)`
- `(:StaticLiteralValueSourceType)-[:rdf__type]->(:ValueSourceType)`
- `(:StaticSubstitutionMaskingMethod)-[:rdf__type]->(:MaskingMethod)`
- `(:SubjectAttributeValueSourceType)-[:rdf__type]->(:ValueSourceType)`
- `(:SubstituteMaskAction)-[:rdf__type]->(:MaskAction)`
- `(:TokenizationMaskingMethod)-[:rdf__type]->(:MaskingMethod)`
- `(:TokenizeMaskAction)-[:rdf__type]->(:MaskAction)`
- `(:UseDefaultMaskFallbackBehavior)-[:rdf__type]->(:FallbackBehavior)`
- `(:ColumnMaskRule)-[:rdfs__subClassOf]->(:EntitlementRule)`
- `(:RowFilterRule)-[:rdfs__subClassOf]->(:EntitlementRule)`
- `(:RowFilterRule)-[:targetsFilteredColumn]->(:Column)`
- `(:ColumnMaskRule)-[:targetsMaskedColumn]->(:Column)`

## Section 5: Enumeration Members

| Enum Class | Member Label | Member URI |
| --- | --- | --- |
| FilterAction | allow | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/AllowFilterAction |
| ComparisonOperator | between | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/BetweenComparisonOperator |
| DenyBehavior | block query | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/BlockQueryDenyBehavior |
| FallbackBehavior | block query | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/BlockQueryDenyBehavior |
| SensitivityClassification | confidential | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/ConfidentialSensitivityClassification |
| FilterAction | deny | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/DenyFilterAction |
| ValueSourceType | derived query | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/DerivedQueryValueSourceType |
| ComparisonOperator | equals | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/EqualsComparisonOperator |
| MaskingMethod | hashing | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/HashingMaskingMethod |
| RulePriority | high priority | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/HighPriority |
| UserType | human user | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/HumanUser |
| ComparisonOperator | in list | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/InListComparisonOperator |
| SensitivityClassification | internal | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/InternalSensitivityClassification |
| RulePriority | low priority | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/LowPriority |
| RulePriority | medium priority | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/MediumPriority |
| MatchMode | multiple values | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/MultipleValuesMatchMode |
| MatchMode | no value | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/NoValueMatchMode |
| ComparisonOperator | not equals | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/NotEqualsComparisonOperator |
| ComparisonOperator | not in list | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/NotInListComparisonOperator |
| MaskingMethod | null replacement | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/NullReplacementMaskingMethod |
| MaskAction | nullify | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/NullifyMaskAction |
| MaskingMethod | pattern masking | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/PatternMaskingMethod |
| SensitivityClassification | phi | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/PHISensitivityClassification |
| SensitivityClassification | pii | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/PIISensitivityClassification |
| UserType | process user | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/ProcessUser |
| SensitivityClassification | public | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/PublicSensitivityClassification |
| MaskAction | redact | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/RedactMaskAction |
| ValueSourceType | request context | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/RequestContextValueSourceType |
| SensitivityClassification | restricted | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/RestrictedSensitivityClassification |
| DenyBehavior | return no rows | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/ReturnNoRowsDenyBehavior |
| FallbackBehavior | return null | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/ReturnNullFallbackBehavior |
| MaskAction | reveal | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/RevealMaskAction |
| ValueSourceType | session context | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/SessionContextValueSourceType |
| MatchMode | single value | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/SingleValueMatchMode |
| ValueSourceType | static literal | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/StaticLiteralValueSourceType |
| MaskingMethod | static substitution | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/StaticSubstitutionMaskingMethod |
| ValueSourceType | subject attribute | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/SubjectAttributeValueSourceType |
| MaskAction | substitute | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/SubstituteMaskAction |
| MaskingMethod | tokenization | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/TokenizationMaskingMethod |
| MaskAction | tokenize | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/TokenizeMaskAction |
| FallbackBehavior | use default mask | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/UseDefaultMaskFallbackBehavior |
