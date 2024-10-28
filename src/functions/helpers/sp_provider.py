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

    
    def search_auto(self, track_name, artists):
        
        # clean inputs
        # clean_track_name, artists = preprocess(track_name), preprocess(artists)
        clean_track_name, artists = preprocess(track_name), preprocess(artists)
        
        query = f"{track_name} {artists}"

        results = self.sp.search(q=query, limit=6, type='track')
        if results['tracks']['items']:

            best_match = ["", 0, 0, "", ""]

            for track in results['tracks']['items']:
                song_title = preprocess(track['name'])
                artist_names = [preprocess(artist['name']) for artist in track['artists']]
                
                #region
                track_names_match = max(fuzzy_matchv2(song_title, track_name), fuzzy_matchv2(song_title, clean_track_name))
                artist_match = max(fuzzy_matchv2(artist_name, artists) for artist_name in artist_names)
                
                
                if track_names_match >= best_match[1] and artist_match >= best_match[2]:
                    print(f"MATCH FOUND FOR {track_name} BY {artists}")
                    print(f"{song_title} BY {artist_names}")
                    best_match[0] = track['uri']
                    best_match[1] = track_names_match
                    best_match[2] = artist_match
                    best_match[3] = song_title
                    best_match[4] = artist_names
            
            if best_match[1] > 65 and best_match[2] > 65:
                print(f"final song title (sp): {best_match[3]}, song title (yt): {track_name.lower()}")
                print(f"final artist names (sp): {best_match[4]}, artist names (yt): {artists}")
                print("")
                return best_match[0]
            
            else: 
                print(f"The best match found for <{track_name}> by <{artists}> is <{best_match[3]}> by <{best_match[4]}>.")
                input(f"Would you like to (1) Smart Sync, (2) manually search the song, or (3) skip? ")
                return None
        else:
            print("err: result didn't match given structure")
            input("Press Enter to continue...")
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

def preprocess(text):
    stopwords = {"official", "music", "video", "topic"}
    # stopwords = {"feat", "featuring", "official", "music", "video", "topic"}
    tokens = text.lower().split()
    filtered_tokens = [token for token in tokens if token not in stopwords]
    filtered_text = " ".join(filtered_tokens)
    
    final_text = re.sub(r'[^a-zA-Z0-9\s]', '', filtered_text)
    
    return final_text

def fuzzy_matchv2(str1, str2):
    ratio = fuzz.ratio(str1, str2)
    partial_ratio = fuzz.partial_ratio(str1, str2)
    
    # Weighted combination for refined matching
    return int(0.7 * ratio + 0.3 * partial_ratio)

