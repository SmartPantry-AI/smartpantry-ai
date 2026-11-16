# SmartPantry AI
# Main Streamlit application

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from modules.pantry_manager import PantryManager

from modules.supabase_client import get_supabase_client
from modules.pantry_grouping import group_pantry_items

from modules.supabase_auth import sign_in_user, sign_out_user

from modules.supabase_pantry import (
    load_user_pantry,
    add_pantry_item,
    delete_user_pantry_item,
    update_pantry_item_quantity,
)

import streamlit as st

from modules.image_recognition import recognize_food
import tempfile
from datetime import date

from modules.storage_guidance import (
    adapt_pantry_item,
    evaluate_foodkeeper,
    evaluate_leftovers,
    find_osu_rule,
)


from modules.recall_checker import (
    get_fda_recalls,
    get_usda_recalls,
    match_recall_to_product,
)

from modules.recipe_recommender import (
    rank_recall_checked_recipes,
    fetch_spoonacular_recipes,
    convert_spoonacular_recipe,
)

from modules.recipe_recommender import (
    rank_recipes,
    recipes as sample_recipes,
    pantry as sample_pantry,
)

from modules.ai_assistant import (
    ask_ai,
    interpret_pantry_request,
    handle_supabase_pantry_command,
)

from modules.barcode_lookup import identify_product


def render_pantry_batch(item):
    """Display one pantry record and its storage guidance."""

    st.caption(f"📦 Batch quantity: {item['quantity']} {item['unit']}")

    storage_labels = {
        "REFRIGERATOR": "Refrigerator",
        "FREEZER": "Freezer",
        "PANTRY": "Pantry / room temperature",
    }

    storage_location = item.get("storage_location")

    if storage_location:
        st.caption(
            f"📦 Stored in: {storage_labels.get(storage_location, storage_location)}"
        )

    if item.get("purchase_date"):
        st.caption(f"📅 Purchased: {item['purchase_date']}")

    if item.get("expiration_date"):
        st.caption(f"🏷️ Package expiration / use-by: {item['expiration_date']}")

    adapted_item = adapt_pantry_item(item)

    foodkeeper_result = evaluate_foodkeeper(
        adapted_item,
        as_of=date.today(),
    )

    if foodkeeper_result["recommended_use_date"]:
        st.caption(
            f"🌱 FoodKeeper use-soon reminder: "
            f"{foodkeeper_result['recommended_use_date']}"
        )
        st.caption(
            f"Priority: {foodkeeper_result['use_priority']}"
        )
        
        if foodkeeper_result["reminder_status"] == "PAST_REMINDER":
            st.warning("⚠️ FoodKeeper reminder is overdue.")
        elif foodkeeper_result["reminder_status"] == "TODAY":
            st.info("📅 FoodKeeper reminder is due today.")

        if foodkeeper_result["source"]:
            st.caption(
                f"Source: {foodkeeper_result['source']}"
            )

    leftovers_result = evaluate_leftovers(
        adapted_item,
        as_of=date.today(),
    )

    if leftovers_result["recommended_use_date"]:
        st.caption(
            f"🧊 FoodSafety.gov use-soon reminder: "
            f"{leftovers_result['recommended_use_date']}"
        )
        st.caption(
            f"Priority: {leftovers_result['use_priority']}"
        )

        if leftovers_result["reminder_status"] == "PAST_REMINDER":
            st.warning("⚠️ FoodSafety.gov reminder is overdue.")
        elif leftovers_result["reminder_status"] == "TODAY":
            st.info("📅 FoodSafety.gov reminder is due today.")

        if leftovers_result["source"]:
            st.caption(
                f"Source: {leftovers_result['source']}"
            )

    osu_rule = find_osu_rule(item["name"])

    if (
        osu_rule is not None
        and storage_location == osu_rule["storage_location"]
    ):
        st.caption(
            f"🌿 OSU Extension storage guidance: "
            f"{osu_rule['duration_raw']}"
        )
        st.caption(
            f"Recommended temperature: "
            f"{osu_rule['storage_temperature_raw']}"
        )
        st.caption(
            "Approximate storage time for best quality; "
            "not a calculated expiration date."
        )
        st.caption(
            f"Source: {osu_rule['source_url']}"
        )
   


st.set_page_config(
    page_title="SmartPantry AI",
    page_icon="🥗",
    layout="wide"
)

