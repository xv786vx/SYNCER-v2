from helpers.sp_provider import SpotifyProvider
from helpers.yt_provider import YoutubeProvider

yt = YoutubeProvider()
sp = SpotifyProvider()

# intro sequence

print("welcome to Syncer!")
playlist_to_modify = input("(Step 1) Choose a SPOTIFY playlist to sync from: ")

# 2. get information about the playlist
pl_info = sp.get_playlist_by_name(playlist_to_modify)
print(f"SPOTIFY playlist chosen: {pl_info['title']}")

# 3. check if same playlist exists in youtube, if not then make it
print(f"Checking if {pl_info['title']} exists in YouTube account...")
if yt.get_playlist_by_name(playlist_to_modify) is None:
    print(f"Playlist {playlist_to_modify} not found in YouTube, creating it now...")
    yt.create_playlist(playlist_to_modify)

# 4. Add each song from spotify to youtube playlist
print(f"(Step 2) Syncing {pl_info['title']}, {pl_info['id']} to Youtube...")
tracks_to_sync = sp.get_playlist_items(pl_info['id'])

for track in tracks_to_sync:
    song = track['title']
    artists = track['artist']
    yt.add_to_playlist(yt.get_playlist_by_name(pl_info['title'])['id'], yt.search(song, artists))