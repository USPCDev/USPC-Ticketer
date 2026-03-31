import streamlit as st
from pyairtable import Api

def airtable_single_ticket_assigner(first_name, last_name, mobile_number, email, form_category, event_order_id, form_ticket_type, available_ticket_filter_formula):
    with st.spinner("Processing..."):
        api = Api(st.secrets["airtable"]["PAT"])
        base = api.base(st.secrets["airtable"]["BASE_ID"])
        single_ticket_orders_base = base.table("Single Ticket Orders")
        single_tickets_base = base.table("Single Tickets")

        # 1. CREATE CUSTOMER ORDER RECORD
        single_ticket_order_record = single_ticket_orders_base.create({
            "First Name": first_name,
            "Last Name": last_name,
            "Mobile Number": mobile_number,
            "Email": email,
            "Form Category": form_category,
            "Form Event Order ID": event_order_id,
            "Form Ticket Type": form_ticket_type
        })
        single_ticket_order_id = single_ticket_order_record["id"]

        # 2. FIND FIRST AVAILABLE TICKET
        available_tickets = single_tickets_base.all(
            formula=available_ticket_filter_formula,
            sort=["Auto ID"],
            max_records=1
        )

        if not available_tickets:
            st.error("No available tickets at this time!")
            st.stop()
        
        ticket = available_tickets[0]
        ticket_record_id = ticket["id"]

        # 3. LINK THE FIRST AVAILABLE TICKET TO THE CURRENT CUSTOMER
        single_ticket_orders_base.update(single_ticket_order_id, {
            "Single Tickets (Linked)": [ticket_record_id]
        })

        # 4. MARK THE LINKED TICKET AS ASSIGNED
        single_tickets_base.update(ticket_record_id, {
            "Assigned": True,
            "Ticket Status": "On Hold",
            "Payment Status": "Pending"
        })

def airtable_family_ticket_assigner(first_name, last_name, mobile_number, email, form_category, event_order_id, form_ticket_type, available_ticket_filter_formula):
    with st.spinner("Processing..."):
        api = Api(st.secrets["airtable"]["PAT"])
        base = api.base(st.secrets["airtable"]["BASE_ID"])
        family_ticket_orders_base = base.table("Family Ticket Orders")
        family_tickets_base = base.table("Family Tickets")

        # 1. CREATE CUSTOMER ORDER RECORD
        family_ticket_order_record = family_ticket_orders_base.create({
            "First Name": first_name,
            "Last Name": last_name,
            "Mobile Number": mobile_number,
            "Email": email,
            "Form Category": form_category,
            "Form Event Order ID": event_order_id,
            "Form Ticket Type": form_ticket_type
        })
        family_ticket_order_id = family_ticket_order_record["id"]

        # 2. FIND FIRST AVAILABLE TICKET
        available_tickets = family_tickets_base.all(
            formula=available_ticket_filter_formula,
            sort=["Auto ID"],
            max_records=1
        )

        if not available_tickets:
            st.error("No available tickets at this time!")
            st.stop()

        ticket = available_tickets[0]
        ticket_record_id = ticket["id"]

        # 3. LINK THE FIRST AVAILABLE TICKET TO THE CURRENT CUSTOMER
        family_ticket_orders_base.update(family_ticket_order_id, {
            "Family Tickets (Linked)": [ticket_record_id]  # Linked field
        })

        # 4. MARK THE LINKED TICKET AS ASSIGNED
        family_tickets_base.update(ticket_record_id, {
            "Assigned": True,
            "Ticket Status": "On Hold",
            "Payment Status": "Pending"
        })

def airtable_get_unassigned_single_ticket_count(filter_formula):
    api = Api(st.secrets["airtable"]["PAT"])
    base = api.base(st.secrets["airtable"]["BASE_ID"])
    single_tickets_base = base.table("Single Tickets")

    # RETURN THE LENGTH OF THE FILTERED DATA
    # Using fields=["id"] to only fetch record IDs, which is more efficient
    return len(single_tickets_base.all(formula=filter_formula, fields=["Auto ID"]))

def airtable_get_unassigned_family_ticket_count(filter_formula):
    api = Api(st.secrets["airtable"]["PAT"])
    base = api.base(st.secrets["airtable"]["BASE_ID"])
    family_tickets_base = base.table("Family Tickets")

    # RETURN THE LENGTH OF THE FILTERED DATA
    # Using fields=["id"] to only fetch record IDs, which is more efficient
    return len(family_tickets_base.all(formula=filter_formula, fields=["Auto ID"]))
