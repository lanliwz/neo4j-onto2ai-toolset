from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ReportStatus(Enum):
    draft = "draft"
    submitted = "submitted"
    accepted = "accepted"
    rejected = "rejected"
    amended = "amended"
    withdrawn = "withdrawn"


class FilingStatus(Enum):
    single = "single"
    marriedFilingJointly = "marriedFilingJointly"
    marriedFilingSeparately = "marriedFilingSeparately"
    headOfHousehold = "headOfHousehold"
    qualifyingSurvivingSpouse = "qualifyingSurvivingSpouse"


class Agent(BaseModel):
    """skos:definition: something autonomous that can adapt to and interact with its environment"""

    model_config = ConfigDict(extra="forbid")

    has_textual_name: Optional[List[str]] = Field(
        default=None,
        description="associates a name, reference name, or appellation with an individual concept",
    )  # uri: https://model.onto2ai.com/schema/hasTextualName

    has_name: Optional[List[ContextualName]] = Field(
        default=None,
        description="is known by",
    )  # uri: https://model.onto2ai.com/schema/hasName


class Party(BaseModel):
    """skos:definition: person or organization"""

    model_config = ConfigDict(extra="forbid")

    has_textual_name: Optional[List[str]] = Field(
        default=None,
        description="associates a name, reference name, or appellation with an individual concept",
    )  # uri: https://model.onto2ai.com/schema/hasTextualName

    has_address: Optional[List[PhysicalAddress]] = Field(
        default=None,
        description="indicates a means by which an entity may be located or contacted or may receive correspondence",
    )  # uri: https://model.onto2ai.com/schema/hasAddress
    has_mailing_address: Optional[List[PhysicalAddress]] = Field(
        default=None,
        description="identifies a physical address where an independent party can receive communications",
    )  # uri: https://model.onto2ai.com/schema/hasMailingAddress
    has_registered_address: Optional[List[ConventionalStreetAddress]] = Field(
        default=None,
        description="identifies an address that is officially recorded with some government authority and at which legal papers may be served",
    )  # uri: https://model.onto2ai.com/schema/hasRegisteredAddress
    has_capacity: Optional[List[LegalCapacity]] = Field(
        default=None,
        description="identifies an individual or organization that has some ability and availability to carry out certain actions, or has certain rights or obligations",
    )  # uri: https://model.onto2ai.com/schema/hasCapacity
    has_responsibility: Optional[List[Duty]] = Field(
        default=None,
        description="specifies a commitment or obligation that an independent party has",
    )  # uri: https://model.onto2ai.com/schema/hasResponsibility
    has_name: Optional[List[ContextualName]] = Field(
        default=None,
        description="is known by",
    )  # uri: https://model.onto2ai.com/schema/hasName

    has_filing_status: Optional[FilingStatusConcept] = Field(
        default=None,
        description="associates a party with its tax filing status category",
    )  # uri: https://model.onto2ai.com/schema/hasFilingStatus


class LegalPerson(BaseModel):
    """skos:definition: party that is recognized as having rights and obligations under the law, including but not limited to the right to sue and be sued, enter into contracts, own property, and incur financial and other obligations"""

    model_config = ConfigDict(extra="forbid")

    has_textual_name: Optional[List[str]] = Field(
        default=None,
        description="associates a name, reference name, or appellation with an individual concept",
    )  # uri: https://model.onto2ai.com/schema/hasTextualName

    is_recognized_in: Optional[List[Jurisdiction]] = Field(
        default=None,
        description="indicates the jurisdiction in which a legal person is considered competent to enter into a contract, conduct business, or participate in other activities, or in which an agreement may be acknowledged and possibly enforceable",
    )  # uri: https://model.onto2ai.com/schema/isRecognizedIn
    is_identified_by: Optional[List[LegalEntityIdentifier]] = Field(
        default=None,
        description="has an identifier that is unique within some context",
    )  # uri: https://model.onto2ai.com/schema/isIdentifiedBy
    employs: Optional[List[Person]] = Field(
        default=None,
        description="indicates someone that is employed by the legal person",
    )  # uri: https://model.onto2ai.com/schema/employs
    has_investment_ownership: Optional[List[EntityOwnership]] = Field(
        default=None,
        description="relates a legal person to the context in which it owns a formal organization",
    )  # uri: https://model.onto2ai.com/schema/hasInvestmentOwnership
    has_principal_executive_office_address: Optional[List[ConventionalStreetAddress]] = Field(
        default=None,
        description="relates an organization to its principal executive address",
    )  # uri: https://model.onto2ai.com/schema/hasPrincipalExecutiveOfficeAddress
    is_authorizee_in: Optional[List[Authorization]] = Field(
        default=None,
        description="indicates the situation that facilitates designation of the legal person as an authorized party for some purpose",
    )  # uri: https://model.onto2ai.com/schema/isAuthorizeeIn
    is_authorizor_in: Optional[List[Authorization]] = Field(
        default=None,
        description="indicates the situation that facilitates designation of an authorized party by the legal person for some purpose",
    )  # uri: https://model.onto2ai.com/schema/isAuthorizorIn
    is_directly_authorized_by: Optional[List[AuthorisingParty]] = Field(
        default=None,
        description="is directly endorsed, enabled, empowered, or otherwise permitted by",
    )  # uri: https://model.onto2ai.com/schema/isDirectlyAuthorizedBy
    has_address: Optional[List[PhysicalAddress]] = Field(
        default=None,
        description="indicates a means by which an entity may be located or contacted or may receive correspondence",
    )  # uri: https://model.onto2ai.com/schema/hasAddress
    has_mailing_address: Optional[List[PhysicalAddress]] = Field(
        default=None,
        description="identifies a physical address where an independent party can receive communications",
    )  # uri: https://model.onto2ai.com/schema/hasMailingAddress
    has_registered_address: Optional[List[ConventionalStreetAddress]] = Field(
        default=None,
        description="identifies an address that is officially recorded with some government authority and at which legal papers may be served",
    )  # uri: https://model.onto2ai.com/schema/hasRegisteredAddress
    has_capacity: Optional[List[LegalCapacity]] = Field(
        default=None,
        description="identifies an individual or organization that has some ability and availability to carry out certain actions, or has certain rights or obligations",
    )  # uri: https://model.onto2ai.com/schema/hasCapacity
    has_responsibility: Optional[List[Duty]] = Field(
        default=None,
        description="specifies a commitment or obligation that an independent party has",
    )  # uri: https://model.onto2ai.com/schema/hasResponsibility
    has_name: Optional[List[ContextualName]] = Field(
        default=None,
        description="is known by",
    )  # uri: https://model.onto2ai.com/schema/hasName