def render_mochi_chat():
    """Display Mochi's chat interface."""

    if "mochi_messages" not in st.session_state:
        st.session_state.mochi_messages = []

    

    if not st.session_state.mochi_messages:
        with st.chat_message(
            "assistant",
            avatar=str(PROJECT_ROOT / "assets" / "mochi_avatar_transparent.png")
        ):
            st.markdown(
                "Hi! I'm Mochi! 🍡💜 Ask me about recipes, "
                "food storage, or anything happening in your kitchen!"
            )

    for message in st.session_state.mochi_messages:
        with st.chat_message(
            message["role"],
            avatar=(
                str(PROJECT_ROOT / "assets" / "mochi_avatar_transparent.png")
                if message["role"] == "assistant"
                else "👤"
            )
        ):
            st.markdown(message["content"])

    pending_command = st.session_state.get("mochi_pending_pantry_command")

    if pending_command:
        st.info(
            f"Pending pantry addition: "
            f"{pending_command['quantity']:g} "
            f"{pending_command['unit']} of "
            f"{pending_command['ingredient']}"
        )

        confirm_col, cancel_col = st.columns(2)

        with confirm_col:
            if st.button("✅ Confirm Add", key="mochi_confirm_add"):
                try:
                    result = handle_supabase_pantry_command(
                        pending_command,
                        st.session_state.supabase_client,
                    )

                    if not result:
                        raise RuntimeError("Pantry addition was not confirmed.")

                    st.session_state.mochi_messages.append({
                        "role": "assistant",
                        "content": (
                            f"Added {pending_command['quantity']:g} "
                            f"{pending_command['unit']} of "
                            f"{pending_command['ingredient']} to your pantry."
                        ),
                    })

                    del st.session_state["mochi_pending_pantry_command"]
                    st.rerun()

                except Exception:
                    st.error(
                        "I couldn't save that item. "
                        "Your pantry may not have been updated."
                    )

        with cancel_col:
            if st.button("Cancel", key="mochi_cancel_add"):
                del st.session_state["mochi_pending_pantry_command"]

                st.session_state.mochi_messages.append({
                    "role": "assistant",
                    "content": "Pantry addition canceled.",
                })

                st.rerun()

    mochi_question = st.chat_input(
        "Ask Mochi anything about your kitchen...",
        key="mochi_shared_chat"
    )

    if mochi_question and mochi_question.strip():
        st.session_state.mochi_messages.append({
            "role": "user",
            "content": mochi_question.strip()
        })

        message_text = mochi_question.strip()

        is_pantry_add_request = (
            message_text.lower().startswith((
                "add ",
                "mochi, add ",
                "mochi add ",
                "please add ",
                "can you add ",
                "could you add ",
                "mochi, can you add ",
                "mochi, could you add ",
                "mochi can you add ",
                "mochi could you add ",
            ))
        )

        if is_pantry_add_request:
            try:
                command = interpret_pantry_request(message_text)
                st.session_state["mochi_pending_pantry_command"] = command

                mochi_response = (
                    f"Would you like me to add "
                    f"{command['quantity']:g} {command['unit']} of "
                    f"{command['ingredient']} to your pantry?"
                )

            except (ValueError, KeyError, TypeError):
                mochi_response = (
                    "I couldn't understand that pantry request. "
                    "Try something like 'Add 2 cups of rice.'"
                )

            st.session_state.mochi_messages.append({
                "role": "assistant",
                "content": mochi_response,
            })
            st.rerun()

        with st.spinner("Mochi is thinking..."):
            mochi_response = ask_ai(
                mochi_question.strip(),
                conversation_history=st.session_state.mochi_messages
            )

        if mochi_response == "Sorry, Mochi is temporarily unavailable.":
            st.error(mochi_response)
        else:
            st.session_state.mochi_messages.append({
                "role": "assistant",
                "content": mochi_response
            })

        st.rerun()

if "supabase_client" not in st.session_state:
    st.session_state.supabase_client = get_supabase_client()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if st.session_state.authenticated:
    try:
        user_response = st.session_state.supabase_client.auth.get_user()

        if (
            user_response.user is None
            or user_response.user.id != st.session_state.get("user_id")
        ):
            st.session_state.clear()
            st.rerun()

    except Exception:
        st.session_state.clear()
        st.rerun()


if not st. session_state.authenticated:
    st.subheader("🔐 Sign in to SmartPantry")

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Sign In")

    if login_button:
        if not email.strip() or not password:
            st.error("Please enter your email and password.")
        else:
            try:
                response = sign_in_user(
                    st.session_state.supabase_client,
                    email.strip(),
                    password,
                )

                if response.user is None or response.session is None:
                    st.error("Unable to sign in.")
                else:
                    st.session_state.authenticated = True
                    st.session_state.user_id = response.user.id
                    st.rerun()
                    

            except Exception:
                st.error("Unable to sign in. Please check your crednetials.")

    st.stop()

if st.sidebar.button("🚪 Sign Out"):
    try:
        sign_out_user(st.session_state.supabase_client)
    finally:
        st.session_state.clear()
        st.rerun()    


with st.sidebar:
    st.title("🥗 SmartPantry")
    st.caption("Your intelligent kitchen companion")

    st.divider()

    selected_page = st.radio(
        "Navigation",
        [
           "🏠 Home",
            "🥕 My Pantry",
            "📷 Scan Food",
            "🧊 Food Safety",
            "🍳 Recipes",
            "🍡 Mochi AI"  
        ],
        label_visibility="collapsed",
        key="main_navigation"
    )

st.title("🥗 SmartPantry AI")
st.write("Your intelligent kitchen assistant.")



if "pantry_manager" not in st.session_state:
    st.session_state.pantry_manager = PantryManager()

    saved_items = load_user_pantry(
        st.session_state.supabase_client
    )

    for item in saved_items:
        st.session_state.pantry_manager.add_item(
            item["name"],
            item["quantity"],
            item["unit"]
        )

