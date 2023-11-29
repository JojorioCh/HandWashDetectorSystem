import streamlit as st
from databaseHWD import *
import os
import sys
from firebase_admin import db

def restart_streamlit():
    os.execv(sys.executable, ['python'] + sys.argv)

# Function to create or get session state
def get_session_state():
    if 'button_clicked' not in st.session_state:
        st.session_state.button_clicked = False

# Function to send data to Firebase Realtime Database
def send_data_to_firebase(data):
    db.reference().update(data)

# Get or create session state
get_session_state()

btn_lbl = 'Switch LED ON/OFF'
# Create a button to light LED up
button_clicked = st.button(btn_lbl)

key = "LED_VAL"
# Update session state if the button is clicked
if button_clicked:
    st.session_state.button_clicked = not st.session_state.button_clicked

# Display a message based on the button state
if st.session_state.button_clicked:
    send_data_to_firebase({key:1})
    st.markdown('<p style="color: green;">The LED is currently ON</p>', unsafe_allow_html=True)
else:
    send_data_to_firebase({key:0})
    st.markdown('<p style="color: red;">The LED is currently OFF</p>', unsafe_allow_html=True)

# Caution message in red
st.title("Refresh Button")
caution_message = """
    <p style='color:red; font-size:20px;'>
        <strong>Caution:</strong> You need to refresh the App every time you use it
    </p>
"""
st.markdown(caution_message, unsafe_allow_html=True)

if st.button("Refresh"):
    st.write("Refreshing...")
    restart_streamlit()

st.title("Database of Handwashing Detection System")
df = database.reset_index(drop='index')

# Display the DataFrame
# st.dataframe(df)

# Add a text input for column selection
column_to_search = st.selectbox("Select a column to search:", database.columns[1:])

# Add a button to trigger the search
search_button = st.button("Search")

# Perform search when the button is clicked
if search_button:
    if column_to_search in df.columns:
        st.subheader(f"Search Results for {column_to_search}:")
        st.dataframe(database[["Time", column_to_search]].dropna().reset_index(drop='index'))
    else:
        st.warning(f"Column '{column_to_search}' not found in the DataFrame.")
