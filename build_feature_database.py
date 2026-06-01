import os
import numpy as np
from feature_extraction import extract_features

dataset_path = "small_dataset"

feature_database = []
image_paths = []

os.makedirs("features", exist_ok=True)

for category in os.listdir(dataset_path):

    category_path = os.path.join(dataset_path, category)

    # 🔥 SKIP FILES (VERY IMPORTANT FIX)
    if not os.path.isdir(category_path):
        print(f"Skipping non-folder: {category_path}")
        continue

    for image_name in os.listdir(category_path):

        image_path = os.path.join(category_path, image_name)

        if not image_name.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue

        try:
            features = extract_features(image_path)
            feature_database.append(features)
            image_paths.append(image_path)
        except Exception as e:
            print(f"Error reading {image_path}: {e}")

feature_database = np.array(feature_database)

np.save("features/features.npy", feature_database)
np.save("features/image_paths.npy", image_paths)

print("Feature database saved successfully.")