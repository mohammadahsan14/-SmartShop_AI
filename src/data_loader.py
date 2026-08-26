import pandas as pd

df = pd.read_csv("data/products/products.csv")

print(df.head())


print("\nDataset shape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nData types:")
print(df.dtypes)

print("\nMissing values:")
print(df.isnull().sum())

print("\nProduct categories:")
print(df["category"].value_counts())

print("\nBrands:")
print(df["brand"].value_counts())

print("\nDuplicate IDs:")
print(df["id"].duplicated().sum())

print("\nPrice range:")
print(df["price"].min(), "-", df["price"].max())

print("\nRating range:")
print(df["rating"].min(), "-", df["rating"].max())

print("\nStock range:")
print(df["stock"].min(), "-", df["stock"].max())