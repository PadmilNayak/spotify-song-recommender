import plotly
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import json
import numpy as np
import re

def create_plot(feature=None,feature_2=None):
    '''creates bar plot for top songs and top artists features'''
    
    df = pd.read_csv('data/spotify_df_2016.csv')
    
    if feature_2 is None: #for plot1 i.e. top songs chart
        dff = df.sort_values(by=feature, ascending=False).head(10)

        fig=px.bar(
                data_frame=dff,
                x=feature,
                y= 'name',
                range_x= [dff[feature].min()*0.97, dff[feature].max()],
                hover_data=['name', 'artists', feature],
                labels={'name': 'Song Name', 'artists':'Artist','popularity':'Popularity',
                'liveness':'Liveness','danceability':'Danceability','tempo':'Tempo','valence':'Valence'},
                #width=500,
                #height=400,
                template='seaborn'
            )

    elif feature is None: #for plot2 i.e. top artists chart
        df['artists_v1'] = df['artists_updated'].apply(lambda x: re.findall(r"'([^']*)'", x))
        df['artists_v2'] = df['artists_updated'].apply(lambda x : re.findall(r"\"(.*)\"",x))
        df['artists_list'] = np.where(df['artists_v1'].apply(lambda x: not x), df['artists_v2'], df['artists_v1'])

        df_exp = df.explode('artists_list')
        df_grpby = df_exp.groupby(['artists_list']).mean()
        df_count = df_exp.groupby('artists_list').size().to_frame('size').sort_values('size',ascending=False)
        df_count.drop(df_count[df_count['size'] < 15].index,axis=0, inplace=True)
        df_join = df_count.join(df_grpby, how='left')

        dff = df_join.sort_values([feature_2], ascending=False).head(10)
        dff['artist_name'] = dff.index
        
        fig=px.bar(
                data_frame=dff,
                x=feature_2,
                y= 'artist_name',
                range_x= [dff[feature_2].min()*0.97, dff[feature_2].max()],
                hover_data=['artist_name', feature_2],
                labels={'name': 'Song Name', 'artists':'Artist','popularity':'Popularity',
                'liveness':'Liveness','danceability':'Danceability','tempo':'Tempo','valence':'Valence', 'size':'No of Songs', 'artist_name':'Artist'},
                #width=500,
                #height=400,
            )
        fig.update_traces(marker_color='#BB7C11')

    fig.update_yaxes(
        tickangle=0,
        ticklabelposition="inside",
        tickfont_size=14,
        tickfont_color="#CCCCCC",
        ticklabeloverflow='hide past div',
        autorange="reversed",
        showgrid=False
    )
    fig.update_xaxes(showticklabels=False,showgrid=False)
    fig.update_layout(
        font_family="Rubik",
        xaxis_title=None,
        yaxis_title=None,
        margin=dict(l =0, r =0, t =20, b =0),
        hoverlabel_bgcolor='#E6E6E6',
        hoverlabel_bordercolor='#D8D8D8',
        hoverlabel_font_color='#3A3A3A',
        paper_bgcolor='#FBFBFB',
        plot_bgcolor='#FBFBFB'
    )
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

def songs_by_year_plot(feature_3='features'):
    '''creates line plot for songs features'''

    df = pd.read_csv('data/spotify_df_2016.csv')

    dff = df.groupby('year').mean()
    dff['duration_min'] = dff['duration_ms'].apply(lambda i: i/60000)
    dff['year'] = dff.index

    if feature_3=='features':
        feature = ['energy','acousticness','danceability','explicit']
        fig=px.line(
            dff, x="year", y=feature
        )
    else:
        fig=px.line(
            dff, x="year", y=feature_3
        )

    fig.update_xaxes(showticklabels=True,showgrid=False,dtick=1)
    fig.update_yaxes(showticklabels=True,showgrid=False)
    fig.update_layout(
        #width=1045,
        #height=400,
        font_family="Rubik",
        xaxis_title=None,
        yaxis_title=None,
        margin=dict(l =0, r =0, t =20, b =0),
        hoverlabel_bgcolor='#E6E6E6',
        hoverlabel_bordercolor='#D8D8D8',
        hoverlabel_font_color='#3A3A3A',
        paper_bgcolor='#FBFBFB',
        plot_bgcolor='#FBFBFB'
    )
    graphJSON2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON2
