from pymongo import MongoClient
import toml
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st

# Load MongoDB connection parameters from secrets.toml
secrets = toml.load(".streamlit/secrets.toml")
mongo_url = secrets["mongo"]["url"]
mongo_database = "Results"


# Connect to MongoDB
client = MongoClient(mongo_url)
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



def insert_rejected_transactions(df_rejects, run_date):
    """
    Insert rejected transactions DataFrame data into MongoDB and add a rejection date.

    Parameters:
    df_rejects (pd.DataFrame): DataFrame containing the rejected transactions data.
    run_date (str): The date to be used as the rejection date.
    """
    try:
        # Add the rejected_date column with the values of run_date
        df_rejects['rejected_date'] = run_date

        # Convert DataFrame to dictionary records for MongoDB insertion
        data_to_insert = df_rejects.to_dict("records")

        # Insert data into MongoDB collection
        collection_results_rejects.insert_many(data_to_insert)
        #print(run_date)

        # Return success message
        return 'Rejected transactions archived in database successfully'
    except Exception as e:
        # Return error message if insertion fails
        return f'Error archiving rejected transactions in database: {str(e)}'


def search_results_by_transaction_date(run_date):
    """
    Search for records in the Reconciliation_results collection by Transaction_Date.

    Parameters:
    transaction_date (str): The Transaction_Date to search for in %Y-%m-%d format.

    Returns:
    pd.DataFrame: DataFrame containing the search results.
    """
    try:
        # Query the MongoDB collection for records with the specified Transaction_Date
        results_recon = collection_recon_results.find({'Date': run_date})

        # Convert the results to a DataFrame
        df_results_recon = pd.DataFrame(list(results_recon))

        return df_results_recon
    except Exception as e:
        # Return an empty DataFrame if the search fails
        print(f'Error searching for records by Transaction_Date: {str(e)}')


def search_rejects_by_transaction_date(run_date):
    """
    Search for records in the Reconciliation_results collection by Transaction_Date.

    Parameters:
    transaction_date (str): The Transaction_Date to search for in %Y-%m-%d format.

    Returns:
    pd.DataFrame: DataFrame containing the search results.
    """
    try:
        # Query the MongoDB collection for records with the specified Transaction_Date
        rejects_recon = collection_results_rejects.find({'rejected_date': run_date})

        # Convert the results to a DataFrame
        df_rejects_recon = pd.DataFrame(list(rejects_recon))

        return df_rejects_recon
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

def count_rapprochement():
    """
    Count the number of records in the Reconciliation_results collection grouped by etat de rapprochement.

    Returns:
    pd.DataFrame: DataFrame containing the count of records for each rapprochement value.
    """
    try:
        # Use MongoDB aggregation framework to count the number of records grouped by the normalized Rapprochement field
        pipeline = [
            {
                "$project": {
                    "Rapprochement": {"$toUpper": "$Rapprochement"}
                }
            },
            {
                "$group": {
                    "_id": "$Rapprochement",
                    "count": {"$sum": 1}
                }
            }
        ]
        results = collection_recon_results.aggregate(pipeline)

        # Convert the aggregation results to a DataFrame
        df_counts = pd.DataFrame(list(results))

        # Rename the columns for clarity
        df_counts.rename(columns={"_id": "Rapprochement", "count": "Count"}, inplace=True)

        return df_counts
    except Exception as e:
        # Print error message if the count fails
        print(f'Error counting records by Etat de rapprochement: {str(e)}')
        return pd.DataFrame()

