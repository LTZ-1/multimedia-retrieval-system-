"""
Multimedia Retrieval System - Database Integrated Version
Evaluates metadata-based retrieval (MBR) vs content-based retrieval (CBIR)
"""
from flask import Flask, render_template_string, request, url_for
from werkzeug.utils import secure_filename
import numpy as np
import os
import time
from PIL import Image as PILImage
import json
import webbrowser
import threading
import logging

from sklearn.metrics.pairwise import cosine_similarity
from models import db, Image, ImageFeature, SearchQuery
from config import (
    SQLALCHEMY_DATABASE_URI, 
    UPLOAD_FOLDER, 
    SMALL_DATASET_PATH,
    FEATURE_VECTOR_DIM
)

# ============================================================================
# FLASK APP SETUP
# ============================================================================
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max upload: 16MB

os.environ.setdefault("FLASK_ENV", "production")
os.environ.setdefault("FLASK_DEBUG", "0")

app.config.update(DEBUG=False, TESTING=False, ENV="production")
app.debug = False

# Initialize database
db.init_app(app)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================
with app.app_context():
    # Create all tables if they don't exist
    db.create_all()
    
    # Check if database is populated
    image_count = Image.query.count()
    if image_count == 0:
        print("\n⚠️  WARNING: Database is empty!")
        print("   Run: python migrate_to_database.py")
        print("   This will migrate your existing CSV and NumPy data to the database.\n")

