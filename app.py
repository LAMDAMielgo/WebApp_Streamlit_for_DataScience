# Dependencies
import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

# Global variables
DATA_PATH = "./data/raw/Motor_Vehicle_Collisions_-_Crashes.csv"

st.title("Motor Vehicle Collisions in New York City")
st.markdown("This app is a Streamlit dash that can be used to analyze motor vehicle collisions in NYC")


@st.cache(persist=True)
def load_data(nrows):
    # Dataset is to large, therefore only a limited part of it is loaded at a time
    # CRASH_DATA & CRASH_TIME are datetime objects
    data_to_return = pd.read_csv(DATA_PATH, nrows=nrows, parse_dates=[['CRASH_DATE', 'CRASH_TIME']])
    data_to_return.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)

    lowercase = lambda x: str(x).lower()
    data_to_return.rename(lowercase, axis='columns', inplace=True)
    data_to_return.rename(columns={'crash_date_crash_time': 'date_time'}, inplace=True)
    return data_to_return


## LOAD DATASET
vehicles_df = load_data(nrows=10000)
print(vehicles_df.columns)

# -------------------------------------------------------- Fist Map
# Geolocated data in map
st.header("Where are the most people injured in NYC?")
# An exploration of the dataset has been done by the teacher to achieve the max indicated
max_injured_people = 19  # Dataset exploration to be done
injured_people = st.slider("Number of persons injured", 0, max_injured_people)
st.map(vehicles_df.query('injured_persons >= @injured_people')[['latitude', 'longitude']].dropna(how='any'))

# ------------------------------------------------------ Second Map
# Using filtering options in streamlit to show a specific hour
st.header("How many collisions occur during a given time of day")
# A a sidebar st.sidebar.slider
hour = st.slider("Hour to look at", 0, 23)
vehicles_df = vehicles_df[vehicles_df['date_time'].dt.hour == hour]

# ------------------------------------------------------
st.markdown(f"Vehicle collisions between {hour}:00 and {hour + 1}:00")
map_midpoint = (np.average(vehicles_df['latitude']), np.average(vehicles_df['longitude']))

st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={"latitude": map_midpoint[0],
                        "longitude": map_midpoint[1],
                        "zoom": 10,
                        "pitch": 50,
                        },
    # see pydeck documentation for more layers
    layers=[
        pdk.Layer(
            "HexagonLayer",
            data=vehicles_df[['date_time', 'latitude', 'longitude']],
            get_position=['longitude', 'latitude'],
            radius=100,
            extruded=True,
            pickable=True,
            elevation_scale=4,
            elevation_range=[0, 1000],
        ),
    ],
))

# ------------------------------------------------------ Charts with Plotly
st.subheader(f"Breakdown by minute between {hour}:00 and {hour + 1}:00")
# filtering data in DF through hour filter
filtered_df = vehicles_df[
    (vehicles_df['date_time'].dt.hour >= hour) & (vehicles_df['date_time'].dt.hour < (hour + 1))
    ]

# creating new DF only with histogram data to load into plotly bar
hist = np.histogram(filtered_df['date_time'].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({'minute': range(60), 'crashes': hist})
# Plotly Chart
fig = px.bar(chart_data, x="minute", y="crashes", hover_data=['minute', 'crashes'], height=400)
st.write(fig)

# ------------------------------------------------------ Final Chart
st.header("Top five dangerous streets by affected type")
selection = st.selectbox(label='Afected type of people', options=['Pedestrians', 'Cyclists', 'Motorists'])

# this could be done better than showed in course project

if selection == 'Pedestrians':
    st.write(vehicles_df.query("injured_pedestrians >=1") \
                 [['on_street_name', 'injured_pedestrians']].nlargest(5, 'injured_pedestrians').dropna(how='any'))
elif selection == 'Cyclists':
    st.write(vehicles_df.query("injured_cyclists >=1") \
                 [['on_street_name', 'injured_cyclists']].nlargest(5, 'injured_cyclists').dropna(how='any'))
elif selection == 'Motorists':
    st.write(vehicles_df.query("injured_motorists >=1") \
                 [['on_street_name', 'injured_motorists']].nlargest(5, 'injured_motorists').dropna(how='any'))

# ------------------------------------------------------ Final Box to Show Raw Data
# Adding an optional checkbox with raw data in the app:
if st.checkbox("Show Raw Data", False):
    st.subheader("Raw Data")
    st.write(vehicles_df)
