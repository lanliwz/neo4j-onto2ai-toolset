# Neo4j Schema Prompt

## Section 1: Node Labels

| Label | Type | URI | Definition |
| --- | --- | --- | --- |
| User | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/User | Principal that invokes or is evaluated against entitlement policies, including a human actor or an automated process. |
| RowFilterRule:EntitlementRule | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/RowFilterRule | Rule that restricts row visibility using predicates. |
| EntitlementRule | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/EntitlementRule | Abstract superclass for entitlement rules that constrain row visibility or column values. |
| ColumnMaskRule:EntitlementRule | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/ColumnMaskRule | Rule that transforms or redacts sensitive column values. |
| FallbackBehavior | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/FallbackBehavior | Enumeration of fallback behaviors applied when a column mask rule cannot resolve masking inputs. |
| DenyBehavior | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/DenyBehavior | Enumeration of enforcement behaviors applied when a row filter rule denies access. |
| ValueSourceType | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/ValueSourceType | Enumeration of runtime source categories used to resolve entitlement rule values. |
| Table | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/Table | Relational table containing columns. |
| UserType | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/UserType | Classification of a user by the kind of actor it represents for entitlement evaluation. |
| MaskingMethod | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/MaskingMethod | Enumeration of masking or transformation strategies available to column mask rules. |
| Policy | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/Policy | Bundle of row-filter and/or column-mask rules. |
| Schema | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/Schema | Relational schema/container for tables. |
| PolicyGroup | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/PolicyGroup | Collection of policies mapped to a persona, role, or function. |
| SensitivityClassification | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/SensitivityClassification | Enumeration of data sensitivity levels used to classify relational columns for entitlement and masking decisions. |
| RelationalDatabase | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/RelationalDatabase | JDBC-connectable relational database platform. |
| MaskAction | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/MaskAction | Enumeration of actions a column mask rule can apply to protected column values. |
| Column | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/Column | Relational column protected by entitlement rules. |
| JdbcConnectionProfile | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/JdbcConnectionProfile | JDBC endpoint and driver metadata for a target database. |
| MatchMode | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/MatchMode | Enumeration of value cardinality modes expected by a row filter rule. |
| ComparisonOperator | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/ComparisonOperator | Enumeration of comparison operators available to row filter predicates. |
| FilterAction | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/FilterAction | Enumeration of actions a row filter rule can apply during entitlement evaluation. |
| RulePriority | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/RulePriority | Enumeration of precedence levels used to order entitlement rules during evaluation. |
| Between | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/BetweenComparisonOperator | Comparison operator requiring a value to fall between two bounds. |
| Equals | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/EqualsComparisonOperator | Comparison operator for equality predicates. |
| InList | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/InListComparisonOperator | Comparison operator requiring a value to appear in an allowed set. |
| NotEquals | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/NotEqualsComparisonOperator | Comparison operator for inequality predicates. |
| NotInList | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/NotInListComparisonOperator | Comparison operator requiring a value not to appear in a denied set. |
| BlockQuery | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/BlockQueryBehavior | Enforcement behavior that blocks the data access request, whether selected as a deny action or as a masking fallback. |
| ReturnNoRows | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/ReturnNoRowsDenyBehavior | Deny behavior that rewrites access to produce an empty result set. |
| ReturnNull | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/ReturnNullFallbackBehavior | Fallback behavior that returns null when masking inputs cannot be resolved. |
| UseDefaultMask | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/UseDefaultMaskFallbackBehavior | Fallback behavior that applies a configured default mask when rule-specific inputs cannot be resolved. |
| Allow | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/AllowFilterAction | Filter action that permits access to rows matching the rule predicate. |
| Deny | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/DenyFilterAction | Filter action that denies access to rows matching the rule predicate. |
| Nullify | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/NullifyMaskAction | Mask action that replaces the protected value with null. |
| Redact | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/RedactMaskAction | Mask action that redacts the protected value. |
| Reveal | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/RevealMaskAction | Mask action that reveals the original value. |
| Substitute | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/SubstituteMaskAction | Mask action that substitutes the protected value with a configured replacement. |
| Tokenize | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/TokenizeMaskAction | Mask action that replaces the original value with a token. |
| Hashing | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/HashingMaskingMethod | Masking method that emits a deterministic hash of the original value. |
| NullReplacement | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/NullReplacementMaskingMethod | Masking method that replaces the original value with null. |
| PatternMasking | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/PatternMaskingMethod | Masking method that preserves a configured pattern while hiding protected portions of a value. |
| StaticSubstitution | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/StaticSubstitutionMaskingMethod | Masking method that emits a fixed replacement value. |
| Tokenization | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/TokenizationMaskingMethod | Masking method that emits a reversible or managed token for the original value. |
| MultipleValues | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/MultipleValuesMatchMode | Match mode indicating the rule expects a collection of comparison values. |
| NoValue | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/NoValueMatchMode | Match mode indicating the rule does not require a comparison value. |
| SingleValue | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/SingleValueMatchMode | Match mode indicating the rule expects one comparison value. |
| HighPriority | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/HighPriority | Priority level indicating a rule should be evaluated before lower-priority rules. |
| LowPriority | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/LowPriority | Priority level indicating a rule should be evaluated after higher-priority rules. |
| MediumPriority | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/MediumPriority | Priority level indicating a rule should be evaluated with standard precedence. |
| Confidential | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/ConfidentialSensitivityClassification | Sensitivity classification for data requiring restricted access because disclosure could create business or privacy risk. |
| Internal | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/InternalSensitivityClassification | Sensitivity classification for data intended for internal organizational use. |
| Phi | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/PHISensitivityClassification | Sensitivity classification for protected health information. |
| Pii | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/PIISensitivityClassification | Sensitivity classification for personally identifiable information. |
| Public | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/PublicSensitivityClassification | Sensitivity classification for data approved for public disclosure. |
| Restricted | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/RestrictedSensitivityClassification | Sensitivity classification for highly controlled data requiring strict access and masking governance. |
| HumanUser | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/HumanUser | User type representing an individual human actor authenticated to access protected data. |
| ProcessUser | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/ProcessUser | User type representing an automated process, service account, or system integration actor. |
| DerivedQuery | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/DerivedQueryValueSourceType | Value source type resolved by executing or evaluating a derived lookup query. |
| RequestContext | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/RequestContextValueSourceType | Value source type resolved from the current data access request context. |
| SessionContext | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/SessionContextValueSourceType | Value source type resolved from the current authenticated session context. |
| StaticLiteral | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/StaticLiteralValueSourceType | Value source type where the rule stores a literal value directly. |
| SubjectAttribute | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/SubjectAttributeValueSourceType | Value source type resolved from an attribute of the evaluated user or principal. |

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
| hasPriority | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/hasPriority | A row filter rule or column mask rule is assigned a priority level for evaluation order. | 1 |
| hasRowFilterRule | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/hasRowFilterRule | Policy contains row-level filtering rules. | 0..* |
| hasSensitivityClassification | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/hasSensitivityClassification | Associates a relational column with a data sensitivity classification used by entitlement and masking controls. | 0..1 |
| hasUserType | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/hasUserType | A user is classified by a user type that identifies whether it is a human actor or an automated process. | 1 |
| hasValueSourceType | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/hasValueSourceType | Associates an entitlement rule with the runtime source category used to resolve rule values. | 0..1 |
| includesPolicy | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/includesPolicy | Policy group bundles one or more policies. | 1..* |
| isMemberOf | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/isMemberOf | User inherits policies via policy group membership. | 1..* |
| rdf__type | http://www.w3.org/1999/02/22-rdf-syntax-ns#type | instance-of relationship | 1 |
| targetsFilteredColumn | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/targetsFilteredColumn | Row-filter rule targets a specific column context. | 1..* |
| targetsMaskedColumn | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/targetsMaskedColumn | Column-mask rule targets a specific column. | 1..* |

