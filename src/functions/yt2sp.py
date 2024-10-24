from helpers.sp_provider import SpotifyProvider
from helpers.yt_provider import YoutubeProvider

yt = YoutubeProvider()
sp = SpotifyProvider()

# intro sequence

print("welcome to Syncer!")
playlist_to_modify = input("(Step 1) Choose a YOUTUBE playlist to sync from: ")

# 2. get information about the playlist
pl_info = yt.get_playlist_by_name(playlist_to_modify)
print(f"YOUTUBE playlist chosen: {pl_info['title']}")

# 3. check if same playlist exists in spotify, if not then make it
print(f"Checking if {pl_info['title']} exists in Spotify account...")
if sp.get_playlist_by_name(playlist_to_modify) is None:
    print(f"Playlist {playlist_to_modify} not found in Spotify, creating it now...")
    sp.create_playlist(playlist_to_modify)
    
# 4. Add each song from youtube to spotify playlist
print(f"(Step 2) Syncing {pl_info['title']}, {pl_info['id']} to Spotify...")
tracks_to_sync = yt.get_playlist_items(pl_info['id'])

for track in tracks_to_sync:
    song = track['title']
    artists = track['artist']
    print(f"Track URI: {sp.search(song, artists)}")
    sp.add_to_playlist(sp.get_playlist_by_name(pl_info['title'])['id'], sp.search(song, artists))