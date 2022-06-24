from flask import render_template, request
from application.main import app
import re
from application import recommender
from application.plot import create_plot, songs_by_year_plot
import numpy as np

@app.route('/')
def home():
    fs_df = recommender.playlist_songs('Favorites').sample(5)
    ps_df = recommender.playlist_songs('top_songs').sample(5)
    fav_list = []
    for i in range(0,5):
        fav_list.append([fs_df['name'].iloc[i],fs_df['artist'].iloc[i],fs_df['url'].iloc[i],fs_df['id'].iloc[i],fs_df['web_url'].iloc[i]])

    pop_list = []
    for i in range(0,5):
        pop_list.append([ps_df['name'].iloc[i],ps_df['artist'].iloc[i],ps_df['url'].iloc[i],ps_df['id'].iloc[i],ps_df['web_url'].iloc[i]])
    return render_template('index.html',pop_songs=pop_list,fav_songs=fav_list)
    
@app.route('/search',methods=['GET','POST'])
def search_song():
    if request.method == 'POST':
        search = request.form.get('search')
        search_df = recommender.search_by_song_and_artist(search)

        search_df['artists_v1'] = search_df['artists_updated'].apply(lambda x: re.findall(r"'([^']*)'", x))
        search_df['artists_v2'] = search_df['artists_updated'].apply(lambda x : re.findall(r"\"(.*)\"",x))
        search_df['artists_list'] = np.where(search_df['artists_v1'].apply(lambda x: not x), search_df['artists_v2'], search_df['artists_v1'])
        search_list = []
        for i in range(len(search_df)):
            search_list.append([search_df['name'].iloc[i],search_df['artists_list'].iloc[i][0],search_df['url'].iloc[i],'https://open.spotify.com/track/' + search_df['id'].iloc[i],search_df['id'].iloc[i]])     
    return render_template('search.html',search_list=search_list, search=search)

@app.route('/recommend/<song>/<song_id>', methods=['GET','POST'])
def recommend(song,song_id):
    #if request.method == 'POST':
        #song_id = request.form.get('song')
    res = recommender.Recommendation_func(song_id)
    res['artists_v1'] = res['artists_updated'].apply(lambda x: re.findall(r"'([^']*)'", x))
    res['artists_v2'] = res['artists_updated'].apply(lambda x : re.findall(r"\"(.*)\"",x))
    res['artists_list'] = np.where(res['artists_v1'].apply(lambda x: not x), res['artists_v2'], res['artists_v1'])
    songs_list = []
    for i in range(len(res)):
        songs_list.append([res['name'].iloc[i],res['artists_list'].iloc[i][0],res['url'].iloc[i],'https://open.spotify.com/track/' + res['id'].iloc[i]])
    return render_template('result.html',songs_list=songs_list,song=song)

@app.route('/dashboard')
def feature():
    feature = 'popularity'
    feature_2='size'
    #feature_3 = 'features'
    total_songs = recommender.total_songs_count()
    total_artists = recommender.total_artists_count()
    mins,secs = recommender.avg_song_length()
    bar = create_plot(feature=feature)
    bar2 = create_plot(feature_2=feature_2)
    line_plot = songs_by_year_plot()
    return render_template('dashboard.html', plot=bar, plot2=bar2, line_plot=line_plot, total_songs=total_songs, total_artists=total_artists,mins=mins,secs=secs )


@app.route('/bar', methods=['GET','POST'])
def change_features():
    feature = request.args['selected']
    graphJSON= create_plot(feature=feature)
    return graphJSON

@app.route('/bar2', methods=['GET','POST'])
def change_features_2():
    feature_2 = request.args['selected']
    graphJSON= create_plot(feature_2=feature_2)
    return graphJSON

@app.route('/line', methods=['GET','POST'])
def change_features_3():
    feature_3 = request.args['selected']
    graphJSON= songs_by_year_plot(feature_3=feature_3)
    return graphJSON