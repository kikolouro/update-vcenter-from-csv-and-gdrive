from pyVim.connect import SmartConnectNoSSL
from pyVmomi import vim
import csv
import os
from tqdm import tqdm
from decouple import config
import datetime
import pytz
from sendemail import sendEmailwithAttachment
csvdata = []


def main():
    user = config('VCENTERUSER')
    password = config('VCENTERPW')
    blacklist = [
        'ISServicedesk01_LAB',
        'ISServicedesk03',
        'ISServicedesk02',
        'TEMPTESTE',
        'TestMDAG',
        'ADLAB',
        'PartitioningTest',
        'Windows 10 Testes',
        'TESTTERRAFORM',
        'ISFWHQTESTE',
        'LABGPORestrictions',
        'Windows Server 2019',
        'JiraTesting',
        'LinuxHardenedRepositoryLab',
        'SOPHOSTestWAF'
    ]
    si = SmartConnectNoSSL(host=config('VCENTERHOST'),
                           user=user,
                           pwd=password,
                           port=443)
    content = si.RetrieveContent()
    objView = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    vmList = objView.view
    objView.Destroy()
    cfm = si.content.customFieldsManager
    timezone = pytz.timezone("Europe/Lisbon")
    date = datetime.datetime.now(
        tz=timezone).strftime("%d-%m-%Y")
    with open(f'VMList-{date}.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'VMName',
            'VMState',
            'TotalCPU',
            'CPUShare',
            'TotalMemory',
            'Datastore',
            'UsedSpaceGB',
            'ProvisionedSpaceGB',
            'Company',
            'Owner',
            'Product',
            'Eliminar?'])
        warnings = []
        for vm in tqdm(vmList):

            if vm.name not in blacklist:
                data = []
                data.append(vm.name)
                data.append(vm.summary.runtime.powerState)
                data.append(vm.summary.config.numCpu)
                data.append(vm.summary.config.cpuReservation)
                data.append(vm.summary.config.memorySizeMB)
                data.append(vm.datastore[0].name)
                # bytes to gigabytes

                #print(vm.name, vm.summary.vm.guest.disk.freeSpace / 1024 / 1024 / 1024 , vm.summary.vm.guest.disk.capacity / 1024 / 1024 / 1024)
                data.append(round((vm.summary.storage.committed) / 1024 / 1024 / 1024, 2))
                data.append(round((vm.summary.storage.uncommitted) / 1024 / 1024 / 1024, 2))
                
                #data.append(vm.datastore[0].summary.capacity / 1024 / 1024 / 1024)
                #print(vm.summary.storage)
                customvalue = vm.customValue
                fields = si.content.customFieldsManager.field
                for field in fields:
                    for cv in customvalue:
                        if cv.key == field.key and field.name == 'Company':
                            data.append(cv.value)
                        elif cv.key == field.key and field.name == 'Owner':
                            data.append(cv.value)
                        elif cv.key == field.key and field.name == 'Product':
                            data.append(cv.value)
                        elif field.name == 'Company' or field.name == 'Owner' or field.name == 'Product':
                            warnings.append(f"[!] - {vm.name} has no {field.name}!")

                data.append('')
                writer.writerow(data)
    sendEmailwithAttachment('servicedesk@infosistema.com', {'email': config('SENDER_EMAIL'), 'password': config('SENDER_PASSWORD')}, f'VMList-{date}.csv'.format(date=date), warnings)
if __name__ == '__main__':
    main()