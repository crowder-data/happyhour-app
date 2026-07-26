import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TIMEZONE = ZoneInfo("America/Chicago")

st.set_page_config(
    page_title="Happy Hour Finder",
    layout="wide"
)

st.title("🍺 LaCrosse Area Happy Hours")


@st.cache_data
def load_data():
    business = pd.read_csv("data/business.csv")
    specials = pd.read_csv("data/specials.csv")
    days = pd.read_csv("data/day.csv")

    return business, specials, days


business, specials, days = load_data()


def get_day_groups(day, day_table):

    if day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
        groups = [day, "Weekday", "Daily"]
    else:
        groups = [day, "Weekend", "Daily"]

    return day_table.loc[
        day_table["Day"].isin(groups),
        "ID"
    ].tolist()


def is_current_time(start_time, stop_time):

    now = datetime.now(TIMEZONE).time()

    start = datetime.strptime(
        start_time,
        "%I:%M:%S %p"
    ).time()

    stop = datetime.strptime(
        stop_time,
        "%I:%M:%S %p"
    ).time()

    if start <= stop:
        return start <= now <= stop

    return now >= start or now <= stop


def time_remaining(stop_time):

    now = datetime.now(TIMEZONE)

    stop = datetime.strptime(
        stop_time,
        "%I:%M:%S %p"
    )

    stop = now.replace(
        hour=stop.hour,
        minute=stop.minute,
        second=stop.second,
        microsecond=0
    )

    if stop < now:
        stop += timedelta(days=1)

    return stop - now


today = datetime.now(TIMEZONE).strftime("%A")

day_ids = get_day_groups(today, days)

todays_specials = specials[
    specials["dayID"].isin(day_ids)
]

todays_specials = todays_specials[
    todays_specials.apply(
        lambda row: is_current_time(
            row["Start"],
            row["Stop"]
        ),
        axis=1
    )
]

results = (
    todays_specials
    .merge(
        business,
        left_on="busID",
        right_on="ID",
        how="left"
    )
    .merge(
        days,
        left_on="dayID",
        right_on="ID",
        how="left",
        suffixes=("", "_day")
    )
)

st.subheader("Current Happy Hours")

if results.empty:

    st.info("No happy hours are active right now.")

else:

    results["TimeRemaining"] = results["Stop"].apply(time_remaining)

    results = results.sort_values("TimeRemaining")

    for _, row in results.iterrows():

        total_minutes = int(
            row["TimeRemaining"].total_seconds() // 60
        )

        hours = total_minutes // 60
        minutes = total_minutes % 60

        if hours > 0:
            remaining = f"{hours}h {minutes}m"
        else:
            remaining = f"{minutes}m"

        header = (
            f"{row['Name']} "
            f"({remaining} remaining)"
        )

        with st.expander(header):

            st.write(f"**Special:** {row['Description']}")

            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Type:** {row['Type']}")
                st.write(f"**Address:** {row['Street']}")
                st.write(f"**City:** {row['City']}")

            with col2:
                st.write(f"**Hours:** {row['Start']} - {row['Stop']}")
                st.write(f"**Day:** {row['Day']}")
