import pandas as pd

policies = pd.read_csv("data/policies/store_policies.csv")

print(policies.head())

print("\nDataset shape:")
print(policies.shape)

print("\nColumns:")
print(policies.columns.tolist())

print("\nMissing values:")


