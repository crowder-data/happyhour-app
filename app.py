import streamlit as st
import pandas as pd
from datetime import datetime

st.title("Happy Hour Finder")

# Load data
business = pd.read_csv(
    "data/business.csv"
)

specials = pd.read_csv(
    "data/specials.csv"
)

days = pd.read_csv(
    "data/day.csv"
)

# Current day
today = datetime.now().strftime("%A")

st.write(f"Today is {today}")

# Find today's day_id
today_id = days.loc[
    days["day"] == today,
    "day_id"
].iloc[0]

# Include daily specials too
daily_id = days.loc[
    days["day"] == "Daily",
    "day_id"
].iloc[0]

# Filter specials
todays_specials = specials[
    specials["day_id"].isin(
        [today_id, daily_id]
    )
]

# Join business info
results = todays_specials.merge(
    business,
    on="business_id"
)

# Display
if len(results) == 0:
    st.write("No happy hours found.")
else:
    st.dataframe(
        results[
            [
                "name",
                "address",
                "start",
                "end",
                "description"
            ]
        ],
        hide_index=True
    )
