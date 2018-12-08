# -*- coding: utf-8 -*-
# =================================================================================================================
# Controlescript metadatakwaliteit v0.7, december 2018
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

# Declareert variabelen met relevante informatie over de analyse (deel 1).
scriptnaam = os.path.abspath(__file__)
starttijd = datetime.datetime.now()

# Print de header.
print "Controlescript metadatakwaliteit v0.7, gemaakt door Luc van der Lecq \n"

# Controleert op de keuze voor lokale bestandsnamen.
if inputnaam_lokaal == "" and outputnaam_lokaal == "":
    # Controleert op het juiste aantal argumenten en of het bestand vanuit het opdrachtprompt/batchbestand bestaat.
    if len(sys.argv) != 3 or os.path.isfile(sys.argv[1]) != True:
        print "Er worden 2 argumenten verwacht: de bestandsnaam van het inputbestand (1) en de bestandsnaam van het outputbestand (2) \n"
        print "Het verwachte format is:" 
        print "<bestandsnaam van python.exe> <bestandsnaam van controleer_metadata_xx.py> <bestandsnaam van het inputbestand> <bestandsnaam van het outputbestand> \n"
        print "Voorbeeld:"
        print "C:\\Python27\\python.exe D:\\ov\\py\\luc\\controleer_metadata_07.py D:\\ov\\rapport_geodata\\rapport_geodata_2018126.txt D:\\ov\\rapport_geodata\\rapport_geodata_2018126_controle.txt \n" 
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

# ---------- Start data-analyse ----------

# Maakt een lijst van alle titels, samenvattingen en ID's tbv controle op uniciteit.
lijst_titel = []
lijst_samenvatting = []
lijst_identification = []
for dataset in data:
    lijst_titel.append(dataset["title"])
    lijst_samenvatting.append(dataset["abstract"])
    lijst_identification.append(dataset["identification"])
    
