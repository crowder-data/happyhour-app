import streamlit as st
import pandas as pd
from datetime import datetime
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
    if day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
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
    ).time()

    start = datetime.strptime(
        start_time,
        "%I:%M:%S %p"
    ).time()

    end = datetime.strptime(
        end_time,
        "%I:%M:%S %p"
    ).time()

    if start <= end:
        return start <= now <= end

    return now >= start or now <= end


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


st.subheader(f"Happy Hours Available Now ({today})")


if results.empty:
    st.info("No happy hours are active right now.")

else:
    results = results.sort_values(["Name", "Start"])

    for _, row in results.iterrows():

        with st.expander(
            f"**{row['Name']}** • {row['Start']} - {row['Stop']}"
        ):

            st.markdown(f"**Special:** {row['Description']}")

            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Type:** {row['Type']}")
                st.write(f"**Street:** {row['Street']}")
                st.write(f"**City:** {row['City']}")

            with col2:
                st.write(f"**Day:** {row['Day']}")
                st.write(f"**Starts:** {row['Start']}")
                st.write(f"**Ends:** {row['Stop']}")

            # Future additions
            # st.link_button("Website", row["Website"])
            # st.link_button("Directions", ...)
            # st.write(row["Phone"])
