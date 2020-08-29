''' 
program parses the output of the PowerShell script, creating a new folder (directory)
with a CSV file containing six columns, a CSV containig twelve columns, and a text file 
including information about the servers and their versions

    Directory structure:
        current_directory
        |   
        |
        |____unique_time_directory
            |   csvfilename1
            |   csvfilename2
            |   txtfilename

    CSV file 1: (includes all servers scanned)
    (1)server name
    (2)whether query ran or not (only runs if there is MSSQL on the server)
    if it ran:
        (3)SQL Edition
        (4)SQL Product Version
        (5)SQL Product Level
    (6)notes (warnings,etc.)
    
    CSV file 2: (only includes the servers scanned that had MSSQL)
    (1)server name
    (2)whether query ran or not
    if it ran:
        (3)SQL Edition
        (4)SQL Product Version
        (5)SQL Product Level
        (6)Current Version's Release Date
        (7)if the last update is no more than 2 months old
        (8)Update Available
        (9)Last Update's Release Date
        (10)Security Updated Needed (still working on it)
        (11)New Service Pack Available
    (12)notes (warnings,etc.)
    
    Text file:
    ~ from initial parsing of the text file created by running the PowerShell script ~
    Number of servers scanned
    Number of servers with SQL
    Number of servers without SQL
    Number of servers did not run query at all
    Number of servers that gave WARNING
    ~ from getting version information for the second CSV file ~
    Number of servers with uninstalled updates that are between 6 months and 1 year old
    Number of servers with uninstalled updates that are between 1 year and 2 years old
    Number of servers with uninstalled updates that are more than 2 years old
    Number of servers with an out-of-date service pack
    Versions of Microsoft SQL Server that the servers had (like 2012, 2014, 2016)
        
'''