for dataset in data:
    # Voegt nieuwe, lege kolommen toe per dataset.
    dataset.update({
            "controle_totaal": "goed",
            "controle_fout": "nee",
            "controle_waarschuwing": "nee",
            "bronmetadata_afwezig": "nee",
            "verouderd_bestand": "nee",
            "fout_teken_titel": "nee",
            "fout_teken_titel_karakter": "",
            "fout_teken_samenvatting": "nee",
            "fout_teken_samenvatting_karakter": "",
            "fout_teken_namen": "nee",
            "fout_teken_namen_karakter": "",
            "fout_beperkingen": "nee",
            "fout_auteur_metadata": "nee",
            "fout_spelling_distributeur": "nee",
            "fout_uniciteit": "nee",             
            "fout_toepassingsschaal": "nee",
            "fout_spelling_land": "nee"
            })
            
    # Controleert op aanwezigheid van bronmetadata.
    if dataset["bronmetadata_aanwezig"] != "Ja":
        dataset["bronmetadata_afwezig"] = "ja"
        dataset["controle_fout"] = "ja"
        dataset["controle_totaal"] = "bronmetadata afwezig"

    # Controleert op verouderde bestanden met een jaarlijkse herzieningsfrequentie.
    if dataset["herzieningsfrequentie"] == "Jaarlijks" and datetime.datetime.strptime(dataset["laatste_wijziging_bestandsbeschrijving"], "%Y-%m-%d") < (datetime.datetime.now() - datetime.timedelta(days=365)):
        dataset["verouderd_bestand"] = "ja"
        dataset["controle_fout"] = "ja"
        if dataset["controle_totaal"] == "goed":
            dataset["controle_totaal"] = "verouderd bestand"
        else:
            dataset["controle_totaal"] += ", verouderd bestand"
    # Controleert op verouderde bestanden met een 2-jaarlijkse herzieningsfrequentie.
    if dataset["herzieningsfrequentie"] == "2-jaarlijks" and datetime.datetime.strptime(dataset["laatste_wijziging_bestandsbeschrijving"], "%Y-%m-%d") < (datetime.datetime.now() - datetime.timedelta(days=730)):
        dataset["verouderd_bestand"] = "ja"
        dataset["controle_fout"] = "ja"
        if dataset["controle_totaal"] == "goed":
            dataset["controle_totaal"] = "verouderd bestand"
        else:
            dataset["controle_totaal"] += ", verouderd bestand"
    # Controleert op verouderde bestanden met een halfjaarlijkse herzieningsfrequentie.
    if dataset["herzieningsfrequentie"] == "1 x per half jaar" and datetime.datetime.strptime(dataset["laatste_wijziging_bestandsbeschrijving"], "%Y-%m-%d") < (datetime.datetime.now() - datetime.timedelta(days=183)):
        dataset["verouderd_bestand"] = "ja"
        dataset["controle_fout"] = "ja"
        if dataset["controle_totaal"] == "goed":
            dataset["controle_totaal"] = "verouderd bestand"
        else:
            dataset["controle_totaal"] += ", verouderd bestand"
    
    for item in dataset.iteritems():
        # Controleert op verboden karakters in de titel.
        if item[0] == "title":
            for karakter in "!@#$%^&*<>,.{}[]?/;:\"":
                if karakter in item[1]:
                    dataset["fout_teken_titel"] = "ja"
                    if karakter in ":.":
                        dataset["controle_waarschuwing"] = "ja"
                    else:
                        dataset["controle_fout"] = "ja"
                    if dataset["fout_teken_titel_karakter"] == "":    
                        dataset["fout_teken_titel_karakter"] = karakter
                    if karakter not in dataset["fout_teken_titel_karakter"]:
                        dataset["fout_teken_titel_karakter"] += " " + karakter                                    
                    if dataset["controle_totaal"] == "goed":
                        dataset["controle_totaal"] = "fout teken in titel"
                    if "fout teken in titel" not in dataset["controle_totaal"]:
                        dataset["controle_totaal"] += ", fout teken in titel"

        # Controleert op verboden karakters in de samenvatting.       
        if item[0] == "abstract":
            for karakter in "&\\|{}[];":
                if karakter in item[1]:
                    dataset["fout_teken_samenvatting"] = "ja"
                    dataset["controle_waarschuwing"] = "ja"
                    if dataset["fout_teken_samenvatting_karakter"] == "":    
                        dataset["fout_teken_samenvatting_karakter"] = karakter
                    if karakter not in dataset["fout_teken_samenvatting_karakter"]:
                        dataset["fout_teken_samenvatting_karakter"] += " " + karakter                    
                    if dataset["controle_totaal"] == "goed":
                        dataset["controle_totaal"] = "fout teken in samenvatting"
                    if "fout teken in samenvatting" not in dataset["controle_totaal"]:
                        dataset["controle_totaal"] += ", fout teken in samenvatting"

        # Controleert op verboden karakters in kolommen met namen van contactpersonen en organisaties.
        if item[0] in (
                "auteur_metadata_naam_contactpersoon", 
                "auteur_metadata_naam_organisatie", 
                "bron_naam_contactpersoon_1",
                "bron_naam_contactpersoon_2",
                "bron_naam_contactpersoon_3",
                "bron_naam_contactpersoon_4",
                "bron_naam_organisatie_1",
                "bron_naam_organisatie_2",
                "bron_naam_organisatie_3",
                "bron_naam_organisatie_4",
                "distributeur_naam_contactpersoon",
                "distributeur_naam_organisatie"
                ):
            for karakter in "&\\|{}[];":
                if karakter in item[1]:
                    dataset["fout_teken_namen"] = "ja"
                    dataset["controle_waarschuwing"] = "ja"
                    if dataset["fout_teken_namen_karakter"] == "":    
                        dataset["fout_teken_namen_karakter"] = karakter
                    if karakter not in dataset["fout_teken_namen_karakter"]:
                        dataset["fout_teken_namen_karakter"] += " " + karakter                    
                    if dataset["controle_totaal"] == "goed":
                        dataset["controle_totaal"] = "fout teken in " + item[0] 
                    if item[0] not in dataset["controle_totaal"]:
                        dataset["controle_totaal"] += ", fout teken in " + item[0]
    
    # Controleert op niet ingevulde "other_constraints".
    if dataset["other_constraints"] == "":
        dataset["fout_beperkingen"] = "ja"
        dataset["controle_fout"] = "ja"
        if dataset["controle_totaal"] == "goed":
            dataset["controle_totaal"] = "fout beperkingen"
        else:
            dataset["controle_totaal"] += ", fout beperkingen"
    for cc in ("by", "mark", "zero"):
    # Controleert op wel een CC, maar interne data.    
        if cc in dataset["other_constraints"]:
            if ("intern gebruik" in dataset["use_limitation"]) or ("intern gebruik" in dataset["other_constraints"]):
                dataset["fout_beperkingen"] = "ja"
                dataset["controle_fout"] = "ja"
                if dataset["controle_totaal"] == "goed":
                    dataset["controle_totaal"] = "fout CC"
                if "fout CC" not in dataset["controle_totaal"]:
                    dataset["controle_totaal"] += ", fout CC"
    # Controleert op geen CC, maar wel publieke data.    
        if ("by" not in dataset["other_constraints"] and 
            "mark" not in dataset["other_constraints"] and
            "zero" not in dataset["other_constraints"] and
            dataset["data_publiek"] == "Ja"):
                dataset["fout_beperkingen"] = "ja"
                dataset["controle_waarschuwing"] = "ja"
                if dataset["controle_totaal"] == "goed":
                    dataset["controle_totaal"] = "publiek zonder CC"
                if "publiek zonder CC" not in dataset["controle_totaal"]:
                    dataset["controle_totaal"] += ", publiek zonder CC"
                
    # Controleert op wel CC-by of CC-mark, maar organisatie is Overijssel.    
    if "Provincie Overijssel" in dataset["distributeur_naam_organisatie"]:
        if "by" in dataset["other_constraints"]:
            dataset["fout_beperkingen"] = "ja"
            dataset["controle_fout"] = "ja"
            if dataset["controle_totaal"] == "goed":
                dataset["controle_totaal"] = "fout CC-by"
            else:
                dataset["controle_totaal"] += ", fout CC-by"
        if "mark" in dataset["other_constraints"]:
            dataset["fout_beperkingen"] = "ja"
            dataset["controle_fout"] = "ja"
            if dataset["controle_totaal"] == "goed":
                dataset["controle_totaal"] = "fout CC-mark"
            else:
                dataset["controle_totaal"] += ", fout CC-mark"
    # Controleert op wel CC-zero, maar organisatie is niet Overijssel.
    if "Provincie Overijssel" not in dataset["distributeur_naam_organisatie"]:
        if "zero" in dataset["other_constraints"]:
            dataset["fout_beperkingen"] = "ja"
            dataset["controle_fout"] = "ja"
            if dataset["controle_totaal"] == "goed":
                dataset["controle_totaal"] = "fout CC-zero"
            else:
                dataset["controle_totaal"] += ", fout CC-zero"

    # Controleert op Provincie Overijssel als auteur van de metadata.
    if dataset["auteur_metadata_naam_organisatie"] != "Provincie Overijssel":
        dataset["fout_auteur_metadata"] = "ja"
        dataset["controle_waarschuwing"] = "ja"
        if dataset["controle_totaal"] == "goed":
            dataset["controle_totaal"] = "fout auteur metadata"
        else:
            dataset["controle_totaal"] += ", fout auteur metadata"
    # Controleert op Provincie Overijssel als auteur van de metadata.
    if "Provincie Overijssel" in dataset["distributeur_naam_organisatie"]:
        if dataset["distributeur_naam_organisatie"] != "Provincie Overijssel":
            dataset["fout_spelling_distributeur"] = "ja"
            dataset["controle_waarschuwing"] = "ja"
            if dataset["controle_totaal"] == "goed":
                dataset["controle_totaal"] = "foute spelling distributeur"
            else:
                dataset["controle_totaal"] += ", foute spelling distributeur"

    # Controleert op uniciteit van titel, samenvatting en ID's
    if lijst_titel.count(dataset["title"]) > 1:
        dataset["fout_uniciteit"] = "ja"
        dataset["controle_fout"] = "ja"
        if dataset["controle_totaal"] == "goed":
            dataset["controle_totaal"] = "titel niet uniek"
        else:
            dataset["controle_totaal"] += ", titel niet uniek"
    if lijst_samenvatting.count(dataset["abstract"]) > 1:
        dataset["fout_uniciteit"] = "ja"
        dataset["controle_fout"] = "ja"
        if dataset["controle_totaal"] == "goed":
            dataset["controle_totaal"] = "samenvatting niet uniek"
        else:
            dataset["controle_totaal"] += ", samenvatting niet uniek" 
    if lijst_identification.count(dataset["identification"]) > 1:
        dataset["fout_uniciteit"] = "ja"
        dataset["controle_fout"] = "ja"
        if dataset["controle_totaal"] == "goed":
            dataset["controle_totaal"] = "identification niet uniek"
        else:
            dataset["controle_totaal"] += ", identification niet uniek" 

    # Controleert op niet ingevulde toepassingsschalen.
    if dataset["toepassingsschalen"] == "":
        dataset["fout_toepassingsschaal"] = "ja"
        dataset["controle_waarschuwing"] = "ja"
        if dataset["controle_totaal"] == "goed":
            dataset["controle_totaal"] = "fout toepassingsschaal"
        else:
            dataset["controle_totaal"] += ", fout toepassingsschaal"        
    # Controleert op toepassingsschalen waarbij het minimum groter is dan het maximum en vv.
    if dataset["toepassingsschaal_van"] != "" and dataset["toepassingsschaal_tot"] != "":
        if int(dataset["toepassingsschaal_van"]) > int(dataset["toepassingsschaal_tot"]):
            dataset["fout_toepassingsschaal"] = "ja"
            dataset["controle_fout"] = "ja"
            if dataset["controle_totaal"] == "goed":
                dataset["controle_totaal"] = "fout toepassingsschaal"
            else:
                dataset["controle_totaal"] += ", fout toepassingsschaal"
        if int(dataset["toepassingsschaal_van"]) == int(dataset["toepassingsschaal_tot"]):
            dataset["fout_toepassingsschaal"] = "ja"
            dataset["controle_waarschuwing"] = "ja"
            if dataset["controle_totaal"] == "goed":
                dataset["controle_totaal"] = "fout toepassingsschaal"
            else:
                dataset["controle_totaal"] += ", fout toepassingsschaal"
    # Controleert op toepassingsschalen onder de 100.
    if dataset["toepassingsschaal_van"] != "" and int(dataset["toepassingsschaal_van"]) < 100:
        dataset["fout_toepassingsschaal"] = "ja"
        dataset["controle_waarschuwing"] = "ja"
        if dataset["controle_totaal"] == "goed":
            dataset["controle_totaal"] = "fout toepassingsschaal"
        else:
            dataset["controle_totaal"] += ", fout toepassingsschaal"
    # Controleert op toepassingsschalen boven de 500.000.
    if dataset["toepassingsschaal_tot"] != "" and int(dataset["toepassingsschaal_tot"]) > 500000:
        dataset["fout_toepassingsschaal"] = "ja"
        dataset["controle_waarschuwing"] = "ja"
        if dataset["controle_totaal"] == "goed":
            dataset["controle_totaal"] = "fout toepassingsschaal"
        else:
            dataset["controle_totaal"] += ", fout toepassingsschaal"

    # Controleert op correcte spelling van de landsnaam van contactpersonen en organisaties.
    for item in dataset.iteritems():
        if item[0] in (
                "auteur_metadata_land_contactpersoon",
                "bron_land_contactpersoon_1",
                "bron_land_contactpersoon_2"
                "bron_land_contactpersoon_3",
                "bron_land_contactpersoon_4",
                "distributeur_land_contactpersoon"
                ):
            if item[1] not in ("Nederland", ""):
                dataset["fout_spelling_land"] = "ja"
                dataset["controle_waarschuwing"] = "ja"
                if dataset["controle_totaal"] == "goed":
                    dataset["controle_totaal"] = "foute spelling land in " + item[0]
                else:
                    dataset["controle_totaal"] += ", foute spelling land in " + item[0]

