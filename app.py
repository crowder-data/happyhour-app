import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

st.set_page_config(
    page_title="Happy Hour Finder",
    layout="wide"
)

st.title("🍺 Happy Hour Finder")


@st.cache_data
def load_data():
    business = pd.read_csv("data/business.csv")
    specials = pd.read_csv("data/specials.csv")
    days = pd.read_csv("data/day.csv")

    return business, specials, days


business, specials, days = load_data()


def get_day_groups(day, day_table):
    if day in [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday"
    ]:
        groups = [day, "Weekday", "Daily"]
    else:
        groups = [day, "Weekend", "Daily"]

    return day_table.loc[
        day_table["Day"].isin(groups),
        "ID"
    ].tolist()


def is_current_time(start_time, end_time):
    now = datetime.now(
        ZoneInfo("America/Chicago")
    )

    start = datetime.strptime(
        start_time,
        "%I:%M:%S %p"
    ).replace(
        year=now.year,
        month=now.month,
        day=now.day
    )

    end = datetime.strptime(
        end_time,
        "%I:%M:%S %p"
    ).replace(
        year=now.year,
        month=now.month,
        day=now.day
    )

    if end < start:
        end += timedelta(days=1)

    if now < start:
        return False

    return start <= now <= end


def time_remaining(stop_time):
    now = datetime.now(
        ZoneInfo("America/Chicago")
    )

    stop = datetime.strptime(
        stop_time,
        "%I:%M:%S %p"
    ).replace(
        year=now.year,
        month=now.month,
        day=now.day
    )

    if stop < now:
        stop += timedelta(days=1)

    return stop - now


today = datetime.now(
    ZoneInfo("America/Chicago")
).strftime("%A")


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


if results.empty:
    st.info("No happy hours are active right now.")

else:

    results["TimeRemaining"] = results["Stop"].apply(
        time_remaining
    )

    results = results.sort_values(
        "TimeRemaining"
    )

    st.subheader(
        f"Happy Hours Available Now ({today})"
    )

    for _, row in results.iterrows():

        total_minutes = int(
            row["TimeRemaining"].total_seconds() // 60
        )

        hours = total_minutes // 60
        minutes = total_minutes % 60

        if hours:
            remaining = f"{hours}h {minutes}m"
        else:
            remaining = f"{minutes}m"

        with st.expander(
            f"**{row['Name']}** ({remaining} remaining)"
        ):

            st.markdown(
                f"### {row['Description']}"
            )

            col1, col2 = st.columns(2)

            with col1:
                st.write(
                    f"**Type:** {row['Type']}"
                )
                st.write(
                    f"**Address:** {row['Street']}"
                )
                st.write(
                    f"**City:** {row['City']}"
                )

            with col2:
                st.write(
                    f"**Day:** {row['Day']}"
                )
                st.write(
                    f"**Hours:** {row['Start']} – {row['Stop']}"
                )

            # Future additions:
            # st.link_button("Website", row["Website"])
            # st.link_button("Directions", google_maps_url)
            # st.write(f"Phone: {row['Phone']}")
