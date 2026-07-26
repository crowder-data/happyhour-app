import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

st.set_page_config(
    page_title="Happy Hour Finder",
    layout="wide"
)

st.title("Happy Hour Finder")


@st.cache_data
def load_data():
    business = pd.read_csv("data/business.csv")
    specials = pd.read_csv("data/specials.csv")
    days = pd.read_csv("data/day.csv")

    return business, specials, days


business, specials, days = load_data()


def get_day_groups(day, day_table):
    return day_table.loc[
        day_table["Day"] == day,
        "ID"
    ].tolist()


def is_current_time(start_time, end_time):
    now = datetime.now(
        ZoneInfo("America/Chicago")
    ).time()

    start = datetime.strptime(
        start_time,
        "%I:%M %p"
    ).time()

    end = datetime.strptime(
        end_time,
        "%I:%M %p"
    ).time()

    if start <= end:
        return start <= now <= end
    else:
        return now >= start or now <= end


today = datetime.now(
    ZoneInfo("America/Chicago")
).strftime("%A")


day_ids = get_day_groups(
    today,
    days
)


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


st.subheader(
    f"Happy Hours Available Now ({today})"
)


if results.empty:
    st.info("No happy hours found right now.")
else:
    st.dataframe(
        results[
            [
                "Type",
                "Name",
                "Street",
                "City",
                "Day",
                "Start",
                "Stop",
                "Description"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )


with st.expander("Debug Information"):
    st.write("Current day:")
    st.write(today)

    st.write("Applicable day IDs:")
    st.write(day_ids)

    st.write("Filtered specials:")
    st.dataframe(todays_specials)
