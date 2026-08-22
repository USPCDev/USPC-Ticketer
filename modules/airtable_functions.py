import streamlit as st
from pyairtable import Api


def _get_airtable_base():
    api = Api(st.secrets["airtable"]["PAT"])
    return api.base(st.secrets["airtable"]["BASE_ID"])


def _get_ticket_table_config(booking_category):
    if booking_category == "Single":
        return {
            "order_table_name": "Single Ticket Orders",
            "ticket_table_name": "Single Tickets",
            "linked_field_name": "Single Tickets (Linked)",
        }

    if booking_category == "Family":
        return {
            "order_table_name": "Family Ticket Orders",
            "ticket_table_name": "Family Tickets",
            "linked_field_name": "Family Tickets (Linked)",
        }

    raise ValueError(f"Unsupported booking category: {booking_category}")


def airtable_create_pending_stripe_booking(first_name, last_name, mobile_number, email, form_category, event_order_id, form_ticket_type, available_ticket_filter_formula, quantity=1):
    with st.spinner("Reserving ticket(s)..."):
        table_config = _get_ticket_table_config(form_category)
        base = _get_airtable_base()
        ticket_orders_base = base.table(table_config["order_table_name"])
        tickets_base = base.table(table_config["ticket_table_name"])

        # 1. FIND AVAILABLE TICKETS BEFORE CREATING AN ORDER
        available_tickets = tickets_base.all(
            formula=available_ticket_filter_formula,
            sort=["Auto ID"],
            max_records=quantity
        )

        if not available_tickets or len(available_tickets) < quantity:
            st.error(f"Only {len(available_tickets) if available_tickets else 0} ticket(s) available for this tier! Please adjust your quantity.")
            st.stop()

        ticket_record_ids = [ticket["id"] for ticket in available_tickets]

        # 2. CREATE CUSTOMER ORDER RECORD AS PAYMENT PENDING
        ticket_order_record = ticket_orders_base.create({
            "First Name": first_name,
            "Last Name": last_name,
            "Mobile Number": mobile_number,
            "Email": email,
            "Form Category": form_category,
            "Form Event Order ID": event_order_id,
            "Form Ticket Type": form_ticket_type,
            "Payment Status": "Pending"
        })
        ticket_order_id = ticket_order_record["id"]

        # 3. LINK ALL RESERVED TICKETS TO THE CURRENT CUSTOMER ORDER
        ticket_orders_base.update(ticket_order_id, {
            table_config["linked_field_name"]: ticket_record_ids
        })

        # 4. MARK ALL LINKED TICKETS AS RESERVED
        for ticket_rec_id in ticket_record_ids:
            tickets_base.update(ticket_rec_id, {
                "Assigned": True,
                "Ticket Status": "On Hold",
                "Payment Status": "Pending"
            })

        # 5. FETCH RELEVANT DETAILS OF THE RESERVED TICKETS
        first_ticket = tickets_base.get(ticket_record_ids[0])
        first_fields = first_ticket.get("fields", {})

        ticket_order_ids = []
        for tid in ticket_record_ids:
            t_data = tickets_base.get(tid)
            t_fields = t_data.get("fields", {})
            if t_fields.get("Order ID"):
                ticket_order_ids.append(str(t_fields.get("Order ID")))

        order_id_summary = ", ".join(ticket_order_ids) if ticket_order_ids else first_fields.get("Order ID")

        return {
            "order_record_id": ticket_order_id,
            "ticket_record_id": ticket_record_ids[0],
            "ticket_record_ids": ticket_record_ids,
            "quantity": quantity,
            "order_table_name": table_config["order_table_name"],
            "ticket_table_name": table_config["ticket_table_name"],
            "order_id": order_id_summary,
            "ticket_type": first_fields.get("Ticket Type"),
            "ticket_price": first_fields.get("Ticket Price"),
        }