def count_rapprochement_by_filiale():
    """
    Count the number of Rapprochement states grouped by Filiale.

    Returns:
    pd.DataFrame: DataFrame containing the count of Rapprochement states for each Filiale.
    """
    try:
        pipeline = [
            {
                "$project": {
                    "FILIALE": 1,
                    "Rapprochement": {"$toUpper": "$Rapprochement"}  # Convert to uppercase to avoid case sensitivity issues
                }
            },
            {
                "$group": {
                    "_id": {
                        "FILIALE": "$FILIALE",
                        "Rapprochement": {"$toUpper": "$Rapprochement"}
                    },
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"_id.FILIALE": 1, "_id.Rapprochement": 1}  # Sort by Filiale and then Rapprochement
            }
        ]
        results = collection_recon_results.aggregate(pipeline)
        df_counts = pd.DataFrame(list(results))

        # Flatten the DataFrame for easier plotting
        df_counts['FILIALE'] = df_counts['_id'].apply(lambda x: x['FILIALE'])
        df_counts['Rapprochement'] = df_counts['_id'].apply(lambda x: x['Rapprochement'])
        df_counts.drop(columns=['_id'], inplace=True)

        return df_counts
    except Exception as e:
        print(f'Error counting records by Rapprochement and Filiale: {str(e)}')
        return pd.DataFrame()

def sum_montants_by_filiale():
    """
    Calculate the sum of Montant Total de Transactions for each Filiale.

    Returns:
    pd.DataFrame: DataFrame containing the sum of Montant Total de Transactions for each Filiale.
    """
    try:
        pipeline = [
            {
                "$project": {
                    "FILIALE": 1,
                    "Montant de Transactions (Couverture)": {
                        "$replaceAll": {  # Remove commas from the montant string
                            "input": "$Montant de Transactions (Couverture)",
                            "find": ",",
                            "replacement": ""
                        }
                    }
                }
            },
            {
                "$project": {
                    "FILIALE": 1,
                    "Montant de Transactions (Couverture)": {
                        "$trim": {  # Remove any extra spaces from the montant string
                            "input": "$Montant de Transactions (Couverture)"
                        }
                    }
                }
            },
            {
                "$project": {
                    "FILIALE": 1,
                    "Montant de Transactions (Couverture)": {
                        "$substrCP": [  # Extract numeric part of the montant string
                            "$Montant de Transactions (Couverture)",
                            0,
                            { "$subtract": [ { "$strLenCP": "$Montant de Transactions (Couverture)" }, 3 ] }  # Remove the last three characters (e.g., ".00")
                        ]
                    }
                }
            },
            {
                "$project": {
                    "FILIALE": 1,
                    "Montant de Transactions (Couverture)": {  # Convert string to float
                        "$toDouble": "$Montant de Transactions (Couverture)"
                    }
                }
            },
            {
                "$group": {
                    "_id": "$FILIALE",
                    "total_montant": { "$sum": "$Montant de Transactions (Couverture)" }  # Sum up the montants
                }
            },
            {
                "$sort": { "total_montant": -1 }  # Sort by total montant in descending order
            }
        ]

        results = collection_recon_results.aggregate(pipeline)
        df_montants = pd.DataFrame(list(results))
        df_montants.rename(columns={'_id': 'FILIALE', 'total_montant': 'Montant de Transactions (Couverture)'}, inplace=True)

        return df_montants

    except Exception as e:
        print(f'Error calculating sum of Montant Total de Transactions by Filiale: {str(e)}')
        return pd.DataFrame()


def count_rejected_by_filiale():
    """
    Count the number of rejected transactions grouped by Filiale.

    Returns:
    pd.DataFrame: DataFrame containing the count of rejected transactions for each Filiale.
    """
    try:
        pipeline = [
            {
                "$group": {
                    "_id": "$FILIALE",
                    "Rejected Count": { "$sum": 1 }  # Count the number of rejected transactions
                }
            },
            {
                "$sort": { "Rejected Count": -1 }  # Sort by the number of rejected transactions in descending order
            }
        ]

        results = collection_results_rejects.aggregate(pipeline)
        df_rejected_counts = pd.DataFrame(list(results))
        df_rejected_counts.rename(columns={'_id': 'FILIALE', 'Rejected Count': 'Nombre de Rejets'}, inplace=True)

        return df_rejected_counts
    except Exception as e:
        print(f'Error counting rejected transactions by Filiale: {str(e)}')
        return pd.DataFrame()







