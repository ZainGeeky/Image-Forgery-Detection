from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model
import numpy as np
import cv2

def detect_splicing(image_path):
    # Load the model
    model = load_model('splicing_detect.h5')

    # Load and preprocess the image
    image_size = (256, 256)
    img = image.load_img(image_path, target_size=image_size)
    img_array = image.img_to_array(img)
    img_array = img_array / 255.0  # Normalize the image

    # Expand the dimensions to match the input shape of the model
    img_array = np.expand_dims(img_array, axis=0)

    # Make predictions
    predictions = model.predict(img_array)
    probability_spliced = predictions[0][0]
    threshold = 0.6  # Adjust the threshold as needed

    return probability_spliced