import streamlit as st
import pandas as pd
import numpy as np
import datetime

st.title('AHS CSV File')


uploaded_file = st.file_uploader("Choose a CSV file that was uploaded from Metasys", type="csv") #forces user to upload file


if uploaded_file is not None:  #checks to see if file uploaded
    df = pd.read_csv(uploaded_file)

    st.write("Here is your CSV file:")
    st.dataframe(df)
 
else:
    st.write("Please upload a CSV file to proceed.") #if nothing then user is forced to upload

