Youtube Smart Playlist Manager
==============================

Uses the Youtube Data API to add new videos to playlists according to
smart playlist specifications in [Smart Playlists file](smart_playlists.json).

Runs every 30 minutes and adds any files from today to playlists. Will not add
duplicates to playlists.

Setup:
  * Run [OAuth Flow script](run_oauth_flow.py).
  * Copy/paste the URL into a web browser, and authenticate with the desired Google account.
  * Copy/paste the authorization code into the pending command prompt.
  * This should dump out creds.data. Copy this into the config_data directory.
  * Modify the example smart_playlists.json file with your own playlist ids and channel IDs.
  * Copy smart_playlists.json into config_data

Run directly:

    python smart_playlists.py -c /config_data/creds.data -p /config_data/smart_playlists.json

To build docker image:

     docker build -t youtube_smart_playlists -f Dockerfile .

     docker create --name youtube_smart_playlists --volume <absolute path to config_data>:/config_data youtube_smart_playlists

     docker start youtube_smart_playlists

     docker logs -f youtube_smart_playlists
