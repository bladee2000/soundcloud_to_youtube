import os
import urllib.request
import shutil
import random
from soundcloud import SoundCloud, BasicTrack, MiniTrack
from scdl_v295 import scdl_edit
from pathvalidate import sanitize_filename
import mutagen
import upload_video
import subprocess



def get_image(track: BasicTrack, path):
    url = track.artwork_url
    if url is None:
        url = track.user.avatar_url
    url = url.replace("large", "t500x500")
    print(url)
    print(os.getcwd())
    try:
        urllib.request.urlretrieve(url, os.getcwd() + rf'/{path}/{track.id}.jpg')
    except urllib.error.HTTPError:
        url = track.user.avatar_url
        url = url.replace("large", "t500x500")
        urllib.request.urlretrieve(url, os.getcwd() + rf'/{path}/{track.id}.jpg')

def delete(path):
    answer = input("delete file? \n (Y/N) : ")
    if answer == "Y" or answer == "y":
        if os.path.isdir(path):
            shutil.rmtree(path)


def video_youtube_upload(item, video_path):
    answer = input("upload on youtube? \n (Y/N) : ")
    if answer == "Y" or answer == "y":
        youtube_title = ""
        VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")

        if item.kind == "track":
            youtube_title = f"{item.user.username} - {item.title}"
        if item.kind == "playlist":
            if item.set_type == "":
                youtube_title += "[Playlist]"
            if item.set_type == "album" or item.set_type == "ep":
                youtube_title += "[Album]"
            if item.set_type == "compilation":
                youtube_title += "[Compilation]"
            youtube_title += f" {item.user.username} - {item.title}"

        if len(youtube_title) > 100:
            youtube_title = youtube_title[:100]
        print(youtube_title)

        description = youtube_description(item)
        print(description)

        description = description.replace('<', '').replace('>', '')

        youtube_title = youtube_title.replace('<', '').replace('>', '')

        if len(description) > 4900:
            print(f"{'-'*20}\ndescription is too long....\n{'-'*20}\n")
            description = ""

        upload_video.run(video_path, youtube_title, description, "10", VALID_PRIVACY_STATUSES[0])


def youtube_description(item):
    if item.kind == "track":
        date = item.display_date[:10]
        text = f"{item.permalink_url}\n\nRelease on : {date}"
        return text

    if item.kind == "playlist":
        date = item.display_date[:10]
        text = f"{item.permalink_url}\n\nRelease on : {date}\n\n"
        current_time = 0

        for track in item.tracks:
            h = int(int(int(current_time / 1000) / 60) / 60)
            m = int(int(current_time / 1000) / 60) - int(int(int(current_time / 1000) / 60) / 60) * 60
            s = int(current_time / 1000) - int(int(current_time / 1000) / 60) * 60

            if h < 10:
                h = f"0{h}"
            if m < 10:
                m = f"0{m}"
            if s < 10:
                s = f"0{s}"

            artist = ""
            if item.set_type == "":
                artist = f"{track.user.username} - "

            if int(item.duration / 1000) >= 3600:
                text += f"{h}:{m}:{s} {artist}{track.title}\n"
            else:
                text += f"{m}:{s} {artist}{track.title}\n"

            current_time += track.duration

        return text


def main(url):
    r = str(random.random())
    temp_path = "temp" + r[2:]
    os.mkdir(temp_path)

    scdl_edit.main({'--addtimestamp': False,
     '--addtofile': False,
     '--auth-token': None,
     '--client-id': None,
     '--debug': False,
     '--download-archive': None,
     '--error': False,
     '--extract-artist': False,
     '--flac': False,
     '--force-metadata': False,
     '--hide-progress': False,
     '--hidewarnings': False,
     '--max-size': None,
     '--min-size': None,
     '--name-format': None,
     '--no-album-tag': False,
     '--no-original': True,
     '--no-playlist': False,
     '--no-playlist-folder': False,
     '--only-original': False,
     '--onlymp3': False,
     '--original-art': False,
     '--original-name': False,
     '--overwrite': False,
     '--path': temp_path,
     '--playlist-name-format': None,
     '--remove': False,
     '--strict-playlist': False,
     '--sync': None,
     '-C': False,
     '-a': False,
     '-c': False,
     '-f': False,
     '-l': url,
     '-n': None,
     '-o': None,
     '-p': False,
     '-r': False,
     '-t': False,
     'me': False}
    )
    os.chdir('..')
    print(os.getcwd())

    client = SoundCloud()

    item = client.resolve(url)

    if item.kind == "track":
        video_path = make_video_only_track(temp_path, item)
        video_youtube_upload(item, video_path)
    if item.kind == "playlist":
        playlist_name = sanitize_filename(item.title)
        item = get_track_list(item, client)
        change_mp3_filename(f"./{temp_path}/{playlist_name}", item, temp_path)

        for track in item.tracks:
            make_video_only_track(temp_path, track, True)

        video_list = open(f"./{temp_path}/videos.txt", "w")
        for track in item.tracks:
            video_list.write(f"file '{track.id}.mkv'\n")
        video_list.close()

        subprocess.run(rf'ffmpeg -safe 0 -f concat -i "{temp_path}/videos.txt"'
                       rf' -max_interleave_delta 0 -c copy "{temp_path}/output.mkv"', shell=True)

        video_youtube_upload(item, rf"{temp_path}/output.mkv")

    delete(temp_path)

def get_track_list(item, client):
    for i in range(len(item.tracks)):
        if isinstance(item.tracks[i], MiniTrack):
            item.tracks[i] = client.get_track(item.tracks[i].id)
    return item


def change_mp3_filename(path, item, temp_path):
    file_list = os.listdir(path)

    for file in file_list:
        metadata = mutagen.File(f"{path}/{file}")
        track_number = int(str(metadata['TRCK']))
        after_filename = f"./{temp_path}/{item.tracks[track_number - 1].id}.mp3"
        os.rename(f"{path}/{file}", after_filename)


def make_video_only_track(temp_path, track: BasicTrack, is_playlist: bool = False):
    get_image(track, temp_path)

    mp3_filename = scdl_edit.limit_filename_length(track.title, ".mp3")
    mp3_filename = scdl_edit.sanitize_str(mp3_filename)

    if is_playlist:
        mp3_filename = f"{track.id}.mp3"

    subprocess.run(rf'ffmpeg -loop 1 -framerate 2 -i "{temp_path}/{track.id}.jpg" -i "{temp_path}/{mp3_filename}" ' +
                   rf'-c:v libx264 -preset medium -tune stillimage -t "{track.duration}ms" -crf 18 -c:a copy -shortest -pix_fmt yuv420p ' +
                   rf'"{temp_path}/{track.id}.mkv"', shell=True)

    return rf"{temp_path}/{track.id}.mkv"


if __name__ == '__main__':
    main(input("url : "))