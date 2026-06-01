import pandas as pd

metadata = pd.read_csv("metadata.csv")

metadata['keywords'] = metadata['keywords'].fillna('')

def metadata_search(query):

    results = metadata[
        metadata['keywords'].str.contains(
            query,
            case=False,
            na=False
        )
    ]

    return results

query = input("Enter search keyword: ")

results = metadata_search(query)

print("\nRetrieved Images:\n")

print(results)