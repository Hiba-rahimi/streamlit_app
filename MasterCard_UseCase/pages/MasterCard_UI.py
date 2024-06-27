import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from MasterCard_UseCase.parser_TT140_MasterCard import *
from MasterCard_UseCase.processing_bank_sources import *
from database_actions import *
from streamlit_modal import Modal


def upload_all_sources():
    if uploaded_mastercard_file is not None:
        try:
            run_date, day_after = extract_date_from_mastercard_file(uploaded_mastercard_file.getvalue().decode("utf-8"))
            st.write("**Run date of MasterCard's Report is :calendar:**", run_date)
            st.write("**You will be performing reconciliation for date :calendar:**", day_after)
        except Exception as e:
            st.error(f"Error extracting date from Mastercard file: {e}")

    df_cybersource = pd.DataFrame(columns=default_columns_cybersource)
    df_pos = pd.DataFrame(columns=default_columns_pos)
    df_sai_manuelle = pd.DataFrame(columns=default_columns_saisie_manuelle)
    
    try:
        if uploaded_cybersource_file:
            cybersource_file_path= save_uploaded_file(uploaded_cybersource_file)
            validate_file_name_and_date(uploaded_cybersource_file.name, 'CYBERSOURCE', date_to_validate=day_after)
            df_cybersource = reading_cybersource(cybersource_file_path)
            mastercard_transactions_cybersource = df_cybersource[df_cybersource['RESEAU'] == 'MASTERCARD INTERNATIONAL']
            total_transactions['Cybersource'] = mastercard_transactions_cybersource['NBRE_TRANSACTION'].sum()
    except Exception as e:
        st.error(f"Error processing Cybersource file: {e}")

    try:
        if uploaded_pos_file:
            pos_file_path = save_uploaded_file(uploaded_pos_file)
            validate_file_name_and_date(uploaded_pos_file.name, 'POS', date_to_validate=day_after)
            df_pos = reading_pos(pos_file_path)
            mastercard_transactions_pos = df_pos[(df_pos['RESEAU'] == 'MASTERCARD INTERNATIONAL') & 
                            (~df_pos['TYPE_TRANSACTION'].str.endswith('_MDS'))]
            total_transactions['POS'] = mastercard_transactions_pos['NBRE_TRANSACTION'].sum()
    except Exception as e:
        st.error(f"Error processing POS file: {e}")

    try:
        if uploaded_sai_manuelle_file:
            sai_manuelle_file_path = save_uploaded_file(uploaded_sai_manuelle_file)
            validate_file_name_and_date(uploaded_sai_manuelle_file.name, 'SAIS_MANU', date_to_validate=day_after)
            df_sai_manuelle = reading_saisie_manuelle(sai_manuelle_file_path)
            mastercard_transactions_sai_manuelle = df_sai_manuelle[df_sai_manuelle['RESEAU'] == 'MASTERCARD INTERNATIONAL']
            total_transactions['Manual Entry'] = mastercard_transactions_sai_manuelle['NBRE_TRANSACTION'].sum()
    except Exception as e:
        st.error(f"Error processing Manual Entry (Saisie Manuelle) file: {e}")

    return df_cybersource, df_sai_manuelle, df_pos

def filter_sources(df_cybersource, df_sai_manuelle, df_pos):
    try:
        filtered_cybersource_df, filtered_saisie_manuelle_df, filtered_pos_df = filtering_sources(df_cybersource, df_sai_manuelle, df_pos)
        return filtered_cybersource_df, filtered_saisie_manuelle_df, filtered_pos_df
    except Exception as e:
        st.error(f"Error filtering source files: {e}")


def pie_chart():
    if total_transactions['Cybersource'] > 0 or total_transactions['POS'] > 0 or total_transactions['Manual Entry'] > 0:
        st.header("	:bar_chart: Transaction Distribution by Source", divider='grey')

        def create_interactive_pie_chart(total_transactions):
            labels = list(total_transactions.keys())
            sizes = list(total_transactions.values())
            fig = go.Figure(data=[go.Pie(labels=labels, values=sizes, hole=.3, textinfo='label+percent+value')])
            return fig

        fig = create_interactive_pie_chart(total_transactions)
        st.plotly_chart(fig)

