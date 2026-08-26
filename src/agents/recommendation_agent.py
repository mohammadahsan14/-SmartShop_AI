from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from src.database.db_connection import get_connection

load_dotenv()

llm = ChatOpenAI(model="gpt-4.1-mini")


class ProductRequest(BaseModel):
    category: str | None = None
    max_price: float | None = None
    min_rating: float | None = None


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
        "tvs": "smart_tv"
    }

    return mapping.get(category, category)


def extract_product_request(user_request):
    structured_llm = llm.with_structured_output(ProductRequest)

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
- If no specific category is mentioned, category must be null.
- Words like product, item, something, or anything are NOT categories.
- max_price can be null.
- min_rating can be null.
- Do not invent values.
"""
    )


def recommend_products(
    category=None,
    max_price=None,
    min_rating=None
):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT id, name, brand, price, rating, stock
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
        ORDER BY rating DESC, price ASC
        LIMIT 5
    """

    cursor.execute(query, params)

    products = cursor.fetchall()

    cursor.close()
    conn.close()

    return products


def recommend_from_text(user_request):
    request = extract_product_request(user_request)

    category = normalize_category(
        request.category
    )

    return recommend_products(
        category,
        request.max_price,
        request.min_rating
    )