import streamlit as st
from databaseHWD import *
import sys
import os

def restart_streamlit():
    os.execv(sys.executable, ['python'] + sys.argv)

st.title("Database of Handwashing Detection System")
df = database.reset_index(drop='index')

# Display the DataFrame
# st.dataframe(df)

st.title("Streamlit Reboot Button Example")
    # Reboot button
    if st.button("Reboot"):
        st.write("Rebooting...")
        restart_streamlit()
        
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

