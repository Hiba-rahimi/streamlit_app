# librairies
import pandas as pd
from parser_TT140_MasterCard import *
import os
import re
import tempfile
import streamlit as st
pd.set_option('future.no_silent_downcasting', True)


# transactions de rejets recyclés à supprimer grace à une date de retraitement (format de date JJ/MM/AAAA)
Date_Retraitement = '30/05/2024'

# Define the function to read CSV files with delimiters
def read_csv_with_delimiters(file_path, default_columns=None, default_delimiter=','):
    """
    Read a CSV file with delimiters `;`, `,`, or space.
    
    Parameters:
        file_path (str): The path to the CSV file.
        default_delimiter (str): The default delimiter to use if the file is empty.
        
    Returns:
        pd.DataFrame: The DataFrame with the CSV content.
    """
    try:
        with open(file_path, 'r') as f:
            first_line = f.readline()

        # Detect delimiter
        if ';' in first_line:
            delimiter = ';'
        elif ',' in first_line:
            delimiter = ','
        elif ' ' in first_line:
            delimiter = r'\s+'  # regex for one or more spaces
        else:
            delimiter = default_delimiter
    except FileNotFoundError:
        delimiter = default_delimiter

    try:
        df = pd.read_csv(file_path, sep=delimiter, engine='python')
    except pd.errors.EmptyDataError:
        df = pd.DataFrame(columns=default_columns)
    
    return df


