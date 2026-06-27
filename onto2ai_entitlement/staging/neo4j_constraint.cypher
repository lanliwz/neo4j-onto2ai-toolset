// ===========================================================
// NEO4J SCHEMA CONSTRAINTS (Source: full_schema_model.json)
// Generated to enforce structural integrity while keeping metadata as comments.
// ===========================================================

// Class: column
// Definition: Relational column protected by entitlement rules.
// URI: http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/Column
// Mandatory property: columnId (cardinality: 1)
CREATE CONSTRAINT Column_columnId_Required IF NOT EXISTS FOR (n:`Column`) REQUIRE n.`columnId` IS NOT NULL;
// Unique property: columnId
CREATE CONSTRAINT Column_columnId_Unique IF NOT EXISTS FOR (n:`Column`) REQUIRE n.`columnId` IS UNIQUE;

// Class: column mask rule
// Definition: Rule that transforms or redacts sensitive column values.
// URI: http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/ColumnMaskRule
// Mandatory property: columnMaskRuleId (cardinality: 1)
CREATE CONSTRAINT ColumnMaskRule_columnMaskRuleId_Required IF NOT EXISTS FOR (n:`ColumnMaskRule`) REQUIRE n.`columnMaskRuleId` IS NOT NULL;
// Unique property: columnMaskRuleId
CREATE CONSTRAINT ColumnMaskRule_columnMaskRuleId_Unique IF NOT EXISTS FOR (n:`ColumnMaskRule`) REQUIRE n.`columnMaskRuleId` IS UNIQUE;

// Class: comparison operator
// Definition: Enumeration of comparison operators available to row filter predicates.
// URI: http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/ComparisonOperator


// Class: deny behavior
// Definition: Enumeration of enforcement behaviors applied when a row filter rule denies access.
// URI: http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/DenyBehavior


// Class: entitlement rule
// Definition: Abstract superclass for entitlement rules that constrain row visibility or column values.
// URI: http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/EntitlementRule


// Class: fallback behavior
// Definition: Enumeration of fallback behaviors applied when a column mask rule cannot resolve masking inputs.
// URI: http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/FallbackBehavior


// Class: filter action
// Definition: Enumeration of actions a row filter rule can apply during entitlement evaluation.
// URI: http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/FilterAction


// Class: jdbc connection profile
// Definition: JDBC endpoint and driver metadata for a target database.
// URI: http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/JdbcConnectionProfile
// Mandatory property: jdbcConnectionProfileId (cardinality: 1)
CREATE CONSTRAINT JdbcConnectionProfile_jdbcConnectionProfileId_Required IF NOT EXISTS FOR (n:`JdbcConnectionProfile`) REQUIRE n.`jdbcConnectionProfileId` IS NOT NULL;
// Unique property: jdbcConnectionProfileId
CREATE CONSTRAINT JdbcConnectionProfile_jdbcConnectionProfileId_Unique IF NOT EXISTS FOR (n:`JdbcConnectionProfile`) REQUIRE n.`jdbcConnectionProfileId` IS UNIQUE;

// Class: mask action
// Definition: Enumeration of actions a column mask rule can apply to protected column values.
// URI: http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/MaskAction


// Class: masking method
// Definition: Enumeration of masking or transformation strategies available to column mask rules.
// URI: http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/MaskingMethod


// Class: match mode
// Definition: Enumeration of value cardinality modes expected by a row filter rule.
// URI: http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/MatchMode


// Class: policy
// Definition: Bundle of row-filter and/or column-mask rules.
// URI: http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/Policy
// Mandatory property: policyId (cardinality: 1)
CREATE CONSTRAINT Policy_policyId_Required IF NOT EXISTS FOR (n:`Policy`) REQUIRE n.`policyId` IS NOT NULL;
// Unique property: policyId
CREATE CONSTRAINT Policy_policyId_Unique IF NOT EXISTS FOR (n:`Policy`) REQUIRE n.`policyId` IS UNIQUE;

