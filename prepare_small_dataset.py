import os
import shutil
import random

# ✅ CORRECT ROOT PATH (VERY IMPORTANT)
source_dataset = "101_ObjectCategories/caltech-101/101_ObjectCategories"

target_dataset = "small_dataset"

selected_categories = [
    "airplanes",
    "bonsai",
    "car_side",
    "faces",
    "watch"
]

os.makedirs(target_dataset, exist_ok=True)

for category in selected_categories:

    source_folder = os.path.join(source_dataset, category)
    target_folder = os.path.join(target_dataset, category)

    os.makedirs(target_folder, exist_ok=True)

    if not os.path.exists(source_folder):
        print(f"❌ Missing: {source_folder}")
        continue

    images = [
        img for img in os.listdir(source_folder)
        if img.lower().endswith(('.jpg', '.jpeg', '.png'))
    ]

    print(f"✅ {category}: {len(images)} images found")

    selected_images = random.sample(images, min(50, len(images)))

    for img in selected_images:
        shutil.copy(
            os.path.join(source_folder, img),
            os.path.join(target_folder, img)
        )

print("\n🎉 Small dataset created successfully.")