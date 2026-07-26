import streamlit as st
import pandas as pd
from datetime import datetime

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
    return (
        day_table.loc[
            day_table["day"] == day,
            "applies_to"
        ]
        .tolist()
    )


def is_current_time(start_time, end_time):
    now = datetime.now().time()

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


today = datetime.today().strftime("%A")

day_groups = get_day_groups(
    today,
    days
)


todays_specials = specials[
    specials["day"].isin(day_groups)
]


todays_specials = todays_specials[
    todays_specials.apply(
        lambda row: is_current_time(
            row["start_time"],
            row["end_time"]
        ),
        axis=1
    )
]


results = todays_specials.merge(
    business,
    on="business_id",
    how="left"
)


st.subheader(f"Happy Hours Available Now ({today})")

if results.empty:
    st.info("No happy hours found right now.")
else:
    display_columns = [
        "name",
        "address",
        "city",
        "state",
        "day",
        "start_time",
        "end_time",
        "description"
    ]

    st.dataframe(
        results[display_columns],
        use_container_width=True,
        hide_index=True
    )


with st.expander("Debug Information"):
    st.write("Day groups:")
    st.write(day_groups)

    st.write("Matching specials:")
    st.dataframe(todays_specials)
