import asyncio
import shlex
from pathlib import Path
from types import SimpleNamespace

import pytest

from spotdl.download.downloader import DownloadManager
from spotdl.search.songObj import SongObj


def create_song_obj(name="test song", artist="test artist") -> SongObj:
    artists = [{"name": artist}]
    raw_track_meta = {
        "name": name,
        "album": {
            "name": "test album",
            "artists": artists,
            "release_date": "2021",
            "images": [
                {"url": "https://i.ytimg.com/vi_webp/iqKdEhx-dD4/hqdefault.webp"}
            ],
        },
        "artists": artists,
        "track_number": "1",
        "genres": ["test genre"],
    }
    raw_album_meta = {"genres": ["test genre"]}
    raw_artist_meta = {"genres": ["test artist genre"]}
    return SongObj(
        raw_track_meta,
        raw_album_meta,
        raw_artist_meta,
        "https://www.youtube.com/watch?v=Th_C95UMegc",
    )


class FakeProcess:
    """Instead of running ffmpeg, just fake it"""
    def __init__(self, command):
        command = shlex.split(command)
        self._input = Path(command[command.index("-i") + 1])
        self._output = Path(command[-1])

    async def communicate(self):
        """
        Ensure that the file has been download, and create empty output file,
        to avoid infinite loop.
        """
        assert self._input.is_file()
        self._output.open("w").close()
        return (None, None)


async def fake_create_subprocess_shell(command):
    return FakeProcess(command)


@pytest.fixture()
def setup(tmpdir, monkeypatch):
    monkeypatch.chdir(tmpdir)
    monkeypatch.setattr(
        asyncio.subprocess, "create_subprocess_shell", fake_create_subprocess_shell
    )
    monkeypatch.setattr(DownloadManager, "set_id3_data", lambda *_: None)
    data = SimpleNamespace()
    data.directory = tmpdir
    yield data


@pytest.mark.vcr()
def test_download_single_song(setup):
    song_obj = create_song_obj()
    DownloadManager().download_single_song(song_obj)

    assert [file.basename for file in setup.directory.listdir() if file.isfile()] == [
        "test artist - test song.mp3"
    ]


@pytest.mark.vcr()
def test_download_multiple_songs(setup):
    song_objs = [
        create_song_obj(name="song1"),
        create_song_obj(name="song2"),
        create_song_obj(name="song3"),
    ]
    DownloadManager().download_multiple_songs(song_objs)

    assert [file.basename for file in setup.directory.listdir() if file.isfile()] == [
        "test artist - song1.mp3",
        "test artist - song2.mp3",
        "test artist - song3.mp3",
    ]