import streamlit as st
import pandas as pd
import io
import plotly.graph_objects as go

from MasterCard_UseCase.parser_TT140_MasterCard import *
from MasterCard_UseCase.processing_bank_sources import *

st.sidebar.image("assets/Logo_hps_0.png", use_column_width=True)
st.sidebar.divider()
st.sidebar.page_link("app.py", label="**Accueil**" , icon="🏠")
st.header("📤 :blue[Veuillez charger les fichiers nécessaires pour la réconciliation avec le rapport Mastercard]", divider='rainbow')

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
        st.write("**La date du rapport MasterCard est :calendar:**", run_date)
        st.write("**Vous effectuerez la réconciliation pour la date :calendar:**", day_after)
    except Exception as e:
        st.error("Erreur lors de l'extraction de la date du fichier Mastercard")

total_transactions = {'Cybersource': 0, 'POS': 0, 'Saisie manuelle': 0}

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
    st.error("Erreur lors du traitement du fichier Cybersource, vérifiez votre fichier téléchargé")

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
    st.error("Erreur lors du traitement du fichier POS, vérifiez votre fichier téléchargé - assurez-vous que la date correspond à la date du fichier Mastercard.")

try:
    if uploaded_sai_manuelle_file:
        sai_manuelle_file_path = save_uploaded_file(uploaded_sai_manuelle_file)
        validate_file_name_and_date(uploaded_sai_manuelle_file.name, 'SAIS_MANU', date_to_validate=day_after)
        df_sai_manuelle = reading_saisie_manuelle(sai_manuelle_file_path)
        mastercard_transactions_sai_manuelle = df_sai_manuelle[df_sai_manuelle['RESEAU'] == 'MASTERCARD INTERNATIONAL']
        total_transactions['Saisie manuelle'] = mastercard_transactions_sai_manuelle['NBRE_TRANSACTION'].sum()
    else:
        df_sai_manuelle = pd.DataFrame(columns=default_columns_saisie_manuelle)
except Exception as e:
    st.error("Erreur lors du traitement du fichier de saisie manuelle, vérifiez votre fichier téléchargé")

try:
    filtered_cybersource_df, filtered_saisie_manuelle_df, filtered_pos_df = filtering_sources(df_cybersource, df_sai_manuelle, df_pos)
except Exception as e:
    st.error("Erreur lors du filtrage des fichiers sources")

# Diagramme circulaire pour les transactions Mastercard
if total_transactions['Cybersource'] > 0 or total_transactions['POS'] > 0 or total_transactions['Saisie manuelle'] > 0:
    st.header("	:bar_chart: Répartition des transactions par source" , divider='grey')
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
            df_recyc = pd.read_excel(recycled_file_path)
            st.write("La date de filtrage est ", filtering_date)
            df_recycled, merged_df, total_nbre_transactions = merging_with_recycled(recycled_file_path, filtered_cybersource_df, filtered_saisie_manuelle_df, filtered_pos_df , filtering_date )
            st.write("Transactions recyclées")
            st.dataframe(df_recycled)
            st.write("### Nombre de transactions des sources avec rej. recyc.", total_nbre_transactions)
        else:
            merged_df, total_nbre_transactions = merging_sources_without_recycled(filtered_cybersource_df, filtered_saisie_manuelle_df, filtered_pos_df)
            st.write("### Nombre de transactions des sources sans rej. recyc.", total_nbre_transactions)
            st.warning("Le fichier recyclé n'a pas été téléchargé. La réconciliation sera effectuée sans les transactions recyclées.")
        col2.metric("**Nombre total de transactions dans les fichiers :**", value=total_nbre_transactions )
        col3.metric("___Différence___", value=abs(nbr_total_MC - total_nbre_transactions), help="La différence nette de transactions entre les deux côtés est")
        
        if st.button('Réconcilier', type="primary", use_container_width=True):
            if nbr_total_MC == total_nbre_transactions:
                st.header('Résultat de la réconciliation')
                df_reconciliated = handle_exact_match_csv(merged_df)
                st.success("Réconciliation effectuée avec correspondance exacte.")
                st.dataframe(df_reconciliated, use_container_width=True)
                col10 , col11 , col12 = st.columns(3 , gap = "small" , vertical_alignment="top")
                with col1:
                    excel_email_path ,file_name = download_file(recon=True, df=df_reconciliated, file_partial_name='results_recon_MC', button_label=":arrow_down: Chargez les résultats de réconciliation au format Excel", run_date=run_date)
                with col2:                  
                    st.button(":email: Insérer le tableau ci-dessous dans un E-mail" , key= 10,type="primary" ,  on_click=lambda: send_excel_contents_to_outlook(excel_email_path , file_name) )
                with col3:
                    st.button(":clipboard: Stocker le tableau ci-dessous",key= 11, type="primary")
            else:
                df_reconciliated = handle_non_match_reconciliation(mastercard_file_path, merged_df)
                df_summary = calculate_rejected_summary(mastercard_file_path)
                df_rejections = extract_rejections(mastercard_file_path, currencies_settings, countries_settings)
                st.warning("Réconciliation effectuée sans correspondance exacte.")
                st.header('Résultat de la réconciliation')
                st.dataframe(df_reconciliated.style.apply(highlight_non_reconciliated_row, axis=1), use_container_width=True)
                col1 , col2 , col3 = st.columns(3 , gap = "medium" )
                with col1:
                    excel_path_email_1 , file_name_1= download_file(recon=True, df=df_reconciliated, file_partial_name='results_recon_MC', button_label=":arrow_down: Téléchargez les résultats de réconciliation", run_date=run_date)
                with col2:                  
                    st.button(":email: Insérer le tableau ci-dessous dans un E-mail",key= 1,    type="primary")
                with col3:
                    st.button(":floppy_disk:  Stocker le tableau ci-dessous",key= 4, type="primary")
                st.header('Résumé des rejets')
                st.dataframe(df_summary)
                
                col4 , col5 , col6 = st.columns(3 , gap = "medium" )
                with col4:
                    excel_path_email_2 , file_name_2 = download_file(recon=False, df=df_summary, file_partial_name='rejected_summary_MC', button_label=":arrow_down: Téléchargez le résumé des rejets", run_date=run_date)
                with col5:
                    st.button(":email: Insérer le tableau ci-dessous dans un E-mail", key= 2, type="primary")
                with col6:
                    st.button(":floppy_disk:  Stocker le tableau ci-dessous", key= 13,type="primary")
                st.header('Transactions rejetées')
                st.dataframe(df_rejections, use_container_width=True)
                col7 , col8 , col9 = st.columns(3, gap ="medium" )
                with col7:
                    excel_path_email_3 , file_name_3= download_file(recon=False, df=df_rejections, file_partial_name='rejected_transactions_MC', button_label=":arrow_down: Téléchargez les résultats de réconciliation", run_date=run_date)
                with col8:
                    st.button(":email: Insérer le tableau ci-dessous dans un E-mail", key= 3,  type="primary")
                with col9:
                    st.button(":floppy_disk:  Stocker le tableau ci-dessous",key=12,  type="primary")
        st.warning("Veuillez charger tous les fichiers requis pour continuer.")
except Exception as e:
    st.error("Erreur lors du traitement du fichier Mastercard")
    st.write(e)
