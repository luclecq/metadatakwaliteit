# -*- coding: utf-8 -*-
# =================================================================================================================
# Controlescript metadatakwaliteit v0.6, december 2018
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

# Lokale bestandsnamen voor gebruik zonder opdrachtprompt (optioneel). Leeg laten voor gebruik via opdrachtprompt/batchbestand.
inputnaam_lokaal = r""
outputnaam_lokaal = r""

# Declareert de starttijd.
starttijd = datetime.datetime.now()

# Print de header.
print "Controlescript metadatakwaliteit v0.6, gemaakt door Luc van der Lecq \n"

# Controleert op de keuze voor lokale bestandsnamen.
if inputnaam_lokaal == "" and outputnaam_lokaal == "":
    # Controleert op het juiste aantal argumenten en of het bestand vanuit het opdrachtprompt/batchbestand bestaat.
    if len(sys.argv) != 3 or os.path.isfile(sys.argv[1]) != True:
        print "Er worden 2 argumenten verwacht: de bestandsnaam van het inputbestand (1) en de bestandsnaam van het outputbestand (2) \n"
        print "Het verwachte format is:" 
        print "<bestandsnaam van python.exe> <bestandsnaam van analyse script .py> <bestandsnaam van het inputbestand> <bestandsnaam van het outputbestand> \n"
        print "Voorbeeld:"
        print "C:\\Python27\\python.exe D:\\ov\\py\\luc\\rapport_geodata_analyse_v3.py D:\\ov\\rapport_geodata\\rapport_geodata_2018117.txt D:\\ov\\rapport_geodata\\rapport_geodata_2018117_analyse.txt \n" 
        sys.exit()
    # Gebruikt de bestandsnamen vanuit het opdrachtprompt/batchbestand voor de analyse.
    else:
        inputnaam = sys.argv[1]
        outputnaam = sys.argv[2]
else:
    # Controleert of het bestand vanuit de lokale bestandsnaam bestaat.
    if os.path.isfile(inputnaam_lokaal) != True:
        sys.exit("Controleer de bestandsnaam van 'inputnaam_lokaal' op regel 21.")
    # Gebruikt lokale bestandsnamen voor de analyse.
    else:
        inputnaam = inputnaam_lokaal
        outputnaam = outputnaam_lokaal

# Print melding voor tijdens de analyse.
print "Metadata controleren... \n"

# Importeert de data vanuit het inputbestand en legt de originele kopteksvolgorde vast.
with open(inputnaam, "r") as input:
    reader = csv.DictReader(input, delimiter=";", quoting=csv.QUOTE_ALL)
    kopteksten = reader.fieldnames
    data = [rij for rij in reader]

