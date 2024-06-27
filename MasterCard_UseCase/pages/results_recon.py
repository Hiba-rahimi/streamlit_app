import streamlit as st
from datetime import datetime
from MasterCard_UseCase.database_actions import *

def main():
    st.sidebar.image("assets/Logo_hps_0.png", use_column_width=True)
    st.sidebar.divider()
    st.sidebar.page_link("app.py", label="**Accueil**" , icon="🏠")
    st.sidebar.page_link("pages/results_recon.py", label="**:alarm_clock: Historique**")
    st.sidebar.page_link("pages/MasterCard_UI.py", label="  **🔀 MasterCard Network Reconciliaiton Option**" )
    st.header("Reconciliation History" , divider= 'rainbow')
    st.write("  ")
    # Create date input and selectbox for multi-criteria search
    search_date = st.date_input("**Select a processing date :**", value=datetime.today(), key="search_date")
    formatted_date = search_date.strftime('%d-%b-%y').upper()


    # Search and display the results when both criteria are provided and the search button is clicked
    if st.button(":mag_right: **Search**", key="search_button" , type="primary" , use_container_width=True):
        df_search_results = search_by_transaction_date(formatted_date)
        if not df_search_results.empty:
            # Normalize the 'Rapprochement' column to upper case for case-insensitive matching
            if not df_search_results.empty:
                st.write("Search Results")
                st.dataframe(df_search_results)
            else:
                st.warning("No records found for the selected date and état de rapprochement.")
        else:
            st.warning("No records found for the selected date.")

if __name__ == "__main__":
    main()