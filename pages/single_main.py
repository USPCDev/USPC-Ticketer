import streamlit as st
from streamlit_phone_number import st_phone_number
from utils import ticketer_bg
from contextlib import contextmanager
from modules import airtable_functions
import phonenumbers
import re

#ticketer_bg.enable_svg_bg()

def booking_success_message(name, email):
    return f"Thank you for placing an order, **{name}**! Your order details will be sent to your email, **{email}**, shortly. If you haven't received any order confirmation email, please contact the support team whose numbers are provided in the homepage. Thank you once again!"

def mobile_number_verifier(mobile_number):
    try:
        # Enforce format: +<country_code><number> (digits only, no spaces)
        if not re.match(r"^\+\d+$", mobile_number):
            return False
        
        # Double check with phonenumbers
        # Passing None for region allows auto-detection from international format
        parsed = phonenumbers.parse(mobile_number, None)
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

    if st.button("Switch to **Family** Booking"):
        st.switch_page("pages/family_main.py")

AVAILABLE_TICKET_FORMULA = "AND({Assigned} = FALSE())"
AVAILABLE_TICKET_COUNT = airtable_functions.airtable_get_total_single_ticket_count(AVAILABLE_TICKET_FORMULA)
single_title = "Single Booking" if AVAILABLE_TICKET_COUNT > 150 else f"Single Booking ({AVAILABLE_TICKET_COUNT} total tickets left!)"
st.title(single_title)

GOLD_TAB, PLATINUM_TAB, DIAMOND_TAB = st.tabs(["Gold 🟡", "Platinum ⚪", "Diamond 🔵"], width="stretch")

