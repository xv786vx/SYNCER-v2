from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
import yt_dlp

from .provider import Provider
from .provider import preprocessv2, preprocessv3, fuzzy_matchv3

import os
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



    def search_auto(self, track_name, artists) -> list:

        # clean inputs
        # print(f"old artists: {artists}")
        # clean_track_name, artists = preprocess(track_name), preprocess(artists)
        clean_track_name, artists = preprocessv3(track_name, artists), preprocessv2(artists)
        print(f"cleaned track name: {clean_track_name}")
        # print(f"old track name: {track_name}")
        print(f"new artists: {artists}")
        print("")
        
        query = f"{clean_track_name} {artists}"

        request = self.youtube.search().list(q=query, part="snippet", type="video", maxResults=6)
        response = request.execute()
        if response['items']:

            best_match = ["", 0, 0, "", ""]

            for item in response['items']:
                artist_names = preprocessv2(item['snippet']['channelTitle'])
                video_title = preprocessv3(item['snippet']['title'], artists)
                
                track_names_match = max(fuzzy_matchv3(video_title, track_name), fuzzy_matchv3(video_title, clean_track_name))
                artist_match = fuzzy_matchv3(artist_names, artists)


                # check if the video title or description contains the song title
                if track_names_match >= best_match[1] and artist_match >= best_match[2]:
                    print(f"MATCH FOUND FOR {track_name} BY {artists}")
                    print(f"{video_title} BY {artist_names}")
                    best_match[0] = item['id']['videoId']
                    best_match[1] = track_names_match
                    best_match[2] = artist_match
                    best_match[3] = video_title
                    best_match[4] = artist_names

            if best_match[1] > 65 and best_match[2] > 65:
                print(f"final song title (sp): {best_match[3]}, song title (yt): {track_name.lower()}")
                print(f"final artist names (sp): {best_match[4]}, artist names (yt): {artists}")
                print("")
                return best_match
            
            else: 
                print("no suitable match found.")
                return None
        else:
            print("err: result didn't match given structure")
            input("Press Enter to continue...")
            return None

        
    def search_manual(self, track_name, artists) -> str:

        clean_track_name, artists = preprocessv2(track_name), preprocessv2(artists)

        query = f"{clean_track_name} {artists}"

        request = self.youtube.search().list(q=query, part="snippet", type="video", maxResults=6)
        response = request.execute()
        if response['items']:
            for item in response['items']:
                video_title = item['snippet']['title']
                artist_names = item['snippet']['channelTitle']
                
                # check if the video title or description contains the song title
                choice = input(f"Is this the song you were looking for? {video_title} by {artist_names} (y/n): ")
                if choice == 'y':
                    return item['id']['videoId']
                
                else:
                    continue
        else:
            print("err: result didn't match given structure")
            input("Press Enter to continue...")
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
                    'id': item['snippet']['resourceId']['videoId'],
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
    

    def download_song(self, track_id):
        video_url = f"https://www.youtube.com/watch?v={track_id}"

        ydl_opts = {
            'format': 'bestaudio[ext=mp4]',
            'outtmpl': 'Downloads/%(title)s.%(ext)s',
        }

        yt_dlp.YoutubeDL(ydl_opts).download([video_url])


    def download_playlist(self, playlist_id, playlist_name):
        playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
        dl_folder = os.makedirs(os.path.join('Downloads', playlist_name), exist_ok=True)

        ydl_opts = {
            'format': 'bestaudio',
            'outtmpl': os.path.join(dl_folder,'%(title)s.%(ext)s'),
            'noplaylist': False,  # Make sure to download the whole playlist
        }

        yt_dlp.YoutubeDL(ydl_opts).download([playlist_url]) 