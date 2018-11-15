# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Versie 3, 13 november 2018
# 
# Luc van der Lecq
# Stageopdracht
# Begeleiding door Gerard Nienhuis
# Dit script is een poging om de controle van de metadatakwaliteit te automatiseren.
# Gemaakt voor Python 2.7.15
#
# Input: een puntkomma-gescheiden bestand met kolomnamen in de eerste rij
# -----------------------------------------------------------------------------

import sys
import os
import csv

# Tijdelijke paden om te testen 
#inputpad = "D:/scratch/rapport_geodata_test.txt"
#outputpad = "D:/scratch/rapport_geodata_test_analyse.txt"

def uitleg():
    print "Er worden 2 argumenten verwacht: het pad van het inputbestand (1) en het pad van het outputbestand (2)"
    print "Het verwachte format is:" 
    print "<bestandspad van python .exe> <bestandspad van analyse script .py> <bestandspad van het inputbestand> <bestandspad van het outputbestand>"
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
    with open(inputpad, "rb") as input:
        reader = csv.DictReader(input, delimiter=";", quoting=csv.QUOTE_ALL)
        data = [rij for rij in reader]
        # Analyse
        for dataset in data:
            if dataset["bronmetadata_aanwezig"] != "Ja":
                dataset["controle_totaal"]="Technische fout"
            else:
                dataset["controle_totaal"]=""
    # Export
    headers = data[0].keys()    
    with open (outputpad, "wb") as output:
        writer = csv.DictWriter(output, headers, delimiter=";", quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(data)
    print "Outputbestand gegenereerd."
