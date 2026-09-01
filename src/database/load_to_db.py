import os
from dotenv import load_dotenv

import pandas as pd
import psycopg2


# --------------------------------------------------
# Environment
# --------------------------------------------------

load_dotenv()


# --------------------------------------------------
# Database connection
# --------------------------------------------------

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )


# --------------------------------------------------
# Load products
# --------------------------------------------------

def load_products(cursor):

    products = pd.read_csv(
        "data/products/products.csv"
    )

    print("\n--- Products ---")
    print("Rows:", len(products))
    print("Columns:", products.columns.tolist())
    print(
        "Duplicate IDs:",
        products["id"].duplicated().sum()
    )

    for _, row in products.iterrows():

        cursor.execute(
            """
            INSERT INTO products
            (
                id,
                name,
                brand,
                category,
                price,
                description,
                stock,
                rating
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
            """,
            (
                row["id"],
                row["name"],
                row["brand"],
                row["category"],
                row["price"],
                row["description"],
                row["stock"],
                row["rating"]
            )
        )

    print(
        f"Loaded {len(products)} products."
    )


# --------------------------------------------------
# Load reviews
# --------------------------------------------------

def load_reviews(cursor):

    reviews = pd.read_csv(
        "data/reviews/reviews.csv"
    )

    products = pd.read_csv(
        "data/products/products.csv"
    )

    invalid_reviews = ~reviews["product_id"].isin(
        products["id"]
    )

    print("\n--- Reviews ---")
    print("Rows:", len(reviews))
    print("Columns:", reviews.columns.tolist())
    print(
        "Invalid product IDs:",
        invalid_reviews.sum()
    )

    for _, row in reviews.iterrows():

        cursor.execute(
            """
            INSERT INTO reviews
            (
                product_id,
                rating,
                text,
                date
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                row["product_id"],
                row["rating"],
                row["text"],
                row["date"]
            )
        )

    print(
        f"Loaded {len(reviews)} reviews."
    )


# --------------------------------------------------
# Load policies
# --------------------------------------------------

def load_policies(cursor):

    policies = pd.read_csv(
        "data/policies/store_policies.csv"
    )

    print("\n--- Policies ---")
    print("Rows:", len(policies))
    print("Columns:", policies.columns.tolist())

    for _, row in policies.iterrows():

        cursor.execute(
            """
            INSERT INTO policies
            (
                policy_type,
                description,
                conditions,
                timeframe
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                row["policy_type"],
                row["description"],
                row["conditions"],
                row["timeframe"]
            )
        )

    print(
        f"Loaded {len(policies)} policies."
    )


# --------------------------------------------------
# Clear existing seed data
# --------------------------------------------------

def clear_existing_data(cursor):

    print("\n--- Clearing existing data ---")

    # Reviews may reference products,
    # so reviews must be deleted first.
    cursor.execute(
        "DELETE FROM reviews;"
    )

    cursor.execute(
        "DELETE FROM policies;"
    )

    cursor.execute(
        "DELETE FROM products;"
    )

    print("Existing seed data cleared.")


# --------------------------------------------------
# Load everything
# --------------------------------------------------

def load_all():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        # Start with a clean dataset
        clear_existing_data(cursor)

        # Reload all CSV datasets
        load_products(cursor)
        load_reviews(cursor)
        load_policies(cursor)

        conn.commit()

        print(
            "\nAll SmartShop data loaded successfully."
        )

    except Exception as exc:

        # Undo everything if any step fails
        conn.rollback()

        print(
            "\nDatabase load failed:"
        )

        print(exc)

        raise

    finally:

        cursor.close()
        conn.close()


# --------------------------------------------------
# Main
# --------------------------------------------------

if __name__ == "__main__":
    load_all()