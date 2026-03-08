from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

class UserType(Enum):
    """Classification of a user by the kind of actor it represents for entitlement evaluation."""
    HUMAN_USER = "human user"
    PROCESS_USER = "process user"

class RulePriority(Enum):
    """Enumeration of precedence levels used to order entitlement rules during evaluation."""
    HIGH_PRIORITY = "high priority"
    LOW_PRIORITY = "low priority"
    MEDIUM_PRIORITY = "medium priority"

class JdbcConnectionProfile(BaseModel):
    """JDBC endpoint and driver metadata for a target database."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    connection_timeout_seconds: Optional[int] = Field(default=None, alias="connectionTimeoutSeconds", description="The connection timeout in seconds for a JDBC connection profile.")
    jdbc_connection_profile_id: str = Field(alias="jdbcConnectionProfileId", description="The unique identifier assigned to a JDBC connection profile.", json_schema_extra={"unique": True})
    jdbc_driver: Optional[str] = Field(default=None, alias="jdbcDriver", description="The JDBC driver class or driver identifier for a connection profile.")
    jdbc_url: Optional[str] = Field(default=None, alias="jdbcUrl", description="The JDBC connection URL for a connection profile.")
    jdbc_user_name: Optional[str] = Field(default=None, alias="jdbcUserName", description="The user name used by a JDBC connection profile to authenticate to a database.")
    ssl_mode: Optional[str] = Field(default=None, alias="sslMode", description="The SSL or transport security mode configured for a JDBC connection profile.")
    connects_to: List[RelationalDatabase] = Field(default_factory=list, alias="connectsTo", description="JDBC profile connects to a target relational database.")

class Column(BaseModel):
    """Relational column protected by entitlement rules."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    column_data_type: Optional[str] = Field(default=None, alias="columnDataType", description="The declared database data type of a relational column.")
    column_default_value: Optional[str] = Field(default=None, alias="columnDefaultValue", description="The default value expression defined for a relational column.")
    column_id: str = Field(alias="columnId", description="The unique identifier assigned to a relational column.", json_schema_extra={"unique": True})
    column_length: Optional[int] = Field(default=None, alias="columnLength", description="The maximum defined length for a relational column value.")
    column_name: Optional[str] = Field(default=None, alias="columnName", description="The name of a relational column.")
    column_precision: Optional[int] = Field(default=None, alias="columnPrecision", description="The numeric precision defined for a relational column.")
    column_scale: Optional[int] = Field(default=None, alias="columnScale", description="The numeric scale defined for a relational column.")
    is_nullable: Optional[bool] = Field(default=None, alias="isNullable", description="Indicates whether a relational column permits null values.")
    ordinal_position: Optional[int] = Field(default=None, alias="ordinalPosition", description="The ordinal position of a relational column within its table.")
    belongs_to_table: List[Table] = Field(default_factory=list, alias="belongsToTable", description="A column belongs to exactly one table.")

class Schema(BaseModel):
    """Relational schema/container for tables."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    is_default_schema: Optional[bool] = Field(default=None, alias="isDefaultSchema", description="Indicates whether a relational schema is the default schema in its database context.")
    schema_description: Optional[str] = Field(default=None, alias="schemaDescription", description="A descriptive summary of the purpose or contents of a relational schema.")
    schema_id: str = Field(alias="schemaId", description="The unique identifier assigned to a relational schema.", json_schema_extra={"unique": True})
    schema_name: Optional[str] = Field(default=None, alias="schemaName", description="The name of a relational schema.")
    schema_owner: Optional[str] = Field(default=None, alias="schemaOwner", description="The owning principal or administrative owner of a relational schema.")
    schema_type: Optional[str] = Field(default=None, alias="schemaType", description="The functional or administrative type of a relational schema.")
    belongs_to_database: List[RelationalDatabase] = Field(default_factory=list, alias="belongsToDatabase", description="Schema belongs to a relational database.")

class Policy(BaseModel):
    """Bundle of row-filter and/or column-mask rules."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    definition: List[str] = Field(default_factory=list, alias="definition", description="A textual definition describing the purpose or semantics of a policy.")
    policy_id: str = Field(alias="policyId", description="The unique identifier assigned to a policy.", json_schema_extra={"unique": True})
    policy_name: List[str] = Field(default_factory=list, alias="policyName", description="The name assigned to a policy.")
    has_column_mask_rule: List[ColumnMaskRule] = Field(default_factory=list, alias="hasColumnMaskRule", description="Policy contains column masking rules.")
    has_row_filter_rule: List[RowFilterRule] = Field(default_factory=list, alias="hasRowFilterRule", description="Policy contains row-level filtering rules.")

