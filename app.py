import streamlit as st 
import revenue.main as revenue_main 
import utils.test_auth as auth
import user_reconile.main as user_main 

PAGES = {
    "Revenue_Cost": "",
    "User_recon": "",
    "Supplier_recon": ""
}


def run_app():
    
    valid = auth.confirm_button_example()
    
    if valid: 
        st.sidebar.title("Navigation")
        selection = st.sidebar.radio("Go to", list(PAGES.keys()))
        if selection == "Revenue_Cost" : revenue_main.auto_main()
        if selection == "User_recon" : user_main.main()
            # st.markdown("test page User")
        if selection == "Supplier_recon" : st.markdown("test page  Supplier_recon")

run_app()