class FormalOrganisation(BaseModel):
    """skos:definition: organization that is recognized in some legal jurisdiction, with associated rights and responsibilities"""

    model_config = ConfigDict(extra="forbid")

    has_textual_name: Optional[List[str]] = Field(
        default=None,
        description="associates a name, reference name, or appellation with an individual concept",
    )  # uri: https://model.onto2ai.com/schema/hasTextualName

    is_classified_by_sic: Optional[List[StandardIndustrialClassificationCode]] = Field(
        default=None,
        description="is systematically grouped based on characteristics by",
    )  # uri: https://model.onto2ai.com/schema/isClassifiedBy
    is_classified_by_naics: Optional[List[NorthAmericanIndustryClassificationSystemCode]] = Field(
        default=None,
        description="is systematically grouped based on characteristics by",
    )  # uri: https://model.onto2ai.com/schema/isClassifiedBy
    is_domiciled_in: Optional[List[GeopoliticalEntity]] = Field(
        default=None,
        description="indicates the principal place where an entity conducts business within some country, such as where its headquarters is located",
    )  # uri: https://model.onto2ai.com/schema/isDomiciledIn
    has_member: Optional[List[Party]] = Field(
        default=None,
        description="includes, as a discrete element",
    )  # uri: https://model.onto2ai.com/schema/hasMember
    has_name: Optional[List[OrganizationName]] = Field(
        default=None,
        description="is known by",
    )  # uri: https://model.onto2ai.com/schema/hasName
    has_goal: Optional[List[Goal]] = Field(
        default=None,
        description="has long-term, desired outcome",
    )  # uri: https://model.onto2ai.com/schema/hasGoal
    has_part: Optional[List[Organization]] = Field(
        default=None,
        description="indicates any portion of something",
    )  # uri: https://model.onto2ai.com/schema/hasPart
    has_sub_unit: Optional[List[OrganizationalSubUnit]] = Field(
        default=None,
        description="relates an organization to a part of that organization",
    )  # uri: https://model.onto2ai.com/schema/hasSubUnit
    has_operating_address: Optional[List[PhysicalAddress]] = Field(
        default=None,
        description="indicates an address at which an organization carries out operations",
    )  # uri: https://model.onto2ai.com/schema/hasOperatingAddress
    has_address: Optional[List[PhysicalAddress]] = Field(
        default=None,
        description="indicates a means by which an entity may be located or contacted or may receive correspondence",
    )  # uri: https://model.onto2ai.com/schema/hasAddress
    has_mailing_address: Optional[List[PhysicalAddress]] = Field(
        default=None,
        description="identifies a physical address where an independent party can receive communications",
    )  # uri: https://model.onto2ai.com/schema/hasMailingAddress
    has_registered_address: Optional[List[ConventionalStreetAddress]] = Field(
        default=None,
        description="identifies an address that is officially recorded with some government authority and at which legal papers may be served",
    )  # uri: https://model.onto2ai.com/schema/hasRegisteredAddress
    has_capacity: Optional[List[LegalCapacity]] = Field(
        default=None,
        description="identifies an individual or organization that has some ability and availability to carry out certain actions, or has certain rights or obligations",
    )  # uri: https://model.onto2ai.com/schema/hasCapacity
    has_responsibility: Optional[List[Duty]] = Field(
        default=None,
        description="specifies a commitment or obligation that an independent party has",
    )  # uri: https://model.onto2ai.com/schema/hasResponsibility
    has_contextual_name: Optional[List[ContextualName]] = Field(
        default=None,
        description="is known by",
    )  # uri: https://model.onto2ai.com/schema/hasName


class DatePeriod(BaseModel):
    """skos:definition: time span over one or more calendar days"""

    model_config = ConfigDict(extra="forbid")

    has_duration: Optional[str] = Field(
        default=None,
        description="specifies the time during which something continues",
    )  # uri: https://model.onto2ai.com/schema/hasDuration
    has_end_date: Optional[date] = Field(
        default=None,
        description="indicates the final or ending date associated with something",
    )  # uri: https://model.onto2ai.com/schema/hasEndDate
    has_start_date: Optional[date] = Field(
        default=None,
        description="indicates the initial date associated with something",
    )  # uri: https://model.onto2ai.com/schema/hasStartDate


class Service(BaseModel):
    """skos:definition: intangible activity performed by some party for the benefit of another party"""

    model_config = ConfigDict(extra="forbid")

    is_provided_by: Optional[List[ServiceProvider]] = Field(
        default=None,
        description="is made available by",
    )  # uri: https://model.onto2ai.com/schema/isProvidedBy
    provides: Optional[List[Capability]] = Field(
        default=None,
        description="makes available",
    )  # uri: https://model.onto2ai.com/schema/provides
    is_provisioned_by: Optional[List[ServiceProvider]] = Field(
        default=None,
        description="identifies the service provider that provisions the service or facility",
    )  # uri: https://model.onto2ai.com/schema/isProvisionedBy