if selected_page == "🏠 Home":
    st.header("🏠 Your Kitchen Dashboard")
    st.caption("Your kitchen, organized. Here's what's happening in your pantry today. 🌿")

    home_main, home_mochi = st.columns(
        [2.3, 1],
        gap="large"
    )


    with home_mochi:
        st.subheader("🍡 Chat with Mochi")
        st.caption("Your AI kitchen companion")
    
        with st.container(height=450, border=True):
            render_mochi_chat()

    with home_main:
        pantry_items = st.session_state.pantry_manager.get_items()


        with st.container(border=True):
            welcome_text, welcome_art = st.columns(
                [2, 1],
                gap="medium",
                vertical_alignment="center"
            )

            with welcome_text:
                st.subheader("Welcome to your kitchen! 💜")
                st.write(
                    "Smarter choices. Less waste. "
                    "Let's make something great today!"
                )

            with welcome_art:
                st.image(
                    PROJECT_ROOT / "assets" / "mochi_avatar_transparent.png",
                    width=180
                )

        total_quantity = sum(item["quantity"] for item in pantry_items)
        items_column, quantity_column = st.columns(2, gap="large")

        with items_column:
            with st.container(border=True):
                st.metric("🥕 Pantry Items", len(pantry_items))
                st.caption("Items currently in your pantry")

        with quantity_column:
            with st.container(border=True):
                st.metric("📦 Recorded Quantity", total_quantity)
                st.caption("Combined quantities across all units")

        st.divider()
        st.subheader("⚡ Quick Actions")

        pantry_action, scan_action = st.columns(2, gap="large")
        safety_action, mochi_action = st.columns(2, gap="large")

        with pantry_action:
            st.button(
                "🥕 My Pantry",
                use_container_width=True,
                type="primary",
                on_click=lambda: st.session_state.update(
                    main_navigation="🥕 My Pantry"
                )
            )
        with scan_action:
            st.button(
                "📷 Scan Food",
                use_container_width=True,
                type="primary",
                on_click=lambda: st.session_state.update(
                    main_navigation="📷 Scan Food"
                )
            )

        with safety_action:
            st.button(
                "🧊 Food Safety",
                use_container_width=True,
                type="primary",
                on_click=lambda: st.session_state.update(
                    main_navigation="🧊 Food Safety"
                )
            )

        with mochi_action:
            st.button(
                "🍡 Mochi AI",
                use_container_width=True,
                type="primary",
                on_click=lambda: st.session_state.update(
                    main_navigation="🍡 Mochi AI"
                )
            )
        
        st.divider()
        st.subheader("🥕 Your Pantry at a Glance")

        if pantry_items:
            st.caption(
                f"Showing {min(len(pantry_items), 5)} of {len(pantry_items)} pantry items"
            )

        if pantry_items:
            for item in pantry_items[:5]:
                with st.container(border=True):
                    st.write(f"🥕 **{item['name'].title()}**")
                    st.caption(f"Quantity: {item['quantity']} {item['unit']}")
        else:
            st.info("Your pantry is empty. Add your first ingredient!")

        st.button(
            "View Full Pantry →",
            use_container_width=True,
            on_click=lambda: st.session_state.update(
                main_navigation="🥕 My Pantry"
            )
        )

        

