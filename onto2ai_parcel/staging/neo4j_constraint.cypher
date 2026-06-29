// ===========================================================
// NEO4J SCHEMA CONSTRAINTS (Source: stagingdb / parcel slice)
// Generated to enforce structural integrity for the staged parcel Pydantic model.
// ===========================================================

// Class: US postal address
// Definition: A United States civic mailing or site address associated with a parcel record, including street, city, postal code, subdivision, and country information.
// URI: http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#USPostalAddress
// Mandatory property: addressId
CREATE CONSTRAINT USPostalAddress_addressId_Required IF NOT EXISTS FOR (n:`USPostalAddress`) REQUIRE n.`addressId` IS NOT NULL;

// Class: US postal address
// Definition: A United States civic mailing or site address associated with a parcel record, including street, city, postal code, subdivision, and country information.
// URI: http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#USPostalAddress
// Mandatory property: streetAddressLine1
CREATE CONSTRAINT USPostalAddress_streetAddressLine1_Required IF NOT EXISTS FOR (n:`USPostalAddress`) REQUIRE n.`streetAddressLine1` IS NOT NULL;

// Class: US postal address
// Definition: A United States civic mailing or site address associated with a parcel record, including street, city, postal code, subdivision, and country information.
// URI: http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#USPostalAddress
// Mandatory property: cityName
CREATE CONSTRAINT USPostalAddress_cityName_Required IF NOT EXISTS FOR (n:`USPostalAddress`) REQUIRE n.`cityName` IS NOT NULL;

// Class: US postal address
// Definition: A United States civic mailing or site address associated with a parcel record, including street, city, postal code, subdivision, and country information.
// URI: http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#USPostalAddress
// Mandatory property: postalCode
CREATE CONSTRAINT USPostalAddress_postalCode_Required IF NOT EXISTS FOR (n:`USPostalAddress`) REQUIRE n.`postalCode` IS NOT NULL;

// Class: GPS coordinate
// Definition: Base geospatial coordinate used for parcel geometry and boundary vertices.
// URI: http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#GPSCoordinate
// Mandatory property: gpsCoordinateId
CREATE CONSTRAINT GPSCoordinate_gpsCoordinateId_Required IF NOT EXISTS FOR (n:`GPSCoordinate`) REQUIRE n.`gpsCoordinateId` IS NOT NULL;

// Class: geometry
// Definition: Base geometry resource in the parcel slice.
// URI: http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#Geometry
// Mandatory property: geometryId
CREATE CONSTRAINT Geometry_geometryId_Required IF NOT EXISTS FOR (n:`Geometry`) REQUIRE n.`geometryId` IS NOT NULL;

// Class: parcel
// Definition: Parcel core record linked to address and geometry.
// URI: http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#Parcel
// Mandatory property: parcelId
CREATE CONSTRAINT Parcel_parcelId_Required IF NOT EXISTS FOR (n:`Parcel`) REQUIRE n.`parcelId` IS NOT NULL;

// Class: GeoJSON feature
// Definition: GeoJSON feature that represents a parcel.
// URI: http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#GeoJSONFeature
// Mandatory property: featureId
CREATE CONSTRAINT GeoJSONFeature_featureId_Required IF NOT EXISTS FOR (n:`GeoJSONFeature`) REQUIRE n.`featureId` IS NOT NULL;

// Class: GeoJSON feature collection
// Definition: GeoJSON feature collection grouping parcel features.
// URI: http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#GeoJSONFeatureCollection
// Mandatory property: featureCollectionId
CREATE CONSTRAINT GeoJSONFeatureCollection_featureCollectionId_Required IF NOT EXISTS FOR (n:`GeoJSONFeatureCollection`) REQUIRE n.`featureCollectionId` IS NOT NULL;
