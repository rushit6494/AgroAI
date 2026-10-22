# 🌾 AgroAI – AI-Powered Smart Crop Recommendation and Plant Health Assistant

AgroAI is a smart agriculture web application built with Streamlit, TensorFlow, and MySQL. It helps farmers make informed decisions through crop recommendation, cotton plant disease/pest detection, soil analysis, a treatment knowledge base, and a farmer dashboard with history tracking.

## Features

- 🌾 **Crop Recommendation** — Random Forest model (~99.5% test accuracy) trained on soil nutrients (N, P, K), temperature, humidity, pH, and rainfall
- 📸 **Plant Disease/Pest Detection** — MobileNetV2 transfer learning model (cotton only, 90.3% test accuracy) detecting bacterial blight, curl virus, leaf hopper/jassid damage, herbicide damage, and more
- 🧪 **Soil Analysis** — Rule-based nutrient status (N/P/K) and pH interpretation
- 💊 **Treatment Knowledge Base** — MySQL-backed product/treatment database, clearly separated from AI diagnosis, with demo data marked "NOT VERIFIED"
- 👨‍🌾 **Farmer Dashboard** — Simple login, multiple farms, and history of saved plant/soil analysis records

## Tech Stack

Python, Streamlit, scikit-learn, XGBoost, TensorFlow/Keras, MySQL, SQLAlchemy, Pandas, Matplotlib/Seaborn

## Project Structure

AgroAI/
├── app/ # Streamlit pages, services
├── ml/
│ ├── crop_recommendation/ # Random Forest pipeline
│ ├── disease_detection/ # MobileNetV2 pipeline (cotton)
│ └── soil_analysis/ # Rule-based logic
├── config/ # Settings, env config
├── database/ # SQL schema (if added)
├── requirements.txt
└── app.py # Entry point


## ⚠️ Important: Models and Dataset Not Included

Due to file size and dataset licensing, the following are **not included in this repository** (excluded via `.gitignore`):
- Trained model files (`*.keras`, `*.joblib`)
- Cotton disease dataset (SAR-CLD-2024, from Mendeley)
- `.env` file (contains local database credentials)

To run this project locally, you must train the models yourself (see Setup below).

## Setup Instructions

### 1. Prerequisites
- Python 3.12
- MySQL 8.0
- Git

### 2. Clone and set up environment
```bash
git clone https://github.com/rushit6494/AgroAI.git
cd AgroAI
py -3.12 -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Create a `.env` file in the project root
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=agroai
MAX_UPLOAD_MB=5
DISEASE_CONFIDENCE_THRESHOLD=0.70
```

### 4. Create the MySQL database
In MySQL Workbench, run:
```sql
CREATE DATABASE agroai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
Then run the schema and demo-data SQL scripts (see `database/` folder) to create the `diseases`, `products`, `treatments`, `users`, `farms`, and `crop_history` tables.

### 5. Download datasets and train models
- Crop Recommendation dataset (Kaggle, Atharva Ingle) → place in `ml/crop_recommendation/dataset/`
- SAR-CLD-2024 cotton disease dataset (Mendeley) → place in `ml/disease_detection/dataset/sar_cld/`

```bash
python ml/crop_recommendation/train.py
python ml/disease_detection/prepare_split.py
python ml/disease_detection/train.py
```

### 6. Run the app
```bash
streamlit run app.py
```

## Known Limitations

- Disease/pest model is trained only on cotton; it is not validated for other crops
- Model may show high confidence on out-of-distribution images (e.g. non-leaf parts, other plants) — always verify results manually
- Severity estimation ("Unknown") is not implemented due to lack of severity-labeled data
- Treatment records in the database are **demo/placeholder data only** and must not be used for actual pesticide application
- Images in the training dataset are not from Gujarat/India field conditions

## Disclaimer

This is an academic/learning project. AI-generated analysis is not an official diagnosis. Always consult a qualified agricultural expert before applying any treatment.