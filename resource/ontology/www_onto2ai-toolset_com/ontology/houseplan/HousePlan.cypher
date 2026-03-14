// ===========================================================
// NEO4J SCHEMA CONSTRAINTS FOR HOUSE PLAN ONTOLOGY
// Companion constraints aligned with HousePlan.rdf
// ===========================================================

// Class: house plan
// Definition: A structured plan describing the layout, spaces, openings, and annotations for a residential building.
// URI: http://www.onto2ai-toolset.com/ontology/houseplan/HousePlan/#HousePlan
// Mandatory property: housePlanId
CREATE CONSTRAINT HousePlan_housePlanId_Required IF NOT EXISTS FOR (n:`HousePlan`) REQUIRE n.`housePlanId` IS NOT NULL;

// Class: building level
// Definition: A floor or split-level section within a house plan, such as a basement, main floor, or upper floor.
// URI: http://www.onto2ai-toolset.com/ontology/houseplan/HousePlan/#BuildingLevel
// Mandatory property: levelId
CREATE CONSTRAINT BuildingLevel_levelId_Required IF NOT EXISTS FOR (n:`BuildingLevel`) REQUIRE n.`levelId` IS NOT NULL;

// Class: space
// Definition: A bounded area within a building level that represents a functional portion of the floor plan.
// URI: http://www.onto2ai-toolset.com/ontology/houseplan/HousePlan/#Space
// Mandatory property: spaceId
CREATE CONSTRAINT Space_spaceId_Required IF NOT EXISTS FOR (n:`Space`) REQUIRE n.`spaceId` IS NOT NULL;

// Class: room
// Definition: A space intended for a specific residential use, such as sleeping, cooking, bathing, or working.
// URI: http://www.onto2ai-toolset.com/ontology/houseplan/HousePlan/#Room
// Mandatory property: spaceId
CREATE CONSTRAINT Room_spaceId_Required IF NOT EXISTS FOR (n:`Room`) REQUIRE n.`spaceId` IS NOT NULL;

// Class: wall
// Definition: A vertical building element that bounds, partitions, or encloses one or more spaces in a house plan.
// URI: http://www.onto2ai-toolset.com/ontology/houseplan/HousePlan/#Wall
// Mandatory property: wallId
CREATE CONSTRAINT Wall_wallId_Required IF NOT EXISTS FOR (n:`Wall`) REQUIRE n.`wallId` IS NOT NULL;

// Class: opening
// Definition: An opening formed in a wall to allow access, light, air, or visibility between spaces or to the exterior.
// URI: http://www.onto2ai-toolset.com/ontology/houseplan/HousePlan/#Opening
// Mandatory property: openingId
CREATE CONSTRAINT Opening_openingId_Required IF NOT EXISTS FOR (n:`Opening`) REQUIRE n.`openingId` IS NOT NULL;

// Class: door
// Definition: An operable opening primarily used to permit passage between spaces or between the building interior and exterior.
// URI: http://www.onto2ai-toolset.com/ontology/houseplan/HousePlan/#Door
// Mandatory property: openingId
CREATE CONSTRAINT Door_openingId_Required IF NOT EXISTS FOR (n:`Door`) REQUIRE n.`openingId` IS NOT NULL;

// Class: window
// Definition: An opening designed to admit daylight, ventilation, or views while remaining part of the building envelope.
// URI: http://www.onto2ai-toolset.com/ontology/houseplan/HousePlan/#Window
// Mandatory property: openingId
CREATE CONSTRAINT Window_openingId_Required IF NOT EXISTS FOR (n:`Window`) REQUIRE n.`openingId` IS NOT NULL;

// Class: fixture
// Definition: A built-in or planned element located within a space, such as cabinetry, plumbing fixtures, or appliances.
// URI: http://www.onto2ai-toolset.com/ontology/houseplan/HousePlan/#Fixture
// Mandatory property: fixtureId
CREATE CONSTRAINT Fixture_fixtureId_Required IF NOT EXISTS FOR (n:`Fixture`) REQUIRE n.`fixtureId` IS NOT NULL;

// Class: dimension annotation
// Definition: An annotation that records measured distances, sizes, or dimensional notes on a house plan.
// URI: http://www.onto2ai-toolset.com/ontology/houseplan/HousePlan/#DimensionAnnotation
// Mandatory property: dimensionAnnotationId
CREATE CONSTRAINT DimensionAnnotation_dimensionAnnotationId_Required IF NOT EXISTS FOR (n:`DimensionAnnotation`) REQUIRE n.`dimensionAnnotationId` IS NOT NULL;

// Class: material specification
// Definition: A specification describing an intended construction material or finish associated with a house plan element.
// URI: http://www.onto2ai-toolset.com/ontology/houseplan/HousePlan/#MaterialSpecification
// Mandatory property: materialSpecificationId
CREATE CONSTRAINT MaterialSpecification_materialSpecificationId_Required IF NOT EXISTS FOR (n:`MaterialSpecification`) REQUIRE n.`materialSpecificationId` IS NOT NULL;

