from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from src.database.db_connection import get_connection

load_dotenv()

llm = ChatOpenAI(model="gpt-4.1-mini")


class PriceRequest(BaseModel):
    category: str
    max_price: float | None = None


def normalize_category(category):
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

    category = category.lower().strip()
    return mapping.get(category, category)


def extract_price_request(user_request):
    structured_llm = llm.with_structured_output(PriceRequest)
    return structured_llm.invoke(user_request)


def compare_products(category, max_price=None):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT id, name, brand, price, rating, stock
        FROM products
        WHERE category = %s
          AND stock > 0
    """

    params = [category]

    if max_price is not None:
        query += " AND price <= %s"
        params.append(max_price)

    query += """
        ORDER BY rating DESC, price ASC
        LIMIT 5
    """

    cursor.execute(query, params)
    products = cursor.fetchall()

    cursor.close()
    conn.close()

    return products


def compare_from_text(user_request):
    request = extract_price_request(user_request)

    category = normalize_category(request.category)

    return compare_products(
        category,
        request.max_price
    )