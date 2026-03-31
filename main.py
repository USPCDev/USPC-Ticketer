import streamlit as st
from booking import user_booking
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
            "About": "USPC Ticket Booking Application Version 1.0 ® 2026 All Rights Reserved"
        }
    )

    # Hides the streamlit main menu
    st.html("""
                <style>
                    .stAppHeader {visibility: hidden;}
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

    if "booking_type" not in st.session_state:
        user_booking()
    else:
        # Once selected, show navigation
        if st.session_state.booking_type == "single":
            pages = st.navigation([st.Page("pages/single.py", title="Single Booking", icon=":material/person:")])
        else:
            pages = st.navigation([st.Page("pages/family.py", title="Family Booking", icon=":material/family_group:")])

        pages.run()

if __name__ == '__main__':
    main()