class Report(BaseModel):
    """skos:definition: document that provides a structured description of something, prepared on ad hoc, periodic, recurring, regular, or as required basis"""

    model_config = ConfigDict(extra="forbid")

    is_provided_by: Optional[List[ReportingParty]] = Field(
        default=None,
        description="is made available by",
    )  # uri: https://model.onto2ai.com/schema/isProvidedBy
    is_submitted_by: Optional[List[Submitter]] = Field(
        default=None,
        description="indicates the party that submits something",
    )  # uri: https://model.onto2ai.com/schema/isSubmittedBy
    has_reporting_period: Optional[List[DatePeriod]] = Field(
        default=None,
        description="specifies the reporting period for which a report applies",
    )  # uri: https://model.onto2ai.com/schema/hasReportingPeriod
    has_report_date_time: Optional[datetime] = Field(
        default=None,
        description="date and time at which a report was issued",
    )  # uri: https://model.onto2ai.com/schema/hasReportDateTime
    has_report_date: Optional[date] = Field(
        default=None,
        description="date on which a report was issued",
    )  # uri: https://model.onto2ai.com/schema/hasReportDate
    is_submitted_to: Optional[List[PartyRole]] = Field(
        default=None,
        description="indicates the party to which something is submitted",
    )  # uri: https://model.onto2ai.com/schema/isSubmittedTo
    is_reported_to: Optional[List[PartyRole]] = Field(
        default=None,
        description="indicates the party to which something is reported",
    )  # uri: https://model.onto2ai.com/schema/isReportedTo
    has_report_status: Optional[ReportStatusConcept] = Field(
        default=None,
        description="associates a report with its processing/lifecycle status",
    )  # uri: https://model.onto2ai.com/schema/hasReportStatus


class Facility(BaseModel):
    """skos:definition: something established to serve a particular purpose, make some course of action or operation easier, or provide some capability or service"""

    model_config = ConfigDict(extra="forbid")

    is_situated_at: Optional[List[Site]] = Field(
        default=None,
        description="is placed at",
    )  # uri: https://model.onto2ai.com/schema/isSituatedAt
    enables: Optional[List[Capability]] = Field(
        default=None,
        description="creates an environment or situation where something can occur or function efficiently",
    )  # uri: https://model.onto2ai.com/schema/enables


class TaxIdentifier(BaseModel):
    """skos:definition: identifier assigned to a taxpayer that enables compulsory financial charges and other levies to be imposed on the taxpayer by a governmental organization in order to fund government spending and various public expenditures"""

    model_config = ConfigDict(extra="forbid")

    has_text_value: Optional[List[str]] = Field(
        default=None,
        description="provides a string value for something, with or without a language tag",
    )  # uri: https://model.onto2ai.com/schema/hasTextValue

    is_applicable_in: Optional[List[Jurisdiction]] = Field(
        default=None,
        description="indicates a context in which something is relevant",
    )  # uri: https://model.onto2ai.com/schema/isApplicableIn
    is_member_of: Optional[List[TaxIdentificationScheme]] = Field(
        default=None,
        description="is a discrete element of",
    )  # uri: https://model.onto2ai.com/schema/isMemberOf
    identifies: Optional[List[Party]] = Field(
        default=None,
        description="recognizes or establishes identity within some context",
    )  # uri: https://model.onto2ai.com/schema/identifies
    complies_with: Optional[List[IdentificationScheme]] = Field(
        default=None,
        description="adheres to policies or rules specified in",
    )  # uri: https://model.onto2ai.com/schema/compliesWith


class Submitter(BaseModel):
    """skos:definition: party presenting something, such as a regulatory report"""

    model_config = ConfigDict(extra="forbid")

    submits: Optional[List[Report]] = Field(
        default=None,
        description="presents something for consideration or review",
    )  # uri: https://model.onto2ai.com/schema/submits
    has_applicable_period: Optional[List[DatePeriod]] = Field(
        default=None,
        description="indicates a date period during which something may be used, applies, is valid or is accurate or relevant",
    )  # uri: https://model.onto2ai.com/schema/hasApplicablePeriod
    is_played_by_party: Optional[List[Party]] = Field(
        default=None,
        description="indicates something filling a role",
    )  # uri: https://model.onto2ai.com/schema/isPlayedBy
    designates: Optional[List[PartyRole]] = Field(
        default=None,
        description="appoints someone officially",
    )  # uri: https://model.onto2ai.com/schema/designates
    is_designated_by: Optional[List[PartyRole]] = Field(
        default=None,
        description="indicates the role of the party that has assigned or appointed someone",
    )  # uri: https://model.onto2ai.com/schema/isDesignatedBy
    has_related_party_role: Optional[List[PartyRole]] = Field(
        default=None,
        description="relates a party acting in a specific role directly to another party acting in the same or another role",
    )  # uri: https://model.onto2ai.com/schema/hasRelatedPartyRole
    elects: Optional[List[PartyRole]] = Field(
        default=None,
        description="chooses someone to hold office or position",
    )  # uri: https://model.onto2ai.com/schema/elects
    nominates: Optional[List[PartyRole]] = Field(
        default=None,
        description="appoints or proposes for appointment",
    )  # uri: https://model.onto2ai.com/schema/nominates
    is_played_by_agent: Optional[List[Agent]] = Field(
        default=None,
        description="indicates something filling a role",
    )  # uri: https://model.onto2ai.com/schema/isPlayedBy
    is_object_role_in: Optional[List[Situation]] = Field(
        default=None,
        description="indicates a situation in which the role is secondary",
    )  # uri: https://model.onto2ai.com/schema/isObjectRoleIn
    is_subject_role_in: Optional[List[Situation]] = Field(
        default=None,
        description="indicates a situation in which the role is the primary topic",
    )  # uri: https://model.onto2ai.com/schema/isSubjectRoleIn


