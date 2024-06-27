import streamlit as st
from datetime import datetime
from database_actions import search_by_transaction_date, search_by_rapprochement

def main():
    st.sidebar.image("assets/Logo_hps_0.png", use_column_width=True)
    st.sidebar.divider()
    st.sidebar.page_link("app.py", label="**Accueil**" , icon="🏠")
    st.sidebar.page_link("pages/results_recon.py", label="**:alarm_clock: Historique**")
    st.sidebar.page_link("pages/MasterCard_UI.py", label=" **MasterCard Network Reconciliaiton Option**" , icon="🔀")

    st.title("Historique de Reconciliation")
    # Create date input and selectbox for multi-criteria search
    search_date = st.date_input("Select RUN Date", value=datetime.today(), key="search_date")
    formatted_date = search_date.strftime('%d-%b-%y').upper()
    
    options = ['OK', 'NOT OK']
    selected_option = st.selectbox('Choisir état de rapprochement:', options).upper()

    # Search and display the results when both criteria are provided and the search button is clicked
    if st.button("Search", key="search_button"):
        df_search_results = search_by_transaction_date(formatted_date)
        if not df_search_results.empty:
            # Normalize the 'Rapprochement' column to upper case for case-insensitive matching
            df_search_results['Rapprochement'] = df_search_results['Rapprochement'].str.upper()
            results_df = df_search_results[df_search_results['Rapprochement'] == selected_option]
            if not results_df.empty:
                st.write("Search Results")
                st.dataframe(results_df)
            else:
                st.write("No records found for the selected date and état de rapprochement.")
        else:
            st.write("No records found for the selected date.")

if __name__ == "__main__":
    main()