from functions.helpers.sp_provider import SpotifyProvider
from functions.helpers.yt_provider import YoutubeProvider

yt = YoutubeProvider()
spp = SpotifyProvider()

# intro sequence

print("welcome to Syncer!")
# for item in spp.get_playlists(): # 1. retrieve spotify playlists
#     print(f"Playlist Name: {item[0]}, Playlist ID: {item[1]}")
playlist_to_modify = input("(Step 1) Choose a playlist to sync from: ")

# 2. get information about the playlist
print(spp.get_playlist_by_name(playlist_to_modify)['name'])

# 3. check if same playlist exists in youtube, if not then make it
if yt.get_playlist_by_name(playlist_to_modify) is None:
    print(f"Playlist {playlist_to_modify} not found in YouTube, creating it now...")
    yt.create_playlist(playlist_to_modify)

# for item in spp.get_playlist_items(playlist_to_modify):
    
