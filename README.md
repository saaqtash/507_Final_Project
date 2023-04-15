# 507_Final_Project

## **Introduction** <br>
The program aims at checking the drug interactions between a list of supplied drugs by a user and create a drug interaction network. It is a two part program. 
The part uses command line prompts asking the users to submit drug names to identify the RXCUI of those drugs. The name can be an ingredient, brand name, clinical dose form, branded dose form, clinical drug component, or branded drug component. The RXCUI codes identified will be used as inputs to a drug interaction API where drugs interactions will be identified and a network of drug interactions will be constructed. 

## **Data Sources**<br>
1- RXNorm API -- https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getDrugs.html <br>
2- Drug Interaction API -- https://lhncbc.nlm.nih.gov/RxNav/APIs/InteractionAPIs.html <br>

## **Run the Program**<br>
1- User is prompted to enter a medication name for RXCUI identification. <br>
2- A list of medications with similar names is produced. <br>
3- User will identify the RXCUI for the drug needed. <br>
4- The program will continue to prompt the user to enter drug names till the user enters quit. <br>
5- Next the user will be prompted to enter the RXCUIs into the drug interaction API. <br>
6- Drug interaction will be identified based on the RXCUIs entered. <br>
7- The interactions will be displayed as a network and a table will provide a summary of the interaction descriptions. <br>


## **Packages to Install:**<br>
pip install prettytable<br>
pip install networkx <br>
