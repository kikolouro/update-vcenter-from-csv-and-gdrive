from pyVim.connect import SmartConnectNoSSL
from pyVmomi import vim, vmodl
from getpass import getpass
import csv
import os
from tqdm import tqdm
from decouple import config
import datetime
import pytz
from decouple import config
from sendemail import sendEmail
import logging

logging.basicConfig(filename=f"./logs/import.log",
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filemode='a', level=logging.INFO)

csvdata = []


def import_customAtributtes(latests_folder_name, senderdata):
    infos = []
    for file in os.listdir(latests_folder_name):
        if file.endswith(".csv"):
            csvdata.append(os.path.join(f"{latests_folder_name}/", file))

    if len(csvdata) > 1:
        infos.append("[!] - Please only provide one CSV file")
        exit()
    else:
        infos.append("[+] - Using CSV file: " + csvdata[0])

    user = config('VCENTERUSER')
    password = config('VCENTERPW')
    si = SmartConnectNoSSL(host=config('VCENTERHOST'),
                           user=user,
                           pwd=password,
                           port=443)

    content = si.RetrieveContent()
    objView = content.viewManager.CreateContainerView(
        content.rootFolder, [vim.VirtualMachine], True)
    vmList = objView.view
    objView.Destroy()
    cfm = si.content.customFieldsManager

    with open(csvdata[0], 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        pbar = tqdm(list(reader))
        count = 0
        for row in pbar:
            pbar.set_description("Processing %s" % row['VMName'])
            logging.info(
                f"[row] - {row['VMName']} | {row['Owner']} | {row['Product']} | {row['Company']}")

            for vm in vmList:

                if vm.name.lower() == row['VMName'].lower():
                    logging.info(f"[{vm.name.lower()}] - Processing")
                    if 'Shutdown' in row:
                        if vm.summary.runtime.powerState == "poweredOn" and row['Shutdown'] == "Sim":
                            infos.append(f"[!] - {vm.name} Must be shutdown")
                            logging.info(
                                f"[{vm.name.lower()}] - Must be shutdown")

                        # vm.ShutdownGuest()
                    customvalue = vm.customValue
                    logging.info(
                        f"[{vm.name.lower()}] - Custom Value: {customvalue}")
                    fields = si.content.customFieldsManager.field
                    for field in fields:
                        logging.info(
                            f"[{vm.name.lower()}] - Current field: {field.key}")

                        if hasattr(field, 'value'):
                            logging.info(
                                f"[field] - {field.key} -> {field.value}")
                        else:
                            logging.info(f"[field] - {field.key}")

                            logging.info(
                                f'[{vm.name.lower()}] - Matched field with customfield {field.name}')
                            if field.name == 'Owner' and 'Owner' in row:
                                logging.info(
                                    f"[{vm.name.lower()}] - Setting field to: {row['Owner']}")

                                cfm.SetField(entity=vm, key=field.key,
                                             value=row['Owner'])
                                infos.append(
                                    f"[+] - {vm.name} Owner set to {row['Owner']}")

                            elif field.name == 'Product' and 'Product' in row:
                                logging.info(
                                    f"[{vm.name.lower()}] - Setting field to: {row['Product']}")
                                cfm.SetField(entity=vm, key=field.key,
                                             value=row['Product'])
                                infos.append(
                                    f"[+] - {vm.name} Product set to {row['Product']}")

                            elif field.name == 'Company' and 'Company' in row:

                                logging.info(
                                    f"[{vm.name.lower()}] - Setting field to: {row['Company']}")

                                cfm.SetField(entity=vm, key=field.key,
                                             value=row['Company'])
                                infos.append(
                                    f"[+] - {vm.name} Company set to {row['Company']}")
                            count += 1
                            logging.info(
                                f'[count] - Incrementing count to {count}')
    data = {"logs": []}
    for info in infos:
        data["logs"].append(info)
    timezone = pytz.timezone("Europe/Lisbon")
    data['datetime'] = datetime.datetime.now(
        tz=timezone).strftime("%d/%m/%Y %H:%M:%S")
    print(count)
    sendEmail(receiver=config('RECIPIENT'), senderdata=senderdata, data=data)
    csvdata.clear()


if __name__ == '__main__':
    import_customAtributtes(
        "./", {"email": config('SENDER_EMAIL'), "password": config('SENDER_PASSWORD')})
