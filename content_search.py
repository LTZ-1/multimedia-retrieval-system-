import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from feature_extraction import extract_features

feature_database = np.load("features/features.npy")

image_paths = np.load(
    "features/image_paths.npy",
    allow_pickle=True
)

def content_search(query_image):

    query_features = extract_features(query_image)

    similarities = cosine_similarity(
        [query_features],
        feature_database
    )[0]

    sorted_indices = similarities.argsort()[::-1]

    top_results = sorted_indices[:5]

    return top_results, similarities

query_image = input("Enter query image path: ")

results, similarities = content_search(query_image)

print("\nTop Matching Images:\n")

for i in results:

    print(
        image_paths[i],
        "Similarity:",
        round(similarities[i], 4)
    )
import time

start = time.time()

results, similarities = content_search(query_image)

end = time.time()

print("\nRetrieval Time:", round(end-start, 4), "seconds")