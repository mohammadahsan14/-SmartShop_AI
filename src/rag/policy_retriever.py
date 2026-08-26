from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

from src.database.db_connection import get_connection

load_dotenv()

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)


def retrieve_policies(question, limit=3):

    question_vector = embeddings.embed_query(question)

    # Convert Python list → pgvector format
    vector_string = "[" + ",".join(map(str, question_vector)) + "]"

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            policy_id,
            policy_type,
            description,
            conditions,
            timeframe,
            embedding <=> %s::vector AS distance
        FROM policies
        WHERE embedding IS NOT NULL
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """, (
        vector_string,
        vector_string,
        limit
    ))

    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results


if __name__ == "__main__":

    question = "Can I return my laptop after 20 days?"

    results = retrieve_policies(question)

    for policy in results:
        print("\nPolicy:", policy[1])
        print("Description:", policy[2])
        print("Timeframe:", policy[4])
        print("Distance:", policy[5])