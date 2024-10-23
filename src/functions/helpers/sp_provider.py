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


    def search(self, track_name):
        """Search for a track by name."""
        results = self.sp.search(q=track_name, limit=1, type='track')
        if results['tracks']['items']:
            track_uri = results['tracks']['items'][0]['uri']
            return track_uri
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
                    'name': pl['name'],
                    'id': pl['id'],
                    'uri': pl['uri'],
                    'image': pl['images'][0]['url'] if pl.get('images') else 'No Image'
                }
        return None  # Return None if playlist not found
    

    def get_playlist_items(self, playlist_id):
        playlist_items = self.sp.playlist_tracks(playlist_id)
        return playlist_items['items']


    def add_to_playlist(self, playlist_id, track_uri):
        """Add track to playlist."""
        try:
            self.sp.playlist_add_items(playlist_id, [track_uri])
            return True
        except spotipy.exceptions.SpotifyException as e:
            return False
    

    def create_playlist(self, user_id, playlist_name, description=""):
        playlist = self.sp.user_playlist_create(user=user_id, name=playlist_name, public=True, description=description)
        print(f"Created Spotify playlist: {playlist['name']} with ID: {playlist['id']}")
        return playlist