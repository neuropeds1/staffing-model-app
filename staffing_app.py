import streamlit as st
import pandas as pd

st.set_page_config(page_title="Shift Coverage Calculator", layout="wide")

st.title("📊 Neurocritical Care Staffing Model Calculator")

st.markdown("""
### Step 1: Add Clinician Groups
Select clinician type, specify how many **rotations (non-APP)** or **APPs (for APP groups)**, and the app will estimate day/night contributions.
""")

st.markdown(
    "> **Note:** Physicians contribute per 28-day rotation. APPs contribute monthly. For 'Other', select your preferred mode."
)

CLINICIAN_TYPES = [
    "Madigan", "VM", "Anesthesia Intern", "Neurosurgery Intern",
    "APP (Night Only)", "APP (Day & Night)", "Year 1 Fellow", "Year 2 Fellow", "Other"
]
clinician_data = []

with st.form("clinician_form"):
    clinician_type = st.selectbox("Select clinician type", CLINICIAN_TYPES)

    # Initialize defaults
    rotations = None
    total_day = 0
    total_night = 0

    # Only show this for the 4 clinician types that use rotations
      if clinician_type:
        # Only show this for the 4 clinician types that use rotations
        if clinician_type in ["Madigan", "VM", "Anesthesia Intern", "Neurosurgery Intern"]:
            rotations = st.number_input("How many 28-day rotations will this group cover?", min_value=1, step=1)

        if clinician_type == "Madigan":
            day_per_rot, night_per_rot = 10, 12
        elif clinician_type == "VM":
            day_per_rot, night_per_rot = 16, 6
        elif clinician_type == "Anesthesia Intern":
            day_per_rot, night_per_rot = 24, 0
        elif clinician_type == "Neurosurgery Intern":
            day_per_rot, night_per_rot = 14, 6

        total_day = day_per_rot * rotations
        total_night = night_per_rot * rotations

    elif clinician_type == "Year 1 Fellow":
        total_day = 0
        total_night = st.number_input("Total night shifts for Year 1 Fellow", min_value=0, step=1)

    elif clinician_type == "Year 2 Fellow":
        total_day = 0
        total_night = st.number_input("Total night shifts for Year 2 Fellow", min_value=0, step=1)

    elif clinician_type == "APP (Night Only)":
        number_of_apps = st.number_input("Number of APPs (Night Only)", min_value=1, step=1)
        nights_per_month = st.number_input("Nights per APP per month", min_value=1, max_value=30, value=12)
        total_day = 0
        total_night = nights_per_month * 12 * number_of_apps

    elif clinician_type == "APP (Day & Night)":
        number_of_apps = st.number_input("Number of APPs (Day & Night)", min_value=1, step=1)
        days_per_month = st.number_input("Days per APP per month", min_value=1, max_value=31, value=11)
        nights_per_month = st.number_input("Nights per APP per month", min_value=0, max_value=30, value=2)
        total_day = days_per_month * 12 * number_of_apps
        total_night = nights_per_month * 12 * number_of_apps

    elif clinician_type == "Other":
        mode = st.radio("How is this clinician scheduled?", ["Per Rotation", "Per Month"])
        if mode == "Per Rotation":
            rotations = st.number_input("Number of 28-day rotations", min_value=1, step=1)
            day_per_rot = st.number_input("Custom day shifts per rotation", min_value=0, step=1)
            night_per_rot = st.number_input("Custom night shifts per rotation", min_value=0, step=1)
            total_day = day_per_rot * rotations
            total_night = night_per_rot * rotations
        else:
            num_clinicians = st.number_input("Number of clinicians", min_value=1, step=1)
            days_per_month = st.number_input("Custom day shifts per month", min_value=0, max_value=31, value=11)
            nights_per_month = st.number_input("Custom night shifts per month", min_value=0, max_value=30, value=2)
            total_day = days_per_month * 12 * num_clinicians
            total_night = nights_per_month * 12 * num_clinicians

    submitted = st.form_submit_button("Add to Model")
    if submitted:
        clinician_entry = {
            "Clinician": clinician_type,
            "Day Shifts": total_day,
            "Night Shifts": total_night
        }
        if rotations:
            clinician_entry["Rotations"] = rotations
        st.session_state.setdefault("clinicians", []).append(clinician_entry)
        st.success(f"Added {clinician_type} with {total_day} day shifts and {total_night} night shifts")

# Optional: Remove last clinician added
if st.button("🗑️ Remove Last Entry"):
    if "clinicians" in st.session_state and st.session_state["clinicians"]:
        removed = st.session_state["clinicians"].pop()
        st.warning(f"Removed last entry: {removed['Clinician']}")
    else:
        st.info("No entries to remove.")

# Calculate Totals
total_day = sum(item["Day Shifts"] for item in st.session_state.get("clinicians", []))
total_night = sum(item["Night Shifts"] for item in st.session_state.get("clinicians", []))

st.markdown("### Step 2: Compare to 6:2 and 8:3 Models")
MODELS = {
    "6:2": {"day": 6 * 365, "night": 2 * 365},
    "8:3": {"day": 8 * 365, "night": 3 * 365},
}

model_results = []

for model, values in MODELS.items():
    day_pct = round((total_day / values["day"]) * 100, 1)
    night_pct = round((total_night / values["night"]) * 100, 1)
    model_results.append({
        "Model": model,
        "Day Needed": values["day"],
        "Night Needed": values["night"],
        "Day Covered": total_day,
        "Night Covered": total_night,
        "% Days Covered": f"{day_pct}%",
        "% Nights Covered": f"{night_pct}%"
    })

st.markdown("### 📋 Breakdown of All Clinician Contributions")
st.dataframe(pd.DataFrame(st.session_state.get("clinicians", [])))

st.markdown("### 📈 Summary of Coverage vs Models")
st.dataframe(pd.DataFrame(model_results))