# Analyseert de data.
for dataset in data:
    # Voegt nieuwe, lege kolommen toe per dataset.
    dataset.update({
            "controle_totaal": "goed",
            "bronmetadata_afwezig": "nee",
            "verouderd_bestand": "nee",
            "fout_teken_titel": "nee", 
            "fout_teken_samenvatting": "nee", 
            "fout_teken_overige": "nee", 
            "fout_teken_karakter": "", 
            "fout_toepassingsschaal": "nee", 
            })

    # Controleert op aanwezigheid van bronmetadata.
    if dataset["bronmetadata_aanwezig"] != "Ja":
        dataset["controle_totaal"] = "bronmetadata afwezig"
        dataset["bronmetadata_afwezig"] = "ja"

    # Controleert op verouderde bestanden met een jaarlijkse herzieningsfrequentie.
    if dataset["herzieningsfrequentie"] == "Jaarlijks" and datetime.datetime.strptime(dataset["laatste_wijziging_bestandsbeschrijving"], "%Y-%m-%d") < (datetime.datetime.now() - datetime.timedelta(days=365)):
        if dataset["controle_totaal"] == "goed":
            dataset["controle_totaal"] = "verouderd bestand"
        else:
            dataset["controle_totaal"] += ", verouderd bestand"
        dataset["verouderd_bestand"] = "ja"
    # Controleert op verouderde bestanden met een 2-jaarlijkse herzieningsfrequentie.
    if dataset["herzieningsfrequentie"] == "2-jaarlijks" and datetime.datetime.strptime(dataset["laatste_wijziging_bestandsbeschrijving"], "%Y-%m-%d") < (datetime.datetime.now() - datetime.timedelta(days=730)):
        if dataset["controle_totaal"] == "goed":
            dataset["controle_totaal"] = "verouderd bestand"
        else:
            dataset["controle_totaal"] += ", verouderd bestand"
        dataset["verouderd_bestand"] = "ja"
    # Controleert op verouderde bestanden met een halfjaarlijkse herzieningsfrequentie.
    if dataset["herzieningsfrequentie"] == "1 x per half jaar" and datetime.datetime.strptime(dataset["laatste_wijziging_bestandsbeschrijving"], "%Y-%m-%d") < (datetime.datetime.now() - datetime.timedelta(days=183)):
        if dataset["controle_totaal"] == "goed":
            dataset["controle_totaal"] = "verouderd bestand"
        else:
            dataset["controle_totaal"] += ", verouderd bestand"
        dataset["verouderd_bestand"] = "ja"
    
    for item in dataset.iteritems():
        # Controleert op verboden karakters in de titel.
        if item[0] == "title":
            for karakter in "!@#$%^&*<>,.{}[]?/;:\'\"":
                if karakter in item[1]:
                    if dataset["controle_totaal"] == "goed":
                        dataset["controle_totaal"] = "fout teken in titel"
                    else:
                        dataset["controle_totaal"] += ", fout teken in titel"
                    dataset["fout_teken_titel"] = "ja"                    
                    if dataset["fout_teken_karakter"] == "":    
                        dataset["fout_teken_karakter"] = karakter
                    else:
                        dataset["fout_teken_karakter"] += " " + karakter
                    dataset["fout_teken_titel"] = "ja"
        # Controleert op verboden karakters in de samenvatting.       
        if item[0] == "abstract":
            for karakter in "&\\|{}[];":
                if karakter in item[1]:
                    if dataset["controle_totaal"] == "goed":
                        dataset["controle_totaal"] = "fout teken in samenvatting"
                    else:
                        dataset["controle_totaal"] += ", fout teken in samenvatting"
                    dataset["fout_teken_samenvatting"] = "ja"
                    if dataset["fout_teken_karakter"] == "":    
                        dataset["fout_teken_karakter"] = karakter
                    else:
                        dataset["fout_teken_karakter"] += " " + karakter
        # Controleert op verboden karakters in de resterende kolommen.
        if item[0] not in ("title", "abstract", "fout_teken_karakter"):
            for karakter in "&\\|{}[];":
                if karakter in item[1]:
                    if dataset["controle_totaal"] == "goed":
                        dataset["controle_totaal"] = "fout teken in " + item[0] 
                    else:
                        dataset["controle_totaal"] += ", fout teken in " + item[0]
                    dataset["fout_teken_overige"] = "ja"
                    if dataset["fout_teken_karakter"] == "":    
                        dataset["fout_teken_karakter"] = karakter
                    if karakter not in dataset["fout_teken_karakter"]:
                        dataset["fout_teken_karakter"] += " " + karakter

    # Controleert op toepassingsschalen onder de 500.
    if dataset["toepassingsschaal_van"] != "" and int(dataset["toepassingsschaal_van"]) < 500:
        if dataset["controle_totaal"] == "goed":
            dataset["controle_totaal"] = "fout toepassingsschaal"
        else:
            dataset["controle_totaal"] += ", fout toepassingsschaal"
        dataset["fout_toepassingsschaal"] = "ja"
    # Controleert op toepassingsschalen boven de miljard.
    if dataset["toepassingsschaal_tot"] != "" and int(dataset["toepassingsschaal_tot"]) > 1000000000:
        if dataset["controle_totaal"] == "goed":
            dataset["controle_totaal"] = "fout toepassingsschaal"
        else:
            dataset["controle_totaal"] += ", fout toepassingsschaal"
        dataset["fout_toepassingsschaal"] = "ja"

# Voegt de namen van de nieuwe kolommen toe aan de originele koptekstvolgorde.
kopteksten = [
        "controle_totaal",
        "bronmetadata_afwezig",
        "verouderd_bestand",
        "fout_teken_titel",
        "fout_teken_samenvatting",
        "fout_teken_overige",
        "fout_teken_karakter",
        "fout_toepassingsschaal",
        ] + kopteksten

# Exporteert de data naar het outputbestand.
with open(outputnaam, "w") as output:
    writer = csv.DictWriter(output, kopteksten, delimiter=";", quoting=csv.QUOTE_ALL)
    writer.writeheader()
    writer.writerows(data)

# Declareert variabelen met relevante informatie over de analyse.
eindtijd = datetime.datetime.now()
looptijd = eindtijd - starttijd
gelezen_regels = str(len(data))
datasets_melding = str(sum(1 for dataset in data if dataset["controle_totaal"] != "goed"))

# Genereert een logbestand met relevante informatie over de analyse.
ouputnaam_log = os.path.dirname(outputnaam) + "\\log_script_" + str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S")) + ".txt"
with open(ouputnaam_log, "w") as log:
    log.write(
            "Input:                          " + inputnaam + "\n" +
            "Output:                         " + outputnaam + "\n" +
            "Gelezen regels:                 " + gelezen_regels + "\n" +
            "Datasets met melding:           " + datasets_melding + "\n" +
            "Starttijd:                      " + starttijd.strftime("%H:%M:%S.%f") + "\n" +
            "Eindtijd:                       " + eindtijd.strftime("%H:%M:%S.%f") + "\n" +
            "Looptijd:                       00:" + str(looptijd)[2:]
            )

# Print relevante informatie over de analyse.
print "Gelezen regels:                 ", gelezen_regels, "\n"
print "Datasets met melding:           ", datasets_melding, "\n"
print "Starttijd:                      ", starttijd.strftime("%H:%M:%S"), "\n"
print "Eindtijd:                       ", eindtijd.strftime("%H:%M:%S"), "\n"
print "Looptijd:                        00:" + str(looptijd)[2:7], "\n"
print "De output is geschreven naar:   ", outputnaam
