import streamlit as st
from utils import ticketer_bg

#ticketer_bg.enable_svg_bg()

if st.button("Back to Home Page", icon=":material/arrow_back_ios_new:", type="primary"):
    if "booking_type" in st.session_state:
        del st.session_state.booking_type
    st.rerun()

st.title("Family Booking")

GOLD_TAB, PLATINUM_TAB, DIAMOND_TAB = st.tabs(["Gold 🟡", "Platinum ⚪", "Diamond 🔵"], width="stretch")

with GOLD_TAB:
    FORM_CATEGORY = "Family" # Differentiates between Single or Family Tickets
    EVENT_ORDER_ID = 73312442 # This is the Event Order ID
    FORM_TICKET_TYPE = "Family - Gold" # This is the Ticket Type initialised in the form

    with st.form("family_gold_form"):
        st.subheader("Gold Booking Form", divider="grey")
        FIRST_NAME = st.text_input("First Name", icon=":material/id_card:", key="family_gold_first_name")
        LAST_NAME = st.text_input("Last Name", icon=":material/id_card:", key="family_gold_last_name")
        EMAIL = st.text_input("Email", icon=":material/mail:", key="family_gold_email")
        form_submitted = st.form_submit_button("Confirm 4 Orders!")

    # BEGIN FORM LOGIC
    if form_submitted:
        if not FIRST_NAME or not LAST_NAME or not EMAIL:
            st.error("All fields are required.")
        else:
        
            # BEGIN AIRTABLE LOGIC
            from pyairtable import Api

            try:
                api = Api(st.secrets["airtable"]["PAT"])
                base = api.base(st.secrets["airtable"]["BASE_ID"])
                family_ticket_orders_base = base.table("Family Ticket Orders")
                family_tickets_base = base.table("Family Tickets")

                # 1. Create customer
                family_ticket_order_record = family_ticket_orders_base.create({
                    "First Name": FIRST_NAME,
                    "Last Name": LAST_NAME,
                    "Email": EMAIL,
                    "Form Category": FORM_CATEGORY,
                    "Form Event Order ID": EVENT_ORDER_ID,
                    "Form Ticket Type": FORM_TICKET_TYPE
                })
                family_ticket_order_id = family_ticket_order_record["id"]

                # 2. Find available ticket
                available_tickets = family_tickets_base.all(
                    formula="AND({Assigned} = FALSE(), {Ticket Type} = 'Family - Gold (£100)')",
                    sort=["Auto ID"],
                    max_records=1
                )

                if not available_tickets:
                    st.warning("No available tickets at this time.")
                else:
                    ticket = available_tickets[0]
                    ticket_record_id = ticket["id"]

                    # 3. Link ticket to customer
                    family_ticket_orders_base.update(family_ticket_order_id, {
                        "Family Tickets (Linked)": [ticket_record_id]  # Linked field
                    })

                    # 4. Mark ticket as assigned
                    family_tickets_base.update(ticket_record_id, {
                        "Assigned": True,
                        "Ticket Status": "On Hold",
                        "Payment Status": "Pending"
                    })

                    st.success("Form submitted and ticket assigned!")

            except Exception as e:
                st.error(f"Error submitting customer data to Airtable: {e}")

