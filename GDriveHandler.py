from io import BytesIO
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from googleapiclient.http import MediaIoBaseDownload
import os
import filecmp
from time import sleep


class GDriveHandler:
    def __init__(self, download_folder_name, latest_folder_name, timeout):
        self.gauth = GoogleAuth()
        self.drive = GoogleDrive(self.gauth)
        self
        self.download_folder_name = download_folder_name
        self.latest_folder_name = latest_folder_name
        self.timeout = timeout

        self.checkifFolderExists(download_folder_name)
        self.checkifFolderExists(latest_folder_name)
        return

    def checkifFolderExists(self, foldername):
        if os.path.isdir(foldername):
            return True
        elif os.path.isfile(foldername):
            raise ValueError("Specified path is a file")
        else:
            os.mkdir(foldername)

    def wait(self):
        sleep(self.timeout)

    def getAllFilesinFolder(self, folder_name):
        fileList = self.drive.ListFile(
            {'q': "'root' in parents and trashed=false"}).GetList()
        files = []
        for file in fileList:
            if(file['title'] == f"{folder_name}"):
                files.append(file['id'])
        return files

    def moveFile(self, filename, foldername):
        os.replace(filename, foldername)

    def downloadEveryFileinFolder(self, folder_name):
        file_list = self.drive.ListFile(
            {'q': "'root' in parents and trashed=false"}).GetList()
        for file1 in file_list:
            if file1['title'] == folder_name:
                folder_id = file1['id']
        file_list = self.drive.ListFile(
            {'q': "'{}' in parents and trashed=false".format(folder_id)}).GetList()
        for i, file1 in enumerate(sorted(file_list, key=lambda x: x['title']), start=1):
            file1.GetContentFile(
                f"./{self.download_folder_name}/{file1['title']}")

        if self.checklatest():
            self.moveTolatest()

    def checklatest(self):
        if not os.path.exists(self.latest_folder_name):
            os.mkdir(self.latest_folder_name) 
        files = os.listdir('./{}'.format(self.latest_folder_name))
        return (len(files) == 0)

    def moveTolatest(self):
        self.deleteAllFilesInDirectory(self.latest_folder_name)
        files = os.listdir(self.download_folder_name)
        for file in files:
            os.replace(f"./{self.download_folder_name}/{file}",
                       f"./{self.latest_folder_name}/{file}")

    def deleteAllFilesInDirectory(self, foldername):
        files = os.listdir(foldername)
        for file in files:
            os.remove(f"{foldername}/{file}")

    def checkifFileExists(self, filename):
        files = os.listdir(self.latest_folder_name)
        # print(files)
        for file in files:
            if file == filename:
                return False
        return True

    def differenceFromLatest(self):

        files = os.listdir(self.download_folder_name)
        for file in files:
            if self.checkifFileExists(file):
                if filecmp.cmp(f"./{self.download_folder_name}/{file}", f"./{self.latest_folder_name}/{file}", Shallow=False):
                    return False
            self.moveTolatest()
        
        return True
