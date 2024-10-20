from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id = client_id,       # Replace with your Client ID
    client_secret= client_secret,   # Replace with your Client Secret
    redirect_uri="http://localhost:3000/callback",     # Replace with your Redirect URI
    scope="playlist-modify-private playlist-modify-public"   # You can adjust scope based on your needs
))

# playlists = sp.current_user_playlists()
# for playlist in playlists['items']:
#     print(f"Playlist Name: {playlist['name']}, Playlist ID: {playlist['id']}")

#     playlist_id = 'your_playlist_id'

# Search for a track by name
track_name = "Blinding Lights"
results = sp.search(q=track_name, limit=1, type='track')

# Get the track's Spotify URI
if results['tracks']['items']:
    track_uri = results['tracks']['items'][0]['uri']
    print(f"Found Track URI: {track_uri}")
else:
    print("Track not found")

# Add the track to the playlist
try:
    sp.playlist_add_items("23UK0Bcl7gTUmIRh0FYPc3", [track_uri])
    print(f"Track added to the playlist!")
except spotipy.exceptions.SpotifyException as e:
    print(f"Error adding track to playlist: {e}")