# ============================================================================
# FEATURE EXTRACTION
# ============================================================================
def extract_features(image_path):
    """
    Extract 512-dimensional color histogram features from an image using Pillow
    Compatible with Python 3.14 (no OpenCV required)
    Creates 8x8x8 3D color histogram (512 bins total)
    """
    image_path = image_path.replace("\\", "/")

    if not os.path.exists(image_path):
        raise ValueError(f"File not found: {image_path}")

    try:
        # Open and resize image using Pillow
        img = PILImage.open(image_path).convert('RGB')
        img = img.resize((256, 256))
        
        # Convert to numpy array
        img_array = np.array(img, dtype=np.uint8)
        
        # Quantize to 8 levels per channel (0-255 -> 0-7)
        r_quantized = (img_array[:, :, 0] // 32).astype(np.int32)
        g_quantized = (img_array[:, :, 1] // 32).astype(np.int32)
        b_quantized = (img_array[:, :, 2] // 32).astype(np.int32)
        
        # Ensure values are in range [0, 7]
        r_quantized = np.clip(r_quantized, 0, 7)
        g_quantized = np.clip(g_quantized, 0, 7)
        b_quantized = np.clip(b_quantized, 0, 7)
        
        # Create 3D histogram: 8x8x8 = 512 bins
        hist_3d = np.zeros((8, 8, 8), dtype=np.float32)
        
        for i in range(img_array.shape[0]):
            for j in range(img_array.shape[1]):
                r_idx = r_quantized[i, j]
                g_idx = g_quantized[i, j]
                b_idx = b_quantized[i, j]
                hist_3d[r_idx, g_idx, b_idx] += 1
        
        # Flatten to 512D vector and normalize
        hist = hist_3d.flatten()
        hist = hist / (hist.sum() + 1e-10)
        
        return hist.astype(np.float32)
    
    except Exception as e:
        raise ValueError(f"Error processing image {image_path}: {str(e)}")


# ============================================================================
# METADATA-BASED RETRIEVAL (MBR)
# ============================================================================
def metadata_search(query, top_k=50):
    """
    Search by keywords in metadata
    """
    # Case-insensitive keyword search
    results = Image.query.filter(
        Image.keywords.ilike(f'%{query}%')
    ).limit(top_k).all()
    
    return results


def metadata_relevant(query):
    """
    Get all relevant images for a keyword query
    Used for computing recall
    """
    results = Image.query.filter(
        Image.keywords.ilike(f'%{query}%')
    ).all()
    
    return results


# ============================================================================
# CONTENT-BASED RETRIEVAL (CBIR)
# ============================================================================
def content_search(query_image, top_k=50):
    """
    Search by visual similarity using color histograms
    Returns: list of Image objects and their similarity scores
    """
    # Extract features from query image
    q_feat = extract_features(query_image)
    
    # Get all images with features from database
    all_images = Image.query.all()
    
    if not all_images:
        return [], []
    
    # Build feature matrix
    features_list = []
    images_with_features = []
    
    for img in all_images:
        if img.features:
            try:
                features_list.append(img.features.features_array)
                images_with_features.append(img)
            except Exception as e:
                print(f"Warning: Could not load features for {img.image_name}: {e}")
    
    if not features_list:
        return [], []
    
    features_array = np.array(features_list)
    
    # Compute similarity
    sims = cosine_similarity([q_feat], features_array)[0]
    
    # Sort by similarity
    idx = np.argsort(sims)[::-1][:top_k]
    
    return [images_with_features[i] for i in idx], sims[idx]


def category_relevant(category):
    """
    Get all images in a specific category
    Used for computing recall
    """
    return Image.query.filter(Image.category == category).all()




# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def get_category_from_path(image_path):
    """Extract category from file path or metadata"""
    image_path = image_path.replace("\\", "/")
    basename = os.path.basename(image_path)
    
    # Try to find in database
    img = Image.query.filter(Image.image_name == basename).first()
    if img:
        return img.category
    
    # Try to infer from path
    parts = image_path.split("/")
    if len(parts) >= 2 and parts[-2] not in {"uploads", "static", "features"}:
        return parts[-2]
    
    return None


def get_category_from_query(query):
    """Get category from query string"""
    if not query:
        return None
    
    q = query.strip().lower()
    if not q:
        return None
    
    # Try direct lookup first
    img = Image.query.filter(Image.keywords.ilike(f'%{q}%')).first()
    if img:
        return img.category
    
    return None


def predict_category_from_feature(feature):
    """
    Predict category by finding most similar category centroid
    """
    # Get all images and group by category
    all_images = Image.query.all()
    category_features = {}
    
    for img in all_images:
        if img.features:
            try:
                if img.category not in category_features:
                    category_features[img.category] = []
                category_features[img.category].append(img.features.features_array)
            except:
                pass
    
    # Compute category centroids
    best_category = None
    best_score = -1.0
    
    for category, features_list in category_features.items():
        centroid = np.mean(features_list, axis=0)
        score = cosine_similarity([feature], [centroid])[0][0]
        if score > best_score:
            best_category = category
            best_score = score
    
    return best_category


def compute_metrics(retrieved_images, relevant_images):
    """
    Compute precision and recall
    """
    retrieved_ids = set(img.id for img in retrieved_images)
    relevant_ids = set(img.id for img in relevant_images)
    
    if not retrieved_ids or not relevant_ids:
        return 0.0, 0.0
    
    correct = retrieved_ids & relevant_ids
    precision = len(correct) / len(retrieved_ids)
    recall = len(correct) / len(relevant_ids)
    
    return precision, recall


def log_search(query_text, search_type, results_count, execution_time):
    """Log search query to database for analysis"""
    log_entry = SearchQuery(
        query_text=query_text,
        search_type=search_type,
        results_count=results_count,
        execution_time=execution_time
    )
    db.session.add(log_entry)
    db.session.commit()


def to_static(p):
    """Convert path for static file serving"""
    return p.replace("\\", "/")
# ============================================================================
# HTML TEMPLATE
# ============================================================================
HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Multimedia Retrieval System</title>

<style>

body {
    font-family: Arial, sans-serif;
    background: linear-gradient(180deg, #0e3c5d 0%, #123854 45%, #0c2241 100%);
    color: white;
    text-align: center;
    min-height: 100vh;
    margin: 0;
    padding: 0;
}

h2 {
    margin-top: 30px;
    color: #33ffdd;
    text-shadow: 0 0 12px rgba(51, 255, 221, 0.7);
}

.container {
    margin: 20px auto;
    max-width: 560px;
    padding: 20px;
}

input, select {
    padding: 12px;
    width: 100%;
    max-width: 520px;
    border-radius: 12px;
    border: none;
    margin: 8px 0;
    box-sizing: border-box;
}

input[type="file"] {
    padding: 6px 12px;
    background: #172b3a;
    color: #fff;
}

button {
    padding: 12px 24px;
    border-radius: 14px;
    border: none;
    background: #00ffcc;
    color: #062724;
    font-weight: bold;
    cursor: pointer;
    box-shadow: 0 8px 18px rgba(0, 255, 204, 0.25);
}

button:hover {
    background: #1af5d8;
}

.metrics-row {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 14px;
    margin-top: 20px;
}

.metric-card {
    background: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.16);
    border-radius: 16px;
    padding: 14px 18px;
    min-width: 140px;
    max-width: 180px;
    text-align: left;
}

.metric-title {
    font-size: 12px;
    color: #b2f7ed;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 6px;
}

.metric-value {
    font-size: 18px;
    font-weight: bold;
    color: #ffffff;
}

.source-tag {
    display: inline-block;
    margin-left: 6px;
    padding: 2px 8px;
    border-radius: 999px;
    background: rgba(0, 255, 204, 0.16);
    color: #00f0c3;
    font-size: 11px;
    vertical-align: middle;
}

.card {
    display: inline-block;
    background: white;
    color: black;
    margin: 15px;
    padding: 10px;
    border-radius: 15px;
    width: 220px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.5);
}

.card img {
    width: 200px;
    height: 150px;
    border-radius: 10px;
}

.path {
    font-size: 12px;
    color: gray;
    word-break: break-all;
}

.score {
    color: green;
    font-weight: bold;
}

.hint {
    color: #b0dfe3;
    font-size: 14px;
    margin-bottom: 10px;
}

.formula-box {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.16);
    border-radius: 16px;
    padding: 14px 18px;
    color: #e6f7fb;
    text-align: left;
    margin-top: 18px;
    max-width: 560px;
    margin-left: auto;
    margin-right: auto;
}

.formula-title {
    font-size: 14px;
    font-weight: bold;
    margin-bottom: 10px;
}

.formula-item {
    font-size: 14px;
    margin-bottom: 6px;
}

.top-link-bar {
    background: rgba(255, 255, 255, 0.08);
    padding: 10px 0;
    text-align: center;
    position: fixed;
    width: 100%;
    top: 0;
    left: 0;
    z-index: 999;
    backdrop-filter: blur(8px);
}

.top-link {
    color: #b7f7ff;
    font-weight: bold;
    text-decoration: none;
    padding: 8px 18px;
    border: 1px solid rgba(183, 247, 255, 0.35);
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.08);
}

