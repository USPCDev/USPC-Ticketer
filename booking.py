import streamlit as st
from datetime import datetime
from utils import asset_gen

def user_booking():

    @st.dialog(" ", width="small", dismissible=False)
    def select_booking():
        st.subheader("Welcome to the :blue[USPC Ticket Booking Platform]", width="stretch")

        options = ["Single", "Family"]
        booking_option = st.pills(
            "Select", options, label_visibility="collapsed", selection_mode="single", default=None, width="stretch"
        )
        if booking_option == "Single":
            st.session_state.booking_type = "single"
            st.rerun()
        elif booking_option == "Family":
            st.session_state.booking_type = "family"
            st.rerun()

        todays_date = datetime.now().strftime("%d/%m/%Y")
        st.text(f"Date: {todays_date}")

    # Asset generation
    asset_gen.home_logo("assets/USPC_LOGO.png")
    asset_gen.home_title("USPC Manchester")
    asset_gen.sub_home_title("Voice of Grace (Ticket Booking Platform)")

    with st.expander("Price & Booking Info", icon="⚠️", expanded=False):

        st.write("Price & Booking Info will come here->")

        # Tabs can be added to split price and booking info


    EMPTY_COL_1, BOOKING_BUTTON_COLUMN, EMPTY_COL_2 = st.columns([2, 1, 2], gap="small", vertical_alignment="center")
    with BOOKING_BUTTON_COLUMN:
        if st.button(":material/login:", type="primary", key="booking_primary", width="stretch", help="Start Booking!"):
            select_booking()
            st.stop()
        