import stripe
import streamlit as st


LOCAL_APP_URL = "https://uspc-ticketer.streamlit.app/"

TICKET_PRICES_IN_PENCE = {
    "Single - Gold": 3000,
    "Single - Platinum": 4000,
    "Single - Diamond": 5000,
    "Family - Gold": 10000,
    "Family - Platinum": 15000,
    "Family - Diamond": 17500,
}


def _get_stripe_secret_key():
    try:
        return st.secrets["stripe"]["SECRET_KEY"]
    except KeyError as exc:
        raise RuntimeError("Stripe secret key is missing from Streamlit secrets.") from exc


def _set_stripe_api_key():
    stripe.api_key = _get_stripe_secret_key()


def get_ticket_price_in_pence(ticket_type):
    if ticket_type not in TICKET_PRICES_IN_PENCE:
        raise ValueError(f"Unsupported Stripe ticket type: {ticket_type}")

    return TICKET_PRICES_IN_PENCE[ticket_type]


def get_ticket_price_in_pounds(ticket_type):
    return get_ticket_price_in_pence(ticket_type) // 100


def create_checkout_session(
    *,
    customer_email,
    ticket_type,
    order_record_id,
    ticket_record_id=None,
    ticket_record_ids=None,
    quantity=1,
    order_table_name,
    ticket_table_name,
    app_base_url=LOCAL_APP_URL,
):
    _set_stripe_api_key()

    unit_amount_in_pence = get_ticket_price_in_pence(ticket_type)
    total_amount_in_pence = unit_amount_in_pence * quantity
    normalized_base_url = app_base_url.rstrip("/")

    # Normalize ticket IDs
    if ticket_record_ids is None and ticket_record_id is not None:
        ticket_record_ids = [ticket_record_id]
    elif isinstance(ticket_record_ids, str):
        ticket_record_ids = [tid.strip() for tid in ticket_record_ids.split(",") if tid.strip()]

    ticket_ids_str = ",".join(ticket_record_ids) if ticket_record_ids else ""
    first_ticket_id = ticket_record_ids[0] if ticket_record_ids else (ticket_record_id or "")

    session = stripe.checkout.Session.create(
        mode="payment",
        customer_email=customer_email,
        line_items=[
            {
                "price_data": {
                    "currency": "gbp",
                    "product_data": {
                        "name": f"USPC Voice of Grace 2026 - {ticket_type}",
                    },
                    "unit_amount": unit_amount_in_pence,
                },
                "quantity": quantity,
            }
        ],
        success_url=f"{normalized_base_url}/payment_return?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{normalized_base_url}/payment_return?payment=cancelled",
        metadata={
            "order_record_id": order_record_id,
            "ticket_record_id": first_ticket_id,
            "ticket_record_ids": ticket_ids_str,
            "quantity": str(quantity),
            "order_table_name": order_table_name,
            "ticket_table_name": ticket_table_name,
            "ticket_type": ticket_type,
        },
    )

    return {
        "session_id": session.id,
        "checkout_url": session.url,
        "amount_in_pence": total_amount_in_pence,
        "amount_in_pounds": total_amount_in_pence // 100,
    }


def retrieve_checkout_session(session_id):
    _set_stripe_api_key()

    return stripe.checkout.Session.retrieve(session_id).to_dict()


def is_checkout_session_paid(session):
    return session.get("payment_status") == "paid"
