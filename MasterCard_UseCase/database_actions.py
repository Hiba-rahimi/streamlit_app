from pymongo import MongoClient
import toml
import pandas as pd
from datetime import datetime, timedelta

# Load MongoDB connection parameters from secrets.toml
secrets = toml.load(".streamlit/secrets.toml")
mongo_host = secrets["mongo"]["host"]
mongo_port = secrets["mongo"]["port"]
mongo_username = secrets["mongo"]["username"]
mongo_password = secrets["mongo"]["password"]
mongo_database = "Results"


# Connect to MongoDB
client = MongoClient(host=mongo_host, port=mongo_port, username=mongo_username, password=mongo_password)
db = client[mongo_database]
collection_recon_results = db['Reconciliation_results']
collection_results_summary = db['Reconciliation_summary']
collection_results_rejects = db['Reconciliation_rejects']

def insert_reconciliated_data(df_result):
    """
    Insert reconciliated DataFrame data into MongoDB.

    Parameters:
    df (pd.DataFrame): DataFrame containing the reconciliated data.
    """
    data_to_insert = df_result.to_dict("records")
    collection_recon_results.insert_many(data_to_insert)
    return 'Reconciliated data archived in database'

def insert_rejection_summary(df_summary):
    """
    Insert summary DataFrame data into MongoDB.

    Parameters:
    df (pd.DataFrame): DataFrame containing the reconciliated data.
    """
    data_to_insert = df_summary.to_dict("records")
    collection_results_summary.insert_many(data_to_insert)
    return 'Reconciliation summary archived in database'

def adjust_transaction_date(df):
    # Ensure 'Transaction Date' is in datetime format
    df['Transaction Date'] = pd.to_datetime(df['Transaction Date'])
    
    # Add new column 'Business Date' with +1 day from 'Transaction Date'
    df['Business Date'] = df['Transaction Date'] + timedelta(days=1)
    
    # Format both 'Transaction Date' and 'Business Date' to %Y-%m-%d
    df['Transaction Date'] = df['Transaction Date'].dt.strftime('%Y-%m-%d')
    df['Business Date'] = df['Business Date'].dt.strftime('%Y-%m-%d')
    
    return df

def insert_rejected_transactions(df_rejects):
    """
    Insert rejected transactions DataFrame data into MongoDB.

    Parameters:
    df_rejects (pd.DataFrame): DataFrame containing the rejected transactions data.
    """
    try:
        # Adjust 'Transaction Date' column by adding 1 day to create 'Adjusted Transaction Date'
        df_rejects = adjust_transaction_date(df_rejects)
        
        # Convert DataFrame to dictionary records for MongoDB insertion
        data_to_insert = df_rejects.to_dict("records")
        
        # Insert data into MongoDB collection
        collection_results_rejects.insert_many(data_to_insert)
        
        df_rejects.drop(columns=['Business Date'], inplace=True)
        
        # Return success message
        return 'Rejected transactions archived in database successfully'
    except Exception as e:
        # Return error message if insertion fails
        return f'Error archiving rejected transactions in database: {str(e)}'
    
def search_by_transaction_date(run_date):
    """
    Search for records in the Reconciliation_results collection by Transaction_Date.

    Parameters:
    transaction_date (str): The Transaction_Date to search for in %Y-%m-%d format.

    Returns:
    pd.DataFrame: DataFrame containing the search results.
    """
    try:
        # Query the MongoDB collection for records with the specified Transaction_Date
        results = collection_recon_results.find({'Date': run_date})
        
        # Convert the results to a DataFrame
        df_results = pd.DataFrame(list(results))
        
        return df_results
    except Exception as e:
        # Return an empty DataFrame if the search fails
        print(f'Error searching for records by Transaction_Date: {str(e)}')

def search_by_rapprochement(rapprochment):
    """
    Search for records in the Reconciliation_results collection by etat rapporchement.

    Parameters:
    rapprochement

    Returns:
    pd.DataFrame: DataFrame containing the search results.
    """
    try:
        # Query the MongoDB collection for records with the specified Transaction_Date
        results = collection_recon_results.find({'Rapprochement': rapprochment})
        
        # Convert the results to a DataFrame
        df_results = pd.DataFrame(list(results))
        
        return df_results
    except Exception as e:
        # Return an empty DataFrame if the search fails
        print(f'Error searching for records by Etat de rapprochement: {str(e)}')