# ---------- Einde data-analyse ----------

# Voegt de namen van de nieuwe kolommen toe aan de originele koptekstvolgorde.
kopteksten = [
        "controle_totaal",
        "controle_fout",
        "controle_waarschuwing",
        "bronmetadata_afwezig",
        "verouderd_bestand",
        "fout_teken_titel",
        "fout_teken_titel_karakter",       
        "fout_teken_samenvatting",
        "fout_teken_samenvatting_karakter",        
        "fout_teken_namen",
        "fout_teken_namen_karakter",
        "fout_beperkingen",
        "fout_auteur_metadata",
        "fout_spelling_distributeur",
        "fout_uniciteit",
        "fout_toepassingsschaal",
        "fout_spelling_land"
        ] + kopteksten

# Exporteert de data naar het outputbestand.
with open(outputnaam, "w") as output:
    writer = csv.DictWriter(output, kopteksten, delimiter=";", quoting=csv.QUOTE_ALL)
    writer.writeheader()
    writer.writerows(data)

# Declareert variabelen met relevante informatie over de analyse (deel 2).
gelezen_regels = str(len(data))
datasets_fout = str(sum(1 for dataset in data if dataset["controle_fout"] != "nee"))
datasets_waarschuwing = str(sum(1 for dataset in data if (dataset["controle_waarschuwing"] != "nee") and dataset["controle_fout"] == "nee"))
eindtijd = datetime.datetime.now()
looptijd = str(eindtijd - starttijd)

