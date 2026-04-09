UNMUTE_AI/
│
├── backend/
│   ├── app.py                    # FastAPI entry point + WebSocket wiring
│   ├── ws_server.py              # WebSocket endpoint & streaming logic
│   ├── predictor.py              # Gesture prediction + smoothing
│   ├── landmark_extractor.py     # MediaPipe + FIXED normalization
│   ├── model_loader.py           # Load trained ML model
│   └── config.py                 # FIXED absolute paths + constants
│
├── frontend/
│   ├── index.html                #web page for translation
│   ├── home.html                 #home page
│   ├── script.js                 # FIXED WebSocket + backpressure
│   └── style.css                 # Full UNMUTE.AI UI styles
│
├── model/
│   └── model.p                   # Trained RandomForest model
│
├── dataset/
│   ├── A_images/
│   ├── B_images/
│   ├── L_images/
│   ├── 1_images/
│   ├── create_A_samples.csv
│   ├── create_B_samples.csv
│   ├── create_L_samples.csv
│   └── create_1_samples.csv
│
├── scripts/
│   ├── create_A_dataset.py       # FIXED paths
│   ├── create_B_dataset.py       # FIXED paths
│   ├── create_L_dataset.py       # FIXED paths
│   ├── create_1_dataset.py       # FIXED paths
│   ├── create_dataset.py         # Kaggle dataset loader
│   └── train_classifier.py       # FIXED CSV paths
│
├── requirements.txt              # FIXED — all dependencies added
├── run.bat                       # Windows startup script (NEW)
├── run.sh                        # Linux/Mac startup script (NEW)
└── README.md                     # Updated setup instructions

To run backend- 1) cd backend
                2) uvicorn app:app --host 127.0.0.1 --port 8000 --reload