if selected_page == "🥕 My Pantry":
    st.header("🥕 My Pantry")
    st.caption("Keep track of your ingredients and manage your kitchen inventory.")
    st.divider()

    st.subheader("📦 Current Inventory")

    st.caption(
        "ℹ️ Storage guidance and use-soon reminders are informational "
        "estimates, not guarantees of food safety. Follow package "
        "instructions and official food-safety recommendations. "
        "When in doubt, throw it out."
    )

    inventory_items = load_user_pantry(
        st.session_state.supabase_client
    )

    grouped_inventory = group_pantry_items(inventory_items)

    if inventory_items:
        st.caption(
            f"You have {len(inventory_items)} pantry "
            f"{'entry' if len(inventory_items) == 1 else 'entries'}."
        )

        for ingredient_name, batches in grouped_inventory.items():
            with st.container(border=True):
                st.subheader(f"🥕 {batches[0]['name'].title()}")

                if len(batches) > 1:
                    units = {item["unit"] for item in batches}

                    if len(units) == 1:
                        total_quantity = sum(item["quantity"] for item in batches)
                        unit = batches[0]["unit"]

                        display_unit = unit

                        if unit == "item" and total_quantity != 1:
                            display_unit = "items"

                        st.caption(f"Total quantity: {total_quantity} {display_unit}")

                    else:
                        st.caption(f"{len(batches)} batches with different units")

                for index, item in enumerate(batches):
                    if index > 0:
                        st.divider()

                    render_pantry_batch(item)

                
    else:
        st.info("Your pantry is empty. Add your first ingredient below!")

    st.divider()

    if st.session_state.pop("reset_manual_entry", False):
        st.session_state["manual_ingredient_name"] = ""
        st.session_state["manual_quantity"] = 1
        st.session_state["manual_unit"] = "item"
        st.session_state["manual_purchase_date"] = None
        st.session_state["manual_expiration_date"] = None
        st.session_state["manual_storage_location"] = ""
        st.session_state["manual_food_classification"] = "Regular ingredient"
        st.session_state["manual_prepared_date"] = None

    if st.session_state.pop("manual_entry_success", False):
        st.success("Ingredient added to your pantry successfully!")


    st.subheader("➕ Add Ingredient")
    st.caption("Add a new ingredient to your kitchen inventory.")

    ingredient_name = st.text_input(
        "Ingredient name",
        key="manual_ingredient_name",
    )

    food_classification = st.selectbox(
        "Food classification",
        options=["Regular ingredient", "Cooked food / leftovers"],
        key="manual_food_classification",
    )

    prepared_date = None

    if food_classification == "Cooked food / leftovers":
        prepared_date = st.date_input(
            "Date prepared",
            value=None,
            max_value=date.today(),
            format="MM/DD/YYYY",
            key="manual_prepared_date",
        )

    quantity_column, unit_column = st.columns(2, gap="large")

    with quantity_column:
        quantity = st.number_input(
            "Quantity",
            min_value=1,
            value=1,
            step=1,
            key="manual_quantity"
        )

    with unit_column:
        unit = st.selectbox(
            "Unit",
            ["item", "bag", "box", "can", "bottle", "lb", "oz", "g", "kg"],
            key="manual_unit",
        )

    st.caption("Optional dates for storage reminders")

    purchase_date = st.date_input(
        "Purchase date",
        value=None,
        format="MM/DD/YYYY",
        key="manual_purchase_date",
    )

    expiration_date = st.date_input(
        "Package expiration / use-by date",
        value=None,
        format="MM/DD/YYYY",
        key="manual_expiration_date",
    )

    storage_location = st.selectbox(
        "Storage location",
        options=["", "REFRIGERATOR", "FREEZER", "PANTRY"],
        format_func=lambda value: {
            "": "Select storage location",
            "REFRIGERATOR": "Refrigerator",
            "FREEZER": "Freezer",
            "PANTRY": "Pantry / room temperature",
        }[value],
        key="manual_storage_location",
    )

    if st.button(
        "➕ Add Ingredient",
        type="primary",
        use_container_width=True
    ):
        if ingredient_name.strip():
            try:
                add_pantry_item(
                    st.session_state.supabase_client,
                    ingredient_name.strip(),
                    quantity,
                    unit,
                    purchase_date=purchase_date.isoformat() if purchase_date else None,
                    expiration_date=expiration_date.isoformat() if expiration_date else None,
                    storage_location=storage_location or None,
                    prepared_date=prepared_date.isoformat() if prepared_date else None,
                )

                st.session_state.pantry_manager.add_item(
                    ingredient_name.strip(),
                    quantity,
                    unit
                )

                st.session_state["manual_entry_success"] = True
                st.session_state["reset_manual_entry"] = True
                st.rerun()

            except Exception:
                st.error("Unable to save ingredient. Please try again.")

        else:
            st.warning("Please enter an ingredient name.")

    st.divider()
    st.subheader("⚙️ Manage Ingredients")
    st.caption("Update quantities or remove ingredients from your pantry.")

    with st.expander("🗑️ Remove Ingredient", expanded=False):
        st.write("Select an ingredient to remove from your pantry.")



        saved_pantry_items = load_user_pantry(
            st.session_state.supabase_client
        )

        if saved_pantry_items:
            selected_item = st.selectbox(
                "Select an ingredient to remove",
                options=saved_pantry_items,
                format_func=lambda item: (
                    f"{item['name']} ({item['quantity']} {item['unit']})"
                ),
            )

            if st.button("🗑️ Delete Selected Ingredient"):
                st.session_state.pending_delete_id = selected_item["id"]
                
        if st.session_state.get("pending_delete_id") is not None:
            pending_item = next(
                (
                    item for item in saved_pantry_items
                    if item["id"] == st.session_state.pending_delete_id
                ),
                None
            )

            if pending_item:
                st.warning(
                    f"Are you sure you want to delete {pending_item['name']}?"
                )

                if st.button("✅ Yes, Delete Ingredient"):
                    try:
                        deleted = delete_user_pantry_item(
                            st.session_state.supabase_client,
                            pending_item["id"]
                        )

                        if deleted:
                            st.session_state.pantry_manager = PantryManager()

                            for item in load_user_pantry(
                                st.session_state.supabase_client
                            ):
                                st.session_state.pantry_manager.add_item(
                                    item["name"],
                                    item["quantity"],
                                    item["unit"]
                                )
                            st.session_state.pending_delete_id = None
                            st.rerun()
                        else:
                            st.warning("Ingredient was not deleted.")

                    except Exception:
                        st.error("Unable to delete ingredient. Please try again.")
            else:
                st.session_state.pending_delete_id = None

    with st.expander("✏️ Update Quantity", expanded=False):
        st.write("Adjust the quantity of an ingredient in your pantry.")

        quantity_items = load_user_pantry(
            st.session_state.supabase_client
        )

        if quantity_items:
            selected_quantity_item = st.selectbox(
                "Select an ingredient to update",
                options=quantity_items,
                format_func=lambda item: (
                    f"{item['name']} "
                    f"({item['quantity']} {item['unit']})"
                    f"[ID: {item['id']}]"
                ),
                key="quantity_item_selection"
            )

            new_quantity = st.number_input(
                "New quantity",
                min_value=1,
                value=int(selected_quantity_item["quantity"]),
                step=1,
                key=f"new_quantity_{selected_quantity_item['id']}"
            )

            if st.button("💾 Update Quantity"):
                try:
                    updated = update_pantry_item_quantity(
                        st.session_state.supabase_client,
                        selected_quantity_item["id"],
                        new_quantity
                    )

                    if updated:
                        st.session_state.pantry_manager = PantryManager()

                        for item in load_user_pantry(
                            st.session_state.supabase_client
                        ):
                            st.session_state.pantry_manager.add_item(
                                item["name"],
                                item["quantity"],
                                item["unit"]
                            )
                        st.success("Quantity updated successfully!")
                        st.rerun()
                    else:
                        st.warning("Quantity was not updated.")

                except Exception:
                    st.error("Unable to update quantity. Please try again.")


        else:
            st.info("Add an ingredient before updating quantities.")

    pantry_items = st.session_state.pantry_manager.get_items()

    if pantry_items:
        st.dataframe(
            pantry_items,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Your pantry is empty. Add your first ingredient!")

if selected_page == "📷 Scan Food":
    st.header("📷 Scan Food")
    st.caption("Identify ingredients from photos or look up products using their barcodes.")
    st.divider()

    image_column, barcode_column = st.columns(2, gap="large")

    with image_column:
        st.subheader("📷 Food Image Recognition")
        st.caption("Upload a photo of food and let AI identify the ingredient.")

        if st.session_state.pop("image_entry_success", False):
            st.success("Ingredient successfully saved to your pantry!")

        def clear_image_recognition():
           st.session_state.recognized_food = None

           for key in (
               "confirmed_image_name",
               "confirmed_image_quantity",
               "confirmed_image_unit",
               "confirmed_image_storage",
               "confirmed_image_purchase_date",
               "confirmed_image_expiration_date",
            ):
               st.session_state.pop(key, None)


        if st.session_state.pop("reset_image_entry", False):
            clear_image_recognition()
            
        if "food_image_upload_version" not in st.session_state:
            st.session_state.food_image_upload_version = 0


        uploaded_image = st.file_uploader(
            "Upload a food image",
            type=["jpg", "jpeg", "png"],
            key=f"food_image_upload_{st.session_state.food_image_upload_version}",
            on_change=clear_image_recognition,
        )


        if uploaded_image is not None:
            st.image(uploaded_image, caption="Uploaded food image")

            if st.button(
                "🔍 Identify Food",
                type="primary",
                use_container_width=True
            ):
                temporary_path = None

                try:
                    with tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=Path(uploaded_image.name).suffix
                    ) as temporary_file:
                        temporary_file.write(uploaded_image.getvalue())
                        temporary_path = Path(temporary_file.name)

                    with st.spinner("Identifying food..."):
                        recognized_food = recognize_food(temporary_path)

                    if not recognized_food or recognized_food.strip().casefold() == "unknown":
                        st.session_state.recognized_food = None
                        st.warning("Food could not be identified.")
                    else:
                        st.session_state.recognized_food = recognized_food.strip()
                       

                except Exception as error:
                    st.error(f"Image recognition failed: {error}")

                finally:
                    if temporary_path is not None:
                        temporary_path.unlink(missing_ok=True)

            
            if st.session_state.get("recognized_food"):
                st.success(
                    f"Recognized ingredient: {st.session_state.recognized_food}"
                )

                st.markdown("#### Confirm Ingredient")

                if not st.session_state.get("confirmed_image_name"):
                    st.session_state.confirmed_image_name = (
                        st.session_state.recognized_food
                    )

                confirmed_image_name = st.text_input(
                    "Ingredient name",
                    key="confirmed_image_name",
                )

                quantity_column, unit_column = st.columns(2, gap="large")

                with quantity_column:
                    confirmed_image_quantity = st.number_input(
                        "Quantity",
                        min_value=1,
                        value=1,
                        step=1,
                        key="confirmed_image_quantity",
                    )

                with unit_column:
                    confirmed_image_unit = st.selectbox(
                        "Unit",
                        ["item", "bag", "box", "can", "bottle", "lb", "oz", "g", "kg"],
                        key="confirmed_image_unit",
                    )

                confirmed_image_storage = st.selectbox(
                    "Storage location",
                    options=["", "REFRIGERATOR", "FREEZER", "PANTRY"],
                    format_func=lambda value: {
                        "": "Select storage location",
                        "REFRIGERATOR": "Refrigerator",
                        "FREEZER": "Freezer",
                        "PANTRY": "Pantry / room temperature",
                    }[value],
                    key="confirmed_image_storage",
                )

                st.caption("Optional dates for storage reminders")

                confirmed_image_purchase_date = st.date_input(
                    "Purchase date",
                    value=None,
                    format="MM/DD/YYYY",
                    key="confirmed_image_purchase_date",
                )

                confirmed_image_expiration_date = st.date_input(
                    "Package expiration / use-by date",
                    value=None,
                    format="MM/DD/YYYY",
                    key="confirmed_image_expiration_date",
                )

                if st.button(
                    "➕ Save Recognized Ingredient to Pantry",
                    use_container_width=True,
                    key="save_recognized_ingredient",
                ):
                    if not confirmed_image_name.strip():
                        st.warning("Please enter an ingredient name.")
                    else:
                        try:
                            add_pantry_item(
                                st.session_state.supabase_client,
                                confirmed_image_name.strip(),
                                confirmed_image_quantity,
                                confirmed_image_unit,
                                purchase_date=(
                                    confirmed_image_purchase_date.isoformat()
                                    if confirmed_image_purchase_date else None
                                ),
                                expiration_date=(
                                    confirmed_image_expiration_date.isoformat()
                                    if confirmed_image_expiration_date else None
                                ),
                                storage_location=confirmed_image_storage or None,
                            )

                            st.session_state.pantry_manager.add_item(
                                confirmed_image_name.strip(),
                                confirmed_image_quantity,
                                confirmed_image_unit,
                            )

                            st.session_state["reset_image_entry"] = True
                            st.session_state["image_entry_success"] = True
                            st.session_state.food_image_upload_version += 1
                            st.rerun()

                        except Exception as error:
                            st.error(f"Could not save ingredient: {error}")

    with barcode_column:
        st.subheader("📦 Barcode Product Lookup")
        st.caption("Scan a product barcode to retrieve its details from Open Food Facts.")

        barcode_image = st.file_uploader(
            "Upload a photo of a product barcode",
            type=["jpg", "jpeg", "png"],
            key="barcode_upload"
        )

        if barcode_image is not None:
            st.image(
                barcode_image,
                caption="Uploaded barcode image",
                width=250
            )
            if "identified_barcode_product" not in st.session_state:
                st.session_state.identified_barcode_product = None

            if st.button(
                "🔍 Identify Product",
                type="primary",
                use_container_width=True
            ):
                barcode_path = None

                try:
                    with tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=Path(barcode_image.name).suffix
                    ) as temporary_file:
                        temporary_file.write(barcode_image.getvalue())
                        barcode_path = Path(temporary_file.name)

                    with st.spinner("Identifying product..."):
                        product, error = identify_product(str(barcode_path))

                    if error:
                        st.session_state.identified_barcode_product = None
                        st.warning(error)
                    elif product:
                        st.session_state.identified_barcode_product = product
                        st.success("Product identified!")
                        st.write("Product:", product.get("product_name"))
                        st.write("Brand:", product.get("brand"))
                        st.write("Barcode:", product.get("barcode"))
                        st.write("Quantity:", product.get("quantity"))
                        st.caption(
                            "Product information comes from Open Food Facts. "
                            "Review the details before adding anything to your pantry."
                        )

                except Exception as error:
                    st.error(f"Barcode lookup failed: {error}")

                finally:
                    if barcode_path is not None:
                        barcode_path.unlink(missing_ok=True)
        
        product_to_confirm = st.session_state.get("identified_barcode_product")

        if product_to_confirm:
            st.markdown("#### Confirm Product")

            confirmed_name = st.text_input(
                "Product name",
                value=product_to_confirm.get("product_name") or "",
                key="confirmed_barcode_name"
            )

            quantity_column, unit_column = st.columns(2, gap="large")

            with quantity_column:
                confirmed_quantity = st.number_input(
                    "Quantity to add",
                    min_value=1,
                    value=1,
                    step=1,
                    key="confirmed_barcode_quantity"
                )

            with unit_column:
                confirmed_unit = st.selectbox(
                    "Unit",
                    ["item", "bag", "box", "can", "bottle", "lb", "oz", "g", "kg"],
                    key="confirmed_barcode_unit"
                )

            if st.button(
                "✅ Confirm and Add to Pantry",
                type="primary",
                use_container_width=True
            ):
                if not confirmed_name.strip():
                    st.warning("Please enter a product name.")
                else:
                    try:
                        add_pantry_item(
                            st.session_state.supabase_client,
                            confirmed_name.strip(),
                            confirmed_quantity,
                            confirmed_unit
                        )

                        st.session_state.pantry_manager = PantryManager()

                        for item in load_user_pantry(
                            st.session_state.supabase_client
                        ):
                            st.session_state.pantry_manager.add_item(
                                item["name"],
                                item["quantity"],
                                item["unit"]
                            )

                    except Exception:
                        st.error("Unable to save product to your pantry.")
                        st.stop()
                
                    st.session_state.identified_barcode_product = None

                    st.success(
                        f"{confirmed_name.strip()} added to your pantry!"
                    )

                    st.rerun() 

