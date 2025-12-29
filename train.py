import os
import time
import torch
from torch import nn, optim
from torchvision import datasets, models, transforms
from PIL import Image, ImageFile 
ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.LOAD_TRUNCATED_IMAGES = True

# ============================
# CẤU HÌNH CƠ BẢN
# ============================
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", DEVICE)

DATA_DIR = "data"          
MODEL_PATH = "model_vietnam.pth"
CLASSES_PATH = "classes.txt"

BATCH_SIZE = 32
NUM_EPOCHS = 30      
LR = 1e-4
PATIENCE = 5            
# ============================
# 1. TRANSFORMS CHO DATA
# ============================
train_transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.RandomResizedCrop(224),
    transforms.RandomHorizontalFlip(),
    transforms.ColorJitter(0.2, 0.2, 0.2, 0.1),  
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
])

val_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
])

# ============================
# 2. DATASET & DATALOADER
# ============================
train_dir = os.path.join(DATA_DIR, "train")
val_dir   = os.path.join(DATA_DIR, "val")

train_dataset = datasets.ImageFolder(train_dir, transform=train_transform)
val_dataset   = datasets.ImageFolder(val_dir,   transform=val_transform)

train_loader = torch.utils.data.DataLoader(
    train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=2
)
val_loader = torch.utils.data.DataLoader(
    val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=2
)

class_names = train_dataset.classes
num_classes = len(class_names)
print("Số lớp:", num_classes)
print("Classes:", class_names)

# Lưu tên lớp ra file để backend dùng lại
with open(CLASSES_PATH, "w", encoding="utf-8") as f:
    for c in class_names:
        f.write(c + "\n")

# ============================
# 3. KHỞI TẠO MODEL RESNET18
# ============================
# Dùng pretrained để nhận diện tốt hơn
model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)

# Freeze một phần backbone (học chậm hơn nhưng ổn định)
for name, param in model.named_parameters():
    param.requires_grad = True  # nếu muốn freeze layer đầu có thể chỉnh

in_features = model.fc.in_features
model.fc = nn.Linear(in_features, num_classes)  # thay FC cho đúng số lớp mình

model = model.to(DEVICE)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=LR)
# Scheduler: nếu val_loss không giảm 3 epoch thì giảm LR
scheduler = optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode='min', factor=0.5, patience=3
)

# ============================
# 4. HÀM TRAIN + VAL + EARLY STOP
# ============================
def train_model(num_epochs=NUM_EPOCHS):
    best_acc = 0.0
    best_state_dict = None
    best_epoch = 0

    epochs_no_improve = 0

    for epoch in range(num_epochs):
        print(f"\n===== Epoch {epoch+1}/{num_epochs} =====")
        start_time = time.time()

        # -------- TRAIN --------
        model.train()
        running_loss = 0.0
        running_corrects = 0
        total = 0

        for inputs, labels in train_loader:
            inputs = inputs.to(DEVICE)
            labels = labels.to(DEVICE)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)

            _, preds = torch.max(outputs, 1)

            loss.backward()
            optimizer.step()

            running_loss += loss.item() * inputs.size(0)
            running_corrects += torch.sum(preds == labels.data)
            total += labels.size(0)

        epoch_loss = running_loss / total
        epoch_acc = running_corrects.double() / total
        print(f"[TRAIN] Loss: {epoch_loss:.4f}  Acc: {epoch_acc:.4f}")

        # -------- VAL --------
        model.eval()
        val_loss = 0.0
        val_corrects = 0
        val_total = 0

        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs = inputs.to(DEVICE)
                labels = labels.to(DEVICE)

                outputs = model(inputs)
                loss = criterion(outputs, labels)

                _, preds = torch.max(outputs, 1)

                val_loss += loss.item() * inputs.size(0)
                val_corrects += torch.sum(preds == labels.data)
                val_total += labels.size(0)

        val_loss /= val_total
        val_acc = val_corrects.double() / val_total
        print(f"[ VAL ] Loss: {val_loss:.4f}  Acc: {val_acc:.4f}")

        # Cập nhật scheduler theo val_loss
        scheduler.step(val_loss)

        # Lưu model tốt nhất theo val_acc
        if val_acc > best_acc:
            best_acc = val_acc
            best_state_dict = model.state_dict()
            best_epoch = epoch + 1
            torch.save(best_state_dict, MODEL_PATH)
            print(f"--> Lưu model tốt nhất: {MODEL_PATH} (epoch={best_epoch}, acc={best_acc:.4f})")
            epochs_no_improve = 0
        else:
            epochs_no_improve += 1
            print(f"Không cải thiện {epochs_no_improve}/{PATIENCE} epoch")

        print(f"Thời gian epoch: {time.time() - start_time:.1f} s")

        # EARLY STOPPING
        if epochs_no_improve >= PATIENCE:
            print(f"\n==> EARLY STOPPING tại epoch {epoch+1}. Best epoch = {best_epoch}, val_acc = {best_acc:.4f}")
            break

    print(f"\nTraining xong. Best val acc = {best_acc:.4f} (epoch={best_epoch})")

if __name__ == "__main__":
    train_model()
