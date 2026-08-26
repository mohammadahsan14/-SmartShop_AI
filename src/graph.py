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
    selected_agent: str
    response: str


# --------------------------------------------------
# General LLM
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
        "selected_agent": selected
    }


# --------------------------------------------------
# General Node
# --------------------------------------------------

def general_node(state: SmartShopState):

    prompt = f"""
You are SmartShop AI, a shopping assistant.

User message:
{state["user_request"]}

If the user is greeting you or making casual conversation,
respond naturally and briefly.

If the request is unrelated to shopping, products, prices,
reviews, or store policies, politely explain that you are
a shopping assistant and mention what you can help with.

Do not pretend you can perform capabilities that SmartShop
does not have.
"""

    response = general_llm.invoke(prompt)

    return {
        "response": response.content
    }


# --------------------------------------------------
# Product formatter
# --------------------------------------------------

def format_products(products):
    if not products:
        return "I couldn't find matching products."

    lines = []

    for product in products:
        product_id, name, brand, price, rating, stock = product

        lines.append(
            f"**{name}**\n"
            f"ID: {product_id}\n"
            f"Brand: {brand}\n"
            f"Price: ${float(price):.2f}\n"
            f"Rating: ⭐ {float(rating):.1f}\n"
            f"Stock: {stock}"
        )

    return "\n\n---\n\n".join(lines)


# --------------------------------------------------
# Recommendation Agent
# --------------------------------------------------

def recommendation_node(state: SmartShopState):
    products = recommend_from_text(
        state["user_request"]
    )

    return {
        "response": format_products(products)
    }


# --------------------------------------------------
# Price Comparison Agent
# --------------------------------------------------

def price_node(state: SmartShopState):
    products = compare_from_text(
        state["user_request"]
    )

    return {
        "response": format_products(products)
    }


# --------------------------------------------------
# Review Agent
# --------------------------------------------------

def review_node(state: SmartShopState):
    answer = summarize_reviews_from_text(
        state["user_request"]
    )

    return {
        "response": answer
    }


# --------------------------------------------------
# Policy Agent
# --------------------------------------------------

def policy_node(state: SmartShopState):
    answer = answer_policy_question(
        state["user_request"]
    )

    return {
        "response": answer
    }


# --------------------------------------------------
# Build LangGraph
# --------------------------------------------------

graph_builder = StateGraph(
    SmartShopState
)

graph_builder.add_node(
    "supervisor",
    supervisor_node
)

graph_builder.add_node(
    "recommendation",
    recommendation_node
)

graph_builder.add_node(
    "price",
    price_node
)

graph_builder.add_node(
    "review",
    review_node
)

graph_builder.add_node(
    "policy",
    policy_node
)

graph_builder.add_node(
    "general",
    general_node
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

def route_from_supervisor(state: SmartShopState):
    return state["selected_agent"]


graph_builder.add_conditional_edges(
    "supervisor",
    route_from_supervisor,
    {
        "recommendation": "recommendation",
        "price": "price",
        "review": "review",
        "policy": "policy",
        "general": "general"
    }
)


# --------------------------------------------------
# End routes
# --------------------------------------------------

graph_builder.add_edge(
    "recommendation",
    END
)

graph_builder.add_edge(
    "price",
    END
)

graph_builder.add_edge(
    "review",
    END
)

graph_builder.add_edge(
    "policy",
    END
)

graph_builder.add_edge(
    "general",
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
    question = "Hi"

    result = smartshop_graph.invoke(
        {
            "user_request": question,
            "selected_agent": "",
            "response": ""
        }
    )

    print(
        "Selected agent:",
        result["selected_agent"]
    )

    print("\nResponse:")
    print(
        result["response"]
    )