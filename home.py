import streamlit as st
from datetime import datetime
from utils import asset_gen
from modules import expander_functions

@st.dialog(" ", width="small", dismissible=True)
def select_booking():
    st.subheader("Welcome to :primary[USPC Manchester's Official Ticket Booker]", width="stretch")

    st.divider()

    st.warning("Please choose **Single** or **Family** option to proceed with the respective ticket creation process. Keep in mind that you may proceed with the **Family** option only if you are **four** in number 😊.")

    options = ["Single", "Family"]
    booking_option = st.pills(
        "Select", options, label_visibility="collapsed", selection_mode="single", default=None, width="stretch"
    )
    if booking_option == "Single":
        st.switch_page("pages/single_main.py")
    elif booking_option == "Family":
        st.switch_page("pages/family_main.py")

    todays_date = datetime.now().strftime("%d/%m/%Y")
    st.text(f"Date: {todays_date}")

# Asset generation
asset_gen.home_logo("assets/USPC_LOGO.png")
asset_gen.home_title("Voice of Grace - 2026")
asset_gen.sub_home_title("September 25, 2026")

st.divider()

expander_functions.info_expander("main_map", "main_segment")

EMPTY_COL_1, BOOKING_BUTTON_COLUMN, EMPTY_COL_2 = st.columns([2, 2, 2], gap="small", vertical_alignment="center")
with BOOKING_BUTTON_COLUMN:
    if st.button("BOOK NOW!", icon=":material/event_available:", type="primary", key="booking_primary", width="stretch", help="Start Booking!"):
        select_booking()

asset_gen.sub_home_title("🌟Meet the Stars!🌟")

st.divider()

SD_COLUMN, SS_COLUMN, FX_COLUMN = st.columns([1, 1, 1], gap="large", vertical_alignment="center", border=False)
with SD_COLUMN:
    asset_gen.artist_image("assets/SD_PIC.png")
    asset_gen.artist_name("Stephen Devassy")

with SS_COLUMN:
    asset_gen.artist_image("assets/SS_PIC.png")
    asset_gen.artist_name("Steven Samuel") 

with FX_COLUMN:
    asset_gen.artist_image("assets/FX_PIC.png")
    asset_gen.artist_name("Francis Xavier")
