"""
Kalki Know — train plant classifier on BOTH leaf + whole-plant folders.
Run: python train_model.py
"""

import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, ConcatDataset
from torchvision import datasets, transforms, models

# ---------- PATHS ----------
LEAF_DIR  = r"C:\Users\Acer\Desktop\Old Data\Akanksha Samantray\Indian Medicinal Leaves Image Datasets\Medicinal Leaf dataset"
PLANT_DIR = r"C:\Users\Acer\Desktop\Old Data\Akanksha Samantray\Indian Medicinal Leaves Image Datasets\Medicinal plant dataset"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_MODEL = os.path.join(BASE_DIR, "kalki_plant_model.pth")
OUT_CLASSES = os.path.join(BASE_DIR, "classes.txt")

BATCH = 32
EPOCHS_HEAD = 2
EPOCHS_FINE = 3
LR_HEAD = 1e-3
LR_FINE = 1e-4

# ---------- CHECK PATHS ----------
if not os.path.isdir(LEAF_DIR):
    print(f"LEAF_DIR not found:\n{LEAF_DIR}")
    raise SystemExit(1)
if not os.path.isdir(PLANT_DIR):
    print(f"PLANT_DIR not found:\n{PLANT_DIR}")
    raise SystemExit(1)

# ---------- TRANSFORMS ----------
train_tf = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.ColorJitter(brightness=0.15, contrast=0.15),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])
val_tf = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])

# ---------- LOAD BOTH FOLDERS ----------
leaf_ds = datasets.ImageFolder(LEAF_DIR, transform=train_tf)
plant_ds = datasets.ImageFolder(PLANT_DIR, transform=train_tf)

print(f"Leaf folder:  {len(leaf_ds.classes)} species, {len(leaf_ds)} images")
print(f"Plant folder: {len(plant_ds.classes)} species, {len(plant_ds)} images")

# ---------- UNION OF CLASSES ----------
all_classes = sorted(set(leaf_ds.classes) | set(plant_ds.classes))
class_to_idx = {c: i for i, c in enumerate(all_classes)}
print(f"\nTotal species in union: {len(all_classes)}")


def remap(ds):
    """Rewrite dataset to use union class index."""
    new_samples = []
    for path, _old in ds.samples:
        parent = os.path.basename(os.path.dirname(path))
        if parent in class_to_idx:
            new_samples.append((path, class_to_idx[parent]))
    ds.samples = new_samples
    ds.classes = all_classes
    ds.class_to_idx = class_to_idx
    return ds


leaf_ds = remap(leaf_ds)
plant_ds = remap(plant_ds)

full = ConcatDataset([leaf_ds, plant_ds])
print(f"Merged images total: {len(full)}")

# ---------- SPLIT ----------
val_size = max(1, int(0.15 * len(full)))
train_size = len(full) - val_size
train_ds, val_ds = torch.utils.data.random_split(full, [train_size, val_size])

# ---------- SAVE CLASSES ----------
with open(OUT_CLASSES, "w", encoding="utf-8") as f:
    f.write("\n".join(all_classes))
print(f"Saved class list → {OUT_CLASSES}")

# ---------- LOADERS ----------
train_loader = DataLoader(train_ds, batch_size=BATCH, shuffle=True, num_workers=0)
val_loader = DataLoader(val_ds, batch_size=BATCH, num_workers=0)

# ---------- DEVICE ----------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device: {device}")

# ---------- MODEL ----------
model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
model.fc = nn.Linear(model.fc.in_features, len(all_classes))
model = model.to(device)
criterion = nn.CrossEntropyLoss()

# ---------- PHASE 1 ----------
for name, p in model.named_parameters():
    p.requires_grad = "fc" in name

opt = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=LR_HEAD)
print("\n[Phase 1] Head training")
for ep in range(EPOCHS_HEAD):
    model.train()
    running = 0.0
    for i, (x, y) in enumerate(train_loader):
        x, y = x.to(device), y.to(device)
        opt.zero_grad()
        loss = criterion(model(x), y)
        loss.backward()
        opt.step()
        running += loss.item()
        if i % 30 == 0:
            print(f"  ep{ep+1} batch{i} loss {loss.item():.3f}")
    print(f"  epoch {ep+1}/{EPOCHS_HEAD} avg loss {running/max(1,len(train_loader)):.3f}")

# ---------- PHASE 2 ----------
for p in model.parameters():
    p.requires_grad = True

opt = optim.Adam(model.parameters(), lr=LR_FINE)
print("\n[Phase 2] Fine-tuning")
for ep in range(EPOCHS_FINE):
    model.train()
    for i, (x, y) in enumerate(train_loader):
        x, y = x.to(device), y.to(device)
        opt.zero_grad()
        loss = criterion(model(x), y)
        loss.backward()
        opt.step()
        if i % 50 == 0:
            print(f"  ep{ep+1} batch{i} loss {loss.item():.3f}")
    model.eval()
    correct = total = 0
    with torch.no_grad():
        for x, y in val_loader:
            x, y = x.to(device), y.to(device)
            correct += (model(x).argmax(1) == y).sum().item()
            total += y.size(0)
    print(f"  epoch {ep+1}/{EPOCHS_FINE} val acc {correct/max(1,total):.3f}")

# ---------- SAVE ----------
torch.save(model.state_dict(), OUT_MODEL)
print(f"\nSaved: {OUT_MODEL}")
print(f"Size: {os.path.getsize(OUT_MODEL)/1024/1024:.1f} MB")
print("Done.")