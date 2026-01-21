from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List

class Person(BaseModel):
    """individual human being, with consciousness of self
    Ontology: https://spec.edmcouncil.org/fibo/ontology/FND/AgentsAndPeople/People/Person
    """

    hasGender: str = Field(..., description="links a particular gender value with a person. URI: https://spec.edmcouncil.org/fibo/ontology/FND/AgentsAndPeople/People/hasGender")
    hasGivenName: Optional[str] = Field(None, description="First Name. URI: https://spec.edmcouncil.org/fibo/ontology/FND/AgentsAndPeople/People/hasGivenName")
    hasSurname: Optional[str] = Field(None, description="Last Name. URI: https://spec.edmcouncil.org/fibo/ontology/FND/AgentsAndPeople/People/hasSurname")
    hasMiddleNameOrInitial: Optional[str] = Field(None, description="Middle Name. URI: https://spec.edmcouncil.org/fibo/ontology/FND/AgentsAndPeople/People/hasMiddleNameOrInitial")
    hasDateOfBirth: date = Field(..., description="Date on which individual was born. URI: https://spec.edmcouncil.org/fibo/ontology/FND/AgentsAndPeople/People/hasDateOfBirth")
    hasPlaceOfBirth: Optional[str] = Field(None, description="Location where individual was born. URI: https://spec.edmcouncil.org/fibo/ontology/FND/AgentsAndPeople/People/hasPlaceOfBirth")
    hasCitizenship: Optional[List[str]] = Field(None, description="Country of citizenship. URI: https://spec.edmcouncil.org/fibo/ontology/FND/AgentsAndPeople/People/hasCitizenship")
    hasResidence: Optional[List[str]] = Field(None, description="Dwelling where individual lives. URI: https://spec.edmcouncil.org/fibo/ontology/FND/AgentsAndPeople/People/hasResidence")
    hasTextualName: Optional[List[str]] = Field(None, description="Appellation with individual concept. URI: https://www.omg.org/spec/Commons/Designators/hasTextualName")

    class Config:
        json_schema_extra = {
            "example": {
                "hasGender": "Female",
                "hasGivenName": "Jane",
                "hasSurname": "Doe",
                "hasDateOfBirth": "1990-01-01",
                "hasPlaceOfBirth": "London"
            }
        }