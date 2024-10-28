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
t_to_sync_yt = yt.get_playlist_items(pl_info['id'])

t_to_sync_sp = []
for track in t_to_sync_yt:
    song = track['title']
    artists = track['artist']
    # print(f"YT: {song}, {artists}")
    # print(f"SP: {sp.searchv2(song, artists)[0]['name']}, {sp.searchv2(song, artists)[1]}...")
    t_to_sync_sp.append(sp.search_auto(song, artists))
    

sp.add_to_playlist(sp.get_playlist_by_name(pl_info['title'])['id'], t_to_sync_sp)