import cv2
import numpy as np
from PIL import Image
import io

def extract_dominant_colors(image: Image.Image, k: int = 5):
    """
    Extracts the dominant colors from an image using KMeans clustering.
    Returns a list of hex color codes.
    """
    # Convert PIL Image to RGB and then to a numpy array
    image = image.convert('RGB')
    data = np.array(image)
    
    # Reshape the data to a list of pixels
    pixels = data.reshape(-1, 3)
    
    # Convert to float32
    pixels = np.float32(pixels)
    
    # Define criteria and apply kmeans()
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    ret, label, center = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    
    # Convert back into uint8, and make original image
    center = np.uint8(center)
    
    # Get the dominant colors as hex strings
    hex_colors = []
    for color in center:
        hex_color = "#{:02x}{:02x}{:02x}".format(color[0], color[1], color[2])
        hex_colors.append(hex_color)
        
    return hex_colors

def basic_image_heuristics(image_bytes: bytes) -> dict:
    """
    Performs basic heuristics on the uploaded image using OpenCV/PIL.
    """
    image = Image.open(io.BytesIO(image_bytes))
    
    # Extract dominant colors
    dominant_colors = extract_dominant_colors(image, k=5)
    
    # Calculate average brightness to determine if it's generally a "light" or "dark" UI
    grayscale_image = image.convert("L")
    stat = np.array(grayscale_image)
    avg_brightness = np.mean(stat)
    mode = "Light" if avg_brightness > 127 else "Dark"

    width, height = image.size
    
    return {
        "dimensions": f"{width}x{height}",
        "orientation": "Landscape" if width > height else "Portrait",
        "dominant_colors": dominant_colors,
        "theme_estimation": mode
    }
