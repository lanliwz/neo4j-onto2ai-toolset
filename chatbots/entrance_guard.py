from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from llm_neo4j_connect import *
from langgraph_state_model import *

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


def guardrails(state: InputState,llm_chain = guardrails_chain) -> OverallState:
    """
    Decides if the question is related to account or not.
    """


    guardrails_output = llm_chain.invoke({"question": state.get("question")})
    database_records = None
    if guardrails_output.decision == "end":
        database_records = "This questions is not about account. Therefore I cannot answer this question."
    return {
        "next_action": guardrails_output.decision,
        "database_records": database_records,
        "steps": ["guardrail"],
    }

def guard_of_taxsystem(state: InputState, llm: ChatOpenAI) -> OverallState:
    class GuardOfTaxSystemOutput(BaseModel):
        decision: Literal["continue", "end"] = Field(
            description="Decision on whether the question is related to tax, payment, billing etc"
        )

    guard_of_entrance = """
    As an intelligent assistant, your primary objective is to decide whether a given question is related to tax/account/balance/billing/payment or not. 
    If the question is related, output "continue". Otherwise, output "end".
    To make this decision, assess the content of the question and determine if it refers to any account balance, transaction, billing, payment, 
    or related topics. Provide only the specified output: "continue" or "end".
    """

    guard_of_entrance_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                guard_of_entrance,
            ),
            (
                "human",
                ("{question}"),
            ),
        ]
    )
    guard_of_entrance_chain = guard_of_entrance_prompt | llm.with_structured_output(GuardOfTaxSystemOutput)
    output = guard_of_entrance_chain.invoke({"question": state.get("question")})
    database_records = None
    if output.decision == "end":
        database_records = "This questions is not about tax/account/balance/billing/payment. Therefore I cannot answer this question."
    return {
        "next_action": output.decision,
        "database_records": database_records,
        "steps": ["guardrail"],
    }