class ReportingParty(BaseModel):
    """skos:definition: party providing a report, typically in response to some contractual, legal, regulatory or other business requirement"""

    model_config = ConfigDict(extra="forbid")

    provides: Optional[List[Report]] = Field(
        default=None,
        description="makes available",
    )  # uri: https://model.onto2ai.com/schema/provides
    has_applicable_period: Optional[List[DatePeriod]] = Field(
        default=None,
        description="indicates a date period during which something may be used, applies, is valid or is accurate or relevant",
    )  # uri: https://model.onto2ai.com/schema/hasApplicablePeriod
    is_played_by_party: Optional[List[Party]] = Field(
        default=None,
        description="indicates something filling a role",
    )  # uri: https://model.onto2ai.com/schema/isPlayedBy
    designates: Optional[List[PartyRole]] = Field(
        default=None,
        description="appoints someone officially",
    )  # uri: https://model.onto2ai.com/schema/designates
    is_designated_by: Optional[List[PartyRole]] = Field(
        default=None,
        description="indicates the role of the party that has assigned or appointed someone",
    )  # uri: https://model.onto2ai.com/schema/isDesignatedBy
    has_related_party_role: Optional[List[PartyRole]] = Field(
        default=None,
        description="relates a party acting in a specific role directly to another party role",
    )  # uri: https://model.onto2ai.com/schema/hasRelatedPartyRole
    elects: Optional[List[PartyRole]] = Field(
        default=None,
        description="chooses someone to hold office or position",
    )  # uri: https://model.onto2ai.com/schema/elects
    nominates: Optional[List[PartyRole]] = Field(
        default=None,
        description="appoints or proposes for appointment",
    )  # uri: https://model.onto2ai.com/schema/nominates
    is_played_by_agent: Optional[List[Agent]] = Field(
        default=None,
        description="indicates something filling a role",
    )  # uri: https://model.onto2ai.com/schema/isPlayedBy
    is_object_role_in: Optional[List[Situation]] = Field(
        default=None,
        description="indicates a situation in which the role is secondary",
    )  # uri: https://model.onto2ai.com/schema/isObjectRoleIn
    is_subject_role_in: Optional[List[Situation]] = Field(
        default=None,
        description="indicates a situation in which the role is the primary topic",
    )  # uri: https://model.onto2ai.com/schema/isSubjectRoleIn


class PartyRole(BaseModel):
    """skos:definition: role played by an organization or individual that may be time bound"""

    model_config = ConfigDict(extra="forbid")

    has_applicable_period: Optional[List[DatePeriod]] = Field(
        default=None,
        description="indicates a date period during which something may be used, applies, is valid or is accurate or relevant",
    )  # uri: https://model.onto2ai.com/schema/hasApplicablePeriod
    is_played_by_party: Optional[List[Party]] = Field(
        default=None,
        description="indicates something filling a role",
    )  # uri: https://model.onto2ai.com/schema/isPlayedBy
    designates: Optional[List[PartyRole]] = Field(
        default=None,
        description="appoints someone officially",
    )  # uri: https://model.onto2ai.com/schema/designates
    is_designated_by: Optional[List[PartyRole]] = Field(
        default=None,
        description="indicates the role of the party that has assigned or appointed someone",
    )  # uri: https://model.onto2ai.com/schema/isDesignatedBy
    has_related_party_role: Optional[List[PartyRole]] = Field(
        default=None,
        description="relates a party role to another party role",
    )  # uri: https://model.onto2ai.com/schema/hasRelatedPartyRole
    elects: Optional[List[PartyRole]] = Field(
        default=None,
        description="chooses someone to hold office or position",
    )  # uri: https://model.onto2ai.com/schema/elects
    nominates: Optional[List[PartyRole]] = Field(
        default=None,
        description="appoints or proposes for appointment",
    )  # uri: https://model.onto2ai.com/schema/nominates
    is_played_by_agent: Optional[List[Agent]] = Field(
        default=None,
        description="indicates something filling a role",
    )  # uri: https://model.onto2ai.com/schema/isPlayedBy
    is_object_role_in: Optional[List[Situation]] = Field(
        default=None,
        description="indicates a situation in which the role is secondary",
    )  # uri: https://model.onto2ai.com/schema/isObjectRoleIn
    is_subject_role_in: Optional[List[Situation]] = Field(
        default=None,
        description="indicates a situation in which the role is the primary topic",
    )  # uri: https://model.onto2ai.com/schema/isSubjectRoleIn


class Situation(BaseModel):
    """skos:definition: setting, state of being, or relationship that is relatively stable for some period of time"""

    model_config = ConfigDict(extra="forbid")

    has_object_role: Optional[List[Role]] = Field(
        default=None,
        description="identifies a person or thing that is affected by, or is a secondary argument in a specific role with respect to a given relation or situation",
    )  # uri: https://model.onto2ai.com/schema/hasObjectRole
    has_subject_role: Optional[List[Role]] = Field(
        default=None,
        description="identifies the person or thing that is being discussed, described, dealt with, or is the main topic in a specific role with respect to a given situation",
    )  # uri: https://model.onto2ai.com/schema/hasSubjectRole
    holds_during: Optional[List[DatePeriod]] = Field(
        default=None,
        description="indicates a date period during which something is true",
    )  # uri: https://model.onto2ai.com/schema/holdsDuring
    has_actor: Optional[List[Actor]] = Field(
        default=None,
        description="identifies the primary party acting in a specific role with respect to a given situation",
    )  # uri: https://model.onto2ai.com/schema/hasActor
    has_undergoer: Optional[List[Undergoer]] = Field(
        default=None,
        description="identifies an experiencer / passive or other object role in a given situation",
    )  # uri: https://model.onto2ai.com/schema/hasUndergoer


