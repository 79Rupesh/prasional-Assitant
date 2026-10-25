import os
import shutil
import subprocess

from core.interfaces.file_system import FileSystemProvider


class MacFileSystem(FileSystemProvider):

    def find(self, name: str) -> list:

        name = name.strip()

        if not name:
            return []

        results = []

        search_paths = [
            os.path.expanduser("~/Desktop"),
            os.path.expanduser("~/Documents"),
            os.path.expanduser("~/Downloads"),
        ]

        for search_path in search_paths:

            for root, directories, files in os.walk(search_path):

                for item in directories + files:

                    if name.lower() in item.lower():

                        results.append(
                            os.path.join(root, item)
                        )

        return results

    def list_directory(self, path: str) -> list:

        path = os.path.expanduser(path)

        if not os.path.isdir(path):
            return []

        return os.listdir(path)

    def open(self, path: str) -> str:

        path = os.path.expanduser(path)

        if not os.path.exists(path):
            return f"Path not found: {path}"

        subprocess.run(
            ["open", path],
            check=True
        )

        return f"Opened {path}"

    def get_info(self, path: str) -> dict:

        path = os.path.expanduser(path)

        if not os.path.exists(path):
            return {}

        stats = os.stat(path)

        return {
            "path": path,
            "name": os.path.basename(path),
            "is_file": os.path.isfile(path),
            "is_directory": os.path.isdir(path),
            "size": stats.st_size,
        }

    def create_file(self, path: str) -> str:

        path = os.path.expanduser(path)

        if os.path.exists(path):
            return f"Path already exists: {path}"

        parent = os.path.dirname(path)

        if parent and not os.path.exists(parent):
            os.makedirs(parent)

        with open(path, "w"):
            pass

        return f"Created file {path}"

    def create_folder(self, path: str) -> str:

        path = os.path.expanduser(path)

        if os.path.exists(path):
            return f"Path already exists: {path}"

        os.makedirs(path)

        return f"Created folder {path}"

    def rename(self, path: str, new_name: str) -> str:

        path = os.path.expanduser(path)

        if not os.path.exists(path):
            return f"Path not found: {path}"

        new_name = new_name.strip()

        if not new_name:
            return "New name cannot be empty."

        new_path = os.path.join(
            os.path.dirname(path),
            new_name
        )

        if os.path.exists(new_path):
            return f"Path already exists: {new_path}"

        os.rename(path, new_path)

        return f"Renamed to {new_name}"

    def move(self, source: str, destination: str) -> str:

        source = os.path.expanduser(source)
        destination = os.path.expanduser(destination)

        if not os.path.exists(source):
            return f"Source not found: {source}"

        if not os.path.exists(destination):
            return f"Destination not found: {destination}"

        shutil.move(source, destination)

        return f"Moved {source} to {destination}"

    def copy(self, source: str, destination: str) -> str:
        source = os.path.expanduser(source)
        destination = os.path.expanduser(destination)

        if not os.path.exists(source):
            return f"Source not found: {source}"
        if not os.path.isdir(destination):
            return f"Destination folder not found: {destination}"

        target = os.path.join(destination, os.path.basename(os.path.normpath(source)))
        if os.path.exists(target):
            return f"A file or folder already exists at {target}"

        try:
            if os.path.isdir(source):
                shutil.copytree(source, target)
            else:
                shutil.copy2(source, target)
        except OSError as error:
            return f"Unable to copy {source}: {error}"
        return f"Copied {source} to {target}"

    def delete(self, path: str) -> str:

        path = os.path.expanduser(path)

        if not os.path.exists(path):
            return f"Path not found: {path}"

        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)

        return f"Deleted {path}"