class RelationalDatabase(BaseModel):
    """JDBC-connectable relational database platform."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    database_edition: Optional[str] = Field(default=None, alias="databaseEdition", description="The commercial or deployment edition of a relational database instance.")
    database_name: Optional[str] = Field(default=None, alias="databaseName", description="The logical or configured name of a relational database instance.")
    database_vendor: Optional[str] = Field(default=None, alias="databaseVendor", description="The database vendor or product family for a relational database instance.")
    database_version: Optional[str] = Field(default=None, alias="databaseVersion", description="The software version of a relational database instance.")
    host_name: Optional[str] = Field(default=None, alias="hostName", description="The network host name serving a relational database instance.")
    port_number: Optional[int] = Field(default=None, alias="portNumber", description="The network port used by a relational database instance.")
    relational_database_id: str = Field(alias="relationalDatabaseId", description="The unique identifier assigned to a relational database instance.", json_schema_extra={"unique": True})

class Table(BaseModel):
    """Relational table containing columns."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    is_temporary_table: Optional[bool] = Field(default=None, alias="isTemporaryTable", description="Indicates whether a relational table is temporary or session-scoped.")
    row_count_estimate: Optional[int] = Field(default=None, alias="rowCountEstimate", description="An estimated row count for a relational table.")
    table_description: Optional[str] = Field(default=None, alias="tableDescription", description="A descriptive summary of the purpose or contents of a relational table.")
    table_id: str = Field(alias="tableId", description="The unique identifier assigned to a relational table.", json_schema_extra={"unique": True})
    table_name: Optional[str] = Field(default=None, alias="tableName", description="The name of a relational table.")
    table_owner: Optional[str] = Field(default=None, alias="tableOwner", description="The owning principal or administrative owner of a relational table.")
    table_type: Optional[str] = Field(default=None, alias="tableType", description="The functional type of a relational table, such as base table or view-backed table.")
    belongs_to_schema: List[Schema] = Field(default_factory=list, alias="belongsToSchema", description="A table belongs to exactly one schema.")

