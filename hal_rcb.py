### author : alexis lebis

import argparse
from datetime import date
import urllib.request
import urllib.parse
import csv
import sys
import json
import os
import re
import pandas as pd

def create_arg_parser():
    # Creates and returns the ArgumentParser object

    parser = argparse.ArgumentParser(description='This script helps with the creation of the criteria for a HAL collection (www.hal.science).\n\n It works with a csv file, formatted as [lastName:str, firstName:str,idHAL:str,ORCiD:str,scholarArrival:AAAA-MM-JJ,scholarDeparture:AAAA-MM-JJ,nonActive:AAAA-MM-JJ,reinstatement:AAAA-MM-JJ]. Please note that "nonActive" is used as the meaning of "mise en disponibilité" in the french civil service ; "reinstatement" means that someone who takes his/her "mise en disponibilité" has returned.\n\n This software comes without any guarantee : please always check the output before using it for your HAL Collection.\n\nAuthor: Alexis Lebis')
    parser.add_argument('csvPath',
                    help='Path to the input csv file.')
    parser.add_argument('--output',
                    help='Path and name of the file to where the criteria should be saved. Use default hal_criteria if missing')
    parser.add_argument('-v', '--verbose', help="Increase output verbosity by displaying HAL criteria produced.", action="store_true")
    parser.add_argument('-s','--startRetrieve', type=str, help="The start date in format AAAA-MM-DD to fetch in the HAL API, included.")
    parser.add_argument('-e','--endRetrieve', type=str, help="The end date in format AAAA-MM-DD to fetch in the HAL API, included.")
    parser.add_argument('-d','--domains', help="Indicate wether or not the primary domains should be printed at the end of the summary.", action="store_true")
    parser.add_argument('-r','--numRows', type=int, help="The number of rows to be retrieved during the queries. Max is 10000. Default 50.", default=50)
    parser.add_argument('-a','--autocorrectrows', help="Auto correct the number of rows to be retrieved during the queries if an error occur. Can generate two queries to the HAL documents portal. It is a quality of life argument.", action="store_true")
    parser.add_argument('-j','--autoscimago', help="Performs automatic check of HAL extracted articles from journals over scimago database (scimago files must be stored in a single folder and each file must by of the form 'scimagojr YEAR.csv')", action="store_true")
    parser.add_argument('-f','--scimagofolder', help="Folder to find all the yearly scimago exports to check", default="scimago-folder")
    return parser

if __name__ == "__main__":
    arg_parser = create_arg_parser()
    parsed_args = arg_parser.parse_args(sys.argv[1:])


PREFIX_IDHAL        = "authIdHal_s:"
PREFIX_ORCID        = "authORCIDIdExt_s:"
PREFIX_SUBMISSION   = "producedDate_tdate:" #ISO 8601 -- should it be publicationDate_tdate ?

OUTPUT_FILE = "hal_with_scimago.csv"

# FOLLOWING IS IA GENERATED (for SCIMAGO Extract)
def load_scimago(year):
    if year in scimago_cache:
        return scimago_cache[year]

    filename = os.path.join(
        parsed_args.scimagofolder,
        f"scimagojr {year}.csv"
    )

    if not os.path.exists(filename):
        print(f"Missing SCImago file for {year}")
        scimago_cache[year] = None
        return None

    # SCImago files are usually ';' separated
    df = pd.read_csv(filename, sep=';', encoding="utf-8")

    # Normalize title column
    if "Title" not in df.columns:
        raise ValueError(
            f"'Title' column not found in {filename}"
        )

    df["Title_norm"] = (
        df["Title"]
        .str.lower()
        .str.strip()
    )

    scimago_cache[year] = df
    return df


# ---------------------------------------------------------
# Extract year and journal
# ---------------------------------------------------------

def extract_year(text):
    m = re.search(r"\b(19|20)\d{2}\b", text)
    return int(m.group()) if m else None


def extract_journal(text):
    """
    HAL format:

    Authors. Title. Journal, 2023, ...
    """

    # Split on ". "
    parts = re.split(r"\.\s+", text)

    if len(parts) < 3:
        return None

    # Third element should normally be the journal
    journal = parts[2]

    # Remove trailing commas if any
    journal = journal.split(",")[0].strip()

    return journal