## Section 3: Node Properties

| Node Label | Property | Data Type | Mandatory |
| --- | --- | --- | --- |
| User | userId | string | Yes |
| RowFilterRule:EntitlementRule | llmRewriteInstruction | string | No |
| RowFilterRule:EntitlementRule | rewriteTemplate | string | No |
| RowFilterRule:EntitlementRule | rowFilterRuleId | string | Yes |
| RowFilterRule:EntitlementRule | ruleExpression | string | No |
| RowFilterRule:EntitlementRule | valueSourceExpression | string | No |
| EntitlementRule | llmRewriteInstruction | string | No |
| EntitlementRule | rewriteTemplate | string | No |
| EntitlementRule | ruleExpression | string | No |
| EntitlementRule | valueSourceExpression | string | No |
| ColumnMaskRule:EntitlementRule | columnMaskRuleId | string | Yes |
| ColumnMaskRule:EntitlementRule | llmRewriteInstruction | string | No |
| ColumnMaskRule:EntitlementRule | maskValueExpression | string | No |
| ColumnMaskRule:EntitlementRule | rewriteTemplate | string | No |
| ColumnMaskRule:EntitlementRule | ruleExpression | string | No |
| ColumnMaskRule:EntitlementRule | valueSourceExpression | string | No |
| Table | isTemporaryTable | boolean | No |
| Table | rowCountEstimate | integer | No |
| Table | tableDescription | string | No |
| Table | tableId | string | Yes |
| Table | tableName | string | No |
| Table | tableOwner | string | No |
| Table | tableType | string | No |
| Policy | policyDescription | string | No |
| Policy | policyId | string | Yes |
| Policy | policyName | string | No |
| Schema | isDefaultSchema | boolean | No |
| Schema | schemaDescription | string | No |
| Schema | schemaId | string | Yes |
| Schema | schemaName | string | No |
| Schema | schemaOwner | string | No |
| Schema | schemaType | string | No |
| PolicyGroup | policyGroupId | string | Yes |
| PolicyGroup | policyGroupName | string | No |
| RelationalDatabase | databaseEdition | string | No |
| RelationalDatabase | databaseName | string | No |
| RelationalDatabase | databaseVendor | string | No |
| RelationalDatabase | databaseVersion | string | No |
| RelationalDatabase | hostName | string | No |
| RelationalDatabase | portNumber | integer | No |
| RelationalDatabase | relationalDatabaseId | string | Yes |
| Column | columnDataType | string | No |
| Column | columnDefaultValue | string | No |
| Column | columnId | string | Yes |
| Column | columnLength | integer | No |
| Column | columnName | string | No |
| Column | columnPrecision | integer | No |
| Column | columnScale | integer | No |
| Column | isNullable | boolean | No |
| Column | ordinalPosition | integer | No |
| JdbcConnectionProfile | connectionTimeoutSeconds | integer | No |
| JdbcConnectionProfile | jdbcConnectionProfileId | string | Yes |
| JdbcConnectionProfile | jdbcDriver | string | No |
| JdbcConnectionProfile | jdbcUrl | string | No |
| JdbcConnectionProfile | jdbcUserName | string | No |
| JdbcConnectionProfile | sslMode | string | No |

