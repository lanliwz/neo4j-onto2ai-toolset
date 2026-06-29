from __future__ import annotations

from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class CountryEnum(str, Enum):
    """Supported country enum values for the staged parcel-address slice."""

    UNITED_STATES_OF_AMERICA = "United States of America (the)"
    CANADA = "Canada (le)"


class USStateEnum(str, Enum):
    """ISO 3166-2 style U.S. state selections for country subdivision."""

    AL = "AL"
    AK = "AK"
    AZ = "AZ"
    AR = "AR"
    CA = "CA"
    CO = "CO"
    CT = "CT"
    DE = "DE"
    FL = "FL"
    GA = "GA"
    HI = "HI"
    ID = "ID"
    IL = "IL"
    IN = "IN"
    IA = "IA"
    KS = "KS"
    KY = "KY"
    LA = "LA"
    ME = "ME"
    MD = "MD"
    MA = "MA"
    MI = "MI"
    MN = "MN"
    MS = "MS"
    MO = "MO"
    MT = "MT"
    NE = "NE"
    NV = "NV"
    NH = "NH"
    NJ = "NJ"
    NM = "NM"
    NY = "NY"
    NC = "NC"
    ND = "ND"
    OH = "OH"
    OK = "OK"
    OR = "OR"
    PA = "PA"
    RI = "RI"
    SC = "SC"
    SD = "SD"
    TN = "TN"
    TX = "TX"
    UT = "UT"
    VT = "VT"
    VA = "VA"
    WA = "WA"
    WV = "WV"
    WI = "WI"
    WY = "WY"


class GPSCoordinate(BaseModel):
    """Base geospatial coordinate used for parcel geometry and boundary vertices."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    gps_coordinate_id: str = Field(
        alias="gpsCoordinateId",
        description="Stable identifier for a GPS coordinate node.",
    )
    latitude: Decimal = Field(
        alias="latitude",
        description="Latitude component of the coordinate.",
    )
    longitude: Decimal = Field(
        alias="longitude",
        description="Longitude component of the coordinate.",
    )


class BoundaryVertex(GPSCoordinate):
    """Ordered boundary point belonging to a polygon geometry."""

    vertex_sequence_number: int = Field(
        alias="vertexSequenceNumber",
        description="Sequence number of the boundary vertex within the polygon.",
    )


class USPostalAddress(BaseModel):
    """Cleaned staged US postal address schema."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    address_id: str = Field(
        alias="addressId",
        description="Stable identifier for a parcel postal address resource.",
    )
    street_address_line1: str = Field(
        alias="streetAddressLine1",
        description="Primary street address line associated with the parcel or mailing address.",
    )
    address_line2: Optional[str] = Field(
        default=None,
        alias="addressLine2",
        description="Optional second line for apartment, suite, unit, floor, or similar detail.",
    )
    city_name: str = Field(
        alias="cityName",
        description="City, town, or municipality name captured for the address.",
    )
    has_subdivision: USStateEnum = Field(
        alias="hasSubdivision",
        description="U.S. state selected from the staged country subdivision enum.",
    )
    postal_code: str = Field(
        alias="postalCode",
        pattern=r"^\d{5}(?:-\d{4})?$",
        description="US ZIP code in five-digit or ZIP+4 format.",
    )
    has_country: CountryEnum = Field(
        default=CountryEnum.UNITED_STATES_OF_AMERICA,
        alias="hasCountry",
        description="Country selected from the staged country enum. Defaults to United States.",
    )


