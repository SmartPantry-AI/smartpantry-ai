import streamlit as st
from components.invitation_bridge import render_invitation_bridge

st.title("SmartPantry Invitation Bridge Test")

result = render_invitation_bridge()

st.write("Component result:", result)