# Genereert een logbestand met relevante informatie over de analyse.
ouputnaam_log = os.path.dirname(outputnaam) + "\\log_script_" + eindtijd.strftime("%Y%m%d_%H%M%S") + ".txt"
with open(ouputnaam_log, "w") as log:
    log.write(
            "Scriptnaam:                     " + scriptnaam + "\n" +
            "Inputnaam:                      " + inputnaam + "\n" +
            "Outputnaam:                     " + outputnaam + "\n" +
            "Gelezen regels:                 " + gelezen_regels + "\n" +
            "Datasets met fout:              " + datasets_fout + "\n" +
            "Datasets met waarschuwing:      " + datasets_waarschuwing + "\n" +
            "Starttijd:                      " + starttijd.strftime("%H:%M:%S.%f") + "\n" +
            "Eindtijd:                       " + eindtijd.strftime("%H:%M:%S.%f") + "\n" +
            "Looptijd:                       00:" + looptijd[2:]
            )

# Print relevante informatie over de analyse.
print "Gelezen regels:                 " + gelezen_regels + "\n"
print "Datasets met fout:              " + datasets_fout + "\n"
print "Datasets met waarschuwing:      " + datasets_waarschuwing + "\n"
print "Starttijd:                      " + starttijd.strftime("%H:%M:%S") + "\n"
print "Eindtijd:                       " + eindtijd.strftime("%H:%M:%S") + "\n"
print "Looptijd:                       " + "00:" + looptijd[2:7] + "\n"
print "De output is geschreven naar:   " + outputnaam
