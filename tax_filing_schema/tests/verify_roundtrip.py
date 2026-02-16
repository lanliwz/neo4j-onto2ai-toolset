import os
import sys
from decimal import Decimal
from datetime import date
from pydantic import BaseModel

# Add 'code' directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'code'))

# Import models and bridge
from models import Form1040_2025, MonetaryAmount, Person, ReportStatus, Currency, FilingStatus
from bridge import PydanticNeo4jBridge

class MockDB:
    """Mock database to simulate execution and capture queries."""
    def __init__(self):
        self.queries = []
        
    def execute_cypher(self, query, params=None, name=None):
        print(f"\n[QUERY: {name}]")
        print(query)
        if params:
            print(f"PARAMS: {params}")
        
        # Return a mock node id for the bridge
        self.queries.append({"query": query, "params": params})
        return [{"node_id": 1, "target_id": 2}]

def test_pydantic_to_neo4j_consistency():
    print("=== Testing Pydantic to Neo4j Param Mapping ===")
    
    # 1. Create a complex model
    taxpayer = Person(
        personName="Alice Smith",
        ssn="999-00-1111",
        fullAddress="123 Main St, Anytown, USA",
        dateOfBirth=date(1985, 5, 12)
    )
    
    monetary_income = MonetaryAmount(amount=Decimal("75000.00"), currency=Currency.USD)
    
    form = Form1040_2025(
        taxYear=2025,
        hasReportStatus=ReportStatus.DRAFT,
        taxableIncome=monetary_income,
        filingStatus=FilingStatus.SINGLE
    )
    
    # 2. Check bridge mapping
    print("\nMapping Form1040_2025 to Neo4j Params...")
    params = PydanticNeo4jBridge.to_neo4j_params(form)
    
    print("\nProperties (Datatype Properties):")
    for k, v in params["properties"].items():
        print(f"  {k}: {v} (type: {type(v).__name__})")
        
    print("\nRelationships (Object Properties):")
    for rel in params["relationships"]:
        print(f"  [:{rel['type']}] -> (:{rel['target_label']})")
        
    # Assertions
    assert params["properties"]["hasTaxYear"] == 2025
    assert params["properties"]["hasReportStatus"] == "Draft"
    assert any(rel["type"] == "hasTaxableIncome" for rel in params["relationships"])
    
    print("\nSUCCESS: Pydantic to Neo4j mapping is consistent with schema aliases.")

def test_full_loading_simulation():
    print("\n=== Testing Full Loading Simulation ===")
    db = MockDB()
    
    taxpayer = Person(
        uri="https://example.org/people/alice",
        personName="Alice Smith",
        ssn="999-00-1111"
    )
    
    income = MonetaryAmount(
        uri="https://example.org/amounts/income_2025",
        amount=Decimal("75000.00"),
        currency=Currency.USD
    )
    
    form = Form1040_2025(
        uri="https://example.org/filings/form1040_2025_alice",
        taxYear=2025,
        taxableIncome=income
    )
    
    print("\nLoading complex model into Mock Neo4j...")
    PydanticNeo4jBridge.load_model_to_neo4j(db, form)
    
    print("\nSimulation complete. Review the queries above for schema alignment.")

if __name__ == "__main__":
    try:
        test_pydantic_to_neo4j_consistency()
        test_full_loading_simulation()
        print("\n=== ALL TESTS PASSED ===")
    except Exception as e:
        print(f"\nFAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
