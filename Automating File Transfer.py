''' You work at a company that receives daily data files from external partners. These files need to be processed and analyzed, but first, they need to be transferred to the company's internal network.

The goal of this project is to automate the process of transferring the files from an external FTP server to the company's internal network.

Here are the steps you can take to automate this process:

    DONE - Use the ftplib library to connect to the external FTP server and list the files in the directory.

    DONE - Use the os library to check for the existence of a local directory where the files will be stored.

    DONE - Use a for loop to iterate through the files on the FTP server and download them to the local directory using the ftplib.retrbinary() method.

    DONE/Question - Use the shutil library to move the files from the local directory to the internal network.

    Done -  Use the schedule library to schedule the script to run daily at a specific time.

    Done - You can also set up a log file to keep track of the files that have been transferred and any errors that may have occurred during the transfer process. '''




from ftplib import FTP
import os
import shutil
import yaml
import schedule
import time
import datetime

#pip install pyyaml


def transferFilesFromFTPServer(ftpServer, distDirPathToCopy, localFolder):

    #Prepare writing to log File
    log = open("logs.txt", "a+") #create if not exists 
    log.write('['+ datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +'] ----- Next Run ----- ' + "\n")

    try:
        ftp = FTP(ftpServer)  # connect to host, default port - SELECT YOUR DESIRED FTP SERVER
        login_status = ftp.login() # user='anonymous', passwd='anonymous@', if there is username and psw ftp.login(user='uor_user', passwd='your_psw')  
        log.write('['+ datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +'] ' + login_status + ' FTP Server: ' + ftpServer + "\n")
    except Exception as e:
        log.write('['+ datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +'] ERROR: Coudnt connect to FTP Server: '+ str(e) + "\n")
        return False

    try:
        change_dir_status = ftp.cwd(distDirPathToCopy)  # change into "debian" directory - SELECT YOUR DESIRED FOLDER TO DOWNLOAD ITS CONTENTS
        log.write('['+ datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +'] ' + change_dir_status + " Current folder: " + distDirPathToCopy + "\n")
    except Exception as e:
        log.write('['+ datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +'] ERROR: Coudnt go to the given directory: '+ str(e) + "\n")
        return False
    
    # ls_status = ftp.retrlines('LIST')  # It just lists the contents of a directory. It does to transfer smth. It Returns '226 Transfer complete' or '550 Failed to open file'
    # print(ls_status)

    if not os.path.exists(localFolder):
        os.mkdir(localFolder)


    untrasferedFiles = {}
    for filename in ftp.nlst(): #iterate all files in the current directory
        #Tranfer the files one by one
        try:
            with open(localFolder +'/'+filename, 'wb') as fp: #downloaded filename + path 
                ftp.retrbinary('RETR '+filename, fp.write) #file to download
        except Exception as e:
            untrasferedFiles[filename] = str(e)
            os.remove(localFolder +'/'+filename)

    #Write to Logs
    if(len(untrasferedFiles) > 0):
        log.write('['+ datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +'] ERROR: Files that did not transfered from FTP Server: ' + str(untrasferedFiles) + "\n")
    else:
        log.write('['+ datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +'] All files transfered succesfully' + "\n")

    quit_status = ftp.quit()
    log.write('['+ datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +']' + quit_status + ' Transfer process Completed!' + "\n")
    log.close()
    return True


def moveFilesToInternalNetwork(localFolder, internalNetworkDir):

    if not os.path.exists(internalNetworkDir):
        os.mkdir(internalNetworkDir)

    source_folder = localFolder
    destination_folder = internalNetworkDir
    unmovedFiles = list()

    # fetch all files
    for file_name in os.listdir(source_folder):

        # construct full file path
        source = source_folder + "/" +file_name
        destination = destination_folder + "/" + file_name

        # move only files
        if os.path.isfile(source):
            shutil.move(source, destination)
        else:
            unmovedFiles.append(file_name)

    #Prepare writing to log File
    log = open("logs.txt", "a+") #create if not exists 

    #Write to Logs
    if(len(unmovedFiles) > 0):
        log.write('['+ datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +'] ERROR: Files that did not moved to internal network from local directory:' + str(unmovedFiles) + "\n")
    else:
        log.write('['+ datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +'] All files moved to internal network succesfully' + "\n")

    log.close()

def automaticFileTransfer():
    args = {}
    with open('parameters.yaml') as f:
        args = yaml.load(f, Loader=yaml.FullLoader)

    #Reading arguments from yaml file does not require to run again the program after an argument changes 
    everythingOk = transferFilesFromFTPServer(args['ftpServer'], args['distDirPathToCopy'], args['localFolder']) #transfer files from distDirPathToCopy to localFolder
    if everythingOk:
        moveFilesToInternalNetwork(args['localFolder'], args['internalNetworkDir']) #move files from localFolder to internalNetworkDir

def main():

    # Run daily at 08:00
    schedule.every().day.at("08:00").do(automaticFileTransfer)

    # Loop so that the scheduling task keeps on running all time.
    while True:
        # Checks whether a scheduled task is pending to run or not
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()