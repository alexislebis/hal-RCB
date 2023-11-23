# hal-RCB

HAL Report and Criteria Builder

This software take a formatted csv file and produce :
* Specific criteria that can be used for automatic stamping for a HAL collection ;
* An export from HAL of all the production of scholars, optionally within a time range, in a simple .txt report (planned : in various formats such as .md and .html)

⚠️ Despite some testings, this software is shipped as is. Please always manually check both the criteria and the export produced by the software to prevent any errors, especially when used for official reports.

## Usage
Invok the script from your shell using Python3.

Path of the csv file is mandatory.

Please check the --help for more information.

```
python3 /path/to/hal_rcb.py --help
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

## Criteria Collection Builder (CCB)
The HAL CCB will try to produce a consistant logical proposition from what you give it.

The result produced from the above example :
```
((authIdHal_s:(alexislebis) OR authORCIDIdExt_s:(0000000321048671)) AND (producedDate_tdate:[2019-09-01T00:00:00Z TO 2021-06-15T00:00:00Z} AND NOT producedDate_tdate:{2020-01-01T00:00:00Z TO 2020-04-01T00:00:00Z]))
```

The criteria can then be used directly in the Administer section in HAL to automatically stamps any publication of the concerned scholars.

## Report Builder (RB)
This software also produces an export of all the productions of the scholars, optionnaly during a specified temporal interval. `-s` or `--startRetrieve` followed by `YYYY-MM-DD` specify the date to start looking for, and `-e` or `--endRetrieve` followed by `YYYY-MM-DD` the date to end up the search. If there is a conflict between `scholarArrival` and `-s` the date which succeed the other is used. Conversely if there is a conflict between `-e` and `scholarDeparture`, the date which preceed the other is used. This way, no work will be retrieved when a scholar leave the institution.

A summary of the primary domains of all the extracted documents can also be produced using the `-d` or `--domains` optional argument.

Example of use in order to retrieve all the works of scholars indicated in the .csv within [2023-01-01,2023-12-30]
```
python3 hal_rcb.py ./hal.csv -s 2023-01-01 -e 2023-12-30 -d
```

It will produced the following `hal_criteria_resolved.txt` file :

```
# Article dans une revue
1. Alexis Lebis, Jérémie Humeau, Anthony Fleury, Flavien Lucas, Mathieu Vermeulen. Fully Individualized Curriculum with Decaying Knowledge, a New Hard Problem: Investigation and Recommendations. International Journal of Artificial Intelligence in Education, 2023, ⟨10.1007/s40593-023-00376-9⟩. ⟨hal-04296931⟩

# Communication dans un congrès
1. Luis Alberto Pinos Ullauri, Anthony Fleury, Wim van den Noortgate, Alexis Lebis, Mathieu Vermeulen, et al.. Modelling the effect of courses over soft skills: A simulation study. 2023 AERA Annual Meeting, American Educational Research Association, Apr 2023, Chicago, United States. ⟨hal-04202625⟩
2. Alexis Lebis, Patrick Delaporte, Romain Deleau, Rémy Pinot, Mathieu Vermeulen. La pédagogie par projet agile abat ses cartes : une métaphore ludique au service de la pratique. 11ème Conférence Environnements Informatiques pour l’Apprentissage Humain (EIAH 2023), Jun 2023, Brest, France. ⟨hal-04148574⟩
3. Luis Alberto Pinos Ullauri, Alexis Lebis, Abir Karami, Mathieu Vermeulen, Anthony Fleury, et al.. Système de recommandation de cours basé sur les soft skills : Une approche utilisant les algorithmes génétiques. EIAH2023 : 11ème Conférence sur les Environnements Informatiques pour l'Apprentissage Humain, Association des Technologies de l’Information pour l’Education et la Formation (ATIEF), Jun 2023, Brest, France. pp.344-347. ⟨hal-04184360⟩

# Poster de conférence

# Proceedings/Recueil des communications

# N°spécial de revue/special issue

# Ouvrages

# Chapitre d'ouvrage

# Article de blog scientifique

# Notice d’encyclopédie ou de dictionnaire

# Traduction

# Brevet

# Autre publication scientifique

# Pré-publication, Document de travail

# Rapport

# Thèse

# HDR

# Cours

# Mémoire d'étudiant

# Image

# Vidéo

# Son

# Carte

# Logiciel
1. Alexis Lebis, Jérémie Humeau. Fully Individualized Curriculum with Decaying Knowledge Meta-Heurisitc Solver. 2023, ⟨swh:1:dir:411f53f49872171a9c3da7caeb967c17fddadcbd;origin=http://gvipers.imt-nord-europe.fr/m3tal/csdvp-evolutionary-algorithm-optimization;visit=swh:1:snp:634276c83e6780dfcdfb1dd5683f7dc970353e9e;anchor=swh:1:rev:54e03bbd717749bab8b70ba3ae5041d70f355ca3⟩. ⟨hal-04298620⟩

# Document associé à des manifestations scientifiques

# Chapitre de rapport

# Thèse d'établissement

# typdoc_MEMLIC

# Note de lecture

# Autre rapport, séminaire, workshop

# Rapport d'activité

# Notes de synthèse


=== Représentativité des domaines
* Education : 1
* Environnements Informatiques pour l'Apprentissage Humain : 4
```
