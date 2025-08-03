import streamlit as st
import pandas as pd
import requests
import pycountry  # for country name → ISO conversion

# --- Helpers ---
def get_country_iso(country_name):
    try:
        return pycountry.countries.lookup(country_name).alpha_2
    except:
        return None

def search_fda_by_country_and_product_code(product_code, country_iso):
    url = (
        f"https://api.fda.gov/device/registrationlisting.json"
        f"?search=product_code:{product_code}+country_code:{country_iso}&limit=100"
    )
    try:
        res = requests.get(url)
        res.raise_for_status()
        return res.json().get("results", [])
    except Exception as e:
        st.error(f"FDA API Error: {e}")
        return []

# --- Streamlit App ---
st.title("FDA Medical Device Manufacturer Lookup by Country and Product Code")

# 1. Country Selection
country_name = st.selectbox(
    "Select a country:",
    sorted([country.name for country in pycountry.countries])
)

# 2. Product Code Input
product_code = st.text_input("Enter FDA Product Code (e.g. 'FOZ')")

# 3. Search
if country_name and product_code:
    country_iso = get_country_iso(country_name)
    if not country_iso:
        st.error("Could not find ISO code for selected country.")
    else:
        with st.spinner("Querying FDA database..."):
            results = search_fda_by_country_and_product_code(product_code, country_iso)

        if results:
            st.success(f"Found {len(results)} manufacturers.")
            df = pd.DataFrame([
                {
                    "Manufacturer": r.get("registrant_name", "N/A"),
                    "FEI Number": r.get("fei_number", "N/A"),
                    "Address": f"{r.get('address_1', '')}, {r.get('city', '')}, {r.get('state_province', '')} {r.get('zip_code', '')}, {r.get('country_code', '')}"
                }
                for r in results
            ])
            st.dataframe(df)
        else:
            st.warning("No results found for that product code and country.")