// Class: policy group
// Definition: Collection of policies mapped to a persona, role, or function.
// URI: http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/PolicyGroup
// Mandatory property: policyGroupId (cardinality: 1)
CREATE CONSTRAINT PolicyGroup_policyGroupId_Required IF NOT EXISTS FOR (n:`PolicyGroup`) REQUIRE n.`policyGroupId` IS NOT NULL;
// Unique property: policyGroupId
CREATE CONSTRAINT PolicyGroup_policyGroupId_Unique IF NOT EXISTS FOR (n:`PolicyGroup`) REQUIRE n.`policyGroupId` IS UNIQUE;

// Class: relational database
// Definition: JDBC-connectable relational database platform.
// URI: http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/RelationalDatabase
// Mandatory property: relationalDatabaseId (cardinality: 1)
CREATE CONSTRAINT RelationalDatabase_relationalDatabaseId_Required IF NOT EXISTS FOR (n:`RelationalDatabase`) REQUIRE n.`relationalDatabaseId` IS NOT NULL;
// Unique property: relationalDatabaseId
CREATE CONSTRAINT RelationalDatabase_relationalDatabaseId_Unique IF NOT EXISTS FOR (n:`RelationalDatabase`) REQUIRE n.`relationalDatabaseId` IS UNIQUE;

// Class: row filter rule
// Definition: Rule that restricts row visibility using predicates.
// URI: http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/RowFilterRule
// Mandatory property: rowFilterRuleId (cardinality: 1)
CREATE CONSTRAINT RowFilterRule_rowFilterRuleId_Required IF NOT EXISTS FOR (n:`RowFilterRule`) REQUIRE n.`rowFilterRuleId` IS NOT NULL;
// Unique property: rowFilterRuleId
CREATE CONSTRAINT RowFilterRule_rowFilterRuleId_Unique IF NOT EXISTS FOR (n:`RowFilterRule`) REQUIRE n.`rowFilterRuleId` IS UNIQUE;

// Class: rule priority
// Definition: Enumeration of precedence levels used to order entitlement rules during evaluation.
// URI: http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/RulePriority


// Class: schema
// Definition: Relational schema/container for tables.
// URI: http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/Schema
// Mandatory property: schemaId (cardinality: 1)
CREATE CONSTRAINT Schema_schemaId_Required IF NOT EXISTS FOR (n:`Schema`) REQUIRE n.`schemaId` IS NOT NULL;
// Unique property: schemaId
CREATE CONSTRAINT Schema_schemaId_Unique IF NOT EXISTS FOR (n:`Schema`) REQUIRE n.`schemaId` IS UNIQUE;

// Class: table
// Definition: Relational table containing columns.
// URI: http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/Table
// Mandatory property: tableId (cardinality: 1)
CREATE CONSTRAINT Table_tableId_Required IF NOT EXISTS FOR (n:`Table`) REQUIRE n.`tableId` IS NOT NULL;
// Unique property: tableId
CREATE CONSTRAINT Table_tableId_Unique IF NOT EXISTS FOR (n:`Table`) REQUIRE n.`tableId` IS UNIQUE;

// Class: user
// Definition: Principal that invokes or is evaluated against entitlement policies, including a human actor or an automated process.
// URI: http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/User
// Mandatory property: userId (cardinality: 1)
CREATE CONSTRAINT User_userId_Required IF NOT EXISTS FOR (n:`User`) REQUIRE n.`userId` IS NOT NULL;
// Unique property: userId
CREATE CONSTRAINT User_userId_Unique IF NOT EXISTS FOR (n:`User`) REQUIRE n.`userId` IS UNIQUE;

// Class: user type
// Definition: Classification of a user by the kind of actor it represents for entitlement evaluation.
// URI: http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/UserType


// Class: value source type
// Definition: Enumeration of runtime source categories used to resolve entitlement rule values.
// URI: http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/ValueSourceType
