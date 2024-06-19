import streamlit as st
import pandas as pd
from MasterCard_UseCase.parser_TT140_MasterCard import *
from MasterCard_UseCase.processing_bank_sources import *
from datetime import date

import plotly.graph_objects as go
st.sidebar.image("assets/Logo_hps_0.png", use_column_width=True)
st.header("📤 :violet[Chargez les fichiers requis pour la réconciliation avec le rapport Mastercard]", divider='rainbow')

uploaded_mastercard_file = st.file_uploader(":arrow_down: **Chargez le fichier Mastercard**", type=["001"])
uploaded_cybersource_file = st.file_uploader(":arrow_down: **Chargez le fichier Cybersource**", type=["csv"])
uploaded_pos_file = st.file_uploader(":arrow_down: **Chargez le fichier POS**", type=["csv"])
uploaded_sai_manuelle_file = st.file_uploader(":arrow_down: **Chargez le fichier de saisie manuelle**", type=["csv"])
filtering_date = st.date_input("Veuillez entrer la date de filtrage pour les transactions rejetées")
uploaded_recycled_file = st.file_uploader(":arrow_down: **Chargez le fichier des transactions recyclées**", type=["xlsx"])

st.divider()
# colonnes standard pour chaque fichier source
default_columns_cybersource = ['NBRE_TRANSACTION', 'MONTANT_TOTAL', 'CUR', 'FILIALE', 'RESEAU', 'TYPE_TRANSACTION']
default_columns_saisie_manuelle = ['NBRE_TRANSACTION', 'MONTANT_TOTAL', 'CUR', 'FILIALE', 'RESEAU']
default_columns_pos = ['FILIALE', 'RESEAU', 'TYPE_TRANSACTION', 'DATE_TRAI', 'CUR', 'NBRE_TRANSACTION', 'MONTANT_TOTAL']

day_after = None  # Initialiser la variable

if uploaded_mastercard_file is not None:
    try: 
        run_date, day_after = extract_date_from_mastercard_file(uploaded_mastercard_file.getvalue().decode("utf-8"))
        st.write("**Run date extraite du rapport Mastercard est :calendar:**", run_date)
        st.write("**Vous effectuerez la réconciliation pour la date :calendar:**", day_after)
    except Exception as e:
        st.error(f"Erreur lors de l'extraction de la date à partir du fichier Mastercard")

total_transactions = {'Cybersource': 0, 'POS': 0, 'Saisie Manuelle': 0}

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
    st.error(f"Erreur lors du traitement du fichier Cybersource, vérifiez votre fichier chargé")

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
    st.error(f"Erreur lors du traitement du fichier POS, vérifiez votre fichier chargé - assurez-vous que la date correspond à celle du fichier Mastercard")

try:
    if uploaded_sai_manuelle_file:
        sai_manuelle_file_path = save_uploaded_file(uploaded_sai_manuelle_file)
        validate_file_name_and_date(uploaded_sai_manuelle_file.name, 'SAIS_MANU', date_to_validate=day_after)
        df_sai_manuelle = reading_saisie_manuelle(sai_manuelle_file_path)
        mastercard_transactions_sai_manuelle = df_sai_manuelle[df_sai_manuelle['RESEAU'] == 'MASTERCARD INTERNATIONAL']
        total_transactions['Saisie Manuelle'] = mastercard_transactions_sai_manuelle['NBRE_TRANSACTION'].sum()

    else:
        df_sai_manuelle = pd.DataFrame(columns=default_columns_saisie_manuelle)
except Exception as e:
    st.error(f"Erreur lors du traitement du fichier de saisie manuelle, vérifiez votre fichier chargé")

try:
    filtered_cybersource_df, filtered_saisie_manuelle_df, filtered_pos_df = filtering_sources(df_cybersource, df_sai_manuelle, df_pos)
except Exception as e:
    st.error(f"Erreur lors du filtrage des fichiers sources")

def highlight_non_reconciliated_row(row):
    return ['background-color: #F99485' if row['Rapprochement'] == 'not ok' else '' for _ in row]


