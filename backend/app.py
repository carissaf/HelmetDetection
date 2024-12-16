from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np, io, base64, joblib, cv2, matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN

app = Flask(__name__)
CORS(app)

# Load model yang sudah di train
clf = joblib.load('helmet_predictor_model.joblib')

# Initialize setiap label (label encoding)
label2id = {"0": 0, "helmet": 1}
id2label = {0: "head", 1: "helmet"}

# Menggunakan ORB dan AKAZE sebagai feature detectors
orb = cv2.ORB_create()
akaze = cv2.AKAZE_create()

# Membuat fungsi untuk combine keypoints
def combine_keypoints(keypoints1, keypoints2, threshold=5):
    combined = list(keypoints1)
    for kp2 in keypoints2:
        if not any(cv2.norm(kp1.pt, kp2.pt) < threshold for kp1 in combined):
            combined.append(kp2)
    return combined

# Membuat fungsi menyeragamkan deskriptor
def pad_or_truncate_descriptors(descriptors, max_descriptors=100):
    if descriptors.shape[0] > max_descriptors:
        return descriptors[:max_descriptors].flatten()
    else:
        padded = np.zeros((max_descriptors, descriptors.shape[1]))
        padded[:descriptors.shape[0]] = descriptors
        return padded.flatten()

