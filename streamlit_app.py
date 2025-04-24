import streamlit as st
import json
import io
import os
from datetime import date, time, datetime
from streamlit_option_menu import option_menu

st.set_page_config(page_title="Blood Logistics Tool", layout="wide")
DATA_FILE = "saved_data.json"

st.title("ONR Blood Mangement Support Tool")
st.sidebar.header("User Input")

def load_saved_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            for k, v in data.items():
                if not ("FormSubmitter:" in k or k.startswith("week_") or k.startswith("simulation_days") or k.startswith("med_platoon_id") or k.startswith("blood_inventory")):
                    st.session_state[k] = v

def save_session_state():
    to_save = {k: v for k, v in st.session_state.items() if not k.startswith("_")}
    with open(DATA_FILE, "w") as f:
        json.dump(to_save, f, indent=4, default=str)

def main():
    load_saved_data()

    with st.sidebar:
        selected = option_menu(
            menu_title="Main Menu",
            options=["Home", "Medical Logistics Company", "Transport Info", "Conflict Prediction"],
            icons=["house", "hospital", "truck", "exclamation-triangle"],
            menu_icon="cast",
            default_index=0
        )

    if selected == "Home":
        show_home()
    elif selected == "Medical Logistics Company":
        show_med_log_company()
    elif selected == "Transport Info":
        show_transport_info()
    elif selected == "Conflict Prediction":
        show_conflict_prediction()

def show_home():
    st.header("Welcome to the Blood Logistics Tool")
    name = st.text_input("Enter your name", value=st.session_state.get("user_name", ""))
    st.session_state["user_name"] = name
    if name:
        st.success(f"Welcome, {name}! Please navigate to the pages on the left to proceed.")
        save_session_state()

def show_med_log_company():
    st.header("Medical Logistics Company Page")

    company_id = st.number_input("Medical Logistics Company ID", min_value=0, step=1, value=st.session_state.get("company_id", 0))
    st.session_state["company_id"] = company_id

    num_platoons = st.number_input("Number of Platoons", min_value=0, step=1, value=st.session_state.get("num_platoons", 0))
    st.session_state["num_platoons"] = num_platoons

    platoons = []
    for i in range(int(num_platoons)):
        st.subheader(f"Platoon {i+1}")
        pid_key = f"pid_{i}"
        size_key = f"size_{i}"
        days_key = f"days_{i}"

        pid = st.text_input(f"Platoon ID {i+1}", value=st.session_state.get(pid_key, ""), key=pid_key)
        size = st.number_input(f"Platoon Size {i+1}", min_value=0, value=st.session_state.get(size_key, 0), key=size_key)
        days_away = st.number_input(f"Days Away from Home Base (Platoon {i+1})", min_value=0, value=st.session_state.get(days_key, 0), key=days_key)

        platoons.append({"Platoon ID": pid, "Size": size, "Days Away": days_away})

    if st.button("Save Medical Logistics Company Info"):
        st.session_state["med_log_company_info"] = {
            "Company ID": company_id,
            "Number of Platoons": num_platoons,
            "Platoons": platoons
        }
        save_session_state()
        st.success("Medical Logistics Company info saved!")

