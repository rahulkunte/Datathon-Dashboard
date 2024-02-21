mapbox_access_token = "pk.eyJ1IjoicmFodWxrdW50ZTciLCJhIjoiY2xzcDBhamp0MGw1ZDJybHpjMTZiaWZxNyJ9.RNIIWEvQpKEaXAyP9b6-WQ"





aed_latlons  = pd.read_parquet(r"aed_locations_latlon.parquet.gzip")
pit_latlons = pd.read_parquet(r"pit_locations_latlon.parquet.gzip")
mug_latlons = pd.read_parquet(r"mug_locations_latlon.parquet.gzip")
amb_locs = pd.read_parquet('ambulance_locations.parquet.gzip')
amb_locs.rename({'latitude': 'Lat', 'longitude': 'Lon'},axis=1, inplace=True)

aed_loc_subset = aed_latlons[aed_latlons.postal_code.isin([2000,2018, 2020, 2030, 2040, 2050, 3000, 3001, 3010, 3012, 3018,8500, 8501, 8510, 8511, 2170])]
aed_latlons_antw_prov = aed_latlons[aed_latlons.province == 'Antwerpen']
aed_loc_subset_sub = aed_loc_subset[['postal_code','Lat', 'Lon']]

vec_dict = {'AED': [aed_locs_antwp,'orange'], 'MUG': [mug_latlons,'purple'], 'AMB': [amb_locs,'green'], 'PIT': [pit_latlons,'red']}


mug_dt = pd.read_csv(r"mug_dt.csv")
amb_dt = pd.read_csv(r"amb_dt.csv")
pit_dt = pd.read_csv(r"pit_dt.csv")

df_hist_cd = pd.read_csv(r"cardiac_arrest.csv")
aed_subset_antkort = pd.read_csv('Ant_kort_aed_wt.csv')
aed_leuantkort = pd.concat([df_aed_leuven, aed_subset_antkort], axis = 0)
amb_subset = amb_dt[amb_dt.province.isin(['Antwerpen', 'Vlaams-Brabant', 'West-Vlaanderen'])]

aggr_dt = pd.concat([mug_dt[['Lat', 'Lon', 'DT_6']], amb_subset[['Lat', 'Lon', 'DT_6']], pit_dt[['Lat', 'Lon', 'DT_6']]], ignore_index=True, axis=0)
vec_dt_dict = {'MUG': mug_dt, 'PIT':pit_dt, 'AMB':amb_subset}

sol_df = pd.read_csv('sol_df.csv')



app = Dash(__name__)
app.title = 'Belgium - Emergency Response'

mygraph = dcc.Graph(id='belgium_map', figure={}, config={'displayModeBar': False}, style ={'height':'650px'})

vector_dropdown = dcc.Dropdown(options=["MUG", "AMB", "PIT"], clearable=True, id='vec_dd',
                               multi=True, style={'width': '70%', 'margin-bottom': '10px'})
vec_dt_dropdown = dcc.Dropdown(options=["MUG", "AMB", "PIT", "All"], clearable=True, id='vec_dt',
                               multi=False, style={'width': '70%', 'margin-bottom': '10px'})

aed_radio = dcc.RadioItems(options=[{'label': 'Yes', 'value': 'Yes'}, {'label': 'No', 'value': 'No'}], value='No',
                           id='aed_loc_option', labelStyle={'display': 'inline-block'}, style={'margin-bottom': '10px'})
aed_subset_radio = dcc.RadioItems(options=[{'label': 'Yes', 'value': 'Yes'}, {'label': 'No', 'value': 'No'}], value='No',
                                 id='aed_subset', labelStyle={'display': 'inline-block'}, style={'margin-bottom': '10px'})
hist_cardiac_radio = dcc.RadioItems(options=[{'label': 'Yes', 'value': 'Yes'}, {'label': 'No', 'value': 'No'}],
                                     value='No', id='hist_cardiac', labelStyle={'display': 'inline-block'},
                                     style={'margin-bottom': '10px'})
all_hosp_radio = dcc.RadioItems(options=[{'label': 'Yes', 'value': 'Yes'}, {'label': 'No', 'value': 'No'}],
                                value='No', id='all_hosps', labelStyle={'display': 'inline-block'},
                                style={'margin-bottom': '10px'})
sol_acc = dcc.RadioItems(options=[{'label': 'Yes', 'value': 'Yes'}, {'label': 'No', 'value': 'No'}], value='No',
                         id='sol', labelStyle={'display': 'inline-block'}, style={'margin-bottom': '10px'})