def airtable_update_order_stripe_session(order_table_name, order_record_id, stripe_checkout_session_id):
    base = _get_airtable_base()
    order_table = base.table(order_table_name)

    order_table.update(order_record_id, {
        "Stripe Checkout Session ID": stripe_checkout_session_id
    })


def airtable_mark_stripe_booking_paid(order_table_name, ticket_table_name, order_record_id, ticket_record_id=None, ticket_record_ids=None, stripe_payment_intent_id=None):
    base = _get_airtable_base()
    order_table = base.table(order_table_name)
    ticket_table = base.table(ticket_table_name)

    order_update_fields = {
        "Payment Status": "Paid"
    }

    if stripe_payment_intent_id:
        order_update_fields["Stripe Payment Intent ID"] = stripe_payment_intent_id

    order_table.update(order_record_id, order_update_fields)

    # Normalize ticket IDs to update
    ids_to_update = []
    if ticket_record_ids:
        if isinstance(ticket_record_ids, str):
            ids_to_update = [tid.strip() for tid in ticket_record_ids.split(",") if tid.strip()]
        elif isinstance(ticket_record_ids, list):
            ids_to_update = ticket_record_ids
    elif ticket_record_id:
        ids_to_update = [ticket_record_id]

    for tid in ids_to_update:
        ticket_table.update(tid, {
            "Payment Status": "Paid"
        })

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

        # 5. FETCH RELEVANT DETAILS OF THE UPDATED TICKET
        updated_ticket = single_tickets_base.get(ticket_record_id)
        fields = updated_ticket.get("fields", {})
        
        return fields.get("Order ID"), fields.get("Ticket Type"), fields.get("Ticket Price")

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
            "Family Tickets (Linked)": [ticket_record_id]
        })

        # 4. MARK THE LINKED TICKET AS ASSIGNED
        family_tickets_base.update(ticket_record_id, {
            "Assigned": True,
            "Ticket Status": "On Hold",
            "Payment Status": "Pending"
        })

        # 5. FETCH THE RELEVANT DETAILS OF THE UPDATED TICKET
        updated_ticket = family_tickets_base.get(ticket_record_id)
        fields = updated_ticket.get("fields", {})

        return fields.get("Order ID"), fields.get("Ticket Type"), fields.get("Ticket Price")

def airtable_get_unassigned_single_ticket_count(filter_formula):
    api = Api(st.secrets["airtable"]["PAT"])
    base = api.base(st.secrets["airtable"]["BASE_ID"])
    single_tickets_base = base.table("Single Tickets")

    # RETURN THE LENGTH OF THE FILTERED DATA
    # Using fields=["id"] to only fetch record IDs, which is more efficient
    return len(single_tickets_base.all(formula=filter_formula, fields=["Auto ID"]))

def airtable_get_total_single_ticket_count(filter_formula):
    api = Api(st.secrets["airtable"]["PAT"])
    base = api.base(st.secrets["airtable"]["BASE_ID"])
    single_tickets_base = base.table("Single Tickets")

    # RETURN THE LENGTH OF ALL DATA
    return len(single_tickets_base.all(formula=filter_formula, fields=["Auto ID"]))

def airtable_get_unassigned_family_ticket_count(filter_formula):
    api = Api(st.secrets["airtable"]["PAT"])
    base = api.base(st.secrets["airtable"]["BASE_ID"])
    family_tickets_base = base.table("Family Tickets")

    # RETURN THE LENGTH OF THE FILTERED DATA
    # Using fields=["id"] to only fetch record IDs, which is more efficient
    return len(family_tickets_base.all(formula=filter_formula, fields=["Auto ID"]))

def airtable_get_total_family_ticket_count(filter_formula):
    api = Api(st.secrets["airtable"]["PAT"])
    base = api.base(st.secrets["airtable"]["BASE_ID"])
    family_tickets_base = base.table("Family Tickets")

    # RETURN THE LENGTH OF ALL DATA
    return len(family_tickets_base.all(formula=filter_formula, fields=["Auto ID"]))
