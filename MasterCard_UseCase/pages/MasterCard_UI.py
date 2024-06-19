
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from MasterCard_UseCase.parser_TT140_MasterCard import *
from MasterCard_UseCase.processing_bank_sources import *
from datetime import date
st.sidebar.image("assets/Logo_hps_0.png", use_column_width=True)
st.header("📤 :violet[Upload Required Files to reconcile with Mastercard Report]", divider='rainbow')


uploaded_mastercard_file = st.file_uploader(":arrow_down: **Upload Mastercard File**", type=["001"])
uploaded_cybersource_file = st.file_uploader(":arrow_down: **Upload Cybersource File**", type=["csv"])
uploaded_pos_file = st.file_uploader(":arrow_down: **Upload POS File**", type=["csv"])
uploaded_sai_manuelle_file = st.file_uploader(":arrow_down: **Upload Manual Entry (***Saisie Manuelle***) File**", type=["csv"])
filtering_date = st.date_input("Please input filtering date for rejected transactions" )
uploaded_recycled_file = st.file_uploader(":arrow_down: **Upload Recycled Transactions File**", type=["xlsx"])

st.divider()
# standard columns for each source file
default_columns_cybersource = ['NBRE_TRANSACTION', 'MONTANT_TOTAL', 'CUR', 'FILIALE', 'RESEAU', 'TYPE_TRANSACTION']
default_columns_saisie_manuelle = ['NBRE_TRANSACTION', 'MONTANT_TOTAL', 'CUR', 'FILIALE', 'RESEAU']
default_columns_pos = ['FILIALE', 'RESEAU', 'TYPE_TRANSACTION', 'DATE_TRAI', 'CUR', 'NBRE_TRANSACTION', 'MONTANT_TOTAL']

day_after = None  # Initialize variable

if uploaded_mastercard_file is not None:
    try: 
        run_date, day_after = extract_date_from_mastercard_file(uploaded_mastercard_file.getvalue().decode("utf-8"))
        st.write("**Run date of MasterCard's Report is :calendar:**", run_date)
        st.write("**You will be performing reconciliation for date :calendar:**", day_after)
    except Exception as e:
        st.error(f"Error extracting date from Mastercard file")

total_transactions = {'Cybersource': 0, 'POS': 0, 'Manual Entry': 0}

try:
    if uploaded_cybersource_file:
        cybersource_file_path = save_uploaded_file(uploaded_cybersource_file)
        validate_file_name_and_date(uploaded_cybersource_file.name, 'CYBERSOURCE', date_to_validate=day_after)
        df_cybersource = reading_cybersource(cybersource_file_path)
        mastercard_transactions_cybersource = df_cybersource[df_cybersource['RESEAU'] == 'MASTERCARD INTERNATIONAL']
        total_transactions['Cybersource'] = mastercard_transactions_cybersource['NBRE_TRANSACTION'].sum()
    else:
        df_cybersource = pd.DataFrame(columns=default_columns_cybersource)
except Exception as e:
    st.error(f"Error processing Cybersource file check your uploaded file")

try:
    if uploaded_pos_file:
        pos_file_path = save_uploaded_file(uploaded_pos_file)
        validate_file_name_and_date(uploaded_pos_file.name, 'POS', date_to_validate=day_after)
        df_pos = reading_pos(pos_file_path)
        mastercard_transactions_pos = df_pos[(df_pos['RESEAU'] == 'MASTERCARD INTERNATIONAL') & 
                         (~df_pos['TYPE_TRANSACTION'].str.endswith('_MDS'))]
        total_transactions['POS'] = mastercard_transactions_pos['NBRE_TRANSACTION'].sum()
    else:
        df_pos = pd.DataFrame(columns=default_columns_pos)
except Exception as e:
    st.error(f"Error processing POS file check your uploaded file - make sure the date matches the Mastercard file date.")

try:
    if uploaded_sai_manuelle_file:
        sai_manuelle_file_path = save_uploaded_file(uploaded_sai_manuelle_file)
        validate_file_name_and_date(uploaded_sai_manuelle_file.name, 'SAIS_MANU', date_to_validate=day_after)
        df_sai_manuelle = reading_saisie_manuelle(sai_manuelle_file_path)
        mastercard_transactions_sai_manuelle = df_sai_manuelle[df_sai_manuelle['RESEAU'] == 'MASTERCARD INTERNATIONAL']
        total_transactions['Manual Entry'] = mastercard_transactions_sai_manuelle['NBRE_TRANSACTION'].sum()

    else:
        df_sai_manuelle = pd.DataFrame(columns=default_columns_saisie_manuelle)
