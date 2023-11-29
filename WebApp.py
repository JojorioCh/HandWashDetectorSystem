import streamlit as st
from databaseHWD import *
import os
import sys

def restart_streamlit():
    os.execv(sys.executable, ['python'] + sys.argv)

st.title("Refresh Button")
# Reboot button

# Caution message in red
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

