import os.path

from aiohttp import ClientSession

from options import Options


class YouTubePlaylistExporter:
    def __init__(self, session: ClientSession):
        self._session: ClientSession = session

    async def export_playlist(self, options: Options):
        self._validate_input(options)

    @staticmethod
    def _validate_input(options: Options):
        if not os.path.isdir(options.output_dir):
            raise Exception() # TODO