def main():

    import pandas as pd

    import csv

    import re
    product_version_regex = re.compile("[0-9\.]+")
    product_level_regex = re.compile("[0-9A-Z]{2,5}")
    

    # to ensure unique directory and file names for every execution of this parsing program
    from datetime import datetime
    time = datetime.now()
    # directory name
    time_directory = time.strftime("%m-%d-%Y-%H-%M-%S") 
    # filename
    csvname = 'allScannedServers.csv'
    txtname = 'SQLVersionOutputStats.txt'

    from os.path import expanduser
    home = expanduser("~")

    # make a new folder for the csv file and txt file
    import os
    #this is the directory the folder will be made in
    current_directory = home
    final_directory = os.path.join(current_directory,time_directory)
    
    # change "time_directory" to "test_directory" or something for testing to avoid making many directories
    final_directory = os.path.join(current_directory,time_directory) 
    
    if not os.path.exists(final_directory): 
       os.makedirs(final_directory)

    # change the directory so txt and csv files are created in it
    os.chdir(final_directory)

    # change csvname to constant like "csvfile.csv" or something when testing/debugging to avoid many different files
    with open(csvname,'w') as file: 

        try:
            # open PowerShell script output in the directory where it is
            os.chdir(home)
            with open('txtfileupdate4.txt', 'r') as reader:

                # change back to new directory
                os.chdir(final_directory)

                # Header of CSV File
                file.write('Server,Did SQL Query Run?,Edition,Product Version,Product Level,Curr_Version Release Date,')
                file.write('Updates Current Within Two Months,Update Available,Last Update Release Date,')
                file.write('Security Update Needed,New Service Pack Available,Other')
                file.write('\n')

                # the line with the server name always contains a 1 and a 0 separated by a tab
                contains_server_name = "1	0"

                # counters for the text file statistics
                server_count = 0
                has_sql_count = 0
                not_with_sql_count = 0
                gave_warning = 0
                didnot_run = 0

                for line in reader:

                    # server name
                    if line.find(contains_server_name) != -1:
                        server_name = line.split()[0]
                        file.write(server_name + ",")
                        server_count = server_count + 1
                        # sometimes PowerShell script will fail entirely, and 
                        # there will not even be "Did SQL Query Run?" output
                        if line.find("[") == -1: 
                            file.write('Blank output - issue running query')
                            file.write('\n')
                            didnot_run += 1

                    # checks if SQL is installed on server (will display True or False, or that there was an issue running query)
                    if line.find("Did SQL Query Run?") != -1:
                        if line.find("True") != -1:
                            file.write("True,") 
                            has_sql_count += 1
                        # if false, might not have SQL, OR there could have been an error when querying
                        if line.find("False") != -1:
                            not_with_sql_count += 1
                            if line.find("WARNING") != -1:
                                file.write("False,,,,,,,,,,")
                                # print the WARNING in the "other" column of csv file
                                warning = ""
                                temp = ""
                                for char in line:
                                    if temp.find(contains_server_name) != -1 and char != '[':
                                        warning = warning + char
                                    elif char == '[':
                                        break
                                    else: 
                                        temp = temp + char
                                warning = warning.strip() # remove whitespace from the warning
                                file.write(warning)
                                file.write('\n')
                                gave_warning += 1
                            else:
                                file.write("False")
                                file.write('\n')

                    # SQL Edition (like "Enterprise Edition: Core-based Licensing (64-bit)" or "Standard Edition (64-bit)")
                    if line.find('"Result": "') != -1 and line.find("Edition") != -1 and line.find(contains_server_name) == -1:
                        temp_2 = ""
                        edition = ""
                        for char in line:
                            if temp_2.find('"Result": "') == -1:
                                temp_2 = temp_2 + char
                            elif temp_2.find('"Result": "') != -1:
                                if char == "\"":
                                    break
                                edition = edition + char
                        file.write(edition + ',')
                        continue

                    # SQL Product Version (like "11.0.7493.4")
                    if line.find('"Result": "') != -1 and line.find(contains_server_name) == -1:
                        temp_3 = ""
                        version = ""
                        for char in line:
                            if temp_3.find('"Result": "') == -1:
                                temp_3 = temp_3 + char
                            elif temp_3.find('"Result": "') != -1:
                                if char == "\"":
                                    break
                                version = version + char
                        if product_version_regex.match(version):
                            file.write(version + ",")
                            continue

                    # SQL Product Level (like "SP2" or "RTM")
                    if line.find('"Result": "') != -1 and line.find(contains_server_name) == -1:
                        temp_4 = ""
                        level = ""
                        for char in line:
                            if temp_4.find('"Result": "') == -1:
                                temp_4 = temp_4 + char
                            elif temp_4.find('"Result": "') != -1:
                                if char == "\"":
                                    break
                                level = level + char
                        if product_level_regex.match(level):
                            file.write(level)
                            file.write('\n')
                            continue

        except FileNotFoundError:
            print("File does not exist - maybe you are in the wrong directory? See what print(os.getcwd()) gives you.", end=' ')
            print("You need to be in the same directory as the output from the PowerShell script that you got from SCCM.")

    # create dataframe from the csv file
    df1 = pd.read_csv(csvname)
 
    # getting product version to load appropriate website into dataframe
    sqlserver6_5regex = re.compile("^6.50.")
    sqlserver7_0regex = re.compile("^7.0.")
    sqlserver2000regex = re.compile("^8.0.")
    sqlserver2005regex = re.compile("^9.0.")
    sqlserver2008regex = re.compile("^10.0.")
    sqlserver2008_R2regex = re.compile("^10.50.")
    sqlserver2012regex = re.compile("^11.0.")
    sqlserver2014regex = re.compile("^12.0.")
    sqlserver2016regex = re.compile("^13.0.")
    sqlserver2017regex = re.compile("^14.0.")
    sqlserver2019regex = re.compile("^15.0.")
    
    # make for loop below faster, don't create same dataframe again if it's already been created
    s6_5 = False
    s7_0 = False
    s2000 = False
    s2005 = False
    s2008 = False
    s2008R2 = False
    s2012 = False
    s2014 = False
    s2016 = False
    s2017 = False
    s2019 = False
    
    # print list of versions in the text file
    versions_list = []
    # dictionary (map) that will store a SQL version (like 2019, 2017, or 6_5) and the most recent update date for that version
    update_dict = {}
    # map storing SQL version and corresponding highest Service Pack available (only applicable to pre-2017 SQL versions)
    sp_dict = {}
    
    # if this process is slow, you can put the SQL versions you have more of towards the top of this for loop
    # for example, if you have a lot of SQL Server 2016 servers, put that elif block right after the if statement
    for pversion in df1['Product Version']:
        pversion = str(pversion)
        if pversion == "nan": # server doesn't have SQL on it :)
            continue
        elif sqlserver2019regex.match(pversion):
            if s2019 == True:
                continue
            else:
                versions_list.append('2019')
                sqlserver2019_webpage = 'https://sqlserverbuilds.blogspot.com/2019/01/sql-server-2019-versions.html'
                df2019 = pd.read_html(sqlserver2019_webpage)[0]
                s2019 = True
                update_dict['2019'] = recent_release(df2019)
        elif sqlserver2017regex.match(pversion):
            if s2017 == True:
                continue
            else:
                versions_list.append('2017')
                sqlserver2017_webpage = 'https://sqlserverbuilds.blogspot.com/2017/01/sql-server-2017-versions.html'
                df2017 = pd.read_html(sqlserver2017_webpage)[0]
                s2017 = True
                update_dict['2017'] = recent_release(df2017)
        elif sqlserver2016regex.match(pversion):
            if s2016 == True:
                continue
            else:
                versions_list.append('2016')
                sqlserver2016_webpage = 'https://sqlserverbuilds.blogspot.com/2016/01/sql-server-2016-versions.html'
                df2016 = pd.read_html(sqlserver2016_webpage)[0]
                s2016 = True
                update_dict['2016'] = recent_release(df2016)
                sp_dict['2016'] = highest_sp(df2016)
        elif sqlserver2014regex.match(pversion):
            if s2014 == True:
                continue
            else:
                versions_list.append('2014')
                sqlserver2014_webpage = 'https://sqlserverbuilds.blogspot.com/2014/01/sql-server-2014-versions.html'
                df2014 = pd.read_html(sqlserver2014_webpage)[0]
                s2014 = True
                update_dict['2014'] = recent_release(df2014)
                sp_dict['2014'] = highest_sp(df2014)
        elif sqlserver2012regex.match(pversion):
            if s2012 == True:
                continue
            else:
                versions_list.append('2012')
                sqlserver2012_webpage = 'https://sqlserverbuilds.blogspot.com/2012/01/sql-server-2012-versions.html'
                df2012 = pd.read_html(sqlserver2012_webpage)[0]
                s2012 = True
                update_dict['2012'] = recent_release(df2012)
                sp_dict['2012'] = highest_sp(df2012)
        elif sqlserver2008_R2regex.match(pversion):
            if s2008R2 == True:
                continue
            else:
                versions_list.append('2008R2')
                sqlserver2008R2_webpage = 'https://sqlserverbuilds.blogspot.com/2008/05/sql-server-2008-r2-versions.html'
                df2008R2 = pd.read_html(sqlserver2008R2_webpage)[0]
                s2008R2 = True
                update_dict['2008R2'] = recent_release(df2008R2)
                sp_dict['2008R2'] = highest_sp(df2008R2)
        elif sqlserver2008regex.match(pversion):
            if s2008 == True:
                continue
            else:
                versions_list.append('2008')
                sqlserver2008_webpage = 'https://sqlserverbuilds.blogspot.com/2008/01/sql-server-2008-versions.html'
                df2008 = pd.read_html(sqlserver2008_webpage)[0]
                s2008 = True
                update_dict['2008'] = recent_release(df2008)
                sp_dict['2008'] = highest_sp(df2008)
        elif sqlserver2005regex.match(pversion):
            if s2005 == True:
                continue
            else:
                versions_list.append('2005')
                sqlserver2005_webpage = 'https://sqlserverbuilds.blogspot.com/2005/01/sql-server-2005-versions.html'
                df2005 = pd.read_html(sqlserver2005_webpage)[0]
                s2005 = True
                update_dict['2005'] = recent_release(df2005)
                sp_dict['2005'] = highest_sp(df2005)
        elif sqlserver2000regex.match(pversion):
            if s2000 == True:
                continue
            else:
                versions_list.append('2000')
                sqlserver2000_webpage = 'https://sqlserverbuilds.blogspot.com/2000/01/sql-server-2000-versions.html'
                df2000 = pd.read_html(sqlserver2000_webpage)[0]
                s2000 = True
                update_dict['2000'] = recent_release(df2000)
                sp_dict['2000'] = highest_sp(df2000)
        elif sqlserver7_0regex.match(pversion):
            if s7_0 == True:
                continue
            else:
                versions_list.append('7_0')
                sqlserver7_0_webpage = 'https://sqlserverbuilds.blogspot.com/2007/01/sql-server-7.html'
                df7_0 = pd.read_html(sqlserver7_0_webpage)[0]
                s7_0 = True
                update_dict['7_0'] = recent_release(df7_0)
                sp_dict['7_0'] = highest_sp(df7_0)
        elif sqlserver6_5regex.match(pversion):
            if s6_5 == True:
                continue
            else:
                versions_list.append('6_5')
                sqlserver6_5_webpage = 'https://sqlserverbuilds.blogspot.com/2006/05/sql-server-6-5.html'
                df6_5 = pd.read_html(sqlserver6_5_webpage)[0]
                s6_5 = True
                update_dict['6_5'] = '5a' # just hard-coding it, it's never going to change again
        else:
            print('Something went wrong. SQL version "' + pversion + '" did not match a regular expression that lists a webpage for that version.', end='')
            print('At the time this program was written, it covered SQL Server versions 6.5 (6.50.___) through 2019 (15.0.____.__)', end='')
            print('If your version is out of that range, go to https://sqlserverbuilds.blogspot.com and add that page to be supported by this program.')
            
    
    
    # get version information about each instance of SQL Server on the servers in the csv file
    
    csv_row_counter = -1
        
    with open(csvname,'r') as parsed_csv: # read and write to the file
        
        # skip the line with the headers in the csv file
        first_line = parsed_csv.readline()
        
        # more counters for text file statistics
        outofdate_sp = 0
        notupdatedin6mon= 0
        notupdatedin1year = 0
        notupdatedin2years = 0
        twomonthsout = 0
        
        # new csv file that we will write to 
        with open('serversWithMSSQL.csv','w+') as finalcsv:
            
            finalcsv.write(first_line) 
       
            # iterate through the parsed csv file and its dataframe
            for p_version,csv_line in zip(df1['Product Version'],parsed_csv):
                
                # remove trailing newline from csv_line
                csv_line = csv_line.rstrip('\n')

                product_version = str(p_version)
                csv_row_counter += 1

                if product_version == "nan": # server doesn't have SQL on it :)
                    continue

                # 2019, 2017, 6_5, etc
                release_type = ""

                
                
                # (6) current version's date
                # use curr_dataframe as the dataframe that corresponds to the webpage representing the product_version (like 14.0.3294.2)  
                if sqlserver2019regex.match(product_version):
                    curr_dataframe = df2019
                    release_type = '2019'
                elif sqlserver2017regex.match(product_version):
                    curr_dataframe = df2017
                    release_type = '2017'
                elif sqlserver2016regex.match(product_version):
                    curr_dataframe = df2016  
                    release_type = '2016'
                elif sqlserver2014regex.match(product_version):
                    curr_dataframe = df2014
                    release_type = '2014'
                elif sqlserver2012regex.match(product_version):
                    curr_dataframe = df2012
                    release_type = '2012'
                elif sqlserver2008_R2regex.match(product_version):
                    curr_dataframe = df2008R2
                    release_type = '2008R2'
                elif sqlserver2008regex.match(product_version):
                    curr_dataframe = df2008
                    release_type = '2008'
                elif sqlserver2005regex.match(product_version):
                    curr_dataframe = df2005
                    release_type = '2005'
                elif sqlserver2000regex.match(product_version):
                    curr_dataframe = df2000
                    release_type = '2000'
                elif sqlserver7_0regex.match(product_version):
                    curr_dataframe = df7_0
                    release_type = '7_0'
                elif sqlserver6_5regex.match(product_version):
                    curr_dataframe = df6_5
                    release_type = '6_5'
                else:
                    print('Something went wrong. SQL version "' + product_version + '" did not match a regular expression that lists a dataframe for that version.', end='')
                    print('At the time this program was written, it covered SQL Server versions 6.5 (6.50.___) through 2019 (15.0.____.__)', end='')
                    print('If your version is out of that range, go to https://sqlserverbuilds.blogspot.com and add that page to be supported by this program.')
                    break

                # once correct row containing the version is found, need to get "Release Date" from same row
                html_row_counter = -1
                # make sure the version is present in the webpage
                bool_found = False 

                for version in curr_dataframe['Build']:
                    html_row_counter += 1
                    if version==product_version:
                        curr_version_date = curr_dataframe['Release Date'][html_row_counter].split()
                        curr_version_date = curr_version_date[0]
                        csv_line = csv_line + ',' + curr_version_date # add to csv file with comma
                        bool_found = True
                        break
                if bool_found == False: # version was not found in webpage for some reason
                    csv_line = csv_line + ','
                    print('There was a problem - the version ' + product_version + ' was not found on the webpage')

                    

                # (7) updates current within two months?
                # got from https://gist.github.com/amalgjose/c767a4846d6ecaa3b6d7
                last_release_date = ""

                for i in update_dict:
                    if i==release_type:
                        last_release_date = update_dict[i]
                        break

                from datetime import datetime
                from dateutil import relativedelta

                # current version's release date
                split_version_date = curr_version_date.split('-')

                date_1Year = int(split_version_date[0])
                date_1Month = int(split_version_date[1])
                date_1Day = int(split_version_date[2])

                date_1 = datetime(date_1Year,date_1Month,date_1Day)

                # new version's release date
                split_version_date2 = last_release_date.split('-')

                date_2Year = int(split_version_date2[0])
                date_2Month = int(split_version_date2[1])
                date_2Day = int(split_version_date2[2])

                date_2 = datetime(date_2Year,date_2Month,date_2Day)

                difference = relativedelta.relativedelta(date_2,date_1)

                # can change this block if you want to check if "Updates Current Within" different timeframe
                if difference.months < 2 and difference.years == 0:
                    csv_line = csv_line + ',' + 'True'
                else:
                    csv_line = csv_line + ',' + 'False'
                    twomonthsout += 1
                    
                # updating counters for text file statistics
                if difference.months >= 6 and difference.years == 0: # between 6 months and 1 year
                    notupdatedin6mon += 1
                    
                if difference.years == 1: # between 1 year and 2 years 
                    notupdatedin1year += 1
            
                if difference.years >= 2: # 2 years or greater
                    notupdatedin2years += 1


                    
                # (8) update available 
                if(last_release_date != curr_version_date):
                    csv_line = csv_line + ',' + 'True'
                else:
                    csv_line = csv_line + ',' + 'False'



                # (9) newest update release date   
                csv_line = csv_line + ',' + last_release_date



                # (10) security update stuff - need to figure this out
                csv_line = csv_line + ','



                #(11) new service pack available
                # SQL Server 2017 and greater does not have service packs
                if release_type >= '2017': 
                    csv_line = csv_line + ','
                # get highest service pack for the year's version through the sp_dict map
                else:
                    biggest_sp = ""
                    curr_sp = str(df1['Product Level'][csv_row_counter])
                    for year in sp_dict:
                        if year==release_type:
                            biggest_sp = sp_dict[year]
                
                    # compare service pack to service pack installed on server
                    if biggest_sp != curr_sp: 
                        outofdate_sp += 1
                        csv_line = csv_line + ',' + biggest_sp
                    else:
                        csv_line = csv_line + ','
                             
                    

                finalcsv.write(csv_line)
                finalcsv.write('\n')

                


    with open('MSSQLoutputStats','w') as file2:

        file2.write(str(server_count))
        file2.write(" server" if server_count==1 else " servers")
        file2.write(" scanned")
        file2.write('\n')
        file2.write("___________________") # trying to make text file a little prettier
        file2.write('\n')
        file2.write('\n')

        file2.write(str(has_sql_count))
        file2.write(" server" if has_sql_count==1 else " servers")
        file2.write(" with SQL (query returned true)")
        file2.write('\n')

        file2.write(str(not_with_sql_count))
        file2.write(" server" if not_with_sql_count==1 else " servers")
        file2.write(" without SQL (query returned false)")
        file2.write('\n')

        file2.write(str(didnot_run))
        file2.write(" server" if didnot_run==1 else " servers")
        file2.write(" did not run query at all (neither true nor false)")
        file2.write('\n')
        file2.write('\n')

        file2.write("Other:")
        file2.write('\n')

        file2.write(str(gave_warning))
        file2.write(" server" if gave_warning==1 else " servers")
        file2.write(" that gave WARNING (query returned false). See the 'allScannedServers' CSV file for more information.")
        file2.write('\n')
        file2.write('\n')
        
        file2.write('\n')
        file2.write("~~~SQL Server Version Information~~~")
        file2.write('\n')
        file2.write('\n')
        
        file2.write(str(twomonthsout))
        file2.write(" server" if notupdatedin6mon==1 else " servers")
        file2.write(" with uninstalled updates that are 2 or more months old")
        file2.write('\n')
        file2.write('\n')
        
        file2.write(str(notupdatedin6mon))
        file2.write(" server" if notupdatedin6mon==1 else " servers")
        file2.write(" with uninstalled updates that are between 6 months and 1 year old")
        file2.write('\n')
        file2.write(str(notupdatedin1year))
        file2.write(" server" if notupdatedin1year==1 else " servers")
        file2.write(" with uninstalled updates that are between 1 year and 2 years old")
        file2.write('\n')
        file2.write(str(notupdatedin2years))
        file2.write(" server" if notupdatedin2years==1 else " servers")
        file2.write(" with uninstalled updates that are more than 2 years old")
        file2.write('\n')
        file2.write('\n')
        
        file2.write(str(outofdate_sp))
        file2.write(" server" if outofdate_sp==1 else " servers")
        file2.write(" with an out-of-date service pack")
        file2.write('\n')
        file2.write('\n')
        
        versions_list.sort()
        file2.write("Scanned servers had Microsoft SQL Server Versions: ")
        file2.write('\n')
        for sql_item in versions_list:
            file2.write("    " + sql_item)
            file2.write('\n')
            
            
    
    if twomonthsout == 1:
        pluralornot = " server"
    else:
        pluralornot = " servers"
        
    

