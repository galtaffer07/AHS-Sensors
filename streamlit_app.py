import streamlit as st
import pandas as pd
import numpy as np
import datetime


st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)

carbon_levels = pd.read_csv(r"C:\Users\galta\Downloads\2023 Q3Q4 AHS ZN-T & CO2 UTC.csv", skipfooter = 3, engine = 'python', index_col=0) 
carbon_levels_without_empty_columns = carbon_levels[[c for c in carbon_levels.columns if not c.startswith('Unnamed: ')]]  #removes the 175 empty columns at end of dataset
pd.DataFrame.iteritems = pd.DataFrame.items
pd.set_option("display.max.columns", None)
#carbon_levels.dropna(axis = 1, inplace = True)
carbon_levels_without_empty_columns.dropna(axis = 0)
