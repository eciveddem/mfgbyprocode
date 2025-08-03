import streamlit as st
import pandas as pd
import requests
import pycountry  # to convert country name to ISO code

# --- Convert country name to ISO 2-letter code ---
def get_country_iso(country_name):
    try:
        return pycountry.countries.lookup(country_name).alpha_2
    except:
        return None

# --- Query FDA API and filter locally by country ---
def search_fda_by_country_and_product_code(product_code, country_iso):
    url = (
        f"https://api.fda.gov/device/registrationlisting.json"
        f"?search=product_code:{product_code}&limit=100"
    )
    try:
        res = requests.get(url)
        res.raise_for_status()
        results = res.json().get("results", [])
        # Locally filter results by country_code
        filtered = [r for r in results if r.get("country_code", "").upper() == country_iso.upper()]
        return filtered
    except Exception as e:
        st.error(f"FDA API Error: {e}")
        return []

# --- Streamlit App ---
def main():
    st.title("🔍 FDA Manufacturer Lookup by Country + Product Code")

    # Country selection
    country_name = st.selectbox(
        "🌍 Select a country:",
        sorted([country.name for country in pycountry.countries])
    )

    # Product code input
    product_code = st.text_input("🏷️ Enter FDA Product Code (e.g., 'FOZ')")

    # Trigger search
    if country_name and product_code:
        country_iso = get_country_iso(country_name)
        if not country_iso:
            st.error("Invalid country selection.")
            return

        with st.spinner("Querying FDA database..."):
            results = search_fda_by_country_and_product_code(product_code, country_iso)

        if not results:
            st.info("No matching manufacturers found in that country for this product code.")
        else:
            st.success(f"Found {len(results)} manufacturers.")
            df = pd.DataFrame([
                {
                    "Manufacturer": r.get("registrant_name", "N/A"),
                    "FEI Number": r.get("fei_number", "N/A"),
                    "Address": f"{r.get('address_1', '')}, {r.get('city', '')}, "
                               f"{r.get('state_province', '')} {r.get('zip_code', '')}, {r.get('country_code', '')}"
                }
                for r in results
            ])
            st.dataframe(df)

if __name__ == "__main__":
    main()
