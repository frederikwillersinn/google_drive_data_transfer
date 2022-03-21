import logging
import os
import pathlib
from typing import Union

import pydrive2
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


class GoogleDriveDataTransfer:
    def __init__(self, auth_dir: Union[str, pathlib.Path]) -> None:
        """
        Creates an instance of the class.

        :param auth_dir: directory with Google Drive client secrets
        """
        self.auth_dir = auth_dir
        self.drive = self.authenticate()
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self.logger = logging.getLogger()

    def authenticate(self) -> pydrive2.drive.GoogleDrive:
        """
        Accesses the Google Drive client secrets and authenticates the user on Google
        Drive. This approach requires identification the first time and then not again.

        :return: authenticated instance of the class
        """
        gauth = GoogleAuth()
        gauth.LoadCredentialsFile(os.path.join(self.auth_dir, "mycreds.txt"))
        if gauth.credentials is None:  # Authenticate if they're not there
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:  # Refresh them if expired
            gauth.Refresh()
        else:  # Initialize the saved creds
            gauth.Authorize()
        gauth.SaveCredentialsFile(os.path.join(self.auth_dir, "mycreds.txt"))
        drive = GoogleDrive(gauth)
        return drive

    def list_files(
        self,
        drive_folder_id: str = None,
        shared_with_me: bool = False,
        include_metadata: bool = False,
    ) -> list:
        """
        Returns a list with files on Google Drive sorted by the date of creation in
        descending order. The ID of a Google Drive folder can be extracted from the URL.

        :param drive_folder_id: ID of the Google Drive folder to list files from (optional)
        :param shared_with_me: whether or not to list files from "Shared with me" directory (optional)
        :param include_metadata: whether or not to include metadata such as file ID, link, type
        :return: list of files on Google Drive
        """
        if shared_with_me:
            file_list = self.drive.ListFile(
                {"q": "sharedWithMe and trashed=false", "orderBy": "createdDate desc"}
            ).GetList()
        else:
            drive_folder_id = drive_folder_id if drive_folder_id else "root"
            file_list = self.drive.ListFile(
                {
                    "q": f"'{drive_folder_id}' in parents and trashed=false",
                    "orderBy": "createdDate desc",
                }
            ).GetList()
        file_list = file_list if include_metadata else [f["title"] for f in file_list]
        return file_list

    def upload_file(
        self,
        file_name: str,
        data_dir: str = os.getcwd(),
        remote_file_name: str = None,
        drive_folder_id: str = None,
    ) -> None:
        """
        Uploads a file to Google Drive. By default, the file gets uploaded to the
        "My Drive" directory. The ID of a Google Drive folder can be extracted from
        the URL.

        :param file_name: local name of the file to upload
        :param data_dir: directory which contains the file to upload
        :param remote_file_name: remote file name, uses local file name by default (optional)
        :param drive_folder_id: ID of the Google Drive folder to upload to (optional)
        :return: None
        """
        file_list = self.list_files(
            drive_folder_id=drive_folder_id, include_metadata=True
        )

        remote_file_name = remote_file_name if remote_file_name else file_name
        drive_folder_id = drive_folder_id if drive_folder_id else "root"

        # File does not exist yet
        if remote_file_name not in [f["title"] for f in file_list]:
            file_of_interest = self.drive.CreateFile(
                {
                    "title": remote_file_name,
                    "parents": [{"id": drive_folder_id}],
                }
            )
            self.logger.info(
                f"Created file '{remote_file_name}' in folder '{drive_folder_id}' on Google Drive..."
            )
        # File already exists
        else:
            for file in file_list:
                if file["title"] == remote_file_name:
                    logging.info(
                        f"Found file '{remote_file_name}' in folder '{drive_folder_id}' on Google Drive..."
                    )
                    file_of_interest = file
                    break  # Stops searching after file was found

        self.logger.info(f"Uploading '{file_name}' to Google Drive...")
        file_of_interest.SetContentFile(os.path.join(data_dir, file_name))
        file_of_interest.Upload()
        self.logger.info("Done.")

    def download_file(
        self,
        file_name: str,
        data_dir: str = os.getcwd(),
        local_file_name: str = None,
        drive_folder_id: str = None,
        shared_with_me: bool = False,
    ) -> None:
        """
        Downloads a file from Google Drive. By default, the file gets downloaded from
        the "My Drive" directory. The ID of a Google Drive folder can be extracted from
        the URL. Drive Documents, Drive Sheets or Drive Presentations will receive the
        appropriate suffix (.docx, .xlsx, .pptx) automatically. If multiple files with
        the given name exist, the most recently created one will be downloaded.

        :param file_name: Google Drive name of the file to download
        :param data_dir: directory which contains the file to download
        :param local_file_name: local file name, uses Google Drive file name by default (optional)
        :param drive_folder_id: ID of the Google Drive folder to download from (optional)
        :param shared_with_me: whether or not to download from the "Shared with me" directory (optional)
        :return: None
        """
        file_list = self.list_files(
            drive_folder_id=drive_folder_id,
            shared_with_me=shared_with_me,
            include_metadata=True,
        )

        local_file_name = local_file_name if local_file_name else file_name
        drive_folder_id = drive_folder_id if drive_folder_id else "root"

        if file_name not in [f["title"] for f in file_list]:
            raise FileNotFoundError(
                f"Could not find file '{file_name}' in folder '{drive_folder_id}' on Google Drive."
            )
        else:
            for file in file_list:
                if file["title"] == file_name:
                    self.logger.info(
                        f"Found file '{file_name}' in folder '{drive_folder_id}' on Google Drive."
                    )
                    file_of_interest = file
                    break  # Stops searching after file was found

            mimetypes = {
                "application/vnd.google-apps.document": {
                    "convert_to": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    "file_suffix": ".docx",
                },  # Drive Document as .docx
                "application/vnd.google-apps.spreadsheet": {
                    "convert_to": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "file_suffix": ".xlsx",
                },  # Drive Sheets as .xlsx
                "application/vnd.google-apps.presentation": {
                    "convert_to": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    "file_suffix": ".pptx",
                },  # Drive Presentation as .pptx
            }
            mimetype = None
            if file_of_interest["mimeType"] in mimetypes.keys():
                mimetype = mimetypes[file_of_interest["mimeType"]]["convert_to"]
                file_suffix = mimetypes[file_of_interest["mimeType"]]["file_suffix"]
                local_file_name = local_file_name + file_suffix

            self.logger.info(
                f"Downloading '{file_name}' from Google Drive as '{local_file_name}'..."
            )
            file_of_interest.GetContentFile(
                os.path.join(data_dir, local_file_name), mimetype=mimetype
            )
            logging.info("Done.")

    def remove_file(self, file_name: str, drive_folder_id: str = None) -> None:
        """
        Removes a file from Google Drive. By default, the file gets removed from the
        "My Drive" directory. The ID of a Google Drive folder can be extracted from the
        URL. If multiple files with the given name exist, the most recently created one
        will be removed.

        :param file_name: Google Drive name of the file to remove
        :param drive_folder_id: ID of the Google Drive folder to remove from (optional)
        :return: None
        """
        drive_folder_id = drive_folder_id if drive_folder_id else "root"
        file_list = self.list_files(
            drive_folder_id=drive_folder_id, include_metadata=True
        )

        if file_name not in [f["title"] for f in file_list]:
            raise FileNotFoundError(
                f"Could not find file '{file_name}' in folder '{drive_folder_id}' on Google Drive."
            )
        else:
            for file in file_list:
                if file["title"] == file_name:
                    self.logger.info(
                        f"Found file '{file_name}' in folder '{drive_folder_id}' on Google Drive."
                    )
                    file_of_interest = file
                    break  # Stops searching after first file with the was found

            self.logger.info(f"Deleting '{file_name}' from Google Drive...")
            file_of_interest.Trash()
            self.logger.info("Done.")
