from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import plotly.express as px
import plotly.graph_objects as go 
import yaml
import streamlit as st
import streamlit_authenticator as stauth
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
import pandas as pd
import streamlit as st


class utils:
    def __init__(self):
        pass
    
    # Authentication
    def login_page(self):
        #st.set_page_config(layout="centered")

        # Display the logo in the sidebar
        #image1,icp,image2 = st.columns((2,8,2))
        #image1.image("./logo.png", width=250)
        #st.markdown(
         #   """
         #   <style>
         #   .reportview-container .main .block-container{max-width:100%;}
       # </style>
         #   """,
           # unsafe_allow_html=True,
        #)

        with open('./credentials.yml') as file:
            config = yaml.safe_load(file)

        authenticator = stauth.Authenticate(
            config['credentials'],
            config['cookie']['name'],
            config['cookie']['key'],
            config['cookie']['expiry_days'],
            config['preauthorized']
        )


        name, authentication_status, username = authenticator.login('Login', 'main')

        return name, authenticator, authentication_status

    # Bar plot showing age and gender based churn percentage
    def age_chart(self,data):
        age = data.groupby(['gym_name','age_group','gender','membership_product_id'])['pause_probability'].value_counts(normalize=True).mul(100).reset_index(name='chance')
        age = age.groupby(['age_group','gender'])['chance'].mean().round().reset_index(name='pause_chance')
        fig = px.histogram(age,x='age_group',y='pause_chance',color="gender", pattern_shape="gender", color_discrete_map = {'Male':'Lightblue','Female':'Pink'})
        fig.update_yaxes(title_text="Percentage", secondary_y=False)
        return fig

    def gender_chart(self,data):
        colors = ['gold', 'mediumturquoise']
        gender = data.groupby('gender')['pause_probability'].mean().mul(100).round().reset_index(name='pause_chance')

        fig = go.Figure(data=[go.Pie(labels=['Female','Male'],
                                    values=gender['pause_chance'])])
        fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=20,
                        marker=dict(colors=colors, line=dict(color='#000000', width=2)))
        return fig

    def send_email(self,send_to, subject, df):
        send_from = "umer@zerve.io"
        password = "Zerve@1234"
        message = """\
        <p><strong>This is a test email&nbsp;</strong></p>
        <p><br></p>
        <p><strong>Greetings&nbsp;</strong><br><strong>Alexandre&nbsp;    </strong></p>
        """
   
        multipart = MIMEMultipart()
        multipart["From"] = send_from
        multipart["To"] = send_to
        multipart["Subject"] = subject  
        attachment = MIMEApplication(df.to_csv())
        attachment["Content-Disposition"] = 'attachment; filename=" {}"'.format(f"{subject}.csv")
        multipart.attach(attachment)
        multipart.attach(MIMEText(message, "html"))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(multipart["From"], password)
        server.sendmail(multipart["From"], multipart["To"], multipart.as_string())
        server.quit()


    def color_pause(self,val):
        color = 'Indianred' if val > 0.7 else 'Lightgreen'
        return f'background-color: {color}'

    # To filter
    def filter_dataframe(self,df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds a UI on top of a dataframe to let viewers filter columns

        Args:
            df (pd.DataFrame): Original dataframe

        Returns:
            pd.DataFrame: Filtered dataframe
        """
        modify = st.checkbox("Add filters")

        if not modify:
            return df

        df = df.copy()

        # Try to convert datetimes into a standard format (datetime, no timezone)
        for col in df.columns:
            if is_object_dtype(df[col]):
                try:
                    df[col] = pd.to_datetime(df[col])
                except Exception:
                    pass

            if is_datetime64_any_dtype(df[col]):
                df[col] = df[col].dt.tz_localize(None)

        modification_container = st.container()

        with modification_container:
            to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
            for column in to_filter_columns:
                left, right = st.columns((1, 20))
                # Treat columns with < 10 unique values as categorical
                if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                    user_cat_input = right.multiselect(
                        f"Values for {column}",
                        df[column].unique(),
                        default=list(df[column].unique()),
                    )
                    df = df[df[column].isin(user_cat_input)]
                elif is_numeric_dtype(df[column]):
                    _min = float(df[column].min())
                    _max = float(df[column].max())
                    step = (_max - _min) / 100
                    user_num_input = right.slider(
                        f"Values for {column}",
                        min_value=_min,
                        max_value=_max,
                        value=(_min, _max),
                        step=step,
                    )
                    df = df[df[column].between(*user_num_input)]
                elif is_datetime64_any_dtype(df[column]):
                    user_date_input = right.date_input(
                        f"Values for {column}",
                        value=(
                            df[column].min(),
                            df[column].max(),
                        ),
                    )
                    if len(user_date_input) == 2:
                        user_date_input = tuple(map(pd.to_datetime, user_date_input))
                        start_date, end_date = user_date_input
                        df = df.loc[df[column].between(start_date, end_date)]
                else:
                    user_text_input = right.text_input(
                        f"Substring or regex in {column}",
                    )
                    if user_text_input:
                        df = df[df[column].astype(str).str.contains(user_text_input)]

        return df


