import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)

if "authentication_status" not in st.session_state:
    st.session_state.authentication_status = None
if "name" not in st.session_state:
    st.session_state.name = None

if st.button("Login"):
    authenticator.login()
    st.session_state.authentication_status = True

if st.session_state["authentication_status"]:
    authenticator.logout()
    st.write(f'Welcome {st.session_state["name"]}')
    st.title('Welcome to AI Attendance')
elif st.session_state["authentication_status"] is True:
    st.error('Username/password is incorrect')
else:
    st.warning('Please click the Login button to authenticate.')