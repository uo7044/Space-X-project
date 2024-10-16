# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
# Read the SpaceX launch data into a pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
launch_sites = spacex_df['Launch Site'].unique().tolist()
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create dropdown options for launch sites
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}] + \
                   [{'label': site, 'value': site} for site in launch_sites]

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # Dropdown for selecting Launch Site
    dcc.Dropdown(id='site-dropdown',
                 options=dropdown_options,
                 value='ALL',
                 placeholder="Select a Launch Site here",
                 searchable=True),
    html.Br(),

    # Pie chart for success rate
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    # Payload range slider
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(id='payload-slider',
                    min=0,
                    max=10000,
                    step=1000,
                    marks={i: f'{i}' for i in range(0, 10001, 2500)},
                    value=[min_payload, max_payload]),
    html.Br(),

    # Scatter plot for payload vs. success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback function for updating the pie chart based on selected site
@app.callback(Output('success-pie-chart', 'figure'),
              Input('site-dropdown', 'value'))
def update_pie_chart(entered_site):
    filtered_df = spacex_df if entered_site == 'ALL' else spacex_df[spacex_df['Launch Site'] == entered_site]
    success_counts = filtered_df['class'].value_counts().to_dict()
    fig = px.pie(names=['Success', 'Failure'], values=[success_counts.get(1, 0), success_counts.get(0, 0)],
                 title=f'Total Success Launches for {entered_site}' if entered_site != 'ALL' else 'Total Success Launches for All Sites')
    return fig

# Callback function for updating the scatter plot based on selected site and payload range
@app.callback(Output('success-payload-scatter-chart', 'figure'),
              [Input('site-dropdown', 'value'), Input('payload-slider', 'value')])
def update_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)]
    if entered_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category',
                     title=f'Payload vs. Outcome for {entered_site} (Payload {low}-{high} Kg)' if entered_site != 'ALL' else f'Payload vs. Outcome for All Sites (Payload {low}-{high} Kg)',
                     labels={'class': 'Outcome', 'Payload Mass (kg)': 'Payload Mass (Kg)'})
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()