## Section 4: Graph Topology

- `(:User)-[:hasUserType]->(:UserType)`
- `(:User)-[:isMemberOf]->(:PolicyGroup)`
- `(:RowFilterRule:EntitlementRule)-[:hasComparisonOperator]->(:ComparisonOperator)`
- `(:RowFilterRule:EntitlementRule)-[:hasDenyBehavior]->(:DenyBehavior)`
- `(:RowFilterRule:EntitlementRule)-[:hasFilterAction]->(:FilterAction)`
- `(:RowFilterRule:EntitlementRule)-[:hasMatchMode]->(:MatchMode)`
- `(:RowFilterRule:EntitlementRule)-[:targetsFilteredColumn]->(:Column)`
- `(:RowFilterRule:EntitlementRule)-[:hasPriority]->(:RulePriority)`
- `(:RowFilterRule:EntitlementRule)-[:hasValueSourceType]->(:ValueSourceType)`
- `(:EntitlementRule)-[:hasPriority]->(:RulePriority)`
- `(:EntitlementRule)-[:hasValueSourceType]->(:ValueSourceType)`
- `(:ColumnMaskRule:EntitlementRule)-[:hasFallbackBehavior]->(:FallbackBehavior)`
- `(:ColumnMaskRule:EntitlementRule)-[:hasMaskAction]->(:MaskAction)`
- `(:ColumnMaskRule:EntitlementRule)-[:hasMaskingMethod]->(:MaskingMethod)`
- `(:ColumnMaskRule:EntitlementRule)-[:targetsMaskedColumn]->(:Column)`
- `(:ColumnMaskRule:EntitlementRule)-[:hasPriority]->(:RulePriority)`
- `(:ColumnMaskRule:EntitlementRule)-[:hasValueSourceType]->(:ValueSourceType)`
- `(:Table)-[:belongsToSchema]->(:Schema)`
- `(:Policy)-[:hasColumnMaskRule]->(:ColumnMaskRule:EntitlementRule)`
- `(:Policy)-[:hasRowFilterRule]->(:RowFilterRule:EntitlementRule)`
- `(:Schema)-[:belongsToDatabase]->(:RelationalDatabase)`
- `(:PolicyGroup)-[:includesPolicy]->(:Policy)`
- `(:Column)-[:belongsToTable]->(:Table)`
- `(:Column)-[:hasSensitivityClassification]->(:SensitivityClassification)`
- `(:JdbcConnectionProfile)-[:connectsTo]->(:RelationalDatabase)`
- `(:Between)-[:rdf__type]->(:ComparisonOperator)`
- `(:Equals)-[:rdf__type]->(:ComparisonOperator)`
- `(:InList)-[:rdf__type]->(:ComparisonOperator)`
- `(:NotEquals)-[:rdf__type]->(:ComparisonOperator)`
- `(:NotInList)-[:rdf__type]->(:ComparisonOperator)`
- `(:BlockQuery)-[:rdf__type]->(:DenyBehavior)`
- `(:ReturnNoRows)-[:rdf__type]->(:DenyBehavior)`
- `(:BlockQuery)-[:rdf__type]->(:FallbackBehavior)`
- `(:ReturnNull)-[:rdf__type]->(:FallbackBehavior)`
- `(:UseDefaultMask)-[:rdf__type]->(:FallbackBehavior)`
- `(:Allow)-[:rdf__type]->(:FilterAction)`
- `(:Deny)-[:rdf__type]->(:FilterAction)`
- `(:Nullify)-[:rdf__type]->(:MaskAction)`
- `(:Redact)-[:rdf__type]->(:MaskAction)`
- `(:Reveal)-[:rdf__type]->(:MaskAction)`
- `(:Substitute)-[:rdf__type]->(:MaskAction)`
- `(:Tokenize)-[:rdf__type]->(:MaskAction)`
- `(:Hashing)-[:rdf__type]->(:MaskingMethod)`
- `(:NullReplacement)-[:rdf__type]->(:MaskingMethod)`
- `(:PatternMasking)-[:rdf__type]->(:MaskingMethod)`
- `(:StaticSubstitution)-[:rdf__type]->(:MaskingMethod)`
- `(:Tokenization)-[:rdf__type]->(:MaskingMethod)`
- `(:MultipleValues)-[:rdf__type]->(:MatchMode)`
- `(:NoValue)-[:rdf__type]->(:MatchMode)`
- `(:SingleValue)-[:rdf__type]->(:MatchMode)`
- `(:HighPriority)-[:rdf__type]->(:RulePriority)`
- `(:LowPriority)-[:rdf__type]->(:RulePriority)`
- `(:MediumPriority)-[:rdf__type]->(:RulePriority)`
- `(:Confidential)-[:rdf__type]->(:SensitivityClassification)`
- `(:Internal)-[:rdf__type]->(:SensitivityClassification)`
- `(:Phi)-[:rdf__type]->(:SensitivityClassification)`
- `(:Pii)-[:rdf__type]->(:SensitivityClassification)`
- `(:Public)-[:rdf__type]->(:SensitivityClassification)`
- `(:Restricted)-[:rdf__type]->(:SensitivityClassification)`
- `(:HumanUser)-[:rdf__type]->(:UserType)`
- `(:ProcessUser)-[:rdf__type]->(:UserType)`
- `(:DerivedQuery)-[:rdf__type]->(:ValueSourceType)`
- `(:RequestContext)-[:rdf__type]->(:ValueSourceType)`
- `(:SessionContext)-[:rdf__type]->(:ValueSourceType)`
- `(:StaticLiteral)-[:rdf__type]->(:ValueSourceType)`
- `(:SubjectAttribute)-[:rdf__type]->(:ValueSourceType)`

