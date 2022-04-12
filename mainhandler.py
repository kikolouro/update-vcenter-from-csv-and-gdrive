from time import sleep
from import_customAtributtes import import_customAtributtes
import threading

class mainHandler:
    def __init__(self):   
        pass

    def import_to_vcenter(self, senderdata, latests_folder_name):
        t = threading.Thread(target=import_customAtributtes, args=(latests_folder_name, senderdata)).start()