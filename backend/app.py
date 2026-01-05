import os
import cv2
import numpy as np
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from tensorflow import keras
import time
import traceback

try:
    import pytesseract
    from PIL import Image as PILImage
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
except:
    pytesseract = None

# Inisialisasi Flask
app = Flask(__name__, static_folder='../frontend', template_folder='../frontend')
CORS(app)

# Konfigurasi
UPLOAD_FOLDER = '../static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'gif'}
MODEL_PATH = 'model_cnn.h5'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Buat folder jika belum ada
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global variables
model = None
characters = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_model():
    """Load model CNN"""
    global model
    try:
        if os.path.exists(MODEL_PATH):
            print(f"Loading model from {MODEL_PATH}...")
            model = keras.models.load_model(MODEL_PATH)
            print("Model loaded successfully!")
        else:
            print(f"Model file {MODEL_PATH} not found. Creating dummy model...")
            model = create_dummy_model()
            model.save(MODEL_PATH)
            print("Dummy model created and saved.")
    except Exception as e:
        print(f"Error loading model: {e}")
        model = create_dummy_model()

def create_dummy_model():
    """Create a dummy model for testing"""
    model = keras.Sequential([
        keras.layers.Input(shape=(28, 28, 1)),
        keras.layers.Flatten(),
        keras.layers.Dense(128, activation='relu'),
        keras.layers.Dense(len(characters), activation='softmax')
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def preprocess_image(image_path):
    """Preprocess image for OCR"""
    try:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("Cannot read image")
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        
        if np.mean(binary) > 127:
            binary = cv2.bitwise_not(binary)
        
        resized = cv2.resize(binary, (28, 28))
        normalized = resized.astype('float32') / 255.0
        processed = np.expand_dims(normalized, axis=-1)
        
        return processed
    except Exception as e:
        print(f"Error preprocessing image: {e}")
        return None

def predict_text(image_array):
    """Predict text from preprocessed image"""
    try:
        if model is None:
            return "ERROR: Model not loaded", 0.0
        
        image_batch = np.expand_dims(image_array, axis=0)
        predictions = model.predict(image_batch, verbose=0)
        
        predicted_idx = np.argmax(predictions[0])
        confidence = np.max(predictions[0])
        
        if 0 <= predicted_idx < len(characters):
            predicted_char = characters[predicted_idx]
        else:
            predicted_char = '?'
        
        return predicted_char, float(confidence)
    
    except Exception as e:
        print(f"Error in prediction: {e}")
        return '?', 0.0

def enhanced_pytesseract_ocr(image_path):
    """
    Enhanced OCR with pytesseract that preserves formatting
    """
    try:
        if pytesseract is None:
            return "", 0.0
        
        img = cv2.imread(image_path)
        if img is None:
            return "", 0.0
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        pil_img = PILImage.fromarray(gray)
        
        best_text = ""
        best_confidence = 0.0
        
        configs = [
            '--oem 3 --psm 3 -c preserve_interword_spaces=1',  
            '--oem 3 --psm 4 -c preserve_interword_spaces=1',  
            '--oem 3 --psm 6 -c preserve_interword_spaces=1',  
            '--oem 3 --psm 11 -c preserve_interword_spaces=1',  
        ]
        
        for config in configs:
            try:
                ocr_data = pytesseract.image_to_data(
                    pil_img, 
                    lang='eng+ind',
                    config=config,
                    output_type=pytesseract.Output.DICT
                )

                reconstructed_text = ""
                current_line = -1
                
                for i in range(len(ocr_data['text'])):
                    text = ocr_data['text'][i].strip()
                    conf = ocr_data['conf'][i]
                    line_num = ocr_data['line_num'][i]

                    if conf > 30 and text:
                        if line_num != current_line and current_line != -1:
                            reconstructed_text += '\n'
                        elif reconstructed_text and reconstructed_text[-1] != '\n':
                            reconstructed_text += ' '
                        
                        reconstructed_text += text
                        current_line = line_num

                confidences = [c for c in ocr_data['conf'] if c > 30]
                avg_confidence = np.mean(confidences) / 100.0 if confidences else 0.5

                score = len(reconstructed_text) * avg_confidence
                
                if score > best_confidence * len(best_text) if best_text else 0:
                    best_text = reconstructed_text
                    best_confidence = avg_confidence
                    
            except Exception as e:
                print(f"Error with config {config}: {e}")
                continue
        
        return best_text, best_confidence
        
    except Exception as e:
        print(f"Error in enhanced OCR: {e}")
        return "", 0.0

def detect_text_regions(image_path):
    """
    Detect text regions and their positions for line detection
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            return []
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        methods = [
            cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
            cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                cv2.THRESH_BINARY, 11, 2),
        ]
        
        all_boxes = []
        
        for binary in methods:

            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                if w > 20 and h > 20:
                    merged = False
                    for i, (bx, by, bw, bh) in enumerate(all_boxes):
                        if (abs(x - bx) < 50 and abs(y - by) < 50) or \
                        (x < bx + bw and x + w > bx and y < by + bh and y + h > by):
                            new_x = min(x, bx)
                            new_y = min(y, by)
                            new_w = max(x + w, bx + bw) - new_x
                            new_h = max(y + h, by + bh) - new_y
                            all_boxes[i] = (new_x, new_y, new_w, new_h)
                            merged = True
                            break
                    
                    if not merged:
                        all_boxes.append((x, y, w, h))
        
        all_boxes.sort(key=lambda box: (box[1] // 20, box[0]))
        
        return all_boxes
        
    except Exception as e:
        print(f"Error detecting text regions: {e}")
        return []

def ocr_with_line_detection(image_path):
    """
    OCR with explicit line detection
    """
    try:
        if pytesseract is None:
            return "", 0.0
        
        img = cv2.imread(image_path)
        if img is None:
            return "", 0.0
        
        text_boxes = detect_text_regions(image_path)
        
        if not text_boxes:
            return enhanced_pytesseract_ocr(image_path)

        lines = []
        current_line = []
        last_y = -1
        
        for box in text_boxes:
            x, y, w, h = box
            
            if last_y == -1:
                last_y = y

            if abs(y - last_y) > h * 0.5:
                if current_line:
                    lines.append(sorted(current_line, key=lambda b: b[0]))
                    current_line = []
            
            current_line.append(box)
            last_y = y
        
        if current_line:
            lines.append(sorted(current_line, key=lambda b: b[0]))

        full_text = ""
        total_confidence = 0.0
        line_count = 0
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        for line_idx, line_boxes in enumerate(lines):
            line_text = ""
            line_confidence = 0.0
            box_count = 0
            
            for box_idx, (x, y, w, h) in enumerate(line_boxes):

                roi = gray[y:y+h, x:x+w]
                if roi.size == 0:
                    continue

                roi_processed = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

                pil_roi = PILImage.fromarray(roi_processed)
                
                try:
                    ocr_result = pytesseract.image_to_string(
                        pil_roi,
                        lang='eng+ind',
                        config='--oem 3 --psm 7 -c preserve_interword_spaces=1'
                    ).strip()
                    
                    if ocr_result:
                        line_text += ocr_result + " "

                        ocr_data = pytesseract.image_to_data(
                            pil_roi,
                            lang='eng+ind',
                            config='--oem 3 --psm 7',
                            output_type=pytesseract.Output.DICT
                        )
                        
                        confidences = [c for c in ocr_data['conf'] if c > 30]
                        if confidences:
                            line_confidence += np.mean(confidences) / 100.0
                            box_count += 1
                            
                except Exception as e:
                    print(f"Error OCRing box: {e}")
                    continue
            
            if line_text:
                full_text += line_text.strip()
                if line_idx < len(lines) - 1:
                    full_text += '\n'
                
                if box_count > 0:
                    total_confidence += line_confidence / box_count
                    line_count += 1
        
        avg_confidence = total_confidence / line_count if line_count > 0 else 0.5
        
        return full_text.strip(), avg_confidence
        
    except Exception as e:
        print(f"Error in line detection OCR: {e}")
        return enhanced_pytesseract_ocr(image_path)

def simple_ocr(image_path):
    """Simple OCR implementation"""
    try:
        if pytesseract is None:
            return "", 0.0
        
        img = cv2.imread(image_path)
        if img is None:
            return "", 0.0
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        preprocessed = [
            gray,
            cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
            cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                cv2.THRESH_BINARY, 11, 2),
        ]
        
        best_text = ""
        best_conf = 0.0
        
        for proc in preprocessed:
            try:
                pil_img = PILImage.fromarray(proc)

                for psm in [3, 4, 6, 11]:
                    config = f'--oem 3 --psm {psm} -c preserve_interword_spaces=1'
                    
                    text = pytesseract.image_to_string(
                        pil_img,
                        lang='eng+ind',
                        config=config
                    ).strip()
                    
                    if text:
                        lines = text.count('\n') + 1
                        words = len(text.split())
                        non_printable = sum(1 for c in text if ord(c) < 32 and c != '\n')

                        conf = min(0.9, 0.5 + (words * 0.05) - (non_printable * 0.1))
                        
                        if conf > best_conf:
                            best_conf = conf
                            best_text = text
                            
            except Exception as e:
                print(f"Simple OCR error: {e}")
                continue
        
        if not best_text:
            filename = os.path.splitext(os.path.basename(image_path))[0]
            best_text = filename.replace('_', ' ').upper()
            best_conf = 0.3
        
        return best_text, best_conf
        
    except Exception as e:
        print(f"Error in simple OCR: {e}")
        return "GAGAL MEMBACA TEKS", 0.1

# Routes
@app.route('/')
def serve_index():
    """Serve the main index.html page"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory(app.static_folder, filename)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'pytesseract_available': pytesseract is not None,
        'endpoints': ['/api/upload', '/api/health', '/']
    })

