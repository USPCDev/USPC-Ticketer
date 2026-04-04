import streamlit as st
import base64

# ----- HOME LOGO ENCODER -----
def home_logo(USPC_LOGO):
    with open(USPC_LOGO, "rb") as USPC_LOGO:
        ENCODED_STRING = base64.b64encode(USPC_LOGO.read())
    st.markdown(
        """
        <style>
        img {
            display: block;
            max-width: 30% !important;
            max-height: auto; 
            margin-left: auto; /* or margin: 0 auto; */
            margin-right: auto;
            margin-top: -30px;
            padding-bottom: 30px;
        }

        .logo {
            transition: transform .2s;
        }

        .logo:hover {
            transform: scale(1.10);
        }
        </style>
        """, unsafe_allow_html = True)
    
    st.markdown(
        f"""
        <img src = "data:image/{"png"};base64,{ENCODED_STRING.decode()}" class="logo">""", unsafe_allow_html = True)

# ----- HOME TITLE ENCODER -----
def home_title(HOME_TITLE):
    st.markdown(
            """
            <style>
                @import url(https://fonts.googleapis.com/css?family=Montserrat);
                .main_title {
                    text-align: center;
                    font-size: calc(1.0em + 5.0vmin) !important;
                    font-family: 'Montserrat', sans-serif;
                    font-weight: bold;
                    color: rgb(5, 31, 170) !important;
                }
            </style>
            """, unsafe_allow_html = True)

    st.markdown(f"<h1 class='main_title'>{HOME_TITLE}</h1>", unsafe_allow_html = True)

# ----- SUB HOME TITLE ENCODER -----
def sub_home_title(SUB_HOME_TITLE):
    st.markdown(
            """
            <style>
                @import url(https://fonts.googleapis.com/css?family=Montserrat);
                .sub_main_title {
                    text-align: center;
                    font-size: calc(1.0em + 2.5vmin) !important;
                    font-family: 'Montserrat', sans-serif;
                    font-weight: bold;
                    color: rgb(5, 31, 170) !important;
                }
            </style>
            """, unsafe_allow_html = True)

    st.markdown(f"<h2 class='sub_main_title'>{SUB_HOME_TITLE}</h2>", unsafe_allow_html = True)
