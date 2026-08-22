import streamlit as st
from streamlit_phone_number import st_phone_number
from utils import ticketer_bg
from contextlib import contextmanager
from modules import airtable_functions, expander_functions, stripe_functions
import phonenumbers
import re

#ticketer_bg.enable_svg_bg()

def booking_success_message(name, email, order_id, ticket_type, ticket_price, quantity=1):
    ticket_str = f"**{quantity}x {ticket_type} Ticket{'s' if quantity > 1 else ''}**" if quantity > 1 else f"**{ticket_type}**"
    return f"##### Thank you for placing an order, **{name}**!\nYour booking for {ticket_str} has been reserved for **{email}** and is currently pending payment. Please complete payment securely using Stripe.\n##### Order Summary:\nBooking Type: {ticket_str}\n\nReference No.: **{order_id}**\n\nTotal Price: **£{ticket_price}.00**\n\nOnce Stripe payment is completed, you will be redirected back to this app and your booking will be marked as **Paid**. Your ticket(s) will then be sent to your email."

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

expander_functions.info_expander("single_map", "single_segment")

AVAILABLE_TICKET_FORMULA = "AND({Assigned} = FALSE())"
AVAILABLE_TICKET_COUNT = airtable_functions.airtable_get_total_single_ticket_count(AVAILABLE_TICKET_FORMULA)
single_title = "Single Booking" if AVAILABLE_TICKET_COUNT > 150 else f"Single Booking ({AVAILABLE_TICKET_COUNT} total tickets left!)"
st.title(single_title)

DIAMOND_TAB, PLATINUM_TAB, GOLD_TAB = st.tabs(["**:blue-background[:blue[DIAMOND]]** 🔵", "**:grey-background[:grey[PLATINUM]]** ⚪", "**:orange-background[:orange[GOLD]]** 🟡"], width="stretch")

