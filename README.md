# Automating-File-Transfer


## Report
This project automates the process of transferring files from an external FTP server to a company's internal network. The script is scheduled to run daily and it writes  needed imformation about every execution in the log file.

## Customization
For customization you only need to change the parameters.yaml file. This file contains the next parameters:
+ FTP server
+ FTP Server directory's contents to copy
+ Local folder to which the files will be transfered initialy
+ Internal network folder to which the files will be transfered after all

Yaml file provides the ability to the user to change the parameters' values without stopping the execution of the script. In this way, the new parameters will be taken into considerartion in the next scheduled run.

## Before running the program you need to install (For Windows)
+ pip install pyyaml

## How to run
+ python '.\Automating File Transfer.py'