# Diagramme circulaire pour les transactions Mastercard
if total_transactions['Cybersource'] > 0 or total_transactions['POS'] > 0 or total_transactions['Saisie Manuelle'] > 0:
    st.header("	:bar_chart: Répartition des transactions par source", divider='grey')
    def create_interactive_pie_chart(total_transactions):
        labels = list(total_transactions.keys())
        sizes = list(total_transactions.values())
        
        fig = go.Figure(data=[go.Pie(labels=labels , values=sizes, hole=.3, textinfo='label+percent+value')])
        
        return fig

    # Créer le diagramme circulaire
    fig = create_interactive_pie_chart(total_transactions)

    # Afficher le diagramme dans Streamlit
    st.plotly_chart(fig)
    
try:
    if uploaded_mastercard_file:
        mastercard_file_path = save_uploaded_file(uploaded_mastercard_file)
        nbr_total_MC, rejected_summary, rejected_df = parse_t140_MC(mastercard_file_path)
        col1, col2, col3 = st.columns(3)
        col1.metric("**Nombre total de transactions dans le fichier Mastercard :**", value=nbr_total_MC)
        if uploaded_recycled_file:
            recycled_file_path = save_uploaded_file(uploaded_recycled_file)
            filtering_date = filtering_date.strftime('%Y-%m-%d')
            st.write("La date de filtrage est ", filtering_date)
            df_recycled,merged_df, total_nbre_transactions = merging_with_recycled(recycled_file_path, filtered_cybersource_df, filtered_saisie_manuelle_df, filtered_pos_df , filtering_date )
            st.write("Transactions recyclées")
            st.dataframe(df_recycled)
            st.write("### Nombre de transactions des sources avec rejets recyclés :", total_nbre_transactions)
            st.dataframe(merged_df)
        else:
            merged_df, total_nbre_transactions = merging_sources_without_recycled(filtered_cybersource_df, filtered_saisie_manuelle_df, filtered_pos_df)
            st.write("### Nombre de transactions des sources sans rejets recyclés :", total_nbre_transactions)
            st.warning('Fichier recyclé non chargé. La réconciliation sera effectuée sans les transactions recyclées.')
        col2.metric("**Nombre total de transactions dans les fichiers :**", value=total_nbre_transactions )
        col3.metric("___Différence___", value=abs(nbr_total_MC - total_nbre_transactions),help="La différence nette de transactions entre les deux côtés est")
        
        if st.button('Réconcilier', type="primary", use_container_width=True):
            if nbr_total_MC == total_nbre_transactions:
                st.header('Résultat de la réconciliation')
                df_reconciliated = handle_exact_match_csv(merged_df)
                st.success("Réconciliation effectuée avec une correspondance exacte.")
                st.dataframe(df_reconciliated)
            else:
                df_non_reconciliated = handle_non_match_reconciliation(mastercard_file_path, merged_df)
                df_summary = calculate_rejected_summary(mastercard_file_path)
                df_rejections = extract_rejections(mastercard_file_path, currencies_settings, countries_settings)
                st.warning("Réconciliation effectuée avec une correspondance non exacte.")
                st.header('Résultat de la réconciliation')
                st.dataframe(df_non_reconciliated.style.apply(highlight_non_reconciliated_row, axis=1))
                st.header('Résumé des rejets')
                st.dataframe(df_summary)
                st.header('Transactions rejetées')
                st.dataframe(df_rejections)
               # st.write("Nombre de transactions rejetée du fichier Mastercard : ", df_summary.iloc[0, 1])
               # st.write("rejets extraits du fichier MasterCard : ",total_nbre_transactions - nbr_total_MC  )
               # if total_nbre_transactions - nbr_total_MC == df_summary.iloc[0, 1]:
               #     st.success("Les rejets extraits du fichier MasterCard ont bien été justifiés")
               # else:
               #     st.warning("Les rejets extraits du fichier MasterCard n'ont pas pu être justifiés.")
    else:
        st.warning("Veuillez Chargez tous les fichiers requis pour continuer.")
except Exception as e:
    st.error(f"Erreur lors du traitement du fichier Mastercard")
