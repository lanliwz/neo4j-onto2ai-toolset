from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List

class Account(BaseModel):
    """
    container for records associated with a business arrangement for regular transactions and services
    Ontology: https://spec.edmcouncil.org/fibo/ontology/FBC/ProductsAndServices/ClientsAndAccounts/Account
    """

    hasBalance: Optional[float] = Field(None, description="Net amount of money available. URI: https://spec.edmcouncil.org/fibo/ontology/FBC/ProductsAndServices/ClientsAndAccounts/hasBalance")
    hasOpenDate: Optional[date] = Field(None, description="Date the account was created. URI: https://spec.edmcouncil.org/fibo/ontology/FBC/ProductsAndServices/ClientsAndAccounts/hasOpenDate")
    hasCloseDate: Optional[date] = Field(None, description="Date the account was closed. URI: https://spec.edmcouncil.org/fibo/ontology/FBC/ProductsAndServices/ClientsAndAccounts/hasCloseDate")
    isIdentifiedBy: Optional[str] = Field(None, description="Account Identifier. URI: https://www.omg.org/spec/Commons/Identifiers/isIdentifiedBy")
    isHeldBy: Optional[str] = Field(None, description="Account Holder. URI: https://spec.edmcouncil.org/fibo/ontology/FND/Relations/Relations/isHeldBy")
    isProvidedBy: Optional[str] = Field(None, description="Account Provider. URI: https://www.omg.org/spec/Commons/Organizations/isProvidedBy")

    class Config:
        json_schema_extra = {
            "example": {
                "hasBalance": 1500.50,
                "hasOpenDate": "2023-01-15",
                "isIdentifiedBy": "ACCT-123456",
                "isHeldBy": "Jane Doe"
            }
        }