with GOLD_TAB:

    # Checking for booking success status in session state
    if st.session_state.get("booking_success_single_gold"):
        st.balloons()
        single_gold_success_message = booking_success_message(st.session_state.booked_name_single_gold, st.session_state.booked_email_single_gold)
        st.success(single_gold_success_message, icon=":material/celebration:")

        # Reset
        del st.session_state.booking_success_single_gold
        del st.session_state.booked_name_single_gold
        del st.session_state.booked_email_single_gold
        if "pending_booking_single_gold" in st.session_state:
            del st.session_state.pending_booking_single_gold

    FORM_CATEGORY = "Single" # Differentiates between Single or Family Tickets
    EVENT_ORDER_ID = 73312205 # This is the Event Order ID
    FORM_TICKET_TYPE = "Single - Gold" # This is the Ticket Type initialised in the form
    AVAILABLE_TICKET_FILTER_FORMULA = "AND({Assigned} = FALSE(), {Ticket Type} = 'Single - Gold (£30)')"
    AVAILABLE_TICKET_COUNT = airtable_functions.airtable_get_unassigned_single_ticket_count(AVAILABLE_TICKET_FILTER_FORMULA)

    with st.form("single_gold_form", clear_on_submit=False, enter_to_submit=False):
        if AVAILABLE_TICKET_COUNT < 50:
            TICKET_TITLE_AND_STATUS_CONTAINER = st.container(border=False)
            with TICKET_TITLE_AND_STATUS_CONTAINER:

                TICKET_BOOKING_TYPE_COLUMN, TICKET_COUNT_COLUMN = st.columns([2, 1], gap="small", vertical_alignment="center", border=False)

                with TICKET_BOOKING_TYPE_COLUMN:
                    st.subheader("Gold Booking Form - :green[£30]/Person", divider="grey")

                with TICKET_COUNT_COLUMN:
                    st.metric("Remaining Gold Tickets", value=f"{AVAILABLE_TICKET_COUNT} Left!", border=True, label_visibility="visible")

        else:
            st.subheader("Gold Booking Form - :green[£30]/Person", divider="grey")

        FIRST_NAME = st.text_input("First Name", placeholder="Enter your first name", icon=":material/id_card:", key=f"single_gold_first_name_{st.session_state.get('single_gold_counter_first_name', 0)}")
        LAST_NAME = st.text_input("Last Name", placeholder="Enter your last name", icon=":material/id_card:", key=f"single_gold_last_name_{st.session_state.get('single_gold_counter_last_name', 0)}")
        EMAIL = st.text_input("Email", placeholder="Enter your email", icon=":material/mail:", help="Please enter the correct email.", key=f"single_gold_email_{st.session_state.get('single_gold_counter_email', 0)}")
        #mobile_number_data = st_phone_number("Mobile Number", placeholder="Enter your mobile number", default_country="GB", key=f"single_gold_mobile_number_{st.session_state.get('single_gold_counter_mobile_number', 0)}")
        #if mobile_number_data and isinstance(mobile_number_data, dict):
            #MOBILE_NUMBER = mobile_number_data.get("number")

        MOBILE_NUMBER = st.text_input("Mobile Number (All countries supported!)", placeholder="Enter your mobile number (e.g.: +447xxxxxxxxx)", icon=":material/call:", help="Please enter the correct mobile number in the provided format without spaces.", key=f"single_gold_mobile_number_{st.session_state.get('single_gold_counter_mobile_number', 0)}")

        is_single_gold_disabled = AVAILABLE_TICKET_COUNT is None or AVAILABLE_TICKET_COUNT == 0
        single_gold_form_button_label = "Request one **Gold** Order!" if not is_single_gold_disabled else "No More Tickets Available!"
        single_gold_form_button_icon = ":material/add_shopping_cart:" if not is_single_gold_disabled else ":material/block:"
        
        single_gold_form_submitted = st.form_submit_button(single_gold_form_button_label, icon=single_gold_form_button_icon, disabled=is_single_gold_disabled)
    
    @st.dialog("Confirm Booking", width="small")
    def show_single_gold_confirm_dialog(first_name, last_name, mobile_number, email, form_category, event_order_id, form_ticket_type, available_ticket_filter_formula):
        st.write(f"Are you sure you want to confirm the booking for **{first_name} {last_name}**?")

        with st_horizontal():
            if st.button("Confirm", type="primary", width="stretch", key="single_gold_confirm_button"):
                try:
                    airtable_functions.airtable_single_ticket_assigner(first_name, last_name, mobile_number, email, form_category, event_order_id, form_ticket_type, available_ticket_filter_formula)

                    st.session_state.booking_success_single_gold = True
                    st.session_state.booked_name_single_gold = first_name
                    st.session_state.booked_email_single_gold = email

                    # RESET SESSION STATES OF INPUT ELEMENTS (This is manual reset rather than using clear_on_submit=True)
                    st.session_state.single_gold_counter_first_name = st.session_state.get('single_gold_counter_first_name', 0) + 1
                    st.session_state.single_gold_counter_last_name = st.session_state.get('single_gold_counter_last_name', 0) + 1
                    st.session_state.single_gold_counter_email = st.session_state.get('single_gold_counter_email', 0) + 1
                    st.session_state.single_gold_counter_mobile_number = st.session_state.get('single_gold_counter_mobile_number', 0) + 1
                    st.rerun()

                except Exception as e:
                    st.error(f"Error: {e}")

            if st.button("Cancel", type="secondary", width="stretch", key="single_gold_cancel_button"):
                st.rerun()

    if single_gold_form_submitted:
        if not FIRST_NAME or not LAST_NAME or not MOBILE_NUMBER or not EMAIL:
            st.error("Please enter all the information!")
        elif not mobile_number_verifier(MOBILE_NUMBER):
            st.error("Please enter a valid mobile number in the example format, +447xxxxxxxxx, without spaces!")
        else:
            # Store data to be used in dialog
            st.session_state.pending_booking_single_gold = {
                "first_name": FIRST_NAME,
                "last_name": LAST_NAME,
                "mobile_number": MOBILE_NUMBER,
                "email": EMAIL,
                "category": FORM_CATEGORY,
                "event_order_id": EVENT_ORDER_ID,
                "ticket_type": FORM_TICKET_TYPE,
                "formula": AVAILABLE_TICKET_FILTER_FORMULA
            }
            show_single_gold_confirm_dialog(FIRST_NAME, LAST_NAME, MOBILE_NUMBER, EMAIL, FORM_CATEGORY, EVENT_ORDER_ID, FORM_TICKET_TYPE, AVAILABLE_TICKET_FILTER_FORMULA)