## Section 5: Enumeration Members

| Enum Class | Member Label | Member URI |
| --- | --- | --- |
| ComparisonOperator | between | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/BetweenComparisonOperator |
| ComparisonOperator | equals | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/EqualsComparisonOperator |
| ComparisonOperator | in list | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/InListComparisonOperator |
| ComparisonOperator | not equals | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/NotEqualsComparisonOperator |
| ComparisonOperator | not in list | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/NotInListComparisonOperator |
| DenyBehavior | block query | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/BlockQueryBehavior |
| DenyBehavior | return no rows | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/ReturnNoRowsDenyBehavior |
| FallbackBehavior | block query | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/BlockQueryBehavior |
| FallbackBehavior | return null | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/ReturnNullFallbackBehavior |
| FallbackBehavior | use default mask | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/UseDefaultMaskFallbackBehavior |
| FilterAction | allow | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/AllowFilterAction |
| FilterAction | deny | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/DenyFilterAction |
| MaskAction | nullify | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/NullifyMaskAction |
| MaskAction | redact | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/RedactMaskAction |
| MaskAction | reveal | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/RevealMaskAction |
| MaskAction | substitute | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/SubstituteMaskAction |
| MaskAction | tokenize | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/TokenizeMaskAction |
| MaskingMethod | hashing | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/HashingMaskingMethod |
| MaskingMethod | null replacement | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/NullReplacementMaskingMethod |
| MaskingMethod | pattern masking | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/PatternMaskingMethod |
| MaskingMethod | static substitution | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/StaticSubstitutionMaskingMethod |
| MaskingMethod | tokenization | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/TokenizationMaskingMethod |
| MatchMode | multiple values | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/MultipleValuesMatchMode |
| MatchMode | no value | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/NoValueMatchMode |
| MatchMode | single value | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/SingleValueMatchMode |
| RulePriority | high priority | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/HighPriority |
| RulePriority | low priority | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/LowPriority |
| RulePriority | medium priority | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/MediumPriority |
| SensitivityClassification | confidential | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/ConfidentialSensitivityClassification |
| SensitivityClassification | internal | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/InternalSensitivityClassification |
| SensitivityClassification | phi | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/PHISensitivityClassification |
| SensitivityClassification | pii | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/PIISensitivityClassification |
| SensitivityClassification | public | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/PublicSensitivityClassification |
| SensitivityClassification | restricted | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/RestrictedSensitivityClassification |
| UserType | human user | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/HumanUser |
| UserType | process user | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/ProcessUser |
| ValueSourceType | derived query | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/DerivedQueryValueSourceType |
| ValueSourceType | request context | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/RequestContextValueSourceType |
| ValueSourceType | session context | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/SessionContextValueSourceType |
| ValueSourceType | static literal | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/StaticLiteralValueSourceType |
| ValueSourceType | subject attribute | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/SubjectAttributeValueSourceType |
