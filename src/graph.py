from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

from src.agents.supervisor_agent import route_request
from src.agents.recommendation_agent import recommend_from_text
from src.agents.price_agent import compare_from_text
from src.agents.review_agent import summarize_reviews_from_text
from src.agents.policy_agent import answer_policy_question


# --------------------------------------------------
# Shared state
# --------------------------------------------------

class SmartShopState(TypedDict):
    user_request: str
    selected_agents: list[str]
    agent_results: list[str]
    response: str


# --------------------------------------------------
# General / Final LLM
# --------------------------------------------------

general_llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)


# --------------------------------------------------
# Supervisor
# --------------------------------------------------

def supervisor_node(state: SmartShopState):

    selected = route_request(
        state["user_request"]
    )

    return {
        "selected_agents": selected
    }


# --------------------------------------------------
# General helper
# --------------------------------------------------

def get_general_response(user_request: str):

    prompt = f"""
You are SmartShop AI, a shopping assistant.

User message:
{user_request}

If the user is greeting you or making casual conversation,
respond naturally and briefly.

If the request is unrelated to shopping, products, prices,
reviews, or store policies, politely explain that you are
a shopping assistant and mention what you can help with.

Do not pretend you can perform capabilities that SmartShop
does not have.
"""

    response = general_llm.invoke(prompt)

    return response.content


# --------------------------------------------------
# Product formatter
# --------------------------------------------------

def format_products(products):

    if not products:
        return "No matching products were found."

    lines = []

    for product in products:

        product_id, name, brand, price, rating, stock = product

        lines.append(
            f"{name}\n"
            f"Product ID: {product_id}\n"
            f"Brand: {brand}\n"
            f"Price: ${float(price):.2f}\n"
            f"Rating: {float(rating):.1f}/5\n"
            f"Stock: {stock}"
        )

    return "\n\n".join(lines)


# --------------------------------------------------
# Multi-Agent Dispatcher
# --------------------------------------------------

def multi_agent_node(state: SmartShopState):

    results = []

    selected_agents = state["selected_agents"]

    for agent in selected_agents:

        # ------------------------------------------
        # Recommendation
        # ------------------------------------------

        if agent == "recommendation":

            result = recommend_from_text(
                state["user_request"]
            )

            if result["type"] == "catalog":

                categories = result["categories"]

                formatted_categories = ", ".join(
                    category.replace("_", " ")
                    for category in categories
                )

                results.append(
                    "Catalog result:\n"
                    f"SmartShop currently has these product categories: "
                    f"{formatted_categories}."
                )

            elif result["type"] == "products":

                results.append(
                    "Recommendation result:\n"
                    + format_products(
                        result["products"]
                    )
                )

        # ------------------------------------------
        # Price
        # ------------------------------------------

        elif agent == "price":

            products = compare_from_text(
                state["user_request"]
            )

            results.append(
                "Price comparison result:\n"
                + format_products(products)
            )

        # ------------------------------------------
        # Review
        # ------------------------------------------

        elif agent == "review":

            answer = summarize_reviews_from_text(
                state["user_request"]
            )

            results.append(
                "Review result:\n"
                + answer
            )

        # ------------------------------------------
        # Policy
        # ------------------------------------------

        elif agent == "policy":

            answer = answer_policy_question(
                state["user_request"]
            )

            results.append(
                "Policy result:\n"
                + answer
            )

        # ------------------------------------------
        # General
        # ------------------------------------------

        elif agent == "general":

            answer = get_general_response(
                state["user_request"]
            )

            results.append(
                "General response:\n"
                + answer
            )

    # Safety fallback
    if not results:
        results.append(
            "No specialist result was available."
        )

    return {
        "agent_results": results
    }


# --------------------------------------------------
# Final Response Composer
# --------------------------------------------------

def final_response_node(state: SmartShopState):

    combined_results = "\n\n".join(
        state["agent_results"]
    )

    prompt = f"""
You are SmartShop AI, a helpful shopping assistant.

Create ONE clean, natural, customer-facing answer.

Customer request:
{state["user_request"]}

Internal specialist results:
{combined_results}

Important rules:

1. Do not mention agents, routing, LangGraph, databases,
   specialist results, or internal system behavior.

2. Do not separate the answer into artificial sections such as:
   "Recommendations", "Reviews", "Policy",
   "Recommendation Agent", "Review Agent", or "Policy Agent".

3. Combine everything into one cohesive response.

4. Connect product recommendations, reviews, pricing,
   and store policy naturally when relevant.

5. Remove duplicated or irrelevant information.

6. Only use facts contained in the internal specialist results.
   Never invent product details, review feedback, prices,
   ratings, stock, or policy information.

7. If one internal result says information could not be found,
   do not make up an answer. Explain that naturally only if
   it is useful to the customer.

8. Prioritize the strongest product options instead of simply
   dumping raw records.

9. Keep the response clear, conversational, and useful.
"""

    result = general_llm.invoke(prompt)

    return {
        "response": result.content
    }


# --------------------------------------------------
# Build LangGraph
# --------------------------------------------------

graph_builder = StateGraph(
    SmartShopState
)


# --------------------------------------------------
# Add nodes
# --------------------------------------------------

graph_builder.add_node(
    "supervisor",
    supervisor_node
)

graph_builder.add_node(
    "multi_agent",
    multi_agent_node
)

graph_builder.add_node(
    "final_response",
    final_response_node
)


# --------------------------------------------------
# Entry point
# --------------------------------------------------

graph_builder.set_entry_point(
    "supervisor"
)


# --------------------------------------------------
# Routing
# --------------------------------------------------

graph_builder.add_edge(
    "supervisor",
    "multi_agent"
)

graph_builder.add_edge(
    "multi_agent",
    "final_response"
)


# --------------------------------------------------
# End
# --------------------------------------------------

graph_builder.add_edge(
    "final_response",
    END
)


# --------------------------------------------------
# Compile graph
# --------------------------------------------------

smartshop_graph = graph_builder.compile()


# --------------------------------------------------
# Local test
# --------------------------------------------------

if __name__ == "__main__":

    question = """
Do you have only speakers?
"""

    result = smartshop_graph.invoke(
        {
            "user_request": question,
            "selected_agents": [],
            "agent_results": [],
            "response": ""
        }
    )

    print(
        "Selected agents:",
        result["selected_agents"]
    )

    print("\nResponse:")
    print(
        result["response"]
    )