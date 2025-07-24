import streamlit as st
import pandas as pd

st.set_page_config(page_title="Shift Coverage Calculator", layout="wide")

# Styling
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

# Initialize state
if "clinicians" not in st.session_state:
    st.session_state["clinicians"] = []

st.markdown("### Step 1️⃣: Add Clinician Group")

CLINICIAN_TYPES = [
    "Madigan", "VM", "Anesthesia Intern", "Neurosurgery Intern",
    "APP (Night Only)", "APP (Day & Night)",
    "Year 1 Fellow", "Year 2 Fellow",
    "UW Neurology R2", "UW Neurology R3/4", "Madigan Neurology",
    "Other"
]
clinician_type = st.selectbox("Select clinician type", CLINICIAN_TYPES)

def add_entry(name, day, night, extra=None):
    new_entry = {
        "Clinician": name,
        "Day Shifts": day,
        "Night Shifts": night,
        "Rotations": None,
        "APPs": None
    }
    if extra:
        new_entry.update(extra)
    st.session_state["clinicians"].append(new_entry)
    st.success(f"✅ Added {name} with {day} day shifts and {night} night shifts.")

# Forms for each type
if clinician_type in ["Madigan", "VM", "Anesthesia Intern", "Neurosurgery Intern"]:
    with st.form("intern_form"):
        rotations = st.number_input("Number of 28-day rotations", min_value=1, step=1)
        if clinician_type == "Madigan":
            d, n = 10, 12
        elif clinician_type == "VM":
            d, n = 16, 6
        elif clinician_type == "Anesthesia Intern":
            d, n = 24, 0
        elif clinician_type == "Neurosurgery Intern":
            d, n = 14, 6
        if st.form_submit_button("➕ Add to Model"):
            add_entry(clinician_type, d * rotations, n * rotations, {"Rotations": rotations})

elif clinician_type in ["Year 1 Fellow", "Year 2 Fellow"]:
    with st.form("fellow_form"):
        night = st.number_input("Total night shifts", min_value=0, step=1)
        if st.form_submit_button("➕ Add to Model"):
            add_entry(clinician_type, 0, night)

elif clinician_type == "APP (Night Only)":
    with st.form("app_night_form"):
        col1, col2 = st.columns(2)
        number = col1.number_input("Number of APPs", min_value=1, step=1)
        nights = col2.number_input("Nights per APP/month", min_value=1, max_value=30, value=12)
        if st.form_submit_button("➕ Add to Model"):
            add_entry(clinician_type, 0, nights * 13 * number, {"APPs": number})

elif clinician_type == "APP (Day & Night)":
    with st.form("app_daynight_form"):
        col1, col2 = st.columns(2)
        number = col1.number_input("Number of APPs", min_value=1, step=1)
        days = col2.number_input("Days per APP/month", min_value=1, max_value=31, value=11)
        nights = st.number_input("Nights per APP/month", min_value=0, max_value=30, value=2)
        if st.form_submit_button("➕ Add to Model"):
            add_entry(clinician_type, days * 12 * number, nights * 12 * number, {"APPs": number})

elif clinician_type in ["UW Neurology R2", "UW Neurology R3/4", "Madigan Neurology"]:
    with st.form("neuro_form"):
        rotations = st.number_input("Number of 28-day rotations", min_value=1, step=1)
        day_per_rot = 17
        night_per_rot = 5
        if st.form_submit_button("➕ Add to Model"):
            add_entry(clinician_type, day_per_rot * rotations, night_per_rot * rotations, {"Rotations": rotations})

elif clinician_type == "Other":
    with st.form("other_form"):
        mode = st.radio("How is this clinician scheduled?", ["Per Rotation", "Per Month"])
        if mode == "Per Rotation":
            rotations = st.number_input("Number of 28-day rotations", min_value=1, step=1)
            day_per_rot = st.number_input("Custom day shifts per rotation", min_value=0, step=1)
            night_per_rot = st.number_input("Custom night shifts per rotation", min_value=0, step=1)
            if st.form_submit_button("➕ Add to Model"):
                add_entry("Other (Rotation)", day_per_rot * rotations, night_per_rot * rotations, {"Rotations": rotations})
        else:
            number = st.number_input("Number of clinicians", min_value=1, step=1)
            days = st.number_input("Day shifts per month", min_value=0, max_value=31, value=11)
            nights = st.number_input("Night shifts per month", min_value=0, max_value=30, value=2)
            if st.form_submit_button("➕ Add to Model"):
                add_entry("Other (Monthly)", days * 12 * number, nights * 12 * number, {"APPs": number})