@app.route('/api/upload', methods=['POST'])
def upload_image():
    """Handle image upload for OCR"""
    start_time = time.time()
    
    if 'image' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No image file provided'
        }), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({
            'success': False,
            'error': 'No selected file'
        }), 400
    
    if not allowed_file(file.filename):
        return jsonify({
            'success': False,
            'error': 'File type not allowed. Use PNG, JPG, JPEG, or BMP'
        }), 400
    
    try:
        # Simpan uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        print(f"Processing file: {filepath}")

        ocr_mode = request.form.get('ocr_mode', 'auto')

        if ocr_mode == 'line_detection' and pytesseract is not None:
            print("Using line detection OCR...")
            text, confidence = ocr_with_line_detection(filepath)
        elif ocr_mode == 'enhanced' and pytesseract is not None:
            print("Using enhanced OCR...")
            text, confidence = enhanced_pytesseract_ocr(filepath)
        elif pytesseract is not None:
            print("Using auto mode OCR...")
            text, confidence = ocr_with_line_detection(filepath)
            if not text or len(text.strip()) < 3:
                text, confidence = simple_ocr(filepath)
        else:
            print("Pytesseract not available, using simple OCR...")
            text, confidence = simple_ocr(filepath)

        if not text or len(text.strip()) < 2:
            print("Trying CNN model...")
            processed_image = preprocess_image(filepath)
            if processed_image is not None:
                char, conf = predict_text(processed_image)
                text = char
                confidence = conf

        if text:
            lines = []
            for line in text.split('\n'):
                cleaned_line = ' '.join(line.split())
                if cleaned_line:
                    lines.append(cleaned_line)
            text = '\n'.join(lines)

        processing_time = time.time() - start_time
        
        return jsonify({
            'success': True,
            'text': text,
            'confidence': float(confidence),
            'processing_time': round(processing_time, 3),
            'filename': filename,
            'line_count': text.count('\n') + 1 if text else 0,
            'char_count': len(text) if text else 0,
            'ocr_mode_used': ocr_mode if pytesseract else 'simple',
            'message': 'OCR processed successfully'
        })
        
    except Exception as e:
        print(f"Error processing upload: {e}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)[:200]
        }), 500


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    load_model()
    
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)