import streamlit as st
from utils import ticketer_bg

#ticketer_bg.enable_svg_bg()

def main():
    st.set_page_config(
        page_title="USPC",
        page_icon="🎟️",
        initial_sidebar_state="auto",
        layout="centered",
        menu_items={
            "Report a bug": "mailto:jeffrygeorge58@gmail.com",
            "About": "USPC Ticket Booking Application Version 1.0 ® 2026. All Rights Reserved."
        }
    )

    # Hides the streamlit app header
    st.html("""
                <style>
                    .stAppHeader {
                        background: rgba(255,248,236,0.5);
                        -webkit-backdrop-filter: blur(5px);
                        backdrop-filter: blur(5px);
                    }
                </style>
            """)
    
    # Hides the streamlit main menu
    #st.html("""
                #<style>
                    #MainMenu {visibility: hidden;}
                #</style>
            #""")

    # Hides the streamlit main menu items
    st.html("""
                <style>
                    .stToolbarActions {visibility: collapse;}
                </style>
            """)

    # Hides the markdown text's anchor link icon
    st.html("""
                <style>
                    .block-container h1 a, 
                    .block-container h2 a, 
                    .block-container h3 a, 
                    .block-container h4 a, 
                    .block-container h5 a, 
                    .block-container h6 a {
                        display: none;
                        visibility: hidden;
                    }
                </style>
            """)
    
    nav_pages = [
        st.Page("home.py"),
        st.Page("pages/single_main.py"),
        st.Page("pages/family_main.py"),
        st.Page("pages/offline_single_main.py"),
        st.Page("pages/offline_family_main.py"),
    ]

    ticketer_pages = st.navigation(pages=nav_pages, position="hidden")
    
    ticketer_pages.run()

if __name__ == '__main__':
    main()
