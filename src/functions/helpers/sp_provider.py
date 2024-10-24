import spotipy
from spotipy.oauth2 import SpotifyOAuth
from .provider import Provider
import os
from dotenv import load_dotenv

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

        results = self.sp.search(q=query, limit=1, type='track')
        print(f"track p1: {results['tracks']}")
        print("")
        print(f"track p2: {results['tracks']['items']}")
        print("")
        print(f"track p3: {results['tracks']['items'][0]}")
        print("")
        print(f"track name: {results['tracks']['items'][0]['name']}")
        print("")
        print(f"artist name: {results['tracks']['items'][0]['artists'][0]['name']}")
        print("")
        print(f"track uri: {results['tracks']['items'][0]['uri']}")
        print("")
        if results['tracks']['items']:
            for track in results['tracks']['items']:
                song_title = track['name'].lower()
                artist_names = [artist['name'].lower() for artist in track['artists']]
                
                if song_title == track_name.lower() and any(artist.lower() in artist_names for artist in artists.split()):
                    return track['uri']
        else:
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
            return True
        except spotipy.exceptions.SpotifyException as e:
            return False
    

    def create_playlist(self, playlist_name):
        playlist = self.sp.user_playlist_create(
            user=self.sp.current_user()['id'], 
            name=playlist_name, public=True, 
            description="made with SYNCER!"
        )
        print(f"Created Spotify playlist: {playlist['name']} with ID: {playlist['id']}")
        return playlist
# %%
