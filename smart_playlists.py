#!/usr/bin/python

import argparse
import os
import json
from datetime import datetime
import dateparser
from oauth2client.file import Storage
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import threading


class YoutubeSmartPlaylistManager:
    API_SERVICE_NAME = 'youtube'
    API_VERSION = 'v3'

    subscriptions_cache = "sub_cache.json"
    smart_playlists_file = "smart_playlists.json"

    def __init__(self, creds, smart_playlists):
        self.cache = {}
        self.get_authenticated_service(creds)
        self.smart_playlists_file = smart_playlists

        if os.path.isfile(self.smart_playlists_file):
            with open(self.smart_playlists_file) as f:
                self.smart_playlists = json.load(f)

        if os.path.isfile(YoutubeSmartPlaylistManager.subscriptions_cache):
            with open(YoutubeSmartPlaylistManager.subscriptions_cache) as f:
                self.cache = json.load(f)

    def get_authenticated_service(self, creds):
        storage = Storage(creds)
        credentials = storage.get()
        self.service = build(YoutubeSmartPlaylistManager.API_SERVICE_NAME,
                             YoutubeSmartPlaylistManager.API_VERSION,
                             credentials=credentials)

    def dump_cache(self):
        with open(YoutubeSmartPlaylistManager.subscriptions_cache, "w") as f:
            json.dump(self.cache, f, indent=4, separators=[",", ": "])

    def get_pages(self, function, max_pages=None, **kwargs):
        page_num = 1
        next_page = None

        while True:
            if max_pages is None or max_pages >= page_num:
                if next_page is None:
                    response = function(**kwargs).execute()
                else:
                    kwargs["pageToken"] = next_page
                    response = function(**kwargs).execute()

                page_num += 1

                if "items" in response:
                    for item in response["items"]:
                        yield item

                if "nextPageToken" in response:
                    next_page = response["nextPageToken"]
                else:
                    break
            else:
                break

    def get_playlist_id_by_channel(self, channel_id):
        if channel_id not in self.cache:
            channels = list(self.get_pages(self.service.channels().list, part="contentDetails", id=channel_id))
            self.cache[channel_id] = channels[0]["contentDetails"]["relatedPlaylists"]["uploads"]
            self.dump_cache()

        return self.cache[channel_id]

    def get_my_subscriptions(self):
        for channel in self.get_pages(self.service.subscriptions().list, part='snippet', mine=True):
            yield channel["snippet"]["resourceId"]["channelId"]

    def get_videos_by_channel_id(self, channel_id, max_pages=None):
        for item in self.get_playlist_videos(self.get_playlist_id_by_channel(channel_id), max_pages):
            yield item

    def get_playlist_videos(self, playlist_id, max_pages=None):
        for item in self.get_pages(self.service.playlistItems().list, max_pages=max_pages, part="snippet", playlistId=playlist_id):
            yield item

    def is_video_in_playlist(self, video_id, playlist_id):
        response = self.service.playlistItems().list(part="snippet", playlistId=playlist_id, videoId=video_id).execute()
        return len(response["items"]) > 0

    def get_todays_videos_by_channel(self, channel_id):
        for video in self.get_videos_by_channel_id(channel_id, 1):
            if dateparser.parse(video["snippet"]["publishedAt"]).date() == datetime.today().date():
                yield video

    def get_all_subbed_videos_from_today(self):
        for channel_id in self.get_my_subscriptions():
            for video in self.get_todays_videos_by_channel(channel_id):
                yield video

    def add_video_to_playlist(self, video_id, playlist_id):
        if self.is_video_in_playlist(video_id, playlist_id):
            return False

        video_resource = {
            "snippet": {
                "playlistId": playlist_id,
                "position": 1,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }

        try:
            self.service.playlistItems().insert(body=video_resource, part="snippet").execute()
            return True
        except HttpError:
            return False

    def handle_smart_playlists(self):
        for playlist_name in self.smart_playlists:
            print("Handling {} smart playlist".format(playlist_name))

            playlist_id = self.smart_playlists[playlist_name]["playlist"]
            channels = self.smart_playlists[playlist_name]["channels"]

            for channel in channels:
                for video in self.get_todays_videos_by_channel(channel):
                    video_id = video["snippet"]["resourceId"]["videoId"]
                    video_title = video["snippet"]["title"]
                    channel_title = video["snippet"]["channelTitle"]

                    if self.add_video_to_playlist(video_id, playlist_id):
                        print("Added {} ({}) to {}".format(video_title, channel_title, playlist_name))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--creds_data", help="Credentials file. Run oauath.py to fill creds_data file.")
    parser.add_argument("-p", "--smart_playlists", help="Smart playlists specifications file (JSON)")
    args = parser.parse_args()

    ysp = YoutubeSmartPlaylistManager(args.creds_data, args.smart_playlists)
    ysp.handle_smart_playlists()
    threading.Timer(60*30, ysp.handle_smart_playlists).start()
