import abc
import csv
import dataclasses
import os.path
import shutil
from dataclasses import dataclass

from dataclasses_json import dataclass_json

from app.apimodels import PlaylistItem
from app.options import Options
from app import utils


class Exporter(abc.ABC):
    @abc.abstractmethod
    def export(self, new_items: list[PlaylistItem]) -> None:
        raise NotImplementedError()


class TitlesExporter(Exporter):
    def __init__(self, options: Options):
        self._options: Options = options
        self._new_version_path = self._get_path("YoutubeBackupNew")
        self._old_version_path = self._get_path("YoutubeBackup")
        self._diff_file_path = self._get_path("YoutubeBackupDiff")
        self._diff_backup_path = self._get_path("YoutubeBackupDiffOld")
        self._old_version_backup_path = self._get_path("YoutubeBackupOld")
        self._missing_videos_path = self._get_path("YoutubeMissingVideos")

    def _get_path(self, suffix: str):
        return f"{os.path.join(self._options.output_dir, self._options.playlist_name)}-{suffix}.txt"

    def export(self, new_items: list[PlaylistItem]) -> None:
        prev_titles: list[str] = self._get_latest_backup_data()
        length_diff: int = self._calc_and_validate_length_diff(new_items, prev_titles)
        self._write_backup()
        self._override_old_files()
        self._write_new_titles(new_items)
        self._write_diff_file(new_items, prev_titles, length_diff)

    def _get_latest_backup_data(self) -> list[str]:
        utils.log(f"Retrieving old {self._options.playlist_name} data")
        path = self._new_version_path
        if not os.path.exists(path):
            return []
        return self._get_data_from_file(path)

    @staticmethod
    def _get_data_from_file(file_path: str) -> list[str]:
        with open(file_path, encoding="utf-8") as f:
            return [line[line.index(".") + 2:].strip() for line in f]

    def _calc_and_validate_length_diff(self, new_items: list[PlaylistItem], prev_titles: list[str]):
        utils.log("Validating new items and calculating diffs")
        num = len(new_items) - len(prev_titles)
        if num >= 0:
            return num
        self._create_missing_videos_file(new_items, prev_titles)
        raise Exception("Some videos were removed since the last run with no update to the files!")

    def _create_missing_videos_file(self, new_items: list[PlaylistItem], prev_titles: list[str]):
        new_titles = {item.snippet.title for item in new_items}
        with open(self._missing_videos_path, "w", encoding="utf-8") as f:
            for i in range(len(prev_titles)):
                if not prev_titles[i] in new_titles:
                    f.write(f"{i + 1}. {prev_titles[i]}\n")

    def _write_backup(self):
        utils.log("Creating backups")
        if os.path.exists(self._old_version_path):
            shutil.copyfile(self._old_version_path, self._old_version_backup_path)
        if os.path.exists(self._diff_file_path):
            shutil.copyfile(self._diff_file_path, self._diff_backup_path)

    def _override_old_files(self):
        if os.path.isfile(self._new_version_path):
            shutil.copyfile(self._new_version_path, self._old_version_path)

    def _write_new_titles(self, new_items: list[PlaylistItem]):
        utils.log(f"Writing new {self._options.playlist_name} titles to file")
        with open(self._new_version_path, "w", encoding="utf-8") as f:
            f.writelines([f"{i + 1}. {new_items[i].snippet.title}\n" for i in range(len(new_items))])

    def _write_diff_file(self, new_items: list[PlaylistItem], prev_titles: list[str], length_diff: int):
        utils.log("Writing diff file")
        with open(self._diff_file_path, "w", encoding="utf-8") as f:
            if self._options.are_new_videos_last:
                for i in range(len(prev_titles)):
                    prev_title = prev_titles[i]
                    new_title = new_items[i].snippet.title
                    if prev_title != new_title:
                        f.write(f"{i + 1}. Old: {prev_title}. New: {new_title}\n")
            else:
                for i in range(len(prev_titles) - 1, -1, -1):
                    prev_title = prev_titles[i]
                    new_title = new_items[i + length_diff].snippet.title
                    if prev_title != new_title:
                        f.write(f"{i + 1 + length_diff}. Old: {prev_title}. New: {new_title}\n")


@dataclass_json
@dataclass
class _CSVPlaylistItem:
    position: int
    id: str
    published_at: str
    title: str
    channel_title: str | None
    channel_id: str | None


@dataclass_json
@dataclass
class _CSVDiffItem:
    position: int
    current_title: str
    previous_title: str
    channel_title: str