with GOLD_TAB:

    # Checking for booking success status in session state
    if st.session_state.get("booking_success_single_gold"):
        st.balloons()
        single_gold_success_message = booking_success_message(
            st.session_state.booked_name_single_gold,
            st.session_state.booked_email_single_gold,
            st.session_state.booked_order_id_single_gold,
            st.session_state.booked_ticket_type_single_gold,
            st.session_state.booked_ticket_price_single_gold,
            st.session_state.get("booked_ticket_quantity_single_gold", 1)
        )
        st.success(single_gold_success_message, icon=":material/celebration:")
        st.warning(
            "⚠️ **Important Payment Step:** Click the button below to pay on Stripe. **Do not close, refresh, or leave your browser** until you are returned here and see the green confirmation screen.",
            icon=":material/warning:"
        )

        # Reset
        del st.session_state.booking_success_single_gold
        del st.session_state.booked_name_single_gold
        del st.session_state.booked_email_single_gold
        del st.session_state.booked_order_id_single_gold
        del st.session_state.booked_ticket_type_single_gold
        del st.session_state.booked_ticket_price_single_gold
        if "booked_ticket_quantity_single_gold" in st.session_state:
            del st.session_state.booked_ticket_quantity_single_gold
        single_gold_checkout_url = st.session_state.get("booked_checkout_url_single_gold")
        if single_gold_checkout_url:
            st.link_button("Pay securely with Stripe", single_gold_checkout_url, type="primary", icon=":material/payment:", width="stretch")
            del st.session_state.booked_checkout_url_single_gold
        if "pending_booking_single_gold" in st.session_state:
            del st.session_state.pending_booking_single_gold

        if st.button("Close Message & Refresh", type="secondary", width="stretch", key="single_gold_refresh_button"):
            st.rerun()
    else:
        FORM_CATEGORY = "Single" # Differentiates between Single or Family Tickets
        EVENT_ORDER_ID = 73312205 # This is the Event Order ID
        FORM_TICKET_TYPE = "Single - Gold" # This is the Ticket Type initialised in the form
        UNIT_PRICE_GOLD = 30
        AVAILABLE_TICKET_FILTER_FORMULA = "AND({Assigned} = FALSE(), {Ticket Type} = 'Single - Gold (£30)')"
        AVAILABLE_TICKET_COUNT = airtable_functions.airtable_get_unassigned_single_ticket_count(AVAILABLE_TICKET_FILTER_FORMULA)

        if AVAILABLE_TICKET_COUNT < 50:
            TICKET_TITLE_AND_STATUS_CONTAINER = st.container(border=False)
            with TICKET_TITLE_AND_STATUS_CONTAINER:

                TICKET_BOOKING_TYPE_COLUMN, TICKET_COUNT_COLUMN = st.columns([2, 1], gap="small", vertical_alignment="center", border=False)

                with TICKET_BOOKING_TYPE_COLUMN:
                    st.subheader(f"Gold Booking Form - :green[£{UNIT_PRICE_GOLD}]/Person", divider="grey")

                with TICKET_COUNT_COLUMN:
                    st.metric("Remaining Gold Tickets", value=f"{AVAILABLE_TICKET_COUNT} Left!", border=True, label_visibility="visible")

        else:
            st.subheader(f"Gold Booking Form - :green[£{UNIT_PRICE_GOLD}]/Person", divider="grey")

        max_gold_tickets = min(3, AVAILABLE_TICKET_COUNT) if AVAILABLE_TICKET_COUNT else 1
        gold_quantity_options = list(range(1, max_gold_tickets + 1)) if max_gold_tickets >= 1 else [1]

        QUANTITY_GOLD = st.radio(
            "Total Tickets (Up to 3 tickets per single booking)",
            options=gold_quantity_options,
            format_func=lambda q: f"{q} Ticket{'s' if q > 1 else ''} (£{q * UNIT_PRICE_GOLD}.00)",
            index=0,
            horizontal=True,
            key=f"single_gold_quantity_{st.session_state.get('single_gold_counter_quantity', 0)}",
            help="You can book 1, 2, or 3 single tickets under your name. For 4 tickets, check out Family Booking!"
        )
        st.caption("💡 *You can add up to 2 additional tickets (total 3). Need 4 tickets? Switch to **Family Booking** for the 4-ticket bundle.*")

        with st.form("single_gold_form", clear_on_submit=False, enter_to_submit=False):
            FIRST_NAME = st.text_input("First Name", placeholder="Enter your first name", icon=":material/id_card:", key=f"single_gold_first_name_{st.session_state.get('single_gold_counter_first_name', 0)}")
            LAST_NAME = st.text_input("Last Name", placeholder="Enter your last name", icon=":material/id_card:", key=f"single_gold_last_name_{st.session_state.get('single_gold_counter_last_name', 0)}")
            EMAIL = st.text_input("Email", placeholder="Enter your email", icon=":material/mail:", help="Please enter the correct email.", key=f"single_gold_email_{st.session_state.get('single_gold_counter_email', 0)}")
            MOBILE_NUMBER = st.text_input("Mobile Number (All countries supported!)", placeholder="Enter your mobile number (e.g.: +447xxxxxxxxx)", icon=":material/call:", help="Please enter the correct mobile number in the provided format without spaces.", key=f"single_gold_mobile_number_{st.session_state.get('single_gold_counter_mobile_number', 0)}")

            is_single_gold_disabled = AVAILABLE_TICKET_COUNT is None or AVAILABLE_TICKET_COUNT == 0 or AVAILABLE_TICKET_COUNT < QUANTITY_GOLD
            single_gold_form_button_label = f"Request {QUANTITY_GOLD} Gold Ticket{'s' if QUANTITY_GOLD > 1 else ''} (£{QUANTITY_GOLD * UNIT_PRICE_GOLD}.00)" if not is_single_gold_disabled else "No More Tickets Available!"
            single_gold_form_button_icon = ":material/add_shopping_cart:" if not is_single_gold_disabled else ":material/block:"
            
            single_gold_form_submitted = st.form_submit_button(single_gold_form_button_label, icon=single_gold_form_button_icon, disabled=is_single_gold_disabled)

        @st.dialog("Confirm Booking", width="small")
        def show_single_gold_confirm_dialog(first_name, last_name, mobile_number, email, form_category, event_order_id, form_ticket_type, available_ticket_filter_formula, quantity):
            total_price = quantity * UNIT_PRICE_GOLD
            ticket_text = f"**{quantity} Gold Ticket{'s' if quantity > 1 else ''}**"
            st.write(f"Are you sure you want to confirm the booking for {ticket_text} for **{first_name} {last_name}** for a total of **£{total_price}.00**?")

            with st_horizontal():
                if st.button("Confirm", type="primary", width="stretch", key="single_gold_confirm_button"):
                    try:
                        booking = airtable_functions.airtable_create_pending_stripe_booking(
                            first_name, last_name, mobile_number, email, form_category, event_order_id, form_ticket_type, available_ticket_filter_formula, quantity=quantity
                        )
                        checkout_session = stripe_functions.create_checkout_session(
                            customer_email=email,
                            ticket_type=form_ticket_type,
                            order_record_id=booking["order_record_id"],
                            ticket_record_ids=booking["ticket_record_ids"],
                            quantity=quantity,
                            order_table_name=booking["order_table_name"],
                            ticket_table_name=booking["ticket_table_name"],
                        )
                        airtable_functions.airtable_update_order_stripe_session(booking["order_table_name"], booking["order_record_id"], checkout_session["session_id"])

                        st.session_state.booking_success_single_gold = True
                        st.session_state.booked_name_single_gold = first_name
                        st.session_state.booked_email_single_gold = email
                        st.session_state.booked_order_id_single_gold = booking["order_id"]
                        st.session_state.booked_ticket_type_single_gold = booking["ticket_type"]
                        st.session_state.booked_ticket_quantity_single_gold = quantity
                        st.session_state.booked_ticket_price_single_gold = checkout_session["amount_in_pounds"]
                        st.session_state.booked_checkout_url_single_gold = checkout_session["checkout_url"]

                        # RESET SESSION STATES OF INPUT ELEMENTS
                        st.session_state.single_gold_counter_first_name = st.session_state.get('single_gold_counter_first_name', 0) + 1
                        st.session_state.single_gold_counter_last_name = st.session_state.get('single_gold_counter_last_name', 0) + 1
                        st.session_state.single_gold_counter_email = st.session_state.get('single_gold_counter_email', 0) + 1
                        st.session_state.single_gold_counter_mobile_number = st.session_state.get('single_gold_counter_mobile_number', 0) + 1
                        st.session_state.single_gold_counter_quantity = st.session_state.get('single_gold_counter_quantity', 0) + 1
                        st.rerun()

                    except Exception as e:
                        st.error(f"Error: {e}")

                if st.button("Cancel", type="secondary", width="stretch", key="single_gold_cancel_button"):
                    st.rerun()

        if single_gold_form_submitted:
            if not FIRST_NAME or not LAST_NAME or not MOBILE_NUMBER or not EMAIL:
                st.error("Please enter all the information!")
            elif not mobile_number_verifier("".join(MOBILE_NUMBER.split())):
                st.error("Please enter a valid mobile number in the example format, +447xxxxxxxxx, without spaces!")
            else:
                # Store data to be used in dialog
                st.session_state.pending_booking_single_gold = {
                    "first_name": FIRST_NAME.strip(),
                    "last_name": LAST_NAME.strip(),
                    "mobile_number": "".join(MOBILE_NUMBER.split()),
                    "email": EMAIL.strip(),
                    "category": FORM_CATEGORY,
                    "event_order_id": EVENT_ORDER_ID,
                    "ticket_type": FORM_TICKET_TYPE,
                    "formula": AVAILABLE_TICKET_FILTER_FORMULA,
                    "quantity": QUANTITY_GOLD,
                }
                show_single_gold_confirm_dialog(FIRST_NAME.strip().title(), LAST_NAME.strip().title(), "".join(MOBILE_NUMBER.split()), EMAIL.strip(), FORM_CATEGORY, EVENT_ORDER_ID, FORM_TICKET_TYPE, AVAILABLE_TICKET_FILTER_FORMULA, QUANTITY_GOLD)

