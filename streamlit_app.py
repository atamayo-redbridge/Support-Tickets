from backend import init_db
init_db()

# 🔹 DASHBOARD BASED ON ROLE
def dashboard():
    st.sidebar.title("🎫 IT Ticketing System")

    if st.session_state["role"] == "admin":
        menu = st.sidebar.radio("Navigation", ["📩 Create User", "📋 Manage Tickets", "📊 Admin Dashboard"])

        if menu == "📋 Manage Tickets":
            st.header("📋 Manage Tickets")
            tickets = get_tickets(None, "admin")

            for ticket in tickets:
                with st.expander(f"🆔 {ticket[0]} | {ticket[1]} - {ticket[4]}"):
                    st.write(f"**Title:** {ticket[2]}")
                    st.write(f"**Description:** {ticket[3]}")
                    st.write(f"**Status:** `{ticket[4]}`")
                    
                    new_status = st.selectbox(f"Update Status for Ticket {ticket[0]}", ["Open", "In Progress", "Closed"], index=["Open", "In Progress", "Closed"].index(ticket[4]))
                    
                    if st.button(f"Update Ticket {ticket[0]}"):
                        update_ticket_status(ticket[0], new_status)
                        st.success(f"✅ Ticket {ticket[0]} updated to `{new_status}`")
                        st.rerun()

    elif st.session_state["role"] == "user":
        st.header("🎟 My Tickets")

        # Create a new ticket
        with st.form(key="ticket_form"):
            title = st.text_input("Ticket Title")
            description = st.text_area("Describe the Issue")
            submit_ticket = st.form_submit_button("Submit Ticket")

        if submit_ticket:
            create_ticket(st.session_state["email"], title, description)
            st.success("✅ Ticket Submitted Successfully!")
            st.rerun()

        # Display User Tickets
        tickets = get_tickets(st.session_state["email"], "user")
        if tickets:
            for ticket in tickets:
                with st.expander(f"🆔 {ticket[0]} | {ticket[2]} - {ticket[4]}"):
                    st.write(f"**Description:** {ticket[3]}")
                    st.write(f"**Status:** `{ticket[4]}`")

    # Logout Button
    if st.sidebar.button("Logout"):
        st.session_state.update({"logged_in": False, "email": None, "role": None})
        st.rerun()