if selected_page == "🧊 Food Safety":
    st.header("🧊 Food Safety")
    st.caption(
        "Review food storage guidance and screen your saved pantry "
        "against FDA and USDA recall records."
    )
    st.divider()

    st.subheader("🚨 Pantry Recall Screening")
    st.caption(
        "Check your saved pantry against available FDA and USDA recall records. "
        "Screening runs only when you request it."
    )

    if st.button(
        "🔍 Check My Pantry for Recalls",
        use_container_width=True,
        key="check_pantry_recalls"
    ):
        pantry_items = load_user_pantry(
            st.session_state.supabase_client
        )

        st.write("Pantry items retrieved:", len(pantry_items))

        if pantry_items:
            with st.spinner("Retrieving USDA recall records..."):
                usda_result = get_usda_recalls()

            if usda_result["error"]:
                st.warning(
                    "USDA recall records could not be retrieved. "
                    "Screening remains incomplete."
                )
            else:
                st.write(
                    "USDA records retrieved:",
                    len(usda_result["records"])
                )

                usda_matches = []
                seen_matches = set()

                for item in pantry_items:
                    product = {
                        "product_name": item["name"],
                        "brand": item.get("brand"),
                        "upc": item.get("upc"),
                        "lot_code": item.get("lot_code"),
                    }

                    for recall in usda_result["records"]:
                        result = match_recall_to_product(product, recall)

                        if result["status"] == "POSSIBLE_MATCH":
                            match_key = (
                                item["id"],
                                recall.get("recall_id"),
                            )

                            if match_key not in seen_matches:
                                seen_matches.add(match_key)
                                usda_matches.append({
                                    "product": item["name"],
                                    "recall": recall,
                                })

                st.write(
                    "USDA records flagged for review:",
                    len(usda_matches)
                )

                if usda_matches:
                    with st.expander("Review USDA screening results"):
                        for match in usda_matches:
                            st.write("Pantry item:", match["product"])
                            st.write(
                                "Recall:",
                                match["recall"].get("product_description")
                            )
                            st.write(
                                "Official notice:",
                                match["recall"].get("source_url")
                            )
                            st.divider()

                st.caption(
                    "Preliminary screening of retrieved records only. "
                    "A potential match requires product verification, "
                    "and zero matches does not establish food safety."
                )

                unique_product_names = sorted({
                    item["name"].strip()
                    for item in pantry_items
                    if item.get("name") and item["name"].strip()
                })[:2]

                fda_records = []
                fda_errors = []

                with st.spinner("Searching FDA recalls for pantry products..."):
                    for product_name in unique_product_names:
                        result = get_fda_recalls(product_name, limit=10)

                        if result["error"]:
                            fda_errors.append(product_name)
                        else:
                            fda_records.extend(result["records"])

                st.write(
                    "FDA recall records retrieved:",
                    len(fda_records)
                )

                fda_matches = []
                seen_fda_matches = set()

                for item in pantry_items:
                    if item["name"].strip() not in unique_product_names:
                        continue

                    product = {
                        "product_name": item["name"],
                        "brand": item.get("brand"),
                        "upc": item.get("upc"),
                        "lot_code": item.get("lot_code"),
                    }

                    for recall in fda_records:
                        result = match_recall_to_product(product, recall)

                        if result["status"] == "POSSIBLE_MATCH":
                            match_key = (
                                item["id"],
                                recall.get("recall_number"),
                            )

                            if match_key not in seen_fda_matches:
                                seen_fda_matches.add(match_key)
                                fda_matches.append({
                                    "product": item["name"],
                                    "recall": recall,
                                })

                st.write(
                    "FDA product-name overlaps requiring verification:",
                    len(fda_matches)
                )

                if fda_matches:
                    with st.expander("Review FDA product-name overlaps"):
                        for match in fda_matches[:10]:
                            st.write("Pantry item:", match["product"])
                            st.write(
                                "Recall:",
                                match["recall"].get("product_description")
                            )
                            st.write(
                                "Recall number:",
                                match["recall"].get("recall_number")
                            )
                            st.divider()

                st.caption(
                    "FDA screening covers only two pantry product names "
                    "and up to ten search records per name. "
                    "Results require product verification."
                )

                st.session_state["pantry_recall_screening"] = {
                    "pantry_item_ids": sorted(
                        item["id"] for item in pantry_items
                    ),
                    "usda_records_checked": len(usda_result["records"]),
                    "usda_name_overlaps": len(usda_matches),
                    "fda_records_checked": len(fda_records),
                    "fda_name_overlaps": len(fda_matches),
                    "fda_searches_failed": len(fda_errors),
                    "status": "INCOMPLETE",
                }

                st.write(
                    "FDA searches that could not be completed:",
                    len(fda_errors)
                )

                st.caption(
                    "FDA searches use pantry product names. Retrieved records "
                    "are not confirmed matches to your specific products."
                )

        else:
            st.info("Your pantry is empty. Add an item before screening.")

    storage_column, recall_column = st.columns(2, gap="large")

    with storage_column:
        st.subheader("🧊 Food Storage Recommendations")
        st.caption("Check available FoodKeeper guidance for refrigerated ingredients.")
        st.caption("Storage location: Refrigerator")

        storage_food = st.text_input(
            "Ingredient for storage guidance",
            value="carrots"
        )

        purchase_date = st.date_input(
            "Purchase date",
            value=date.today()
        )

        if st.button(
            "🧊 Check Storage Guidance",
            type="primary",
            use_container_width=True
        ):
            item = {
                "item_id": "storage-demo-001",
                "food_type": storage_food,
                "storage_location": "REFRIGERATOR",
                "purchase_date": purchase_date.isoformat()
            }

            result = evaluate_foodkeeper(
                item,
                as_of=date.today()
            )
            st.markdown("#### 📋 Storage Guidance Results")

            if result["use_priority"] == "UNKNOWN":
                st.warning(result["reason"])
            else:
                st.success(
                    f"Recommended use reminder: "
                    f"{result['recommended_use_date']}"
                )

            if result["use_priority"] != "UNKNOWN":
                priority_column, days_column = st.columns(2, gap="large")

                with priority_column:
                    st.metric("Use Priority", result["use_priority"])

                with days_column:
                    st.metric("Days Remaining", result["days_remaining"])

                st.caption(
                    "This is a use-soon reminder, not a food safety determination."
                )


    with recall_column:
        st.subheader("🚨 Food Recall Checker")
        st.caption("Search FDA recall records for products that may have been recalled.")
        st.caption("Search results are not confirmation that your specific product is affected.")

        recall_product = st.text_input(
            "Enter a food product to check for FDA recalls",
            placeholder="Example: peanut butter"
        )

        if st.button(
            "🔍 Search FDA Recalls",
            type="primary",
            use_container_width=True
        ):
            if not recall_product.strip():
                st.warning("Please enter a product name.")
            else:
                with st.spinner("Searching FDA recall records..."):
                    recall_result = get_fda_recalls(
                        recall_product.strip(),
                        limit=10
                    )

                records = recall_result["records"]

                st.markdown("#### 📋 Recall Search Results")

                if recall_result["error"]:
                    st.error(
                        f"Recall search could not be completed: "
                        f"{recall_result['error']}"
                    )

                if records:
                    st.warning(
                        f"Found {len(records)} FDA recall records. "
                        "These are search results, not confirmed matches "
                        "to your specific product."
                    )

                    for record in records[:10]:
                        with st.expander(
                            record.get("product_description", "Recall record")
                        ):

                            st.caption(
                                "FDA recall record. Verify product identifiers" 
                                " before determining whether your item is affected."
                            )
                            
                            st.write(
                                "Recall number:",
                                record.get("recall_number", "Not available")
                            )
                            st.write(
                                "Reason:",
                                record.get("reason_for_recall", "Not available")
                            )
                            st.write(
                                "Recall status:",
                                record.get("status", "Not available")
                            )

                elif not recall_result["error"]:
                    st.info(
                        "No records returned for this search. "
                        "Product safety has not been verified."
                    )

                st.caption(
                    "FDA search only. Recall verification remains incomplete. "
                    "Confirm product identifiers and official recall details."
                )


