from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

CSV_PATH = DATA_DIR / "student_data_cleaned.csv"


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(CSV_PATH)

print("Original columns:")
print(df.columns.tolist())


# ============================================================
# 1. FIX Previous_GPA → Previous_CGPA
# ============================================================

if "Previous_CGPA" not in df.columns:

    if "Previous_GPA" in df.columns:

        df["Previous_CGPA"] = df["Previous_GPA"]

        print("✓ Previous_GPA converted to Previous_CGPA")

    else:

        raise ValueError(
            "Neither Previous_CGPA nor Previous_GPA exists."
        )


# ============================================================
# 2. CREATE GRADE
# ============================================================

def cgpa_to_grade(cgpa):

    if cgpa >= 3.7:
        return "A+"

    elif cgpa >= 3.3:
        return "A"

    elif cgpa >= 3.0:
        return "B+"

    elif cgpa >= 2.7:
        return "B"

    elif cgpa >= 2.3:
        return "C+"

    elif cgpa >= 2.0:
        return "C"

    elif cgpa >= 1.5:
        return "D"

    else:
        return "F"


if "Grade" not in df.columns:

    df["Grade"] = df["Final_CGPA"].apply(
        cgpa_to_grade
    )

    print("✓ Grade column created")


# ============================================================
# 3. CREATE RISK LEVEL
# ============================================================

def risk_from_row(row):

    risk_points = 0

    # Attendance
    if row["Attendance_Pct"] < 60:
        risk_points += 3

    elif row["Attendance_Pct"] < 75:
        risk_points += 1

    # Previous CGPA
    if row["Previous_CGPA"] < 2.0:
        risk_points += 3

    elif row["Previous_CGPA"] < 2.5:
        risk_points += 2

    elif row["Previous_CGPA"] < 3.0:
        risk_points += 1

    # Study hours
    if row["Study_Hours_Per_Day"] < 1.5:
        risk_points += 2

    elif row["Study_Hours_Per_Day"] < 3:
        risk_points += 1

    # Final CGPA
    if row["Final_CGPA"] < 2.0:
        risk_points += 2

    elif row["Final_CGPA"] < 2.5:
        risk_points += 1

    # Final risk category
    if risk_points >= 5:
        return "High Risk"

    elif risk_points >= 2:
        return "Medium Risk"

    else:
        return "Low Risk"


if "Risk_Level" not in df.columns:

    df["Risk_Level"] = df.apply(
        risk_from_row,
        axis=1
    )

    print("✓ Risk_Level column created")


# ============================================================
# 4. REMOVE OLD Previous_GPA COLUMN
# ============================================================

if "Previous_GPA" in df.columns:

    df.drop(
        columns=["Previous_GPA"],
        inplace=True
    )


# ============================================================
# 5. ARRANGE COLUMNS
# ============================================================

required_order = [
    "Student_ID",
    "Gender",
    "Age",
    "Major",
    "Attendance_Pct",
    "Study_Hours_Per_Day",
    "Previous_CGPA",
    "Sleep_Hours",
    "Social_Hours_Week",
    "Final_CGPA",
    "Grade",
    "Risk_Level"
]

# Keep required columns first
existing_required = [
    col for col in required_order
    if col in df.columns
]

other_columns = [
    col for col in df.columns
    if col not in existing_required
]

df = df[
    existing_required + other_columns
]


# ============================================================
# 6. SAVE CORRECTED DATASET
# ============================================================

df.to_csv(
    CSV_PATH,
    index=False
)


# ============================================================
# 7. DISPLAY RESULT
# ============================================================

print("\n======================================")
print("DATASET REPAIRED SUCCESSFULLY")
print("======================================")

print("\nFinal columns:")

for column in df.columns:
    print("✓", column)

print("\nRisk distribution:")

print(
    df["Risk_Level"].value_counts()
)

print("\nGrade distribution:")

print(
    df["Grade"].value_counts()
)

print("\nSaved to:")

print(CSV_PATH)