with PLATINUM_TAB:

    # Checking for booking success status in session state
    if st.session_state.get("booking_success_single_platinum"):
        st.balloons()
        single_platinum_success_message = booking_success_message(
            st.session_state.booked_name_single_platinum,
            st.session_state.booked_email_single_platinum,
            st.session_state.booked_order_id_single_platinum,
            st.session_state.booked_ticket_type_single_platinum,
            st.session_state.booked_ticket_price_single_platinum,
            st.session_state.get("booked_ticket_quantity_single_platinum", 1)
        )
        st.success(single_platinum_success_message, icon=":material/celebration:")
        st.warning(
            "⚠️ **Important Payment Step:** Click the button below to pay on Stripe. **Do not close, refresh, or leave your browser** until you are returned here and see the green confirmation screen.",
            icon=":material/warning:"
        )

        # Reset
        del st.session_state.booking_success_single_platinum
        del st.session_state.booked_name_single_platinum
        del st.session_state.booked_email_single_platinum
        del st.session_state.booked_order_id_single_platinum
        del st.session_state.booked_ticket_type_single_platinum
        del st.session_state.booked_ticket_price_single_platinum
        if "booked_ticket_quantity_single_platinum" in st.session_state:
            del st.session_state.booked_ticket_quantity_single_platinum
        single_platinum_checkout_url = st.session_state.get("booked_checkout_url_single_platinum")
        if single_platinum_checkout_url:
            st.link_button("Pay securely with Stripe", single_platinum_checkout_url, type="primary", icon=":material/payment:", width="stretch")
            del st.session_state.booked_checkout_url_single_platinum
        if "pending_booking_single_platinum" in st.session_state:
            del st.session_state.pending_booking_single_platinum

        if st.button("Close Message & Refresh", type="secondary", width="stretch", key="single_platinum_refresh_button"):
            st.rerun()
    else:
        FORM_CATEGORY = "Single" # Differentiates between Single or Family Tickets
        EVENT_ORDER_ID = 73312270 # This is the Event Order ID
        FORM_TICKET_TYPE = "Single - Platinum" # This is the Ticket Type initialised in the form
        UNIT_PRICE_PLATINUM = 40
        AVAILABLE_TICKET_FILTER_FORMULA = "AND({Assigned} = FALSE(), {Ticket Type} = 'Single - Platinum (£40)')"
        AVAILABLE_TICKET_COUNT = airtable_functions.airtable_get_unassigned_single_ticket_count(AVAILABLE_TICKET_FILTER_FORMULA)

        if AVAILABLE_TICKET_COUNT < 50:
            TICKET_TITLE_AND_STATUS_CONTAINER = st.container(border=False)
            with TICKET_TITLE_AND_STATUS_CONTAINER:

                TICKET_BOOKING_TYPE_COLUMN, TICKET_COUNT_COLUMN = st.columns([2.5, 1], gap="small", vertical_alignment="center", border=False)

                with TICKET_BOOKING_TYPE_COLUMN:
                    st.subheader(f"Platinum Booking Form - :green[£{UNIT_PRICE_PLATINUM}]/Person", divider="grey")

                with TICKET_COUNT_COLUMN:
                    st.metric("Remaining Platinum Tickets", value=f"{AVAILABLE_TICKET_COUNT} Left!", border=True, label_visibility="visible")

        else:
            st.subheader(f"Platinum Booking Form - :green[£{UNIT_PRICE_PLATINUM}]/Person", divider="grey")

        max_platinum_tickets = min(3, AVAILABLE_TICKET_COUNT) if AVAILABLE_TICKET_COUNT else 1
        platinum_quantity_options = list(range(1, max_platinum_tickets + 1)) if max_platinum_tickets >= 1 else [1]

        QUANTITY_PLATINUM = st.radio(
            "Total Tickets (Up to 3 tickets per single booking)",
            options=platinum_quantity_options,
            format_func=lambda q: f"{q} Ticket{'s' if q > 1 else ''} (£{q * UNIT_PRICE_PLATINUM}.00)",
            index=0,
            horizontal=True,
            key=f"single_platinum_quantity_{st.session_state.get('single_platinum_counter_quantity', 0)}",
            help="You can book 1, 2, or 3 single tickets under your name. For 4 tickets, check out Family Booking!"
        )
        st.caption("💡 *You can add up to 2 additional tickets (total 3). Need 4 tickets? Switch to **Family Booking** for the 4-ticket bundle.*")

        with st.form("single_platinum_form", clear_on_submit=False, enter_to_submit=False):
            FIRST_NAME = st.text_input("First Name", placeholder="Enter your first name", icon=":material/id_card:", key=f"single_platinum_first_name_{st.session_state.get('single_platinum_counter_first_name', 0)}")
            LAST_NAME = st.text_input("Last Name", placeholder="Enter your last name", icon=":material/id_card:", key=f"single_platinum_last_name_{st.session_state.get('single_platinum_counter_last_name', 0)}")
            EMAIL = st.text_input("Email", placeholder="Enter your email", icon=":material/mail:", help="Please enter the correct email.", key=f"single_platinum_email_{st.session_state.get('single_platinum_counter_email', 0)}")
            MOBILE_NUMBER = st.text_input("Mobile Number (All countries supported!)", placeholder="Enter your mobile number (e.g.: +447xxxxxxxxx)", icon=":material/call:", help="Please enter the correct mobile number in the provided format without spaces.", key=f"single_platinum_mobile_number_{st.session_state.get('single_platinum_counter_mobile_number', 0)}")

            is_single_platinum_disabled = AVAILABLE_TICKET_COUNT is None or AVAILABLE_TICKET_COUNT == 0 or AVAILABLE_TICKET_COUNT < QUANTITY_PLATINUM
            single_platinum_form_button_label = f"Request {QUANTITY_PLATINUM} Platinum Ticket{'s' if QUANTITY_PLATINUM > 1 else ''} (£{QUANTITY_PLATINUM * UNIT_PRICE_PLATINUM}.00)" if not is_single_platinum_disabled else "No More Tickets Available!"
            single_platinum_form_button_icon = ":material/add_shopping_cart:" if not is_single_platinum_disabled else ":material/block:"

            single_platinum_form_submitted = st.form_submit_button(single_platinum_form_button_label, icon=single_platinum_form_button_icon, disabled=is_single_platinum_disabled)

        @st.dialog("Confirm Booking", width="small")
        def show_single_platinum_confirm_dialog(first_name, last_name, mobile_number, email, form_category, event_order_id, form_ticket_type, available_ticket_filter_formula, quantity):
            total_price = quantity * UNIT_PRICE_PLATINUM
            ticket_text = f"**{quantity} Platinum Ticket{'s' if quantity > 1 else ''}**"
            st.write(f"Are you sure you want to confirm the booking for {ticket_text} for **{first_name} {last_name}** for a total of **£{total_price}.00**?")

            with st_horizontal():
                if st.button("Confirm", type="primary", width="stretch", key="single_platinum_confirm_button"):
                    try:
                        booking = airtable_functions.airtable_create_pending_stripe_booking(first_name, last_name, mobile_number, email, form_category, event_order_id, form_ticket_type, available_ticket_filter_formula, quantity=quantity)
                        checkout_session = stripe_functions.create_checkout_session(
                            customer_email=email,
                            ticket_type=form_ticket_type,
                            order_record_id=booking["order_record_id"],
                            ticket_record_ids=booking["ticket_record_ids"],
                            quantity=quantity,
                            order_table_name=booking["order_table_name"],
                            ticket_table_name=booking["ticket_table_name"],
                        )
                        airtable_functions.airtable_update_order_stripe_session(booking["order_table_name"], booking["order_record_id"], checkout_session["session_id"])

                        st.session_state.booking_success_single_platinum = True
                        st.session_state.booked_name_single_platinum = first_name
                        st.session_state.booked_email_single_platinum = email
                        st.session_state.booked_order_id_single_platinum  = booking["order_id"]
                        st.session_state.booked_ticket_type_single_platinum = booking["ticket_type"]
                        st.session_state.booked_ticket_quantity_single_platinum = quantity
                        st.session_state.booked_ticket_price_single_platinum = checkout_session["amount_in_pounds"]
                        st.session_state.booked_checkout_url_single_platinum = checkout_session["checkout_url"]

                        # RESET SESSION STATES OF INPUT ELEMENTS
                        st.session_state.single_platinum_counter_first_name = st.session_state.get('single_platinum_counter_first_name', 0) + 1
                        st.session_state.single_platinum_counter_last_name = st.session_state.get('single_platinum_counter_last_name', 0) + 1
                        st.session_state.single_platinum_counter_email = st.session_state.get('single_platinum_counter_email', 0) + 1
                        st.session_state.single_platinum_counter_mobile_number = st.session_state.get('single_platinum_counter_mobile_number', 0) + 1
                        st.session_state.single_platinum_counter_quantity = st.session_state.get('single_platinum_counter_quantity', 0) + 1
                        st.rerun()

                    except Exception as e:
                        st.error(f"Error: {e}")

                if st.button("Cancel", type="secondary", width="stretch", key="single_platinum_cancel_button"):
                    st.rerun()

        if single_platinum_form_submitted:
            if not FIRST_NAME or not LAST_NAME or not MOBILE_NUMBER or not EMAIL:
                st.error("Please enter all the information!")
            elif not mobile_number_verifier("".join(MOBILE_NUMBER.split())):
                st.error("Please enter a valid mobile number in the example format, +447xxxxxxxxx, without spaces!")
            else:
                # Store data to be used in dialog
                st.session_state.pending_booking_single_platinum = {
                    "first_name": FIRST_NAME.strip(),
                    "last_name": LAST_NAME.strip(),
                    "mobile_number": "".join(MOBILE_NUMBER.split()),
                    "email": EMAIL.strip(),
                    "category": FORM_CATEGORY,
                    "event_order_id": EVENT_ORDER_ID,
                    "ticket_type": FORM_TICKET_TYPE,
                    "formula": AVAILABLE_TICKET_FILTER_FORMULA,
                    "quantity": QUANTITY_PLATINUM,
                }
                show_single_platinum_confirm_dialog(FIRST_NAME.strip().title(), LAST_NAME.strip().title(), "".join(MOBILE_NUMBER.split()), EMAIL.strip(), FORM_CATEGORY, EVENT_ORDER_ID, FORM_TICKET_TYPE, AVAILABLE_TICKET_FILTER_FORMULA, QUANTITY_PLATINUM)