class Authorization(BaseModel):
    """skos:definition: situation in which a party authorizes someone to act on their behalf or to have specific capabilities under certain conditions for some period of time"""

    model_config = ConfigDict(extra="forbid")

    has_authorized_party: Optional[List[AuthorisedParty]] = Field(
        default=None,
        description="indicates the party (role) that is endorsed, enabled, empowered, or otherwise permitted to do something in the situation",
    )  # uri: https://model.onto2ai.com/schema/hasAuthorizedParty
    has_authorizing_party: Optional[List[AuthorisingParty]] = Field(
        default=None,
        description="indicates the party (role) that endorses, enables, empowers, or gives permission in the situation",
    )  # uri: https://model.onto2ai.com/schema/hasAuthorizingParty
    has_authorizee: Optional[List[LegalPerson]] = Field(
        default=None,
        description="indicates the legal person that is endorsed, enabled, empowered, or otherwise permitted to do something in the situation",
    )  # uri: https://model.onto2ai.com/schema/hasAuthorizee
    has_authorizor: Optional[List[LegalPerson]] = Field(
        default=None,
        description="indicates the legal person that endorses, enables, empowers, or gives permission in the situation",
    )  # uri: https://model.onto2ai.com/schema/hasAuthorizor
    has_object_role: Optional[List[Role]] = Field(
        default=None,
        description="identifies a person or thing that is affected by, or is a secondary argument in a specific role with respect to a given relation or situation",
    )  # uri: https://model.onto2ai.com/schema/hasObjectRole
    has_subject_role: Optional[List[Role]] = Field(
        default=None,
        description="identifies the person or thing that is being discussed, described, dealt with, or is the main topic in a specific role with respect to a given situation",
    )  # uri: https://model.onto2ai.com/schema/hasSubjectRole
    holds_during: Optional[List[DatePeriod]] = Field(
        default=None,
        description="indicates a date period during which something is true",
    )  # uri: https://model.onto2ai.com/schema/holdsDuring
    has_actor: Optional[List[Actor]] = Field(
        default=None,
        description="identifies the primary party acting in a specific role with respect to a given situation",
    )  # uri: https://model.onto2ai.com/schema/hasActor
    has_undergoer: Optional[List[Undergoer]] = Field(
        default=None,
        description="identifies an experiencer / passive or other object role in a given situation",
    )  # uri: https://model.onto2ai.com/schema/hasUndergoer


class AuthorisedParty(BaseModel):
    """skos:definition: party that has been given the ability to act on behalf of another party or to have specified capabilities under some set of guidelines for some period of time"""

    model_config = ConfigDict(extra="forbid")

    is_played_by: Optional[List[LegalPerson]] = Field(
        default=None,
        description="indicates something filling a role",
    )  # uri: https://model.onto2ai.com/schema/isPlayedBy
    is_authorized_through: Optional[List[Authorization]] = Field(
        default=None,
        description="indicates the situation that facilitates endorsement of the authorized party for some purpose",
    )  # uri: https://model.onto2ai.com/schema/isAuthorizedThrough
    is_authorized_by: Optional[List[AuthorisingParty]] = Field(
        default=None,
        description="is endorsed, enabled, empowered, or otherwise permitted by",
    )  # uri: https://model.onto2ai.com/schema/isAuthorizedBy
    is_object_role_in: Optional[List[Situation]] = Field(
        default=None,
        description="indicates a situation in which the role is secondary",
    )  # uri: https://model.onto2ai.com/schema/isObjectRoleIn
    is_subject_role_in: Optional[List[Situation]] = Field(
        default=None,
        description="indicates a situation in which the role is the primary topic",
    )  # uri: https://model.onto2ai.com/schema/isSubjectRoleIn


