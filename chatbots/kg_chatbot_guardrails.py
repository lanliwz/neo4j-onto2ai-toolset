from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from llm_neo4j_connect import *
from cipher_execute_state import *

guardrails_system = """
As an intelligent assistant, your primary objective is to decide whether a given question is related to account/balance/billing/payment or not. 
If the question is related, output "account". Otherwise, output "end".
To make this decision, assess the content of the question and determine if it refers to any account balance, transaction, billing, payment, 
or related topics. Provide only the specified output: "account" or "end".
"""

guardrails_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            guardrails_system,
        ),
        (
            "human",
            ("{question}"),
        ),
    ]
)

class GuardrailsOutput(BaseModel):
    decision: Literal["account", "end"] = Field(
        description="Decision on whether the question is related to account"
    )

guardrails_chain = guardrails_prompt | llm.with_structured_output(GuardrailsOutput)


def guardrails(state: InputState) -> OverallState:
    """
    Decides if the question is related to account or not.
    """
    guardrails_output = guardrails_chain.invoke({"question": state.get("question")})
    database_records = None
    if guardrails_output.decision == "end":
        database_records = "This questions is not about account. Therefore I cannot answer this question."
    return {
        "next_action": guardrails_output.decision,
        "database_records": database_records,
        "steps": ["guardrail"],
    }