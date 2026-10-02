from pathlib import Path
import json
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from xgboost import XGBClassifier

from utils.data_manager import load_students

GRADE_FEATURES = [
    "Gender", "Age", "Major", "Attendance_Pct",
    "Study_Hours_Per_Day", "Previous_CGPA", "Sleep_Hours",
    "Social_Hours_Week"
]
RISK_FEATURES = [
    "Major", "Attendance_Pct", "Previous_CGPA",
    "Study_Hours_Per_Day", "Sleep_Hours", "Social_Hours_Week"
]

def build_preprocessor(cat, num):
    return ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat),
        ("num", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scale", StandardScaler())
        ]), num)
    ])

def candidates():
    common = [
        ("Logistic Regression", LogisticRegression(max_iter=3000)),
        ("Random Forest", RandomForestClassifier(
            n_estimators=300, random_state=42, class_weight="balanced"
        )),
        ("XGBoost", XGBClassifier(
            n_estimators=300, max_depth=5, learning_rate=.05,
            subsample=.85, colsample_bytree=.85,
            objective="multi:softprob", eval_metric="mlogloss",
            random_state=42, n_jobs=2
        ))
    ]
    return dict(common)

def train_task(X, y, preprocessor):
    enc = LabelEncoder()
    y_enc = enc.fit_transform(y.astype(str))
    Xtr, Xte, ytr, yte = train_test_split(
        X, y_enc, test_size=.20, random_state=42, stratify=y_enc
    )
    results, fitted = {}, {}
    for name, estimator in candidates().items():
        pipe = Pipeline([("preprocessor", preprocessor), ("model", estimator)])
        pipe.fit(Xtr, ytr)
        pred = pipe.predict(Xte)
        results[name] = {
            "Accuracy": round(accuracy_score(yte, pred), 4),
            "Precision_weighted": round(precision_score(yte, pred, average="weighted", zero_division=0), 4),
            "Recall_weighted": round(recall_score(yte, pred, average="weighted", zero_division=0), 4),
            "F1_weighted": round(f1_score(yte, pred, average="weighted", zero_division=0), 4),
        }
        fitted[name] = pipe
    best = max(results, key=lambda k: results[k]["F1_weighted"])
    return fitted[best], enc, results, best

def ensure_models(data_dir: Path, model_dir: Path):
    model_dir.mkdir(parents=True, exist_ok=True)

    needed = [
        model_dir / "grade_model.pkl",
        model_dir / "risk_model.pkl",
        model_dir / "grade_encoder.pkl",
        model_dir / "risk_encoder.pkl",
        model_dir / "model_metrics.json"
    ]

    if all(p.exists() for p in needed):
        return

    df = load_students(data_dir)

    required_columns = set(
        GRADE_FEATURES +
        RISK_FEATURES +
        ["Grade", "Risk_Level"]
    )

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "The student dataset is missing required columns: "
            + ", ".join(missing_columns)
            + "\n\nAvailable columns are: "
            + ", ".join(df.columns.astype(str))
        )

    Xg = df[GRADE_FEATURES].copy()
    yg = df["Grade"].astype(str)

    Xr = df[RISK_FEATURES].copy()
    yr = df["Risk_Level"].astype(str)

    grade_pre = build_preprocessor(
        ["Gender", "Major"],
        [
            c for c in GRADE_FEATURES
            if c not in ["Gender", "Major"]
        ]
    )

    risk_pre = build_preprocessor(
        ["Major"],
        [
            c for c in RISK_FEATURES
            if c != "Major"
        ]
    )

    grade_model, grade_enc, grade_results, grade_best = train_task(
        Xg, yg, grade_pre
    )

    risk_model, risk_enc, risk_results, risk_best = train_task(
        Xr, yr, risk_pre
    )

    joblib.dump(
        grade_model,
        model_dir / "grade_model.pkl"
    )

    joblib.dump(
        grade_enc,
        model_dir / "grade_encoder.pkl"
    )

    joblib.dump(
        risk_model,
        model_dir / "risk_model.pkl"
    )

    joblib.dump(
        risk_enc,
        model_dir / "risk_encoder.pkl"
    )

    with open(
        model_dir / "model_metrics.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            {
                "grade": grade_results,
                "risk": risk_results,
                "selected_models": {
                    "grade": grade_best,
                    "risk": risk_best
                }
            },
            f,
            indent=2
        )

def load_models(model_dir: Path):
    return (
        joblib.load(model_dir/"grade_model.pkl"),
        joblib.load(model_dir/"grade_encoder.pkl"),
        joblib.load(model_dir/"risk_model.pkl"),
        joblib.load(model_dir/"risk_encoder.pkl"),
    )

def predict_grade(features: dict, model_dir: Path):
    grade_model, grade_encoder, _, _ = load_models(model_dir)
    X = pd.DataFrame([features])
    pred = grade_model.predict(X)[0]
    label = grade_encoder.inverse_transform([pred])[0]
    probability = None
    if hasattr(grade_model, "predict_proba"):
        p = grade_model.predict_proba(X)[0]
        probability = float(max(p))
    return label, probability

def predict_risk(features: dict, model_dir: Path):
    _, _, risk_model, risk_encoder = load_models(model_dir)
    X = pd.DataFrame([features])
    pred = risk_model.predict(X)[0]
    label = risk_encoder.inverse_transform([pred])[0]
    probability = None
    if hasattr(risk_model, "predict_proba"):
        p = risk_model.predict_proba(X)[0]
        probability = float(max(p))
    return label, probability
