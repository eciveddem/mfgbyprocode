import streamlit as st
import pandas as pd
import requests
import pycountry

# --- Convert country name to ISO code ---
def get_country_iso(country_name):
    try:
        return pycountry.countries.lookup(country_name).alpha_2
    except:
        return None

# --- Get labelers from GUDID API by product code ---
def get_labelers_by_product_code(product_code):
    url = f"https://api.fda.gov/device/udi.json?search=product_code:{product_code}&limit=100"
    try:
        res = requests.get(url)
        res.raise_for_status()
        results = res.json().get("results", [])
        labelers = list(set([r.get("labeler_name", "").strip() for r in results if r.get("labeler_name")]))
        return labelers
    except Exception as e:
        st.error(f"GUDID API Error: {e}")
        return []

# --- Search registration data by labeler name ---
def search_registration_by_labeler(labeler_name):
    url = f"https://api.fda.gov/device/registrationlisting.json?search=registrant_name:\"{labeler_name}\"&limit=100"
    try:
        res = requests.get(url)
        res.raise_for_status()
        return res.json().get("results", [])
    except:
        return []

# --- Streamlit App ---
def main():
    st.title("🔍 FDA Manufacturer Lookup by Product Code and Country")

    # Inputs
    product_code = st.text_input("🏷️ Enter FDA Product Code (e.g., 'FMF')")

    country_name = st.selectbox(
        "🌍 Select a country:",
        sorted([country.name for country in pycountry.countries])
    )

    # Execute search
    if product_code and country_name:
        country_iso = get_country_iso(country_name)
        if not country_iso:
            st.error("Invalid country.")
            return

        with st.spinner("Fetching labelers from GUDID..."):
            labelers = get_labelers_by_product_code(product_code)

        if not labelers:
            st.warning("No labelers found for this product code.")
            return

        st.info(f"🔎 Found {len(labelers)} labeler(s) for product code '{product_code}'.")

        manufacturers = []

        with st.spinner("Searching FDA Registration data..."):
            for labeler in labelers:
                registrations = search_registration_by_labeler(labeler)
                for r in registrations:
                    if r.get("country_code", "").upper() == country_iso:
                        manufacturers.append({
                            "Manufacturer": r.get("registrant_name", "N/A"),
                            "FEI Number": r.get("fei_number", "N/A"),
                            "Address": f"{r.get('address_1', '')}, {r.get('city', '')}, "
                                       f"{r.get('state_province', '')} {r.get('zip_code', '')}, {r.get('country_code', '')}"
                        })

        if manufacturers:
            st.success(f"✅ Found {len(manufacturers)} manufacturer(s) in {country_name}.")
            df = pd.DataFrame(manufacturers)
            st.dataframe(df)
        else:
            st.warning(f"No manufacturers found in {country_name} for that product code.")

if __name__ == "__main__":
    main()