# Function to save uploaded file to a temporary location
def save_uploaded_file(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(uploaded_file.read())
        return temp_file.name

# standard columns for each source file
default_columns_cybersource = ['NBRE_TRANSACTION', 'MONTANT_TOTAL', 'CUR', 'FILIALE', 'RESEAU', 'TYPE_TRANSACTION']
default_columns_saisie_manuelle = ['NBRE_TRANSACTION', 'MONTANT_TOTAL', 'CUR', 'FILIALE', 'RESEAU']
default_columns_pos = ['FILIALE', 'RESEAU', 'TYPE_TRANSACTION', 'DATE_TRAI', 'CUR', 'NBRE_TRANSACTION', 'MONTANT_TOTAL']

def reading_cybersource(cybersource_file):
    if os.path.exists(cybersource_file):
        df_cybersource = read_csv_with_delimiters(cybersource_file, default_columns_cybersource)
        df_cybersource.columns = df_cybersource.columns.str.strip()
        df_cybersource['TYPE_TRANSACTION'] = 'ACHAT'
        df_cybersource = df_cybersource.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        # handle unified format of columns for merging after
        df_cybersource['RESEAU'] = df_cybersource['RESEAU'].astype(str)
        df_cybersource['FILIALE'] = df_cybersource['FILIALE'].astype(str)
        df_cybersource['CUR'] = df_cybersource['CUR'].astype(str)
        return df_cybersource
    else:
        df_cybersource = pd.DataFrame(columns=default_columns_saisie_manuelle)
        #st.write("The Saisie Manuelle file does not exist at the specified path.")

# Read Saisie Manuelle file
def reading_saisie_manuelle(saisie_manuelle_file):
    if os.path.exists(saisie_manuelle_file):
        df_sai_manuelle = read_csv_with_delimiters(saisie_manuelle_file, default_columns_saisie_manuelle)
        df_sai_manuelle.columns = df_sai_manuelle.columns.str.strip()
        df_sai_manuelle = df_sai_manuelle.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        # handle unified format of columns for merging after
        df_sai_manuelle['RESEAU'] = df_sai_manuelle['RESEAU'].astype(str)
        df_sai_manuelle['FILIALE'] = df_sai_manuelle['FILIALE'].astype(str)
        df_sai_manuelle['CUR'] = df_sai_manuelle['CUR'].astype(str)
        
        return df_sai_manuelle
    else:
        df_sai_manuelle = pd.DataFrame(columns=default_columns_saisie_manuelle)
        #print("The Saisie Manuelle file does not exist at the specified path.")

# Read POS file
def reading_pos(pos_file):
    if os.path.exists(pos_file):
        df_pos = read_csv_with_delimiters(pos_file, default_columns_pos)
        df_pos.columns = df_pos.columns.str.strip()
        df_pos = df_pos.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        df_pos.rename(columns={'BANQUE': 'FILIALE'}, inplace=True)
        # handle unified format of columns for merging after
        df_pos['RESEAU'] = df_pos['RESEAU'].astype(str)
        df_pos['FILIALE'] = df_pos['FILIALE'].astype(str)
        df_pos['CUR'] = df_pos['CUR'].astype(str)
        return df_pos
    else:
        df_pos = pd.DataFrame(columns=default_columns_pos)
        #print("The POS file does not exist at the specified path.")

def filtering_sources(df_cybersource, df_sai_manuelle, df_pos):
    # Filter each source to get MASTERCARD network transactions
    filtered_cybersource_df = df_cybersource[df_cybersource['RESEAU'] == 'MASTERCARD INTERNATIONAL']
    filtered_saisie_manuelle_df = df_sai_manuelle[df_sai_manuelle['RESEAU'] == 'MASTERCARD INTERNATIONAL']
    filtered_pos_df = df_pos[(df_pos['RESEAU'] == 'MASTERCARD INTERNATIONAL') & 
                         (~df_pos['TYPE_TRANSACTION'].str.endswith('_MDS'))]
    return filtered_cybersource_df, filtered_saisie_manuelle_df, filtered_pos_df


def validate_file_name_and_date(file_name, source, date_to_validate=None):
    """
    Validate the file name based on the source, the required pattern, 
    and optionally validate the date extracted from the file name.
    
    Parameters:
        file_name (str): The name of the uploaded file.
        source (str): The source type (CYBERSOURCE, POS, or SAIS_MANU).
        date_to_validate (str): The date to validate against the one in the file name. (Optional)
        
    Returns:
        bool: True if the file name is valid, False otherwise.
        
    Raises:
        ValueError: If the file name is invalid or if the date does not match the expected pattern.
    """
    pattern = f"^TRANSACTION_{source}_TRAITE_SG_\\d{{2}}-\\d{{2}}-\\d{{2}}_\\d{{6}}\\.CSV$"
    if not re.match(pattern, file_name):
        raise ValueError(f"Invalid file name: {file_name}. Expected pattern: TRANSACTION_{source}_TRAITE_SG_YY-MM-DD_HHMMSS.CSV")

    # Extract the date from the file name
    date_match = re.search(r"\d{2}-\d{2}-\d{2}", file_name)
    if date_match:
        extracted_date_str = date_match.group(0)
        try:
            extracted_date = datetime.strptime(extracted_date_str, '%y-%m-%d')
        except ValueError:
            raise ValueError(f"Extracted date ({extracted_date_str}) does not match the expected format 'yy-mm-dd'.")

        if date_to_validate:
            try:
                date_to_validate_dt = datetime.strptime(date_to_validate, '%d/%m/%Y')
            except ValueError:
                raise ValueError(f"Provided date ({date_to_validate}) does not match the expected format 'dd/mm/yyyy'.")
            
            # Subtract one day from the extracted date
            previous_day = extracted_date - timedelta(days=1)
            
            # Format both dates to 'dd/mm/yyyy' for comparison
            extracted_date_minus_one_str = previous_day.strftime('%d/%m/%Y')
            
            if extracted_date_minus_one_str != date_to_validate:
                raise ValueError(f"Date extracted from the file name minus one day ({extracted_date_minus_one_str}) does not match the provided date ({date_to_validate}).")
    else:
        raise ValueError("Date not found in the file name.")

    return True

# Converting the excel rejects file to a df
def excel_to_csv_to_df(excel_file_path, sheet_name=0):
    """
    Converts an Excel file to a CSV file and then reads it into a Pandas DataFrame.

    Parameters:
        excel_file_path (str): Path to the Excel file.
        sheet_name (str or int): Name or index of the sheet to convert (default is the first sheet).

    Returns:
        pd.DataFrame: DataFrame containing the data from the CSV file.
    """
    try:
        # Read the Excel file
        df = pd.read_excel(excel_file_path, sheet_name=sheet_name, header=0)
        
        # Define the CSV file path
        csv_file_path = excel_file_path.replace('.xlsx', '.csv')
        
        # Save the DataFrame to a CSV file without an index
        df.to_csv(csv_file_path, index=False)
        
        # Read the CSV file into a DataFrame
        df_csv = read_csv_with_delimiters(csv_file_path)
        return df_csv
    
    except PermissionError as p_error:
        print(f"Permission error: {p_error}. Please check your file permissions.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return None


# Merge the dataframes on relevant common columns
def merging_sources_without_recycled(filtered_cybersource_df, filtered_saisie_manuelle_df, filtered_pos_df):
# Merge POS and Saisie Manuelle dataframes
    merged_df = pd.merge(
        filtered_pos_df,
        filtered_saisie_manuelle_df,
        on=['FILIALE', 'RESEAU', 'CUR'],
        suffixes=('_pos', '_saisie'),
        how='outer'  # Use outer join to keep all rows from both dataframes
    )

    # Merge with filtered_cybersource_df
    merged_df = pd.merge(
        merged_df,
        filtered_cybersource_df,
        on=['FILIALE', 'RESEAU', 'CUR', 'TYPE_TRANSACTION'],
        suffixes=('_merged', '_cybersource'),
        how='outer'  # Use outer join to keep all rows from all dataframes
    )

    # Fill missing values with 0 and sum the 'NBRE_TRANSACTION' values
    merged_df['NBRE_TRANSACTION'] = (merged_df['NBRE_TRANSACTION_pos'].fillna(0) +
                                    merged_df['NBRE_TRANSACTION_saisie'].fillna(0) +
                                    merged_df['NBRE_TRANSACTION'].fillna(0))

    # Convert 'NBRE_TRANSACTION' to integer
    merged_df['NBRE_TRANSACTION'] = merged_df['NBRE_TRANSACTION'].astype(int)

    # Use MONTANT_TOTAL from filtered_pos_df
    merged_df['MONTANT_TOTAL'] = merged_df['MONTANT_TOTAL_pos'].fillna(0).infer_objects()


    # Use MONTANT_TOTAL from filtered_pos_df
    merged_df['MONTANT_TOTAL'] = merged_df['MONTANT_TOTAL_pos'].fillna(0)

    # Drop unnecessary columns
    merged_df.drop(['NBRE_TRANSACTION_pos', 'NBRE_TRANSACTION_saisie', 'MONTANT_TOTAL_pos', 'MONTANT_TOTAL_saisie'], axis=1, inplace=True)

    # Drop duplicate rows
    merged_df.drop_duplicates(subset=['FILIALE', 'RESEAU', 'CUR', 'TYPE_TRANSACTION', 'DATE_TRAI'], inplace=True)
    total_nbre_transactions = merged_df['NBRE_TRANSACTION'].sum()
    return merged_df , total_nbre_transactions


def merging_with_recycled(recycled_rejected_file,filtered_cybersource_df, filtered_saisie_manuelle_df, filtered_pos_df, filtering_date):
    df_merged, _ = merging_sources_without_recycled(filtered_cybersource_df, filtered_saisie_manuelle_df, filtered_pos_df)
    df_recycled = excel_to_csv_to_df(recycled_rejected_file)    
    df_recycled.columns = df_recycled.columns.str.strip()
    df_recycled = df_recycled.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    df_recycled.rename(columns={'BANQUE': 'FILIALE'}, inplace=True)
    # Filter rows where 'Date_Retraitement' is not equal to the specified date
    
    df_recycled = df_recycled[df_recycled['Date Retraitement'] == filtering_date]
    
    df_recycled.drop_duplicates(subset=['FILIALE', 'RESEAU', 'ARN', 'Autorisation', 'Date Transaction', 'Montant', 'Devise'], inplace=True)
    # Normalize 'FILIALE' values
    df_recycled['FILIALE'] = df_recycled['FILIALE'].str.replace("COTE D'IVOIRE", "COTE D IVOIRE")

    # Remove any commas and spaces from the 'Montant' column and convert it to numeric
    df_recycled['Montant'] = df_recycled['Montant'].str.replace(',', '').str.replace(' ', '').astype(float)

    # Normalize 'FILIALE' values
    df_recycled['FILIALE'] = df_recycled['FILIALE'].str.replace('SG-', 'SG - ')

    # Group by FILIALE and RESEAU and calculate the count and sum of Montant
    summary = df_recycled.groupby(['FILIALE', 'RESEAU']).agg(
        NBRE_TRANSACTION=('Montant', 'count'),
        MONTANT_TOTAL=('Montant', 'sum')
    ).reset_index()

    # Merge the summary DataFrame into the corresponding 'FILIALE' values of the 'df_merged' DataFrame
    merged_df = df_merged.merge(summary, on=['FILIALE', 'RESEAU'], how='left', suffixes=('_merged', '_summary'))

    # Fill NaN values with 0
    merged_df.fillna(0, inplace=True)

    # Sum the values of 'NBRE_TRANSACTION_merged' and 'NBRE_TRANSACTION_summary' columns and assign it to 'NBRE_TRANSACTION'
    merged_df['NBRE_TRANSACTION'] = merged_df['NBRE_TRANSACTION_merged'] + merged_df['NBRE_TRANSACTION_summary']

    # Drop unnecessary columns
    merged_df.drop(['NBRE_TRANSACTION_merged', 'NBRE_TRANSACTION_summary'], axis=1, inplace=True)

    # Sum the values of 'MONTANT_TOTAL_merged' and 'MONTANT_TOTAL_summary' columns and assign it to 'MONTANT_TOTAL'
    merged_df['MONTANT_TOTAL'] = merged_df['MONTANT_TOTAL_merged'] + merged_df['MONTANT_TOTAL_summary']

    # Drop unnecessary columns
    merged_df.drop(['MONTANT_TOTAL_merged', 'MONTANT_TOTAL_summary'], axis=1, inplace=True)

    # Convert 'NBRE_TRANSACTION' to integers
    merged_df['NBRE_TRANSACTION'] = merged_df['NBRE_TRANSACTION'].astype(int)

    total_nbre_transactions = merged_df['NBRE_TRANSACTION'].sum()
    #print(total_nbre_transactions)


    return df_recycled, merged_df, total_nbre_transactions


def populating_table_reconcialited(merged_df):
    # Columns to be included in the reconciliated DataFrame
    new_columns = [
        'FILIALE', 'Réseau', 'Type', 'Date', 'Devise', 'NbreTotaleDeTransactions',
        'Montant Total de Transactions', 'Rapprochement', 'Nbre Total de Rejets',
        'Montant de Rejets', 'Nbre de Transactions (Couverture)', 
        'Montant de Transactions (Couverture)'
    ]

    # Mapping between the old and new column names
    column_mapping = {
        'FILIALE': 'FILIALE',
        'RESEAU': 'Réseau',
        'TYPE_TRANSACTION': 'Type',
        'DATE_TRAI': 'Date',
        'CUR': 'Devise',
        'NBRE_TRANSACTION': 'NbreTotaleDeTransactions',
        'MONTANT_TOTAL': 'Montant Total de Transactions'
    }

    # Rename columns
    merged_df.rename(columns=column_mapping, inplace=True)

    # Add the missing columns with default values
    for column in set(new_columns) - set(merged_df.columns):
        merged_df[column] = ''

    # Reorder the columns
    merged_df = merged_df[new_columns]
    return merged_df

def handle_exact_match_csv(merged_df):
    populating_table_reconcialited(merged_df)
    df_reconciliated = merged_df.copy()
    df_reconciliated['Rapprochement'] = 'ok'
    df_reconciliated['Montant de Transactions (Couverture)'] = df_reconciliated['Montant Total de Transactions']
    df_reconciliated['Nbre de Transactions (Couverture)'] = df_reconciliated['NbreTotaleDeTransactions']
    #df_reconciliated.to_csv('reconciliated.csv', index=False)
    return df_reconciliated

def handle_non_match_reconciliation(file_path,merged_df):
    populating_table_reconcialited(merged_df)
    df_reconciliated = merged_df.copy()
    # Load the rejected summary data
    df_rejected_summary = calculate_rejected_summary(file_path)

    # Ensure the relevant columns exist in the reconciliated DataFrame
    if 'FILIALE' not in df_reconciliated.columns:
        raise KeyError('The required columns are missing in the reconciliated DataFrame.')

    # Add the columns if they do not exist
    if 'Rapprochement' not in df_reconciliated.columns:
        df_reconciliated['Rapprochement'] = 'ok'

    # Create a set of FILIALEs with issues from the rejected summary
    filiales_with_issues = set(df_rejected_summary['FILIALE'])

    # Update the reconciliated DataFrame
    df_reconciliated['Rapprochement'] = df_reconciliated['FILIALE'].apply(
        lambda x: 'not ok' if x in filiales_with_issues else 'ok'
    )

    # Update Nbre Total de Rejets and Montant de Rejets based on the rejected summary data
    for index, row in df_rejected_summary.iterrows():
        filiale = row['FILIALE']
        nbr_rejets = row['Nbre Total de Rejets']
        montant_rejets = row['Montant de Rejets']

        # Find the matching row in the reconciliated DataFrame
        match_idx = df_reconciliated[df_reconciliated['FILIALE'] == filiale].index

        if not match_idx.empty:
            # Update the matching row
            df_reconciliated.loc[match_idx, 'Nbre Total de Rejets'] = nbr_rejets
            df_reconciliated.loc[match_idx, 'Montant de Rejets'] = montant_rejets
            df_reconciliated['Montant de Transactions (Couverture)'] = df_reconciliated['Montant Total de Transactions']
            df_reconciliated['Nbre de Transactions (Couverture)'] = df_reconciliated['NbreTotaleDeTransactions']

    # Fill NaN values in 'Nbre Total de Rejets' with 0 before converting to integer type
    df_reconciliated['Nbre Total de Rejets'] = df_reconciliated['Nbre Total de Rejets'].replace('', 0).fillna(0).astype(int)
    # Save the updated DataFrame to a CSV file
    #df_reconciliated.to_csv('reconciliated.csv', index=False)
    return df_reconciliated


