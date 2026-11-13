import streamlit as st
from components.invitation_bridge import render_invitation_bridge

st.title("SmartPantry Invitation Bridge Test")

result = render_invitation_bridge(invitation_handled=True)

credentials_received = bool(
    result and result.get("invitation_credentials")
)

st.write("Credentials received by Python:", credentials_received)

status = result.get("status", {}) if result else {}

st.write("Invitation detected:", status.get("invitationDetected", False))
st.write("Invitation ready:", status.get("invitationReady", False))
st.write("Component running in iframe:", status.get("runningInIframe"))