# Fungsi untuk melakukan pemrosesan gambar
def preprocess_image(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    image = cv2.GaussianBlur(image, (11, 11), 0)
    image = cv2.equalizeHist(image)
    return image

# Fungsi untuk extract features
def extract_features_from_image(image):
    keypoints_orb, descriptors_orb = orb.detectAndCompute(image, None)
    keypoints_akaze, descriptors_akaze = akaze.detectAndCompute(image, None)

    if descriptors_orb is None or descriptors_akaze is None:
        return None, None

    min_rows = min(descriptors_orb.shape[0], descriptors_akaze.shape[0])
    descriptors_orb = descriptors_orb[:min_rows]
    descriptors_akaze = descriptors_akaze[:min_rows]

    combined_descriptors = np.hstack((descriptors_orb, descriptors_akaze))
    combined_keypoints = combine_keypoints(keypoints_orb, keypoints_akaze)

    return combined_descriptors, combined_keypoints

# Fungsi untuk mengkalkulasikan IoU score
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
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file:
        file_bytes = np.frombuffer(file.read(), np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        # Memproses gambar dengan memanggil function yang sudah dideclare dan diinitialize di atas
        processed_image = preprocess_image(image)

        # Extract features dari gambar
        descriptors, keypoints = extract_features_from_image(processed_image)

        if descriptors is None:
            return jsonify({'error': 'Could not extract features from the image'}), 400

        # Pad descriptors supaya ukurannya lebih konsisten
        padded_descriptors = pad_or_truncate_descriptors(descriptors, max_descriptors=100)

        # Prediksi class (helmet atau head) dan confidence scorenya
        prediction = clf.predict([padded_descriptors])
        predicted_class = id2label[prediction[0]]
        confidence = clf.predict_proba([padded_descriptors])[0][prediction[0]]

        # DBSCAN clustering untuk mendukung pembuatan bounding box
        keypoint_coords = np.array([kp.pt for kp in keypoints])
        clustering = DBSCAN(eps=50, min_samples=3).fit(keypoint_coords)
        labels = clustering.labels_

        # Mengkalkulasikan bounding boxes
        generated_bboxes = []
        for label in np.unique(labels):
            if label == -1:
                continue
            cluster_points = keypoint_coords[labels == label]
            x_min = np.min(cluster_points[:, 0])
            x_max = np.max(cluster_points[:, 0])
            y_min = np.min(cluster_points[:, 1])
            y_max = np.max(cluster_points[:, 1])
            generated_bboxes.append([x_min, y_min, x_max, y_max])

        # Mendapat value width dan height
        total_width = 0
        total_height = 0
        c = 0
        for x_min, y_min, x_max, y_max in generated_bboxes:
            width = int(x_max)-int(x_min)
            height = int(y_max)-int(y_min)
            total_width += width
            total_height += height
            c +=1

        avg_width = int(total_width/c) if c>0 else 0
        avg_height = int(total_height/c) if c>0 else 0

        # Mengklasifikasikan object pada setiap bounding box
        cropped_descriptors_list = []
        used_bboxes = []
        for bbox in generated_bboxes:
            x_min, y_min, x_max, y_max = map(int, bbox)
            cropped_image = processed_image[y_min:y_max, x_min:x_max]
            cropped_desc, _ = extract_features_from_image(cropped_image)
            if cropped_desc is not None:
                cropped_descriptors_list.append(cropped_desc)

        if cropped_descriptors_list:
            padded_cropped_descriptors_list = [pad_or_truncate_descriptors(desc, max_descriptors=100) for desc in cropped_descriptors_list]
            padded_cropped_descriptors_list = np.array(padded_cropped_descriptors_list)

            input_y_pred = clf.predict(padded_cropped_descriptors_list)
            input_probabilities = clf.predict_proba(padded_cropped_descriptors_list)

            for i, (predicted_class, prob) in enumerate(zip(input_y_pred, input_probabilities)):
              if(max(prob)>0.6):
                used_bboxes.append((generated_bboxes[i], predicted_class, max(prob)))

        # Menampilkan hasil klasifikasi dengan sliding windows
        all_windows = []
        window_size = (avg_width, avg_height) if avg_width > 0 and avg_height > 0 else (50,50)
        step_size = (int(window_size[0] / 2), int(window_size[1] / 2))
        for y in range(0, processed_image.shape[0] - window_size[1] + 1, step_size[1]):
            for x in range(0, processed_image.shape[1] - window_size[0] + 1, step_size[0]):
                window = processed_image[y:y + window_size[1], x:x + window_size[0]]
                all_windows.append((x, y, window))

        windows_descriptors_list = []
        windows_idx_list = []
        for i, (x, y, window) in enumerate(all_windows):
             window_desc, _ = extract_features_from_image(window)
             if window_desc is not None:
                  windows_descriptors_list.append(window_desc)
                  windows_idx_list.append(i)

        used_windows = []
        if windows_descriptors_list:
            padded_input_windows_descriptors_list = [pad_or_truncate_descriptors(desc, max_descriptors=100) for desc in windows_descriptors_list]
            padded_input_windows_descriptors_list = np.array(padded_input_windows_descriptors_list)
            input_probabilities = clf.predict_proba(padded_input_windows_descriptors_list)
            input_y_pred = clf.predict(padded_input_windows_descriptors_list)
            for i, (predicted_class, prob) in enumerate(zip(input_y_pred, input_probabilities)):
              if(max(prob)>0.7):
                used_windows.append((windows_idx_list[i], predicted_class, max(prob)))

        # Konversi warna menjadi RGB
        img_with_bbox = cv2.cvtColor(processed_image, cv2.COLOR_GRAY2RGB)

        # Menggambar bounding box dan labelnya
        for bbox, label,proba in used_bboxes:
            x_min, y_min, x_max, y_max = map(int, bbox)
            cv2.rectangle(img_with_bbox, (x_min, y_min), (x_max, y_max), (255, 0, 0), 2)
            confidence_score = proba
            label_text = f"{id2label[label]} {confidence_score:.2f}"
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(img_with_bbox, label_text, (x_min, y_min - 10), font, 0.5, (255, 0, 0), 2)

        for i, label,proba in used_windows:
            x, y, _ = all_windows[i]
            window = all_windows[i][2]
            window_desc, _ = extract_features_from_image(window)
            if window_desc is not None:
                confidence_score = proba
                cv2.rectangle(img_with_bbox, (x,y), (x + window_size[0], y + window_size[1]), (0, 255, 0), 2)
                label_text = f"{id2label[label]} {confidence_score:.2f}"
                cv2.putText(img_with_bbox, label_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        _, buffer = cv2.imencode('.jpg', img_with_bbox)
        encoded_image = base64.b64encode(buffer).decode('utf-8')
        # Convert koordinat bounding box ke standard Python ints

        generated_bboxes_int = []
        for bbox in generated_bboxes:
             generated_bboxes_int.append(list(map(int, bbox)))


        return jsonify({
            'predicted_class': str(id2label[label]),  # Konversi menjadi string jika numpy type
            'confidence': float(confidence),  # Konversi numpy.float menjadi Python float
            'image': encoded_image,
            'bounding_boxes': [[int(x) for x in bbox] for bbox in generated_bboxes_int]  # Konversi numpy.int64 menjadi Python int
        })
    return jsonify({'error': 'Failed to process the file'}), 500


if __name__ == '__main__':
    app.run(debug=True)