from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2, numpy as np, io, base64

app = Flask(__name__)
CORS(app)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file:
        file_bytes = np.frombuffer(file.read(), np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        processed_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        _, buffer = cv2.imencode('.jpg', processed_image)
        encoded_image = base64.b64encode(buffer).decode('utf-8') #ini base64
        predicted_class = "Helmet Detected"  #contoh aja
        confidence = 0.95  # contoh aja

        return jsonify({
            'predicted_class': predicted_class,
            'confidence': confidence,
            'image': encoded_image
        })

    return jsonify({'error': 'Failed to process the file'}), 500

if __name__ == '__main__':
    app.run(debug=True)

