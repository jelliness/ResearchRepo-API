# created by Jelly Mallari
# continued by Nicole Cabansag (for other charts and added reset_button function)

import dash
from dash import Dash, html, dcc, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from . import view_manager
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def default_if_empty(selected_values, default_values):
    """
    Returns default_values if selected_values is empty.
    """
    return selected_values if selected_values else default_values

class Engage_Dash:
    def __init__(self, flask_app):
        """
        Initialize the MainDashboard class and set up the Dash app.
        """
        self.dash_app = Dash(__name__, server=flask_app, url_base_pathname='/engage/', 
                             external_stylesheets=[dbc.themes.BOOTSTRAP])

        self.palette_dict = view_manager.get_college_colors()
        
        # Get default values
        self.default_colleges = view_manager.get_unique_values('college_id')
        self.default_statuses = view_manager.get_unique_values('status')
        self.default_years = [view_manager.get_min_value('year'), view_manager.get_max_value('year')]
        self.create_layout()
        self.set_callbacks()

        self.all_sdgs = [
            'SDG 1', 'SDG 2', 'SDG 3', 'SDG 4', 'SDG 5', 'SDG 6', 'SDG 7', 
            'SDG 8', 'SDG 9', 'SDG 10', 'SDG 11', 'SDG 12', 'SDG 13', 
            'SDG 14', 'SDG 15', 'SDG 16', 'SDG 17'
        ]

    def create_layout(self):
        """
        Create the layout of the dashboard.
        """

        college = html.Div(
            [
                dbc.Label("Select College:", style={"color": "#08397C"}),
                dbc.Checklist(
                    id="college",
                    options=[{'label': value, 'value': value} for value in view_manager.get_unique_values('college_id')],
                    value=[],
                    inline=True,
                ),
            ],
            className="mb-4",
        )

        status = html.Div(
            [
                dbc.Label("Select Status:", style={"color": "#08397C"}),
                dbc.Checklist(
                    id="status",
                    options=[{'label': value, 'value': value} for value in sorted(
                        view_manager.get_unique_values('status'), key=lambda x: (x != 'READY', x != 'PULLOUT', x)
                    )],
                    value=[],
                    inline=True,
                ),
            ],
            className="mb-4",
        )

        slider = html.Div(
            [
                dbc.Label("Select Years: ", style={"color": "#08397C"}),
                dcc.RangeSlider(
                    min=view_manager.get_min_value('year'), 
                    max=view_manager.get_max_value('year'), 
                    step=1, 
                    id="years",
                    marks=None,
                    tooltip={"placement": "bottom", "always_visible": True},
                    value=[view_manager.get_min_value('year'), view_manager.get_max_value('year')],
                    className="p-0",
                ),
            ],
            className="mb-4",
        )

        button = html.Div(
            [
                dbc.Button("Reset", color="primary", id="reset_button"),
            ],
            className="d-grid gap-2",
        )

        controls = dbc.Col(
            dbc.Card(
                [
                    html.H4("Filters", style={"margin": "10px 0px", "color": "red"}),  # Set the color to red
                    college,
                    status,
                    slider,
                    button,
                ],
                body=True,
                style={
                    "background": "#d3d8db",
                    "height": "100vh",  # Full-height sidebar
                    "position": "sticky",  # Sticky position instead of fixed
                    "top": 0,
                    "padding": "20px",
                    "border-radius": "0",  # Remove rounded corners
                },
            )
        )

        text_display = dbc.Container([
            dbc.Row([
                dbc.Container([
                    dbc.Row([
                        dbc.Col(
                        self.create_display_card("Total Research Papers", str(len(view_manager.get_all_data()))),
                        style={"display": "flex", "justify-content": "center", "align-items": "center", "padding": "0", "margin": "0"}
                    ),
                    dbc.Col(
                        self.create_display_card("Intended for Publication", str(len(view_manager.filter_data('status', 'READY', invert=False)))),
                        style={"display": "flex", "justify-content": "center", "align-items": "center", "padding": "0", "margin": "0"}
                    ),
                    dbc.Col(
                        self.create_display_card("Submitted Papers", str(len(view_manager.filter_data('status', 'SUBMITTED', invert=False)))),
                        style={"display": "flex", "justify-content": "center", "align-items": "center", "padding": "0", "margin": "0"}
                    ),
                    dbc.Col(
                        self.create_display_card("Accepted Papers", str(len(view_manager.filter_data('status', 'ACCEPTED', invert=False)))),
                        style={"display": "flex", "justify-content": "center", "align-items": "center", "padding": "0", "margin": "0"}
                    ),
                    dbc.Col(
                        self.create_display_card("Published Papers", str(len(view_manager.filter_data('status', 'PUBLISHED', invert=False)))),
                        style={"display": "flex", "justify-content": "center", "align-items": "center", "padding": "0", "margin": "0"}
                    ),
                    dbc.Col(
                        self.create_display_card("Pulled-out Papers", str(len(view_manager.filter_data('status', 'PULLOUT', invert=False)))),
                        style={"display": "flex", "justify-content": "center", "align-items": "center", "padding": "0", "margin": "0"}
                    )
                    ])
                ])
            ], style={"margin": "0", "display": "flex", "justify-content": "space-around", "align-items": "center"})
        ], style={"padding": "2rem"}, id="text-display-container")

        main_dash = dbc.Container([
                dbc.Row([  # Row for the line and pie charts
                    dbc.Col(dcc.Graph(id='college_line_plot'), width=8, style={"height": "auto", "overflow": "hidden", "paddingTop": "20px"}),
                    dbc.Col(dcc.Graph(id='college_pie_chart'), width=4, style={"height": "auto", "overflow": "hidden", "paddingTop": "20px"})
                ], style={"margin": "10px"})
            ], fluid=True, style={"border": "2px solid #FFFFFF", "borderRadius": "5px","transform": "scale(1)", "transform-origin": "0 0"})  # Adjust the scale as needed

        sub_dash1 = dbc.Container([
                dbc.Row([
                    dbc.Col(dcc.Graph(id='research_status_bar_plot'), width=6, style={"height": "auto", "overflow": "hidden"}),
                    dbc.Col(dcc.Graph(id='research_type_bar_plot'), width=6, style={"height": "auto", "overflow": "hidden"})
                ], style={"margin": "10px"})
            ], fluid=True, style={"border": "2px solid #FFFFFF", "borderRadius": "5px","transform": "scale(1)", "transform-origin": "0 0"})  # Adjust the scale as needed

        sub_dash2 = dbc.Container([ 
                dbc.Row([
                    dbc.Col(dcc.Graph(id='proceeding_conference_line_graph'), width=6, style={"height": "auto", "overflow": "hidden"}),
                    dbc.Col(dcc.Graph(id='proceeding_conference_bar_plot'), width=6, style={"height": "auto", "overflow": "hidden"})
                ], style={"margin": "10px"})
            ], fluid=True, style={"border": "2px solid #FFFFFF", "borderRadius": "5px","transform": "scale(1)", "transform-origin": "0 0"})  # Adjust the scale as needed

        sub_dash3 = dbc.Container([
            dbc.Row([
                dbc.Col(dcc.Graph(id='sdg_bar_plot'), width=12)  # Increase width to 12 to occupy the full space
            ], style={"margin": "10px"})
        ], fluid=True, style={"border": "2px solid #FFFFFF", "borderRadius": "5px", "transform": "scale(1)", "transform-origin": "0 0"})

        sub_dash4 = dbc.Container([
                dbc.Row([
                    dbc.Col(dcc.Graph(id='nonscopus_scopus_line_graph'), width=6, style={"height": "auto", "overflow": "hidden"}),
                    dbc.Col(dcc.Graph(id='nonscopus_scopus_bar_plot'), width=6, style={"height": "auto", "overflow": "hidden"})
                ], style={"margin": "10px"})
            ], fluid=True, style={"border": "2px solid #FFFFFF", "borderRadius": "5px","transform": "scale(1)", "transform-origin": "0 0"})  # Adjust the scale as needed
        
        sub_dash5 = dbc.Container([
            dbc.Row([
                dbc.Col(dcc.Graph(id='term_college_bar_plot'), width=12)  # Increase width to 12 to occupy the full space
            ], style={"margin": "10px"})
        ], fluid=True, style={"border": "2px solid #FFFFFF", "borderRadius": "5px", "transform": "scale(1)", "transform-origin": "0 0"})


        self.dash_app.layout = html.Div([
            dcc.Interval(id="data-refresh-interval", interval=1000, n_intervals=0),  # 1 second
            dcc.Store(id="shared-data-store"),  # Shared data store to hold the updated dataset
            dbc.Container([
                dbc.Row([
                    dbc.Col(controls, width=2, style={"height": "100%"}),  # Controls on the side
                    dbc.Col(
                        html.Div([  # Wrapper div for horizontal scrolling
                            dcc.Dropdown(
                                id='date-range-dropdown',
                                options=[
                                    {'label': 'Last 7 Days', 'value': '7D'},
                                    {'label': 'Last 2 Weeks', 'value': '14D'},
                                    {'label': 'Last Month', 'value': '1M'},
                                    {'label': 'Last 6 Months', 'value': '6M'}
                                ],
                                value='7D',
                                placeholder='Select a date range'
                            ),
                            dbc.Row(text_display, style={"flex": "1"}),  # Display `text_display` at the top
                            dbc.Row(
                                dcc.Loading(
                                    id="loading-main-dash",
                                    type="circle",
                                    children=main_dash
                                ), style={"flex": "2"}
                            ),
                            dbc.Row(
                                dcc.Loading(
                                    id="loading-sub-dash5",
                                    type="circle",
                                    children=sub_dash5
                                ), style={"flex": "1"}
                            ),  
                            dbc.Row(
                                dcc.Loading(
                                    id="loading-sub-dash1",
                                    type="circle",
                                    children=sub_dash1
                                ), style={"flex": "1"}
                            ),    
                            dbc.Row(
                                dcc.Loading(
                                    id="loading-sub-dash3",
                                    type="circle",
                                    children=sub_dash3
                                ), style={"flex": "1"}
                            ),    
                            dbc.Row(
                                dcc.Loading(
                                    id="loading-sub-dash2",
                                    type="circle",
                                    children=sub_dash2
                                ), style={"flex": "1"}
                            ),    
                            dbc.Row(
                                dcc.Loading(
                                    id="loading-sub-dash4",
                                    type="circle",
                                    children=sub_dash4
                                ), style={"flex": "1"}
                            ),    
                        ], style={
                            "height": "90%",  # Reduced content area height
                            "display": "flex",
                            "flex-direction": "column",
                            "overflow-x": "auto",  # Allow horizontal scrolling for the entire content
                            "flex-grow": "1",  # Ensure content area grows to fill available space
                            "margin": "0",
                            "padding": "3px",
                        })
                    , style={
                        "height": "100%",  # Ensure wrapper takes full height
                        "display": "flex",
                        "flex-direction": "column"
                    }),
                ], style={"height": "100%", "display": "flex"}),
            ], fluid=True, className="dbc dbc-ag-grid", style={
                "height": "80vh",  # Reduced viewport height
                "margin": "0", 
                "padding": "0",
            })
        ], style={
            "height": "90vh",  # Reduced overall height
            "margin": "0",
            "padding": "0",
            "overflow-x": "hidden",  # No scrolling for outermost div
            "overflow-y": "hidden",  # No vertical scrolling for outermost div
        })


    def create_display_card(self, title, value):
        """
        Create a display card for showing metrics.
        """
        return html.Div([
            html.Div([
                html.H5(title, style={'textAlign': 'center', 'font-size': '14px' if len(title) > 20 else '16px'}),
                html.H2(value, style={'textAlign': 'center'})
            ], style={
                "border": "2px solid #0A438F",    # Border color
                "borderRadius": "10px",           # Rounded corners
                "padding": "10px",                # Padding inside the card
                "width": "170px",                 # Fixed width
                "height": "150px",                # Fixed height
                "display": "flex",
                "flexDirection": "column",
                "justifyContent": "center",
                "alignItems": "center",
                "margin": "0"
            })
        ])
    
    def get_program_colors(self, df):
        unique_programs = df['program_id'].unique()
        random_colors = px.colors.qualitative.Plotly[:len(unique_programs)]
        self.program_colors = {program: random_colors[i % len(random_colors)] for i, program in enumerate(unique_programs)}
    
    def update_line_plot(self, selected_colleges, selected_status, selected_years):
        df = view_manager.get_filtered_data(selected_colleges, selected_status, selected_years)
        
                # Convert 'date' column to datetime
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(by='date')


        # Transform data for Plotly
        df_melted = df.melt(id_vars=['date'], 
                            value_vars=['total_views', 'total_unique_views', 'total_downloads'], 
                            var_name='Metric', 
                            value_name='Count')

        # Create the line chart using Plotly
        fig = px.line(df_melted, 
                    x='date', 
                    y='Count', 
                    color='Metric', 
                    title='Views and Downloads Over Time',
                    labels={'date': 'Date', 'Count': 'Count', 'Metric': 'Metric'},
                    markers=True)

        # Show the chart
        return fig
    
    def update_pie_chart(self, selected_colleges, selected_status, selected_years):
        df = view_manager.get_filtered_data(selected_colleges, selected_status, selected_years)
        
        if len(selected_colleges) == 1:
            college_name = selected_colleges[0]
            filtered_df = df[df['college_id'] == college_name]
            detail_counts = filtered_df.groupby('program_id').size()
            self.get_program_colors(filtered_df) 
        else:
            detail_counts = df.groupby('college_id').size()
        
        fig_pie = px.pie(
            names=detail_counts.index,
            values=detail_counts,
            color=detail_counts.index,
            color_discrete_map=self.palette_dict if len(selected_colleges) > 1 else self.program_colors,
            labels={'names': 'Category', 'values': 'Number of Research Outputs'},
        )

        fig_pie.update_layout(
            template='plotly_white',
            margin=dict(l=0, r=0, t=30, b=0),
            height=400
        )

        return fig_pie
    
    def update_research_type_bar_plot(self, selected_colleges, selected_status, selected_years):
        df = view_manager.get_filtered_data(selected_colleges, selected_status, selected_years)
        if df.empty:
            return px.bar(title="No data available")
        
        fig = go.Figure()

        if len(selected_colleges) == 1:
            self.get_program_colors(df) 
            status_count = df.groupby(['research_type', 'program_id']).size().reset_index(name='Count')
            pivot_df = status_count.pivot(index='research_type', columns='program_id', values='Count').fillna(0)

            sorted_programs = sorted(pivot_df.columns)
            title = f"Comparison of Research Output Type Across Programs"

            for program in sorted_programs:
                fig.add_trace(go.Bar(
                    x=pivot_df.index,
                    y=pivot_df[program],
                    name=program,
                    marker_color=self.program_colors[program]
                ))
        else:
            status_count = df.groupby(['research_type', 'college_id']).size().reset_index(name='Count')
            pivot_df = status_count.pivot(index='research_type', columns='college_id', values='Count').fillna(0)
            title = 'Comparison of Research Output Type Across Colleges'
            
            for college in pivot_df.columns:
                fig.add_trace(go.Bar(
                    x=pivot_df.index,
                    y=pivot_df[college],
                    name=college,
                    marker_color=self.palette_dict.get(college, 'grey')
                ))

        fig.update_layout(
            barmode='group',
            xaxis_title='Research Type',  
            yaxis_title='Number of Research Outputs',  
            title=title
        )

        return fig

    def update_research_status_bar_plot(self, selected_colleges, selected_status, selected_years):
        df = view_manager.get_filtered_data(selected_colleges, selected_status, selected_years)

        if df.empty:
            return px.bar(title="No data available")

        status_order = ['READY', 'SUBMITTED', 'ACCEPTED', 'PUBLISHED', 'PULLOUT']

        fig = go.Figure()

        if len(selected_colleges) == 1:
            self.get_program_colors(df) 
            status_count = df.groupby(['status', 'program_id']).size().reset_index(name='Count')
            pivot_df = status_count.pivot(index='status', columns='program_id', values='Count').fillna(0)

            sorted_programs = sorted(pivot_df.columns)
            title = f"Comparison of Research Status Across Programs"

            for program in sorted_programs:
                fig.add_trace(go.Bar(
                    x=pivot_df.index,
                    y=pivot_df[program],
                    name=program,
                    marker_color=self.program_colors[program]
                ))
        else:
            status_count = df.groupby(['status', 'college_id']).size().reset_index(name='Count')
            pivot_df = status_count.pivot(index='status', columns='college_id', values='Count').fillna(0)
            title = 'Comparison of Research Output Status Across Colleges'
            
            for college in pivot_df.columns:
                fig.add_trace(go.Bar(
                    x=pivot_df.index,
                    y=pivot_df[college],
                    name=college,
                    marker_color=self.palette_dict.get(college, 'grey')
                ))

        fig.update_layout(
            barmode='group',
            xaxis_title='Research Status',  
            yaxis_title='Number of Research Outputs',  
            title=title,
            xaxis=dict(
                tickvals=status_order,  # This should match the unique statuses in pivot_df index
                ticktext=status_order    # This ensures that the order of the statuses is displayed correctly
            )
        )

        # Ensure the x-axis is sorted in the defined order
        fig.update_xaxes(categoryorder='array', categoryarray=status_order)

        return fig
    
    def create_publication_bar_chart(self, selected_colleges, selected_status, selected_years):  # Modified by Nicole Cabansag
        df = view_manager.get_filtered_data(selected_colleges, selected_status, selected_years)
        
        df = df[df['scopus'] != 'N/A']

        if len(selected_colleges) == 1:
            grouped_df = df.groupby(['scopus', 'program_id']).size().reset_index(name='Count')
            x_axis = 'program_id'
            xaxis_title = 'Programs'
            title = f'Scopus vs. Non-Scopus per Program in {selected_colleges[0]}'
        else:
            grouped_df = df.groupby(['scopus', 'college_id']).size().reset_index(name='Count')
            x_axis = 'college_id'
            xaxis_title = 'Colleges'
            title = 'Scopus vs. Non-Scopus per College'
        
        fig_bar = px.bar(
            grouped_df,
            x=x_axis,
            y='Count',
            color='scopus',
            barmode='group',
            color_discrete_map=self.palette_dict,
            labels={'scopus': 'Scopus vs. Non-Scopus'}
        )
        
        fig_bar.update_layout(
            title=title,
            xaxis_title=xaxis_title,
            yaxis_title='Number of Research Outputs',
            template='plotly_white',
            height=400
        )

        return fig_bar
    
    def update_publication_format_bar_plot(self, selected_colleges, selected_status, selected_years):
        df = view_manager.get_filtered_data(selected_colleges, selected_status, selected_years)
        
        df = df[df['journal'] != 'unpublished']
        df = df[df['status'] != 'PULLOUT']

        if len(selected_colleges) == 1:
            grouped_df = df.groupby(['journal', 'program_id']).size().reset_index(name='Count')
            x_axis = 'program_id'
            xaxis_title = 'Programs'
            title = f'Publication Formats per Program in {selected_colleges[0]}'
        else:
            grouped_df = df.groupby(['journal', 'college_id']).size().reset_index(name='Count')
            x_axis = 'college_id'
            xaxis_title = 'Colleges'
            title = 'Publication Formats per College'

        fig_bar = px.bar(
            grouped_df,
            x=x_axis,
            y='Count',
            color='journal',
            barmode='group',
            color_discrete_map=self.palette_dict,
            labels={'journal': 'Publication Format'}
        )
        
        fig_bar.update_layout(
            title=title,
            xaxis_title=xaxis_title,
            yaxis_title='Number of Research Outputs',
            template='plotly_white',
            height=400
        )

        return fig_bar


    def update_sdg_chart(self, selected_colleges, selected_status, selected_years):
        df = view_manager.get_filtered_data(selected_colleges, selected_status, selected_years)
        
        if df.empty:
            return px.bar(title="No data available")

        df_copy = df.copy()

        if len(selected_colleges) == 1:
            self.get_program_colors(df)
            df_copy = df_copy.set_index('program_id')['sdg'].str.split(';').apply(pd.Series).stack().reset_index(name='sdg')
            df_copy['sdg'] = df_copy['sdg'].str.strip()
            df_copy = df_copy.drop(columns=['level_1'])
            sdg_count = df_copy.groupby(['sdg', 'program_id']).size().reset_index(name='Count')
            pivot_df = sdg_count.pivot(index='sdg', columns='program_id', values='Count').reindex(self.all_sdgs).fillna(0)
            pivot_df['Total'] = pivot_df.sum(axis=1)
            pivot_df = pivot_df.sort_values(by='Total', ascending=False).drop(columns='Total')
            pivot_df = pivot_df.reindex(self.all_sdgs)

            sorted_programs = sorted(pivot_df.columns)  # Sort programs alphabetically
            pivot_df = pivot_df[sorted_programs]  # Reorder the columns in pivot_df by the sorted program list
            title = f'Programs in {selected_colleges[0]} Targeting Each SDG'

            if pivot_df.empty:
                print("Pivot DataFrame is empty after processing")
                return px.bar(title="No data available")

            fig = go.Figure()

            for program in sorted_programs:
                fig.add_trace(go.Bar(
                    y=pivot_df.index,
                    x=pivot_df[program],
                    name=program,
                    orientation='h',
                    marker_color=self.program_colors[program]
                ))
        else:
            df_copy = df_copy.set_index('college_id')['sdg'].str.split(';').apply(pd.Series).stack().reset_index(name='sdg')
            df_copy['sdg'] = df_copy['sdg'].str.strip()
            df_copy = df_copy.drop(columns=['level_1'])
            sdg_count = df_copy.groupby(['sdg', 'college_id']).size().reset_index(name='Count')
            pivot_df = sdg_count.pivot(index='sdg', columns='college_id', values='Count').reindex(self.all_sdgs).fillna(0)
            pivot_df['Total'] = pivot_df.sum(axis=1)
            pivot_df = pivot_df.sort_values(by='Total', ascending=False).drop(columns='Total')
            pivot_df = pivot_df.reindex(self.all_sdgs)

            title = 'Colleges Targeting Each SDG'

            if pivot_df.empty:
                print("Pivot DataFrame is empty after processing")
                return px.bar(title="No data available")

            fig = go.Figure()

            for college in pivot_df.columns:
                fig.add_trace(go.Bar(
                    y=pivot_df.index,
                    x=pivot_df[college],
                    name=college,
                    orientation='h',
                    marker_color=self.palette_dict.get(college, 'grey')
                ))

        fig.update_layout(
            barmode='stack',
            xaxis_title='Number of Research Outputs',
            yaxis_title='SDG Targeted',
            title=title,
            yaxis=dict(
                autorange='reversed',
                tickvals=self.all_sdgs,
                ticktext=self.all_sdgs
            )
        )
        
        return fig
    
    def scopus_line_graph(self, selected_colleges, selected_status, selected_years):  # Modified by Nicole Cabansag
        df = view_manager.get_filtered_data(selected_colleges, selected_status, selected_years)
        
        # Filter out rows where 'scopus' is 'N/A'
        df = df[df['scopus'] != 'N/A']

        # Group data by 'scopus' and 'year'
        grouped_df = df.groupby(['scopus', 'year']).size().reset_index(name='Count')

        # Create the line chart
        fig_line = px.line(
            grouped_df,
            x='year',
            y='Count',
            color='scopus',
            line_group='scopus',
            color_discrete_map=self.palette_dict,
            labels={'scopus': 'Scopus vs. Non-Scopus'}
        )

        # Update layout for the figure
        fig_line.update_layout(
            title='Scopus vs. Non-Scopus Publications Over Time',
            xaxis_title='Academic Year',
            yaxis_title='Number of Research Outputs',
            template='plotly_white',
            height=400,
            xaxis=dict(
                tickformat="%d"  # Ensures years are displayed as whole numbers without commas
            )
        )

        return fig_line


    def publication_format_line_plot(self, selected_colleges, selected_status, selected_years):
        df = view_manager.get_filtered_data(selected_colleges, selected_status, selected_years)
        
        # Filter out rows with 'unpublished' journals and 'PULLOUT' status
        df = df[df['journal'] != 'unpublished']
        df = df[df['status'] != 'PULLOUT']

        # Group data by 'journal' and 'year'
        grouped_df = df.groupby(['journal', 'year']).size().reset_index(name='Count')

        # Create the line chart
        fig_line = px.line(
            grouped_df,
            x='year',
            y='Count',
            color='journal',
            line_group='journal',
            color_discrete_map=self.palette_dict,
            labels={'journal': 'Publication Format'}
        )

        # Update layout for the figure
        fig_line.update_layout(
            title='Publication Formats Over Time',
            xaxis_title='Academic Year',
            yaxis_title='Number of Research Outputs',
            template='plotly_white',
            height=400,
            xaxis=dict(
                tickformat="%d"  # Ensures years are displayed as whole numbers without commas
            )
        )

        return fig_line

    def update_research_outputs_by_year_and_term(self, selected_colleges, selected_status, selected_years):
        df = view_manager.get_filtered_data(selected_colleges, selected_status, selected_years)

        if df.empty:
            return px.bar(title="No data available")

        if len(selected_colleges) == 1:
            # Group by year, program_id, and term for a single college
            self.get_program_colors(df) 
            grouped_df = df.groupby(['year', 'program_id', 'term']).size().reset_index(name='Count')
            x_axis = 'year'
            color_axis = 'program_id'
            xaxis_title = 'Year'
            yaxis_title = 'Number of Research Outputs'
            title = f'Number of Research Outputs by Programs in {selected_colleges[0]} and Year for Each Academic Term' 
            color_label = 'Program'
        else:
            # Group by year, college_id, and term for multiple colleges
            grouped_df = df.groupby(['year', 'college_id', 'term']).size().reset_index(name='Count')
            x_axis = 'year'
            color_axis = 'college_id'
            xaxis_title = 'Year'
            yaxis_title = 'Number of Research Outputs'
            title = 'Number of Research Outputs by College and Year for Each Academic Term'
            color_label = 'College'

        # Create the bar chart with stacking enabled and facets for each term
        fig_bar = px.bar(
            grouped_df,
            x=x_axis,
            y='Count',
            color=color_axis,
            barmode='stack',  # Stack bars for the same year
            color_discrete_map=self.palette_dict if len(selected_colleges) > 1 else self.program_colors,
            facet_col='term',  # Facet by term (1, 2, 3)
            labels={x_axis: xaxis_title, 'Count': yaxis_title, color_axis: color_label}
        )

        # Update the layout of the chart
        fig_bar.update_layout(
            title=title,
            xaxis_title=xaxis_title,
            yaxis_title=yaxis_title,
            template='plotly_white',
            height=400
        )

        return fig_bar


    def set_callbacks(self):
        """
        Set up the callback functions for the dashboard.
        """

        # Callback for reset button
        @self.dash_app.callback(
            [Output('college', 'value'),
            Output('status', 'value'),
            Output('years', 'value')],
            [Input('reset_button', 'n_clicks')],
            prevent_initial_call=True
        )
        def reset_filters(n_clicks):
            return [], [], [view_manager.get_min_value('year'), view_manager.get_max_value('year')]

        @self.dash_app.callback(
            Output('college_line_plot', 'figure'),
            [
                Input('college', 'value'),
                Input('status', 'value'),
                Input('years', 'value')
            ]
        )
        def update_lineplot(selected_colleges, selected_status, selected_years):
            selected_colleges = default_if_empty(selected_colleges, self.default_colleges)
            selected_status = default_if_empty(selected_status, self.default_statuses)
            selected_years = selected_years if selected_years else self.default_years
            return self.update_line_plot(selected_colleges, selected_status, selected_years)

        @self.dash_app.callback(
            Output('college_pie_chart', 'figure'),
            [
                Input('college', 'value'),
                Input('status', 'value'),
                Input('years', 'value')
            ]
        )
        def update_piechart(selected_colleges, selected_status, selected_years):
            selected_colleges = default_if_empty(selected_colleges, self.default_colleges)
            selected_status = default_if_empty(selected_status, self.default_statuses)
            selected_years = selected_years if selected_years else self.default_years
            return self.update_pie_chart(selected_colleges, selected_status, selected_years)

        @self.dash_app.callback(
            Output('research_type_bar_plot', 'figure'),
            [
                Input('college', 'value'), 
                Input('status', 'value'), 
                Input('years', 'value')
            ]
        )
        def update_research_type_bar_plot(selected_colleges, selected_status, selected_years):
            selected_colleges = default_if_empty(selected_colleges, self.default_colleges)
            selected_status = default_if_empty(selected_status, self.default_statuses)
            selected_years = selected_years if selected_years else self.default_years
            return self.update_research_type_bar_plot(selected_colleges, selected_status, selected_years)
        
        @self.dash_app.callback(
            Output('research_status_bar_plot', 'figure'),
            [
                Input('college', 'value'), 
                Input('status', 'value'), 
                Input('years', 'value')
            ]
        )
        def update_research_status_bar_plot(selected_colleges, selected_status, selected_years):
            selected_colleges = default_if_empty(selected_colleges, self.default_colleges)
            selected_status = default_if_empty(selected_status, self.default_statuses)
            selected_years = selected_years if selected_years else self.default_years
            return self.update_research_status_bar_plot(selected_colleges, selected_status, selected_years)
        
        @self.dash_app.callback(
            Output('nonscopus_scopus_bar_plot', 'figure'),
            [Input('college', 'value'), 
             Input('status', 'value'), 
             Input('years', 'value')]
        )
        def create_publication_bar_chart(selected_colleges, selected_status, selected_years):
            selected_colleges = default_if_empty(selected_colleges, self.default_colleges)
            selected_status = default_if_empty(selected_status, self.default_statuses)
            selected_years = selected_years if selected_years else self.default_years
            return self.create_publication_bar_chart(selected_colleges, selected_status, selected_years)
        
        @self.dash_app.callback(
            Output('proceeding_conference_bar_plot', 'figure'),
            [
                Input('college', 'value'), 
                Input('status', 'value'), 
                Input('years', 'value')
            ]
        )
        def update_publication_format_bar_plot(selected_colleges, selected_status, selected_years):
            selected_colleges = default_if_empty(selected_colleges, self.default_colleges)
            selected_status = default_if_empty(selected_status, self.default_statuses)
            selected_years = selected_years if selected_years else self.default_years
            return self.update_publication_format_bar_plot(selected_colleges, selected_status, selected_years)
        
        @self.dash_app.callback(
            Output('sdg_bar_plot', 'figure'),
            [
                Input('college', 'value'), 
                Input('status', 'value'), 
                Input('years', 'value')
            ]
        )
        def update_sdg_chart(selected_colleges, selected_status, selected_years):
            selected_colleges = default_if_empty(selected_colleges, self.default_colleges)
            selected_status = default_if_empty(selected_status, self.default_statuses)
            selected_years = selected_years if selected_years else self.default_years
            return self.update_sdg_chart(selected_colleges, selected_status, selected_years)
        
        @self.dash_app.callback(
            Output("shared-data-store", "data"),
            Input("data-refresh-interval", "n_intervals")
        )
        def refresh_shared_data_store(n_intervals):
            updated_data = view_manager.get_all_data()
            return updated_data.to_dict('records')
        
        #"""
        @self.dash_app.callback(
            Output('text-display-container', 'children'),
            Input("data-refresh-interval", "n_intervals")
        )
        def refresh_text_display(n_intervals):
            return dbc.Container([
                    dbc.Row([
                        dbc.Col(
                        self.create_display_card("Views", str(view_manager.get_sum_value('total_views'))),
                        style={"display": "flex", "justify-content": "center", "align-items": "center", "padding": "0", "margin": "0"}
                    ),
                    dbc.Col(
                        self.create_display_card("Unique Views", str(view_manager.get_sum_value('total_unique_views'))),
                        style={"display": "flex", "justify-content": "center", "align-items": "center", "padding": "0", "margin": "0"}
                    ),
                    dbc.Col(
                        self.create_display_card("Downloads", str(view_manager.get_sum_value('total_downloads'))),
                        style={"display": "flex", "justify-content": "center", "align-items": "center", "padding": "0", "margin": "0"}
                    ),
                    dbc.Col(
                        self.create_display_card("Average Views per Research Output", f"{view_manager.get_average_views_per_research_id():.2f}%"),
                        style={"display": "flex", "justify-content": "center", "align-items": "center", "padding": "0", "margin": "0"}
                    ),
                    dbc.Col(
                        self.create_display_card("Conversion Rate", f"{view_manager.get_conversion_rate():.2f}%"),
                        style={"display": "flex", "justify-content": "center", "align-items": "center", "padding": "0", "margin": "0"}
                    )
                    ])
                ])
        #"""

        @self.dash_app.callback(
            Output('nonscopus_scopus_line_graph', 'figure'),
            [
                Input('college', 'value'),
                Input('status', 'value'),
                Input('years', 'value')
            ]
        )
        def scopus_line_graph(selected_colleges, selected_status, selected_years):
            selected_colleges = default_if_empty(selected_colleges, self.default_colleges)
            selected_status = default_if_empty(selected_status, self.default_statuses)
            selected_years = selected_years if selected_years else self.default_years
            return self.scopus_line_graph(selected_colleges, selected_status, selected_years)
        
        @self.dash_app.callback(
            Output('proceeding_conference_line_graph', 'figure'),
            [
                Input('college', 'value'),
                Input('status', 'value'),
                Input('years', 'value')
            ]
        )
        def publication_format_line_plot(selected_colleges, selected_status, selected_years):
            selected_colleges = default_if_empty(selected_colleges, self.default_colleges)
            selected_status = default_if_empty(selected_status, self.default_statuses)
            selected_years = selected_years if selected_years else self.default_years
            return self.publication_format_line_plot(selected_colleges, selected_status, selected_years)
        
        @self.dash_app.callback(
            Output('term_college_bar_plot', 'figure'),
            [
                Input('college', 'value'),
                Input('status', 'value'),
                Input('years', 'value')
            ]
        )
        def update_research_outputs_by_year_and_term(selected_colleges, selected_status, selected_years):
            selected_colleges = default_if_empty(selected_colleges, self.default_colleges)
            selected_status = default_if_empty(selected_status, self.default_statuses)
            selected_years = selected_years if selected_years else self.default_years
            return self.update_research_outputs_by_year_and_term(selected_colleges, selected_status, selected_years)