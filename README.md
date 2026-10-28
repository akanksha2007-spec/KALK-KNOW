# KALK-KNOW -Plant Knowledge System🌿

Kalki Know is an offline-first, AI-powered desktop application designed to identify and provide comprehensive knowledge about medicinal plants and traditional Ayurvedic remedies. 

Built for the modern era while preserving ancient wisdom.

## ✨ Features
- **AI Plant Identification:** Uses a custom-trained ResNet50 model to identify 15+ medicinal plants from leaf images with a confidence threshold to prevent false positives.
- **Plant Repository:** A searchable database of 84+ medicinal plants including their taxonomy, traditional uses, and safety notes.
- **Herbal Remedies:** Evidence-based traditional remedies mapped to specific diseases and plants.
- **Vaidya AI Assistant:** An integrated AI chatbot that answers questions based on your local plant database.
- **Research Contributions:** Allows users to upload and manage research papers and field notes.
- **Offline-First Architecture:** All data is stored locally using SQLite. No internet required for core features.

## 🛠️ Tech Stack
- **Frontend:** PySide6 (Qt for Python)
- **Database:** SQLite
- **Machine Learning:** PyTorch, Torchvision
- **AI Integration:** DeepSeek API (via OrcaRouter)

## 🚀 How to Run Locally
1. Clone the repository.
2. Create a virtual environment and install dependencies:
   `pip install -r requirements.txt` *(Note: PyTorch and PySide6 required)*
3. Add your API key in the `.env` file:
   `DEEPSEEK_API_KEY=your_key_here`
4. Run the app:
   `python main.py`

## 📌 Note
The machine learning models (`.pth`) and SQLite database (`.db`) are excluded from this repository due to size limits. You can generate them using `train_model.py` and `seed_from_csv.py`.

---
*Preserving biodiversity and promoting preventive healthcare through technology.*
