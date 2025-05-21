import tensorflow as tf
from tensorflow.keras.preprocessing import image_dataset_from_directory

dataset_path = "dataset"  # Ganti dengan path ke dataset
batch_size = 32
img_size = (224, 224)

train_dataset = image_dataset_from_directory(
    dataset_path,
    shuffle=True,
    image_size=img_size,
    batch_size=batch_size
)

# Melihat class names
class_names = train_dataset.class_names
print(class_names)  # Output: ['matang', 'mentah', 'setengah_matang']
