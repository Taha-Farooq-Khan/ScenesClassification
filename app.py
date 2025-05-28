from flask import Flask, request, render_template, jsonify
import tensorflow as tf
from PIL import Image
import numpy as np
import requests
from io import BytesIO
import os

app = Flask(__name__)

# Load the trained CNN model
model = tf.keras.models.load_model('models/cnn_model.h5')

# Define class labels
class_labels = ['buildings', 'forest', 'glacier', 'mountain', 'sea', 'street']

# Image preprocessing function
def preprocess_image(image, target_size=(150, 150)):
    # Resize image to the target size expected by the model
    image = image.resize(target_size)
    # Convert image to numpy array and normalize
    image_array = np.array(image) / 255.0
    # Add batch dimension
    image_array = np.expand_dims(image_array, axis=0)
    return image_array

# Function to download image from URL
def download_image(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content)).convert('RGB')
        return image, None
    except Exception as e:
        return None, str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        image = None
        # Check if an image file was uploaded
        if 'image' in request.files and request.files['image'].filename != '':
            file = request.files['image']
            image = Image.open(file.stream).convert('RGB')
        # Check if an image URL was provided
        elif 'image_url' in request.form and request.form['image_url']:
            url = request.form['image_url']
            image, error = download_image(url)
            if image is None:
                return jsonify({'error': f'Failed to download image: {error}'}), 400
        else:
            return jsonify({'error': 'No image or URL provided'}), 400

        # Preprocess the image
        processed_image = preprocess_image(image)

        # Make prediction
        predictions = model.predict(processed_image)
        predicted_class = class_labels[np.argmax(predictions[0])]

        return jsonify({
            'prediction': predicted_class
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    app.run(debug=True)