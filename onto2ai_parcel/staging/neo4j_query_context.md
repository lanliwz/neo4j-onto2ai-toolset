# Neo4j Schema Prompt

## Section 1: Node Labels

| Label | Type | URI | Definition |
| --- | --- | --- | --- |
| Parcel | owl__Class | http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#Parcel | Parcel core record linked to address and geometry. |
| Address | owl__Class | http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#Address | A general address resource associated with a parcel. |
| USPostalAddress:Address | owl__Class | http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#USPostalAddress | A United States civic mailing or site address associated with a parcel record, including street, city, postal code, subdivision, and country information. |
| Geometry | owl__Class | http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#Geometry | Base geometry resource in the parcel slice. |
| PolygonGeometry:Geometry | owl__Class | http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#PolygonGeometry | Polygon geometry describing the parcel boundary. |
| GPSCoordinate | owl__Class | http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#GPSCoordinate | Base geospatial coordinate used for parcel geometry and boundary vertices. |
| BoundaryVertex:GPSCoordinate | owl__Class | http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#BoundaryVertex | Ordered boundary point belonging to a polygon geometry. |
| GeoJSONFeature | owl__Class | http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#GeoJSONFeature | GeoJSON feature that represents a parcel. |
| GeoJSONFeatureCollection | owl__Class | http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#GeoJSONFeatureCollection | GeoJSON feature collection grouping parcel features. |
| Country | owl__Class | http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#Country | A sovereign country used as an enumerated reference value for parcel addresses. |
| CountrySubdivision | owl__Class | http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#CountrySubdivision | A state, province, territory, or similar first-level administrative subdivision used as an enumerated reference value for parcel addresses. |
| UnitedStatesOfAmerica | owl__NamedIndividual | https://www.omg.org/spec/LCC/Countries/ISO3166-1-CountryCodes/UnitedStatesOfAmerica | The sovereign country commonly referred to as the United States. |
| Canada | owl__NamedIndividual | https://www.omg.org/spec/LCC/Countries/ISO3166-1-CountryCodes/Canada | The sovereign country commonly referred to as Canada. |
| USState | owl__NamedIndividual | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-XX | A U.S. state enumerated as a country subdivision using an ISO 3166-2 code. |

## Section 2: Relationship Types

| Relationship | URI | Definition | Cardinality |
| --- | --- | --- | --- |
| hasParcelAddress | http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#hasParcelAddress | Relates a parcel to the postal address carried by the parcel record. | 0..* |
| hasParcelGeometry | http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#hasParcelGeometry | Relates a parcel to polygon geometry describing its mapped boundary. | 0..* |
| hasSubdivision | http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#hasSubdivision | Relates a parcel postal address to the state or other first-level subdivision used for the address. | 1..1 |
| hasCountry | http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#hasCountry | Relates a parcel postal address to the sovereign country used for the address. | 1..1 |
| hasBoundaryVertex | http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#hasBoundaryVertex | Relates polygon geometry to its ordered boundary vertices. | 0..* |
| representsParcel | http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#representsParcel | Relates a GeoJSON feature to the parcel it represents. | 0..* |
| hasFeature | http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#hasFeature | Relates a feature collection to the GeoJSON features it contains. | 0..* |

## Section 3: Node Properties

| Node Label | Property | Data Type | Mandatory |
| --- | --- | --- | --- |
| Address | addressId | string | Yes |
| USPostalAddress:Address | streetAddressLine1 | xsd:string | Yes |
| USPostalAddress:Address | addressLine2 | xsd:string | No |
| USPostalAddress:Address | cityName | xsd:string | Yes |
| USPostalAddress:Address | subdivision | string | Yes |
| USPostalAddress:Address | postalCode | xsd:string | Yes |
| USPostalAddress:Address | country | string | Yes |
| Geometry | geometryId | string | Yes |
| PolygonGeometry:Geometry | coordinateSequenceText | xsd:string | No |
| GPSCoordinate | gpsCoordinateId | string | Yes |
| GPSCoordinate | latitude | xsd:decimal | No |
| GPSCoordinate | longitude | xsd:decimal | No |
| BoundaryVertex:GPSCoordinate | vertexSequenceNumber | xsd:integer | No |
| Parcel | parcelId | string | Yes |
| Parcel | parcelIdentifier | xsd:string | No |
| Parcel | fullAddressText | xsd:string | No |
| GeoJSONFeature | featureId | string | Yes |
| GeoJSONFeature | geometryTypeName | xsd:string | No |
| GeoJSONFeature | sourceObjectId | xsd:string | No |
| GeoJSONFeatureCollection | featureCollectionId | string | Yes |

