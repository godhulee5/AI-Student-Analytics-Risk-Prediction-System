# AI Student Analytics & Risk Prediction — College Admin Portal

A Streamlit-based college-admin application for student analytics, academic risk prediction,
grade prediction, early warning, student management, reports, and administration.

## ML basis
This project follows the uploaded Colab notebook:
- Grade Prediction uses Gender, Age, Major, Attendance, Study Hours, Previous CGPA, Sleep Hours and Social Hours.
- Academic Risk Prediction uses Major, Attendance, Previous CGPA, Study Hours, Sleep Hours and Social Hours.
- The notebook compares Logistic Regression, Random Forest and XGBoost and selects the deployment model by weighted F1.
- If Grade/Risk_Level are absent, the notebook engineers them using its documented rules.

## Run in VS Code

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

Open the local URL shown by Streamlit.

## Admin login
Demo credentials:
- Username: `admin`
- Password: `admin123`

Change these before real institutional deployment. For production, replace the demo login
with your college's authenticated identity system.

## Real college data
Put your CSV at:

`data/student_data_cleaned.csv`

The expected core fields are:
Student_ID, Gender, Age, Major, Attendance_Pct, Study_Hours_Per_Day,
Previous_CGPA, Sleep_Hours, Social_Hours_Week, Final_CGPA

The app can also accept the target fields Grade and Risk_Level if present.

If the file is not present, the app creates a clearly-labelled demo dataset so the interface
can be tested immediately. Demo records should not be presented as real college records.

## Model artifacts
At startup the app trains/reuses local models:
- models/grade_model.pkl
- models/risk_model.pkl
- models/grade_encoder.pkl
- models/risk_encoder.pkl
- models/model_metrics.json

The training implementation mirrors the uploaded notebook's feature sets and target creation.

## Modules
1. Dashboard
2. Student Management
3. Academic Analytics
4. AI Risk Prediction
5. Grade Prediction
6. Early Warning System
7. Reports
8. Admin Panel

## Important research note
Risk and grade outputs are model predictions/decision-support indicators, not definitive
judgments about a student. In a research paper, describe engineered targets as engineered
targets when they are created from rules rather than supplied by the original dataset.

## Research Project Enhancements
The application includes six research-focused modules:
1. Student Performance Dashboard with filters and academic/risk visualizations.
2. Smart Early Warning System integrating existing and newly predicted High Risk students.
3. Explainable AI using stored global model feature importance.
4. Model Evaluation & Comparison for Logistic Regression, Random Forest and XGBoost.
5. Student Progress Tracking with prediction history over time.
6. Intervention Management for mentor actions, follow-up dates and case status.
