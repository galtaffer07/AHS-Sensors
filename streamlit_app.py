import streamlit as st
import pandas as pd
import numpy as np
import datetime

st.title('AHS CSV File')

st.write(f"Pandas version: {pd.__version__}")

uploaded_file = st.file_uploader("Choose a CSV file that was uploaded from Metasys", type="csv") #forces user to upload file



if uploaded_file is not None:  #checks to see if file uploaded
    carbon_levels = pd.read_csv(uploaded_file, skipfooter = 3, engine = 'python', index_col=0)
    carbon_levels_without_empty_columns = carbon_levels[[c for c in carbon_levels.columns if not c.startswith('Unnamed: ')]]  #removes the 175 empty columns at end of dataset
    pd.DataFrame.iteritems = pd.DataFrame.items
    pd.set_option("display.max.columns", None)
    #carbon_levels.dropna(axis = 1, inplace = True)
    #st.write("Before dropping NaNs:", carbon_levels_without_empty_columns)
    carbon_levels_without_empty_columns.dropna(axis = 0)
    #st.write("After dropping NaNs:", carbon_levels_without_empty_columns)

    

    #PROCESS FOR FILTERING
    Holidays_for_script = [
        datetime.date(2024, 1, 1),
        datetime.date(2024, 1, 15),
        datetime.date(2024, 2, 19),
        datetime.date(2024, 2, 20),
        datetime.date(2024, 2, 21),
        datetime.date(2024, 2, 22),
        datetime.date(2024, 2, 23),
        datetime.date(2024, 4, 15),
        datetime.date(2024, 4, 16),
        datetime.date(2024, 4, 17),
        datetime.date(2024, 4, 18),
        datetime.date(2024, 4, 19),
        datetime.date(2024, 5, 27),
        datetime.date(2024, 6, 19)
        #datetime.date(2019, 2, 18), #when the data starts - feb break
        #datetime.date(2019, 2, 19),
        #datetime.date(2019, 2, 20),
        #datetime.date(2019, 2, 21),
        #datetime.date(2019, 2, 22),
        #datetime.date(2019, 4, 15), #april break
        #datetime.date(2019, 4, 16),
        #datetime.date(2019, 4, 17),
        #datetime.date(2019, 4, 18),
        #datetime.date(2019, 4, 19),
        #datetime.date(2019, 5, 27) #memorial day
    ] 

    early_release_days = [
        datetime.date(2024, 1, 26),
        datetime.date(2024, 3, 8),
        datetime.date(2024, 5, 3)
        #datetime.date(2019, 2, 1),
        #datetime.date(2019, 3, 15),
        #datetime.date(2019, 5, 3)
    ]
    SCHOOL_START_TIME = datetime.time(8, 15) #7:45 for old data, 8:15 for new
    NORMAL_RELEASE_TIME = datetime.time(2, 51) #2:20 for old data, 2:51 for new
    EARLY_RELEASE_TIME = datetime.time(11, 30) #10:50 for old data, 11:30 for new

    carbon_levels_without_empty_columns.index = pd.to_datetime(carbon_levels_without_empty_columns.index)
    #st.write(carbon_levels.index)
    #st.write(carbon_levels.index.time)

    time_is_not_notschool = ~np.isin(carbon_levels_without_empty_columns.index.time, (pd.date_range("8:00", "15:00", freq = "1min").time))
    carbon_levels_school = carbon_levels_without_empty_columns[~time_is_not_notschool] #filters out of school hours
    #st.write("After filtering out school hours:", carbon_levels_school)


    time_is_not_weekend = ~np.isin(carbon_levels_school.index.weekday, [5,6]) #filters weekends
    carbon_levels_not_weekends = carbon_levels_school[time_is_not_weekend]
    #st.write("After filtering out weekends:", carbon_levels_not_weekends)

    #st.write(carbon_levels_not_weekends)

    time_is_not_holiday = ~np.isin(carbon_levels_not_weekends.index.date, Holidays_for_script) #filters holidays
    carbon_levels_without_holidays = carbon_levels_not_weekends[time_is_not_holiday]
    #st.write("After filtering out holidays:", carbon_levels_without_holidays)

    is_early_release_day = np.isin(carbon_levels_without_holidays.index.date, early_release_days) #filters early release days
    is_within_early_release_hours = (
        is_early_release_day
        & (carbon_levels_without_holidays.index.time >= SCHOOL_START_TIME)
        & (carbon_levels_without_holidays.index.time <= EARLY_RELEASE_TIME)
    )
    is_within_normal_school_hours = (
        ~is_early_release_day
        & (carbon_levels_without_holidays.index.time >= SCHOOL_START_TIME)
        & (carbon_levels_without_holidays.index.time <= NORMAL_RELEASE_TIME)
    )
    carbon_levels_in_normal_school_hours = carbon_levels_without_holidays[
        (is_within_early_release_hours | is_within_normal_school_hours)
    ]
    #st.write("After filtering out early release days:", carbon_levels_without_holidays)
    
    
    
    
    week = carbon_levels_without_holidays.index.to_period('W-MON')
    month = carbon_levels_without_holidays.index.to_period('M')
    grouped_by_week = carbon_levels_without_holidays.groupby(week) #makes a dataset that groups times by week
    grouped_by_month = carbon_levels_without_holidays.groupby(month) #makes a dataset that groups all times by month
    
    #FINDING RANGE OF DATA TO USE
    sorted_column = carbon_levels_without_holidays['Cafe UV08 ZN08 CO2'].sort_values()
    first_benchmark = sorted_column.quantile(0.25)
    last_benchmark = sorted_column.quantile(0.75)
    data_range = last_benchmark - first_benchmark
    data_within_range = carbon_levels_without_holidays[(carbon_levels_without_holidays['Cafe UV08 ZN08 CO2'] >= first_benchmark) & (carbon_levels_without_holidays['Cafe UV08 ZN08 CO2'] <= last_benchmark)]
    
    #st.write(str(carbon_levels_without_holidays['CC RTU06 ZN-T'].quantile(0.25)) + "-" + str(carbon_levels_without_holidays['CC RTU06 ZN-T'].quantile(0.75)))
    
    #st.write(carbon_levels_without_holidays)
    check_base = carbon_levels.drop(columns = carbon_levels.columns[0], axis = 1)

    selected_sensor = st.selectbox('Select a sensor:', list(carbon_levels_without_holidays.columns))
    if selected_sensor:
        st.write(f'Sensor: {selected_sensor}')

        st.write("Weekly values:")
        weekly_values = grouped_by_week[selected_sensor].mean()
        for i, value in weekly_values.items():
            if "CO2" in selected_sensor:
                st.write(f"Week {i}: {value:.1f} ppm")
            else:
                st.write(f"Week {i}: {value:.1f}°F")
    
    #st.write("Weekly values: " + str(grouped_by_week['RM309 ZN14 Q CO2'].mean())) 
    #st.write(grouped_by_month['RM309 ZN14 Q CO2'].mean()) #prints out monthly averages
    
    v = "input"
    terminate_loop = False
    targ1 = 70
    targ2 = 80   #please change as needed
    
    def flag_sensors(df, min_level=1600, max_level=1900):
        flagged_sensors = []
        for sensor in df.columns:
            if df[sensor].between(min_level, max_level).any():
                flagged_sensors.append(sensor)
        return flagged_sensors
    
    def sort_sensors(df, min_level=1600, max_level=1900):
        high = []
        medium = []
        light = []
    
        for sensor in df.columns:
            count = df[sensor].between(min_level, max_level).sum()
            if count >= 50:
                high.append(sensor)
            elif 5 <= count < 25:
                medium.append(sensor)
            elif count > 0:
                light.append(sensor)
    
        return high, medium, light
    
    def broken_sensors(df, min_level=1900, max_level=5000):
        broken_sensors = []
        for sensor in df.columns:
            if df[sensor].between(min_level, max_level).any():
                broken_sensors.append(sensor)
            return broken_sensors
    
    def find_rooms_needing_AC(df):
        sensor_medians={}
    
        for sensor in df.columns:
            top_temps = df[sensor].nlargest(21)
            sensor_medians[sensor] = top_temps.median()
    
        sorted_sensors = sorted(sensor_medians.items(), key=lambda x: x[1], reverse = True)
        return sorted_sensors
    
    temperature = [col for col in carbon_levels_without_holidays.columns if 'CO2' not in col.upper()]#checks to see if columns in dataset do not have CO2 in name => temperature sensor
    st.write("### Sensors Needing AC (Sorted by Median Temperature)")

    # Toggle button to show/hide the sensor list
    if 'show_sensors' not in st.session_state:
        st.session_state.show_sensors = False  # Initialize the toggle state

    # Button to toggle the sensor list
    if st.button("Toggle Sensor List"):
        st.session_state.show_sensors = not st.session_state.show_sensors

    # Display results if the button has been clicked
    if st.session_state.show_sensors:
        sorted_rooms = find_rooms_needing_AC(carbon_levels_without_holidays[temperature])
        for sensor, median in sorted_rooms:
            st.write(f"**{sensor}**: {median:.1f}°F")
    
    #st.write(find_max_temperatures(carbon_levels_without_holidays))
    morning = ~np.isin(carbon_levels_without_holidays.index.time, (pd.date_range("8:00", "9:30", freq = "1min").time)) #This will be used to denote the time periods in early morning
    carbon_levels_test = carbon_levels_without_holidays[~morning]
    #st.write(carbon_levels_test)
    new_name = input("Enter a sensor name to check: ")
    if (carbon_levels_test[new_name].quantile(0.65) < 68):
        st.write("Bad system.")
        st.write(carbon_levels_test[new_name].quantile(0.65))
    else:
        st.write("Good system with a temp of " + str(carbon_levels_test[new_name].quantile(0.65)) + " degrees Fahrenheit.")
    
    st.write(carbon_levels_without_holidays)
    st.write(flag_sensors(carbon_levels_test))
    
    high_list, medium_list, light_list = sort_sensors(carbon_levels_without_holidays)
    
    st.write("High sensors are " + str(high_list))
    st.write(medium_list)
    
    #st.write(broken_sensors(carbon_levels_without_holidays))
    
    while not terminate_loop:
        column_name = input("Enter a sensor name to check if its system is all-set: ")
        filter_level = input("Checking system for T or CO2: ").lower()
        if filter_level == "t":
            if column_name in carbon_levels_without_holidays.columns:
                if ((abs(carbon_levels_without_holidays[column_name].quantile(0.15)-targ1) < 2) and (abs(carbon_levels_without_holidays[column_name].quantile(0.85)- targ2) < 2)):
                    st.write("Good system")
                    st.write("\nThis system runs from " + str(carbon_levels_without_holidays[column_name].quantile(0.15)) + " F to " + str(carbon_levels_without_holidays[column_name].quantile(0.85)) + " F.")
                    while v != "yes":
                        v = input("Check again? ").lower()
                        if v == "no":
                            terminate_loop = True
                            break
                        elif v != "yes":
                            print("Invalid, try again: ")
    
                else:
                    st.write("Bad system")
                    st.write("\nThis system runs from " + str(carbon_levels_without_holidays[column_name].quantile(0.15)) + " F to " + str(carbon_levels_without_holidays[column_name].quantile(0.85)) + " F.")
                    while v != "yes":
                        v = input("Check again? ").lower()
                        if v == "no":
                            terminate_loop = True
                            break 
                        elif v != "yes":
                            st.write("Invalid, try again: ")
        elif filter_level == "co2":
            if column_name in carbon_levels_without_holidays.columns:
                if ((carbon_levels_without_holidays[column_name].quantile(0.45)) < 800):
                    st.write("Good system")
                    st.write("\nThis system runs from " + str(carbon_levels_without_holidays[column_name].quantile(0.45)) + " ppm to " + str(carbon_levels_without_holidays[column_name].quantile(0.85)) + " ppm.")
                    while v != "yes":
                        v = input("Check again? ").lower()
                        if v == "no":
                            terminate_loop = True
                            break
                        elif v != "yes":
                            st.write("Invalid, try again: ")
    
                else:
                    st.write("Bad system")
                    st.write("\nThis system runs from " + str(carbon_levels_without_holidays[column_name].quantile(0.45)) + " ppm to " + str(carbon_levels_without_holidays[column_name].quantile(0.85)) + " ppm.")
                    while v != "yes":
                        v = input("Check again? ").lower()
                        if v == "no":
                            terminate_loop = True
                            break 
                        elif v != "yes":
                            st.write("Invalid, try again: ")
    
    
    
            





                

    st.write("Here is your CSV file:")
    st.dataframe(carbon_levels_without_holidays)

 
else:
    st.write("Please upload a CSV file to proceed.") #if nothing then user is forced to upload

