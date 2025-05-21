import cv2
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np

# Load model yang sudah disimpan
model_path = "model_cabai.h5"
model = tf.keras.models.load_model(model_path)

# Nama kelas sesuai dataset saat training
class_names = ["matang", "mentah", "setengah_matang"]

def predict_image(img):
    # Pre-processing gambar untuk model
    img_resized = cv2.resize(img, (224, 224))
    img_array = image.img_to_array(img_resized)
    img_array = np.expand_dims(img_array, axis=0)  # Tambahkan batch dimension
    img_array /= 255.0  # Normalisasi

    # Prediksi
    predictions = model.predict(img_array)
    predicted_class = np.argmax(predictions)  # Ambil kelas dengan probabilitas tertinggi
    confidence = np.max(predictions)  # Ambil nilai probabilitas tertinggi

    return class_names[predicted_class], confidence

# Buka kamera
cap = cv2.VideoCapture(1)  # Ganti dengan index kamera eksternal Anda

while True:
    ret, frame = cap.read()  # Tangkap frame
    if not ret:
        print("Gagal menangkap frame!")
        break

    # Konversi gambar ke HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Tentukan rentang warna untuk cabai merah dan hijau
    # Cabai merah
    lower_red = np.array([0, 120, 70])
    upper_red = np.array([10, 255, 255])
    red_mask = cv2.inRange(hsv, lower_red, upper_red)

    # Cabai hijau
    lower_green = np.array([35, 40, 40])
    upper_green = np.array([85, 255, 255])
    green_mask = cv2.inRange(hsv, lower_green, upper_green)

    # Gabungkan mask merah dan hijau
    mask = cv2.bitwise_or(red_mask, green_mask)

    # Cari kontur pada mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Jika ada kontur (yaitu cabai terdeteksi)
    if contours:
        # Dapatkan kontur terbesar, ini adalah cabai terbesar yang terdeteksi
        largest_contour = max(contours, key=cv2.contourArea)

        # Buat bounding box di sekitar kontur terbesar
        x, y, w, h = cv2.boundingRect(largest_contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Crop gambar berdasarkan bounding box untuk prediksi
        cropped_image = frame[y:y + h, x:x + w]

        # Prediksi cabai pada gambar yang terdeteksi
        predicted_class, confidence = predict_image(cropped_image)

        # Tampilkan prediksi di atas frame
        cv2.putText(frame, f"{predicted_class} ({confidence*100:.2f}%)", 
                    (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Tampilkan gambar menggunakan OpenCV (cv2.imshow)
    cv2.imshow("Deteksi Cabai", frame)

    # Tekan 'q' untuk keluar dari loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Lepaskan kamera dan tutup jendela setelah keluar dari loop
cap.release()
cv2.destroyAllWindows()
