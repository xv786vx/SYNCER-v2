class Provider:
    def search_auto(self, query):
        """Search for tracks or videos."""
        raise NotImplementedError("Subclasses should implement this!")

    def convert_mp3(self, item_id):
        """Convert a (Youtube) video or (Spotify) song to mp3 so it can be uploaded onto the respective platform."""
        raise NotImplementedError("Subclasses should implement this!")

    def get_playlists(self):
        """Get user playlists."""
        raise NotImplementedError("Subclasses should implement this!")
    
    def get_playlist_items(self, playlist_id):
        """Get items in a playlist."""
        raise NotImplementedError("Subclasses should implement this!")

    def add_to_playlist(self, playlist_id, item_id):
        """Add a track or video to a playlist."""
        raise NotImplementedError("Subclasses should implement this!")
    
    def create_playlist(self, name):
        """Create a new playlist."""
        raise NotImplementedError("Subclasses should implement this!")
    