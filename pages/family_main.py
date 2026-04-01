import streamlit as st
from streamlit_phone_number import st_phone_number
from utils import ticketer_bg
from contextlib import contextmanager
from modules import airtable_functions
import phonenumbers
import re

#ticketer_bg.enable_svg_bg()

def mobile_number_verifier(mobile_number):
    try:
        # Enforce format: +447xxxxxxxxx
        if not re.match(r"^\+447\d{9}$", mobile_number):
            return False
        
        # Double check with phonenumbers
        parsed = phonenumbers.parse(mobile_number, "GB")
        return phonenumbers.is_valid_number(parsed)
    
    except:
        return False

horizontal_style="""<style class="hide-element">
                        .element-container:has(.hide-element) {
                            display: none;
                        }
                        div[data-testid="stVerticalBlock"]:has(> .element-container .horizontal-marker) {
                            display: flex;
                            flex-direction: row !important;
                            flex-wrap: wrap;
                            gap: 0.5rem;
                            align-items: baseline;
                        }
                        div[data-testid="stVerticalBlock"]:has(> .element-container .horizontal-marker) div {
                            width: max-content !important;
                        }
                    </style>"""

@contextmanager
def st_horizontal():
    st.markdown(horizontal_style, unsafe_allow_html=True)
    with st.container():
        st.markdown('<span class="hide-element horizontal-marker"></span>', unsafe_allow_html=True)
        yield

with st_horizontal():
    if st.button(":material/arrow_back_ios_new:", type="primary", help="Back to Home Page"):
        st.switch_page("home.py")

    if st.button("Switch to **Single** Booking"):
        st.switch_page("pages/single_main.py")

AVAILABLE_TICKET_FORMULA = "AND({Assigned} = FALSE())"
AVAILABLE_TICKET_COUNT = airtable_functions.airtable_get_total_family_ticket_count(AVAILABLE_TICKET_FORMULA)
st.title(f"Family Booking ({AVAILABLE_TICKET_COUNT} tickets left!)")

GOLD_TAB, PLATINUM_TAB, DIAMOND_TAB = st.tabs(["Gold 🟡", "Platinum ⚪", "Diamond 🔵"], width="stretch")