class CSVExporter(Exporter):
    def __init__(self, options: Options):
        self._options: Options = options
        self._new_version_path = self._get_path("items")
        self._old_version_path = self._get_path("items-backup")
        self._diff_file_path = self._get_path("diff")
        self._diff_backup_path = self._get_path("diff-backup")
        self._old_version_backup_path = self._get_path("backup-backup")
        self._missing_videos_path = self._get_path("missing-videos")
        self._missing_videos_backup_path = self._get_path("missing-videos-backup")

    def _get_path(self, suffix: str):
        return os.path.join(self._options.output_dir, f"YouTube-{self._options.playlist_name}-{suffix}.csv")

    def export(self, new_items: list[PlaylistItem]) -> None:
        prev_items: list[_CSVPlaylistItem] = self._get_latest_backup_data()
        self._write_backup()
        self._override_old_files()
        converted_new_items = [self._to_csv_item(item, idx + 1) for idx, item in enumerate(new_items)]
        self._write_new_data(converted_new_items)
        self._write_diff_file(converted_new_items, prev_items)
        self._write_missing_videos_file(converted_new_items, prev_items)

    def _get_latest_backup_data(self) -> list[_CSVPlaylistItem]:
        utils.log(f"Retrieving old {self._options.playlist_name} data")
        path = self._new_version_path
        if not os.path.exists(path):
            return []
        return self._get_data_from_file(path)

    @staticmethod
    def _get_data_from_file(file_path: str) -> list[_CSVPlaylistItem]:
        with open(file_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            # noinspection PyUnresolvedReferences
            return [_CSVPlaylistItem.from_dict(d) for d in reader]

    def _write_backup(self):
        utils.log("Creating backups")
        if os.path.exists(self._old_version_path):
            shutil.copyfile(self._old_version_path, self._old_version_backup_path)
        if os.path.exists(self._diff_file_path):
            shutil.copyfile(self._diff_file_path, self._diff_backup_path)
        if os.path.exists(self._missing_videos_path):
            shutil.copyfile(self._missing_videos_path, self._diff_backup_path)

    def _override_old_files(self):
        if os.path.isfile(self._new_version_path):
            shutil.copyfile(self._new_version_path, self._old_version_path)

    @staticmethod
    def _to_csv_item(item: PlaylistItem, position: int) -> _CSVPlaylistItem:
        return _CSVPlaylistItem(position=position,
                                id=item.snippet.resource_id.video_id,
                                published_at=item.snippet.published_at,
                                title=item.snippet.title,
                                channel_id=item.snippet.video_owner_channel_id,
                                channel_title=item.snippet.video_owner_channel_title,
                                )

    def _write_new_data(self, items: list[_CSVPlaylistItem]):
        utils.log(f"Writing new {self._options.playlist_name} titles to file")
        with open(self._new_version_path, "w", encoding="utf-8", newline='') as f:
            writer = self._dict_writer(f, _CSVPlaylistItem)
            for item in items:
                # noinspection PyUnresolvedReferences
                writer.writerow(item.to_dict())

    def _write_diff_file(self, new_items: list[_CSVPlaylistItem], prev_items: list[_CSVPlaylistItem]):
        utils.log("Writing diff file")
        prev_item_id_to_item: dict[str, _CSVPlaylistItem] = {item.id: item for item in prev_items}
        with open(self._diff_file_path, "w", encoding="utf-8", newline='') as f:
            # noinspection PyTypeChecker
            diff_writer = self._dict_writer(f, _CSVDiffItem)
            for i in range(len(new_items)):
                cur_item = new_items[i]
                prev_item = prev_item_id_to_item.get(cur_item.id)
                if prev_item and prev_item.title != cur_item.title:
                    # noinspection PyUnresolvedReferences
                    diff_writer.writerow(_CSVDiffItem(position=cur_item.position,
                                                      current_title=cur_item.title,
                                                      previous_title=prev_item.title,
                                                      channel_title=cur_item.channel_title).to_dict())

    def _write_missing_videos_file(self, new_items: list[_CSVPlaylistItem], prev_items: list[_CSVPlaylistItem]):
        utils.log("Writing missing videos file")
        cur_item_ids: set[str] = {item.id for item in new_items}
        with open(self._missing_videos_path, "w", encoding="utf-8", newline='') as f:
            missing_writer = self._dict_writer(f, _CSVPlaylistItem)
            for prev_item in prev_items:
                if prev_item.id not in cur_item_ids:
                    # noinspection PyUnresolvedReferences
                    missing_writer.writerow(prev_item.to_dict())

    @staticmethod
    def _dict_writer(f, clazz):
        writer = csv.DictWriter(f, [field.name for field in dataclasses.fields(clazz)])
        writer.writeheader()
        return writer
