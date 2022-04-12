from GDriveHandler import GDriveHandler
from decouple import config
from mainhandler import mainHandler
gdrive = GDriveHandler('Downloads', 'Latest', 60 * 60)
mhandler = mainHandler()
def main():
    while True:
        gdrive.downloadEveryFileinFolder("Teste")
        if gdrive.differenceFromLatest():
            mhandler.import_to_vcenter({"email": config('SENDER_EMAIL'), "password": config('SENDER_PASSWORD')}, gdrive.latest_folder_name)    
        gdrive.wait()
if __name__ == "__main__":
    main()