// Class: address
// Definition: A structured location designator used to describe the civic location of a house plan site.
// URI: http://www.onto2ai-toolset.com/ontology/houseplan/HousePlan/#Address
// Mandatory property: addressId
CREATE CONSTRAINT Address_addressId_Required IF NOT EXISTS FOR (n:`Address`) REQUIRE n.`addressId` IS NOT NULL;

// Class: US postal address
// Definition: A United States civic mailing or site address including street, municipality, state, and postal code components.
// URI: http://www.onto2ai-toolset.com/ontology/houseplan/HousePlan/#USPostalAddress
// Mandatory property: addressId
CREATE CONSTRAINT USPostalAddress_addressId_Required IF NOT EXISTS FOR (n:`USPostalAddress`) REQUIRE n.`addressId` IS NOT NULL;

// Class: GPS coordinate
// Definition: A geospatial coordinate describing the latitude and longitude of a house plan site or surveyed point.
// URI: http://www.onto2ai-toolset.com/ontology/houseplan/HousePlan/#GPSCoordinate
// Mandatory property: gpsCoordinateId
CREATE CONSTRAINT GPSCoordinate_gpsCoordinateId_Required IF NOT EXISTS FOR (n:`GPSCoordinate`) REQUIRE n.`gpsCoordinateId` IS NOT NULL;

// Class: survey reference
// Definition: A survey record or legal reference describing parcel boundaries, lot designations, and site measurement context for a house plan.
// URI: http://www.onto2ai-toolset.com/ontology/houseplan/HousePlan/#SurveyReference
// Mandatory property: surveyReferenceId
CREATE CONSTRAINT SurveyReference_surveyReferenceId_Required IF NOT EXISTS FOR (n:`SurveyReference`) REQUIRE n.`surveyReferenceId` IS NOT NULL;

// Class: parcel
// Definition: A legally identified tract of land associated with a house plan site and referenced by address, survey, or tax records.
// URI: http://www.onto2ai-toolset.com/ontology/houseplan/HousePlan/#Parcel
// Mandatory property: parcelId
CREATE CONSTRAINT Parcel_parcelId_Required IF NOT EXISTS FOR (n:`Parcel`) REQUIRE n.`parcelId` IS NOT NULL;

// Class: GeoJSON feature collection
// Definition: A GeoJSON feature collection resource that groups one or more features from a source file.
// URI: http://www.onto2ai-toolset.com/ontology/houseplan/HousePlan/#GeoJSONFeatureCollection
// Mandatory property: featureCollectionId
CREATE CONSTRAINT GeoJSONFeatureCollection_featureCollectionId_Required IF NOT EXISTS FOR (n:`GeoJSONFeatureCollection`) REQUIRE n.`featureCollectionId` IS NOT NULL;

// Class: GeoJSON feature
// Definition: A GeoJSON feature that carries source properties and a geometry describing a mapped parcel or other site object.
// URI: http://www.onto2ai-toolset.com/ontology/houseplan/HousePlan/#GeoJSONFeature
// Mandatory property: featureId
CREATE CONSTRAINT GeoJSONFeature_featureId_Required IF NOT EXISTS FOR (n:`GeoJSONFeature`) REQUIRE n.`featureId` IS NOT NULL;

// Class: geometry
// Definition: A geometric representation of a mapped object, such as a point, line, or polygon.
// URI: http://www.onto2ai-toolset.com/ontology/houseplan/HousePlan/#Geometry
// Mandatory property: geometryId
CREATE CONSTRAINT Geometry_geometryId_Required IF NOT EXISTS FOR (n:`Geometry`) REQUIRE n.`geometryId` IS NOT NULL;

// Class: polygon geometry
// Definition: A closed polygon geometry used to represent an areal boundary, such as a tax parcel footprint.
// URI: http://www.onto2ai-toolset.com/ontology/houseplan/HousePlan/#PolygonGeometry
// Mandatory property: geometryId
CREATE CONSTRAINT PolygonGeometry_geometryId_Required IF NOT EXISTS FOR (n:`PolygonGeometry`) REQUIRE n.`geometryId` IS NOT NULL;

// Class: boundary vertex
// Definition: A GPS coordinate used as an ordered vertex in a polygon boundary.
// URI: http://www.onto2ai-toolset.com/ontology/houseplan/HousePlan/#BoundaryVertex
// Mandatory property: gpsCoordinateId
CREATE CONSTRAINT BoundaryVertex_gpsCoordinateId_Required IF NOT EXISTS FOR (n:`BoundaryVertex`) REQUIRE n.`gpsCoordinateId` IS NOT NULL;

// Class: room classification
// Definition: An enumeration of common residential room types used to classify rooms in a house plan.
// URI: http://www.onto2ai-toolset.com/ontology/houseplan/HousePlan/#RoomClassification
