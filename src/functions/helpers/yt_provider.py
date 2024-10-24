from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from .provider import Provider
import os
import json
from dotenv import load_dotenv

load_dotenv()

yt_client_id = os.getenv("YT_CLIENT_ID")
yt_project_id = os.getenv("YT_PROJECT_ID")
yt_auth_uri = os.getenv("YT_AUTH_URI")
yt_token_uri = os.getenv("YT_TOKEN_URI")
yt_auth_provider_x509_cert_url = os.getenv("YT_AUTH_PROVIDER_X509_CERT_URL")
yt_client_secret = os.getenv("YT_CLIENT_SECRET")
yt_redirect_uri = os.getenv("YT_REDIRECT_URIS")

TOKEN_FILE = "token.json"

class YoutubeProvider(Provider):
    def __init__(self):
        scopes =   ['https://www.googleapis.com/auth/youtube.readonly',
                        'https://www.googleapis.com/auth/youtube']
        
        credentials = None
        
        # load credentials from token file if it exists
        if os.path.exists(TOKEN_FILE):
            credentials = Credentials.from_authorized_user_file(TOKEN_FILE, scopes=scopes)
            if credentials and credentials.expired and credentials.refresh_token:
                try:
                    credentials.refresh(Request())
                except RefreshError:
                    print("Failed to refresh token.")
                    credentials = None
        
        # if not valid credentials available, prompt user to authenticate
        if not credentials or not credentials.valid:
            flow = InstalledAppFlow.from_client_config(
                {
                    "web": {
                        "client_id": yt_client_id,
                        "project_id": yt_project_id,
                        "auth_uri": yt_auth_uri,
                        "token_uri": yt_token_uri,
                        "auth_provider_x509_cert_url": yt_auth_provider_x509_cert_url,
                        "client_secret": yt_client_secret,
                        "redirect_uris": [yt_redirect_uri],
                    }
                },
                scopes = scopes
            )
            credentials = flow.run_local_server(port=3000)
            
            # save credentials to token file for later use
            with open(TOKEN_FILE, "w") as token_file:
                token_file.write(credentials.to_json())
        
        self.youtube = build('youtube', 'v3', credentials=credentials)



    def search(self, song_title, artists):
        query = f"{song_title} {artists}"
        request = self.youtube.search().list(q=query, part="snippet", type="video", maxResults=7)
        response = request.execute()
        if response['items']:
            for item in response['items']:
                video_title = item['snippet']['title'].lower()
                video_description = item['snippet']['description'].lower()
                
                # check if the video title or description contains the song title
                if (song_title.lower() in video_title or video_description) and (artists.lower() in video_title or video_description):
                    return item['id']['videoId']
        else:
            return None
    

    def get_playlists(self):
        request = self.youtube.playlists().list(part="snippet", mine=True)
        response = request.execute()
        return [
            {
                'title': pl['snippet']['title'],
                'id': pl['id'],
                'description': pl['snippet'].get('description', ""),
                'image': pl['snippet']['thumbnails']['default']['url']
            }
            for pl in response.get("items", [])]
    

    def get_playlist_by_name(self, playlist_name):
        playlists = self.get_playlists()
        for pl in playlists:
            if pl['title'].lower() == playlist_name.lower():  # Case-insensitive comparison
                return {
                    'title': pl['title'],
                    'id': pl['id'],
                    'description': pl.get('description', ''),
                    'image': pl.get('thumbnail', None),
                }
        return None 

    def get_playlist_items(self, playlist_id):
        """get all items (videos) in playlist."""
        playlist_items = []
        request = self.youtube.playlistItems().list(part="snippet", playlistId=playlist_id, maxResults=25)
    
        while request:
            response = request.execute()
            
            # Add the current batch of items to the playlist_items list
            playlist_items.extend([
                {
                    'title': item['snippet']['title'],
                    # 'videoId': item['snippet']['resourceId']['videoId'],
                    'artist': item['snippet']['videoOwnerChannelTitle']
                }
                for item in response['items']
            ])
            
            # Check if there's a next page
            request = self.youtube.playlistItems().list_next(request, response)
    
        return playlist_items
    

    def add_to_playlist(self, playlist_id, item_id):
        request = self.youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": item_id
                    }
                }
            }
        )
        request.execute()
    
    def create_playlist(self, playlist_name):
        request = self.youtube.playlists().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": playlist_name,
                    "description": "made with SYNCER!"
                },
                "status": {
                    "privacyStatus": "public"  # can be "private" or "unlisted"
                }
            }
        )
        response = request.execute()
        print(f"Created YouTube playlist: {response['snippet']['title']} with ID: {response['id']}")
        return response