except Exception as e:
    st.error(f"Error processing Manual Entry (Saisie Manuelle) file check your uploaded file")

try:
    filtered_cybersource_df, filtered_saisie_manuelle_df, filtered_pos_df = filtering_sources(df_cybersource, df_sai_manuelle, df_pos)
except Exception as e:
    st.error(f"Error filtering source files")

def highlight_non_reconciliated_row(row):
    return ['background-color: #F99485' if row['Rapprochement'] == 'not ok' else '' for _ in row]


# Pie Chart for Mastercard Transactions
if total_transactions['Cybersource'] > 0 or total_transactions['POS'] > 0 or total_transactions['Manual Entry'] > 0:
    st.header("	:bar_chart: Transaction Distribution by Source" , divider='grey')
    def create_interactive_pie_chart(total_transactions):
        labels = list(total_transactions.keys())
        sizes = list(total_transactions.values())
        
        fig = go.Figure(data=[go.Pie(labels=labels , values=sizes, hole=.3, textinfo='label+percent+value')])
        
        return fig

    # Create the pie chart
    fig = create_interactive_pie_chart(total_transactions)

    # Display the chart in Streamlit
    st.plotly_chart(fig)
    
try:
    if uploaded_mastercard_file:
        mastercard_file_path = save_uploaded_file(uploaded_mastercard_file)
        nbr_total_MC, rejected_summary, rejected_df = parse_t140_MC(mastercard_file_path)
        col1, col2, col3 = st.columns(3)
        col1.metric("**Total number of transactions in Mastercard file:**", value=nbr_total_MC)
        if uploaded_recycled_file:
            recycled_file_path = save_uploaded_file(uploaded_recycled_file)
            filtering_date = filtering_date.strftime('%Y-%m-%d')
            st.write("filtering date is ", filtering_date)
            df_recycled,merged_df, total_nbre_transactions = merging_with_recycled(recycled_file_path, filtered_cybersource_df, filtered_saisie_manuelle_df, filtered_pos_df , filtering_date )
            st.write("Recycled Transactions")
            st.dataframe(df_recycled)
            st.write("### Nombre de transactions des sources avec rej. recyc.", total_nbre_transactions)
            st.dataframe(merged_df)
        else:
            merged_df, total_nbre_transactions = merging_sources_without_recycled(filtered_cybersource_df, filtered_saisie_manuelle_df, filtered_pos_df)
            st.write("### Nombre de transactions des sources sans rej. recyc.", total_nbre_transactions)
            st.warning('Recycled file not uploaded. Reconciliation will be done without recycled transactions.')
        col2.metric("**Total number of transactions in the files:**", value=total_nbre_transactions )
        col3.metric("___Difference___", value=abs(nbr_total_MC - total_nbre_transactions),help="The net difference in transactions between the two sides is")
        
        if st.button('Reconciliate', type="primary", use_container_width=True):
            if nbr_total_MC == total_nbre_transactions:
                st.header('Reconciliation Result')
                df_reconciliated = handle_exact_match_csv(merged_df)
                st.success("Reconciliation done with exact match.")
                st.dataframe(df_reconciliated)
            else:
                df_non_reconciliated = handle_non_match_reconciliation(mastercard_file_path, merged_df)
                df_summary = calculate_rejected_summary(mastercard_file_path)
                df_rejections = extract_rejections(mastercard_file_path, currencies_settings, countries_settings)
                st.warning("Reconciliation done with non-exact match.")
                st.header('Reconciliation Result')
                st.dataframe(df_non_reconciliated.style.apply(highlight_non_reconciliated_row, axis=1))
                st.header('Rejection summary')
                st.dataframe(df_summary)
                st.header('Rejected transactions')
                st.dataframe(df_rejections)
    else:
        st.warning("Please upload all required files to proceed.")
except Exception as e:
    st.error(f"Error processing Mastercard file")
