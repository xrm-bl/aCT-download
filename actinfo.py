import os,sys,requests
from requests.exceptions import RequestException, ConnectionError, HTTPError, Timeout
from xml.etree import ElementTree as ET
import argparse
import getpass
import csv

# Replace 'url' with your WebDAV server URL
source = 'https://dc-act.spring8.or.jp/remote.php/dav/files/'

# initColors, findLargestElement, createMatrix, makeRows, createWrappingRows, createRowUnderFields, printRowsInTable, printTable are from:
# https://github.com/SuperMaZingCoder/TableIt
# Copyright 2021 SuperMaZingCoder
# Under MIT lisence
def initColors():
    os.system("cls")

def findLargestElement(rows, cols, lengthArray, matrix):
    # Loop through each row
    for i in range(rows):  
        # Loop through each column
        for j in range(cols):
            lengthArray.append(len(str(matrix[i][j])))
    # Sort the length matrix so that we can find the element with the longest length
    lengthArray.sort()
    # Store that length
    largestElementLength = lengthArray[-1]

    return largestElementLength


def createMatrix(rows, cols, matrixToWorkOn, matrix):
    # Loop through each row
    for i in range(rows):    
        # Append a row to matrixToWorkOn for each row in the matrix passed in
        matrixToWorkOn.append([])
        # Loop through each column
        for j in range(cols):
            # Add a each column of the current row (in string form) to matrixToWorkOn
            matrixToWorkOn[i].append(str(matrix[i][j]))

def makeRows(rows, cols, largestElementLength, rowLength, matrixToWorkOn, finalTable, color):
    # Loop through each row
    for i in range(rows):
        # Initialize the row that will we work on currently as a blank string
        currentRow = ""
        # Loop trhough each column
        for j in range(cols):
            # If we are using colors then do the same thing but as without (below)
            if ((color != None) and (j == 0 or i == 0)):
                # Only add color if it is in the first column or first row
                currentEl = " " + "\033[38;2;" + str(color[0]) + ";" + str(color[1]) + ";" + str(color[2]) +"m" + matrixToWorkOn[i][j] + "\033[0m"
            # If we are not using colors (or j != 0 or i != 0) just add a space and the element that should be in that position to a variable which will store the current element to work on
            else:
                currentEl = " " + matrixToWorkOn[i][j]

            # If the raw element is less than the largest length of a raw element (raw element is just the unformatted element passed in)
            if (largestElementLength != len(matrixToWorkOn[i][j])):
                # If we are using colors then add the amount of spaces that is equal to the difference of the largest element length and the current element (minus the length that is added for the color)
                # * The plus two here comes from the one space we would normally need and the fact that we need to account for a space that tbe current element already has
                if (color != None):
                    if (j == 0 or i == 0):
                        currentEl = currentEl + " " * (largestElementLength - (len(currentEl) - len("\033[38;2;" + str(color[0]) + ";" + str(color[1]) + ";" + str(color[2]) + "m" + "\033[0m")) + 2) + "|"
                    # If it is not the first column or first row than it doesn't need to subtract the color length
                    else:
                        currentEl = currentEl + " " * (largestElementLength - len(currentEl) + 2) + "|"
                # If we are not using color just do the same thing as above when we were using colors for when the row or column is not the first each time
                else:
                    currentEl = currentEl + " " * (largestElementLength - len(currentEl) + 2) + "|"
            # If the raw element length us equal to the largest length of a raw element then we don't need to add extra spaces
            else:
                currentEl = currentEl + " " + "|"
            # Now add the current element to the row that we are working on
            currentRow += currentEl
        # When the entire row that we were working on is done add it as a row to the final table that we will print
        finalTable.append("|" + currentRow)
    # If we are using color then the length of each row (each row will end up being the same length) equals to the length of the last row (again each row will end up being the same length) minus the length the color will inevitably add if we are using colors
    if (color != None):
        rowLength = len(currentRow) - len("\033[38;2;" + str(color[0]) + ";" + str(color[1]) + ";" + str(color[2]) + "m" + "\033[0m")
    # Otherwise (we are not using colors) the length of each row will be equal to the length of the last row (each row will end up being the same length)
    else:
        rowLength = len(currentRow)  
    
    return rowLength

def createWrappingRows(rowLength, finalTable):
    # Here we deal with the rows that will go on the top and bottom of the table (look like -> +--------------+), we start by initializing an empty string
    wrappingRows = ""
    # Then for the length of each row minus one (have to account for the plus that comes at the end, not minus two because rowLength doesn't include the | at the beginning) we add a -
    for i in range(rowLength - 1):
        wrappingRows += "-"
    # Add a plus at the beginning
    wrappingRows = "+" + wrappingRows
    # Add a plus at the end
    wrappingRows += "+"

     # Add the two wrapping rows
    finalTable.insert(0, wrappingRows)
    finalTable.append(wrappingRows)

