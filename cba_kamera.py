import cv2

# Mencoba berbagai index untuk melihat kamera yang tersedia
for i in range(5):  # Coba dengan index 0 sampai 4
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Kamera ditemukan pada index {i}")
        cap.release()
    else:
        print(f"Tidak ada kamera di index {i}")
