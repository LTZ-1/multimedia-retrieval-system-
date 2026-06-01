import cv2
import numpy as np
import os

def extract_features(image_path):

    # 🔴 FIX 1: check empty input
    if image_path is None or image_path.strip() == "":
        raise ValueError("Empty image path received")

    # 🔴 FIX 2: normalize path
    image_path = image_path.replace("\\", "/")

    # 🔴 FIX 3: check file exists
    if not os.path.exists(image_path):
        raise ValueError(f"Image not found: {image_path}")

    image = cv2.imread(image_path)

    # 🔴 FIX 4: check image loaded
    if image is None:
        raise ValueError(f"Cannot load image: {image_path}")

    image = cv2.resize(image, (256, 256))

    histogram = cv2.calcHist(
        [image],
        [0, 1, 2],
        None,
        [8, 8, 8],
        [0, 256, 0, 256, 0, 256]
    )

    cv2.normalize(histogram, histogram)

    return histogram.flatten()