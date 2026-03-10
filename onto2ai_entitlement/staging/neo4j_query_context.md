# Neo4j Schema Prompt

## Section 1: Node Labels

| Label | Type | URI | Definition |
| --- | --- | --- | --- |
| JdbcConnectionProfile | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/JdbcConnectionProfile | JDBC endpoint and driver metadata for a target database. |
| Column | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/Column | Relational column protected by entitlement rules. |
| Schema | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/Schema | Relational schema/container for tables. |
| Policy | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/Policy | Bundle of row-filter and/or column-mask rules. |
| UserType | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/UserType | Classification of a user by the kind of actor it represents for entitlement evaluation. |
| RelationalDatabase | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/RelationalDatabase | JDBC-connectable relational database platform. |
| Table | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/Table | Relational table containing columns. |
| RowFilterRule | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/RowFilterRule | Rule that restricts row visibility using predicates. |
| ColumnMaskRule | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/ColumnMaskRule | Rule that transforms or redacts sensitive column values. |
| PolicyGroup | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/PolicyGroup | Collection of policies mapped to a persona, role, or function. |
| User | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/User | Principal that invokes or is evaluated against entitlement policies, including a human actor or an automated process. |
| RulePriority | owl__Class | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/RulePriority | Enumeration of precedence levels used to order entitlement rules during evaluation. |
| HighPriority | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/HighPriority | Priority level indicating a rule should be evaluated before lower-priority rules. |
| LowPriority | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/LowPriority | Priority level indicating a rule should be evaluated after higher-priority rules. |
| MediumPriority | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/MediumPriority | Priority level indicating a rule should be evaluated with standard precedence. |
| HumanUser | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/HumanUser | User type representing an individual human actor authenticated to access protected data. |
| ProcessUser | owl__NamedIndividual | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/ProcessUser | User type representing an automated process, service account, or system integration actor. |

## Section 2: Relationship Types

| Relationship | URI | Definition | Cardinality |
| --- | --- | --- | --- |
| belongsToDatabase | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/belongsToDatabase | Schema belongs to a relational database. | 0..* |
| belongsToSchema | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/belongsToSchema | A table belongs to exactly one schema. | 0..* |
| belongsToTable | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/belongsToTable | A column belongs to exactly one table. | 0..* |
| connectsTo | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/connectsTo | JDBC profile connects to a target relational database. | 0..* |
| hasColumnMaskRule | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/hasColumnMaskRule | Policy contains column masking rules. | 0..* |
| hasPriority | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/hasPriority | Associates an entitlement rule with its precedence level. | 0..1 |
| hasRowFilterRule | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/hasRowFilterRule | Policy contains row-level filtering rules. | 0..* |
| hasUserType | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/hasUserType | A user is classified by a user type that identifies whether it is a human actor or an automated process. | 0..1 |
| includesPolicy | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/includesPolicy | Policy group bundles one or more policies. | 0..* |
| isMemberOf | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/isMemberOf | User inherits policies via policy group membership. | 0..* |
| rdf__type |  | instance-of relationship | 1 |
| targetsFilteredColumn | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/targetsFilteredColumn | Row-filter rule targets a specific column context. | 0..* |
| targetsMaskedColumn | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/targetsMaskedColumn | Column-mask rule targets a specific column. | 0..* |

## Section 3: Node Properties

