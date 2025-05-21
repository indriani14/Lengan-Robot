import os
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from PIL import Image
import matplotlib.pyplot as plt

# Path dataset
dataset_path = "dataset"  # Sesuaikan dengan lokasi dataset

# --- 1. CEK DAN KONVERSI GAMBAR ---
def check_and_convert_images(dataset_path):
    for category in os.listdir(dataset_path):
        if category not in ["matang", "mentah", "setengah_matang"]:
            continue  # Skip kategori selain "matang" dan "mentah"
        
        category_path = os.path.join(dataset_path, category)

        if os.path.isdir(category_path):  # Pastikan ini folder
            for img_name in os.listdir(category_path):
                img_path = os.path.join(category_path, img_name)

                try:
                    with Image.open(img_path) as img:
                        # Cek apakah gambar kosong atau tidak valid
                        if img.size == (0, 0):
                            print(f"Gambar kosong: {img_path}. Menghapus...")
                            os.remove(img_path)
                            continue

                        # Jika format tidak PNG atau JPEG, konversi ke PNG
                        if img.format not in ["JPEG", "PNG"]:
                            img = img.convert("RGB")
                            new_path = img_path.rsplit(".", 1)[0] + ".png"
                            img.save(new_path, "PNG")
                            os.remove(img_path)  # Hapus file lama
                            print(f"File dikonversi ke PNG: {img_path} -> {new_path}")

                except Exception as e:
                    print(f"File tidak valid atau rusak: {img_path}. Error: {e}")
                    os.remove(img_path)

# Jalankan pengecekan gambar
check_and_convert_images(dataset_path)

# --- 2. LOAD DATASET ---
batch_size = 32
img_size = (224, 224)
epochs = 4

train_dataset = tf.keras.preprocessing.image_dataset_from_directory(
    dataset_path,
    shuffle=True,
    image_size=img_size,
    batch_size=batch_size,
    validation_split=0.2,
    subset="training",
    seed=123
)

val_dataset = tf.keras.preprocessing.image_dataset_from_directory(
    dataset_path,
    shuffle=True,
    image_size=img_size,
    batch_size=batch_size,
    validation_split=0.2,
    subset="validation",
    seed=123
)

# Class names
class_names = train_dataset.class_names
print("Class Names:", class_names)

# Normalisasi gambar
normalization_layer = layers.Rescaling(1./255)
train_dataset = train_dataset.map(lambda x, y: (normalization_layer(x), y))
val_dataset = val_dataset.map(lambda x, y: (normalization_layer(x), y))

# --- 3. MODEL CNN ---
model = keras.Sequential([
    layers.Conv2D(32, (3,3), activation='relu', input_shape=(224, 224, 3)),
    layers.MaxPooling2D(2,2),
    
    layers.Conv2D(64, (3,3), activation='relu'),
    layers.MaxPooling2D(2,2),

    layers.Conv2D(128, (3,3), activation='relu'),
    layers.MaxPooling2D(2,2),

    layers.Flatten(),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.5),  # Mengurangi overfitting
    layers.Dense(3, activation='softmax')  # Hanya 2 kelas: matang dan mentah
])

# Compile model
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# --- 4. TRAINING MODEL ---
history = model.fit(train_dataset, validation_data=val_dataset, epochs=epochs)

# --- 5. PLOT HASIL TRAINING ---
plt.plot(history.history['accuracy'], label='Train Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()
plt.show()

# --- 6. SIMPAN MODEL ---
model.save("model_cabai.h5")
print("Model telah disimpan sebagai 'model_cabai.h5'")
