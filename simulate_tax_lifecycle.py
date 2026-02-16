import os
import sys
from decimal import Decimal
from datetime import date
from neo4j import GraphDatabase

# Ensure we can import from the tax_filing_schema/code directory
SCHEMA_CODE_PATH = "/Users/weizhang/github/neo4j-onto2ai-toolset/tax_filing_schema/code"
if SCHEMA_CODE_PATH not in sys.path:
    sys.path.append(SCHEMA_CODE_PATH)

from models import Form1040_2025, MonetaryAmount, Person, ReportStatus, Currency, FilingStatus
from bridge import PydanticNeo4jBridge

# Production Database Config from Environment
# We try to use the standard project env vars if possible
from dotenv import load_dotenv
load_dotenv()

URI = os.getenv("NEO4J_MODEL_DB_URL", "bolt://localhost:7687")
USER = os.getenv("NEO4J_MODEL_DB_USERNAME", "neo4j")
PASSWORD = os.getenv("NEO4J_MODEL_DB_PASSWORD", "password")
DATABASE = "tax2025" # Explicitly target the new simulation DB

class Neo4jWrapper:
    def __init__(self):
        self._driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
        
    def close(self):
        self._driver.close()
        
    def execute_cypher(self, query, params=None, name=None):
        with self._driver.session(database=DATABASE) as session:
            result = session.run(query, params or {})
            return [record.data() for record in result]

def run_simulation():
    db = Neo4jWrapper()
    print(f"🚀 Starting Tax Filing Lifecycle Simulation on database: {DATABASE}")

    try:
        # --- PHASE 1: INITIAL DRAFT ---
        print("\n[PHASE 1] Creating initial Draft 1040 filing...")
        
        alice = Person(
            uri="https://example.org/people/alice_smith",
            personName="Alice Smith",
            ssn="999-00-1111",
            dateOfBirth=date(1985, 5, 12),
            birthPlace="New York, NY"
        )
        
        form = Form1040_2025(
            uri="https://example.org/filings/2025/alice_smith_1040",
            taxYear=2025,
            hasReportStatus=ReportStatus.DRAFT,
            filingStatus=FilingStatus.SINGLE
        )
        # Link taxpayer to form (Conceptual link, bridge handles per-class)
        # For simplicity in this bridge version, we load them sequentially
        
        PydanticNeo4jBridge.load_model_to_neo4j(db, alice)
        PydanticNeo4jBridge.load_model_to_neo4j(db, form)
        
        # Connect Person to Form via isSubmittedBy (Manual link for now as models are top-level)
        db.execute_cypher(
            "MATCH (a:Person {ssn: $ssn}), (f:Form1040_2025 {uri: $f_uri}) "
            "MERGE (f)-[:isSubmittedBy]->(a)",
            params={"ssn": "999-00-1111", "f_uri": form.uri},
            name="link_taxpayer_to_form"
        )
        print("✅ Draft created and linked to taxpayer.")

        # --- PHASE 2: POPULATE INCOME ---
        print("\n[PHASE 2] Populating income data...")
        income = MonetaryAmount(
            uri="https://example.org/amounts/alice_2025_wages",
            amount=Decimal("85400.00"),
            currency=Currency.USD
        )
        
        # Add income to model and reload (Bridge handles MERGE)
        form.taxableIncome = income
        PydanticNeo4jBridge.load_model_to_neo4j(db, form)
        print(f"✅ Income of ${income.amount} added to filing.")

        # --- PHASE 3: SUBMISSION ---
        print("\n[PHASE 3] Finalizing and Submitting...")
        
        # Update status
        form.hasReportStatus = ReportStatus.SUBMITTED
        PydanticNeo4jBridge.load_model_to_neo4j(db, form)
        
        print("✅ Filing set to SUBMITTED state.")

        # --- VERIFICATION ---
        print("\n[VERIFICATION] Querying database state...")
        # Note: We must use the ontological aliases (has*) stored in Neo4j
        res = db.execute_cypher(
            "MATCH (f:Form1040_2025)-[:hasReportStatus]->(s) "
            "MATCH (f)-[:isSubmittedBy]->(p:Person) "
            "MATCH (f)-[:hasTaxableIncome]->(i:MonetaryAmount) "
            "RETURN f.hasTaxYear as Year, s.rdfs__label as Status, p.hasName as Taxpayer, i.hasAmount as Income"
        )
        
        if res:
            row = res[0]
            print(f"--- DATABASE RECORD ---")
            print(f"Year: {row['Year']}")
            print(f"Status: {row['Status']}")
            print(f"Taxpayer: {row['Taxpayer']}")
            print(f"Income: ${row['Income']}")
            print(f"------------------------")
            print("\n🎊 Lifecycle simulation successful!")

    except Exception as e:
        print(f"❌ Simulation failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_simulation()
