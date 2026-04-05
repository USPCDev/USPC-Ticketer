import streamlit as st
from streamlit_folium import st_folium
import folium
from modules import doc_functions

def info_expander(map_key, segmented_key):
    with st.expander("Very Important Info (Click here to open)!", icon=":material/info:", expanded=False):

        VENUE_DETAILS_TAB, TARIFF_DETAILS_TAB, TICKETS_INFO_TAB, SUPPORT_TEAM_TAB = st.tabs(["Venue Details", "Tariff Details", "Tickets Info", "Support Team"], width="stretch")

        with VENUE_DETAILS_TAB:
            st.subheader("Venue Details", divider="grey")

            VENUE_MAP_CONTAINER = st.container(border=True)
            with VENUE_MAP_CONTAINER:

                vog_venue_map = folium.Map(location=[53.379954470015505, -2.2654038143669117])
                folium.Marker(
                    [53.379954470015505, -2.2654038143669117],
                    popup="Forum Centre",
                    tooltip="Forum Centre"
                ).add_to(vog_venue_map)

                st_folium(vog_venue_map, zoom=15, width="stretch", height=300, key=f"st_folium_map{map_key}")

            VENUE_DETAILS_CONTAINER = st.container(border=False)
            with VENUE_DETAILS_CONTAINER:
                st.markdown("#### :material/stadium: Venue Name: *Wythenshawe Forum Centre*")
                st.markdown("#### :material/location_on: Address: *Poundswick Ln*")
                st.markdown("#### :material/map_search: Postcode: *M22 9PQ*")
                st.markdown("#### :material/location_city: City: *Manchester*")

                st.divider()

                st.markdown("#### :material/calendar_month: Date: *25th September, 2026*")
                st.markdown("#### :material/nest_clock_farsight_analog: Time: *5:30 PM to 9:30 PM*")

        with TARIFF_DETAILS_TAB:
            tariff_category_options = ["Single", "Family"]
            tariff_category_selection = st.segmented_control("Directions", tariff_category_options, default="Single", label_visibility="collapsed", selection_mode="single", key=f"st_segmented_control{segmented_key}")

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

        with TICKETS_INFO_TAB:
            st.subheader("Tickets Info", divider="grey")

            st.markdown("* **1 Ticket = 1 Seat**. For **Single** Tickets, as the name suggests, one order is equivalent to one ticket which is equivalent to one seat. For **Family** Tickets, each order is equivalent to four tickets which is equivalent to four seats. Please make sure that you are a family of four before proceeding for a **Family** Ticket.")

            st.markdown("* If you are a family of three, please proceed onto buying three **Single** Tickets but if you are family of five, for example, please proceed onto buying one **Family** Ticket and one additional **Single** Ticket (please make sure that details such as the *First Name*, *Last Name* & *Email* are the same while booking this additional ticket(s)).")

            st.markdown("* Seats can be shared by infants or children but if you decide to use a seat for your child, you are requested to pay the respective seat.")

            st.markdown("* Once an **Ticket Order** has been confirmed, an email will be sent to you with relevant information regarding your order along with payment instructions.")

            st.markdown("* Please make sure that once an order has been confirmed, the payment must be made within 7 days, otherwise, the ticket will be available for other users to buy. You may need to initiate a fresh booking.")

        #with TERMS_AND_CONDITIONS_TAB:
            #doc_functions.terms_and_conditions()

        #with PRIVACY_POLICY_TAB:
            #doc_functions.privacy_policy()

        with SUPPORT_TEAM_TAB:
            st.subheader("Support Team", divider="grey")
            PERSON1_COLUMN, PERSON2_COLUMN, PERSON3_COLUMN = st.columns([1, 1, 1], gap="small", vertical_alignment="center")

            with PERSON1_COLUMN:
                st.link_button("Mathew Varghese", icon=":material/call:", url="tel:+447967758301", width="stretch")

            with PERSON2_COLUMN:
                st.link_button("Binu Chacko", icon=":material/call:", url="tel:+447793975948", width="stretch")

            with PERSON3_COLUMN:
                st.link_button("Geoffry Mathew", icon=":material/call:", url="tel:+447464139381", width="stretch")
