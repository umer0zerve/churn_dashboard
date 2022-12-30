import streamlit as st
import pandas as pd
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from utils import utils 


helper = utils()

st.set_page_config(layout="wide")

name, authenticator, authentication_status = helper.login_page()

if authentication_status == False:
    st.error('Username/password is incorrect')
if authentication_status == None:
    st.warning('Please enter your username and password')

if authentication_status:
    authenticator.logout('Logout', 'main')
    st.write(f'Welcome *{name}*')
    
    # Display the logo in the sidebar
    image1,icp,image2 = st.columns((2,8,2))
    image1.image("./logo.png", width=250)
    image2.image("./zerve_logo.jfif", width=250)
    st.markdown(
        """
        <style>
        .reportview-container .main .block-container{max-width:100%;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("Membership Pause Prediction Dashboard")

    # Load the data
    df = pd.read_csv("./predictions.csv")
    df2 = pd.read_csv('./gyms.csv', usecols =['gym_id','gym_name','gps_latitude','gps_longitude'])
    # Remove rows with missing values
    df = df.dropna()
    df["user_id"] = df["user_id"].astype(int)
    df["membership_product_id"] = df["membership_product_id"].astype(int)
    # Create the dropdown filters
    f1, f2,f3= st.columns(3)


    gym_name = f1.selectbox("Gym Name", ["All"] + df["gym_name"].unique().tolist())
    gender = f2.selectbox("Gender", ["All"] + df["gender"].unique().tolist())
    age_group = f3.selectbox("Age Group", ["All"] + df["age_group"].unique().tolist())

    # Filter the data based on the selected options
    filtered_data = df
    if gym_name != "All":
        filtered_data = filtered_data[filtered_data["gym_name"] == gym_name]
    if gender != "All":
        filtered_data = filtered_data[filtered_data["gender"] == gender]
    if age_group != "All":
        filtered_data = filtered_data[filtered_data["age_group"] == age_group]


    kpi1, kpi2= st.columns(2)
    # create three columns
    kpi1.metric(
        label="Avg Pause Probability",
        value=round(filtered_data['pause_probability'].mean(),ndigits=3))

    # create three columns
    kpi2.metric(
        label="Avg Pause Probability",
        value=round(filtered_data['no_pause_probability'].mean(),ndigits=3))

    col1, col2 = st.columns(2)
    # Display the filtered data
    with col1:
        st.header('Filtered Data')
        st.dataframe(filtered_data)
        st.dataframe(df.style.apply(helper.highlight_survived, axis=1))
        st.dataframe(df.style.applymap(helper.color_survived, subset=['pause_probability']))


    with col2:
        st.header('Gym Location')
        map_data = filtered_data.merge(df2,on='gym_name')
        map_data = map_data.rename(columns={'gps_latitude': 'latitude', 'gps_longitude': 'longitude'})
        st.map(map_data)


    col3, col4 = st.columns(2)
    with col3:
        st.header('Age Group')
        age_fig = helper.age_chart(filtered_data)
        st.plotly_chart(age_fig)

    with col4:
        st.header('Gender')
        age_fig = helper.gender_chart(filtered_data)
        st.plotly_chart(age_fig)

    # Dsiplay map
    actionbutton1, actionbutton2, actionbutton3, actionbutton4 = st.columns(4)
    # Add a button to download the filtered data
    if actionbutton1.button("Download as CSV"):
        st.dataframe.download(filtered_data)

    # Send Email 
    if actionbutton2.button('Email CSV'):
        email = helper.send_email(st.text_input('Write your email id'), 'Predictions', df)






