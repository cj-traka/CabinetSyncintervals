from distutils.cmd import Command
from fileinput import filename
from logging import root
import os
import re
import datetime
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import *

def extract_log_entries(log_file):
    log_entries = {}
    with open(log_file) as f:
        for line in f:
            if "Sending Announce to" in line:
                #Extract the Date, Time, Level, Sender and Message
                #use the split method to split the line into an array
                #The format of the line is:
                #{Date} {Time} {Level} {Sender} {Message}
                entry = line.split()
                #iterate through the array and store the Date, Time, and Message in a list
                date = ""
                time = ""
                message = ""
                for i in range(len(entry)):
                    if i == 0:
                        date = entry[i]
                    elif i == 1:
                        time = entry[i]
                    elif i == 2:
                        level = entry[i]
                    elif i == 3:
                        sender = entry[i]
                    else:
                        message += entry[i] + " "
                #extract the CabinetName and IP from the Message
                cabinet_details = extract_cabinet_details(message)
                #Store the Date, Time, and Cabinet Details in a hash
                log_entries[date + " " + time] = [cabinet_details]
    return log_entries

def extract_cabinet_details(line):
    cabinet_details = {}
    #use regex to extract the cabinet name, the name will start after the word "Sending Announce to" and end before the word "at" followed by the IP
    cabinet_name = re.search(r'Sending Announce to (.*) at', line).group(1)
    #add the cabinet name to the cabinet_details hash
    cabinet_details["CabinetName"] = cabinet_name
    cabinet_details["IP"] = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', line).group(0)
    return cabinet_details

def print_sync_details(log_entries):
    #retuns a multi line string containing the sync details
    #key + ": " + log_entries[key][0]["CabinetName"] + " at " + log_entries[key][0]["IP"]
    sync_details = ""
    for key in log_entries:
        sync_details += key + ": " + log_entries[key][0]["CabinetName"] + " at " + log_entries[key][0]["IP"] + "\n"
    return sync_details

#Write a method to measure the average time between syncs for each cabinet.
#Call the method average_sync_times.
def average_sync_times(log_entries):
    #Create a new hash to store the average sync times
    average_sync_times = {}
    #Create a new has to store the last saved sync time for each cabinet
    last_sync_times = {}
    #Iterate through the log entries
    for key in log_entries:
        #Extract the cabinet name and IP
        cabinet_details = log_entries[key][0]
        #If the cabinet name is not in the hash, add it
        if cabinet_details["CabinetName"] not in average_sync_times:
            average_sync_times[cabinet_details["CabinetName"]] = []
            #Add the cabinet and sync time to the last sync time hash
            last_sync_times[cabinet_details["CabinetName"]] = datetime.datetime.strptime(key, "%Y-%m-%d %H:%M:%S.%f")
        else:
            current_datetime = datetime.datetime.strptime(key, "%Y-%m-%d %H:%M:%S.%f")
            #last_sync as a datetime object
            last_sync = last_sync_times[cabinet_details["CabinetName"]]
            #Confirm last_sync is a date time object, otherwise convert it
            if not isinstance(last_sync, datetime.datetime):
                last_sync = datetime.datetime.strptime(last_sync, "%Y-%m-%d %H:%M:%S.%f")
            #Calculate the difference between the current sync time and the last sync time, use seconds
            difference = (current_datetime - last_sync).total_seconds()
            #Add the difference to the average sync times hash
            average_sync_times[cabinet_details["CabinetName"]].append(difference)
            #Update the last sync time to the current sync time
            last_sync_times[cabinet_details["CabinetName"]] = key
    #Iterate through the average sync times hash
    results = {}
    for key in average_sync_times:
        #Calculate the average sync time for each cabinet
        average_sync_times[key] = sum(average_sync_times[key]) / len(average_sync_times[key])
        results[key] = average_sync_times[key]
    return results

def print_average_sync_times(average_sync_times):
    #return a multi line string containing the average sync times
    #key + ": " + str(average_sync_times[key])
    average_sync_times_string = ""
    for key in average_sync_times:
        average_sync_times_string += key + ": " + str(average_sync_times[key]) + "\n"
    return average_sync_times_string


window = tk.Tk()
#Set the window title
window.title("Log File Parser")
window.resizable(False, False)
window.geometry("665x250")
#Create a scrollable text box
text = tk.Text(window, height=12)
#add scrollbar to the text box
scrollbar = tk.Scrollbar(window, command=text.yview)
text.configure(yscrollcommand=scrollbar.set)
text.grid(row=0, column=0, sticky='nsew')
def extract_syncs_from_file():
    filetypes = (('Log Files', 'Debugging_Log*.txt'), ('All files', '*'))
    log_file = fd.askopenfilename(
        title="Select a log file",
        initialdir="/",
        filetypes=filetypes
        )

    result = extract_log_entries(log_file)
    text.delete(1.0, tk.END)
    text.insert(1.0, print_sync_details(result))

def average_sync_times_file():
    filetypes = (('Log Files', 'Debugging_Log*.txt'), ('All files', '*'))
    log_file = fd.askopenfilename(
        title="Select a log file",
        initialdir="/",
        filetypes=filetypes
        )

    result = average_sync_times(extract_log_entries(log_file))
    text.delete(1.0, tk.END)
    text.insert(1.0, print_average_sync_times(result))
    

button = tk.Button(window,text ="Extract Sync Entries", command=extract_syncs_from_file)
#Create a button
button2 = tk.Button(window,text ="Average Sync Times", command=average_sync_times_file)
button.grid(row=1, column=0, sticky='nsew')
button2.grid(row=2, column=0, sticky='nsew')
#Create a scrollbar for the text box
scrollbar = tk.Scrollbar(window)
scrollbar.grid(row=0, column=1, sticky='nsew')
scrollbar.config(command=text.yview)
text.config(yscrollcommand=scrollbar.set)    
#Run the window
window.mainloop()
#End of program