with GOLD_TAB:
    FORM_CATEGORY = "Family" # Differentiates between Single or Family Tickets
    EVENT_ORDER_ID = 73312442 # This is the Event Order ID
    FORM_TICKET_TYPE = "Family - Gold" # This is the Ticket Type initialised in the form
    AVAILABLE_TICKET_FILTER_FORMULA = "AND({Assigned} = FALSE(), {Ticket Type} = 'Family - Gold (£100)')"
    AVAILABLE_TICKET_COUNT = airtable_functions.airtable_get_unassigned_family_ticket_count(AVAILABLE_TICKET_FILTER_FORMULA)

    with st.form("family_gold_form", clear_on_submit=False, enter_to_submit=False):
        TICKET_TITLE_AND_STATUS_CONTAINER = st.container(border=False)
        with TICKET_TITLE_AND_STATUS_CONTAINER:

            TICKET_BOOKING_TYPE_COLUMN, TICKET_COUNT_COLUMN = st.columns([2, 1], gap="small", vertical_alignment="center", border=False)

            with TICKET_BOOKING_TYPE_COLUMN:
                st.subheader("Gold Booking Form - :green[£100]/Family", divider="grey")

            with TICKET_COUNT_COLUMN:
                st.metric("Remaining Gold Tickets", value=f"{AVAILABLE_TICKET_COUNT} Left!", border=True, label_visibility="visible")

        FIRST_NAME = st.text_input("First Name", placeholder="Enter your first name", icon=":material/id_card:", key=f"family_gold_first_name_{st.session_state.get('family_gold_counter_first_name', 0)}")
        LAST_NAME = st.text_input("Last Name", placeholder="Enter your last name", icon=":material/id_card:", key=f"family_gold_last_name_{st.session_state.get('family_gold_counter_last_name', 0)}")
        EMAIL = st.text_input("Email", placeholder="Enter your email", icon=":material/mail:", help="Please enter the correct email.", key=f"family_gold_email_{st.session_state.get('family_gold_counter_email', 0)}")
        #mobile_number_data = st_phone_number("Mobile Number", placeholder="Enter your mobile number", default_country="GB", key=f"family_gold_mobile_number_{st.session_state.get('family_gold_counter_mobile_number', 0)}")
        #if mobile_number_data and isinstance(mobile_number_data, dict):
            #MOBILE_NUMBER = mobile_number_data.get("number")

        MOBILE_NUMBER = st.text_input("Mobile Number", placeholder="Enter your mobile number (e.g.: +447xxxxxxxxx)", icon=":material/call:", help="Please enter the correct mobile number in the provided format without spaces.", key=f"family_gold_mobile_number_{st.session_state.get('family_gold_counter_mobile_number', 0)}")

        is_family_gold_disabled = AVAILABLE_TICKET_COUNT is None or AVAILABLE_TICKET_COUNT == 0
        family_gold_form_button_label = "Request one **Gold** Order!" if not is_family_gold_disabled else "No More Tickets Available!"
        family_gold_form_button_icon = ":material/add_shopping_cart:" if not is_family_gold_disabled else ":material/block:"

        family_gold_form_submitted = st.form_submit_button(family_gold_form_button_label, icon=family_gold_form_button_icon, disabled=is_family_gold_disabled)

    @st.dialog("Confirm Booking", width="small")
    def show_family_gold_confirm_dialog(first_name, last_name, mobile_number, email, form_category, event_order_id, form_ticket_type, available_ticket_filter_formula):
        st.write(f"Are you sure you want to confirm the booking for **{first_name} {last_name}**?")

        with st_horizontal():
            if st.button("Confirm", type="primary", width="stretch", key="family_gold_confirm_button"):
                try:
                    airtable_functions.airtable_family_ticket_assigner(first_name, last_name, mobile_number, email, form_category, event_order_id, form_ticket_type, available_ticket_filter_formula)

                    st.session_state.booking_success_family_gold = True
                    st.session_state.booked_name_family_gold = first_name
                    st.session_state.booked_email_family_gold = email

                    # RESET SESSION STATES OF INPUT ELEMENTS (This is manual reset rather than using clear_on_submit=True)
                    st.session_state.family_gold_counter_first_name = st.session_state.get('family_gold_counter_first_name', 0) + 1
                    st.session_state.family_gold_counter_last_name = st.session_state.get('family_gold_counter_last_name', 0) + 1
                    st.session_state.family_gold_counter_email = st.session_state.get('family_gold_counter_email', 0) + 1
                    st.session_state.family_gold_counter_mobile_number = st.session_state.get('family_gold_counter_mobile_number', 0) + 1
                    st.rerun()

                except Exception as e:
                    st.error(f"Error: {e}")

            if st.button("Cancel", type="secondary", width="stretch", key="family_gold_cancel_button"):
                st.rerun()

    if family_gold_form_submitted:
        if not FIRST_NAME or not LAST_NAME or not MOBILE_NUMBER or not EMAIL:
            st.error("Please enter all the information!")
        elif not mobile_number_verifier(MOBILE_NUMBER):
            st.error("Please enter a valid mobile number in the format, +447xxxxxxxxx!")
        else:
            # Store data to be used in dialog
            st.session_state.pending_booking_family_gold = {
                "first_name": FIRST_NAME,
                "last_name": LAST_NAME,
                "mobile_number": MOBILE_NUMBER,
                "email": EMAIL,
                "category": FORM_CATEGORY,
                "event_order_id": EVENT_ORDER_ID,
                "ticket_type": FORM_TICKET_TYPE,
                "formula": AVAILABLE_TICKET_FILTER_FORMULA
            }
            show_family_gold_confirm_dialog(FIRST_NAME, LAST_NAME, MOBILE_NUMBER, EMAIL, FORM_CATEGORY, EVENT_ORDER_ID, FORM_TICKET_TYPE, AVAILABLE_TICKET_FILTER_FORMULA)

    # Check for success
    if st.session_state.get("booking_success_family_gold"):
        st.balloons()
        st.success(f"Thank you for placing an order, **{st.session_state.booked_name_family_gold}**! Your order details will be sent to your email, **{st.session_state.booked_email_family_gold}**, shortly. If you haven't received any order confirmation email, please contact the support team whose numbers are provided in the homepage. Thank you once again!", icon=":material/celebration:")

        # Reset
        del st.session_state.booking_success_family_gold
        del st.session_state.booked_name_family_gold
        del st.session_state.booked_email_family_gold
        if "pending_booking_family_gold" in st.session_state:
            del st.session_state.pending_booking_family_gold

