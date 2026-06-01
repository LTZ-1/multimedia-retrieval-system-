def precision(retrieved, relevant):

    retrieved = set(retrieved)

    relevant = set(relevant)

    correct = retrieved.intersection(relevant)

    return len(correct) / len(retrieved)

def recall(retrieved, relevant):

    retrieved = set(retrieved)

    relevant = set(relevant)

    correct = retrieved.intersection(relevant)

    return len(correct) / len(relevant)

# EXAMPLE REAL TEST

retrieved = [
    "airplanes_1.jpg",
    "airplanes_2.jpg",
    "airplanes_3.jpg",
    "bonsai_1.jpg",
    "watch_1.jpg"
]

relevant = [
    "airplanes_1.jpg",
    "airplanes_2.jpg",
    "airplanes_3.jpg",
    "airplanes_4.jpg",
    "airplanes_5.jpg"
]

p = precision(retrieved, relevant)

r = recall(retrieved, relevant)

print("Precision:", round(p,2))

print("Recall:", round(r,2))