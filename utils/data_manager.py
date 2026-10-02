
from pathlib import Path
import pandas as pd


# ============================================================
# LOAD STUDENT DATA
# ============================================================

def load_students(data_dir):
    """
    Load student dataset from CSV.
    """

    data_dir = Path(data_dir)

    csv_path = data_dir / "student_data_cleaned.csv"

    if not csv_path.exists():
        raise FileNotFoundError(
            f"Student dataset not found: {csv_path}"
        )

    df = pd.read_csv(csv_path)

    return df


# ============================================================
# SAVE STUDENT DATA
# ============================================================

def save_students(df, data_dir):
    """
    Save student dataframe to CSV.
    """

    data_dir = Path(data_dir)

    data_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    csv_path = data_dir / "student_data_cleaned.csv"

    df.to_csv(
        csv_path,
        index=False
    )


# ============================================================
# GRADE FROM CGPA
# ============================================================

def grade_from_cgpa(cgpa):
    """
    Convert CGPA into a simple grade category.

    Adjust these ranges if your dataset uses
    a different grading system.
    """

    try:
        cgpa = float(cgpa)
    except:
        return "Unknown"

    if cgpa >= 3.70:
        return "A"

    elif cgpa >= 3.30:
        return "B"

    elif cgpa >= 3.00:
        return "C"

    elif cgpa >= 2.50:
        return "D"

    elif cgpa >= 2.00:
        return "E"

    else:
        return "F"


# ============================================================
# RISK FROM STUDENT ROW
# ============================================================

def risk_from_row(row):
    """
    Calculate a basic academic risk level.

    This is used when a student is added or updated.
    """

    try:

        attendance = float(
            row.get("Attendance_Pct", 0)
        )

        previous_cgpa = float(
            row.get("Previous_CGPA", 0)
        )

        study_hours = float(
            row.get("Study_Hours_Per_Day", 0)
        )

        # High Risk
        if (
            attendance < 60
            or previous_cgpa < 2.0
            or study_hours < 2
        ):
            return "High Risk"

        # Medium Risk
        elif (
            attendance < 75
            or previous_cgpa < 2.5
            or study_hours < 3
        ):
            return "Medium Risk"

        # Low Risk
        else:
            return "Low Risk"

    except Exception:
        return "Unknown"


# ============================================================
# SAVE AI PREDICTION HISTORY
# ============================================================

def save_prediction_history(
    data_dir,
    prediction_type,
    student_id,
    features,
    prediction,
    confidence=None
):
    """
    Save every AI prediction into prediction_history.csv.

    This function is used by:
        - Grade Prediction
        - Risk Prediction
    """

    from datetime import datetime

    data_dir = Path(data_dir)

    data_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    history_file = (
        data_dir / "prediction_history.csv"
    )

    # --------------------------------------------------------
    # CREATE RECORD
    # --------------------------------------------------------

    record = {
        "Prediction_Date_Time":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "Prediction_Type":
            prediction_type,

        "Student_ID":
            student_id,

        "Gender":
            features.get("Gender", ""),

        "Age":
            features.get("Age", ""),

        "Major":
            features.get("Major", ""),

        "Attendance_Pct":
            features.get(
                "Attendance_Pct",
                ""
            ),

        "Study_Hours_Per_Day":
            features.get(
                "Study_Hours_Per_Day",
                ""
            ),

        "Previous_CGPA":
            features.get(
                "Previous_CGPA",
                ""
            ),

        "Sleep_Hours":
            features.get(
                "Sleep_Hours",
                ""
            ),

        "Social_Hours_Week":
            features.get(
                "Social_Hours_Week",
                ""
            ),

        "Prediction":
            prediction,

        "Confidence":
            (
                round(
                    confidence * 100,
                    2
                )
                if confidence is not None
                else ""
            )
    }

    new_record = pd.DataFrame(
        [record]
    )

    # --------------------------------------------------------
    # APPEND TO EXISTING HISTORY
    # --------------------------------------------------------

    if history_file.exists():

        try:

            history = pd.read_csv(
                history_file
            )

        except Exception:

            history = pd.DataFrame()

        history = pd.concat(
            [
                history,
                new_record
            ],
            ignore_index=True
        )

    else:

        history = new_record

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    history.to_csv(
        history_file,
        index=False
    )


# ============================================================
# LOAD AI PREDICTION HISTORY
# ============================================================

def load_prediction_history(data_dir):
    """
    Load saved AI prediction history.
    """

    data_dir = Path(data_dir)

    history_file = (
        data_dir / "prediction_history.csv"
    )

    if history_file.exists():

        try:

            return pd.read_csv(
                history_file
            )

        except Exception:

            pass

    # Empty dataframe if history doesn't exist yet
    return pd.DataFrame(
        columns=[
            "Prediction_Date_Time",
            "Prediction_Type",
            "Student_ID",
            "Gender",
            "Age",
            "Major",
            "Attendance_Pct",
            "Study_Hours_Per_Day",
            "Previous_CGPA",
            "Sleep_Hours",
            "Social_Hours_Week",
            "Prediction",
            "Confidence"
        ]
    )

def initialize_data(data_dir):
    """
    Initialize the application data directory.
    """

    data_dir = Path(data_dir)

    # Create data directory if it does not exist
    data_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # Check for the main student dataset
    student_file = data_dir / "student_data_cleaned.csv"

    if not student_file.exists():
        print(
            f"Warning: Student dataset not found: {student_file}"
        )

    return data_dir
# ============================================================
# INTERVENTION MANAGEMENT
# ============================================================

def load_interventions(data_dir):
    path = Path(data_dir) / "interventions.csv"
    columns = ["Created_At", "Student_ID", "Mentor", "Intervention_Type", "Status", "Follow_Up_Date", "Notes"]
    if not path.exists():
        return pd.DataFrame(columns=columns)
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame(columns=columns)


def save_intervention(data_dir, student_id, mentor, intervention_type, status, follow_up_date, notes):
    from datetime import datetime
    path = Path(data_dir) / "interventions.csv"
    record = pd.DataFrame([{
        "Created_At": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Student_ID": student_id,
        "Mentor": mentor,
        "Intervention_Type": intervention_type,
        "Status": status,
        "Follow_Up_Date": follow_up_date,
        "Notes": notes,
    }])
    old = load_interventions(data_dir)
    pd.concat([old, record], ignore_index=True).to_csv(path, index=False)