with PLATINUM_TAB:
    FORM_CATEGORY = "Family" # Differentiates between Single or Family Tickets
    EVENT_ORDER_ID = 73312475 # This is the Event Order ID
    FORM_TICKET_TYPE = "Family - Platinum" # This is the Ticket Type initialised in the form
    AVAILABLE_TICKET_FILTER_FORMULA = "AND({Assigned} = FALSE(), {Ticket Type} = 'Family - Platinum (£150)')"
    AVAILABLE_TICKET_COUNT = airtable_functions.airtable_get_unassigned_family_ticket_count(AVAILABLE_TICKET_FILTER_FORMULA)

    with st.form("family_platinum_form", clear_on_submit=False, enter_to_submit=False):
        TICKET_TITLE_AND_STATUS_CONTAINER = st.container(border=False)
        with TICKET_TITLE_AND_STATUS_CONTAINER:

            TICKET_BOOKING_TYPE_COLUMN, TICKET_COUNT_COLUMN = st.columns([2.5, 1], gap="small", vertical_alignment="center", border=False)

            with TICKET_BOOKING_TYPE_COLUMN:
                st.subheader("Platinum Booking Form - :green[£150]/Family", divider="grey")

            with TICKET_COUNT_COLUMN:
                st.metric("Remaining Platinum Tickets", value=f"{AVAILABLE_TICKET_COUNT} Left!", border=True, label_visibility="visible")

        FIRST_NAME = st.text_input("First Name", placeholder="Enter your first name", icon=":material/id_card:", key=f"family_platinum_first_name_{st.session_state.get('family_platinum_counter_first_name', 0)}")
        LAST_NAME = st.text_input("Last Name", placeholder="Enter your last name", icon=":material/id_card:", key=f"family_platinum_last_name_{st.session_state.get('family_platinum_counter_last_name', 0)}")
        EMAIL = st.text_input("Email", placeholder="Enter your email", icon=":material/mail:", help="Please enter the correct email.", key=f"family_platinum_email_{st.session_state.get('family_platinum_counter_email', 0)}")
        #mobile_number_data = st_phone_number("Mobile Number", placeholder="Enter your mobile number", default_country="GB", key=f"family_platinum_mobile_number_{st.session_state.get('family_platinum_counter_mobile_number', 0)}")
        #if mobile_number_data and isinstance(mobile_number_data, dict):
            #MOBILE_NUMBER = mobile_number_data.get("number")

        MOBILE_NUMBER = st.text_input("Mobile Number", placeholder="Enter your mobile number (e.g.: +447xxxxxxxxx)", icon=":material/call:", help="Please enter the correct mobile number in the provided format without spaces.", key=f"family_platinum_mobile_number_{st.session_state.get('family_platinum_counter_mobile_number', 0)}")

        is_family_platinum_disabled = AVAILABLE_TICKET_COUNT is None or AVAILABLE_TICKET_COUNT == 0
        family_platinum_form_button_label = "Request one **Platinum** Order!" if not is_family_platinum_disabled else "No More Tickets Available!"
        family_platinum_form_button_icon = ":material/add_shopping_cart:" if not is_family_platinum_disabled else ":material/block:"

        family_platinum_form_submitted = st.form_submit_button(family_platinum_form_button_label, icon=family_platinum_form_button_icon, disabled=is_family_platinum_disabled)

    @st.dialog("Confirm Booking", width="small")
    def show_family_platinum_confirm_dialog(first_name, last_name, mobile_number, email, form_category, event_order_id, form_ticket_type, available_ticket_filter_formula):
        st.write(f"Are you sure you want to confirm the booking for **{first_name} {last_name}**?")

        with st_horizontal():
            if st.button("Confirm", type="primary", width="stretch", key="family_platinum_confirm_button"):
                try:
                    airtable_functions.airtable_family_ticket_assigner(first_name, last_name, mobile_number, email, form_category, event_order_id, form_ticket_type, available_ticket_filter_formula)

                    st.session_state.booking_success_family_platinum = True
                    st.session_state.booked_name_family_platinum = first_name
                    st.session_state.booked_email_family_platinum = email

                    # RESET SESSION STATES OF INPUT ELEMENTS
                    st.session_state.family_platinum_counter_first_name = st.session_state.get('family_platinum_counter_first_name', 0) + 1
                    st.session_state.family_platinum_counter_last_name = st.session_state.get('family_platinum_counter_last_name', 0) + 1
                    st.session_state.family_platinum_counter_email = st.session_state.get('family_platinum_counter_email', 0) + 1
                    st.session_state.family_platinum_counter_mobile_number = st.session_state.get('family_platinum_counter_mobile_number', 0) + 1
                    st.rerun()

                except Exception as e:
                    st.error(f"Error: {e}")

            if st.button("Cancel", type="secondary", width="stretch", key="family_platinum_cancel_button"):
                st.rerun()

    if family_platinum_form_submitted:
        if not FIRST_NAME or not LAST_NAME or not MOBILE_NUMBER or not EMAIL:
            st.error("Please enter all the information!")
        elif not mobile_number_verifier(MOBILE_NUMBER):
            st.error("Please enter a valid mobile number in the format, +447xxxxxxxxx!")
        else:
            # Store data to be used in dialog
            st.session_state.pending_booking_family_platinum = {
                "first_name": FIRST_NAME,
                "last_name": LAST_NAME,
                "mobile_number": MOBILE_NUMBER,
                "email": EMAIL,
                "category": FORM_CATEGORY,
                "event_order_id": EVENT_ORDER_ID,
                "ticket_type": FORM_TICKET_TYPE,
                "formula": AVAILABLE_TICKET_FILTER_FORMULA
            }
            show_family_platinum_confirm_dialog(FIRST_NAME, LAST_NAME, MOBILE_NUMBER, EMAIL, FORM_CATEGORY, EVENT_ORDER_ID, FORM_TICKET_TYPE, AVAILABLE_TICKET_FILTER_FORMULA)

    # Check for success
    if st.session_state.get("booking_success_family_platinum"):
        st.balloons()
        st.success(f"Thank you for placing an order, **{st.session_state.booked_name_family_platinum}**! Your order details will be sent to your email, **{st.session_state.booked_email_family_platinum}**, shortly. If you haven't received any order confirmation email, please contact the support team whose numbers are provided in the homepage. Thank you once again!", icon=":material/celebration:")

        # Reset
        del st.session_state.booking_success_family_platinum
        del st.session_state.booked_name_family_platinum
        del st.session_state.booked_email_family_platinum
        if "pending_booking_family_platinum" in st.session_state:
            del st.session_state.pending_booking_family_platinum

