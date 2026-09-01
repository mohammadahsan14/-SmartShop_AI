from typing import Literal

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel


# --------------------------------------------------
# Environment
# --------------------------------------------------

load_dotenv()


# --------------------------------------------------
# LLM
# --------------------------------------------------

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)


# --------------------------------------------------
# Supervisor structured output
# --------------------------------------------------

class RouteDecision(BaseModel):
    agents: list[
        Literal[
            "recommendation",
            "review",
            "price",
            "policy",
            "general"
        ]
    ]


router = llm.with_structured_output(RouteDecision)


# --------------------------------------------------
# Route customer request
# --------------------------------------------------

def route_request(user_request: str) -> list[str]:

    decision = router.invoke(
        f"""
        You are the supervisor for SmartShop AI.

        Your job is to identify ALL agents needed to answer
        the customer's request.

        Available agents:

        recommendation:
        Use when the customer wants product suggestions,
        recommendations, or help finding products.

        review:
        Use when the customer asks about customer reviews,
        opinions, ratings, pros, cons, feedback, or sentiment.

        price:
        Use when the customer wants to compare products,
        prices, brands, costs, or value.

        policy:
        Use when the customer asks about returns,
        refunds, exchanges, shipping, warranty,
        or other store policies.

        general:
        Use for greetings, thanks, casual conversation,
        or questions that do not belong to a specialist agent.


        IMPORTANT ROUTING RULES:

        1. A customer request may require MULTIPLE agents.

        2. Return EVERY relevant agent needed to answer
           the complete request.

        3. Do NOT select only the primary intent when the
           customer asks for multiple things.

        4. Do NOT include "general" when one or more
           specialist agents can answer the request.

        5. Only select agents that are actually relevant
           to the customer's request.


        Examples:

        Customer:
        "Recommend me a laptop under $900"

        Agents:
        ["recommendation"]


        Customer:
        "What do customers say about laptops?"

        Agents:
        ["review"]


        Customer:
        "Compare these laptop prices"

        Agents:
        ["price"]


        Customer:
        "What is your return policy?"

        Agents:
        ["policy"]


        Customer:
        "Recommend me a laptop under $900 and explain
        the return policy"

        Agents:
        ["recommendation", "policy"]


        Customer:
        "Recommend me a laptop under $900,
        tell me what the reviews say,
        and explain the return policy."

        Agents:
        ["recommendation", "review", "policy"]


        Customer:
        "Hello, how are you?"

        Agents:
        ["general"]


        Customer request:

        {user_request}
        """
    )

    return decision.agents


# --------------------------------------------------
# Local test
# --------------------------------------------------

if __name__ == "__main__":

    question = """
    Recommend me a laptop under $900,
    tell me what the reviews say,
    and explain the return policy.
    """

    selected_agents = route_request(question)

    print("Supervisor selected:", selected_agents)