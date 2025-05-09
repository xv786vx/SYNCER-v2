from src.functions.helpers.sp_provider import SpotifyProvider
from src.functions.helpers.yt_provider import YoutubeProvider


def sync_sp_to_yt(playlist_to_modify):
    yt = YoutubeProvider()
    sp = SpotifyProvider()


    pl_info = sp.get_playlist_by_name(playlist_to_modify)
    print(f"SPOTIFY playlist chosen: {pl_info['title']}")

    # 3. check if same playlist exists in youtube, if not then make it
    print(f"Checking if {pl_info['title']} exists in YouTube account...")
    if yt.get_playlist_by_name(playlist_to_modify) is None:
        print(f"Playlist {playlist_to_modify} not found in YouTube, creating it now...")
        yt.create_playlist(playlist_to_modify)

    # 4. Add each song from spotify to youtube playlist
    print(f"(Step 2) Syncing {pl_info['title']}, {pl_info['id']} to Youtube...")
    t_to_sync_sp = sp.get_playlist_items(pl_info['id'])

    t_to_sync_yt = []
    for track in t_to_sync_sp:
        song = track['title']
        artists = track['artist']

        result = yt.search_auto(song, artists)
        if result is not None:
            print(result)
            t_to_sync_yt.append(result[0])
        else:
            print(f"A suitable match for <{song}> by <{artists}> was not found.")
            choice = int(input(f"Would you like to (1) manually search the song, or (2) skip? "))
            if choice == 1:
                song = input("Enter the song title: ")
                artists = input("Enter the artist(s): ")
                result = yt.search_manual(song, artists)
                t_to_sync_yt.append(result)
            
            else:
                continue

    yt.add_to_playlist(yt.get_playlist_by_name(pl_info['title'])['id'], t_to_sync_yt)
