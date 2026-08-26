from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from src.database.db_connection import get_connection

load_dotenv()

llm = ChatOpenAI(model="gpt-4.1-mini")


class ReviewRequest(BaseModel):
    product_id: str | None = None
    product_name: str | None = None


def extract_review_request(user_request):
    structured_llm = llm.with_structured_output(ReviewRequest)
    return structured_llm.invoke(user_request)


def find_product_id(product_id=None, product_name=None):
    conn = get_connection()
    cursor = conn.cursor()

    if product_id:
        cursor.execute("""
            SELECT id
            FROM products
            WHERE id = %s
            LIMIT 1
        """, (product_id,))

    elif product_name:
        cursor.execute("""
            SELECT id
            FROM products
            WHERE LOWER(name) LIKE LOWER(%s)
            LIMIT 1
        """, (f"%{product_name}%",))

    else:
        cursor.close()
        conn.close()
        return None

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result[0] if result else None


def get_reviews(product_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT rating, text
        FROM reviews
        WHERE product_id = %s
        LIMIT 20
    """, (product_id,))

    reviews = cursor.fetchall()

    cursor.close()
    conn.close()

    return reviews


def summarize_reviews(product_id):
    reviews = get_reviews(product_id)

    if not reviews:
        return "No customer reviews were found for this product."

    review_text = "\n".join(
        [f"Rating: {r[0]} | Review: {r[1]}" for r in reviews]
    )

    prompt = f"""
    Summarize these customer reviews.

    Return:
    - Overall sentiment
    - Main positives
    - Main complaints

    Reviews:
    {review_text}
    """

    response = llm.invoke(prompt)

    return response.content


def summarize_reviews_from_text(user_request):
    request = extract_review_request(user_request)

    product_id = find_product_id(
        request.product_id,
        request.product_name
    )

    if not product_id:
        return "I could not find that product."

    return summarize_reviews(product_id)