# Multimedia Retrieval System

This repository implements a multimedia retrieval system that supports two complementary approaches:

- **Metadata-Based Retrieval (MBR)**: searches images by keywords, categories, and annotated metadata.
- **Content-Based Retrieval (CBR)**: searches images by visual similarity using feature extraction and nearest-neighbor comparison.

## Evaluating Retrieval Performance

Retrieval performance can be assessed by comparing how well each approach returns relevant images for a given query. The two most common metrics are:

- **Precision**: the proportion of retrieved images that are actually relevant.
- **Recall**: the proportion of all relevant images that are retrieved.

### Metadata-Based Retrieval (MBR)

MBR relies on structured information stored in `metadata.csv`.

Advantages:

- Fast lookup through keyword matching.
- Good when metadata quality is high and categories are accurate.
- Easy to explain why a result was returned.

Limitations:

- Dependent on complete and consistent metadata.
- Cannot find visually similar images that are not described by the same text.
- Sensitive to spelling and keyword coverage.

### Content-Based Retrieval (CBR)

CBR compares image features directly, using a visual descriptor pipeline implemented in `feature_extraction.py`.

Advantages:

- Can identify visually similar images even without metadata.
- Works well when appearance matters more than category labels.
- Helps discover search results across different categories or missing annotations.

Limitations:

- Requires feature extraction and similarity computation, which is more compute-intensive.
- The quality of results depends on the chosen feature representation.
- May return visually similar images that are not semantically relevant.

## Comparing MBR vs. CBR

A strong evaluation should consider both approaches side by side:

- Use the same query dataset for both MBR and CBR.
- Measure precision and recall for each approach.
- Analyze cases where MBR succeeds and CBR fails, and vice versa.
- Consider macro-level metrics such as mean precision and mean recall across many queries.

### When to use each approach

- Use **MBR** when accurate metadata is already available and search must be fast.
- Use **CBR** when images may not have good metadata or when visual similarity is the primary criterion.
- A hybrid system is often best: use metadata to narrow candidates, then CBR to rerank by visual similarity.

## Existing Evaluation Tools

This project includes two evaluation scripts:

- `evaluation_auto.py`: performs automatic retrieval evaluation using image categories as ground truth and reports mean precision and recall over the dataset.
- `evaluation_manual.py`: runs a single query and asks the user to mark retrieved images as relevant so precision can be measured manually.

## How to run evaluation

1. Activate the virtual environment:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Run automatic evaluation:
   ```powershell
   python evaluation_auto.py
   ```
4. Run manual evaluation:
   ```powershell
   python evaluation_manual.py
   ```

## Notes on the Dataset

- Features are stored in `features/features.npy` and image paths in `features/image_paths.npy`.
- Metadata is stored in `metadata.csv` and is used by the web app and metadata-based search logic.
- The dataset contains category folders such as `airplanes`, `faces`, `watch`, and more.

## Using the Web App

The app in `app.py` supports both metadata-based and content-based retrieval modes.

- Select **Metadata-Based Retrieval** to search by keyword.
- Select **Content-Based Retrieval** to upload an image or provide a local image path.
- Precision and recall metrics shown in the UI are computed against available category and metadata relevance.
# multimedia-retrieval-system-