with PLATINUM_TAB:

    # Checking for booking success status in session state
    if st.session_state.get("booking_success_single_platinum"):
        st.balloons()
        single_platinum_success_message = booking_success_message(st.session_state.booked_name_single_platinum, st.session_state.booked_email_single_platinum)
        st.success(single_platinum_success_message, icon=":material/celebration:")

        # Reset
        del st.session_state.booking_success_single_platinum
        del st.session_state.booked_name_single_platinum
        del st.session_state.booked_email_single_platinum
        if "pending_booking_single_platinum" in st.session_state:
            del st.session_state.pending_booking_single_platinum

    FORM_CATEGORY = "Single" # Differentiates between Single or Family Tickets
    EVENT_ORDER_ID = 73312270 # This is the Event Order ID
    FORM_TICKET_TYPE = "Single - Platinum" # This is the Ticket Type initialised in the form
    AVAILABLE_TICKET_FILTER_FORMULA = "AND({Assigned} = FALSE(), {Ticket Type} = 'Single - Platinum (£40)')"
    AVAILABLE_TICKET_COUNT = airtable_functions.airtable_get_unassigned_single_ticket_count(AVAILABLE_TICKET_FILTER_FORMULA)

    with st.form("single_platinum_form", clear_on_submit=False, enter_to_submit=False):
        if AVAILABLE_TICKET_COUNT < 50:
            TICKET_TITLE_AND_STATUS_CONTAINER = st.container(border=False)
            with TICKET_TITLE_AND_STATUS_CONTAINER:

                TICKET_BOOKING_TYPE_COLUMN, TICKET_COUNT_COLUMN = st.columns([2.5, 1], gap="small", vertical_alignment="center", border=False)

                with TICKET_BOOKING_TYPE_COLUMN:
                    st.subheader("Platinum Booking Form - :green[£40]/Person", divider="grey")

                with TICKET_COUNT_COLUMN:
                    st.metric("Remaining Platinum Tickets", value=f"{AVAILABLE_TICKET_COUNT} Left!", border=True, label_visibility="visible")

        else:
            st.subheader("Platinum Booking Form - :green[£40]/Person", divider="grey")

        FIRST_NAME = st.text_input("First Name", placeholder="Enter your first name", icon=":material/id_card:", key=f"single_platinum_first_name_{st.session_state.get('single_platinum_counter_first_name', 0)}")
        LAST_NAME = st.text_input("Last Name", placeholder="Enter your last name", icon=":material/id_card:", key=f"single_platinum_last_name_{st.session_state.get('single_platinum_counter_last_name', 0)}")
        EMAIL = st.text_input("Email", placeholder="Enter your email", icon=":material/mail:", help="Please enter the correct email.", key=f"single_platinum_email_{st.session_state.get('single_platinum_counter_email', 0)}")
        #mobile_number_data = st_phone_number("Mobile Number", placeholder="Enter your mobile number", default_country="GB", key=f"single_platinum_mobile_number_{st.session_state.get('single_platinum_counter_mobile_number', 0)}")
        #if mobile_number_data and isinstance(mobile_number_data, dict):
            #MOBILE_NUMBER = mobile_number_data.get("number")

        MOBILE_NUMBER = st.text_input("Mobile Number (All countries supported!)", placeholder="Enter your mobile number (e.g.: +447xxxxxxxxx)", icon=":material/call:", help="Please enter the correct mobile number in the provided format without spaces.", key=f"single_platinum_mobile_number_{st.session_state.get('single_platinum_counter_mobile_number', 0)}")

        is_single_platinum_disabled = AVAILABLE_TICKET_COUNT is None or AVAILABLE_TICKET_COUNT == 0
        single_platinum_form_button_label = "Request one **Platinum** Order!" if not is_single_platinum_disabled else "No More Tickets Available!"
        single_platinum_form_button_icon = ":material/add_shopping_cart:" if not is_single_platinum_disabled else ":material/block:"

        single_platinum_form_submitted = st.form_submit_button(single_platinum_form_button_label, icon=single_platinum_form_button_icon, disabled=is_single_platinum_disabled)

    @st.dialog("Confirm Booking", width="small")
    def show_single_platinum_confirm_dialog(first_name, last_name, mobile_number, email, form_category, event_order_id, form_ticket_type, available_ticket_filter_formula):
        st.write(f"Are you sure you want to confirm the booking for **{first_name} {last_name}**?")

        with st_horizontal():
            if st.button("Confirm", type="primary", width="stretch", key="single_platinum_confirm_button"):
                try:
                    airtable_functions.airtable_single_ticket_assigner(first_name, last_name, mobile_number, email, form_category, event_order_id, form_ticket_type, available_ticket_filter_formula)

                    st.session_state.booking_success_single_platinum = True
                    st.session_state.booked_name_single_platinum = first_name
                    st.session_state.booked_email_single_platinum = email

                    # RESET SESSION STATES OF INPUT ELEMENTS
                    st.session_state.single_platinum_counter_first_name = st.session_state.get('single_platinum_counter_first_name', 0) + 1
                    st.session_state.single_platinum_counter_last_name = st.session_state.get('single_platinum_counter_last_name', 0) + 1
                    st.session_state.single_platinum_counter_email = st.session_state.get('single_platinum_counter_email', 0) + 1
                    st.session_state.single_platinum_counter_mobile_number = st.session_state.get('single_platinum_counter_mobile_number', 0) + 1
                    st.rerun()

                except Exception as e:
                    st.error(f"Error: {e}")

            if st.button("Cancel", type="secondary", width="stretch", key="single_platinum_cancel_button"):
                st.rerun()

    if single_platinum_form_submitted:
        if not FIRST_NAME or not LAST_NAME or not MOBILE_NUMBER or not EMAIL:
            st.error("Please enter all the information!")
        elif not mobile_number_verifier(MOBILE_NUMBER):
            st.error("Please enter a valid mobile number in the example format, +447xxxxxxxxx, without spaces!")
        else:
            # Store data to be used in dialog
            st.session_state.pending_booking_single_platinum = {
                "first_name": FIRST_NAME,
                "last_name": LAST_NAME,
                "mobile_number": MOBILE_NUMBER,
                "email": EMAIL,
                "category": FORM_CATEGORY,
                "event_order_id": EVENT_ORDER_ID,
                "ticket_type": FORM_TICKET_TYPE,
                "formula": AVAILABLE_TICKET_FILTER_FORMULA
            }
            show_single_platinum_confirm_dialog(FIRST_NAME, LAST_NAME, MOBILE_NUMBER, EMAIL, FORM_CATEGORY, EVENT_ORDER_ID, FORM_TICKET_TYPE, AVAILABLE_TICKET_FILTER_FORMULA)