class RowFilterRule(BaseModel):
    """Rule that restricts row visibility using predicates."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    comparison_operator: Optional[str] = Field(default=None, alias="comparisonOperator", description="The comparison operator a row filter rule applies when rewriting a query predicate.")
    deny_behavior: Optional[str] = Field(default=None, alias="denyBehavior", description="The enforcement behavior applied when a row filter rule denies access, such as return no rows or block query.")
    filter_action: Optional[str] = Field(default=None, alias="filterAction", description="The action a row filter rule applies when rewriting a query, such as allow or deny.")
    llm_rewrite_instruction: Optional[str] = Field(default=None, alias="llmRewriteInstruction", description="A canonical instruction telling an LLM how to rewrite a query for this row filter rule.")
    match_mode: Optional[str] = Field(default=None, alias="matchMode", description="The value cardinality mode a row filter rule expects, such as single value, multiple values, or no value.")
    rewrite_template: Optional[str] = Field(default=None, alias="rewriteTemplate", description="A deterministic query rewrite template with placeholders for runtime filter values.")
    row_filter_rule_id: str = Field(alias="rowFilterRuleId", description="The unique identifier assigned to a row filter rule.", json_schema_extra={"unique": True})
    rule_expression: Optional[str] = Field(default=None, alias="ruleExpression", description="The executable or declarative row-filter expression associated with a row filter rule.")
    value_source_expression: Optional[str] = Field(default=None, alias="valueSourceExpression", description="The expression, path, or lookup instruction used to resolve row filter values at runtime.")
    value_source_type: Optional[str] = Field(default=None, alias="valueSourceType", description="The source category used to resolve row filter values, such as static literal, subject attribute, session context, or derived query.")
    targets_filtered_column: List[Column] = Field(default_factory=list, alias="targetsFilteredColumn", description="Row-filter rule targets a specific column context.")
    has_priority: Optional[RulePriority] = Field(default=None, alias="hasPriority", description="Associates an entitlement rule with its precedence level.")

class ColumnMaskRule(BaseModel):
    """Rule that transforms or redacts sensitive column values."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    column_mask_rule_id: str = Field(alias="columnMaskRuleId", description="The unique identifier assigned to a column mask rule.", json_schema_extra={"unique": True})
    fallback_behavior: Optional[str] = Field(default=None, alias="fallbackBehavior", description="The fallback behavior applied when a column mask rule cannot resolve its masking inputs.")
    llm_rewrite_instruction: Optional[str] = Field(default=None, alias="llmRewriteInstruction", description="A canonical instruction telling an LLM how to rewrite a query projection for this column mask rule.")
    mask_action: Optional[str] = Field(default=None, alias="maskAction", description="The masking action a column mask rule applies, such as reveal, redact, tokenize, or substitute.")
    mask_value_expression: Optional[str] = Field(default=None, alias="maskValueExpression", description="The expression used to compute the masked value emitted by a column mask rule.")
    masking_method: Optional[str] = Field(default=None, alias="maskingMethod", description="The masking method or transformation strategy used by a column mask rule.")
    rewrite_template: Optional[str] = Field(default=None, alias="rewriteTemplate", description="A deterministic projection rewrite template with placeholders for masked output values.")
    rule_expression: Optional[str] = Field(default=None, alias="ruleExpression", description="The executable or declarative masking expression associated with a column mask rule.")
    value_source_expression: Optional[str] = Field(default=None, alias="valueSourceExpression", description="The expression, path, or lookup instruction used to resolve masking inputs at runtime.")
    value_source_type: Optional[str] = Field(default=None, alias="valueSourceType", description="The source category used to resolve masking inputs, such as static literal, subject attribute, session context, or derived query.")
    targets_masked_column: List[Column] = Field(default_factory=list, alias="targetsMaskedColumn", description="Column-mask rule targets a specific column.")
    has_priority: Optional[RulePriority] = Field(default=None, alias="hasPriority", description="Associates an entitlement rule with its precedence level.")

class PolicyGroup(BaseModel):
    """Collection of policies mapped to a persona, role, or function."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    policy_group_id: str = Field(alias="policyGroupId", description="The unique identifier assigned to a policy group.", json_schema_extra={"unique": True})
    policy_group_name: List[str] = Field(default_factory=list, alias="policyGroupName", description="The name assigned to a policy group.")
    includes_policy: List[Policy] = Field(default_factory=list, alias="includesPolicy", description="Policy group bundles one or more policies.")

class User(BaseModel):
    """Principal that invokes or is evaluated against entitlement policies, including a human actor or an automated process."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    user_id: str = Field(alias="userId", description="The unique identifier assigned to a user.", json_schema_extra={"unique": True})
    is_member_of: List[PolicyGroup] = Field(default_factory=list, alias="isMemberOf", description="User inherits policies via policy group membership.")
    has_user_type: Optional[UserType] = Field(default=None, alias="hasUserType", description="A user is classified by a user type that identifies whether it is a human actor or an automated process.")
