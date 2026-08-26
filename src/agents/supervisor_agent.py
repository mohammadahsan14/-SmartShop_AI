from typing import Literal
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(model="gpt-4.1-mini")


class RouteDecision(BaseModel):
    agent: Literal[
        "recommendation",
        "review",
        "price",
        "policy",
        "general"
    ]


router = llm.with_structured_output(RouteDecision)


def route_request(user_request):
    decision = router.invoke(
        f"""
        Route this customer request to exactly one agent.

        recommendation:
        Used when the customer wants product suggestions.

        review:
        Used when the customer asks about customer reviews,
        opinions, pros, cons, or sentiment.

        price:
        Used when the customer wants to compare products,
        prices, brands, or value.

        policy:
        Used for returns, refunds, exchanges, shipping,
        or store-policy questions.

        general:
        Greetings
        Thanks
        Casual conversation
        Questions that don't belong to the other agents

        Customer request:
        {user_request}
        """
    )

    return decision.agent


if __name__ == "__main__":
    question = "Find me a good laptop under $900"

    selected_agent = route_request(question)

    print("Supervisor selected:", selected_agent)