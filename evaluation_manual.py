import numpy as np
from feature_extraction import extract_features
from sklearn.metrics.pairwise import cosine_similarity

features = np.load("features/features.npy")
image_paths = np.load("features/image_paths.npy", allow_pickle=True)

def search(query_features, top_k=5):
    sims = cosine_similarity([query_features], features)[0]
    idx = np.argsort(sims)[::-1][:top_k]
    return [image_paths[i] for i in idx]

# input query image
query_path = input("Enter query image path: ")

query_features = extract_features(query_path)

results = search(query_features)

print("\nTop Results:\n")
for r in results:
    print(r)

# manual relevance input
relevant_count = int(input("\nHow many of these are relevant? "))

precision = relevant_count / len(results)

print("\nPrecision:", precision)