## Section 4: Graph Topology

- `(:Parcel)-[:hasParcelAddress]->(:USPostalAddress:Address)`
- `(:Parcel)-[:hasParcelGeometry]->(:PolygonGeometry:Geometry)`
- `(:USPostalAddress:Address)-[:hasSubdivision]->(:CountrySubdivision)`
- `(:USPostalAddress:Address)-[:hasCountry]->(:Country)`
- `(:PolygonGeometry:Geometry)-[:hasBoundaryVertex]->(:BoundaryVertex:GPSCoordinate)`
- `(:GeoJSONFeature)-[:representsParcel]->(:Parcel)`
- `(:GeoJSONFeatureCollection)-[:hasFeature]->(:GeoJSONFeature)`

## Section 5: Enumeration Members

| Enum Class | Member Label | Member URI |
| --- | --- | --- |
| Country | United States of America (the) | https://www.omg.org/spec/LCC/Countries/ISO3166-1-CountryCodes/UnitedStatesOfAmerica |
| Country | Canada (le) | https://www.omg.org/spec/LCC/Countries/ISO3166-1-CountryCodes/Canada |
| CountrySubdivision | Alabama | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-AL |
| CountrySubdivision | Alaska | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-AK |
| CountrySubdivision | Arizona | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-AZ |
| CountrySubdivision | Arkansas | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-AR |
| CountrySubdivision | California | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-CA |
| CountrySubdivision | Colorado | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-CO |
| CountrySubdivision | Connecticut | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-CT |
| CountrySubdivision | Delaware | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-DE |
| CountrySubdivision | Florida | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-FL |
| CountrySubdivision | Georgia | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-GA |
| CountrySubdivision | Hawaii | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-HI |
| CountrySubdivision | Idaho | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-ID |
| CountrySubdivision | Illinois | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-IL |
| CountrySubdivision | Indiana | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-IN |
| CountrySubdivision | Iowa | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-IA |
| CountrySubdivision | Kansas | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-KS |
| CountrySubdivision | Kentucky | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-KY |
| CountrySubdivision | Louisiana | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-LA |
| CountrySubdivision | Maine | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-ME |
| CountrySubdivision | Maryland | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-MD |
| CountrySubdivision | Massachusetts | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-MA |
| CountrySubdivision | Michigan | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-MI |
| CountrySubdivision | Minnesota | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-MN |
| CountrySubdivision | Mississippi | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-MS |
| CountrySubdivision | Missouri | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-MO |
| CountrySubdivision | Montana | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-MT |
| CountrySubdivision | Nebraska | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-NE |
| CountrySubdivision | Nevada | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-NV |
| CountrySubdivision | New Hampshire | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-NH |
| CountrySubdivision | New Jersey | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-NJ |
| CountrySubdivision | New Mexico | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-NM |
| CountrySubdivision | New York | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-NY |
| CountrySubdivision | North Carolina | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-NC |
| CountrySubdivision | North Dakota | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-ND |
| CountrySubdivision | Ohio | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-OH |
| CountrySubdivision | Oklahoma | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-OK |
| CountrySubdivision | Oregon | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-OR |
| CountrySubdivision | Pennsylvania | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-PA |
| CountrySubdivision | Rhode Island | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-RI |
| CountrySubdivision | South Carolina | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-SC |
| CountrySubdivision | South Dakota | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-SD |
| CountrySubdivision | Tennessee | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-TN |
| CountrySubdivision | Texas | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-TX |
| CountrySubdivision | Utah | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-UT |
| CountrySubdivision | Vermont | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-VT |
| CountrySubdivision | Virginia | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-VA |
| CountrySubdivision | Washington | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-WA |
| CountrySubdivision | West Virginia | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-WV |
| CountrySubdivision | Wisconsin | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-WI |
| CountrySubdivision | Wyoming | https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-WY |
