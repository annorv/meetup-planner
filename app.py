import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta

# --- Constants ---
CSV_FILE = "availability_data.csv"
CLEAR_CODE = "letscleartable"

# --- Page Config ---
st.set_page_config(page_title="📆 Meet-Up Planner", layout="centered", page_icon="📅")

# --- CSS Styling ---
st.markdown("""
    <style>
    .title {
        font-size: 40px;
        font-weight: 800;
        color: #4f8bf9;
        text-align: center;
        margin-bottom: 20px;
    }
    .section-title {
        font-size: 24px;
        font-weight: 600;
        color: white;
        margin-top: 30px;
    }
    .footer {
        font-size: 13px;
        text-align: center;
        margin-top: 30px;
        color: #888;
    }
    .stButton>button {
        background-color: #4f8bf9;
        color: white;
        border-radius: 8px;
        padding: 6px 16px;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# --- Init CSV ---
def init_csv():
    try:
        pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        pd.DataFrame(columns=["Name", "Date", "Start Time", "End Time"]).to_csv(CSV_FILE, index=False)

init_csv()

# --- Sidebar Navigation ---
st.sidebar.title("📋 Menu")
page = st.sidebar.radio("Navigate to", ["Submit Availability", "View Suggestions", "Edit My Entries", "Admin Controls"])

# --- App Title ---
st.markdown('<div class="title">📆 Friends Meet-Up Planner</div>', unsafe_allow_html=True)

# --- Page: Submit Availability ---
if page == "Submit Availability":
    st.markdown('<div class="section-title">📝 Submit Your Availability</div>', unsafe_allow_html=True)

    with st.form("availability_form"):
        name = st.text_input("Your Name")

        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", datetime.today())
        with col2:
            end_date = st.date_input("End Date", datetime.today())

        col3, col4 = st.columns(2)
        with col3:
            start_time = st.time_input("Start Time", time(18, 0))
        with col4:
            end_time = st.time_input("End Time", time(20, 0))

        submit = st.form_submit_button("📩 Submit Availability")

        if submit:
            if name.strip() == "":
                st.warning("Please enter your name.")
            elif start_date > end_date:
                st.warning("Start date must be before end date.")
            elif start_time >= end_time:
                st.warning("Start time must be before end time.")
            else:
                new_rows = []
                for i in range((end_date - start_date).days + 1):
                    date = start_date + timedelta(days=i)
                    new_rows.append({
                        "Name": name.strip(),
                        "Date": date.strftime('%Y-%m-%d'),
                        "Start Time": start_time.strftime('%H:%M'),
                        "End Time": end_time.strftime('%H:%M')
                    })
                df = pd.read_csv(CSV_FILE)
                df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
                df.to_csv(CSV_FILE, index=False)
                st.success(f"✅ Availability submitted for {len(new_rows)} day(s)!")

# --- Page: View Suggestions ---
elif page == "View Suggestions":
    st.markdown('<div class="section-title">📊 Group Availability</div>', unsafe_allow_html=True)
    df = pd.read_csv(CSV_FILE)

    if df.empty:
        st.info("No data available yet.")
    else:
        st.dataframe(df)

        total_people = df["Name"].nunique()
        grouped = df.groupby("Date")["Name"].nunique().reset_index()
        everyone_free = grouped[grouped["Name"] == total_people]

        st.markdown('<div class="section-title">🤝 Suggested Dates (Everyone Available)</div>', unsafe_allow_html=True)
        if everyone_free.empty:
            st.warning("No single date where everyone is available yet.")
        else:
            st.success("🎉 Dates where all friends are free:")
            for date in everyone_free["Date"]:
                st.markdown(f"- 📅 **{date}**")

# --- Page: Edit My Entries ---
elif page == "Edit My Entries":
    st.markdown('<div class="section-title">✏️ Edit or Delete Your Availability</div>', unsafe_allow_html=True)

    df = pd.read_csv(CSV_FILE)
    name_to_edit = st.text_input("Enter your name to edit your entries")

    if name_to_edit:
        user_df = df[df["Name"].str.lower() == name_to_edit.strip().lower()]
        if user_df.empty:
            st.warning("No entries found for that name.")
        else:
            edited_df = st.data_editor(user_df, use_container_width=True, num_rows="dynamic")

            if st.button("💾 Save Changes"):
                df = df[df["Name"].str.lower() != name_to_edit.strip().lower()]
                df = pd.concat([df, edited_df], ignore_index=True)
                df.to_csv(CSV_FILE, index=False)
                st.success("✅ Changes saved!")

            if st.button("🗑️ Delete All My Entries"):
                df = df[df["Name"].str.lower() != name_to_edit.strip().lower()]
                df.to_csv(CSV_FILE, index=False)
                st.success("🧹 All your entries have been deleted.")

# --- Page: Admin Controls ---
elif page == "Admin Controls":
    st.markdown('<div class="section-title">🔐 Admin: Clear All Data</div>', unsafe_allow_html=True)

    clear_input = st.text_input("Enter secret code to clear data", type="password")
    if st.button("🧹 Clear Availability Table"):
        if clear_input == CLEAR_CODE:
            pd.DataFrame(columns=["Name", "Date", "Start Time", "End Time"]).to_csv(CSV_FILE, index=False)
            st.success("✅ All data cleared.")
        else:
            st.error("❌ Incorrect passcode.")

# --- Footer ---
st.markdown('<div class="footer">💡 Made with Streamlit • Share with friends & enjoy planning smarter!</div>', unsafe_allow_html=True)