class Geometry(BaseModel):
    """Base geometry resource in the parcel slice."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    geometry_id: str = Field(
        alias="geometryId",
        description="Stable identifier for a geometry resource.",
    )


class PolygonGeometry(Geometry):
    """Polygon geometry describing the parcel boundary."""

    coordinate_sequence_text: Optional[str] = Field(
        default=None,
        alias="coordinateSequenceText",
        description="Serialized coordinate sequence for the polygon geometry.",
    )
    has_boundary_vertex: List[BoundaryVertex] = Field(
        default_factory=list,
        alias="hasBoundaryVertex",
        description="Ordered boundary vertices that define the polygon geometry.",
    )


class Parcel(BaseModel):
    """Parcel core record linked to address and geometry."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    parcel_id: str = Field(
        alias="parcelId",
        description="Stable identifier for a parcel record.",
    )
    parcel_identifier: Optional[str] = Field(
        default=None,
        alias="parcelIdentifier",
        description="Human-readable parcel identifier or external parcel code.",
    )
    district_code: Optional[str] = Field(
        default=None,
        alias="districtCode",
        description="District code assigned to the parcel in the source parcel dataset.",
    )
    section_code: Optional[str] = Field(
        default=None,
        alias="sectionCode",
        description="Section code assigned to the parcel in the source parcel dataset.",
    )
    block_code: Optional[str] = Field(
        default=None,
        alias="blockCode",
        description="Block code assigned to the parcel in the source parcel dataset.",
    )
    lot_code: Optional[str] = Field(
        default=None,
        alias="lotCode",
        description="Lot code assigned to the parcel in the source parcel dataset.",
    )
    municipality_name: Optional[str] = Field(
        default=None,
        alias="municipalityName",
        description="Municipality or locality name associated with the parcel in the source dataset.",
    )
    parcel_postal_code: Optional[str] = Field(
        default=None,
        alias="parcelPostalCode",
        description="Postal ZIP code carried directly on the parcel record by the source dataset.",
    )
    full_address_text: Optional[str] = Field(
        default=None,
        alias="fullAddressText",
        description="Source-system full parcel address text.",
    )
    parcel_area_acres: Optional[Decimal] = Field(
        default=None,
        alias="parcelAreaAcres",
        description="Parcel area expressed in acres as reported by the source parcel dataset.",
    )
    land_use_text: Optional[str] = Field(
        default=None,
        alias="landUseText",
        description="Land-use code and description string assigned to the parcel in the source dataset.",
    )
    last_update_text: Optional[str] = Field(
        default=None,
        alias="lastUpdateText",
        description="Last-update text value carried by the source parcel dataset.",
    )
    create_date_text: Optional[str] = Field(
        default=None,
        alias="createDateText",
        description="Source create-date text value associated with the parcel record.",
    )
    title_flag_text: Optional[str] = Field(
        default=None,
        alias="titleFlagText",
        description="Source text flag indicating whether the parcel record is title-related.",
    )
    parcel_status_text: Optional[str] = Field(
        default=None,
        alias="parcelStatusText",
        description="Status string assigned to the parcel in the source dataset.",
    )
    overlap_flag_text: Optional[str] = Field(
        default=None,
        alias="overlapFlagText",
        description="Source text flag indicating whether the parcel overlaps another mapped area.",
    )
    recorded_deed_acres: Optional[Decimal] = Field(
        default=None,
        alias="recordedDeedAcres",
        description="Recorded deed area of the parcel expressed in acres.",
    )
    has_parcel_address: List[USPostalAddress] = Field(
        default_factory=list,
        alias="hasParcelAddress",
        description="Postal addresses associated with the parcel record.",
    )
    has_parcel_geometry: List[PolygonGeometry] = Field(
        default_factory=list,
        alias="hasParcelGeometry",
        description="Polygon geometries associated with the parcel.",
    )


class GeoJSONFeature(BaseModel):
    """GeoJSON feature that represents a parcel."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    feature_id: str = Field(
        alias="featureId",
        description="Stable identifier for a GeoJSON feature.",
    )
    geometry_type_name: Optional[str] = Field(
        default=None,
        alias="geometryTypeName",
        description="GeoJSON geometry type name, such as Polygon.",
    )
    source_object_id: Optional[str] = Field(
        default=None,
        alias="sourceObjectId",
        description="Source-system object identifier for the feature.",
    )
    represents_parcel: List[Parcel] = Field(
        default_factory=list,
        alias="representsParcel",
        description="Parcel represented by this GeoJSON feature.",
    )


class GeoJSONFeatureCollection(BaseModel):
    """GeoJSON feature collection grouping parcel features."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    feature_collection_id: str = Field(
        alias="featureCollectionId",
        description="Stable identifier for a GeoJSON feature collection.",
    )
    has_feature: List[GeoJSONFeature] = Field(
        default_factory=list,
        alias="hasFeature",
        description="GeoJSON features contained in the collection.",
    )
