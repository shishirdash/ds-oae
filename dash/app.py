from dash import Dash, html, dcc
import fiona
import pandas as pd
import plotly.io as pio
import plotly.graph_objects as go

app = Dash(__name__)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options


# No need to pass "layer='etc'" if there's only one layer
df = []
locs = {'type': 'FeatureCollection', 'features': []}
with fiona.open('../WastewaterOutfall.gpkg') as layer:
    for feature in layer:
        df.append({
            'id': feature['id'],
            'major_minor': feature['properties']['majorMinorStatus'],
            'city_state': f"{feature['properties']['cityName']}, {feature['properties']['stateUSPS']}",
            "lat": feature['geometry']['coordinates'][1],
            "long": feature['geometry']['coordinates'][0],
            "permit_status": feature['properties']['permitStatus'],
            "text": f"{feature['properties']['cityName']}, {feature['properties']['stateUSPS']}: {feature['properties']['majorMinorStatus']}; Permit \n{feature['properties']['permitStatus']}",
        })
        feature['properties'][
            'cityStateName'] = f"{feature['properties']['cityName']}, {feature['properties']['stateUSPS']}"
        locs['features'].append(feature)
df = pd.DataFrame(df)

df['point_score'] = 100
df.loc[df.major_minor == 'Minor', 'point_score'] = 50

df['point_color'] = 'blue'
df.loc[df.major_minor == 'Minor', 'point_color'] = 'red'

# pio.renderers.default = "browser"

fig = go.Figure(data=go.Scattergeo(
    lon=df['long'],
    lat=df['lat'],
    text=df['text'],
    locationmode="USA-states",
    marker_color=df['point_color'],
    hoverinfo='text'
))
fig.update_layout(
    title='Outfall locations',
    geo_scope='usa',
)

app.layout = html.Div(children=[
    html.H1(children='Dashboard for OAE visuals'),

    html.Div(children=''' 
        Wastewater outfall locations       
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
