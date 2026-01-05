### 🖼️ OCR Web Application (CNN + PyTesseract)

Aplikasi web OCR (Optical Character Recognition) yang menggabungkan algoritma  
CNN (Convolutional Neural Network) dan PyTesseract untuk mendeteksi serta mengekstrak teks dari sebuah gambar.

Pengguna dapat mengunggah gambar yang mengandung teks, kemudian sistem akan memproses dan menampilkan hasil teks yang dapat **disalin secara langsung**.


## 📋 Fitur Utama

### 📤 Upload Gambar
Mendukung format:
- PNG
- JPG
- JPEG
- BMP
- GIF

### 🧠 Multiple OCR Methods
- **PyTesseract** dengan berbagai konfigurasi OCR
- **CNN** untuk deteksi karakter individual
- **Deteksi baris teks otomatis**

### 🖼️ Preprocessing Otomatis
- Grayscale
- Thresholding
- Adaptive preprocessing untuk meningkatkan akurasi OCR

### 📄 Output Teks
- Hasil teks dapat **disalin**
- Menampilkan confidence hasil OCR

### 🌐 Antarmuka Responsif
- Dapat diakses dari desktop maupun mobile

### 🌍 Multi Language Support
- Bahasa Inggris
- Bahasa Indonesia

---

## 🔧 Prasyarat

### 1️⃣ Python
- Python **3.11.9** (direkomendasikan)
- Virtual environment *(opsional tetapi disarankan)*

---

### 2️⃣ Tesseract OCR
PyTesseract membutuhkan **Tesseract OCR Engine** yang terinstal di sistem.

#### 🪟 Windows
1. Download installer:

[https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)

```
2. Pilih versi **64-bit**
3. Install Tesseract
4. Catat lokasi instalasi (default):
```

C:\Program Files\Tesseract-OCR

````

#### 🐧 Linux (Ubuntu / Debian)
```bash
sudo apt update
sudo apt install tesseract-ocr
sudo apt install libtesseract-dev
````

#### 🍎 MacOS

```bash
brew install tesseract
```

---

### 3️⃣ Konfigurasi Environment Variable Tesseract

#### 🪟 Windows

Tambahkan path Tesseract ke **Environment Variables**:

1. Cari **Environment Variables** di Start Menu
2. Pilih **Edit the system environment variables**
3. Klik **Environment Variables**
4. Pada **System Variables**, edit **Path**
5. Tambahkan:

   ```
   C:\Program Files\Tesseract-OCR
   ```
6. Restart terminal / command prompt

**Alternatif (langsung di kode `app.py`):**

```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

---

#### 🐧 Linux / 🍎 MacOS

Biasanya otomatis terdeteksi. Jika tidak, atur manual di kode:

```python
# Linux
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

# MacOS
pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'
```

---

## ⚙️ Instalasi

### 1️⃣ Clone / Download Project

```bash
git clone https://github.com/arnugrha/ocrCnnApp.git
cd ocrCnnApp
```

---

### 2️⃣ Setup Virtual Environment (Opsional)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / MacOS
source venv/bin/activate
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🚀 Menjalankan Aplikasi

### 1️⃣ Jalankan Server Flask

```bash
python app.py
```

---

### 2️⃣ Akses Aplikasi

Buka browser dan kunjungi:

```
http://localhost:5000
```

---

## 🔌 Endpoint API

### 🏠 Halaman Utama

```
GET /
```

### ❤️ Health Check

```
GET /api/health
```

### 📤 Upload Gambar OCR

```
POST /api/upload
```

**Form Data:**

* `image` : File gambar
* `ocr_mode` : auto | enhanced | line_detection

---

## 📞 Support & Troubleshooting

Jika mengalami masalah:

* Pastikan semua dependencies terinstal dengan benar
* Pastikan Tesseract OCR sudah terpasang dan terdeteksi
* Periksa error log di terminal
* Gunakan endpoint `/api/health` untuk pengecekan sistem
* Buat issue di repository GitHub

---

## 👨‍💻 Author

**Arie Nugraha**
Mahasiswa S1 Informatika