with DIAMOND_TAB:

    # Checking for booking success status in session state
    if st.session_state.get("booking_success_single_diamond"):
        st.balloons()
        single_diamond_success_message = booking_success_message(st.session_state.booked_name_single_diamond, st.session_state.booked_email_single_diamond)
        st.success(single_diamond_success_message, icon=":material/celebration:")

        # Reset
        del st.session_state.booking_success_single_diamond
        del st.session_state.booked_name_single_diamond
        del st.session_state.booked_email_single_diamond
        if "pending_booking_single_diamond" in st.session_state:
            del st.session_state.pending_booking_single_diamond

    FORM_CATEGORY = "Single" # Differentiates between Single or Family Tickets
    EVENT_ORDER_ID = 73312306 # This is the Event Order ID
    FORM_TICKET_TYPE = "Single - Diamond" # This is the Ticket Type initialised in the form
    AVAILABLE_TICKET_FILTER_FORMULA = "AND({Assigned} = FALSE(), {Ticket Type} = 'Single - Diamond (£50)')"
    AVAILABLE_TICKET_COUNT = airtable_functions.airtable_get_unassigned_single_ticket_count(AVAILABLE_TICKET_FILTER_FORMULA)

    with st.form("single_diamond_form", clear_on_submit=False, enter_to_submit=False):
        if AVAILABLE_TICKET_COUNT < 50:
            TICKET_TITLE_AND_STATUS_CONTAINER = st.container(border=False)
            with TICKET_TITLE_AND_STATUS_CONTAINER:

                TICKET_BOOKING_TYPE_COLUMN, TICKET_COUNT_COLUMN = st.columns([2.5, 1], gap="small", vertical_alignment="center", border=False)

                with TICKET_BOOKING_TYPE_COLUMN:
                    st.subheader("Diamond Booking Form - :green[£50]/Person", divider="grey")

                with TICKET_COUNT_COLUMN:
                    st.metric("Remaining Diamond Tickets", value=f"{AVAILABLE_TICKET_COUNT} Left!", border=True, label_visibility="visible")

        else:
            st.subheader("Diamond Booking Form - :green[£50]/Person", divider="grey")

        FIRST_NAME = st.text_input("First Name", placeholder="Enter your first name", icon=":material/id_card:", key=f"single_diamond_first_name_{st.session_state.get('single_diamond_counter_first_name', 0)}")
        LAST_NAME = st.text_input("Last Name", placeholder="Enter your last name", icon=":material/id_card:", key=f"single_diamond_last_name_{st.session_state.get('single_diamond_counter_last_name', 0)}")
        EMAIL = st.text_input("Email", placeholder="Enter your email", icon=":material/mail:", help="Please enter the correct email.", key=f"single_diamond_email_{st.session_state.get('single_diamond_counter_email', 0)}")
        #mobile_number_data = st_phone_number("Mobile Number", placeholder="Enter your mobile number", default_country="GB", key=f"single_diamond_mobile_number_{st.session_state.get('single_diamond_counter_mobile_number', 0)}")
        #if mobile_number_data and isinstance(mobile_number_data, dict):
            #MOBILE_NUMBER = mobile_number_data.get("number")

        MOBILE_NUMBER = st.text_input("Mobile Number (All countries supported!)", placeholder="Enter your mobile number (e.g.: +447xxxxxxxxx)", icon=":material/call:", help="Please enter the correct mobile number in the provided format without spaces.", key=f"single_diamond_mobile_number_{st.session_state.get('single_diamond_counter_mobile_number', 0)}")

        is_single_diamond_disabled = AVAILABLE_TICKET_COUNT is None or AVAILABLE_TICKET_COUNT == 0
        single_diamond_form_button_label = "Request one **Diamond** Order!" if not is_single_diamond_disabled else "No More Tickets Available!"
        single_diamond_form_button_icon = ":material/add_shopping_cart:" if not is_single_diamond_disabled else ":material/block:"

        single_diamond_form_submitted = st.form_submit_button(single_diamond_form_button_label, icon=single_diamond_form_button_icon, disabled=is_single_diamond_disabled)

    @st.dialog("Confirm Booking", width="small")
    def show_single_diamond_confirm_dialog(first_name, last_name, mobile_number, email, form_category, event_order_id, form_ticket_type, available_ticket_filter_formula):
        st.write(f"Are you sure you want to confirm the booking for **{first_name} {last_name}**?")

        with st_horizontal():
            if st.button("Confirm", type="primary", width="stretch", key="single_diamond_confirm_button"):
                try:
                    airtable_functions.airtable_single_ticket_assigner(first_name, last_name, mobile_number, email, form_category, event_order_id, form_ticket_type, available_ticket_filter_formula)

                    st.session_state.booking_success_single_diamond = True
                    st.session_state.booked_name_single_diamond = first_name
                    st.session_state.booked_email_single_diamond = email

                    # RESET SESSION STATES OF INPUT ELEMENTS
                    st.session_state.single_diamond_counter_first_name = st.session_state.get('single_diamond_counter_first_name', 0) + 1
                    st.session_state.single_diamond_counter_last_name = st.session_state.get('single_diamond_counter_last_name', 0) + 1
                    st.session_state.single_diamond_counter_email = st.session_state.get('single_diamond_counter_email', 0) + 1
                    st.session_state.single_diamond_counter_mobile_number = st.session_state.get('single_diamond_counter_mobile_number', 0) + 1
                    st.rerun()

                except Exception as e:
                    st.error(f"Error: {e}")

            if st.button("Cancel", type="secondary", width="stretch", key="single_diamond_cancel_button"):
                st.rerun()

    if single_diamond_form_submitted:
        if not FIRST_NAME or not LAST_NAME or not MOBILE_NUMBER or not EMAIL:
            st.error("Please enter all the information!")
        elif not mobile_number_verifier(MOBILE_NUMBER):
            st.error("Please enter a valid mobile number in the example format, +447xxxxxxxxx, without spaces!")
        else:
            # Store data to be used in dialog
            st.session_state.pending_booking_single_diamond = {
                "first_name": FIRST_NAME,
                "last_name": LAST_NAME,
                "mobile_number": MOBILE_NUMBER,
                "email": EMAIL,
                "category": FORM_CATEGORY,
                "event_order_id": EVENT_ORDER_ID,
                "ticket_type": FORM_TICKET_TYPE,
                "formula": AVAILABLE_TICKET_FILTER_FORMULA
            }
            show_single_diamond_confirm_dialog(FIRST_NAME, LAST_NAME, MOBILE_NUMBER, EMAIL, FORM_CATEGORY, EVENT_ORDER_ID, FORM_TICKET_TYPE, AVAILABLE_TICKET_FILTER_FORMULA)