if selected_page == "🍳 Recipes":
    st.header("🍳 Recipe Recommendations")
    st.caption(
        "Explore recipe ideas based on your pantry ingredients "
        "and review their recommendation status."
    )

    st.divider()

    st.write(
        "Discover recipe ideas using ingredients already in your pantry."
    )

    if st.button(
        "🍽️ Find Recipes",
        type="primary",
        use_container_width=True
    ):
        st.caption(
            "Recipe suggestions are based on your pantry ingredients. "
            "For additional peace of mind, you can check available "
            "recall information on the Food Safety page."
        )

        st.subheader("🥗 Sample Recipe Rankings")
        st.caption(
            "Explore how sample recipes rank against your saved pantry ingredients. "
            "These are examples, not verified recipe recommendations."
        )

        pantry_items = st.session_state.pantry_manager.get_items()

        screening = st.session_state.get("pantry_recall_screening")

        if screening is None:
            st.warning(
                "Your pantry has not been screened for recalls in this session. "
                "Visit Food Safety to run a check."
            )
        else:
            st.info(
                "Latest pantry screening: "
                f"{screening['usda_records_checked']} USDA records and "
                f"{screening['fda_records_checked']} FDA records reviewed. "
                "Screening remains incomplete."
            )

        ranked_recipes = rank_recipes(
            sample_recipes,
            pantry_items,
            0.60,
            0.40
        )

        for index, recipe in enumerate(ranked_recipes, start=1):
            with st.container(border=True):
                st.write(f"**{index}. {recipe['name']}**")
                st.caption(f"Sample ranking score: {recipe['score']:.1f}")

        st.caption(
            "Rankings use your saved pantry ingredients and sample recipes. "
            "Expiration dates are not yet connected to recipe scoring. "
            "These recipes have not passed recall verification "
            "and are not approved recommendations."
        )

if selected_page == "🍡 Mochi AI":
    st.header("🍡 Chat with Mochi")
    st.caption(
        "Your friendly AI kitchen companion for food storage, "
        "recipes, and pantry questions."
    )
    st.divider()

    left_panel, right_panel = st.columns([1.4, 1], gap="large")

    with left_panel:
        st.image(
            PROJECT_ROOT / "assets" / "mochi_avatar_transparent.png",
            width=140
        )

        st.subheader("Meet Mochi 🍡")
        st.write(
            "Your friendly kitchen companion! "
            "I'm here to help with recipes, food storage, "
            "and making the most of your pantry."
        )

   
    with right_panel:
        st.subheader("💬 Mochi Chat")
        st.caption("Your kitchen companion is ready to help!")

        with st.container(height=450, border=True):
            render_mochi_chat()



