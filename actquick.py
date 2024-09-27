import os,sys,requests
from xml.etree import ElementTree as ET
import argparse
import getpass
import zipfile
from concurrent.futures import ThreadPoolExecutor
from time import time

# Replace 'url' with your WebDAV server URL
source = 'https://dc-act.spring8.or.jp/remote.php/dav/files/'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--user', type=str, default=None, help='userID for aCT download website',required=True) 
    parser.add_argument('--proposal', type=str, default=None, help='Proposal No., e.g., 2024AXXXX',required=True)
    parser.add_argument('--sampleid', type=str, default=None, nargs='*', help='Sample ID (if known) , 10-digits number')
    ###parser.add_argument('--zip', type=str, default=None, nargs='*', 
    ###    choices=['rh', 'rh_222', 'rh_444', 'ro', 'ro_222', 'ro_444', 'all','allro','allrh','all222','all444'],
    ###    required=True)
    parser.add_argument('--output', type=str, default=None, help='where to save (Default = /UserData/YOUR_USER_ID/PROPOSAL_NO/SAMPLE_ID)')
    parser.add_argument('--nounzip', action='store_true', default=False, help='use this option when you do not want to extract zip files')
    
    args = parser.parse_args()

    # if args.zip == ["all"]:
    #     args.zip = ["ro_444", "rh_444", "ro_222", "rh_222", "ro", "rh"]
    # elif args.zip == ["allrh"]:
    #     args.zip = ["rh_444", "rh_222", "rh"]
    # elif args.zip == ["allro"]:
    #     args.zip = ["ro_444", "ro_222", "ro"]
    # elif args.zip == "all222":
    #     args.zip = ["ro_222", "rh_222"]
    # elif args.zip == ["all444"]:
    #     args.zip = ["ro_444", "rh_444"]
    # else:
    #     pass

    print("\n")
    args.pw = getpass.getpass() # password入力をショートカットする場合はこの行をコメントアウト
    # args.pw = "hogehoge" # password入力をショートカットする場合はこの行に記入    



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
    
    def get_sample_id(response):
        # Parse the XML response
        tree = ET.fromstring(response.content)
        namespaces = {'d': 'DAV:'}  # Adjust the namespace if necessary
        print("\n")
        print(f"{args.proposal} Searching...")
        sample_id_list = []
        # Find all 'href' elements - they contain the directory names
        num = 0
        for href in tree.findall('.//d:href', namespaces):
            dirname = os.path.basename(os.path.dirname(href.text))
            if dirname != args.proposal:
                sample_id_list.append(dirname)
                num = num + 1

        if num != 0:
            #print(f"{num} data found")
            #print("\n")
            return sample_id_list
        else:
            #print("no data found")
            #print("\n")
            sys.exit()
        
    
    def downloadzip(proposal,sampleid,inputzip,outputzip):
        start = time()
        print(f"Downloading: {inputzip}")
        # Make a GET request to the WebDAV server to download the file
        response = requests.get(inputzip, auth=(args.user, args.pw), stream=True)
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        last_reported_percent = 0
        
        # Check if the request was successful
        if response.status_code == 200:
            # Write the content of the response to a local file
            #output = str(output) + "/" + str(args.zip) + ".zip"
            with open(outputzip, 'wb') as file:
                # file.write(response.content)
                for data in response.iter_content(1024*1024):
                    file.write(data)
                    downloaded += len(data)
                    current_percent = (downloaded / total_size) * 100
                    # Update the progress bar only if the increase is significant
                    if current_percent - last_reported_percent >= 1:
                        print_progress_bar(current_percent)
                        last_reported_percent = current_percent
                #print("\n")
            
            elapsed = time() - start
            filesize = round(total_size / 1024 ** 2, 2)
            speed = round(filesize / elapsed)
            print(f"zip downloaded successfully!: {outputzip} ({round(elapsed)} sec. elapsed, speed = {speed} MB/sec)")
        else:
            print(f"Failed to download file. Status code: {response.status_code}")
            print("\n")

    def print_progress_bar(percent_complete):
        bar_length = 50
        filled_length = int(bar_length * percent_complete // 100)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        print(f"\rProgress: |{bar}| {percent_complete:.2f}%", end='\r')

    def extract_zip(zip_path, extract_to):
        # Open the zip file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Get the list of file names
            file_names = zip_ref.namelist()
            total_files = len(file_names)  # Total files to extract
            update_interval = max(1, total_files // 100)  # Update every 1% of the total files

            # Extract files one by one
            for i, file in enumerate(file_names, start=1):
                # Extract the file
                zip_ref.extract(file, extract_to)
                # Only update progress after a certain number of extracts or at the end
                if i % update_interval == 0 or i == total_files:
                    progress = (i / total_files) * 100  # Calculate progress percentage
                    sys.stdout.write(f"\rExtracting... {progress:.2f}%")
                    sys.stdout.flush()
            
    ## sampleIDリスト取得
    if args.sampleid == None:
        url = str(source) + str(args.user) + "/" + str(args.proposal)
        proposal_response = urlcheck(url, "--user or Password or --proposal")
        sample_id_list = get_sample_id(proposal_response)
    else: 
        sample_id_list = []# args.sampleid
        url = str(source) + str(args.user) + "/" + str(args.proposal)  
        urlcheck(url, "--user or Password or --proposal")

        def wildcardcheck(id_list):
            for elem in id_list:
                if '*' in str(elem):
                    return True
            return False

        result = wildcardcheck(args.sampleid)

        if result is True:
            proposal_response = urlcheck(url, "--user or Password or --proposal")
            sample_id_list_temp = get_sample_id(proposal_response)   

            for elem in args.sampleid:
                if "*" in elem:
                    key = elem.strip('*')
                    for sample_id in sample_id_list_temp:
                        if sample_id.startswith(key):
                            sample_id_list.append(sample_id)
                        else:
                            pass
                else:    
                    url = str(source) + str(args.user) + "/" + str(args.proposal) + "/" + str(elem)
                    urlcheck(url, "--sampleid")
                    sample_id_list.append(elem)
        
        else:
            sample_id_list = args.sampleid
            for sampleid in sample_id_list:    
                url = str(source) + str(args.user) + "/" + str(args.proposal) + "/" + str(sampleid)
                urlcheck(url, "--sampleid")

    sample_id_list = list(dict.fromkeys(sample_id_list))

    print(f"{len(sample_id_list)} data found")
    print("\n")
    print(sample_id_list)

    ## 保存先の整合性確認
    if args.output == None:
        outputpath = "/UserData/" + str(args.user)
        if os.path.exists(outputpath) is False:
            outputpath = os.getcwd()
    else:
        outputpath = args.output

    os.makedirs(os.path.dirname(outputpath), exist_ok=True)
    print(f"\nZip will be donwloaded to {outputpath}")

    ## 入出力リスト作成
    inoutlist = []
    for sampleid in sample_id_list:
            # for ziptype in args.zip:
        inputzip = str(source) + str(args.user) + "/" + str(args.proposal) + "/" + str(sampleid) + "/rc-check/rc-check.zip"
        outputzip = outputpath + "/" + str(args.proposal) + "/" + str(sampleid) + "/rc-check.zip"
        inout = [args.proposal, sampleid, inputzip, outputzip] #, ziptype]
        inoutlist.append(inout)

    ## 軽いものからダウンロードするようにリストを並び替える
    # d_order = {"ro_444" : 0, "rh_444" : 1, "ro_222" : 2, "rh_222" : 3, "ro" : 4, "rh" : 5}
    # inoutlist = sorted(inoutlist, key=lambda x: d_order[x[4]])
    # print("Smaller zip (4x4x4 and ro) will be first served. PRESS Ctrl + C for cancel")
    # print("\n")

    ## リストを順番にダウンロード(,展開,zip削除)
    for data in inoutlist:
        os.makedirs(os.path.dirname(data[3]), exist_ok=True)
        downloadzip(data[0],data[1],data[2],data[3])
        
        if args.nounzip == False:
            start = time()
            zipdir = os.path.dirname(data[3])
            os.makedirs(zipdir, exist_ok=True)
            extract_zip(data[3], zipdir)
            os.remove(data[3])
            # if data[4] == "ro" or data[4] == "rh": ## roとrhは二段階の展開
            #     print(f"\nExtracting {data[4]}-1,-2,-3,-4.zip in parallel (takes some time)")
            #     zipdir = os.path.dirname(data[3]) + "/" + data[4]

            #     def rorhzip(path):
            #         with zipfile.ZipFile(path) as zf:
            #             zf.extractall(zipdir)
            #         os.remove(path)
            #     ziplist = [zipdir+ "-" + str(i) + ".zip" for i in range(1,5)]
            #     os.makedirs(zipdir, exist_ok=True)
            #     with ThreadPoolExecutor(max_workers=4) as executor:
            #         executor.map(rorhzip,ziplist)

                # マルチスレッド（４並列）での展開が失敗する場合は逐次処理                
                # extract_zip(zipdir + "-1.zip", zipdir)
                # print(f"\n{data[4]}-1.zip extracted") 
                # os.remove(zipdir+ "-1.zip")
                # extract_zip(zipdir + "-2.zip", zipdir)
                # print(f"\n{data[4]}-2.zip extracted")
                # os.remove(zipdir+ "-2.zip") 
                # extract_zip(zipdir + "-3.zip", zipdir)
                # print(f"\n{data[4]}-3.zip extracted") 
                # os.remove(zipdir+ "-3.zip")
                # extract_zip(zipdir + "-4.zip", zipdir)
                # print(f"\n{data[4]}-4.zip extracted") 
                # os.remove(zipdir+ "-4.zip")

            elapsed = round(time() - start)
            print(f"Extraction complete. ({elapsed} sec.)")   
            print("\n")

            # else:
            #     elapsed = round(time() - start)
            #     print(f"\nExtraction complete. ({elapsed} sec.)")  
            #     print("\n")  
        else:
            pass
    
if __name__ == '__main__':
    main()