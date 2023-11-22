# hal-CCB
HAL Criteria Collection Builder (CCB)

This software take a formatted csv file and produce some specific criteria that can be usefull for automatic stamping for a HAL collection.

## Usage
Invok the script from your shell using Python3.

Path of the csv file is mandatory.

Please check the --help for more information.

```
python3 /path/to/soft --help
```

## CSV format
To work, the software expects a specific CSV format of 8 columns, described as follow :

* 1st columun : lastName [type:str]
* 2nd columun : firstName [type:str]
* 3rd columun : idHAL [type:str] (see [here](https://doc.archives-ouvertes.fr/en/idhal-and-cv/))
* 4th columun : ORCiD [type:str] (see [here](https://orcid.org/))
* 5th columun : scholarArrival [type:AAAA-MM-JJ] (date of arrival of the scholar in the lab)
* 6th columun : scholarDeparture [type:AAAA-MM-JJ] (date of departure of the scholar in the lab)
* 7th columun : nonActive [type:AAAA-MM-JJ] (date of "mise en disponibilité" of the scholar)
* 8th columun : reinstatement [type:AAAA-MM-JJ] (date of coming back from "mise en disponibilité")

Please note that all the fields can be optionnal: the software will try to produce consistent output. For example, it will skip scholars who do not have either an idHal and an ORCiD.

Example with all the fields filled for one scholar:
```
lastName,firstName,idHAL,ORCiD,scholarArrival,scholarDeparture,nonActive,reinstatement
lebis,alexis,alexislebis,0000-0003-2104-8671,2019-09-01,2021-06-15,2020-01-01,2020-04-01
```

Adding more scholars can be made by making a new line to the csv.

## Output
The CCB will try to produce a consistant logical proposition from what you give it.

The result produced from the above example :
```
((authIdHal_s:(alexislebis) OR authORCIDIdExt_s:(0000000321048671)) AND (producedDate_tdate:[2019-09-01T00:00:00Z TO 2021-06-15T00:00:00Z} AND NOT producedDate_tdate:{2020-01-01T00:00:00Z TO 2020-04-01T00:00:00Z]))
```

## Other use
This software also produces an export of all the work of the scholars, optionnaly during a specified temporal interval. `-s` or `--startRetrieve` followed by `YYYY-MM-DD` specify the date to start looking for, and `-e` or `--endRetrieve` followed by `YYYY-MM-DD` the date to end up the search. If there is a conflict between `scholarArrival` and `-s` the date which succeed the other is used. Conversely if there is a conflict between `-e` and `scholarDeparture`, the date which preceed the other is used. This way, no work will be retrieved when a scholar leave the institution.

A summary of the primary domains of all the extracted documents can also be produced using the `-d` or `--domains` optional argument.

Example of use retrieving all the work of scholars indicated in the .csv in [2023-01-01,2023-12-30]
```
python3 hal_ccb.py ./hal.csv -s 2023-01-01 -e 2023-12-30 -d
```