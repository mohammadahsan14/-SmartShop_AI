import pandas as pd

reviews = pd.read_csv("data/reviews/reviews.csv")

print(reviews.head())

print("\nDataset shape:")
print(reviews.shape)

print("\nColumns:")
print(reviews.columns.tolist())

print("\nMissing values:")
print(reviews.isnull().sum())


products = pd.read_csv("data/products/products.csv")

invalid_reviews = ~reviews["product_id"].isin(products["id"])

print("\nReviews with invalid product IDs:")

print(invalid_reviews.sum())


print("\nReview rating distribution:")
print(reviews["rating"].value_counts().sort_index())

print("\nReview date range:")
print(reviews["date"].min(), "to", reviews["date"].max())


