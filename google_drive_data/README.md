# google_drive_data

google_drive_data is a simple Python package which is built based on
[PyDrive2](https://docs.iterative.ai/PyDrive2/) and allows basic file management on
Google Drive.

## Features of google_drive_data

The package contains the following features:

### 1. List all files on Google Drive

By default, the list contains all files from the "My Drive" directory.

Options:
- list files from any other folder on Google Drive
- include metadata, such as the file ID, the file link, or the file type

### 2. Upload a file to Google Drive

By default, the file gets uploaded to the "My Drive" directory.

Options:
- upload the file with a different name than the local one 
- upload a file into any other folder on Google Drive

### 3. Download a file from Google Drive

By default, the file gets downloaded from the "My Drive" directory. Drive Documents,
Drive Sheets or Drive Presentations will receive the appropriate suffix (.docx, .xlsx,
.pptx) automatically.

Options:
- download the file with a different name than the remote one
- download a file from any other folder on Google Drive

### 4. Remove a file from Google Drive

By default, the file gets removed from the "My Drive" directory.

Options:
- remove a file from any other a folder on Google Drive

## How to install

You can install google_drive_data with a regular pip command.

`$ pip install google_drive_data`

## Quickstart

1. Go to the [APIs Console](https://console.developers.google.com/iam-admin/projects)
   and make your own project.
2. Search for 'Google Drive API', select the entry, and click 'Enable'.
3. Select 'Credentials' from the left menu, click 'Create Credentials', select
   'OAuth client ID'.
4. Now, the product name and consent screen need to be set -> click
   'Configure consent screen' and follow the instructions. Once finished:
5. Select 'Application type' to be Web application.
6. Enter an appropriate name.
7. Input http://localhost:8080/ for 'Authorized redirect URIs'.
8. Click 'Create'.
9. Click 'Download JSON' on the right side of Client ID to download
   `client_secret_<really long ID>.json`.
10. The downloaded file has all authentication information of your application.
    Rename the file to `client_secrets.json` and place it in your working directory.
    
The `auth_dir` attribute you need to provide when instantiating `GoogleDriveData` class
must be the directory which contains the `client_secrets.json`. When you instantiate and
object of the `GoogleDriveData` class for the first time, you will see a web browser
asking you for authentication. Click 'Accept', and you are done with authentication.
This needs to be done only once.

Parts of the Quickstart documentation were taken from the
[PyDrive2 documentation](https://docs.iterative.ai/PyDrive2/quickstart/#authentication).

## Sample code

### Download a file from Google Drive:

Input:
````python
from google_drive_data.GoogleDriveData import GoogleDriveData
auth_dir = 'path_to_client_secrets'
drive = GoogleDriveData(auth_dir)
drive.download_file(file_name="file.csv")
````

Logged output:
````text
<TIMESTAMP> - INFO - Found file 'file.csv' in folder 'root' on Google Drive.
<TIMESTAMP> - INFO - Downloading 'file.csv' from Google Drive as 'file.csv'...
<TIMESTAMP> - INFO - Done.
````