class RegulatoryAgency(BaseModel):
    """skos:definition: public authority or government agency responsible for exercising authority over something in a regulatory or supervisory capacity"""

    model_config = ConfigDict(extra="forbid")

    is_played_by_formal_organisation: Optional[List[FormalOrganisation]] = Field(
        default=None,
        description="indicates something filling a role",
    )  # uri: https://model.onto2ai.com/schema/isPlayedBy
    issues: Optional[List[GovernmentIssuedLicense]] = Field(
        default=None,
        description="officially makes something available",
    )  # uri: https://model.onto2ai.com/schema/issues
    provides_regulatory_service: Optional[List[RegulatoryService]] = Field(
        default=None,
        description="makes available",
    )  # uri: https://model.onto2ai.com/schema/provides
    has_jurisdiction: Optional[List[Jurisdiction]] = Field(
        default=None,
        description="relates a regulatory agency to a jurisdiction over which it has some level of legal authority",
    )  # uri: https://model.onto2ai.com/schema/hasJurisdiction
    is_played_by_legal_person: Optional[List[LegalPerson]] = Field(
        default=None,
        description="indicates something filling a role",
    )  # uri: https://model.onto2ai.com/schema/isPlayedBy
    authorizes_through: Optional[List[Authorization]] = Field(
        default=None,
        description="indicates the situation that facilitates designation of an authorized party by the authorizing party",
    )  # uri: https://model.onto2ai.com/schema/authorizesThrough
    authorizes: Optional[List[AuthorisedParty]] = Field(
        default=None,
        description="endorses, enables, empowers, or gives permission to",
    )  # uri: https://model.onto2ai.com/schema/authorizes
    authorizes_directly: Optional[List[LegalPerson]] = Field(
        default=None,
        description="endorses, enables, empowers, or gives permission directly to",
    )  # uri: https://model.onto2ai.com/schema/authorizesDirectly
    provides_service: Optional[List[Service]] = Field(
        default=None,
        description="makes available",
    )  # uri: https://model.onto2ai.com/schema/provides
    provisions_service: Optional[List[Service]] = Field(
        default=None,
        description="customizes, provides, or outfits something required for use in delivering a service",
    )  # uri: https://model.onto2ai.com/schema/provisions
    provisions_facility: Optional[List[Facility]] = Field(
        default=None,
        description="customizes, provides, or outfits something required for use in delivering a service",
    )  # uri: https://model.onto2ai.com/schema/provisions
    acts_in: Optional[List[Situation]] = Field(
        default=None,
        description="indicates a situation in which the actor plays a primary role",
    )  # uri: https://model.onto2ai.com/schema/actsIn
    is_played_by_party: Optional[List[Party]] = Field(
        default=None,
        description="indicates something filling a role",
    )  # uri: https://model.onto2ai.com/schema/isPlayedBy
    is_played_by_agent: Optional[List[Agent]] = Field(
        default=None,
        description="indicates something filling a role",
    )  # uri: https://model.onto2ai.com/schema/isPlayedBy
    has_applicable_period: Optional[List[DatePeriod]] = Field(
        default=None,
        description="indicates a date period during which something may be used, applies, is valid or relevant",
    )  # uri: https://model.onto2ai.com/schema/hasApplicablePeriod
    designates: Optional[List[PartyRole]] = Field(
        default=None,
        description="appoints someone officially",
    )  # uri: https://model.onto2ai.com/schema/designates
    is_designated_by: Optional[List[PartyRole]] = Field(
        default=None,
        description="indicates the role of the party that has assigned or appointed someone",
    )  # uri: https://model.onto2ai.com/schema/isDesignatedBy
    has_related_party_role: Optional[List[PartyRole]] = Field(
        default=None,
        description="relates a party acting in a specific role directly to another party role",
    )  # uri: https://model.onto2ai.com/schema/hasRelatedPartyRole
    elects: Optional[List[PartyRole]] = Field(
        default=None,
        description="chooses someone to hold office or position",
    )  # uri: https://model.onto2ai.com/schema/elects
    nominates: Optional[List[PartyRole]] = Field(
        default=None,
        description="appoints or proposes for appointment",
    )  # uri: https://model.onto2ai.com/schema/nominates
    is_object_role_in: Optional[List[Situation]] = Field(
        default=None,
        description="indicates a situation in which the role is secondary",
    )  # uri: https://model.onto2ai.com/schema/isObjectRoleIn
    is_subject_role_in: Optional[List[Situation]] = Field(
        default=None,
        description="indicates a situation in which the role is the primary topic",
    )  # uri: https://model.onto2ai.com/schema/isSubjectRoleIn


class RegulatoryService(BaseModel):
    """skos:definition: service provided by a regulatory agency, which may include, but not be limited to, examination, monitoring, supervision, testing, or other capabilities required to ensure the integrity, fairness, safety, or other capacity of a given industry, organization, or product"""

    model_config = ConfigDict(extra="forbid")

    is_provided_by_regulatory_agency: Optional[List[RegulatoryAgency]] = Field(
        default=None,
        description="is made available by",
    )  # uri: https://model.onto2ai.com/schema/isProvidedBy
    is_provided_by_service_provider: Optional[List[ServiceProvider]] = Field(
        default=None,
        description="is made available by",
    )  # uri: https://model.onto2ai.com/schema/isProvidedBy
    provides: Optional[List[Capability]] = Field(
        default=None,
        description="makes available",
    )  # uri: https://model.onto2ai.com/schema/provides
    is_provisioned_by: Optional[List[ServiceProvider]] = Field(
        default=None,
        description="identifies the service provider that provisions the service or facility",
    )  # uri: https://model.onto2ai.com/schema/isProvisionedBy


class GovernmentIssuedLicense(BaseModel):
    """skos:definition: grant of permission needed to legally perform some task, provide some service, exercise a certain privilege, or pursue some business or occupation"""

    model_config = ConfigDict(extra="forbid")

    is_issued_by_regulatory_agency: Optional[List[RegulatoryAgency]] = Field(
        default=None,
        description="indicates the party responsible for circulating, distributing, or publishing something",
    )  # uri: https://model.onto2ai.com/schema/isIssuedBy
    confers: Optional[List[LegalCapacity]] = Field(
        default=None,
        description="grants or bestows by virtue of some authority",
    )  # uri: https://model.onto2ai.com/schema/confers
    is_issued_by_licensor: Optional[List[Licensor]] = Field(
        default=None,
        description="indicates the party responsible for issuing the license",
    )  # uri: https://model.onto2ai.com/schema/isIssuedBy
    has_party_role: Optional[List[Licensee]] = Field(
        default=None,
        description="identifies a specific role played by some person or organization as related to a situation, agreement, contract, policy, regulation, activity or other relationship",
    )  # uri: https://model.onto2ai.com/schema/hasPartyRole
    holds_during: Optional[List[DatePeriod]] = Field(
        default=None,
        description="indicates a date period during which something is true",
    )  # uri: https://model.onto2ai.com/schema/holdsDuring