#     import smtplib
#     from email.message import EmailMessage


#     message = """
# Hello, this is the automated bi-weekly SQL Server update. (alright, it's not exactly automated yet, but we're getting there!)
# There are """ + str(twomonthsout) + pluralornot + """ with updates pending that are two months or older.

# The first CSV file attached contains information about the SQL Version on specific servers, and the second includes all servers
# scanned but with little information about SQL Version.
# The text file attached has some simple statistics about the number of servers with SQL, and the SQL Versions present on servers.

# """
    

#     email = EmailMessage()
#     email["From"] = ''
#     email["Subject"] = "SQL Server Version Updatesssss"
#     email["To"] = [''] 
#     email.set_content(message)
#     with open('serversWithMSSQL.csv','rb') as content_file:
#         content = content_file.read()
#         email.add_attachment(content,maintype='csv',subtype='csv',filename='serversWithMSSQL.csv')
#     with open('MSSQLoutputStats','rb') as text_file:
#         content2 = text_file.read()
#         email.add_attachment(content2,maintype='txt',subtype='txt',filename='SQLstats.txt')
#     with open(csvname,'rb') as csv_file:
#         content3 = csv_file.read()
#         email.add_attachment(content3,maintype='csv',subtype='csv',filename='allScannedServers.csv')

