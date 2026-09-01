from typing import Literal

from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from src.database.db_connection import get_connection


load_dotenv()

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)


# --------------------------------------------------
# Request Models
# --------------------------------------------------

class ProductRequest(BaseModel):
    category: str | None = None
    max_price: float | None = None
    min_rating: float | None = None


class ProductIntent(BaseModel):
    intent: Literal[
        "catalog",
        "recommendation"
    ]


# --------------------------------------------------
# Category Normalization
# --------------------------------------------------

def normalize_category(category):

    if not category:
        return None

    category = category.lower().strip()

    if category in {
        "product",
        "products",
        "item",
        "items",
        "something",
        "anything"
    }:
        return None

    mapping = {
        "smartphones": "smartphone",
        "phones": "smartphone",
        "phone": "smartphone",

        "laptops": "laptop",

        "speakers": "speaker",

        "smart tv": "smart_tv",
        "smart tvs": "smart_tv",
        "tv": "smart_tv",
        "tvs": "smart_tv"
    }

    return mapping.get(
        category,
        category
    )


# --------------------------------------------------
# Detect Product Intent
# --------------------------------------------------

def extract_product_intent(user_request):

    structured_llm = llm.with_structured_output(
        ProductIntent
    )

    return structured_llm.invoke(
        f"""
You are classifying a SmartShop product request.

Customer request:
{user_request}

Choose exactly one intent:

catalog:
Use when the customer is asking about SmartShop's
overall product catalog or available product categories.

Examples:
- What kinds of products do you have?
- What products does SmartShop sell?
- What categories do you have?
- Do you only have speakers?
- Do you sell laptops?
- What else do you sell?

recommendation:
Use when the customer wants products recommended,
searched, or filtered.

Examples:
- Recommend me a laptop.
- Find a speaker under $300.
- What can I buy under $500?
- Show me products with a 5 star rating.
- Recommend a smartphone under $800.

Important:
- Classify only the current customer request.
- Do not assume the catalog contains only the category
  mentioned in the request.
"""
    )


# --------------------------------------------------
# Extract Recommendation Filters
# --------------------------------------------------

def extract_product_request(user_request):

    structured_llm = llm.with_structured_output(
        ProductRequest
    )

    return structured_llm.invoke(
        f"""
Extract shopping filters from this request:

{user_request}

Valid categories are only:
- laptop
- smartphone
- speaker
- smart_tv

Rules:
- If no specific category is mentioned,
  category must be null.
- Words like product, products, item, items,
  something, or anything are NOT categories.
- max_price can be null.
- min_rating can be null.
- Do not invent values.
"""
    )


# --------------------------------------------------
# Product Search
# --------------------------------------------------

def recommend_products(
    category=None,
    max_price=None,
    min_rating=None
):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        query = """
            SELECT
                id,
                name,
                brand,
                price,
                rating,
                stock
            FROM products
            WHERE stock > 0
        """

        params = []

        if category:
            query += " AND category = %s"
            params.append(category)

        if max_price is not None:
            query += " AND price <= %s"
            params.append(max_price)

        if min_rating is not None:
            query += " AND rating >= %s"
            params.append(min_rating)

        query += """
            ORDER BY
                rating DESC,
                price ASC
            LIMIT 5
        """

        cursor.execute(
            query,
            params
        )

        return cursor.fetchall()

    finally:

        cursor.close()
        conn.close()


# --------------------------------------------------
# Catalog Categories
# --------------------------------------------------

def get_product_categories():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT DISTINCT category
            FROM products
            WHERE category IS NOT NULL
            ORDER BY category
            """
        )

        return [
            row[0]
            for row in cursor.fetchall()
        ]

    finally:

        cursor.close()
        conn.close()


# --------------------------------------------------
# Main Recommendation Entry Point
# --------------------------------------------------

def recommend_from_text(user_request):

    intent = extract_product_intent(
        user_request
    )

    # ----------------------------------------------
    # Catalog question
    # ----------------------------------------------

    if intent.intent == "catalog":

        categories = get_product_categories()

        return {
            "type": "catalog",
            "categories": categories
        }

    # ----------------------------------------------
    # Recommendation question
    # ----------------------------------------------

    request = extract_product_request(
        user_request
    )

    category = normalize_category(
        request.category
    )

    products = recommend_products(
        category=category,
        max_price=request.max_price,
        min_rating=request.min_rating
    )

    return {
        "type": "products",
        "products": products
    }


# --------------------------------------------------
# Local Test
# --------------------------------------------------

if __name__ == "__main__":

    questions = [
        "What kinds of products does SmartShop have?",
        "Do you only have speakers?",
        "Recommend me a laptop under $900"
    ]

    for question in questions:

        print("\nQuestion:")
        print(question)

        result = recommend_from_text(
            question
        )

        print("\nResult:")
        print(result)