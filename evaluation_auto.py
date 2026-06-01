import os
import numpy as np
from collections import defaultdict
from feature_extraction import extract_features
from sklearn.metrics.pairwise import cosine_similarity

# Load feature database
features = np.load("features/features.npy")
image_paths = np.load("features/image_paths.npy", allow_pickle=True)

# Create category map from path
def get_category(path):
    return path.split("\\")[-2]

# Build ground truth
ground_truth = defaultdict(list)

for path in image_paths:
    category = get_category(path)
    ground_truth[category].append(path)

def search(query_features, top_k=5):
    sims = cosine_similarity([query_features], features)[0]
    idx = np.argsort(sims)[::-1][:top_k]
    return [image_paths[i] for i in idx]

# Evaluate system
precision_list = []
recall_list = []

for query_path in image_paths:

    query_features = extract_features(query_path)
    category = get_category(query_path)

    relevant = set(ground_truth[category])

    retrieved = search(query_features, top_k=5)
    retrieved_set = set(retrieved)

    tp = len(retrieved_set & relevant)

    precision = tp / len(retrieved_set)
    recall = tp / len(relevant)

    precision_list.append(precision)
    recall_list.append(recall)

print("\n===== AUTO EVALUATION RESULTS =====")
print("Mean Precision:", sum(precision_list) / len(precision_list))
print("Mean Recall:", sum(recall_list) / len(recall_list))