class TaxAuthority(BaseModel):
    """skos:definition: regulatory agency that has jurisdiction over the assessment, determination, collection, imposition and other aspects of any tax"""

    model_config = ConfigDict(extra="forbid")

    issues_tax_identifier: Optional[List[TaxIdentifier]] = Field(
        default=None,
        description="officially makes something available",
    )  # uri: https://model.onto2ai.com/schema/issues
    has_jurisdiction: Optional[List[Jurisdiction]] = Field(
        default=None,
        description="relates a tax authority to a jurisdiction over which it has some level of legal authority",
    )  # uri: https://model.onto2ai.com/schema/hasJurisdiction
    manages: Optional[List[TaxIdentificationScheme]] = Field(
        default=None,
        description="relates a party role to something it directs or administers",
    )  # uri: https://model.onto2ai.com/schema/manages
    is_played_by_formal_organisation: Optional[List[FormalOrganisation]] = Field(
        default=None,
        description="indicates something filling a role",
    )  # uri: https://model.onto2ai.com/schema/isPlayedBy
    issues_license: Optional[List[GovernmentIssuedLicense]] = Field(
        default=None,
        description="officially makes something available",
    )  # uri: https://model.onto2ai.com/schema/issues
    provides_regulatory_service: Optional[List[RegulatoryService]] = Field(
        default=None,
        description="makes available",
    )  # uri: https://model.onto2ai.com/schema/provides
    is_played_by_legal_person: Optional[List[LegalPerson]] = Field(
        default=None,
        description="indicates something filling a role",
    )  # uri: https://model.onto2ai.com/schema/isPlayedBy
    authorizes_through: Optional[List[Authorization]] = Field(
        default=None,
        description="indicates the situation that facilitates designation of an authorized party by the authorizing party",
    )  # uri: https://model.onto2ai.com/schema/authorizesThrough
    authorizes: Optional[List[AuthorisedParty]] = Field(
        default=None,
        description="endorses, enables, empowers, or gives permission to",
    )  # uri: https://model.onto2ai.com/schema/authorizes
    authorizes_directly: Optional[List[LegalPerson]] = Field(
        default=None,
        description="endorses, enables, empowers, or gives permission directly to",
    )  # uri: https://model.onto2ai.com/schema/authorizesDirectly
    provides_service: Optional[List[Service]] = Field(
        default=None,
        description="makes available",
    )  # uri: https://model.onto2ai.com/schema/provides
    provisions_service: Optional[List[Service]] = Field(
        default=None,
        description="customizes, provides, or outfits something required for use in delivering a service",
    )  # uri: https://model.onto2ai.com/schema/provisions
    provisions_facility: Optional[List[Facility]] = Field(
        default=None,
        description="customizes, provides, or outfits something required for use in delivering a service",
    )  # uri: https://model.onto2ai.com/schema/provisions
    acts_in: Optional[List[Situation]] = Field(
        default=None,
        description="indicates a situation in which the actor plays a primary role",
    )  # uri: https://model.onto2ai.com/schema/actsIn
    is_played_by_party: Optional[List[Party]] = Field(
        default=None,
        description="indicates something filling a role",
    )  # uri: https://model.onto2ai.com/schema/isPlayedBy
    is_played_by_agent: Optional[List[Agent]] = Field(
        default=None,
        description="indicates something filling a role",
    )  # uri: https://model.onto2ai.com/schema/isPlayedBy
    has_applicable_period: Optional[List[DatePeriod]] = Field(
        default=None,
        description="indicates a date period during which something may be used, applies, is valid or relevant",
    )  # uri: https://model.onto2ai.com/schema/hasApplicablePeriod
    designates: Optional[List[PartyRole]] = Field(
        default=None,
        description="appoints someone officially",
    )  # uri: https://model.onto2ai.com/schema/designates
    is_designated_by: Optional[List[PartyRole]] = Field(
        default=None,
        description="indicates the role of the party that has assigned or appointed someone",
    )  # uri: https://model.onto2ai.com/schema/isDesignatedBy
    has_related_party_role: Optional[List[PartyRole]] = Field(
        default=None,
        description="relates a party acting in a specific role directly to another party role",
    )  # uri: https://model.onto2ai.com/schema/hasRelatedPartyRole
    elects: Optional[List[PartyRole]] = Field(
        default=None,
        description="chooses someone to hold office or position",
    )  # uri: https://model.onto2ai.com/schema/elects
    nominates: Optional[List[PartyRole]] = Field(
        default=None,
        description="appoints or proposes for appointment",
    )  # uri: https://model.onto2ai.com/schema/nominates
    is_object_role_in: Optional[List[Situation]] = Field(
        default=None,
        description="indicates a situation in which the role is secondary",
    )  # uri: https://model.onto2ai.com/schema/isObjectRoleIn
    is_subject_role_in: Optional[List[Situation]] = Field(
        default=None,
        description="indicates a situation in which the role is the primary topic",
    )  # uri: https://model.onto2ai.com/schema/isSubjectRoleIn


class TaxIdentificationScheme(BaseModel):
    """skos:definition: identification scheme used to identify taxpayers in some jurisdiction"""

    model_config = ConfigDict(extra="forbid")

    is_applicable_in: Optional[List[Jurisdiction]] = Field(
        default=None,
        description="indicates a context in which something is relevant",
    )  # uri: https://model.onto2ai.com/schema/isApplicableIn


class Jurisdiction(BaseModel):
    """skos:definition: context, typically a defined territory or legal domain, within which some legal authority, rules, regulations, or official powers apply"""

    model_config = ConfigDict(extra="forbid")


class FilingStatusConcept(BaseModel):
    """skos:definition: tax filing status category used to determine how a party files (e.g., single, married filing jointly)"""

    model_config = ConfigDict(extra="forbid")

    has_filing_status_value: Optional[FilingStatus] = Field(
        default=None,
        description="links filing status concept to an enum value",
    )  # uri: https://model.onto2ai.com/schema/hasFilingStatusValue


class ReportStatusConcept(BaseModel):
    """skos:definition: lifecycle or processing state of a report (e.g., draft, submitted, accepted, rejected)"""

    model_config = ConfigDict(extra="forbid")

    has_report_status_value: Optional[ReportStatus] = Field(
        default=None,
        description="links report status concept to an enum value",
    )  # uri: https://model.onto2ai.com/schema/hasReportStatusValue


class Role(BaseModel):
    """skos:definition: abstract characterization of a part played by some entity in a particular context or situation"""

    model_config = ConfigDict(extra="forbid")


