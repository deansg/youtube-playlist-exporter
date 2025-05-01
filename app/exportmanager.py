import os.path

from aiohttp import ClientSession

from app.apimodels import PlaylistItem
from app.exporters import CSVExporter, TitlesExporter, Exporter
from app.options import Options
from app.retriever import PlaylistDataRetriever


class YouTubePlaylistExportManager:
    def __init__(self, session: ClientSession, options: Options):
        self._session: ClientSession = session
        self._options: Options = options
        self._validate_input()
        self._exporter: Exporter = CSVExporter(options) if options.csv_output else TitlesExporter(options)

    def _validate_input(self):
        if not os.path.isdir(self._options.output_dir):
            raise Exception(f"Supplied output folder {self._options.output_dir} doesn't exist")
        if not self._options.playlist_id:
            raise Exception("Must provide a non-empty playlist ID")
        if self._options.private_playlist and not self._options.secret_file:
            raise Exception(
                "A secret file containing the path API client's secret must be provided for private playlists")

    def _get_path(self, suffix: str):
        return f"{os.path.join(self._options.output_dir, self._options.playlist_name)}-{suffix}.txt"

    async def export_playlist(self):
        new_items: list[PlaylistItem] = await PlaylistDataRetriever(self._session, self._options).retrieve()
        if not new_items:
            raise Exception("Given playlist is empty")
        self._exporter.export(new_items)
