# SmartPantry AI
# Main Streamlit application

import sys
from pathlib import Path

from modules.pantry_manager import PantryManager

from modules.supabase_client import get_supabase_client

from modules.supabase_auth import sign_in_user, sign_out_user

from modules.supabase_pantry import (
    load_user_pantry,
    add_pantry_item,
    delete_user_pantry_item,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from modules.image_recognition import recognize_food
import tempfile
from datetime import date
from modules.storage_guidance import evaluate_foodkeeper
from modules.recall_checker import get_fda_recalls
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

from modules.ai_assistant import ask_ai

from modules.barcode_lookup import identify_product


st.set_page_config(
    page_title="SmartPantry AI",
    page_icon="🥗",
    layout="wide"
)

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


st.title("🥗 SmartPantry AI")
st.write("Your intelligent kitchen assistant.")

st.info("Welcome! Manage your pantry, check food safety, and discover recipes.")

pantry_tab, scan_tab, safety_tab, recipes_tab, mochi_tab = st.tabs(
    [
        "🥕 My Pantry",
        "📷 Scan Food",
        "🧊 Food Safety",
        "🍳 Recipes",
        "🍡 Mochi"
    ]
)

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


with pantry_tab:
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
            try:
                add_pantry_item(
                    st.session_state.supabase_client,
                    ingredient_name.strip(),
                    quantity,
                    unit
                )

                st.session_state.pantry_manager.add_item(
                    ingredient_name.strip(),
                    quantity,
                    unit
                )

                st.success("Ingredient added to your pantry!")

            except Exception:
                st.error("Unable to save ingredient. Please try again.")

        else:
            st.warning("Please enter an ingredient name.")

    st.subheader("🗑️ Remove Ingredient")



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

    pantry_items = st.session_state.pantry_manager.get_items()

    if pantry_items:
        st.dataframe(
            pantry_items,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Your pantry is empty. Add your first ingredient!")

with scan_tab:
    image_column, barcode_column = st.columns(2, gap="large")

    with image_column:
        st.subheader("📷 Food Image Recognition")

        uploaded_image = st.file_uploader(
            "Upload a food image",
            type=["jpg", "jpeg", "png"]
        )

        if uploaded_image is not None:
            st.image(uploaded_image, caption="Uploaded food image")

            if st.button("🔍 Identify Food"):
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

                    if recognized_food.lower() == "unknown":
                        st.warning("Food could not be identified.")
                    else:
                        st.success(f"Identified food: {recognized_food}")

                except Exception as error:
                    st.error(f"Image recognition failed: {error}")

                finally:
                    if temporary_path is not None:
                        temporary_path.unlink(missing_ok=True)


with safety_tab:
    storage_column, recall_column = st.columns(2, gap="large")

    with storage_column:
        st.subheader("🧊 Food Storage Recommendations")

        storage_food = st.text_input(
            "Ingredient for storage guidance",
            value="carrots"
        )

        purchase_date = st.date_input(
            "Purchase date",
            value=date.today()
        )

        if st.button("🧊 Check Storage Guidance"):
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

            if result["use_priority"] == "UNKNOWN":
                st.warning(result["reason"])
            else:
                st.success(
                    f"Recommended use reminder: "
                    f"{result['recommended_use_date']}"
                )

                st.write(
                    f"Use priority: {result['use_priority']}"
                )

                st.write(
                    f"Days remaining: {result['days_remaining']}"
                )

                st.caption(
                    "This is a use-soon reminder, not a food safety determination."
                )


with recall_column:
    st.subheader("🚨 Food Recall Checker")

    recall_product = st.text_input(
        "Enter a food product to check for FDA recalls",
        placeholder="Example: peanut butter"
    )

    if st.button("🔍 Search FDA Recalls"):
        if not recall_product.strip():
            st.warning("Please enter a product name.")
        else:
            with st.spinner("Searching FDA recall records..."):
                recall_result = get_fda_recalls(
                    recall_product.strip(),
                    limit=10
                )

            records = recall_result["records"]

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


with recipes_tab:
    st.subheader("🍳 Recipe Recommendations")

    st.write(
        "Find recipes using pantry ingredients, "
        "with recall verification required before recommending them."
    )

    if st.button("🍽️ Find Recipes"):
        st.info(
            "Recipe recommendations require verified recall clearance. "
            "Ingredients with incomplete recall checks cannot be "
            "approved for recipe recommendations."
        )

        st.subheader("Recipe Ranking Using Your Pantry")

        ranked_recipes = rank_recipes(
            sample_recipes,
            pantry_items,
            0.60,
            0.40
        )

        for index, recipe in enumerate(ranked_recipes, start=1):
            st.write(
                f"{index}. {recipe['name']} "
                f"— Score: {recipe['score']:.1f}"
            )

        st.caption(
            "Rankings use your saved pantry ingredients and sample recipes. "
            "Expiration dates are not yet connected to recipe scoring. "
            "These recipes have not passed recall verification "
            "and are not approved recommendations."
        )

with mochi_tab:
    st.image(PROJECT_ROOT / "assets" / "mochi_avatar.png", width=140)
    st.subheader("Meet Mochi, Your AI Kitchen Assistant")

    mochi_question = st.text_input(
        "Ask Mochi a question",
        placeholder="Example: How should I store fresh spinach?"
    )

    if st.button("💬 Ask Mochi"):
        if not mochi_question.strip():
            st.warning("Please enter a question for Mochi.")
        else:
            with st.spinner("Mochi is thinking..."):
                mochi_response = ask_ai(mochi_question.strip())

            st.info(mochi_response)


with barcode_column:
    st.subheader("📦 Barcode Product Lookup")

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

        if st.button("🔍 Identify Product"):
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

        confirmed_quantity = st.number_input(
            "Quantity to add",
            min_value=1,
            value=1,
            step=1,
            key="confirmed_barcode_quantity"
        )

        confirmed_unit = st.selectbox(
            "Unit",
            ["item", "bag", "box", "can", "bottle", "lb", "oz", "g", "kg"],
            key="confirmed_barcode_unit"
        )

        if st.button("✅ Confirm and Add to Pantry"):
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

