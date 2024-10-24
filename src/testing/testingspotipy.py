from functions.helpers.sp_provider import SpotifyProvider

sp = SpotifyProvider()

track_name = "Hello"
artists = "Adele"

results = sp.search(track_name, artists)