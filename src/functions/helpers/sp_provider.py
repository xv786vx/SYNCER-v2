import spotipy
from spotipy.oauth2 import SpotifyOAuth
from .provider import Provider
import os
from dotenv import load_dotenv
from fuzzywuzzy import fuzz
import re

load_dotenv()

sp_client_id = os.getenv("SP_CLIENT_ID")
sp_client_secret = os.getenv("SP_CLIENT_SECRET")

class SpotifyProvider(Provider):
    def __init__(self):
        self.client_id = sp_client_id
        self.client_secret = sp_client_secret
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id = self.client_id,       # Replace with your Client ID
            client_secret= self.client_secret,   # Replace with your Client Secret
            redirect_uri="http://localhost:3000/callback",     # Replace with your Redirect URI
            scope="playlist-modify-private playlist-modify-public"   # You can adjust scope based on your needs
        ))


    def search(self, track_name, artists):
        query = f"{track_name} {artists}"

        results = self.sp.search(q=query, limit=5, type='track')
        if results['tracks']['items']:
            for track in results['tracks']['items']:
                song_title = track['name'].lower()
                artist_names = [artist['name'].lower() for artist in track['artists']]
                print(f"song title (sp): {song_title}, song title (yt): {track_name.lower()}")
                print(f"artist names (sp): {artist_names}, artist names (yt): {artists}")

                print((song_title in track_name.lower() or track_name.lower() in song_title))
                print(any(track_name.lower() in artist_name or artist_name in track_name.lower() for artist_name in artist_names))
                
                
                if (song_title in track_name.lower() or track_name.lower() in song_title) and (any(artist_name in artists.lower() or artists.lower() in artist_name for artist_name in artist_names) or 
                                                                                               any(track_name.lower() in artist_name or artist_name in track_name.lower() for artist_name in artist_names)):
                    print(track['uri'])
                    return track['uri']
                else:
                    print("err: no match found")
        else:
            print("err: result didn't match given structure")
            return None
        
    def searchv2(self, track_name, artists):
        
        # clean inputs
        track_name = clean_str(track_name)
        artists = clean_str(artists)
        
        query = f"{track_name} {artists}"

        results = self.sp.search(q=query, limit=5, type='track')
        if results['tracks']['items']:
            for track in results['tracks']['items']:
                song_title = clean_str(track['name'])
                artist_names = [clean_str(artist['name']) for artist in track['artists']]
                
                
                track_names_match = fuzzy_match(song_title, track_name)
                
                
                artist_match = (any(fuzzy_match(artist_name, artists) for artist_name in artist_names) or 
                any(artist_name in track_name or track_name in artist_name for artist_name in artist_names))
                
                
                if track_names_match and artist_match:
                    return track['uri']
                else:
                    print("err: no match found")
        else:
            print("err: result didn't match given structure")
            return None
    

    def get_playlists(self):
        """Get user playlists."""
        playlists = self.sp.current_user_playlists()
        return [
            (
                pl['name'], 
                pl['id'], 
                pl['images'][0]['url'] if pl.get('images') else 'No Image', 
                pl['uri']
            ) 
        for pl in playlists['items']]
    

    def get_playlist_by_name(self, playlist_name):
        """Search and return a playlist by its name."""
        playlists = self.sp.current_user_playlists()
        for pl in playlists['items']:
            if pl['name'].lower() == playlist_name.lower():  # Case-insensitive comparison
                return {
                    'title': pl['name'],
                    'id': pl['id'],
                    'description': pl.get('description', ''),
                    'image': pl['images'][0]['url'] if pl.get('images') else 'No Image',
                }
        return None  # Return None if playlist not found
    

    def get_playlist_items(self, playlist_id):
        playlist_items = self.sp.playlist_tracks(playlist_id)
        tracks_info = []
        for item in playlist_items['items']:
            track = item['track']
            track_name = track['name']
            artists = ', '.join([artist['name'] for artist in track['artists']])
            
            tracks_info.append({
                'title': track_name,
                'artist': artists,
            })
        
        return tracks_info


    def add_to_playlist(self, playlist_id, track_uri):
        
        """Add track to playlist."""
        try:
            self.sp.playlist_add_items(playlist_id, track_uri)
            print('sigma')
            return True
        except spotipy.exceptions.SpotifyException as e:
            print('ligma')
            return False
    

    def create_playlist(self, playlist_name):
        playlist = self.sp.user_playlist_create(
            user=self.sp.current_user()['id'], 
            name=playlist_name, public=True, 
            description="made with SYNCER!"
        )
        print(f"Created Spotify playlist: {playlist['name']} with ID: {playlist['id']}")
        return playlist


# HELPER FUNCTIONS FOR IMPROVING SPOTIFY SEARCH CAPABILITIES
def fuzzy_match(str1, str2):
    return fuzz.ratio(str1, str2) > 65 or (str1 in str2 or str2 in str1)

def clean_str(s):
    return re.sub(r'[^a-zA-Z0-9\s]', '', s).strip().lower()
