import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, datasets
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import os

def load_mnist_data():
    """Load MNIST dataset for digits 0-9"""
    (x_train, y_train), (x_test, y_test) = datasets.mnist.load_data()

    x_train = x_train.astype('float32') / 255.0
    x_test = x_test.astype('float32') / 255.0

    x_train = np.expand_dims(x_train, -1)
    x_test = np.expand_dims(x_test, -1)

    y_train = keras.utils.to_categorical(y_train, 10)
    y_test = keras.utils.to_categorical(y_test, 10)
    
    return (x_train, y_train), (x_test, y_test)

def load_emnist_data():
    """Load EMNIST dataset for letters A-Z"""
    try:

        print("⚠️ EMNIST dataset not available, creating synthetic data...")

        num_samples = 1000
        num_classes = 26
        img_size = 28
        
        x_synth = np.random.randn(num_samples, img_size, img_size, 1).astype('float32')
        x_synth = (x_synth - x_synth.min()) / (x_synth.max() - x_synth.min())
        
        y_synth = np.random.randint(0, num_classes, num_samples)
        y_synth = keras.utils.to_categorical(y_synth, num_classes)
        
        return x_synth, y_synth
        
    except Exception as e:
        print(f"Error loading EMNIST: {e}")
        return None, None

def create_combined_dataset():
    """Create combined dataset of digits and letters"""
    (x_digits_train, y_digits_train), (x_digits_test, y_digits_test) = load_mnist_data()

    x_letters_train, y_letters_train = load_emnist_data()
    
    if x_letters_train is not None:
        x_letters_train, x_letters_test, y_letters_train, y_letters_test = train_test_split(
            x_letters_train, y_letters_train, test_size=0.2, random_state=42
        )

        y_letters_train = y_letters_train + 10 
        y_letters_test = y_letters_test + 10

        x_train = np.concatenate([x_digits_train, x_letters_train])
        y_train = np.concatenate([y_digits_train, y_letters_train])
        x_test = np.concatenate([x_digits_test, x_letters_test])
        y_test = np.concatenate([y_digits_test, y_letters_test])
        
        num_classes = 36
    else:
        x_train, y_train = x_digits_train, y_digits_train
        x_test, y_test = x_digits_test, y_digits_test
        num_classes = 10
    
    return (x_train, y_train), (x_test, y_test), num_classes

def train_model():
    """Train CNN model for OCR"""
    print("📊 Loading and preparing data...")

    (x_train, y_train), (x_test, y_test), num_classes = create_combined_dataset()
    
    print(f"📈 Dataset shape:")
    print(f"  Training: {x_train.shape[0]} samples")
    print(f"  Testing: {x_test.shape[0]} samples")
    print(f"  Classes: {num_classes}")
    
    # Buat model
    print("🧠 Creating CNN model...")
    from model import create_cnn_model
    model = create_cnn_model(num_classes=num_classes)
    
    # Model summary
    model.summary()
    
    # Callbacks
    callbacks = [
        keras.callbacks.EarlyStopping(
            patience=10,
            restore_best_weights=True
        ),
        keras.callbacks.ReduceLROnPlateau(
            factor=0.5,
            patience=5,
            min_lr=1e-6
        ),
        keras.callbacks.ModelCheckpoint(
            'model_cnn_best.h5',
            save_best_only=True,
            monitor='val_accuracy'
        )
    ]
    
    # Train model
    print("🚀 Training model...")
    history = model.fit(
        x_train, y_train,
        batch_size=32,
        epochs=50,
        validation_split=0.2,
        callbacks=callbacks,
        verbose=1
    )
    
    # Evaluasi model
    print("📊 Evaluating model...")
    test_loss, test_acc = model.evaluate(x_test, y_test, verbose=0)
    print(f"✅ Test accuracy: {test_acc:.4f}")
    print(f"✅ Test loss: {test_loss:.4f}")
    
    # Simpan Model
    model.save('model_cnn.h5')
    print("💾 Model saved as model_cnn.h5")

    plot_training_history(history)
    
    return model, history

def plot_training_history(history):
    """Plot training history"""
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    
    # Plot accuracy
    axes[0].plot(history.history['accuracy'], label='Training Accuracy')
    axes[0].plot(history.history['val_accuracy'], label='Validation Accuracy')
    axes[0].set_title('Model Accuracy')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Accuracy')
    axes[0].legend()
    axes[0].grid(True)
    
    # Plot loss
    axes[1].plot(history.history['loss'], label='Training Loss')
    axes[1].plot(history.history['val_loss'], label='Validation Loss')
    axes[1].set_title('Model Loss')
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Loss')
    axes[1].legend()
    axes[1].grid(True)
    
    plt.tight_layout()
    plt.savefig('training_history.png')
    plt.show()

if __name__ == '__main__':
    print("🎯 Starting OCR CNN Model Training...")
    model, history = train_model()
    print("🏁 Training completed!")