def handle_recon(filtered_cybersource_df, filtered_saisie_manuelle_df, filtered_pos_df):
    try:
        # Initialize session state variables
        if 'df_reconciliated' not in st.session_state:
            st.session_state.df_reconciliated = None
        if 'df_non_reconciliated' not in st.session_state:
            st.session_state.df_non_reconciliated = None
        if 'df_summary' not in st.session_state:
            st.session_state.df_summary = None
        if 'df_rejections' not in st.session_state:
            st.session_state.df_rejections = None
        if 'show_modal' not in st.session_state:
            st.session_state.show_modal = False
        
        if uploaded_mastercard_file:
            mastercard_file_path = save_uploaded_file(uploaded_mastercard_file)
            nbr_total_MC, rejected_summary, rejected_df = parse_t140_MC(mastercard_file_path)
            col1, col2, col3 = st.columns(3)
            col1.metric("**Total number of transactions in Mastercard file:**", value=nbr_total_MC)

            if uploaded_recycled_file:
                recycled_file_path = save_uploaded_file(uploaded_recycled_file)
                df_recyc = pd.read_excel(recycled_file_path)
                st.write("filtering date is ", filtering_date)
                df_recycled, merged_df, total_nbre_transactions = merging_with_recycled(
                    recycled_file_path, filtered_cybersource_df, filtered_saisie_manuelle_df, filtered_pos_df, filtering_date)
                st.write("Recycled Transactions")
                st.dataframe(df_recycled)
                st.write("### Nombre de transactions des sources avec rej. recyc.", total_nbre_transactions)
                st.dataframe(merged_df)
            else:
                merged_df, total_nbre_transactions = merging_sources_without_recycled(
                    filtered_cybersource_df, filtered_saisie_manuelle_df, filtered_pos_df)
                st.write("### Nombre de transactions des sources sans rej. recyc.", total_nbre_transactions)
                st.warning('Recycled file not uploaded. Reconciliation will be done without recycled transactions.')

            col2.metric("**Total number of transactions in the files:**", value=total_nbre_transactions)
            col3.metric("___Difference___", value=abs(nbr_total_MC - total_nbre_transactions), help="The net difference in transactions between the two sides is")

            if st.button('Reconciliate', type="primary", use_container_width=True):
                if nbr_total_MC == total_nbre_transactions:
                    st.header('Reconciliation Result')
                    st.session_state.df_reconciliated = handle_exact_match_csv(merged_df)
                    st.success("Reconciliation done with exact match.")
                else:
                    st.session_state.df_non_reconciliated = handle_non_match_reconciliation(mastercard_file_path, merged_df)
                    st.session_state.df_summary = calculate_rejected_summary(mastercard_file_path)
                    st.session_state.df_rejections = extract_rejections(mastercard_file_path, currencies_settings, countries_settings)
                    st.warning("Reconciliation done with non-exact match.")
                    
            # Always display the dataframes stored in session state
            if st.session_state.df_reconciliated is not None:
                st.header('Reconciliation Result')
                st.dataframe(st.session_state.df_reconciliated)
                show_modal_confirmation(
                    modal_key="reconciliation_modal",
                    title="Confirm Insert",
                    insert_type= "reconciliation",
                    message="Are you sure you want to insert the reconciliated transactions into the database?",
                    confirm_action=insert_reconciliated_data,
                    data=st.session_state.df_reconciliated
                )
                run_date, day_after = extract_date_from_mastercard_file(uploaded_mastercard_file.getvalue().decode("utf-8"))
                excel_path_email_1 , file_name_1= download_file(recon=True, df=st.session_state.df_reconciliated, file_partial_name='results_recon_MC', button_label=":arrow_down: Téléchargez les résultats de réconciliation", run_date=run_date)

                
                
            if st.session_state.df_non_reconciliated is not None:
                st.header('Reconciliation Result')
                st.dataframe(st.session_state.df_non_reconciliated.style.apply(highlight_non_reconciliated_row, axis=1))
                show_modal_confirmation(
                    modal_key="non_reconciliation_modal",
                    title="Confirm Insert",
                    insert_type= "reconciliation",
                    message="Are you sure you want to insert the reconciliated transactions into the database?",
                    confirm_action=insert_reconciliated_data,
                    data=st.session_state.df_non_reconciliated
                )
                run_date, day_after = extract_date_from_mastercard_file(uploaded_mastercard_file.getvalue().decode("utf-8"))
                excel_path_email_1 , file_name_1= download_file(recon=True, df=st.session_state.df_non_reconciliated, file_partial_name='results_recon_MC', button_label=":arrow_down: Téléchargez les résultats de réconciliation", run_date=run_date)

                st.header('Rejection summary')
                st.dataframe(st.session_state.df_summary)
   
                show_modal_confirmation(
                    modal_key="summary_modal",
                    title="Confirm Insert",
                    insert_type="summary",
                    message="Are you sure you want to insert the reconciliated summary into the database?",
                    confirm_action=insert_rejection_summary,
                    data=st.session_state.df_summary
                )

                run_date, day_after = extract_date_from_mastercard_file(uploaded_mastercard_file.getvalue().decode("utf-8"))
                excel_path_email_2 , file_name_2 = download_file(recon=False, df=st.session_state.df_summary, file_partial_name='rejected_summary_MC', button_label=":arrow_down: Téléchargez le résumé des rejets", run_date=run_date)
       
               
                st.header('Rejected transactions')
                st.dataframe(st.session_state.df_rejections)
        
                show_modal_confirmation(
                    modal_key="rejections_modal",
                    title="Confirm Insert",
                    insert_type= "rejects",
                    message="Are you sure you want to insert the rejects into the database?",
                    confirm_action=insert_rejected_transactions,
                    data=st.session_state.df_rejections
                )
          
                run_date, day_after = extract_date_from_mastercard_file(uploaded_mastercard_file.getvalue().decode("utf-8"))
                excel_path_email_3 , file_name_3= download_file(recon=False, df=st.session_state.df_rejections, file_partial_name='rejected_transactions_MC', button_label=":arrow_down: Téléchargez les rejets", run_date=run_date)
                    
        else:
            st.warning("Please upload all required files to proceed.")
    except Exception as e:
        st.error(f"Error processing Mastercard file {e}")



