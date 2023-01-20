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
To wrok, the software expects a specific CSV format of 8 columns, described as follow :

* 1st columun : lastName [type:str]
* 2nd columun : firstName [type:str]
* 3rd columun : idHAL [type:str] (see [here](https://doc.archives-ouvertes.fr/en/idhal-and-cv/))
* 4th columun : ORCiD [type:str] (see [here](https://orcid.org/))
* 5th columun : scholarArrival [type:AAAA-MM-JJ] (date of arrival of the scholar in the lab)
* 6th columun : scholarDeparture [type:AAAA-MM-JJ] (date of departure of the scholar in the lab)
* 7th columun : nonActive [type:AAAA-MM-JJ] (date of "mise en disponibilité" of the scholar)
* 8th columun : reinstatement [type:AAAA-MM-JJ] (date of coming back from "mise en disponibilité")

Please note that all the fields can be optionnal: the software will try to produce consistent output. For example, it will skip scholars who do not have both an idHal and an ORCiD.

Example with all the fields filled for one scholar:
```
lastName,firstName,idHAL,ORCiD,scholarArrival,scholarDeparture,nonActive,reinstatement
lebis,alexis,alexislebis,0000-0003-2104-8671,2019-09-01,2021-06-15,2020-01-01,2020-04-01
```

Adding more scholars can be made by making a new line to the csv.