def show_transport_info():
    st.header("Transport Information Page")

    company_id = st.number_input("Medical Company ID", min_value=0, step=1, value=st.session_state.get("transport_company_id", 0), key="transport_company_id")

    num_transports = st.number_input("Number of Transportation Options", min_value=0, step=1, value=st.session_state.get("num_transports", 0))
    st.session_state["num_transports"] = num_transports

    transport_methods = ["Helicopter", "Truck", "Boat", "Drone", "Airplane"]
    transports = []

    for i in range(int(num_transports)):
        st.subheader(f"Transport Option {i+1}")

        method = st.selectbox(f"Select Transportation Method {i+1}", transport_methods, index=transport_methods.index(st.session_state.get(f"method_{i}", "Helicopter")), key=f"method_{i}")

        lon = st.text_input(f"Longitude for Blood Resource Location {i+1}", value=st.session_state.get(f"lon_{i}", ""), key=f"lon_{i}")
        lat = st.text_input(f"Latitude for Blood Resource Location {i+1}", value=st.session_state.get(f"lat_{i}", ""), key=f"lat_{i}")
        platoon_id = st.number_input(f"Medical Platoon ID {i+1}", min_value=0, value=st.session_state.get(f"platoon_id_{i}", 0), key=f"platoon_id_{i}")
        days_away = st.number_input(f"Days Away from Platoon Location {i+1}", min_value=0, value=st.session_state.get(f"days_away_{i}", 0), key=f"days_away_{i}")
        num_dates = st.number_input(f"Number of Delivery Dates for Transport {i+1}", min_value=0, max_value=365, step=1, value=st.session_state.get(f"num_dates_{i}", 0), key=f"num_dates_{i}")

        delivery_schedule = []
        for j in range(int(num_dates)):
            st.markdown(f"**Delivery {j+1} for Transport {i+1}**")
            date_key = f"transport_deliv_date_{i}_{j}"
            raw_value = st.session_state.get(date_key, date.today())

            if isinstance(raw_value, str):
                try:
                    raw_value = date.fromisoformat(raw_value)
                    st.session_state[date_key] = raw_value
                except ValueError:
                    raw_value = date.today()
                    st.session_state[date_key] = raw_value

            delivery_date = st.date_input(f"Delivery Date {j+1} for Transport {i+1}", value=raw_value, key=date_key)

            pickup_key = f"transport_pickup_{i}_{j}"
            raw_pickup = st.session_state.get(pickup_key, time(9, 0))
            if isinstance(raw_pickup, str):
                try:
                    raw_pickup = datetime.strptime(raw_pickup, "%H:%M:%S").time()
                    st.session_state[pickup_key] = raw_pickup
                except ValueError:
                    raw_pickup = time(9, 0)
                    st.session_state[pickup_key] = raw_pickup

            pickup_time = st.time_input(f"Pickup Time on {delivery_date}", value=raw_pickup, key=pickup_key)

            dropoff_key = f"transport_dropoff_{i}_{j}"
            raw_dropoff = st.session_state.get(dropoff_key, time(10, 0))
            if isinstance(raw_dropoff, str):
                try:
                    raw_dropoff = datetime.strptime(raw_dropoff, "%H:%M:%S").time()
                    st.session_state[dropoff_key] = raw_dropoff
                except ValueError:
                    raw_dropoff = time(10, 0)
                    st.session_state[dropoff_key] = raw_dropoff

            dropoff_time = st.time_input(f"Drop-off Time on {delivery_date}", value=raw_dropoff, key=dropoff_key)

            capacity = st.number_input(f"Capacity (pints) for Delivery {j+1} for Transport {i+1}", min_value=0, value=st.session_state.get(f"transport_capacity_{i}_{j}", 0), key=f"transport_capacity_{i}_{j}")

            delivery_schedule.append({
                "Date": delivery_date.strftime("%Y-%m-%d"),
                "Pickup Time": pickup_time.strftime("%H:%M"),
                "Drop-off Time": dropoff_time.strftime("%H:%M"),
                "Capacity (pints)": capacity
            })

        transports.append({
            "Method": method,
            "Coordinates": {"Longitude": lon, "Latitude": lat},
            "Platoon ID": platoon_id,
            "Days Away": days_away,
            "Delivery Schedule": delivery_schedule
        })

    if st.button("Submit Transport Info"):
        st.session_state["transport_info"] = transports
        save_session_state()
        st.success("Transport data saved!")

def show_conflict_prediction():
    st.header("Conflict Prediction Page")

    if "user_data" not in st.session_state:
        st.session_state.user_data = []

    with st.form(key="conflict_prediction_form"):
        simulation_days = st.number_input(
            "Length of Simulation in Days:", min_value=0,
            value=st.session_state.get("simulation_days", 0),
            key="simulation_days"
        )

        med_platoon_id = st.number_input(
            "Medical Platoon ID:", min_value=0,
            value=st.session_state.get("med_platoon_id", 0),
            key="med_platoon_id"
        )

        blood_inventory = st.number_input(
            "Fresh Whole Blood Inventory on Hand (pints):", min_value=0,
            value=st.session_state.get("blood_inventory", 0),
            key="blood_inventory"
        )

        st.markdown("### Weekly Combat Intelligence Assessment")
        conflict_matrix = []
        conflict_level_labels = ["1: Non-Combat", "2: Sustain Combat", "3: Assault Combat", "4: Extreme Combat"]

        if simulation_days > 0:
            num_weeks = (simulation_days + 6) // 7
            for week in range(num_weeks):
                st.markdown(f"#### Week {week + 1}")
                st.markdown("_Based on your current intelligence, the likelihood of being at each conflict level..._")
                week_data = []
                total = 0
                for level in range(4):
                    slider_key = f"week_{week}_level_{level}"
                    val = st.slider(
                        f"{conflict_level_labels[level]} (0–5):", min_value=0, max_value=5,
                        step=1, value=st.session_state.get(slider_key, 0), key=slider_key
                    )
                    total += val
                    week_data.append(val)
                if total != 5:
                    st.error(f"Week {week + 1}: Conflict levels must sum to 5 (currently {total}).")
                conflict_matrix.append(week_data)

        submit = st.form_submit_button("Submit")

        if submit:
            errors = [f"Week {i + 1} conflict level sliders must sum to 5." for i, week in enumerate(conflict_matrix) if sum(week) != 5]

            if errors:
                for e in errors:
                    st.error(e)
            else:
                new_entry = {
                    "Length of Simulation in Days": simulation_days,
                    "Medical Platoon ID": med_platoon_id,
                    "Fresh Whole Blood Inventory on Hand (pints)": blood_inventory,
                    "Weekly Conflict Level Distribution": {
                        "Labels": conflict_level_labels,
                        "Data": conflict_matrix
                    }
                }
                st.session_state.user_data.append(new_entry)
                save_session_state()
                st.success("Data added successfully!")

    st.subheader("Stored User Data")
    if st.session_state.user_data:
        st.json(st.session_state.user_data)
        json_data = json.dumps(st.session_state.user_data, indent=4)
        json_file = io.BytesIO(json_data.encode())
        st.download_button(
            label="Download JSON File",
            data=json_file,
            file_name="user_data.json",
            mime="application/json"
        )

if __name__ == "__main__":
    main()
