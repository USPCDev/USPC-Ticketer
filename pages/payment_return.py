import streamlit as st
from modules import airtable_functions, stripe_functions


st.title("Payment Status")

session_id = st.query_params.get("session_id")
payment_status = st.query_params.get("payment")

if payment_status == "cancelled":
    st.warning("Your Stripe payment was cancelled. Your booking is still pending and has not been confirmed as paid.")
    if st.button("Back to Home", type="primary"):
        st.switch_page("home.py")
    st.stop()

if not session_id:
    st.info("No Stripe payment session was provided. Please return to the booking page and try again.")
    if st.button("Back to Home", type="primary"):
        st.switch_page("home.py")
    st.stop()

try:
    with st.spinner("Verifying your Stripe payment and confirming ticket(s)... Please do not close or refresh this page."):
        session = stripe_functions.retrieve_checkout_session(session_id)

    if stripe_functions.is_checkout_session_paid(session):
        metadata = session.get("metadata", {})
        order_table_name = metadata.get("order_table_name")
        ticket_table_name = metadata.get("ticket_table_name")
        order_record_id = metadata.get("order_record_id")
        ticket_record_ids = metadata.get("ticket_record_ids") or metadata.get("ticket_record_id")
        stripe_payment_intent_id = session.get("payment_intent")

        if not all([order_table_name, ticket_table_name, order_record_id, ticket_record_ids]):
            st.error("Payment was received, but the booking metadata is incomplete. Please contact support.")
            st.stop()

        airtable_functions.airtable_mark_stripe_booking_paid(
            order_table_name=order_table_name,
            ticket_table_name=ticket_table_name,
            order_record_id=order_record_id,
            ticket_record_ids=ticket_record_ids,
            stripe_payment_intent_id=stripe_payment_intent_id,
        )

        st.balloons()
        st.success("Payment successful! Your booking is confirmed as paid. Your ticket(s) will be sent to your email shortly.", icon=":material/check_circle:")

        if st.button("Back to Home", type="primary"):
            st.switch_page("home.py")
    else:
        st.warning("Stripe has not confirmed this payment yet. If you completed payment, please wait a moment and refresh this page.")
        if st.button("Refresh payment status", type="primary"):
            st.rerun()

except Exception as e:
    st.error(f"Could not verify payment: {e}")
    st.info("If money has left your account, please contact support before trying another booking.")
