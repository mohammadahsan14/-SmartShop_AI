from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

from src.database.db_connection import get_connection

load_dotenv()

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)


def embed_all_policies():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT policy_id, policy_type, description, conditions, timeframe
        FROM policies
        WHERE embedding IS NULL
    """)

    policies = cursor.fetchall()

    print(f"Policies to embed: {len(policies)}")

    for policy in policies:
        policy_id, policy_type, description, conditions, timeframe = policy

        text = f"""
        Policy Type: {policy_type}
        Description: {description}
        Conditions: {conditions}
        Timeframe: {timeframe}
        """

        vector = embeddings.embed_query(text)

        cursor.execute("""
            UPDATE policies
            SET embedding = %s
            WHERE policy_id = %s
        """, (vector, policy_id))

        print(f"Embedded policy {policy_id}")

    conn.commit()

    cursor.close()
    conn.close()

    print("All policies embedded successfully.")


if __name__ == "__main__":
    embed_all_policies()