# Manage entries
st.markdown("### 🗑️ Manage Entries")
if st.button("Remove Last Entry"):
    if st.session_state["clinicians"]:
        removed = st.session_state["clinicians"].pop()
        st.warning(f"Removed last entry: {removed['Clinician']}")
    else:
        st.info("No entries to remove.")

# Apply 16% buffer to APPs
app_entries = [item for item in st.session_state["clinicians"] if item.get("APPs") is not None]
non_app_entries = [item for item in st.session_state["clinicians"] if item.get("APPs") is None]

raw_app_day = sum(item["Day Shifts"] for item in app_entries)
raw_app_night = sum(item["Night Shifts"] for item in app_entries)

# Apply buffers to both APP and non-APP clinicians
adjusted_app_day = round(raw_app_day * 0.84)
adjusted_app_night = round(raw_app_night * 0.84)

raw_non_app_day = sum(item["Day Shifts"] for item in non_app_entries)
raw_non_app_night = sum(item["Night Shifts"] for item in non_app_entries)

adjusted_non_app_day = round(raw_non_app_day * 0.85)
adjusted_non_app_night = round(raw_non_app_night * 0.85)

total_day = adjusted_non_app_day + adjusted_app_day
total_night = adjusted_non_app_night + adjusted_app_night


# Display totals
st.markdown("---")
st.markdown("## 📈 Step 2️⃣: Compare Coverage to Models")

col1, col2 = st.columns(2)
with col1:
    st.metric("Total Day Shifts", total_day)
with col2:
    st.metric("Total Night Shifts", total_night)

with st.expander("📉 Shift Adjustments (Buffer for PTO, sick calls, etc.)"):
    st.subheader("APPs (16% buffer):")
    st.write(f"🟦 Raw APP Day Shifts: {raw_app_day}")
    st.write(f"🟦 Adjusted APP Day Shifts (× 0.84): {adjusted_app_day}")
    st.write(f"🌙 Raw APP Night Shifts: {raw_app_night}")
    st.write(f"🌙 Adjusted APP Night Shifts (× 0.84): {adjusted_app_night}")
    st.divider()
    st.subheader("Non-APPs (15% buffer):")
    st.write(f"🟦 Raw Non-APP Day Shifts: {raw_non_app_day}")
    st.write(f"🟦 Adjusted Non-APP Day Shifts (× 0.85): {adjusted_non_app_day}")
    st.write(f"🌙 Raw Non-APP Night Shifts: {raw_non_app_night}")
    st.write(f"🌙 Adjusted Non-APP Night Shifts (× 0.85): {adjusted_non_app_night}")

# Compare to models
MODELS = {
    "6:2": {"day": 6 * 365, "night": 2 * 365},
    "6:3": {"day": 6 * 365, "night": 3 * 365},
    "7:2": {"day": 7 * 365, "night": 2 * 365},
    "7:3": {"day": 7 * 365, "night": 3 * 365},
    "8:2": {"day": 8 * 365, "night": 2 * 365},
    "8:3": {"day": 8 * 365, "night": 3 * 365},
}
results = []
for model, val in MODELS.items():
    pct_day = round((total_day / val["day"]) * 100, 1)
    pct_night = round((total_night / val["night"]) * 100, 1)
    results.append({
        "Model": model,
        "Day Needed": val["day"],
        "Night Needed": val["night"],
        "Day Covered": total_day,
        "Night Covered": total_night,
        "% Days Covered": f"{pct_day}%",
        "% Nights Covered": f"{pct_night}%"
    })

st.markdown("### 📊 Model Comparison Table")
st.dataframe(pd.DataFrame(results), use_container_width=True)

# Clinician breakdown
st.markdown("### 👥 Clinician Contribution Table")
df = pd.DataFrame(st.session_state["clinicians"])
st.dataframe(df.fillna("—"), use_container_width=True)
