# SmartPantry AI
# Main Streamlit application

import streamlit as st
from modules.pantry_manager import PantryManager
from modules.pantry_database import (
    create_pantry_table,
    load_pantry_items,
    save_pantry_item
)

st.set_page_config(
    page_title="SmartPantry AI",
    page_icon="🥗",
    layout="wide"
)

st.title("🥗 SmartPantry AI")
st.write("Your intelligent kitchen assistant.")

st.info("Welcome! Manage your pantry, check food safety, and discover recipes.")

if "pantry_manager" not in st.session_state:
    create_pantry_table()

    st.session_state.pantry_manager = PantryManager()

    saved_items = load_pantry_items()

    for item in saved_items:
        st.session_state.pantry_manager.add_item(
            item["name"],
            item["quantity"],
            item["unit"]
        )

st.header("🥕 My Pantry")

ingredient_name = st.text_input("Ingredient name")

quantity = st.number_input(
    "Quantity",
    min_value=1,
    value=1,
    step=1
)

unit = st.selectbox(
    "Unit",
    ["item", "bag", "box", "can", "bottle", "lb", "oz", "g", "kg"]
)

if st.button("➕ Add Ingredient"):
    if ingredient_name.strip():
        st.session_state.pantry_manager.add_item(
            ingredient_name,
            quantity,
            unit
        )

        save_pantry_item(
            ingredient_name.strip(),
            quantity,
            unit
        )

        st.success(f"{ingredient_name} added to your pantry!")
    else:
        st.warning("Please enter an ingredient name.")

pantry_items = st.session_state.pantry_manager.get_items()

if pantry_items:
    st.dataframe(
        pantry_items,
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("Your pantry is empty. Add your first ingredient!")