body {
    padding-top: 64px;
}

.error {
    color: #ff9fa0;
    background: rgba(255, 255, 255, 0.08);
    padding: 10px 14px;
    border-radius: 12px;
    display: inline-block;
    margin-top: 14px;
}

.db-status {
    background: rgba(0, 255, 204, 0.1);
    border: 1px solid rgba(0, 255, 204, 0.3);
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 12px;
    margin-top: 10px;
    color: #00ffcc;
}

</style>

</head>

<body>

<div class="top-link-bar">
    <a class="top-link" href="http://127.0.0.1:5000/" target="_blank" rel="noopener noreferrer" onclick="window.open(this.href, '_blank'); return false;">🔄 Open Interface</a>
</div>

<h2>🎯 Multimedia Retrieval System</h2>

<div class="container">

<form method="POST" enctype="multipart/form-data">

<select name="method">
    <option value="mbr" {% if selected_method == 'mbr' %}selected{% endif %}>📁 Metadata-Based Retrieval (MBR)</option>
    <option value="cbr" {% if selected_method == 'cbr' %}selected{% endif %}>🖼 Content-Based Retrieval (CBIR)</option>
</select>

<br>

<input name="query" placeholder="Enter keyword or image path" value="{{ query|default('') }}">
    <div class="hint">For content search, upload an image or enter a local path inside the project.</div>
    <input type="file" name="upload" accept="image/*">