with DIAMOND_TAB:

    # Checking for booking success status in session state
    if st.session_state.get("booking_success_single_diamond"):
        st.balloons()
        single_diamond_success_message = booking_success_message(
            st.session_state.booked_name_single_diamond,
            st.session_state.booked_email_single_diamond,
            st.session_state.booked_order_id_single_diamond,
            st.session_state.booked_ticket_type_single_diamond,
            st.session_state.booked_ticket_price_single_diamond,
            st.session_state.get("booked_ticket_quantity_single_diamond", 1)
        )
        st.success(single_diamond_success_message, icon=":material/celebration:")
        st.warning(
            "⚠️ **Important Payment Step:** Click the button below to pay on Stripe. **Do not close, refresh, or leave your browser** until you are returned here and see the green confirmation screen.",
            icon=":material/warning:"
        )

        # Reset
        del st.session_state.booking_success_single_diamond
        del st.session_state.booked_name_single_diamond
        del st.session_state.booked_email_single_diamond
        del st.session_state.booked_order_id_single_diamond
        del st.session_state.booked_ticket_type_single_diamond
        del st.session_state.booked_ticket_price_single_diamond
        if "booked_ticket_quantity_single_diamond" in st.session_state:
            del st.session_state.booked_ticket_quantity_single_diamond
        single_diamond_checkout_url = st.session_state.get("booked_checkout_url_single_diamond")
        if single_diamond_checkout_url:
            st.link_button("Pay securely with Stripe", single_diamond_checkout_url, type="primary", icon=":material/payment:", width="stretch")
            del st.session_state.booked_checkout_url_single_diamond
        if "pending_booking_single_diamond" in st.session_state:
            del st.session_state.pending_booking_single_diamond

        if st.button("Close Message & Refresh", type="secondary", width="stretch", key="single_diamond_refresh_button"):
            st.rerun()
    else:
        FORM_CATEGORY = "Single" # Differentiates between Single or Family Tickets
        EVENT_ORDER_ID = 73312306 # This is the Event Order ID
        FORM_TICKET_TYPE = "Single - Diamond" # This is the Ticket Type initialised in the form
        UNIT_PRICE_DIAMOND = 50
        AVAILABLE_TICKET_FILTER_FORMULA = "AND({Assigned} = FALSE(), {Ticket Type} = 'Single - Diamond (£50)')"
        AVAILABLE_TICKET_COUNT = airtable_functions.airtable_get_unassigned_single_ticket_count(AVAILABLE_TICKET_FILTER_FORMULA)

        if AVAILABLE_TICKET_COUNT < 50:
            TICKET_TITLE_AND_STATUS_CONTAINER = st.container(border=False)
            with TICKET_TITLE_AND_STATUS_CONTAINER:

                TICKET_BOOKING_TYPE_COLUMN, TICKET_COUNT_COLUMN = st.columns([2.5, 1], gap="small", vertical_alignment="center", border=False)

                with TICKET_BOOKING_TYPE_COLUMN:
                    st.subheader(f"Diamond Booking Form - :green[£{UNIT_PRICE_DIAMOND}]/Person", divider="grey")

                with TICKET_COUNT_COLUMN:
                    st.metric("Remaining Diamond Tickets", value=f"{AVAILABLE_TICKET_COUNT} Left!", border=True, label_visibility="visible")

        else:
            st.subheader(f"Diamond Booking Form - :green[£{UNIT_PRICE_DIAMOND}]/Person", divider="grey")

        max_diamond_tickets = min(3, AVAILABLE_TICKET_COUNT) if AVAILABLE_TICKET_COUNT else 1
        diamond_quantity_options = list(range(1, max_diamond_tickets + 1)) if max_diamond_tickets >= 1 else [1]

        QUANTITY_DIAMOND = st.radio(
            "Total Tickets (Up to 3 tickets per single booking)",
            options=diamond_quantity_options,
            format_func=lambda q: f"{q} Ticket{'s' if q > 1 else ''} (£{q * UNIT_PRICE_DIAMOND}.00)",
            index=0,
            horizontal=True,
            key=f"single_diamond_quantity_{st.session_state.get('single_diamond_counter_quantity', 0)}",
            help="You can book 1, 2, or 3 single tickets under your name. For 4 tickets, check out Family Booking!"
        )
        st.caption("💡 *You can add up to 2 additional tickets (total 3). Need 4 tickets? Switch to **Family Booking** for the 4-ticket bundle.*")

        with st.form("single_diamond_form", clear_on_submit=False, enter_to_submit=False):
            FIRST_NAME = st.text_input("First Name", placeholder="Enter your first name", icon=":material/id_card:", key=f"single_diamond_first_name_{st.session_state.get('single_diamond_counter_first_name', 0)}")
            LAST_NAME = st.text_input("Last Name", placeholder="Enter your last name", icon=":material/id_card:", key=f"single_diamond_last_name_{st.session_state.get('single_diamond_counter_last_name', 0)}")
            EMAIL = st.text_input("Email", placeholder="Enter your email", icon=":material/mail:", help="Please enter the correct email.", key=f"single_diamond_email_{st.session_state.get('single_diamond_counter_email', 0)}")
            MOBILE_NUMBER = st.text_input("Mobile Number (All countries supported!)", placeholder="Enter your mobile number (e.g.: +447xxxxxxxxx)", icon=":material/call:", help="Please enter the correct mobile number in the provided format without spaces.", key=f"single_diamond_mobile_number_{st.session_state.get('single_diamond_counter_mobile_number', 0)}")

            is_single_diamond_disabled = AVAILABLE_TICKET_COUNT is None or AVAILABLE_TICKET_COUNT == 0 or AVAILABLE_TICKET_COUNT < QUANTITY_DIAMOND
            single_diamond_form_button_label = f"Request {QUANTITY_DIAMOND} Diamond Ticket{'s' if QUANTITY_DIAMOND > 1 else ''} (£{QUANTITY_DIAMOND * UNIT_PRICE_DIAMOND}.00)" if not is_single_diamond_disabled else "No More Tickets Available!"
            single_diamond_form_button_icon = ":material/add_shopping_cart:" if not is_single_diamond_disabled else ":material/block:"

            single_diamond_form_submitted = st.form_submit_button(single_diamond_form_button_label, icon=single_diamond_form_button_icon, disabled=is_single_diamond_disabled)

        @st.dialog("Confirm Booking", width="small")
        def show_single_diamond_confirm_dialog(first_name, last_name, mobile_number, email, form_category, event_order_id, form_ticket_type, available_ticket_filter_formula, quantity):
            total_price = quantity * UNIT_PRICE_DIAMOND
            ticket_text = f"**{quantity} Diamond Ticket{'s' if quantity > 1 else ''}**"
            st.write(f"Are you sure you want to confirm the booking for {ticket_text} for **{first_name} {last_name}** for a total of **£{total_price}.00**?")

            with st_horizontal():
                if st.button("Confirm", type="primary", width="stretch", key="single_diamond_confirm_button"):
                    try:
                        booking = airtable_functions.airtable_create_pending_stripe_booking(first_name, last_name, mobile_number, email, form_category, event_order_id, form_ticket_type, available_ticket_filter_formula, quantity=quantity)
                        checkout_session = stripe_functions.create_checkout_session(
                            customer_email=email,
                            ticket_type=form_ticket_type,
                            order_record_id=booking["order_record_id"],
                            ticket_record_ids=booking["ticket_record_ids"],
                            quantity=quantity,
                            order_table_name=booking["order_table_name"],
                            ticket_table_name=booking["ticket_table_name"],
                        )
                        airtable_functions.airtable_update_order_stripe_session(booking["order_table_name"], booking["order_record_id"], checkout_session["session_id"])

                        st.session_state.booking_success_single_diamond = True
                        st.session_state.booked_name_single_diamond = first_name
                        st.session_state.booked_email_single_diamond = email
                        st.session_state.booked_order_id_single_diamond = booking["order_id"]
                        st.session_state.booked_ticket_type_single_diamond = booking["ticket_type"]
                        st.session_state.booked_ticket_quantity_single_diamond = quantity
                        st.session_state.booked_ticket_price_single_diamond = checkout_session["amount_in_pounds"]
                        st.session_state.booked_checkout_url_single_diamond = checkout_session["checkout_url"]

                        # RESET SESSION STATES OF INPUT ELEMENTS
                        st.session_state.single_diamond_counter_first_name = st.session_state.get('single_diamond_counter_first_name', 0) + 1
                        st.session_state.single_diamond_counter_last_name = st.session_state.get('single_diamond_counter_last_name', 0) + 1
                        st.session_state.single_diamond_counter_email = st.session_state.get('single_diamond_counter_email', 0) + 1
                        st.session_state.single_diamond_counter_mobile_number = st.session_state.get('single_diamond_counter_mobile_number', 0) + 1
                        st.session_state.single_diamond_counter_quantity = st.session_state.get('single_diamond_counter_quantity', 0) + 1
                        st.rerun()

                    except Exception as e:
                        st.error(f"Error: {e}")

                if st.button("Cancel", type="secondary", width="stretch", key="single_diamond_cancel_button"):
                    st.rerun()

        if single_diamond_form_submitted:
            if not FIRST_NAME or not LAST_NAME or not MOBILE_NUMBER or not EMAIL:
                st.error("Please enter all the information!")
            elif not mobile_number_verifier("".join(MOBILE_NUMBER.split())):
                st.error("Please enter a valid mobile number in the example format, +447xxxxxxxxx, without spaces!")
            else:
                # Store data to be used in dialog
                st.session_state.pending_booking_single_diamond = {
                    "first_name": FIRST_NAME.strip(),
                    "last_name": LAST_NAME.strip(),
                    "mobile_number": "".join(MOBILE_NUMBER.split()),
                    "email": EMAIL.strip(),
                    "category": FORM_CATEGORY,
                    "event_order_id": EVENT_ORDER_ID,
                    "ticket_type": FORM_TICKET_TYPE,
                    "formula": AVAILABLE_TICKET_FILTER_FORMULA,
                    "quantity": QUANTITY_DIAMOND,
                }
                show_single_diamond_confirm_dialog(FIRST_NAME.strip().title(), LAST_NAME.strip().title(), "".join(MOBILE_NUMBER.split()), EMAIL.strip(), FORM_CATEGORY, EVENT_ORDER_ID, FORM_TICKET_TYPE, AVAILABLE_TICKET_FILTER_FORMULA, QUANTITY_DIAMOND)
