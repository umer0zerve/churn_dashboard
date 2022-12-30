from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import plotly.express as px
import plotly.graph_objects as go 
import yaml
import streamlit as st
import streamlit_authenticator as stauth


class utils:
    def __init__(self):
        pass

    def login_page(self):
        #st.set_page_config(layout="centered")

        # Display the logo in the sidebar
        image1,icp,image2 = st.columns((2,8,2))
        image1.image("./logo.png", width=250)
        st.markdown(
            """
            <style>
            .reportview-container .main .block-container{max-width:100%;}
        </style>
            """,
            unsafe_allow_html=True,
        )

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

    def age_chart(self,data):
        age = data.groupby(['gym_name','age_group','gender','membership_product_id'])['pause_probability'].value_counts(normalize=True).mul(100).reset_index(name='chance')
        age = age.groupby(['age_group','gender'])['chance'].mean().round().reset_index(name='pause_chance')
        fig = px.histogram(age,x='age_group',y='pause_chance',color="gender", pattern_shape="gender", color_discrete_map = {'Male':'Blue','Female':'Pink'})
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
        for receiver in send_to:
                multipart = MIMEMultipart()
                multipart["From"] = send_from
                multipart["To"] = receiver
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


    def highlight_survived(self,s):
        return ['background-color: green']*len(s) if s.pause_probability else ['background-color: red']*len(s)

    def color_survived(val):
        color = 'Red' if val > 0.7 else 'green'
        return f'background-color: {color}'
