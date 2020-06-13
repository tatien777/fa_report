PAGES = {
    "Home": "home",
    "Resources": "resources",
    "Gallery": "Gallery"
}

import streamlit as st 
st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", list(PAGES.keys()))
if selection == "Home" : st.markdown("page home")
if selection == "Resources" : st.markdown("page Resources")
if selection == "Gallery" : st.markdown("page Gallery")
# with st.spinner(f"Loading {selection} ..."):
#         ast.shared.components.write_page(page)
    
st.sidebar.title("Contribute")