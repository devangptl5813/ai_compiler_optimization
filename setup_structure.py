import os

# Create directory structure
dirs = [
    "programs",
    "src",
    "data",
    "models",
    "results",
    "results/graphs"
]

for d in dirs:
    os.makedirs(d, exist_ok=True)

print("Created folder structure successfully.")
