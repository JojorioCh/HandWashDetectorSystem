import streamlit as st
from databaseHWD import *

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
        st.dataframe(database[["Time", column_to_search]].reset_index(drop='index'))
    else:
        st.warning(f"Column '{column_to_search}' not found in the DataFrame.")

