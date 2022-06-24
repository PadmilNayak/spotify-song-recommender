import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import warnings
warnings.filterwarnings("ignore")
import re

cfs_test = pd.read_csv('./data/complete_feature_set_2016.csv', nrows=10)

float_cols = [c for c in cfs_test if cfs_test[c].dtype == "float64"]
float32_cols = {c: np.float32 for c in float_cols}

complete_feature_set = pd.read_csv('./data/complete_feature_set_2016.csv', engine='c', dtype=float32_cols)

spotify_df = pd.read_csv('./data/spotify_df_2016.csv')
spotify_df.drop(['valence','acousticness','explicit','instrumentalness','key','liveness','loudness','mode','release_date','speechiness','tempo','artists_v1','artists_v2','artists_song','consolidates_genre_lists','popularity_red'],axis=1,inplace=True)

SPOTIPY_CLIENT_ID='724c333b4d9d443ba99b70c6f394908f'
SPOTIPY_CLIENT_SECRET='9be32c1aa413471bad21547bf08204c7'
SPOTIPY_REDIRECT_URI='http://localhost:8881/'
SCOPE = 'user-library-read'
sp = spotipy.Spotify(auth_manager = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET,redirect_uri=SPOTIPY_REDIRECT_URI, scope=SCOPE))

def Recommendation_func(selection_id):
    '''takes input a spotify song id and returns similar songs in a pandas df'''
    selected_song_features = complete_feature_set[complete_feature_set['id'] == selection_id]
    selected_song_features.drop('id',axis=1, inplace= True)

    nonselected_song_features = complete_feature_set.drop(complete_feature_set.index[complete_feature_set['id'] == selection_id])

    Recommmendation_df = spotify_df[spotify_df['id'].isin(nonselected_song_features['id'].values)]
    Recommmendation_df['sim'] = cosine_similarity(nonselected_song_features.drop('id',axis=1).values, selected_song_features.values.reshape(1,-1))[:,0]
    Recommendation_df_top20 = Recommmendation_df.sort_values('sim', ascending = False).head(15)
    Recommendation_df_top20['url'] = Recommendation_df_top20['id'].apply(lambda x : sp.track(x)['album']['images'][1]['url'])
    
    return Recommendation_df_top20

def search_by_song_name(song_string, df):
    '''Searches a song by song name in the given dataframe and return a list of matching songs'''
    
    return df[df.name.str.contains(song_string, case = False, na = False)].sort_values(by = 'popularity', ascending = False).head(15)

def search_by_artist_name(artist_string, df):
    '''Searches a song by artist name in the given dataframe and return a list of matching songs'''
    
    return df[df.artists.str.contains(artist_string, case = False, na = False)].sort_values(by = 'popularity', ascending = False)

def search_by_song_and_artist(search_string, df=spotify_df):
    '''Separates the search string in two parts by 'by:' and searches by first part in songs name and second part in the artist name'''
    
    if 'by:' in search_string:
        song_name_search = search_string.split('by:',1)[0].strip()
        artist_name_search = search_string.split('by:',1)[1].strip()
        
        searched_songs_by_artist_df = search_by_artist_name(artist_name_search, df)
        searched_songs_df = search_by_song_name(song_name_search, searched_songs_by_artist_df)
        
        searched_songs_df['url'] = searched_songs_df['id'].apply(lambda x : sp.track(x)['album']['images'][1]['url'])
        return searched_songs_df
    else:
        searched_songs_df = search_by_song_name(search_string, df)
        searched_songs_df['url'] = searched_songs_df['id'].apply(lambda x : sp.track(x)['album']['images'][1]['url'])
        return searched_songs_df


id_name = {}

for i in sp.current_user_playlists()['items']:
    id_name[i['name']] = i['uri'].split(':')[2]
    
def playlist_songs(playlist_name, id_dic=id_name, df=spotify_df):
    '''returns a df containing playlist songs if it exists in the specified input dataframe 
     input: playlist name, dictionary containing name-id mapping of all playlists, dataframe
     output: df with name, artists, id, url for cover-image, spotify url, date added'''
    
    playlist = pd.DataFrame()
    playlist_name = playlist_name
    
    for ix, i in enumerate(sp.playlist(id_dic[playlist_name])['tracks']['items']):
        playlist.loc[ix, 'artist'] = i['track']['artists'][0]['name']
        playlist.loc[ix, 'name'] = i['track']['name']
        playlist.loc[ix, 'id'] = i['track']['id']
        playlist.loc[ix, 'url'] = i['track']['album']['images'][1]['url']
        playlist.loc[ix, 'web_url'] = 'https://open.spotify.com/track/' + i['track']['id']
        playlist.loc[ix, 'date_added'] = i['added_at']
    
    playlist['date_added'] = pd.to_datetime(playlist['date_added'])
    
    playlist = playlist[playlist['id'].isin(df['id'].values)].sort_values('date_added', ascending = False)
    
    return playlist

def total_songs_count():
    '''returns total songs present in the data'''
    count = len(spotify_df)
    return count

def total_artists_count(df=spotify_df):
    '''returns total unique artists in the data'''
    df['artists_v1'] = df['artists_updated'].apply(lambda x: re.findall(r"'([^']*)'", x))
    df['artists_v2'] = df['artists_updated'].apply(lambda x : re.findall(r"\"(.*)\"",x))
    df['artists_list'] = np.where(df['artists_v1'].apply(lambda x: not x), df['artists_v2'], df['artists_v1'])

    list=[]
    for i in range(len(df)):
        for j in range(len(df.iloc[i,-1])):
            list.append(df.iloc[i,-1][j])
    
    list_np = np.array(list)
    list_unique = np.unique(list_np)
    
    return len(list_unique)

def avg_song_length(df=spotify_df):
    '''returns avg length of songs'''
    mean_length = df['duration_ms'].mean()
    mean_mins = mean_length/60000
    mins = int(mean_mins)
    secs = round((mean_mins%mins)*60)

    return mins,secs 


