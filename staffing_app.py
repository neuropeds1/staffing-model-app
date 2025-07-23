import streamlit as st
import pandas as pd

st.set_page_config(page_title="Shift Coverage Calculator", layout="wide")

# Optional: Styling for MDCalc-like feel
st.markdown("""
<style>
h1, h2, h3, h4 {
    color: #004d80;
}
div.stButton > button {
    background-color: #0073e6;
    color: white;
    font-weight: bold;
    border-radius: 6px;
    padding: 0.5em 2em;
}
div[data-testid="metric-container"] {
    background-color: #f0f2f6;
    padding: 10px;
    border-radius: 8px;
    border: 1px solid #d0d0d0;
}
</style>
""", unsafe_allow_html=True)

st.title("🧠 Neurocritical Care Staffing Model Calculator")

st.markdown("### Step 1️⃣: Add Clinician Groups")
st.markdown("Select clinician type and estimate their contribution to day/night shifts.")

st.info("ℹ️ **Note**: Physicians contribute per 28-day rotation. APPs contribute monthly. Fellows contribute nights only. For 'Other', choose your preferred mode.")

CLINICIAN_TYPES = [
    "Madigan", "VM", "Anesthesia Intern", "Neurosurgery Intern",
    "APP (Night Only)", "APP (Day & Night)", "Year 1 Fellow", "Year 2 Fellow", "Other"
]

with st.form("clinician_form"):
    st.subheader("👤 Clinician Details")
    clinician_type = st.selectbox("Select clinician type", CLINICIAN_TYPES)

    rotations = None
    total_day = 0
    total_night = 0

    if clinician_type in ["Madigan", "VM", "Anesthesia Intern", "Neurosurgery Intern"]:
        rotations = st.number_input("Number of 28-day rotations", min_value=1, step=1)

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
        total_night = st.number_input("Total night shifts (Year 1 Fellow)", min_value=0, step=1)

    elif clinician_type == "Year 2 Fellow":
        total_night = st.number_input("Total night shifts (Year 2 Fellow)", min_value=0, step=1)

    elif clinician_type == "APP (Night Only)":
        col1, col2 = st.columns(2)
        with col1:
            number = st.number_input("Number of APPs (Night Only)", min_value=1, step=1)
        with col2:
            nights = st.number_input("Nights per APP per month", min_value=1, max_value=30, value=12)
        total_night = nights * 12 * number

    elif clinician_type == "APP (Day & Night)":
        col1, col2 = st.columns(2)
        with col1:
            number = st.number_input("Number of APPs (Day & Night)", min_value=1, step=1)
        with col2:
            days = st.number_input("Days per APP per month", min_value=1, max_value=31, value=11)
        nights = st.number_input("Nights per APP per month", min_value=0, max_value=30, value=2)
        total_day = days * 12 * number
        total_night = nights * 12 * number

    elif clinician_type == "Other":
        mode = st.radio("How is this clinician scheduled?", ["Per Rotation", "Per Month"])
        if mode == "Per Rotation":
            rotations = st.number_input("Number of 28-day rotations", min_value=1, step=1)
            day_per_rot = st.number_input("Custom day shifts per rotation", min_value=0, step=1)
            night_per_rot = st.number_input("Custom night shifts per rotation", min_value=0, step=1)
            total_day = day_per_rot * rotations
            total_night = night_per_rot * rotations
        else:
            number = st.number_input("Number of clinicians", min_value=1, step=1)
            days = st.number_input("Day shifts per month", min_value=0, max_value=31, value=11)
            nights = st.number_input("Night shifts per month", min_value=0, max_value=30, value=2)
            total_day = days * 12 * number
            total_night = nights * 12 * number

    submitted = st.form_submit_button("➕ Add to Model")
    if submitted:
        new_entry = {
            "Clinician": clinician_type,
            "Day Shifts": total_day,
            "Night Shifts": total_night
        }
        if rotations:
            new_entry["Rotations"] = rotations
        st.session_state.setdefault("clinicians", []).append(new_entry)
        st.success(f"✅ Added {clinician_type} with {total_day} day shifts and {total_night} night shifts.")

# Optional removal
st.markdown("### 🗑️ Manage Entries")
if st.button("Remove Last Entry"):
    if "clinicians" in st.session_state and st.session_state["clinicians"]:
        removed = st.session_state["clinicians"].pop()
        st.warning(f"Removed last entry: {removed['Clinician']}")
    else:
        st.info("No entries to remove.")

# Totals
total_day = sum(item["Day Shifts"] for item in st.session_state.get("clinicians", []))
total_night = sum(item["Night Shifts"] for item in st.session_state.get("clinicians", []))

st.markdown("---")
st.markdown("## 📈 Step 2️⃣: Compare Coverage to Models")

col1, col2 = st.columns(2)
with col1:
    st.metric("Total Day Shifts", total_day)
with col2:
    st.metric("Total Night Shifts", total_night)

MODELS = {
    "6:2": {"day": 6 * 365, "night": 2 * 365},
    "8:3": {"day": 8 * 365, "night": 3 * 365},
}
model_results = []

for model, val in MODELS.items():
    pct_day = round((total_day / val["day"]) * 100, 1)
    pct_night = round((total_night / val["night"]) * 100, 1)
    model_results.append({
        "Model": model,
        "Day Needed": val["day"],
        "Night Needed": val["night"],
        "Day Covered": total_day,
        "Night Covered": total_night,
        "% Days Covered": f"{pct_day}%",
        "% Nights Covered": f"{pct_night}%"
    })

st.markdown("### 📊 Model Comparison Table")
st.dataframe(pd.DataFrame(model_results), use_container_width=True)

st.markdown("### 👥 Clinician Contribution Table")
st.dataframe(pd.DataFrame(st.session_state.get("clinicians", [])), use_container_width=True)