class ContextualName(BaseModel):
    """skos:definition: name that is used to identify something within a particular context"""

    model_config = ConfigDict(extra="forbid")


class OrganizationName(BaseModel):
    """skos:definition: name used to identify an organization"""

    model_config = ConfigDict(extra="forbid")


class PhysicalAddress(BaseModel):
    """skos:definition: address at which an entity may be physically located or contacted, or at which it may receive correspondence"""

    model_config = ConfigDict(extra="forbid")


class ConventionalStreetAddress(BaseModel):
    """skos:definition: street address expressed using conventional addressing components suitable for postal or official use"""

    model_config = ConfigDict(extra="forbid")


class LegalCapacity(BaseModel):
    """skos:definition: ability, rights, or authority to perform certain actions or to have certain rights or obligations under law"""

    model_config = ConfigDict(extra="forbid")


class Duty(BaseModel):
    """skos:definition: commitment or obligation that an independent party has"""

    model_config = ConfigDict(extra="forbid")


class IdentificationScheme(BaseModel):
    """skos:definition: set of rules and policies that govern how identifiers are assigned and structured within a context"""

    model_config = ConfigDict(extra="forbid")


class LegalEntityIdentifier(BaseModel):
    """skos:definition: identifier that uniquely identifies a legal entity within some context"""

    model_config = ConfigDict(extra="forbid")


class EntityOwnership(BaseModel):
    """skos:definition: context describing ownership interest of one entity in another"""

    model_config = ConfigDict(extra="forbid")


class Person(BaseModel):
    """skos:definition: human individual"""

    model_config = ConfigDict(extra="forbid")


class GeopoliticalEntity(BaseModel):
    """skos:definition: political or administrative entity such as a country, state, province, or municipality"""

    model_config = ConfigDict(extra="forbid")


class StandardIndustrialClassificationCode(BaseModel):
    """skos:definition: code from the Standard Industrial Classification system used to classify organizations by industry"""

    model_config = ConfigDict(extra="forbid")


class NorthAmericanIndustryClassificationSystemCode(BaseModel):
    """skos:definition: code from the North American Industry Classification System used to classify organizations by industry"""

    model_config = ConfigDict(extra="forbid")


class Goal(BaseModel):
    """skos:definition: long-term desired outcome or objective"""

    model_config = ConfigDict(extra="forbid")


class Organization(BaseModel):
    """skos:definition: social or legal entity that is organized for a purpose"""

    model_config = ConfigDict(extra="forbid")


class OrganizationalSubUnit(BaseModel):
    """skos:definition: part of an organization that functions as a subdivision or unit"""

    model_config = ConfigDict(extra="forbid")


class ServiceProvider(BaseModel):
    """skos:definition: party that makes a service available or provisions it"""

    model_config = ConfigDict(extra="forbid")


class Capability(BaseModel):
    """skos:definition: ability or capacity made available by a service or provided by an organization"""

    model_config = ConfigDict(extra="forbid")


class Site(BaseModel):
    """skos:definition: place or location at which something is situated"""

    model_config = ConfigDict(extra="forbid")


class Licensor(BaseModel):
    """skos:definition: party responsible for issuing or granting a license"""

    model_config = ConfigDict(extra="forbid")


class Licensee(BaseModel):
    """skos:definition: party role of a party that is granted a license"""

    model_config = ConfigDict(extra="forbid")


class AuthorisingParty(BaseModel):
    """skos:definition: party (role) that endorses, enables, empowers, or gives permission in an authorization situation"""

    model_config = ConfigDict(extra="forbid")


class Actor(BaseModel):
    """skos:definition: primary party acting in a specific role with respect to a given situation"""

    model_config = ConfigDict(extra="forbid")


class Undergoer(BaseModel):
    """skos:definition: experiencer, passive participant, or other object role in a given situation"""

    model_config = ConfigDict(extra="forbid")


Agent.model_rebuild()
Party.model_rebuild()
LegalPerson.model_rebuild()
FormalOrganisation.model_rebuild()
DatePeriod.model_rebuild()
Service.model_rebuild()
Report.model_rebuild()
Facility.model_rebuild()
TaxIdentifier.model_rebuild()
Submitter.model_rebuild()
ReportingParty.model_rebuild()
PartyRole.model_rebuild()
Situation.model_rebuild()
Authorization.model_rebuild()
AuthorisedParty.model_rebuild()
RegulatoryAgency.model_rebuild()
RegulatoryService.model_rebuild()
GovernmentIssuedLicense.model_rebuild()
TaxAuthority.model_rebuild()
TaxIdentificationScheme.model_rebuild()
Jurisdiction.model_rebuild()
FilingStatusConcept.model_rebuild()
ReportStatusConcept.model_rebuild()
Role.model_rebuild()
ContextualName.model_rebuild()
OrganizationName.model_rebuild()
PhysicalAddress.model_rebuild()
ConventionalStreetAddress.model_rebuild()
LegalCapacity.model_rebuild()
Duty.model_rebuild()
IdentificationScheme.model_rebuild()
LegalEntityIdentifier.model_rebuild()
EntityOwnership.model_rebuild()
Person.model_rebuild()
GeopoliticalEntity.model_rebuild()
StandardIndustrialClassificationCode.model_rebuild()
NorthAmericanIndustryClassificationSystemCode.model_rebuild()
Goal.model_rebuild()
Organization.model_rebuild()
OrganizationalSubUnit.model_rebuild()
ServiceProvider.model_rebuild()
Capability.model_rebuild()
Site.model_rebuild()
Licensor.model_rebuild()
Licensee.model_rebuild()
AuthorisingParty.model_rebuild()
Actor.model_rebuild()
Undergoer.model_rebuild()
