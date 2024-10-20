import os
import google.oauth2.credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# Set up YouTube API
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly',
          'https://www.googleapis.com/auth/youtube']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
CLIENT_SECRETS_FILE = 'CLIENT_SECRETS_FILE.json'

flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
credentials = flow.run_local_server(port=3000) 

youtube = build('youtube', 'v3', credentials=credentials)

# get the user's playlists
# request = youtube.playlists().list(part="snippet", mine=True)
# response = request.execute()

# # print out playlists (formatted)
# for playlist in response.get("items", []):
#     print(f"Playlist Title: {playlist['snippet']['title']}")
#     print(f"Playlist ID: {playlist['id']}")

test_playlist_id = "PLNEK6awsEHdvo1BzA-xn7aeaRD8Hs-1oX"

video_id = "UqIJ6xKRQRM"

# Insert the video into the playlist
request = youtube.playlistItems().insert(
    part="snippet",
    body={
        "snippet": {
            "playlistId": test_playlist_id,
            "resourceId": {
                "kind": "youtube#video",
                "videoId": video_id
            }
        }
    }
)

response = request.execute()

# Print the response to confirm that the video was added
print(f"Video added to playlist: {response['snippet']['title']}")
    