app.layout = html.Div([
    html.Div([
        html.Div([html.Label('1. Choose vector'), vector_dropdown]),
        html.Div([html.Label('2. Visualize AED locations(Antwerp)?'), aed_radio]),
    ], style={'width': '25%', 'display': 'inline-block'}),

    html.Div([
        html.Div([html.Label('3. Vector accessibility?'), vec_dt_dropdown]),
        html.Div([html.Label('4. AED accessibility?'), aed_subset_radio]),
    ], style={'width': '25%', 'display': 'inline-block'}),

    html.Div([
        html.Div([html.Label('5. Past cardiac intervention cases'), hist_cardiac_radio]),
        html.Div([html.Label('6. All hospitals?'), all_hosp_radio]),
    ], style={'width': '25%', 'display': 'inline-block'}),

    html.Div([
        html.Div([html.Label('7. Check solution?'), sol_acc]),
    ], style={'width': '25%', 'display': 'inline-block'}),

    html.Div([mygraph])
])





@app.callback(
    Output('belgium_map', 'figure'),
    [
        Input('vec_dd', 'value'),
        Input('aed_loc_option', 'value'),
        Input('aed_subset', 'value'),
        Input('vec_dt', 'value'),
        Input('hist_cardiac', 'value'),
        Input('all_hosps', 'value'),
        Input('sol', 'value')
    ]
)
def update_graph(vec_val, aed_op, aed_subset, vec_dt_choice, cardiac_hist_opt, all_opt, sol_opt):
    
    fig = px.choropleth_mapbox(mapbox_style="carto-positron", #open-street-map
                           zoom=6, center = {"lat": 50.5039, "lon": 4.4699})

    # for trace in fig.data:
    #     trace_name = trace.name
    #     if trace_name and trace_name.startswith('group_'):
    #         trace.visible = False    
    
    
    if vec_val:
        for vec_type in vec_val:
            chosen_df = vec_dict[vec_type][0]
            vec_col = vec_dict[vec_type][1]
            vec_lats = chosen_df['Lat']
            vec_longs = chosen_df['Lon']
            scatter_vec = go.Scattermapbox(
                lat=vec_lats, lon=vec_longs, mode='markers',
                marker=dict(size=10, opacity=0.8), name=f'{vec_type}',
                showlegend = True
            )

            # Clear existing traces related to vectors
            
            fig.add_trace(scatter_vec)
            fig.update_traces(selector=dict(name=f'{vec_type}'), marker={'color': vec_col}, legendgroup=f'group_{vec_type}')
            # fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, uirevision = 'Dont change',
            #                  legend=dict(x=0, y=-0.05, tracegroupgap=6), showlegend=True)
       

    if(aed_op == 'Yes'):
        aed_df = vec_dict["AED"][0]
        aed_col = vec_dict["AED"][1]
        aed_lats = aed_df['Lat']
        aed_longs = aed_df['Lon']
        scatter_aed = go.Scattermapbox(
            lat=aed_lats, lon=aed_longs, mode='markers',
            marker=dict(size=10, opacity=0.8), name=f'AED locations',
            # text = 'AED location', hoverinfo = 'text',
            showlegend = True
        )

        # Clear existing traces related to vectors

        fig.add_trace(scatter_aed)
        fig.update_traces(selector=dict(name=f'AED locations'), marker={'color': aed_col}, legendgroup=f'group_AED')
        # fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, uirevision = 'Dont change',showlegend=True)
        
        
    # Polygons for AED accesibility in subset: leuven, antwerp and kortrijk.  
    if(aed_subset == 'Yes'):


        print('Inside check driving time')

        interior_coords = []
        exterior_coords = []
        # indx = test_dt_df[test_dt_df[hosp_serv] == 1.0].index.values          


        # Create a list to hold the individual polygons
        polygons = []

        for row in aed_leuantkort_updated.itertuples(index=False):
            polygon = Polygon(ast.literal_eval(row.WT_3m1p5))
            polygons.append(polygon)

        # Calculate the cascaded union of all polygons to get the aggregated polygon
        aggregated_polygon = unary_union(polygons)

        # print('\nCreated aggregate polygon')

        # Check if it's a MultiPolygon
        if isinstance(aggregated_polygon, MultiPolygon):
            num_geometries = len(list(aggregated_polygon.geoms))
            for polygon in aggregated_polygon.geoms:
                exterior_coords = list(polygon.exterior.coords)
                if exterior_coords:
                    dt_lats_exterior, dt_lons_exterior = zip(*exterior_coords)
                else:
                    dt_lats_exterior, dt_lons_exterior = [], []
                    
                aed_wt_trace = go.Scattermapbox(
                    mode="lines",
                    lon=dt_lons_exterior,
                    lat=dt_lats_exterior,
                    opacity=1,
                    name=f'Walking Time(3min, 1.5m/s) To: AED',
                    showlegend=False,
                    text = 'AED acbty. zone',
                    hoverinfo = 'text'
                )

                fig.add_trace(aed_wt_trace)

        else:

            exterior_coords = list(aggregated_polygon.exterior.coords)

            if exterior_coords:
                dt_lats_exterior, dt_lons_exterior = zip(*exterior_coords)
            else:
                dt_lats_exterior, dt_lons_exterior = [], []

            aed_wt_trace = go.Scattermapbox(
                mode="lines",
                lon=dt_lons_exterior,
                lat=dt_lats_exterior,
                opacity=1,
                name=f'Walking Time(3min, 1.5m/s) To: AED',
                show_legend = False,
                text = 'AED acbty. zone',
                hoverinfo = 'text'
                
            )

            fig.add_trace(aed_wt_trace)
            print('\nSingle Polygon, Added trace')

        fig.update_traces(selector=dict(name=f'Walking Time(3min, 1.5m/s) To: AED'), line=dict(width=3, color='#83C750'))
        
                