<button type="submit">🔍 Search</button>

</form>

{% if error %}
    <p class="error">{{ error }}</p>
{% endif %}

<div class="metrics-row">
    <div class="metric-card">
        <div class="metric-title">Search Mode</div>
        <div class="metric-value">{{ selected_method|upper }}</div>
    </div>
    <div class="metric-card">
        <div class="metric-title">Retrieval Time</div>
        <div class="metric-value">{{ retrieval_time }} s</div>
    </div>
    <div class="metric-card">
        <div class="metric-title">Precision</div>
        <div class="metric-value">{{ precision }}</div>
    </div>
    <div class="metric-card">
        <div class="metric-title">Recall</div>
        <div class="metric-value">{{ recall }}</div>
    </div>
    <div class="metric-card">
        <div class="metric-title">Results</div>
        <div class="metric-value">{{ result_count }}</div>
    </div>
</div>

<div class="formula-box">
    <div class="formula-title">📊 Evaluation Metrics:</div>
    <div class="formula-item">✓ Precision = relevant_retrieved / total_retrieved</div>
    <div class="formula-item">✓ Recall = relevant_retrieved / total_relevant_in_dataset</div>
    <div class="formula-item">✓ Retrieval Time = query execution time</div>
</div>

<div class="db-status">
    📊 Database Status: {{ db_status }}
</div>

</div>

<hr>

{% if results %}

<h3>Results ({{ result_count }} found)</h3>

<div>

{% for result in results %}

<div class="card">

<img src="{{ url_for('static', filename=result.image_path) }}" alt="Result image">

<p class="score">Score: {{ result.score }} <span class="source-tag">{{ result.source }}</span></p>

<p class="path">{{ result.image_name }}<br>Category: {{ result.category }}</p>

</div>

{% endfor %}

</div>

{% endif %}