# Function to show a modal confirmation dialog
def show_modal_confirmation(modal_key, title, message, confirm_action, data, insert_type):
    modal = Modal(key=modal_key, title=title)

    if st.button(f'Sauvegarder résultats de {insert_type}', key=f'sauvegarder_resultats_{modal_key}',type="primary", use_container_width=True):
        modal.open()

    if modal.is_open():
        with modal.container():
            st.write(message)
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Yes", key=f"{modal_key}_yes"):
                    confirm_action(data)
                    modal.close()
   
            with col2:
                if st.button("No", key=f"{modal_key}_no"):
                    modal.close()
 
    return modal

def main():
    st.sidebar.image("assets/Logo_hps_0.png", use_column_width=True)
    st.header("📤 :violet[Upload Required Files to reconcile with Mastercard Report]", divider='rainbow')
    st.sidebar.page_link("pages/results_recon.py", label=" **Résultats de réconciliation**")


    global uploaded_mastercard_file, uploaded_cybersource_file, uploaded_pos_file, uploaded_sai_manuelle_file, filtering_date, uploaded_recycled_file
    uploaded_mastercard_file = st.file_uploader(":arrow_down: **Upload Mastercard File**", type=["001"])
    uploaded_cybersource_file = st.file_uploader(":arrow_down: **Upload Cybersource File**", type=["csv"])
    uploaded_pos_file = st.file_uploader(":arrow_down: **Upload POS File**", type=["csv"])
    uploaded_sai_manuelle_file = st.file_uploader(":arrow_down: **Upload Manual Entry (***Saisie Manuelle***) File**", type=["csv"])
    filtering_date = st.date_input("Please input filtering date for rejected transactions")
    uploaded_recycled_file = st.file_uploader(":arrow_down: **Upload Recycled Transactions File**", type=["xlsx"])

    st.divider()
    global default_columns_cybersource, default_columns_saisie_manuelle, default_columns_pos, total_transactions, day_after

    default_columns_cybersource = ['NBRE_TRANSACTION', 'MONTANT_TOTAL', 'CUR', 'FILIALE', 'RESEAU', 'TYPE_TRANSACTION']
    default_columns_saisie_manuelle = ['NBRE_TRANSACTION', 'MONTANT_TOTAL', 'CUR', 'FILIALE', 'RESEAU']
    default_columns_pos = ['FILIALE', 'RESEAU', 'TYPE_TRANSACTION', 'DATE_TRAI', 'CUR', 'NBRE_TRANSACTION', 'MONTANT_TOTAL']

    day_after = None
    total_transactions = {'Cybersource': 0, 'POS': 0, 'Manual Entry': 0}

    try:
        df_cybersource, df_sai_manuelle, df_pos = upload_all_sources()
    except Exception as e:
        st.error(f"Error uploading sources")

    try:
        filtered_cybersource_df, filtered_saisie_manuelle_df, filtered_pos_df = filter_sources(df_cybersource, df_sai_manuelle, df_pos)
    except Exception as e:
        st.error(f"Cannot process the files")

    pie_chart()

    try:
        handle_recon(filtered_cybersource_df, filtered_saisie_manuelle_df, filtered_pos_df)
    except Exception as e:
        st.error(f"Cannot proceed with reconciliation")
    
    # Handling session state variables based on file uploads
    if not uploaded_mastercard_file and not uploaded_cybersource_file and not uploaded_pos_file and not uploaded_sai_manuelle_file:
        # Reset session state variables if no files are uploaded
        st.session_state.df_reconciliated = None
        st.session_state.df_non_reconciliated = None
        st.session_state.df_summary = None
        st.session_state.df_rejections = None
        st.session_state.show_modal = False


if __name__ == "__main__":
    main()