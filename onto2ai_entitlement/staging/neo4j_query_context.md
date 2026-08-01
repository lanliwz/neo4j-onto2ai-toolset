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