# Vector driving times: 
    if(vec_dt_choice):

        print('Inside vec driving time')
        if(vec_dt_choice == 'All'):
            df = aggr_dt
        else:
            df = vec_dt_dict[vec_dt_choice]
            
        interior_coords = []
        exterior_coords = []


        polygons = []

        for row in df.itertuples(index=False):
            polygon = Polygon(ast.literal_eval(row.DT_6))
            polygons.append(polygon)


        aggregated_polygon = unary_union(polygons)

        if isinstance(aggregated_polygon, MultiPolygon):

            num_geometries = len(list(aggregated_polygon.geoms))

            for polygon in aggregated_polygon.geoms:

                exterior_coords = list(polygon.exterior.coords)

                for interior in polygon.interiors:
                    interior_coords.extend(list(interior.coords))

                if exterior_coords:
                    dt_lats_exterior, dt_lons_exterior = zip(*exterior_coords)
                else:
                    dt_lats_exterior, dt_lons_exterior = [], []

                if interior_coords:
                    dt_lats_interior, dt_lons_interior = zip(*interior_coords)
                else:
                    dt_lats_interior, dt_lons_interior = [], []

                vec_dt_trace = go.Scattermapbox(
                    mode="lines",
                    lon=dt_lons_exterior,
                    lat=dt_lats_exterior,
                    opacity=1,
                    name=f'Driving Time(6mins): {vec_dt_choice}',
                    showlegend=False,
                    text = f'{vec_dt_choice} acbty. zone',
                    hoverinfo = 'text'# Conditionally set showlegend
                )

                interior_trace = go.Scattermapbox(
                    mode="markers",
                    fill=None,
                    lon=dt_lons_interior,
                    lat=dt_lats_interior,
                    opacity=0.7,
                    name=f'Unreachable Area Boundary To: {vec_dt_choice}',
                    text = f'{vec_dt_choice} inacb. zone',
                    hoverinfo = 'text',
                    showlegend=False # Conditionally set showlegend
                )
                
                # Add both traces to the figure
                fig.add_trace(vec_dt_trace)
                fig.add_trace(interior_trace)
                # print('\nMultipolygon, Added trace')
        else:

            exterior_coords = list(aggregated_polygon.exterior.coords)
            for interior in aggregated_polygon.interiors:
                interior_coords.extend(list(interior.coords))
            if exterior_coords:
                dt_lats_exterior, dt_lons_exterior = zip(*exterior_coords)
            else:
                dt_lats_exterior, dt_lons_exterior = [], []
            if interior_coords:
                dt_lats_interior, dt_lons_interior = zip(*interior_coords)
            else:
                dt_lats_interior, dt_lons_interior = [], []

            vec_dt_trace = go.Scattermapbox(
                mode="lines",
                lon=dt_lons_exterior,
                lat=dt_lats_exterior,
                opacity=1,
                hoverinfo= None ,
                name=f'Driving Time(6mins): {vec_dt_choice}',
                showlegend = False
            )

            interior_trace = go.Scattermapbox(
                mode="markers",
                fill=None,
                lon=dt_lons_interior,
                lat=dt_lats_interior,
                opacity=0.7,
                name=f'Unreachable Area Boundary To: {vec_dt_choice}',
                showlegend = False
            )
            # Add both traces to the figure
            fig.add_trace(vec_dt_trace)
            fig.add_trace(interior_trace)
            print('\nSingle Polygon, Added trace')

            
        fig.update_traces(selector=dict(name=f'Driving Time(6mins): {vec_dt_choice}'), line=dict(width=3, color='black'))
        fig.update_traces(selector=dict(name=f'Unreachable Area Boundary To: {vec_dt_choice}'), marker=dict(size=3, color='blue'))
        # fig.update_layout(
        #     legend=dict(x=0, y=-0.3, tracegroupgap=6), showlegend = False
        # )                      
    
    if(cardiac_hist_opt == 'Yes'):
        
        df = df_hist_cd
        ch_lats = df_hist_cd['Lat']
        ch_longs = df_hist_cd['Lon']
        scatter_ch = go.Scattermapbox(
            lat=ch_lats, lon=ch_longs, mode='markers',
            marker=dict(size=10, opacity=0.8), name=f'Prev. cardiac intv.s',
            text = 'Historical C.A. case',
            hoverinfo = 'text',
            showlegend = True
        )


        fig.add_trace(scatter_ch)
        fig.update_traces(selector=dict(name=f'Prev. cardiac intv.s'), marker={'color': 'purple'}, legendgroup=f'group_CH')
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, uirevision = 'Dont change')

    if(all_opt == 'Yes'):
        
        all_col = 'purple'
        all_lats = df_hosp['Latitude']
        all_longs = df_hosp['Longitude']
        scatter_all = go.Scattermapbox(
            lat=all_lats, lon=all_longs, mode='markers',
            marker=dict(size=10, opacity=0.8), name=f'All hosp',
            showlegend = True
        )

        fig.add_trace(scatter_all)
        fig.update_traces(selector=dict(name=f'All hosp'), marker={'color': all_col}, legendgroup=f'group_all_hosp')
        # fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, uirevision = 'Dont change',
                         # legend=dict(x=0, y=-0.05, tracegroupgap=6), showlegend=False)        
        
    if(sol_opt == 'Yes'):
        print('\nInside 2 sols')
        interior_coords = []
        exterior_coords = []
        polygons = []
        for row in sol_df.itertuples(index=False):
            polygon = Polygon(ast.literal_eval(row.WT_3m1p5))
            polygons.append(polygon)
        aggregated_polygon = unary_union(polygons)
        if isinstance(aggregated_polygon, MultiPolygon):

            num_geometries = len(list(aggregated_polygon.geoms))

            for polygon in aggregated_polygon.geoms:

                exterior_coords = list(polygon.exterior.coords)

                if exterior_coords:
                    dt_lats_exterior, dt_lons_exterior = zip(*exterior_coords)
                else:
                    dt_lats_exterior, dt_lons_exterior = [], []

                sol_wt_trace = go.Scattermapbox(
                    mode="lines",
                    lon= dt_lons_exterior,
                    lat=dt_lats_exterior,
                    opacity=1,
                    name=f'WT To: AED',
                    showlegend=False,
                    text = 'AED acbty. zone',
                    hoverinfo = 'text'
                )

            fig.add_trace(sol_wt_trace)
        else:

            exterior_coords = list(aggregated_polygon.exterior.coords)

            if exterior_coords:
                dt_lats_exterior, dt_lons_exterior = zip(*exterior_coords)
            else:
                dt_lats_exterior, dt_lons_exterior = [], []

            sol_wt_trace = go.Scattermapbox(
                mode="lines",
                lon=dt_lons_exterior,
                lat=dt_lats_exterior,
                opacity=1,
                name=f'WT To: AED',
                showlegend = True,
                text = 'AED acbty. zone',
                hoverinfo = 'text'               
            )

            fig.add_trace(sol_wt_trace)

            print('\nSingle Polygon, Added trace')
            

        fig.update_traces(selector=dict(name=f'WT To: AED'), line=dict(width=3, color='turquoise'))        
        
    # fig.data = [trace for trace in fig.data if "scattermapbox" not in trace.type]    
    
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, uirevision = 'Dont change',
                         legend=dict(x=0, y=-0.05, tracegroupgap=6)) #showlegend=True) 
        
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, jupyter_mode='external', use_reloader=False)