def find_journal(df, journal): #EXACT MATCH
    journal_norm = journal.strip().lower()

    match = df[df["Title_norm"] == journal_norm]

    if match.empty:
        return None

    return match.iloc[0]
###########

with open(parsed_args.csvPath, newline='') as csvfile:

    reader = csv.DictReader(csvfile)
    print("Generating HAL new criteria...")
    critHAL = ""

    for row in reader:
        idHAL = ""
        ORCiD = ""
        autID = ""
        arrive= ""
        depart= ""
        ad = ""
        d1 = ""
        rd1 =""
        drd1 = ""
        tmpCst = ""

        rowCrit = ""

        print("* Processing: "+row['firstName'] + " "+ row['lastName'])
        
        if(not(row['idHAL'] == "")):
            idHAL = PREFIX_IDHAL+"("+row['idHAL']+")"
        
        if(not(row['ORCiD'] == "")):
            ORCiD = PREFIX_ORCID+"("+row['ORCiD']+")"
            ORCiD = ORCiD.replace("-","")

        #Building logical prop :
        ## (scholar_id OR isWorkingForInstitution)
        ### scholar_id = idHAL OR ORCiD
        ### isWorkingForInstitution <->  (arrive >= datePubli AND datePubli < depart) AND ( datePubli <= dispo1 OR datePubli >= retourDispo1)
        autID = idHAL
        if(idHAL and ORCiD):
            autID += " OR "
        autID += ORCiD
        
        #IF non idHAL or ORCiD, can't identify author ! Print error then abort this scholar
        if(autID == ""):
            print("There was an issue while parsing "+row['firstName'] + row['lastName']+"'s id. Aborting his/her HAL criteria. Please check the .csv file. If the scholar does not have an idHAL, please make him/her create one.")
            continue

        #Adding temporal conditions now

        ##Building scholar arriving and departure
        if(not(row["scholarArrival"] == "")):
            arrive = "["+row["scholarArrival"]+"T00:00:00Z"
        if(not(row["scholarDeparture"] == "")):
            depart = row["scholarDeparture"] +"T00:00:00Z"+ "}" #excluding last element
        
        ##Exploiting -s and -e to adjust arrive and depart -- at the end here, the arrive date is correctly set
        if(parsed_args.startRetrieve):
            if(arrive == ""):
                arrive = "["+parsed_args.startRetrieve+"T00:00:00Z"
            else:
                dateS = date.fromisoformat(parsed_args.startRetrieve)
                dateA = date.fromisoformat(arrive.replace("[","").replace("T00:00:00Z",""))
                if(dateS > dateA): #date arrive precedes date s, so arrive have to be replaced by s requested by user invoking the script
                    arrive = "["+parsed_args.startRetrieve+"T00:00:00Z"
                #else, nothing to do bc dateS precedes the date of the scholar so we can't retrieve its works previous to his/her enrollemnt in the institutions

        ##Exploiting -s and -e to adjust arrive and depart -- at the end here, the arrive date is correctly set
        if(parsed_args.endRetrieve):
            if(depart == ""):
                depart = parsed_args.endRetrieve+"T00:00:00Z"+"}"
            else:
                dateS = date.fromisoformat(parsed_args.endRetrieve)
                dateD = date.fromisoformat(depart.replace("}","").replace("T00:00:00Z",""))
                if(dateD > dateS): #date s precedes date depart, so depart have to be replaced by s requested by user invoking the script
                    depart = parsed_args.endRetrieve+"T00:00:00Z"+"}"
                #else, nothing to do bc dateS precedes the date of the scholar so we can't retrieve its works previous to his/her enrollemnt in the institutions

        if(arrive):
            if(depart):
                ad = PREFIX_SUBMISSION + arrive + " TO " + depart
            else:
                ad = PREFIX_SUBMISSION + arrive + " TO * ]"
        else:
            if(depart):
                ad = PREFIX_SUBMISSION + "[* TO "+ depart
            else:
                ad = ""

        ## scholar "dispo"
        if(not(row["nonActive"] == "")):
            d1 = row["nonActive"]
        if(not(row["reinstatement"] == "")):
            rd1 = row["reinstatement"]
        if(d1):
            if(rd1):
                drd1 = "NOT "+ PREFIX_SUBMISSION + "{" + d1 + "T00:00:00Z TO "+ rd1+"T00:00:00Z]"
            else: #not come back yet
                drd1 = "NOT "+ PREFIX_SUBMISSION + "{" + d1 + "T00:00:00Z TO *]"
        else:
            if(rd1):
                print("The .csv file contains strange information regarding the 'dispo' of "+row['prenom'] +" "+ row['nom']+". Please, check and fix. For now, skipping this constraint.")
                d1 = ""
                rd1 = ""
                drd1 = ""

        tmpCst = ad
        if(tmpCst and drd1):
            tmpCst += " AND "
        tmpCst += drd1


        rowCrit = "("+autID+")"
        if(tmpCst):
            rowCrit += " AND ("+tmpCst+")"

        if(critHAL):
            critHAL += " OR "
        critHAL += "("+rowCrit+")"

    print("HAL criteria generated.")
    if(parsed_args.verbose):
        print(critHAL)

    #Querying the HAL API

    ## Retrieving each document type
    doc_types = {}
    doc_contents = {}
    url = "https://api.archives-ouvertes.fr/ref/doctype"
    page = urllib.request.urlopen(url)
    html_bytes = page.read()
    html = html_bytes.decode("utf-8")
    data = json.loads(html)
    for i in data['response']['result']['doc']:
        doc_types[i["str"][0]]=i["str"][1]
        doc_contents[i["str"][0]]=[]
    
    ## Retrieving each domain type
    # domain_types = {}
    # url = "https://api.archives-ouvertes.fr/ref/domain"
    # page = urllib.request.urlopen(url)
    # html_bytes = page.read()
    # html = html_bytes.decode("utf-8")
    # data = json.loads(html)
    # for i in data['response']['docs']:
    #     accro,dom_lab = i["label_s"].split("=")
    #     accro = accro[:-1]
    #     dom_lab = dom_lab[1:]
    #     domain_types[accro]=dom_lab
    # print(domain_types)

    ## Retrieving json for all the scholars with GET query personnalized
    url = "https://api.archives-ouvertes.fr/search/"
    way_naming_entry = "label_s" #can be "label_s" "citationFull_s"
    values = {"q":critHAL, "wt":"json", "fl":"docType_s,primaryDomain_s,docid,uri_s,authIdHal_s,"+way_naming_entry, "rows":parsed_args.numRows}
    data = urllib.parse.urlencode(values)
    url = '?'.join([url,data])
    if(parsed_args.verbose):
        print(url)
    page = urllib.request.urlopen(url)
    html_bytes = page.read()
    html = html_bytes.decode("utf-8")
    if(parsed_args.verbose):
        print(html)
    data = json.loads(html)

    ## Checking if rows if suffisant or not ; auto-correct
    if int(data["response"]["numFound"]) > parsed_args.numRows:
        print("Warning /!\ The number of rows used ("+str(parsed_args.numRows)+") does not match the number of documents found ("+str(data["response"]["numFound"])+")!")
        if parsed_args.autocorrectrows:
            print("Auto correcting the number of rows from "+str(parsed_args.numRows)+" to "+str(data["response"]["numFound"]))
            url = "https://api.archives-ouvertes.fr/search/"
            way_naming_entry = "label_s" #can be "label_s" "citationFull_s"
            values = {"q":critHAL, "wt":"json", "fl":"docType_s,primaryDomain_s,docid,uri_s,authIdHal_s,"+way_naming_entry, "rows":data["response"]["numFound"]}
            data = urllib.parse.urlencode(values)
            url = '?'.join([url,data])
            if(parsed_args.verbose):
                print(url)
            page = urllib.request.urlopen(url)
            html_bytes = page.read()
            html = html_bytes.decode("utf-8")
            if(parsed_args.verbose):
                print(html)
            data = json.loads(html)
        else:
            print("You should envisage to increase the number of rows value fetched using the -r argument.")
            exit()

    ## Sorting each doc according to their types
    key = "docType_s"
    arr_val_id = way_naming_entry
    for i in data["response"]["docs"]:
        content = i[arr_val_id]
        doc_contents[i[key]].append(content)

    ## Counting each primary domain iff args.domains is true
    if(parsed_args.domains):
        key = "primaryDomain_s"
        domains = {}
        for i in data["response"]["docs"]:
            if i[key] in domains:
                domains[i[key]] += 1
            else:
                domains[i[key]] = 1

        ### Retrieving each domain encountered (the API does not give us ALL the domain, so we have to proced this way : first identify all id domain (cf above), then query the api)
        domain_types = {}
        domain_query = "("
    
        for key,val in domains.items():
            domain_query += "code_s:"+key+" OR "
        domain_query = domain_query[:-4]+")"

        domain_url = "https://api.archives-ouvertes.fr/ref/domain"
        domain_get = {"q":domain_query,"rows":len(domains)} # using len(domain) for adapting the size of the domain query (hal api is defaulted to 30)
        data_domain = urllib.parse.urlencode(domain_get)
        domain_url = "?".join([domain_url,data_domain])
        if(parsed_args.verbose):
            print(domain_url)
        page = urllib.request.urlopen(domain_url)
        html_bytes = page.read()
        html = html_bytes.decode("utf-8")
        if(parsed_args.verbose):
            print(html)
        data = json.loads(html)
        for i in data['response']['docs']:
            accro,dom_lab = i["label_s"].split("=")
            accro = accro[:-1]
            dom_lab = dom_lab[1:]
            domain_types[accro]=dom_lab.split("/")[-1]#could remove .split("/")[-1] in order to retrieve the entire path of the domain, not ontly the leaf of the domain tree
            

    # Exporting results
    ## Exporting HAL criteria used in the query
    path = ""
    if(parsed_args.output):
        path = parsed_args.output
    else:
        path = "hal_criteria.txt"
    f = open(path, "w")
    f.write(critHAL)
    f.close
    print("HAL criteria saved to:"+ path)

    ## Exporting the query resolved in plaintext in a simple format (could be improve with various formats such as md rt etc...)
    path = ""
    if(parsed_args.output):
        path = parsed_args.output.split(".")[0]+"_resolved.txt"
    else:
        path = "hal_criteria_resolved.txt"
    f = open(path, "w")
    resolHAL = ""
    for type,content in doc_contents.items():
        resolHAL += "\n# " + doc_types[type] + "\n"
        counter = 1
        for i in content:
            resolHAL += str(counter)+ ". " + (urllib.parse.unquote(i) +"\n").replace("&#x27E8;","⟨").replace("&#x27E9;","⟩")
            counter += 1
    
    if(parsed_args.domains):
        resolHAL += "\n\n=== Représentativité des domaines\n"
        print(domains)
        for key,val in domains.items():
            resolHAL += "* " + domain_types[key] + " : " + str(val) +"\n"
    f.write(resolHAL)
    f.close
    print("HAL export to:"+ path)
    if(parsed_args.domains):
        print("Domains summary has been added to the end of the report (word of caution: the list is not ordered)")


# SCIMAGO autolabeling
    
    if(parsed_args.autoscimago):
        scimago_cache = {}
        results = []

        for pub in doc_contents["ART"]:

            year = extract_year(pub)
            journal = extract_journal(pub)

            result = {
                "Publication": pub,
                "Year": year,
                "Journal": journal,
                "H index": None,
                "Quartile": None,
                "SJR": None,
                "Categories": None
            }

            if year is None or journal is None:
                results.append(result)
                continue

            df = load_scimago(year)

            if df is None:
                results.append(result)
                continue

            row = find_journal(df, journal)

            if row is not None:

                if "H index" in row:
                    result["H index"] = row["H index"]

                if "SJR Best Quartile" in row:
                    result["Quartile"] = row["SJR Best Quartile"]

                if "SJR" in row:
                    result["SJR"] = row["SJR"]

                if "Categories" in row:
                    result["Categories"] = row["Categories"]

            else:
                print(f"Journal not found: {journal} ({year})")

            results.append(result)

        pd.DataFrame(results).to_csv(
            OUTPUT_FILE,
            index=False,
            encoding="utf-8"
        )

        print("Done.")        


