# mssql-version-sccm

Apologies for my spaghetti code if anyone actually reads this - this was my first time writing an extensive Python program and I did not intend for it to get this long. I also wrote it within jupyter notebook instead of using an IDE and Anaconda Prompt, which was a mistake. Might clean the whole program up at some point.

The program parses the output of a PowerShell script asking servers for their versions, and indicates which MSSQL versions are out-of-date.

In SCCM, create a new script, and paste the PowerShell script into the box. Run it on the device collection that contains the servers that you want to query. It is okay if it runs on servers that do not have MSSQL installed - the Python parsing script will sort those out for you.

Once the script completes on the servers (it should be quick) copy and paste the results into a text file. 
In the text file, the results will look something like the samples/input/SCCMresult.txt file.

Put that text file in the same directory as the parseOutputOfPowerShellSCCM.py program.
Run the python program and it will parse the text file. It will create a new directory in your current directory with two CSV files and a text file, which contain the version information that you want!

In the samples/output directory, check out the output of the parsing program.