def createRowUnderFields(largestElementLength, cols, finalTable):
    # Initialize the row that will be created 
    rowUnderFields = ""
    # Loop through each column
    for j in range(cols):
        # For each column add a plus
        currentElUnderField = "+" 
        # Then add an amount of -'s equal to the length of largest raw element and add 2 for the 2 spaces that will be either side the element
        currentElUnderField = currentElUnderField + "-" * (largestElementLength + 2)
        # Then add the current element (there will be one for each column) to the final row that will be under the fields
        rowUnderFields += currentElUnderField
    # Add a final plus at the end of the row
    rowUnderFields += "+"
    # Insert this row under the first row
    finalTable.insert(2, rowUnderFields)

def printRowsInTable(finalTable):
    # For each row - print it
    for row in finalTable:
        print(row)

def printTable(matrix, useFieldNames=False, color=None):
    # Rows equal amount of lists inside greater list
    rows = len(matrix)
    # Cols equal amount of elements inside each list
    cols = len(matrix[0])
    # This is the array to sort the length of each element
    lengthArray = []
    # This is the variable to store the vakye of the largest length of any element
    largestElementLength = None
    #This is the variable that will store the length of each row
    rowLength = None
    # This is the matrix that we will work with throughout this program (main difference between matrix passed in and this matrix is that the matrix that is passed in doesn't always have elements which are all strings)
    matrixToWorkOn = []
    #This the list in which each row will be one of the final table to be printed
    finalTable = []

    largestElementLength = findLargestElement(rows, cols, lengthArray, matrix)
    createMatrix(rows, cols, matrixToWorkOn, matrix)
    rowLength = makeRows(rows, cols, largestElementLength, rowLength, matrixToWorkOn, finalTable, color)
    createWrappingRows(rowLength, finalTable)
    if (useFieldNames):
        createRowUnderFields(largestElementLength, cols, finalTable)
    printRowsInTable(finalTable)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--user', type=str, default=None, help='userID for aCT download website',required=True) 
    parser.add_argument('--proposal', type=str, default=None, help='Proposal No., e.g., 2024AXXXX',required=True)
    parser.add_argument('--sampleid', type=str, default=None, help='Sample ID, 10-digits number (optional)')
    parser.add_argument('--samplename', type=str, default=None, help='Sample Name (optional)')
    parser.add_argument('--pixelsize', type=float, default=None, help='Pixel size (without unit, optional)')
    parser.add_argument('--exposure', type=float, default=None, help='Exposure (without unit, optional)')
    parser.add_argument('--projections', type=int, default=None, help='Number of projections (optional)')
    parser.add_argument('--xray', type=float, default=None, help='X-Ray Energy (without unit, optional)')
    ##temporary## parser.add_argument('--csv', action='store_true', default=False, help='output csv file (optional)')
    parser.add_argument('--txt', action='store_true', default=False, help='output text file (optional)')
    args = parser.parse_args()

    print("\n")
    args.pw = getpass.getpass()
    
    def urlcheck(url, stage):
        # Set up the headers to ask for directory contents (depth can be 0, 1, or "infinity")
        headers = {
            'Depth': '1',
            'Content-Type': 'application/xml'
                    }
        # Make the PROPFIND request
        response = requests.request("PROPFIND", url, auth=(args.user, args.pw), headers=headers)
        # Check if the request was successful
        if response.status_code != 207:  # 207 Multi-Status means success in WebDAV
            print(f"access failured. Check {stage}")
            sys.exit()
        else:
            return response

    def getinfo(response):
        # Parse the XML response
        tree = ET.fromstring(response.content)
        namespaces = {'d': 'DAV:'}  # Adjust the namespace if necessary
        print("\n")
        print(f"{args.proposal} Searching...")
        ##temporary## header = [["Sample ID", "Sample Name", "Pixel Size", "Exposure", "Projections", "X-ray"]]
        header = [["Sample ID, Sample Name, Pixel Size, Exposure, Projections, X-ray"]] ##temporary##
        # Find all 'href' elements - they contain the directory names
        num = 0

        keys = [args.sampleid, args.samplename, args.pixelsize, args.exposure, args.projections, args.xray]

        if keys[0] == None:
            for href in tree.findall('.//d:href', namespaces):
                dirname = os.path.basename(os.path.dirname(href.text))
                if dirname != args.proposal:
                    HEADERurl = str(source) + str(args.user) + "/" + str(args.proposal) + "/" + str(dirname) +  "/HEADER.md"
                    try:
                        HEADERdata = requests.get(HEADERurl, auth=(args.user, args.pw), timeout=5.0).content
                        response.raise_for_status()
                    except ConnectionError as ce:
                        HEADERdata = [f"{args.proposal} {dirname} Connection Error: {ce}"]
                    except HTTPError as he:
                        HEADERdata = [f"{args.proposal} {dirname} HTTP Error: {he}"]
                    except Timeout as te:
                        HEADERdata = [f"{args.proposal} {dirname} Timeout Error: {te}"]
                    except RequestException as re:
                        HEADERdata = [f"{args.proposal} {dirname} Error: {re}"]

                    #print(HEADERdata)

                    try:
                        HEADERdata = HEADERdata.decode('utf8')
                    except AttributeError:
                        pass
                    
                    try:
                        HEADERdata = HEADERdata.splitlines()
                    except AttributeError:
                        pass
                    
                    if HEADERdata == ['This is the WebDAV interface. It can only be accessed by WebDAV clients such as the Nextcloud desktop sync client.']:
                        HEADERdata = [f"{args.proposal} {dirname} Empty HEADER.md"]
                    elif len(HEADERdata) != 1:
                        ##temporary## HEADERdata = HEADERdata[2].split('|') 
                        HEADERdata = [HEADERdata[2]] ##temporary##
                    else:
                        pass
                    print(HEADERdata[0])

                    if len(HEADERdata) == 9:
                        #if args.samplename == None and args.pixelsize == None and args.exposure == None and args.projections == None and args.xray == None:
                        if all(x is None for x in keys) is True:
                            header.append([HEADERdata[2],HEADERdata[3],HEADERdata[4],HEADERdata[5],HEADERdata[6],HEADERdata[7]])
                            num = num + 1
                        else:
                            #if HEADERdata[3] == args.samplename or float(HEADERdata[4].split()[0]) == args.pixelsize or float(HEADERdata[5].split()[0]) == args.exposure or int(HEADERdata[6]) == args.projections or float(HEADERdata[7].split()[0]) == args.xray:
                            if keys[1] is None or keys[1] == HEADERdata[3]:
                                if keys[2] is None or keys[2] == float(HEADERdata[4].split()[0]):
                                    if keys[3] is None or keys[3] == float(HEADERdata[5].split()[0]):
                                        if keys[4] is None or keys[4] == int(HEADERdata[6]):
                                            if keys[5] is None or keys[5] == float(HEADERdata[7].split()[0]):
                                                header.append([HEADERdata[2],HEADERdata[3],HEADERdata[4],HEADERdata[5],HEADERdata[6],HEADERdata[7]])
                                                num = num + 1 
                                            else:
                                                pass
                                        else:
                                            pass
                                    else:
                                        pass
                                else:
                                    pass
                            else:
                                pass
                    else:
                        ##temporary## pass
                        header.append(HEADERdata) ##temporary##   
                        num = num + 1 ##temporary## 
        else:
            HEADERurl = str(source) + str(args.user) + "/" + str(args.proposal) + "/" + str(args.sampleid) +  "/HEADER.md"
            try:
                HEADERdata = requests.get(HEADERurl, auth=(args.user, args.pw), timeout=5.0).content
                response.raise_for_status()
            except ConnectionError as ce:
                HEADERdata = [f"{args.proposal} {dirname} Connection Error: {ce}"]
            except HTTPError as he:
                HEADERdata = [f"{args.proposal} {dirname} HTTP Error: {he}"]
            except Timeout as te:
                HEADERdata = [f"{args.proposal} {dirname} Timeout Error: {te}"]
            except RequestException as re:
                HEADERdata = [f"{args.proposal} {dirname} Error: {re}"]

            #print(HEADERdata)

            try:
                HEADERdata = HEADERdata.decode('utf8')
            except AttributeError:
                pass
            
            try:
                HEADERdata = HEADERdata.splitlines()
            except AttributeError:
                pass
            
            if HEADERdata == ['This is the WebDAV interface. It can only be accessed by WebDAV clients such as the Nextcloud desktop sync client.']:
                HEADERdata = [f"{args.proposal} {dirname} Empty HEADER.md"]
            elif len(HEADERdata) != 1:
                ##temporary## HEADERdata = HEADERdata[2].split('|') 
                HEADERdata = [HEADERdata[2]] ##temporary##
            else:
                pass

            print(HEADERdata[0]) 

        if num != 0:
            print(f"{num} data found")
            ##temporary## printTable(header, useFieldNames=True)
            print("\n")
            ##temporary## if args.csv == True:
            if args.txt == True: ##temporary##    
                ##temporary## csvpath = f'{args.proposal}.csv'
                csvpath = f'{args.proposal}.txt'
                # Writing to a CSV file
                with open(csvpath, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerows(header)
                print(f"csv file saved as: {os.getcwd()}/{csvpath}")
                print("\n")
        else:
            print("no match")
            print("\n")
    
    if args.sampleid != None:
        url = str(source) + str(args.user) + "/" + str(args.proposal) + "/" + str(args.sampleid)
        proposal_response = urlcheck(url, "--sampleid")
        getinfo(proposal_response)

    elif args.sampleid == None:
        url = str(source) + str(args.user) + "/" + str(args.proposal)
        proposal_response = urlcheck(url, "--user or Password or --proposal")
        getinfo(proposal_response)
    
    else:
        pass
    
if __name__ == '__main__':
    main()
