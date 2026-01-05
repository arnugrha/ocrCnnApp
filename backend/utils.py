import cv2
import numpy as np
import os

def preprocess_for_ocr(image_path):
    """
    Simple preprocessing for OCR
    """
    try:
        # Baca gambar
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Cannot read image from {image_path}")
        
        # Convert ke grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Menerapkan Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Menerapkan adaptive threshold
        binary = cv2.adaptiveThreshold(
            blurred, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Balikkan jika diperlukan
        if np.mean(binary) > 127:
            binary = cv2.bitwise_not(binary)
        
        # Menyimpan gambar yang diproses untuk debugging
        debug_path = image_path.replace('.', '_processed.')
        cv2.imwrite(debug_path, binary)
        print(f"Processed image saved: {debug_path}")
        
        return binary
    
    except Exception as e:
        print(f"Error in preprocessing: {e}")
        return None

def segment_characters(image):
    """
    Simple character segmentation
    """
    try:
        # Find contours
        contours, _ = cv2.findContours(
            image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        characters = []
        bounding_boxes = []
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            if w > 10 and h > 10:
                char_img = image[y:y+h, x:x+w]
                
                char_resized = cv2.resize(char_img, (28, 28))
                
                char_normalized = char_resized.astype('float32') / 255.0
                
                characters.append(char_normalized)
                bounding_boxes.append((x, y, w, h))
        
        return characters, bounding_boxes
    
    except Exception as e:
        print(f"Error in character segmentation: {e}")
        return [], []