with PLATINUM_TAB:
    FORM_CATEGORY = "Family" # Differentiates between Single or Family Tickets
    EVENT_ORDER_ID = 73312475 # This is the Event Order ID
    FORM_TICKET_TYPE = "Family - Platinum" # This is the Ticket Type initialised in the form

    with st.form("family_platinum_form"):
        st.subheader("Platinum Booking Form", divider="grey")
        FIRST_NAME = st.text_input("First Name", icon=":material/id_card:", key="family_platinum_first_name")
        LAST_NAME = st.text_input("Last Name", icon=":material/id_card:", key="family_platinum_last_name")
        EMAIL = st.text_input("Email", icon=":material/mail:", key="family_platinum_email")
        form_submitted = st.form_submit_button("Confirm 4 Orders!")

    # BEGIN FORM LOGIC
    if form_submitted:
        if not FIRST_NAME or not LAST_NAME or not EMAIL:
            st.error("All fields are required.")
        else:
        
            # BEGIN AIRTABLE LOGIC
            from pyairtable import Api

            try:
                api = Api(st.secrets["airtable"]["PAT"])
                base = api.base(st.secrets["airtable"]["BASE_ID"])
                family_ticket_orders_base = base.table("Family Ticket Orders")
                family_tickets_base = base.table("Family Tickets")

                # 1. Create customer
                family_ticket_order_record = family_ticket_orders_base.create({
                    "First Name": FIRST_NAME,
                    "Last Name": LAST_NAME,
                    "Email": EMAIL,
                    "Form Category": FORM_CATEGORY,
                    "Form Event Order ID": EVENT_ORDER_ID,
                    "Form Ticket Type": FORM_TICKET_TYPE
                })
                family_ticket_order_id = family_ticket_order_record["id"]

                # 2. Find available ticket
                available_tickets = family_tickets_base.all(
                    formula="AND({Assigned} = FALSE(), {Ticket Type} = 'Family - Platinum (£150)')",
                    sort=["Auto ID"],
                    max_records=1
                )

                if not available_tickets:
                    st.warning("No available tickets at this time.")
                else:
                    ticket = available_tickets[0]
                    ticket_record_id = ticket["id"]

                    # 3. Link ticket to customer
                    family_ticket_orders_base.update(family_ticket_order_id, {
                        "Family Tickets (Linked)": [ticket_record_id]  # Linked field
                    })

                    # 4. Mark ticket as assigned
                    family_tickets_base.update(ticket_record_id, {
                        "Assigned": True,
                        "Ticket Status": "On Hold",
                        "Payment Status": "Pending"
                    })

                    st.success("Form submitted and ticket assigned!")

            except Exception as e:
                st.error(f"Error submitting customer data to Airtable: {e}")

with DIAMOND_TAB:
    FORM_CATEGORY = "Family" # Differentiates between Single or Family Tickets
    EVENT_ORDER_ID = 73312496 # This is the Event Order ID
    FORM_TICKET_TYPE = "Family - Diamond" # This is the Ticket Type initialised in the form

    with st.form("family_diamond_form"):
        st.subheader("Diamond Booking Form", divider="grey")
        FIRST_NAME = st.text_input("First Name", icon=":material/id_card:", key="family_diamond_first_name")
        LAST_NAME = st.text_input("Last Name", icon=":material/id_card:", key="family_diamond_last_name")
        EMAIL = st.text_input("Email", icon=":material/mail:", key="family_diamond_email")
        form_submitted = st.form_submit_button("Confirm 4 Orders!")

    # BEGIN FORM LOGIC
    if form_submitted:
        if not FIRST_NAME or not LAST_NAME or not EMAIL:
            st.error("All fields are required.")
        else:
        
            # BEGIN AIRTABLE LOGIC
            from pyairtable import Api

            try:
                api = Api(st.secrets["airtable"]["PAT"])
                base = api.base(st.secrets["airtable"]["BASE_ID"])
                family_ticket_orders_base = base.table("Family Ticket Orders")
                family_tickets_base = base.table("Family Tickets")

                # 1. Create customer
                family_ticket_order_record = family_ticket_orders_base.create({
                    "First Name": FIRST_NAME,
                    "Last Name": LAST_NAME,
                    "Email": EMAIL,
                    "Form Category": FORM_CATEGORY,
                    "Form Event Order ID": EVENT_ORDER_ID,
                    "Form Ticket Type": FORM_TICKET_TYPE
                })
                family_ticket_order_id = family_ticket_order_record["id"]

                # 2. Find available ticket
                available_tickets = family_tickets_base.all(
                    formula="AND({Assigned} = FALSE(), {Ticket Type} = 'Family - Diamond (£175)')",
                    sort=["Auto ID"],
                    max_records=1
                )

                if not available_tickets:
                    st.warning("No available tickets at this time.")
                else:
                    ticket = available_tickets[0]
                    ticket_record_id = ticket["id"]

                    # 3. Link ticket to customer
                    family_ticket_orders_base.update(family_ticket_order_id, {
                        "Family Tickets (Linked)": [ticket_record_id]  # Linked field
                    })

                    # 4. Mark ticket as assigned
                    family_tickets_base.update(ticket_record_id, {
                        "Assigned": True,
                        "Ticket Status": "On Hold",
                        "Payment Status": "Pending"
                    })

                    st.success("Form submitted and ticket assigned!")

            except Exception as e:
                st.error(f"Error submitting customer data to Airtable: {e}")
