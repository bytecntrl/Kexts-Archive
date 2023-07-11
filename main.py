import io
import json
import zipfile
import shutil

import requests

GITHUB_API = "https://api.github.com/repos"


def extract_kext_from_zip(zip_data: io.BytesIO, name: str) -> bool:
    with zipfile.ZipFile(zip_data, "r") as zip_ref:
        zip_members = zip_ref.namelist()
        folder_members = [
            member
            for member in zip_members
            if member.startswith(f"{name}.kext/")
        ]

        for member in folder_members:
            zip_ref.extract(member, "tmp")

        return bool(folder_members)


def main():
    with open("kext.json", "r") as f:
        data = json.load(f)

    for kext in data:
        name = kext["name"]
        owner = kext["owner"]
        repo = kext["repo"]

        response = requests.get(f"{GITHUB_API}/{owner}/{repo}/releases/latest")

        if response.status_code != 200:
            continue

        download_url = [
            x["browser_download_url"]
            for x in response.json()["assets"]
            if "RELEASE" in x["name"]
        ][0]

        zip_response = requests.get(download_url)
        if zip_response.status_code != 200:
            continue

        kext_data = extract_kext_from_zip(
            io.BytesIO(zip_response.content), name
        )

        if kext_data:
            shutil.move(f"tmp/{name}.kext", f"kext/{name}.kext")


if __name__ == "__main__":
    main()