with DIAMOND_TAB:
    FORM_CATEGORY = "Family" # Differentiates between Single or Family Tickets
    EVENT_ORDER_ID = 73312496 # This is the Event Order ID
    FORM_TICKET_TYPE = "Family - Diamond" # This is the Ticket Type initialised in the form
    AVAILABLE_TICKET_FILTER_FORMULA = "AND({Assigned} = FALSE(), {Ticket Type} = 'Family - Diamond (£175)')"
    AVAILABLE_TICKET_COUNT = airtable_functions.airtable_get_unassigned_family_ticket_count(AVAILABLE_TICKET_FILTER_FORMULA)

    with st.form("family_diamond_form", clear_on_submit=False, enter_to_submit=False):
        TICKET_TITLE_AND_STATUS_CONTAINER = st.container(border=False)
        with TICKET_TITLE_AND_STATUS_CONTAINER:

            TICKET_BOOKING_TYPE_COLUMN, TICKET_COUNT_COLUMN = st.columns([2.5, 1], gap="small", vertical_alignment="center", border=False)

            with TICKET_BOOKING_TYPE_COLUMN:
                st.subheader("Diamond Booking Form - :green[£175]/Family", divider="grey")

            with TICKET_COUNT_COLUMN:
                st.metric("Remaining Diamond Tickets", value=f"{AVAILABLE_TICKET_COUNT} Left!", border=True, label_visibility="visible")

        FIRST_NAME = st.text_input("First Name", placeholder="Enter your first name", icon=":material/id_card:", key=f"family_diamond_first_name_{st.session_state.get('family_diamond_counter_first_name', 0)}")
        LAST_NAME = st.text_input("Last Name", placeholder="Enter your last name", icon=":material/id_card:", key=f"family_diamond_last_name_{st.session_state.get('family_diamond_counter_last_name', 0)}")
        EMAIL = st.text_input("Email", placeholder="Enter your email", icon=":material/mail:", help="Please enter the correct email.", key=f"family_diamond_email_{st.session_state.get('family_diamond_counter_email', 0)}")
        #mobile_number_data = st_phone_number("Mobile Number", placeholder="Enter your mobile number", default_country="GB", key=f"family_diamond_mobile_number_{st.session_state.get('family_diamond_counter_mobile_number', 0)}")
        #if mobile_number_data and isinstance(mobile_number_data, dict):
            #MOBILE_NUMBER = mobile_number_data.get("number")

        MOBILE_NUMBER = st.text_input("Mobile Number", placeholder="Enter your mobile number (e.g.: +447xxxxxxxxx)", icon=":material/call:", help="Please enter the correct mobile number in the provided format without spaces.", key=f"family_diamond_mobile_number_{st.session_state.get('family_diamond_counter_mobile_number', 0)}")

        is_family_diamond_disabled = AVAILABLE_TICKET_COUNT is None or AVAILABLE_TICKET_COUNT == 0
        family_diamond_form_button_label = "Request one **Diamond** Order!" if not is_family_diamond_disabled else "No More Tickets Available!"
        family_diamond_form_button_icon = ":material/add_shopping_cart:" if not is_family_diamond_disabled else ":material/block:"

        family_diamond_form_submitted = st.form_submit_button(family_diamond_form_button_label, icon=family_diamond_form_button_icon, disabled=is_family_diamond_disabled)

    @st.dialog("Confirm Booking", width="small")
    def show_family_diamond_confirm_dialog(first_name, last_name, mobile_number, email, form_category, event_order_id, form_ticket_type, available_ticket_filter_formula):
        st.write(f"Are you sure you want to confirm the booking for **{first_name} {last_name}**?")

        with st_horizontal():
            if st.button("Confirm", type="primary", width="stretch", key="family_diamond_confirm_button"):
                try:
                    airtable_functions.airtable_family_ticket_assigner(first_name, last_name, mobile_number, email, form_category, event_order_id, form_ticket_type, available_ticket_filter_formula)

                    st.session_state.booking_success_family_diamond = True
                    st.session_state.booked_name_family_diamond = first_name
                    st.session_state.booked_email_family_diamond = email

                    # RESET SESSION STATES OF INPUT ELEMENTS
                    st.session_state.family_diamond_counter_first_name = st.session_state.get('family_diamond_counter_first_name', 0) + 1
                    st.session_state.family_diamond_counter_last_name = st.session_state.get('family_diamond_counter_last_name', 0) + 1
                    st.session_state.family_diamond_counter_email = st.session_state.get('family_diamond_counter_email', 0) + 1
                    st.session_state.family_diamond_counter_mobile_number = st.session_state.get('family_diamond_counter_mobile_number', 0) + 1
                    st.rerun()

                except Exception as e:
                    st.error(f"Error: {e}")

            if st.button("Cancel", type="secondary", width="stretch", key="family_diamond_cancel_button"):
                st.rerun()

    if family_diamond_form_submitted:
        if not FIRST_NAME or not LAST_NAME or not MOBILE_NUMBER or not EMAIL:
            st.error("Please enter all the information!")
        elif not mobile_number_verifier(MOBILE_NUMBER):
            st.error("Please enter a valid mobile number in the format, +447xxxxxxxxx!")
        else:
            # Store data to be used in dialog
            st.session_state.pending_booking_family_diamond = {
                "first_name": FIRST_NAME,
                "last_name": LAST_NAME,
                "mobile_number": MOBILE_NUMBER,
                "email": EMAIL,
                "category": FORM_CATEGORY,
                "event_order_id": EVENT_ORDER_ID,
                "ticket_type": FORM_TICKET_TYPE,
                "formula": AVAILABLE_TICKET_FILTER_FORMULA
            }
            show_family_diamond_confirm_dialog(FIRST_NAME, LAST_NAME, MOBILE_NUMBER, EMAIL, FORM_CATEGORY, EVENT_ORDER_ID, FORM_TICKET_TYPE, AVAILABLE_TICKET_FILTER_FORMULA)

    # Check for success
    if st.session_state.get("booking_success_family_diamond"):
        st.balloons()
        st.success(f"Thank you for placing an order, **{st.session_state.booked_name_family_diamond}**! Your order details will be sent to your email, **{st.session_state.booked_email_family_diamond}**, shortly. If you haven't received any order confirmation email, please contact the support team whose numbers are provided in the homepage. Thank you once again!", icon=":material/celebration:")

        # Reset
        del st.session_state.booking_success_family_diamond
        del st.session_state.booked_name_family_diamond
        del st.session_state.booked_email_family_diamond
        if "pending_booking_family_diamond" in st.session_state:
            del st.session_state.pending_booking_family_diamond
