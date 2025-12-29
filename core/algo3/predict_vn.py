# backend_model.py
import os
import sys
import io
import urllib.parse
import webbrowser
import torch
from torchvision import models, transforms
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


MODEL_PATH = os.path.join(BASE_DIR, "model_vietnam.pth")
CLASSES_PATH = os.path.join(BASE_DIR, "classes.txt")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)

# ========================
# 1. LOAD CLASS NAMES
# ========================

with open(CLASSES_PATH, "r", encoding="utf-8") as f:
    CLASS_NAMES = [line.strip() for line in f.readlines()]
num_classes = len(CLASS_NAMES)
print("Số lớp:", num_classes)
print("Classes:", CLASS_NAMES)

# ========================
# 2. LOAD MODEL
# ========================
model = models.resnet18(weights=None)   
in_features = model.fc.in_features
model.fc = torch.nn.Linear(in_features, num_classes)

state_dict = torch.load(MODEL_PATH, map_location=device)
model.load_state_dict(state_dict)
model.eval()
model.to(device)

# ========================
# 3. TIỀN XỬ LÝ ẢNH

preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
])

# ========================
# 4. CORE PREDICT
# ========================
def _predict_tensor(img_tensor: torch.Tensor):
    """
    img_tensor: [1, 3, 224, 224] đã preprocess & đưa lên device
    """
    with torch.no_grad():
        outputs = model(img_tensor)
        probs = torch.softmax(outputs, dim=1)
        conf, pred_idx = torch.max(probs, 1)
        pred_idx = pred_idx.item()
        conf = conf.item()

    label = CLASS_NAMES[pred_idx]
    return label, conf

# ========================
# 5. HÀM PUBLIC – DÙNG LẠI
# ========================
def predict_image_path(image_path: str):
    """Dự đoán từ đường dẫn file ảnh (dùng CMD / Tkinter / script)."""
    img = Image.open(image_path).convert("RGB")
    tensor = preprocess(img).unsqueeze(0).to(device)
    return _predict_tensor(tensor)

def predict_pil_image(img: Image.Image):
    """Dự đoán từ PIL Image (dùng cho Streamlit, Tkinter)."""
    img = img.convert("RGB")
    tensor = preprocess(img).unsqueeze(0).to(device)
    return _predict_tensor(tensor)

def predict_image_bytes(image_bytes: bytes):
    """Dự đoán từ bytes ảnh (upload web, socket, v.v.)."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    tensor = preprocess(img).unsqueeze(0).to(device)
    return _predict_tensor(tensor)

# ========================
# 6. MAP UTILS
# ========================
def normalize_location_name(label: str) -> str:
    """
    Chuyển nhãn model sang dạng dễ đọc / dễ tìm map.
    Ví dụ: 'Buu_dien_Trung_tam' -> 'Buu dien Trung tam'
    """
    cleaned = label.replace("_", " ")
    return " ".join(cleaned.split())

def build_map_url(label: str):
    """
    Trả về (location_name, map_url) để mở Google Maps.
    Thêm 'TP Hồ Chí Minh' vào query để ưu tiên kết quả đúng khu vực.
    """
    location_name = normalize_location_name(label)
    query = urllib.parse.quote(f"{location_name} TP Hồ Chí Minh")
    map_url = f"https://www.google.com/maps/search/?api=1&query={query}"
    return location_name, map_url

def open_map(label: str):
    """
    Mở Google Maps cho nhãn dự đoán. Luôn trả về (location_name, map_url).
    """
    location_name, map_url = build_map_url(label)
    try:
        webbrowser.open(map_url)
    except Exception as exc:  
        print(f"Không mở được trình duyệt: {exc}")
    return location_name, map_url