| Node Label | Property | Data Type | Mandatory |
| --- | --- | --- | --- |
| JdbcConnectionProfile | connectionTimeoutSeconds | xsd:integer | No |
| JdbcConnectionProfile | jdbcConnectionProfileId | string | Yes |
| JdbcConnectionProfile | jdbcDriver | xsd:string | No |
| JdbcConnectionProfile | jdbcUrl | xsd:string | No |
| JdbcConnectionProfile | jdbcUserName | xsd:string | No |
| JdbcConnectionProfile | sslMode | xsd:string | No |
| Column | columnDataType | xsd:string | No |
| Column | columnDefaultValue | xsd:string | No |
| Column | columnId | string | Yes |
| Column | columnLength | xsd:integer | No |
| Column | columnName | xsd:string | No |
| Column | columnPrecision | xsd:integer | No |
| Column | columnScale | xsd:integer | No |
| Column | isNullable | xsd:boolean | No |
| Column | ordinalPosition | xsd:integer | No |
| Schema | isDefaultSchema | xsd:boolean | No |
| Schema | schemaDescription | xsd:string | No |
| Schema | schemaId | string | Yes |
| Schema | schemaName | xsd:string | No |
| Schema | schemaOwner | xsd:string | No |
| Schema | schemaType | xsd:string | No |
| Policy | definition | string | No |
| Policy | policyId | string | Yes |
| Policy | policyName | string | No |
| RelationalDatabase | databaseEdition | xsd:string | No |
| RelationalDatabase | databaseName | xsd:string | No |
| RelationalDatabase | databaseVendor | xsd:string | No |
| RelationalDatabase | databaseVersion | xsd:string | No |
| RelationalDatabase | hostName | xsd:string | No |
| RelationalDatabase | portNumber | xsd:integer | No |
| RelationalDatabase | relationalDatabaseId | string | Yes |
| Table | isTemporaryTable | xsd:boolean | No |
| Table | rowCountEstimate | xsd:integer | No |
| Table | tableDescription | xsd:string | No |
| Table | tableId | string | Yes |
| Table | tableName | xsd:string | No |
| Table | tableOwner | xsd:string | No |
| Table | tableType | xsd:string | No |
| RowFilterRule | comparisonOperator | xsd:string | No |
| RowFilterRule | denyBehavior | xsd:string | No |
| RowFilterRule | filterAction | xsd:string | No |
| RowFilterRule | llmRewriteInstruction | xsd:string | No |
| RowFilterRule | matchMode | xsd:string | No |
| RowFilterRule | rewriteTemplate | xsd:string | No |
| RowFilterRule | rowFilterRuleId | string | Yes |
| RowFilterRule | ruleExpression | xsd:string | No |
| RowFilterRule | valueSourceExpression | xsd:string | No |
| RowFilterRule | valueSourceType | xsd:string | No |
| ColumnMaskRule | columnMaskRuleId | string | Yes |
| ColumnMaskRule | fallbackBehavior | xsd:string | No |
| ColumnMaskRule | llmRewriteInstruction | xsd:string | No |
| ColumnMaskRule | maskAction | xsd:string | No |
| ColumnMaskRule | maskValueExpression | xsd:string | No |
| ColumnMaskRule | maskingMethod | xsd:string | No |
| ColumnMaskRule | rewriteTemplate | xsd:string | No |
| ColumnMaskRule | ruleExpression | xsd:string | No |
| ColumnMaskRule | valueSourceExpression | xsd:string | No |
| ColumnMaskRule | valueSourceType | xsd:string | No |
| PolicyGroup | policyGroupId | string | Yes |
| PolicyGroup | policyGroupName | string | No |
| User | userId | string | Yes |

## Section 4: Graph Topology

- `(:JdbcConnectionProfile)-[:connectsTo]->(:RelationalDatabase)`
- `(:Column)-[:belongsToTable]->(:Table)`
- `(:Schema)-[:belongsToDatabase]->(:RelationalDatabase)`
- `(:Policy)-[:hasColumnMaskRule]->(:ColumnMaskRule)`
- `(:Policy)-[:hasRowFilterRule]->(:RowFilterRule)`
- `(:Table)-[:belongsToSchema]->(:Schema)`
- `(:RowFilterRule)-[:targetsFilteredColumn]->(:Column)`
- `(:RowFilterRule)-[:hasPriority]->(:RulePriority)`
- `(:ColumnMaskRule)-[:targetsMaskedColumn]->(:Column)`
- `(:ColumnMaskRule)-[:hasPriority]->(:RulePriority)`
- `(:PolicyGroup)-[:includesPolicy]->(:Policy)`
- `(:User)-[:isMemberOf]->(:PolicyGroup)`
- `(:User)-[:hasUserType]->(:UserType)`
- `(:HighPriority)-[:rdf__type]->(:RulePriority)`
- `(:LowPriority)-[:rdf__type]->(:RulePriority)`
- `(:MediumPriority)-[:rdf__type]->(:RulePriority)`
- `(:HumanUser)-[:rdf__type]->(:UserType)`
- `(:ProcessUser)-[:rdf__type]->(:UserType)`

## Section 5: Enumeration Members

| Enum Class | Member Label | Member URI |
| --- | --- | --- |
| RulePriority | high priority | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/HighPriority |
| RulePriority | low priority | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/LowPriority |
| RulePriority | medium priority | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/MediumPriority |
| UserType | human user | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/HumanUser |
| UserType | process user | http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/ProcessUser |