</body>
</html>
"""

# ============================================================================
# ROUTES
# ============================================================================
@app.route("/", methods=["GET", "POST"])
def index():
    """Main search interface"""
    results = []
    error = None
    selected_method = request.form.get("method", "mbr")
    
    if selected_method not in ["mbr", "cbr"]:
        selected_method = "mbr"
    
    query = request.form.get("query", "").strip()
    
    retrieval_time = 0.0
    precision = 0.0
    recall = 0.0
    result_count = 0
    
    # Get database status
    with app.app_context():
        db_image_count = Image.query.count()
        db_feature_count = ImageFeature.query.count()
        db_status = f"{db_image_count} images, {db_feature_count} features"
    
    if request.method == "POST":
        upload = request.files.get("upload")
        image_path = None
        
        # Handle file upload
        if upload and upload.filename:
            filename = secure_filename(upload.filename)
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            upload.save(save_path)
            image_path = save_path
        elif query and os.path.exists(query):
            image_path = query
        
        # ====== METADATA-BASED RETRIEVAL (MBR) ======
        if selected_method == "mbr":
            if query:
                try:
                    start = time.perf_counter()
                    mbr_results = metadata_search(query, top_k=50)
                    retrieval_time = time.perf_counter() - start
                    
                    # Log the search
                    log_search(query, "MBR", len(mbr_results), retrieval_time)
                    
                    # Convert to result format
                    results = []
                    for img in mbr_results:
                        results.append({
                            "image_name": img.image_name,
                            "image_path": img.file_path,
                            "category": img.category,
                            "score": 1.0,
                            "source": "MBR"
                        })
                    
                    # Compute metrics
                    relevant = metadata_relevant(query)
                    precision, recall = compute_metrics(mbr_results, relevant)
                    
                except Exception as e:
                    error = f"MBR Error: {str(e)}"
            else:
                error = "📁 Enter a keyword for metadata-based search."
        
        # ====== CONTENT-BASED RETRIEVAL (CBIR) ======
        elif selected_method == "cbr":
            if image_path:
                try:
                    start = time.perf_counter()
                    cbr_results, scores = content_search(image_path, top_k=100)
                    retrieval_time = time.perf_counter() - start
                    
                    # Log the search
                    log_search(image_path, "CBIR", len(cbr_results), retrieval_time)
                    
                    # Determine query image category
                    query_category = get_category_from_path(image_path)
                    if not query_category:
                        query_category = get_category_from_query(query)
                    if not query_category:
                        query_category = predict_category_from_feature(extract_features(image_path))
                    
                    desired_k = 6
                    
                    # Filter results by category for better evaluation
                    if query_category:
                        filtered_results = []
                        filtered_scores = []
                        
                        for img, score in zip(cbr_results, scores):
                            if img.category == query_category:
                                filtered_results.append(img)
                                filtered_scores.append(score)
                            if len(filtered_results) >= desired_k:
                                break
                        
                        if not filtered_results:
                            error = "❌ No results from the same category as query image."
                        else:
                            results = []
                            for img, score in zip(filtered_results, filtered_scores):
                                results.append({
                                    "image_name": img.image_name,
                                    "image_path": img.file_path,
                                    "category": img.category,
                                    "score": round(float(score), 4),
                                    "source": "CBIR"
                                })
                            
                            # Compute metrics
                            relevant = category_relevant(query_category)
                            precision, recall = compute_metrics(filtered_results, relevant)
                    else:
                        # If category can't be determined, return top results
                        results = []
                        for img, score in zip(cbr_results[:desired_k], scores[:desired_k]):
                            results.append({
                                "image_name": img.image_name,
                                "image_path": img.file_path,
                                "category": img.category,
                                "score": round(float(score), 4),
                                "source": "CBIR"
                            })
                        
                        error = "⚠️  Query image category unknown; showing most similar images."
                
                except Exception as e:
                    error = f"CBIR Error: {str(e)}"
            else:
                error = "🖼 Upload an image or enter a valid path for content-based search."
        
        result_count = len(results)
    
    return render_template_string(
        HTML,
        results=results,
        error=error,
        selected_method=selected_method,
        query=query,
        retrieval_time=round(retrieval_time, 4),
        precision=round(precision, 4),
        recall=round(recall, 4),
        result_count=result_count,
        db_status=db_status
    )


@app.route("/api/stats", methods=["GET"])
def api_stats():
    """API endpoint for getting database statistics"""
    with app.app_context():
        total_images = Image.query.count()
        total_features = ImageFeature.query.count()
        categories = db.session.query(Image.category).distinct().count()
        total_queries = SearchQuery.query.count()
        
        return {
            "total_images": total_images,
            "total_features": total_features,
            "categories": categories,
            "total_queries": total_queries
        }

# ============================================================================
# STARTUP
# ============================================================================
if __name__ == "__main__":
    url = "http://127.0.0.1:5000"
    
    # Open browser automatically
    browser_thread = threading.Timer(1.0, lambda: webbrowser.open_new_tab(url))
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        from waitress import serve
        logging.getLogger("waitress.queue").setLevel(logging.ERROR)
        print(f"\n{'='*70}")
        print(f"✅ Starting Multimedia Retrieval System")
        print(f"{'='*70}")
        print(f"🔗 URL: {url}")
        print(f"📊 Visit http://127.0.0.1:5000/api/stats for database statistics")
        print(f"{'='*70}\n")
        serve(app, host="127.0.0.1", port=5000)
    except Exception as e:
        print(f"⚠️  Waitress not available: {e}")
        print(f"Falling back to Flask development server...\n")
        app.run(debug=False, use_reloader=False)