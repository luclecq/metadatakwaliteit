# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Controlescript metadatakwaliteit V0.4, november 2018
# 
# Luc van der Lecq
# Stageopdracht
# Begeleiding door Gerard Nienhuis
# Dit script is een poging om de controle van de metadatakwaliteit te automatiseren.
# Gemaakt voor Python 2.7.15
#
# Input: een puntkomma-gescheiden bestand met kolomnamen in de eerste rij
# -----------------------------------------------------------------------------

import csv
import datetime
import os
import sys

# Tijdelijke paden om te testen 
#inputpad = "D:/scratch/rapport_geodata_test.txt"
#outputpad = "D:/scratch/rapport_geodata_test_analyse.txt"

starttijd = datetime.datetime.now().strftime("%H:%M:%S")
print "Controlescript metadatakwaliteit V0.4, gemaakt door Luc van der Lecq \n"

def uitleg():
    print "Er worden 2 argumenten verwacht: het pad van het inputbestand (1) en het pad van het outputbestand (2) \n"
    print "Het verwachte format is:" 
    print "<bestandspad van python .exe> <bestandspad van analyse script .py> <bestandspad van het inputbestand> <bestandspad van het outputbestand> \n"
    print "Voorbeeld:"
    print "C:\\Python27\\python.exe D:\\ov\\py\\luc\\rapport_geodata_analyse_v3.py D:\\ov\\rapport_geodata\\rapport_geodata_2018117.txt D:\\ov\\rapport_geodata\\rapport_geodata_2018117_analyse.txt" 

# Controleert op het juiste aantal argumenten en of het inputbestand bestaat.
if len(sys.argv) != 3:
    uitleg()
elif os.path.isfile(sys.argv[1]) != True:
    uitleg()
else:
    # Import    
    inputpad = sys.argv[1]
    outputpad = sys.argv[2]
    with open(inputpad, "r") as input:
        reader = csv.DictReader(input, delimiter=";", quoting=csv.QUOTE_ALL)
        headers = reader.fieldnames
        data = [rij for rij in reader]
        # Analyse
        for dataset in data:
            if dataset["bronmetadata_aanwezig"] != "Ja":
                dataset["controle_totaal"]="De xml is verwijderd, maar de data staat nog in service"
            else:
                dataset["controle_totaal"]=""
        headers.insert(0, "controle_totaal")
    # Export
    with open (outputpad, "w") as output:
        writer = csv.DictWriter(output, headers, delimiter=";", quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(data)
    eindtijd = datetime.datetime.now().strftime("%H:%M:%S")
    print "Gelezen regels:                 ", len(data), "\n"
    print "Starttijd:                      ", starttijd, "\n"
    print "Eindtijd:                       ", eindtijd, "\n"
    print "De output is geschreven naar:   ", os.path.basename(outputpad)
