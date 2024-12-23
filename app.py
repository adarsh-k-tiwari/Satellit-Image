# Importing the libraries
import streamlit as st
import requests
import os
import pandas as pd
from dotenv import load_dotenv
from io import BytesIO
from PIL import Image

# Load environment variables
load_dotenv()

# Set page title and icon
st.set_page_config(
    page_title="Satellite Images",
    page_icon=":earth_americas:️",
)

# Create and display the DataFrame
data = {
    "Address": [],
    "Latitude": [],
    "Longitude": [],
    "API URL": []
}


# Function for pulling out the coordinates of location provided
def get_coordinates(api_key, address):
    """
    Fetch geographical coordinates for a given address using Google Maps API.
    Parameters:
        api_key: The Google Maps API key
        address: The address to fetch coordinates for the location provided
    Return:
        Longitude and latitude of the location
    """

    endpoint = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": api_key}
    response = requests.get(endpoint, params=params)
    data = response.json()
    # st.write(data)
    if response.status_code == 200 and data['results']:
        return data['results'][0]['geometry']['location']
    return None

def get_mapbox_image(api_key, latitude, longitude):
    endpoint = f"https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v12/static/{longitude},{latitude},16/600x400@2x"
    params = {"access_token": api_key}
    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))
        return img
    else:
        return None

# Add CSS to set background image
def set_background(image_url):
    st.markdown(f"""
    <style>
        .stApp{{
        background-image: url("{image_url}");
        background-position: center;
        background-repeat: no-repeat;
        background-size: cover;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        }}
        [data-testid="stHeader"]{{
        background-color: transparent;}}
    </style>
""", unsafe_allow_html=True)
    
main_bg_url = "https://i.postimg.cc/hvLy6wcG/TAMU-bg-1.jpg"
set_background(main_bg_url)

# Streamlit app
def main():
    st.markdown('<h1 style="text-align: center"><span style="color:#ffffff;font-family: Poppins, sans-serif; font-size: 1.5em;font-weight:500">Satellite Image Viewer</span></h1>', unsafe_allow_html=True)    
    st.markdown('<div style="color:#E5E5E5;text-align: center; font-family: Poppins, sans-serif; font-style: italic;">Generate street view satellite images!</div>', unsafe_allow_html=True)
    # set_background(main_bg_url)
    st.divider()
     # Initialize session state for DataFrame    
        
    tab1, tab2 = st.tabs(["Generate Image", "Database"])
    with tab1:
        # Input form for location and actions
        with st.form(key="input_form", border=False):
            address = st.text_input("Enter your favorite place")
            submit = st.form_submit_button("Submit")

        if submit and address:
            # Setting up the API keys
            google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
            maps_api_key = os.getenv("MAPS_API_KEY")

            # Option 4: AI Vision
            location = get_coordinates(google_maps_api_key, address)
            if location:
                st.write(f"{address} Details:\n")
                st.write(f"Latitude: {location['lat']} Longitude: {location['lng']}")
                with st.spinner("Generating Satellite Image..."):
                    image_bytes = get_mapbox_image(maps_api_key, location['lat'], location['lng'])
                    
                    # Update the DataFrame in session state
                    if not st.session_state.location_data["Address"].str.contains(address, case=False).any():
                        mapbox_url = f"https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v12/static/{location['lng']},{location['lat']},16/600x400@2x?access_token=maps_api_key"
                        new_row = pd.DataFrame(
                            {"Address": [address], "Latitude": [location['lat']], "Longitude": [location['lng']], "API URL": [mapbox_url]}
                        )
                        st.session_state.location_data = pd.concat([st.session_state.location_data, new_row], ignore_index=True)
                    if image_bytes:
                        st.image(image_bytes, caption=f"Satellite Image of {address}.")
                    else:
                        st.error("Unable to fetch the image for the place.")

        elif submit:
            st.error("Please enter a location.")
    
    
    with tab2:
        # Database connection
        if "location_data" not in st.session_state:
            st.session_state.location_data = pd.DataFrame(columns=["Address", "Latitude", "Longitude", "API URL"])
        st.markdown("### Address Data")
        st.dataframe(st.session_state.location_data, hide_index=True, use_container_width=True)


if __name__ == "__main__":
    main()