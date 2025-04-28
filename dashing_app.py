import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "Rainfall Forecast Dashboard"

# Load the forecast data
forecast_df = pd.read_csv('rainfall_forecast_output.csv')
forecast_df['Date'] = pd.to_datetime(forecast_df['Date'])

# Define the layout
app.layout = html.Div([
    html.H1("Rainfall Forecast Dashboard", style={
    'fontFamily': 'Arial',
    'backgroundImage': 'url("https://images.unsplash.com/photo-1501594907352-04cda38ebc29")',
    'backgroundSize': 'cover',
    'backgroundPosition': 'center',
    'backgroundRepeat': 'no-repeat',
    'backgroundAttachment': 'fixed',  # Optional: for parallax scrolling effect
    'color': 'white',
    'minHeight': '100vh',
    'width': '100%',
    'height': '100%',
    'padding': '20px'  # Add some padding if needed
}),

    html.Div([
        html.Label("Select Date Range for Forecast:", style={'fontWeight': 'bold'}),
        dcc.DatePickerRange(
            id='date-picker-range',
            min_date_allowed=forecast_df['Date'].min(),
            max_date_allowed=forecast_df['Date'].max(),
            initial_visible_month=forecast_df['Date'].min(),
            start_date=forecast_df['Date'].min(),
            end_date=forecast_df['Date'].max(),
            display_format='YYYY-MM-DD',
            style={'margin': '10px 0'}
        ),
    ], style={'padding': '20px', 'backgroundColor': '#ECF0F1', 'borderRadius': '5px', 'margin': '20px'}),

    html.Div([
        dcc.Graph(id='forecast-line-plot'),
        dcc.Graph(id='rain-category-bar'),
    ], style={'padding': '20px'}),

    html.Div([
        html.H3("Forecast Data Table", style={'textAlign': 'center'}),
        dcc.Graph(id='forecast-table')
    ], style={'padding': '20px'}),
], style={'fontFamily': 'Arial', 'maxWidth': '1200px', 'margin': 'auto'})


# Callback to update the line plot
@app.callback(
    Output('forecast-line-plot', 'figure'),
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_line_plot(start_date, end_date):
    filtered_df = forecast_df[
        (forecast_df['Date'] >= start_date) & (forecast_df['Date'] <= end_date)
    ]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=filtered_df['Date'], 
        y=filtered_df['ARIMA_Forecast_mm'], 
        name='ARIMA Forecast', 
        line=dict(color='red')
    ))
    fig.add_trace(go.Scatter(
        x=filtered_df['Date'], 
        y=filtered_df['LSTM_Forecast_mm'], 
        name='LSTM Forecast', 
        line=dict(color='green')
    ))
    
    fig.update_layout(
        title='Rainfall Forecast (ARIMA vs LSTM)',
        xaxis_title='Date',
        yaxis_title='Rainfall (mm)',
        template='plotly_white',
        hovermode='x unified'
    )
    return fig


# Callback to update the rain category bar plot
@app.callback(
    Output('rain-category-bar', 'figure'),
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_bar_plot(start_date, end_date):
    filtered_df = forecast_df[
        (forecast_df['Date'] >= start_date) & (forecast_df['Date'] <= end_date)
    ]
    
    category_counts = filtered_df['Rain_Category'].value_counts().reset_index()
    category_counts.columns = ['Rain_Category', 'Count']
    
    fig = px.bar(
        category_counts,
        x='Rain_Category',
        y='Count',
        color='Rain_Category',
        color_discrete_map={
            'No Rain': '#3498DB',
            'Drizzle': '#1ABC9C',
            'Moderate': '#F1C40F',
            'Heavy': '#E74C3C'
        },
        title='Rain Category Distribution'
    )
    fig.update_layout(
        xaxis_title='Rain Category',
        yaxis_title='Number of Days',
        template='plotly_white'
    )
    return fig


# Callback to update the data table
@app.callback(
    Output('forecast-table', 'figure'),
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_table(start_date, end_date):
    filtered_df = forecast_df[
        (forecast_df['Date'] >= start_date) & (forecast_df['Date'] <= end_date)
    ][['Date', 'ARIMA_Forecast_mm', 'LSTM_Forecast_mm', 'Rain_Category']]
    
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['Date', 'ARIMA Forecast (mm)', 'LSTM Forecast (mm)', 'Rain Category'],
            fill_color='#2C3E50',
            font=dict(color='white', size=12),
            align='left'
        ),
        cells=dict(
            values=[
                filtered_df['Date'].dt.strftime('%Y-%m-%d'),
                filtered_df['ARIMA_Forecast_mm'].round(2),
                filtered_df['LSTM_Forecast_mm'].round(2),
                filtered_df['Rain_Category']
            ],
            fill_color='#ECF0F1',
            align='left'
        )
    )])
    fig.update_layout(margin=dict(t=20, l=0, r=0, b=0))
    return fig


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
