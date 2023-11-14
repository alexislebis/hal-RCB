### author : alexis lebis

import argparse
from datetime import date
import csv
import sys

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
    return parser

if __name__ == "__main__":
    arg_parser = create_arg_parser()
    parsed_args = arg_parser.parse_args(sys.argv[1:])


PREFIX_IDHAL        = "authIdHal_s:"
PREFIX_ORCID        = "authORCIDIdExt_s:"
PREFIX_SUBMISSION   = "producedDate_tdate:" #ISO 8601 -- should it be publicationDate_tdate ?

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
                print("The .csv file contains strange information regarding the 'dispo' of "+row['prenom'] + row['nom']+". Please, check and fix. For now, skipping this constraint.")
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

    path = ""
    if(parsed_args.output):
        path = parsed_args.output
    else:
        path = "hal_criteria.txt"
    f = open(path, "w")
    f.write(critHAL)
    f.close
    print("HAL criteria saved to:"+ path)
