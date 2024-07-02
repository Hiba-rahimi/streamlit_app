import streamlit as st
import plotly.graph_objects as go
from MasterCard_UseCase.database_actions import *

def pie_chart_etat_rapprochement():
    st.header("	:bar_chart:  Repartition de l'état de rapprochement", divider='grey')

    # Get the counts of each Rapprochement
    df_counts = count_rapprochement()

    if df_counts.empty:
        st.write("No data available for état de rapprochement.")
        return

    # Extract labels and sizes
    labels = df_counts['Rapprochement'].tolist()
    sizes = df_counts['Count'].tolist()

    def create_interactive_pie_chart():
        fig = go.Figure(data=[go.Pie(labels=labels, values=sizes, hole=.3, textinfo='label+percent+value')])
        return fig

    fig = create_interactive_pie_chart()
    st.plotly_chart(fig)

def create_bar_chart_by_filiale():
    """
    Create a bar chart that counts the number of Rapprochement states by Filiale.

    Returns:
    fig: A Plotly bar chart figure.
    """
    df_counts = count_rapprochement_by_filiale()

    if df_counts.empty:
        print("No data available for état de rapprochement by Filiale.")
        return None

    # Initialize the bar chart figure
    fig = go.Figure()

    # Add bars for each Filiale
    for filiale in df_counts['FILIALE'].unique():
        df_filiale = df_counts[df_counts['FILIALE'] == filiale]
        fig.add_trace(go.Bar(
            x=df_filiale['Rapprochement'],
            y=df_filiale['count'],
            name=filiale
        ))

    # Update layout for better visuals
    fig.update_layout(
        barmode='group',
        title="Repartition de l'état de rapprochement par Filiale",
        xaxis_title="Rapprochement",
        yaxis_title="Count",
        xaxis=dict(
            title='Rapprochement',
            tickmode='linear'
        ),
        yaxis=dict(
            title='Count'
        ),
        legend_title="FILIALE",
    )

    # Debugging: Check the figure content
    print(fig)

    return fig

def display_bar_chart_by_filiale():
    st.header(":bar_chart: Repartition de l'état de rapprochement par Filiale", divider='grey')

    # Create the bar chart figure
    fig_bar = create_bar_chart_by_filiale()
    if fig_bar is not None:
        st.plotly_chart(fig_bar)
    else:
        st.write("No bar chart available.")

def create_bar_chart_montants_by_filiale():
    """
    Create a bar chart that shows the sum of Montant Total de Transactions for each Filiale.

    Returns:
    fig: A Plotly bar chart figure.
    """
    df_montants = sum_montants_by_filiale()

    if df_montants.empty:
        print("No data available for Montant Total de Transactions by Filiale.")
        return None

    # Initialize the bar chart figure
    fig = go.Figure()

    # Add bars for each Filiale with different colors
    for filiale in df_montants['FILIALE'].unique():
        df_filiale = df_montants[df_montants['FILIALE'] == filiale]
        fig.add_trace(go.Bar(
            x=[filiale],  # Single bar for this Filiale
            y=df_filiale['Montant de Transactions (Couverture)'],
            text=df_filiale['Montant de Transactions (Couverture)'].apply(lambda x: f'{x:,.2f}'),  # Format numbers with commas
            textposition='auto',
            name=filiale,  # Add Filiale name to the legend
            legendgroup=filiale  # Group traces with the same FILIALE for distinct colors
        ))

    # Update layout for better visuals
    fig.update_layout(
        title="Somme des Montants Totaux de Transactions par Filiale couverts",
        xaxis_title="FILIALE",
        yaxis_title="Montant de Transactions (Couverture)",
        xaxis=dict(
            title='FILIALE',
            tickmode='linear',
            tickangle=-45,  # Rotate x-axis labels for better readability
            showticklabels=False  # Remove the x-axis labels
        ),
        yaxis=dict(
            title="Montant de Transactions (Couverture)"
        ),
        legend_title="FILIALE",
        showlegend=True,  # Ensure that the legend is shown
        barmode='group'  # Group bars to show each Filiale together
    )

    # Debugging: Check the figure content
    print(fig)

    return fig

def display_bar_chart_montants_by_filiale():
    st.header(":bar_chart: Montants Totaux de Transactions par Filiale couverts", divider='grey')

    # Create the bar chart figure
    fig_bar = create_bar_chart_montants_by_filiale()
    if fig_bar is not None:
        st.plotly_chart(fig_bar)
    else:
        st.write("No bar chart available.")

def create_bar_chart_rejected_by_filiale():
    """
    Create a bar chart that shows the number of rejected transactions for each Filiale.

    Returns:
    fig: A Plotly bar chart figure.
    """
    df_rejected_counts = count_rejected_by_filiale()

    if df_rejected_counts.empty:
        print("No data available for rejected transactions by Filiale.")
        return None

    # Initialize the bar chart figure
    fig = go.Figure()

    # Add bars for each Filiale
    for filiale in df_rejected_counts['FILIALE'].unique():
        df_filiale = df_rejected_counts[df_rejected_counts['FILIALE'] == filiale]
        fig.add_trace(go.Bar(
            x=[filiale],  # x-axis represents Filiale
            y=df_filiale['Nombre de Rejets'],  # y-axis represents the count of rejected transactions
            text=df_filiale['Nombre de Rejets'],
            textposition='auto',
            name=filiale,  # The name for this trace, which will appear in the legend
            legendgroup=filiale  # Grouping traces with the same FILIALE for distinct colors
        ))

    # Update layout for better visuals
    fig.update_layout(
        title="Nombre de Transactions Rejetées par Filiale",
        xaxis_title="FILIALE",
        yaxis_title="Nombre de Rejets",
        xaxis=dict(
            title='FILIALE',
            tickmode='linear',
            tickangle=-45
        ),
        yaxis=dict(
            title="Nombre de Rejets"
        ),
        legend_title="FILIALE",
        showlegend=True,  # Ensure that the legend is shown
        barmode='group'  # Group the bars to show each Filiale
    )

    # Debugging: Check the figure content
    print(fig)

    return fig

def display_bar_chart_rejects_by_filiale():
    st.header(":bar_chart: Rejets par filiale", divider='grey')

    # Create the bar chart figure
    fig_bar = create_bar_chart_rejected_by_filiale()
    if fig_bar is not None:
        st.plotly_chart(fig_bar)
    else:
        st.write("No bar chart available.")




def main():
    st.sidebar.image("assets/Logo_hps_0.png", use_column_width=True)
    st.sidebar.divider()
    st.sidebar.page_link("app.py", label="**Accueil**", icon="🏠")
    st.sidebar.page_link("pages/results_recon.py", label="**:alarm_clock: Historique**")
    st.sidebar.page_link("pages/Dashboard.py", label="  **📊 Tableau de bord**" )
    st.sidebar.page_link("pages/MasterCard_UI.py", label="**🔀 MasterCard Network Reconciliaiton Option**")
    st.sidebar.page_link("pages/calendar_view.py", label="**📆 Vue Agenda**")
    st.header("Tableau de bord", divider='rainbow')
    st.write("  ")
    col1, col2  = st.columns(2)
    with col1:
        pie_chart_etat_rapprochement()
    with col2:
        display_bar_chart_by_filiale()
    display_bar_chart_montants_by_filiale()
    col3, col4 = st.columns(2)
    with col3:
        display_bar_chart_rejects_by_filiale()



if __name__ == "__main__":
    main()