import streamlit as st
from datetime import datetime
from utils import asset_gen

def user_booking():

    @st.dialog(" ", width="small", dismissible=True)
    def select_booking():
        st.subheader("Welcome to the :blue[USPC Ticket Booking Platform]", width="stretch")

        st.divider()

        st.warning("Please choose **Single** or **Family** option to proceed with the respective ticket creation process. Keep in mind that you may proceed with the **Family** option only if you are **four** in number 😊.")

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
    asset_gen.home_title("Voice of Grace - 2026")

    st.divider()

    with st.expander("Price & Booking Info (Please read before proceeding)", icon=":material/info:", expanded=False):

        TARIFF_DETAILS_TAB, IMPORTANT_INFO_TAB, SUPPORT_TEAM_TAB = st.tabs(["Tariff Details", "Important Info", "Support Team"], width="stretch")

        with TARIFF_DETAILS_TAB:
            tariff_category_options = ["Single", "Family"]
            tariff_category_selection = st.segmented_control("Directions", tariff_category_options, default="Single", label_visibility="collapsed", selection_mode="single")

            if tariff_category_selection == "Single":
                st.subheader("Single Ticket Tariff Details", divider="grey")
                GOLD_COLUMN, PLATINUM_COLUMN, DIAMOND_COLUMN = st.columns([1, 1, 1], gap="small", vertical_alignment="center")

                with GOLD_COLUMN:
                    st.metric("Gold 🟡", value="£ 30", border=True)

                with PLATINUM_COLUMN:
                    st.metric("Platinum ⚪", value="£ 40", border=True)

                with DIAMOND_COLUMN:
                    st.metric("Diamond 🔵", value="£ 50", border=True)

            elif tariff_category_selection == "Family":
                st.subheader("Family Ticket Tariff Details", divider="grey")
                GOLD_COLUMN, PLATINUM_COLUMN, DIAMOND_COLUMN = st.columns([1, 1, 1], gap="small", vertical_alignment="center")

                with GOLD_COLUMN:
                    st.metric("Gold 🟡", value="£ 100", border=True)

                with PLATINUM_COLUMN:
                    st.metric("Platinum ⚪", value="£ 150", border=True)

                with DIAMOND_COLUMN:
                    st.metric("Diamond 🔵", value="£ 175", border=True)

        with IMPORTANT_INFO_TAB:
            st.subheader("Important Info", divider="grey")

            st.markdown("* **1 Ticket = 1 Seat**. For **Single** Tickets, as the name suggests, one order is equivalent to one ticket which is equivalent to one seat. For **Family** Tickets, each order is equivalent to four tickets which is equivalent to four seats. Please make sure that you are a family of four before proceeding for a **Family** Ticket.")

            st.markdown("* If you are a family of three, please proceed onto buying three **Single** Tickets but if you are family of five, for example, please proceed onto buying one **Family** Ticket and one additional **Single** Ticket (please make sure that details such as the *First Name*, *Last Name* & *Email* are the same while booking this additional ticket(s)).")

            st.markdown("* Seats can be shared by infants or children but if you decide to use a seat for your child, you are requested to pay the respective seat.")

            st.markdown("* Once an **Ticket Order** has been confirmed, an email will be sent to you with relevant information regarding your order along with payment instructions.")

            st.markdown("* Please make sure that once an order has been confirmed, the payment must be made within 7 days, otherwise, the ticket will be available for other users to buy. You may need to initiate a fresh booking.")

        with SUPPORT_TEAM_TAB:
            st.subheader("Support Team", divider="grey")
            PERSON1_COLUMN, PERSON2_COLUMN, PERSON3_COLUMN = st.columns([1, 1, 1], gap="small", vertical_alignment="center")

            with PERSON1_COLUMN:
                st.link_button("Mathew Varghese", icon=":material/call:", url="tel:+447967758301", width="stretch")

            with PERSON2_COLUMN:
                st.link_button("Binu Chacko", icon=":material/call:", url="tel:+447793975948", width="stretch")

            with PERSON3_COLUMN:
                st.link_button("Geoffry Mathew", icon=":material/call:", url="tel:+447464139381", width="stretch")

    EMPTY_COL_1, BOOKING_BUTTON_COLUMN, EMPTY_COL_2 = st.columns([2, 1, 2], gap="small", vertical_alignment="center")
    with BOOKING_BUTTON_COLUMN:
        if st.button("Book Here!", type="primary", key="booking_primary", width="stretch", help="Start Booking!"):
            select_booking()
            st.stop()
        