import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import cv2
import os

def create_cnn_model(input_shape=(28, 28, 1), num_classes=36):
    """
    Create a CNN model for character recognition
    Supports 0-9 digits and A-Z letters (total 36 classes)
    """
    model = keras.Sequential([
        layers.Conv2D(32, (3, 3), activation='relu', padding='same', input_shape=input_shape),
        layers.BatchNormalization(),
        layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        layers.Flatten(),
        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(128, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(num_classes, activation='softmax')
    ])
    
    # Compile model
    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model

def load_model(model_path='model_cnn.h5'):
    """Load trained CNN model"""
    if os.path.exists(model_path):
        try:
            model = keras.models.load_model(model_path)
            print(f"✅ Model loaded from {model_path}")
            return model
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return None
    else:
        print(f"⚠️ Model file not found at {model_path}")
        print("📝 Creating a new model...")
        return create_cnn_model()

def predict_character(model, char_image):
    """
    Predict character from image using CNN model
    
    Args:
        model: Trained CNN model
        char_image: Preprocessed character image (grayscale, 28x28)
    
    Returns:
        tuple: (predicted_character, confidence)
    """
    try:
        if char_image.shape != (28, 28):
            char_image = cv2.resize(char_image, (28, 28))
        
        char_image = char_image.astype('float32') / 255.0
        
        char_image = np.expand_dims(char_image, axis=(0, -1))
        
        predictions = model.predict(char_image, verbose=0)

        predicted_class = np.argmax(predictions[0])
        confidence = np.max(predictions[0])

        character = class_to_char(predicted_class)
        
        return character, float(confidence)
        
    except Exception as e:
        print(f"Error in prediction: {e}")
        return '?', 0.0

def class_to_char(class_index):
    """
    Map class index to character
    0-9: digits 0-9
    10-35: letters A-Z
    """
    if 0 <= class_index <= 9:
        return str(class_index)  # Digits 0-9
    elif 10 <= class_index <= 35:
        return chr(ord('A') + class_index - 10)
    else:
        return '?'
    
def get_prediction_fallback(image):
    """Fallback prediction when model fails"""
    image_mean = np.mean(image)
    
    if image_mean > 0.7:
        return 'A', 0.8
    elif image_mean > 0.5:
        return 'B', 0.7
    else:
        return 'C', 0.6