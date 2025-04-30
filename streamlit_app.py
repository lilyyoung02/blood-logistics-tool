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

    if isinstance(st.session_state.get("transport_info"), list):
        del st.session_state["transport_info"]

    company_id = st.number_input("Medical Company ID", min_value=0, step=1,
                                 value=st.session_state.get("transport_company_id", 0),
                                 key="transport_company_id")

    num_platoons = st.number_input("Number of Platoons", min_value=0, step=1,
                                   value=st.session_state.get("transport_num_platoons", 0),
                                   key="transport_num_platoons")

    transport_methods = ["Helicopter", "Truck", "Boat", "Drone", "Airplane"]
    all_platoon_transports = []

    for p in range(int(num_platoons)):
        st.subheader(f"Platoon {p+1} Transportation Info")

        num_transports = st.number_input(f"Number of Transportation Options for Platoon {p+1}", min_value=0, step=1,
                                         value=st.session_state.get(f"num_transports_{p}", 0),
                                         key=f"num_transports_{p}")

        platoon_transports = []

        for i in range(int(num_transports)):
            st.markdown(f"**Transport Option {i+1} for Platoon {p+1}**")

            method = st.selectbox(
                f"Select Transportation Method", transport_methods,
                index=transport_methods.index(st.session_state.get(f"method_{p}_{i}", "Helicopter")),
                key=f"method_{p}_{i}"
            )

            days_away = st.number_input(f"Days Away from Supply Base", min_value=0.0, step=0.1,
                                        value=st.session_state.get(f"days_away_{p}_{i}", 0.0),
                                        key=f"days_away_{p}_{i}")

            avg_days_between = st.number_input(
                f"Average Days Between Restocks", min_value=0.0, step=0.1,
                value=st.session_state.get(f"avg_days_{p}_{i}", 0.0),
                key=f"avg_days_{p}_{i}")

            max_days_between = st.number_input(
                f"Maximum Days Between Restocks", min_value=0.0, step=0.1,
                value=st.session_state.get(f"max_days_{p}_{i}", 0.0),
                key=f"max_days_{p}_{i}")

            transport_capacity = st.number_input(
                f"Transport Capacity (pints)", min_value=0, step=1,
                value=st.session_state.get(f"transport_capacity_{p}_{i}", 0),
                key=f"transport_capacity_{p}_{i}")

            platoon_transports.append({
                "Method": method,
                "Days Away from Base": days_away,
                "Average Days Between Restocks": avg_days_between,
                "Maximum Days Between Restocks": max_days_between,
                "Transport Capacity (pints)": transport_capacity
            })

        all_platoon_transports.append({
            "Platoon Number": p + 1,
            "Transport Options": platoon_transports
        })

    if st.button("Submit Transport Info"):
        st.session_state["transport_info"] = {
            "Company ID": company_id,
            "Platoons": all_platoon_transports
        }
        save_session_state()
        st.success("Transport data saved!")


    if "transport_info" in st.session_state:
        st.subheader("Platoon Summary")
        for platoon in st.session_state["transport_info"].get("Platoons", []):
            with st.expander(f"Platoon {platoon['Platoon Number']} Summary"):
                for idx, option in enumerate(platoon["Transport Options"]):
                    st.markdown(f"**Transport {idx + 1}:**")
                    st.write(option)


def show_conflict_prediction():
    st.header("Conflict Prediction Page")

    if "user_data" not in st.session_state:
        st.session_state.user_data = []

    with st.form(key="conflict_prediction_form"):
        simulation_days = st.number_input(
            "Length of Simulation in Days:", min_value=1,
            value=st.session_state.get("simulation_days", 15),
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

        st.markdown("### Define Conflict Assessment Ranges")
        st.markdown("_Specify day ranges (inclusive) for which you want to define conflict levels._")

        num_ranges = st.number_input("Number of Ranges", min_value=1, value=3, key="num_ranges")
        day_ranges = []
        conflict_matrix = []
        conflict_level_labels = ["1: Non-Combat", "2: Sustain Combat", "3: Assault Combat", "4: Extreme Combat"]

        last_end = 0
        for i in range(int(num_ranges)):
            st.markdown(f"**Range {i+1}**")

            start_day = st.number_input(f"Start Day of Range {i+1}", min_value=1,
                                        value=last_end + 1, key=f"start_day_{i}")
            end_day = st.number_input(f"End Day of Range {i+1}", min_value=start_day,
                                      value=min(simulation_days, start_day + 4), key=f"end_day_{i}")
            last_end = end_day

            day_ranges.append((start_day, end_day))

            st.markdown("_Based on your intelligence, set the likelihood of each conflict level._")
            range_data = []
            total = 0
            for level in range(4):
                slider_key = f"range_{i}_level_{level}"
                val = st.slider(
                    f"{conflict_level_labels[level]} (0–5):", min_value=0, max_value=5, step=1,
                    value=st.session_state.get(slider_key, 0), key=slider_key
                )
                total += val
                range_data.append(val)

            if total != 5:
                st.error(f"Range {i+1} ({start_day}–{end_day}): conflict levels must sum to 5 (currently {total}).")

            conflict_matrix.append(range_data)

        submit = st.form_submit_button("Submit")

        if submit:
            # Validation: ensure full coverage and no overlap
            flat_coverage = []
            errors = []

            for idx, (start, end) in enumerate(day_ranges):
                if sum(conflict_matrix[idx]) != 5:
                    errors.append(f"Range {idx+1} ({start}–{end}): conflict levels must sum to 5.")
                flat_coverage.extend(range(start, end + 1))

            if sorted(flat_coverage) != list(range(1, simulation_days + 1)):
                errors.append("Ranges must cover all days from 1 to simulation length without gaps or overlaps.")

            if errors:
                for err in errors:
                    st.error(err)
            else:
                new_entry = {
                    "Length of Simulation in Days": simulation_days,
                    "Medical Platoon ID": med_platoon_id,
                    "Fresh Whole Blood Inventory on Hand (pints)": blood_inventory,
                    "Conflict Ranges": [
                        {
                            "Days": f"{start}-{end}",
                            "Conflict Levels": {
                                "Labels": conflict_level_labels,
                                "Distribution": dist
                            }
                        }
                        for (start, end), dist in zip(day_ranges, conflict_matrix)
                    ]
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