#     smtpObj = smtplib.SMTP('insert mail server here')
#     smtpObj.send_message(email)         
#     print("Successfully sent email with SQL Server information")
         
        
       
        
def recent_release(app_dataframe):
    # get most recent version update date - will be printed to csv file later
    import re
    release_date_regex = re.compile("^([0-9-]{10}).*new$")
    for date in app_dataframe['Release Date']:

        if release_date_regex.match(date):
            l_release_date = date.split() 
            # the last update's release date: in form "2020-05-28".
            l_release_date = l_release_date[0]
            return str(l_release_date)
        
        
def highest_sp(versions_dataframe):
    import re
    service_pack_regex = re.compile("Service Pack [1-9]{1}")
    sp_regex = re.compile("SP[1-9]{1}")
    
    service_pack = 'SP'
    service_pack2 = 'Service Pack '

    temp_pack1 = service_pack
    temp_pack2 = service_pack2

    for description in versions_dataframe['KB / Description']:
        # a service pack in the form "Server Pack _" is present in the table
        if service_pack_regex.search(description): 
            service_packs1 = re.findall(sp_regex,description)
            for pack in service_packs1:
                if pack > temp_pack1: # compare to hard-coded value
                    temp_pack1 = pack

        # a service pack in the form "SP_" is present in the table
        if sp_regex.search(description):
            service_packs2 = re.findall(service_pack_regex,description)
            for pack2 in service_packs2:
                if pack2 > temp_pack2: # compare to hard-coded value
                    temp_pack2 = pack2
    
    # find the highest service pack
    if temp_pack2 > service_pack2:
        temp_pack2 = 'SP' + temp_pack2[13] # put version in normal "SP_" format
        if temp_pack1 > service_pack and temp_pack1 >= temp_pack2:
            return temp_pack1
        elif temp_pack1 > service_pack and temp_pack1 < temp_pack2:
            return temp_pack2
    else:
        return temp_pack1
    

    
    
if __name__ == '__main__':
    main()
