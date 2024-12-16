# import seluruh library yang digunakan
from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2, numpy as np, io, base64
import joblib
from sklearn.cluster import DBSCAN

app = Flask(__name__)
CORS(app)

# Load model yang sudah dilatih dengan format joblib
clf = joblib.load('helmet_predictor_model.joblib')

# Memberikan ID ke label dan sebaliknya
label2id = {"0": 0, "helmet": 1}
id2label = {0: "head", 1: "helmet"}

# Fungsi untuk padding atau memotong deskriptor agar panjangnya seragam
def pad_or_truncate_descriptors(descriptors, max_descriptors=100):
    if descriptors.shape[0] > max_descriptors:
        return descriptors[:max_descriptors].flatten()
    else:
        padded = np.zeros((max_descriptors, descriptors.shape[1]))
        padded[:descriptors.shape[0]] = descriptors
        return padded.flatten()

# Fungsi untuk preprocessing gambar sesuai dengan yang sudah kita buat di file .ipynb
def preprocess_image(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Konversi warna ke RGB
    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)  # Konversi warna ke Grayscale
    image = cv2.GaussianBlur(image, (11, 11), 0)  # Mengaplikasikan Gaussian Blur
    image = cv2.equalizeHist(image)  # Menggunakan Histogram Equalization
    return image

# Ekstraksi fitur dari gambar menggunakan ORB dan AKAZE
def extract_features_from_image(image):
    orb = cv2.ORB_create()
    akaze = cv2.AKAZE_create()

    keypoints_orb, descriptors_orb = orb.detectAndCompute(image, None)
    keypoints_akaze, descriptors_akaze = akaze.detectAndCompute(image, None)

    # Kita menggabungkan keypoints dan deskriptor supaya menghasilkan representasi fitur gambar yang lebih kuat
    combined_keypoints = keypoints_orb + keypoints_akaze
    if descriptors_orb is None or descriptors_akaze is None:
        return None, None  # Jika tidak ada deskriptor, kembalikan None

    min_rows = min(descriptors_orb.shape[0], descriptors_akaze.shape[0])
    descriptors_orb = descriptors_orb[:min_rows]
    descriptors_akaze = descriptors_akaze[:min_rows]

    combined_descriptors = np.hstack((descriptors_orb, descriptors_akaze))

    return combined_descriptors, combined_keypoints

# Menghitung Intersection over Union (IoU) antara dua bounding boxes
def calculate_iou(box_a, box_p):
    x_min_inter = max(box_a[0], box_p[0])
    y_min_inter = max(box_a[1], box_p[1])
    x_max_inter = min(box_a[2], box_p[2])
    y_max_inter = min(box_a[3], box_p[3])

    inter_width = max(0, x_max_inter - x_min_inter)
    inter_height = max(0, y_max_inter - y_min_inter)
    area_inter = inter_width * inter_height

    area_a = (box_a[2] - box_a[0]) * (box_a[3] - box_a[1])
    area_p = (box_p[2] - box_p[0]) * (box_p[3] - box_p[1])

    area_union = area_a + area_p - area_inter
    iou = area_inter / area_union if area_union > 0 else 0
    return iou

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

        # Preprocessing gambar dengan memanggil def preprocess_image
        processed_image = preprocess_image(image)

        # Ekstraksi fitur dari gambar dengan memanggil def extract_features_from_image
        descriptors, keypoints = extract_features_from_image(processed_image)

        if descriptors is None:
            return jsonify({'error': 'Could not extract features from image'}), 400

        # Padding deskriptor agar ukurannya seragam dengan memanggil def pad_or_truncate_descriptors
        padded_descriptors = pad_or_truncate_descriptors(descriptors, max_descriptors=100)

        # Prediksi dengan model clf yang sudah di load
        prediction = clf.predict([padded_descriptors])
        predicted_class = id2label[prediction[0]]
        confidence = clf.predict_proba([padded_descriptors])[0][prediction[0]]

        # Clustering untuk bounding box dengan DBSCAN
        keypoint_coords = np.array([kp.pt for kp in keypoints])
        clustering = DBSCAN(eps=50, min_samples=3).fit(keypoint_coords)
        labels = clustering.labels_

        # Menghitung bounding box berdasarkan keypoint clusters
        generated_bboxes = []
        for label in np.unique(labels):
            if label == -1:  # Mengabaikan noise points
                continue

            cluster_points = keypoint_coords[labels == label]
            x_min = np.min(cluster_points[:, 0])
            x_max = np.max(cluster_points[:, 0])
            y_min = np.min(cluster_points[:, 1])
            y_max = np.max(cluster_points[:, 1])

            generated_bboxes.append([x_min, y_min, x_max, y_max])

        # Menggambar bounding box pada gambar
        img_with_bbox = cv2.cvtColor(processed_image, cv2.COLOR_GRAY2RGB)  # Konversi warna ke RGB untuk visualisasi
        for bbox in generated_bboxes:
            x_min, y_min, x_max, y_max = map(int, bbox)
            cv2.rectangle(img_with_bbox, (x_min, y_min), (x_max, y_max), (255, 0, 0), 2)  # Gambar bounding box

            # Kita bisa berikan label pada bounding box berupa predicted class dan confidence nya
            label_text = f"{predicted_class} ({confidence*100:.2f}%)"
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(img_with_bbox, label_text, (x_min, y_min - 10), font, 0.8, (0, 255, 0), 2)

        # Mengkodekan gambar dengan bounding box ke dalam base64 untuk dikembalikan ke frontend yang sudah dibuat
        _, buffer = cv2.imencode('.jpg', img_with_bbox)  # Menggunakan img_with_bbox yang sudah ada bounding box
        encoded_image = base64.b64encode(buffer).decode('utf-8')

        return jsonify({
            'predicted_class': predicted_class, # return hasil prediksi : head / helmet
            'confidence': confidence, # return persentase confidence
            'image': encoded_image,  # Gambar yang sudah digambar bounding box
            'bounding_boxes': generated_bboxes  # Mengembalikan koordinat bounding box
        })

    return jsonify({'error': 'Failed to process the file'}), 500

if __name__ == '__main__':
    app.run(debug=True)