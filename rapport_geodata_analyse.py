# -*- coding: utf-8 -*-
# =================================================================================================================
# Controlescript metadatakwaliteit v0.5, november 2018
# 
# Gemaakt door Luc van der Lecq als stageopdracht.
# Begeleiding door Gerard Nienhuis, Provincie Overijssel.

# Dit script automatiseert de controle van de metadatakwaliteit van datasets in het Overijsselse geoportaal.
# Gemaakt voor Python 2.7.15.
# Input: een puntkomma-gescheiden metadata-bestand met kolomnamen in de eerste rij.
# Output: identiek aan de input, plus een aantal controlekolommen.
# =================================================================================================================

# Importeert vereiste modules.
import csv
import datetime
import os
import sys

# Lokale bestandspaden voor gebruik zonder opdrachtprompt (optioneel). Leeg laten voor gebruik via opdrachtprompt/batchbestand.
inputpad_lokaal = r""
outputpad_lokaal = r""

# Declareert de starttijd.
starttijd = datetime.datetime.now().strftime("%H:%M:%S")

# Print de header.
print "Controlescript metadatakwaliteit v0.5, gemaakt door Luc van der Lecq \n"

# Controleert op de keuze voor lokale bestandspaden.
if inputpad_lokaal == "" and outputpad_lokaal == "":
    # Controleert op het juiste aantal argumenten en of het inputbestand vanuit het opdrachtprompt/batchbestand bestaat.
    if len(sys.argv) != 3 or os.path.isfile(sys.argv[1]) != True:
        print "Er worden 2 argumenten verwacht: het pad van het inputbestand (1) en het pad van het outputbestand (2) \n"
        print "Het verwachte format is:" 
        print "<bestandspad van python .exe> <bestandspad van analyse script .py> <bestandspad van het inputbestand> <bestandspad van het outputbestand> \n"
        print "Voorbeeld:"
        print "C:\\Python27\\python.exe D:\\ov\\py\\luc\\rapport_geodata_analyse_v3.py D:\\ov\\rapport_geodata\\rapport_geodata_2018117.txt D:\\ov\\rapport_geodata\\rapport_geodata_2018117_analyse.txt \n" 
        sys.exit()
    # Gebruikt inputpaden vanuit het opdrachtprompt/batchbestand voor de analyse.
    else:
        inputpad = sys.argv[1]
        outputpad = sys.argv[2]
else:
    # Controleert of het inputbestand vanuit het lokale inputpad bestaat.
    if os.path.isfile(inputpad_lokaal) != True:
        sys.exit("Controleer het bestandspad van 'inputpad_lokaal' op regel 21.")
    # Gebruikt lokale bestansdpaden voor de analyse.
    else:
        inputpad = inputpad_lokaal
        outputpad = outputpad_lokaal

# Print melding voor tijdens de analyse.
print "Metadata controleren... \n"

# Importeert de data vanuit het inputbestand.
with open(inputpad, "r") as input:
    reader = csv.DictReader(input, delimiter=";", quoting=csv.QUOTE_ALL)
    kopteksten = reader.fieldnames
    data = [rij for rij in reader]
    
# Analyseert de data.
for dataset in data:
    # Voegt nieuwe, lege kolommen toe per dataset
    dataset.update({"controle_totaal": "", "bronmetadata_afwezig": "", "fout_teken_titel": "", "fout_teken_abstract": ""})
    
    if dataset["bronmetadata_aanwezig"] != "Ja":
        dataset["controle_totaal"] = "Bronmetadata afwezig"
        dataset["bronmetadata_afwezig"] = "x"
    
    if any(karakter in dataset["title"] for karakter in "!@#$%^&*<>,.{}[]?/;:\'\""):
        if dataset["controle_totaal"] == "":
            dataset["controle_totaal"] = "fout teken in titel"
        else:
            dataset["controle_totaal"] += ", fout teken in titel"
        dataset["fout_teken_titel"] = "x"
    
    if any(karakter in dataset["abstract"] for karakter in "&\\|{}[];"):
        if dataset["controle_totaal"] == "":
            dataset["controle_totaal"] = "fout teken in samenvatting"
        else:
            dataset["controle_totaal"] += ", fout teken in samenvatting"
        dataset["fout_teken_abstract"] = "x"

# Voegt de namen van de nieuwe kolommen toe aan de originele headervolgorde.
kopteksten = ["controle_totaal", "bronmetadata_afwezig", "fout_teken_titel", "fout_teken_abstract"] + kopteksten

# Exporteert de data naar het outputbestand.
with open (outputpad, "w") as output:
    writer = csv.DictWriter(output, kopteksten, delimiter=";", quoting=csv.QUOTE_ALL)
    writer.writeheader()
    writer.writerows(data)

# Declareert de eindtijd.
eindtijd = datetime.datetime.now().strftime("%H:%M:%S")

# Print relevante informatie over de analyse.
print "Gelezen regels:                 ", len(data), "\n"
print "Datasets met melding:           ", sum(1 for dataset in data if dataset["controle_totaal"] != ""), "\n"
print "Starttijd:                      ", starttijd, "\n"
print "Eindtijd:                       ", eindtijd, "\n"
print "De output is geschreven naar:   ", os.path.basename(outputpad)
