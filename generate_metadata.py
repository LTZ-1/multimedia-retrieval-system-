import os
import pandas as pd

dataset_path = "small_dataset"

data = []

# CHECK dataset exists
if not os.path.exists(dataset_path):
    print("Dataset folder not found!")
    exit()

for category in os.listdir(dataset_path):

    category_path = os.path.join(dataset_path, category)

    # skip non-folders
    if not os.path.isdir(category_path):
        continue

    for image_name in os.listdir(category_path):

        # only images
        if image_name.endswith(('.jpg', '.jpeg', '.png')):

            data.append({
                "image_name": image_name,
                "category": category,
                "keywords": category.replace("_", " ")
            })

# CREATE dataframe
df = pd.DataFrame(data)

# CHECK if dataframe empty
if df.empty:
    print("No images found!")
else:
    df.to_csv("metadata.csv", index=False)
    print("Metadata file created successfully.")
    print(df.head())