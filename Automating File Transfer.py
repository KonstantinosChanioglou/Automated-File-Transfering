from ftplib import FTP
import os
import shutil
import yaml
import schedule
import time
import datetime


def transferFilesFromFTPServer(ftpServer, username, psw, distDirPathToCopy, localFolder):

    #Prepare writing to log File
    log = open("logs.txt", "a+") #create if not exists and append at the end
    log.write('['+ datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +'] ----- Next Run ----- ' + "\n")

    try:
        ftp = FTP(ftpServer)  # connect to host, default port - SELECT YOUR DESIRED FTP SERVER
        if(username == '' and psw == ''):
            login_status = ftp.login() # user='anonymous', passwd='anonymous@'
        else:
            login_status = ftp.login(user=username, passwd=psw) #if there is username and psw ftp.login(user='your_user', passwd='your_psw')  

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

    #if not exist create the folder
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
    
    quit_status = ftp.quit()

    #Write to Logs
    if(len(untrasferedFiles) > 0):
        log.write('['+ datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +'] ERROR: Files that did not transfered from FTP Server: ' + str(untrasferedFiles) + "\n")
    else:
        log.write('['+ datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +'] All files transfered succesfully' + "\n")
    log.write('['+ datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +'] ' + quit_status + ' Transfer process Completed!' + "\n")
    log.close()
    
    return True


def moveFilesToInternalNetwork(localFolder, internalNetworkDir):

    #if not exist create the folder
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

    #Write to Logs
    log = open("logs.txt", "a+") #create if not exists and append at the end
    if(len(unmovedFiles) > 0):
        log.write('['+ datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +'] ERROR: Files that did not moved to internal network from local directory:' + str(unmovedFiles) + "\n")
    else:
        log.write('['+ datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +'] All files moved to internal network succesfully' + "\n")
    log.close()
    

def automaticFileTransfer():
    args = {}
    with open('parameters.yaml') as f:
        args = yaml.load(f, Loader=yaml.FullLoader)

    #Reading arguments from yaml file does not require to run again the program after an argument is changed 
    everythingOk = transferFilesFromFTPServer(args['ftpServer'], args['usename'], args['psw'], args['distDirPathToCopy'], args['localFolder']) #transfer files from distDirPathToCopy to localFolder
    if everythingOk:
        moveFilesToInternalNetwork(args['localFolder'], args['internalNetworkDir']) #move files from localFolder to internalNetworkDir

def main():

    # Run daily at 08:00
    schedule.every().day.at("08:00").do(automaticFileTransfer)
    #schedule.every(30).seconds.do(automaticFileTransfer) #for testing

    # Loop so that the scheduling task keeps on running all time.
    while True:
        # Checks whether a scheduled task is pending to run or not
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
