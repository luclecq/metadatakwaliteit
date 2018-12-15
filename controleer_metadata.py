# -*- coding: utf-8 -*-
# =================================================================================================================
# Controlescript metadatakwaliteit v1.0, december 2018
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
print "Controlescript metadatakwaliteit v1.0, gemaakt door Luc van der Lecq \n"

# Controleert op de keuze voor lokale bestandsnamen.
if inputnaam_lokaal == "" and outputnaam_lokaal == "":
    # Controleert op het juiste aantal argumenten en of het bestand vanuit het opdrachtprompt/batchbestand bestaat.
    if len(sys.argv) != 3 or os.path.isfile(sys.argv[1]) != True:
        print "Er worden 2 argumenten verwacht: de bestandsnaam van het inputbestand (1) en de bestandsnaam van het outputbestand (2) \n"
        print "Het verwachte format is:" 
        print "<bestandsnaam van python.exe> <bestandsnaam van controleer_metadata_xx.py> <bestandsnaam van het inputbestand> <bestandsnaam van het outputbestand> \n"
        print "Voorbeeld:"
        print "C:\\Python27\\python.exe D:\\ov\\py\\luc\\controleer_metadata_10.py D:\\ov\\rapport_geodata\\rapport_geodata_20181217.txt D:\\ov\\rapport_geodata\\rapport_geodata_20181217_controle.txt \n" 
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

# ---------- Start metadata-controle ----------

# Maakt een lijst van alle titels, alternatieve titels, samenvattingen en ID's tbv controle op uniciteit.
lijst_titel = []
lijst_alternatieve_titel = []
lijst_samenvatting = []
lijst_identification = []
email_dict_1 = {}
naam_dict_1 = {}
for dataset in data:
    lijst_titel.append(dataset["title"])
    lijst_alternatieve_titel.append(dataset["alternate_title"])
    lijst_samenvatting.append(dataset["abstract"])
    lijst_identification.append(dataset["identification"])
    if not dataset["bron_email_contactpersoon_1"] in email_dict_1:
        email_dict_1[dataset["bron_email_contactpersoon_1"].decode("utf-8")] = dataset["bron_naam_contactpersoon_1"]
    if not dataset["bron_naam_contactpersoon_1"] in naam_dict_1:
        naam_dict_1[dataset["bron_naam_contactpersoon_1"].decode("utf-8")] = dataset["bron_email_contactpersoon_1"]

for dataset in data:
    # Voegt nieuwe kolommen toe per dataset.
    dataset.update({
            "controle_totaal": "goed",
            "controle_fout": "nee",
            "controle_fout_aantal": 0,
            "controle_fout_detail": "",
            "controle_waarschuwing": "nee",
            "controle_waarschuwing_aantal": 0,
            "controle_waarschuwing_detail": "",
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
            "fout_lengte_samenvatting": "nee",
            "fout_lengte_titel": "nee",
            "fout_spelling_land": "nee",
#            "fout_https": "nee",
            "fout_combinatie_naam_email": "nee"
            })
         
    # Controleert op aanwezigheid van bronmetadata.
    if dataset["bronmetadata_aanwezig"] != "Ja":
        dataset["bronmetadata_afwezig"] = "ja"
        dataset["controle_fout"] = "ja"
        if dataset["controle_fout_detail"] == "":
            dataset["controle_fout_detail"] = "bronmetadata afwezig"
        else:
            dataset["controle_fout_detail"] += ", bronmetadata afwezig"        
        if dataset["controle_totaal"] == "goed":
            dataset["controle_totaal"] = "bronmetadata afwezig"
        else:
            dataset["controle_totaal"] += ", bronmetadata afwezig"

    # Controleert op verouderde bestanden met een 2-jaarlijkse herzieningsfrequentie.
    if dataset["herzieningsfrequentie"] == "2-jaarlijks" and datetime.datetime.strptime(dataset["laatste_wijziging_bestandsbeschrijving"], "%Y-%m-%d") < (datetime.datetime.now() - datetime.timedelta(days=730)):
        dataset["verouderd_bestand"] = "ja"
        dataset["controle_fout"] = "ja"
        if dataset["controle_fout_detail"] == "":
            dataset["controle_fout_detail"] = "verouderd bestand"
        else:
            dataset["controle_fout_detail"] += ", verouderd bestand"        
        if dataset["controle_totaal"] == "goed":
            dataset["controle_totaal"] = "verouderd bestand"
        else:
            dataset["controle_totaal"] += ", verouderd bestand"
    # Controleert op verouderde bestanden met een jaarlijkse herzieningsfrequentie.
    if dataset["herzieningsfrequentie"] == "Jaarlijks" and datetime.datetime.strptime(dataset["laatste_wijziging_bestandsbeschrijving"], "%Y-%m-%d") < (datetime.datetime.now() - datetime.timedelta(days=365)):
        dataset["verouderd_bestand"] = "ja"
        dataset["controle_fout"] = "ja"
        if dataset["controle_fout_detail"] == "":
            dataset["controle_fout_detail"] = "verouderd bestand"
        else:
            dataset["controle_fout_detail"] += ", verouderd bestand"        
        if dataset["controle_totaal"] == "goed":
            dataset["controle_totaal"] = "verouderd bestand"
        else:
            dataset["controle_totaal"] += ", verouderd bestand"
    # Controleert op verouderde bestanden met een halfjaarlijkse herzieningsfrequentie.
    if dataset["herzieningsfrequentie"] == "1 x per half jaar" and datetime.datetime.strptime(dataset["laatste_wijziging_bestandsbeschrijving"], "%Y-%m-%d") < (datetime.datetime.now() - datetime.timedelta(days=183)):
        dataset["verouderd_bestand"] = "ja"
        dataset["controle_fout"] = "ja"
        if dataset["controle_fout_detail"] == "":
            dataset["controle_fout_detail"] = "verouderd bestand"
        else:
            dataset["controle_fout_detail"] += ", verouderd bestand"        
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
                    if karakter in ":.,":
                        dataset["controle_waarschuwing"] = "ja"
                        if dataset["controle_waarschuwing_detail"] == "":
                            dataset["controle_waarschuwing_detail"] = "fout teken in titel"
                        if "fout teken in titel" not in dataset["controle_waarschuwing_detail"]:
                            dataset["controle_waarschuwing_detail"] += ", fout teken in titel"
                    else:
                        dataset["controle_fout"] = "ja"
                        if dataset["controle_fout_detail"] == "":
                            dataset["controle_fout_detail"] = "fout teken in titel"
                        if "fout teken in titel" not in dataset["controle_fout_detail"]:
                            dataset["controle_fout_detail"] += ", fout teken in titel"                        
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
                    if dataset["controle_waarschuwing_detail"] == "":
                        dataset["controle_waarschuwing_detail"] = "fout teken in samenvatting"
                    if "fout teken in samenvatting" not in dataset["controle_waarschuwing_detail"]:
                        dataset["controle_waarschuwing_detail"] += ", fout teken in samenvatting"                    
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
            for karakter in "&\\|{}[]":
                if karakter in item[1]:
                    dataset["fout_teken_namen"] = "ja"
                    dataset["controle_waarschuwing"] = "ja"
                    if dataset["controle_waarschuwing_detail"] == "":
                        dataset["controle_waarschuwing_detail"] = "fout teken in " + item[0] 
                    if item[0] not in dataset["controle_waarschuwing_detail"]:
                        dataset["controle_waarschuwing_detail"] += ", fout teken in " + item[0]                    
                    if dataset["fout_teken_namen_karakter"] == "":    
                        dataset["fout_teken_namen_karakter"] = karakter
                    if karakter not in dataset["fout_teken_namen_karakter"]:
                        dataset["fout_teken_namen_karakter"] += " " + karakter                    
                    if dataset["controle_totaal"] == "goed":
                        dataset["controle_totaal"] = "fout teken in " + item[0] 
                    if item[0] not in dataset["controle_totaal"]:
                        dataset["controle_totaal"] += ", fout teken in " + item[0]

    for cc in ("by", "mark", "zero"):
    # Controleert op wel een CC, maar interne data.    
        if cc in dataset["other_constraints"]:
            if ("intern gebruik" in dataset["use_limitation"]) or ("intern gebruik" in dataset["other_constraints"]):
                dataset["fout_beperkingen"] = "ja"
                dataset["controle_fout"] = "ja"
                if dataset["controle_fout_detail"] == "":
                    dataset["controle_fout_detail"] = "fout CC"
                if "fout CC" not in dataset["controle_fout_detail"]:
                    dataset["controle_fout_detail"] += ", fout CC"                
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
                if dataset["controle_waarschuwing_detail"] == "":
                    dataset["controle_waarschuwing_detail"] = "publiek zonder CC"
                if "publiek zonder CC" not in dataset["controle_waarschuwing_detail"]:
                    dataset["controle_waarschuwing_detail"] += ", publiek zonder CC"                
                if dataset["controle_totaal"] == "goed":
                    dataset["controle_totaal"] = "publiek zonder CC"
                if "publiek zonder CC" not in dataset["controle_totaal"]:
                    dataset["controle_totaal"] += ", publiek zonder CC"
                
    # Controleert op wel CC-by of CC-mark, maar distributeur is Overijssel.    
    if "Provincie Overijssel" in dataset["distributeur_naam_organisatie"]:
        if "by" in dataset["other_constraints"]:
            dataset["fout_beperkingen"] = "ja"
            dataset["controle_fout"] = "ja"
            if dataset["controle_fout_detail"] == "":
                dataset["controle_fout_detail"] = "fout CC-by"
            else:
                dataset["controle_fout_detail"] += ", fout CC-by"            
            if dataset["controle_totaal"] == "goed":
                dataset["controle_totaal"] = "fout CC-by"
            else:
                dataset["controle_totaal"] += ", fout CC-by"
        if "mark" in dataset["other_constraints"]:
            dataset["fout_beperkingen"] = "ja"
            dataset["controle_fout"] = "ja"
            if dataset["controle_fout_detail"] == "":
                dataset["controle_fout_detail"] = "fout CC-mark"
            else:
                dataset["controle_fout_detail"] += ", fout CC-mark"            
            if dataset["controle_totaal"] == "goed":
                dataset["controle_totaal"] = "fout CC-mark"
            else:
                dataset["controle_totaal"] += ", fout CC-mark"
    # Controleert op wel CC-zero, maar distributeur is niet Overijssel.
    if "Provincie Overijssel" not in dataset["distributeur_naam_organisatie"]:
        if "zero" in dataset["other_constraints"]:
            dataset["fout_beperkingen"] = "ja"
            dataset["controle_fout"] = "ja"
            if dataset["controle_fout_detail"] == "":
                dataset["controle_fout_detail"] = "fout CC-zero"
            else:
                dataset["controle_fout_detail"] += ", fout CC-zero"            
            if dataset["controle_totaal"] == "goed":
                dataset["controle_totaal"] = "fout CC-zero"
            else:
                dataset["controle_totaal"] += ", fout CC-zero"

    # Controleert op Provincie Overijssel als auteur van de metadata.
    if dataset["auteur_metadata_naam_organisatie"] != "Provincie Overijssel":
        dataset["fout_auteur_metadata"] = "ja"
        dataset["controle_waarschuwing"] = "ja"
        if dataset["controle_waarschuwing_detail"] == "":
            dataset["controle_waarschuwing_detail"] = "fout auteur metadata"
        else:
            dataset["controle_waarschuwing_detail"] += ", fout auteur metadata"        
        if dataset["controle_totaal"] == "goed":
            dataset["controle_totaal"] = "fout auteur metadata"
        else:
            dataset["controle_totaal"] += ", fout auteur metadata"
    # Controleert op de spelling van Provincie Overijssel als distributeur.
    if "Provincie Overijssel" in dataset["distributeur_naam_organisatie"]:
        if dataset["distributeur_naam_organisatie"] != "Provincie Overijssel":
            dataset["fout_spelling_distributeur"] = "ja"
            dataset["controle_waarschuwing"] = "ja"
            if dataset["controle_waarschuwing_detail"] == "":
                dataset["controle_waarschuwing_detail"] = "foute spelling distributeur"
            else:
                dataset["controle_waarschuwing_detail"] += ", foute spelling distributeur"            
            if dataset["controle_totaal"] == "goed":
                dataset["controle_totaal"] = "foute spelling distributeur"
            else:
                dataset["controle_totaal"] += ", foute spelling distributeur"

    # Controleert op uniciteit van titel, alternatieve titel, samenvatting en ID's
    if lijst_titel.count(dataset["title"]) > 1:
        dataset["fout_uniciteit"] = "ja"
        dataset["controle_fout"] = "ja"
        if dataset["controle_fout_detail"] == "":
            dataset["controle_fout_detail"] = "titel niet uniek"
        else:
            dataset["controle_fout_detail"] += ", titel niet uniek"        
        if dataset["controle_totaal"] == "goed":
            dataset["controle_totaal"] = "titel niet uniek"
        else:
            dataset["controle_totaal"] += ", titel niet uniek"
    if lijst_alternatieve_titel.count(dataset["alternate_title"]) > 1:
        dataset["fout_uniciteit"] = "ja"
        dataset["controle_fout"] = "ja"
        if dataset["controle_fout_detail"] == "":
            dataset["controle_fout_detail"] = "alternatieve titel niet uniek"
        else:
            dataset["controle_fout_detail"] += ", alternative titel niet uniek"        
        if dataset["controle_totaal"] == "goed":
            dataset["controle_totaal"] = "alternatieve titel niet uniek"
        else:
            dataset["controle_totaal"] += ", alternatieve titel niet uniek"
    if lijst_samenvatting.count(dataset["abstract"]) > 1:
        dataset["fout_uniciteit"] = "ja"
        dataset["controle_waarschuwing"] = "ja"
        if dataset["controle_waarschuwing_detail"] == "":
            dataset["controle_waarschuwing_detail"] = "samenvatting niet uniek"
        else:
            dataset["controle_waarschuwing_detail"] += ", samenvatting niet uniek"        
        if dataset["controle_totaal"] == "goed":
            dataset["controle_totaal"] = "samenvatting niet uniek"
        else:
            dataset["controle_totaal"] += ", samenvatting niet uniek" 
    if lijst_identification.count(dataset["identification"]) > 1:
        dataset["fout_uniciteit"] = "ja"
        dataset["controle_fout"] = "ja"
        if dataset["controle_fout_detail"] == "":
            dataset["controle_fout_detail"] = "identification niet uniek"
        else:
            dataset["controle_fout_detail"] += ", identification niet uniek"         
        if dataset["controle_totaal"] == "goed":
            dataset["controle_totaal"] = "identification niet uniek"
        else:
            dataset["controle_totaal"] += ", identification niet uniek" 
        
    if dataset["toepassingsschaal_van"] != "" and dataset["toepassingsschaal_tot"] != "":
        # Controleert op toepassingsschalen waarbij het minimum groter is dan het maximum en vv.        
        if int(dataset["toepassingsschaal_van"]) > int(dataset["toepassingsschaal_tot"]):
            dataset["fout_toepassingsschaal"] = "ja"
            dataset["controle_fout"] = "ja"
            if dataset["controle_fout_detail"] == "":
                dataset["controle_fout_detail"] = "fout toepassingsschaal"
            else:
                dataset["controle_fout_detail"] += ", fout toepassingsschaal"            
            if dataset["controle_totaal"] == "goed":
                dataset["controle_totaal"] = "fout toepassingsschaal"
            else:
                dataset["controle_totaal"] += ", fout toepassingsschaal"
        # Controleert op toepassingsschalen waarbij het minimum en het maximum gelijk zijn.        
        if int(dataset["toepassingsschaal_van"]) == int(dataset["toepassingsschaal_tot"]):
            dataset["fout_toepassingsschaal"] = "ja"
            dataset["controle_waarschuwing"] = "ja"
            if dataset["controle_waarschuwing_detail"] == "":
                dataset["controle_waarschuwing_detail"] = "fout toepassingsschaal"
            else:
                dataset["controle_waarschuwing_detail"] += ", fout toepassingsschaal"            
            if dataset["controle_totaal"] == "goed":
                dataset["controle_totaal"] = "fout toepassingsschaal"
            else:
                dataset["controle_totaal"] += ", fout toepassingsschaal"
    # Controleert op toepassingsschalen onder de 100.
    if dataset["toepassingsschaal_van"] != "" and int(dataset["toepassingsschaal_van"]) < 100:
        dataset["fout_toepassingsschaal"] = "ja"
        dataset["controle_waarschuwing"] = "ja"
        if dataset["controle_waarschuwing_detail"] == "":
            dataset["controle_waarschuwing_detail"] = "fout toepassingsschaal"
        else:
            dataset["controle_waarschuwing_detail"] += ", fout toepassingsschaal"            
        if dataset["controle_totaal"] == "goed":
            dataset["controle_totaal"] = "fout toepassingsschaal"
        else:
            dataset["controle_totaal"] += ", fout toepassingsschaal"
    # Controleert op toepassingsschalen boven de 500.000.
    if dataset["toepassingsschaal_tot"] != "" and int(dataset["toepassingsschaal_tot"]) > 500000:
        dataset["fout_toepassingsschaal"] = "ja"
        dataset["controle_waarschuwing"] = "ja"
        if dataset["controle_waarschuwing_detail"] == "":
            dataset["controle_waarschuwing_detail"] = "fout toepassingsschaal"
        else:
            dataset["controle_waarschuwing_detail"] += ", fout toepassingsschaal"      
        if dataset["controle_totaal"] == "goed":
            dataset["controle_totaal"] = "fout toepassingsschaal"
        else:
            dataset["controle_totaal"] += ", fout toepassingsschaal"

    # Controleert op het aantal karakters van titel en samenvatting dat buiten bepaalde grenswaarden ligt.
    if len(dataset["abstract"]) > 2000:
        dataset["fout_lengte_samenvatting"] = "ja"
        dataset["controle_fout"] = "ja"
        if dataset["controle_fout_detail"] == "":
            dataset["controle_fout_detail"] = "samenvatting te lang"
        else:
            dataset["controle_fout_detail"] += ", samenvatting te lang"      
        if dataset["controle_totaal"] == "goed":
            dataset["controle_totaal"] = "samenvatting te lang"
        else:
            dataset["controle_totaal"] += ", samenvatting te lang"
    if len(dataset["abstract"]) < 100:
        dataset["fout_lengte_samenvatting"] = "ja"
        dataset["controle_waarschuwing"] = "ja"
        if dataset["controle_waarschuwing_detail"] == "":
            dataset["controle_waarschuwing_detail"] = "samenvatting kort"
        else:
            dataset["controle_waarschuwing_detail"] += ", samenvatting kort"      
        if dataset["controle_totaal"] == "goed":
            dataset["controle_totaal"] = "samenvatting kort"
        else:
            dataset["controle_totaal"] += ", samenvatting kort"
    if len(dataset["title"]) < 10:
        dataset["fout_lengte_titel"] = "ja"
        dataset["controle_waarschuwing"] = "ja"
        if dataset["controle_waarschuwing_detail"] == "":
            dataset["controle_waarschuwing_detail"] = "titel kort"
        else:
            dataset["controle_waarschuwing_detail"] += ", titel kort"      
        if dataset["controle_totaal"] == "goed":
            dataset["controle_totaal"] = "titel kort"
        else:
            dataset["controle_totaal"] += ", titel kort"        
    if len(dataset["title"]) > 100:
        dataset["fout_lengte_titel"] = "ja"
        dataset["controle_waarschuwing"] = "ja"
        if dataset["controle_waarschuwing_detail"] == "":
            dataset["controle_waarschuwing_detail"] = "titel lang"
        else:
            dataset["controle_waarschuwing_detail"] += ", titel lang"      
        if dataset["controle_totaal"] == "goed":
            dataset["controle_totaal"] = "titel lang"
        else:
            dataset["controle_totaal"] += ", titel lang"    

    # Controleert op het gebruik van https in url's van websites van contactpersonen en organisaties.
#    for item in dataset.iteritems():
#        if item[0] in (
#                "auteur_metadata_website_organisatie",
#                "distributeur_website_organisatie",
#                "bron_website_organisatie_1",
#                "bron_website_organisatie_2",
#                "bron_website_organisatie_3",
#                "bron_website_organisatie_4"
#                ):
#            if item[1] != "":
#                if "https" not in item[1]:
#                    dataset["fout_https"] = "ja"
#                    if item[0] == "bron_website_organisatie_1":
#                        dataset["controle_fout"] = "ja"
#                        if dataset["controle_fout_detail"] == "":
#                            dataset["controle_fout_detail"] = "fout https in contactpersoon 1"
#                        if "fout https in contactpersoon 1" not in dataset["controle_fout_detail"]:
#                            dataset["controle_fout_detail"] += ", fout https in contactpersoon 1"
#                        if dataset["controle_totaal"] == "goed":
#                            dataset["controle_totaal"] = "fout https in contactpersoon 1"
#                        else:
#                            dataset["controle_totaal"] += ", fout https in contactpersoon 1"
#                    else:
#                        dataset["controle_waarschuwing"] = "ja"
#                        if dataset["controle_waarschuwing_detail"] == "":
#                            dataset["controle_waarschuwing_detail"] += "fout https in " + item[0]            
#                        if item[0] not in dataset["controle_waarschuwing_detail"]:
#                            dataset["controle_waarschuwing_detail"] += ", fout https in " + item[0]
#                        if dataset["controle_totaal"] == "goed":
#                            dataset["controle_totaal"] = "fout https in " + item[0]
#                        if item[0] not in dataset["controle_totaal"]:
#                            dataset["controle_totaal"] += ", fout https in " + item[0]

    # Controleert op correcte spelling van de landsnaam van contactpersonen en organisaties.
    for item in dataset.iteritems():
        if item[0] in (
                "auteur_metadata_land_contactpersoon",
                "bron_land_contactpersoon_1",
                "bron_land_contactpersoon_2",
                "bron_land_contactpersoon_3",
                "bron_land_contactpersoon_4",
                "distributeur_land_contactpersoon"
                ):
            if item[1] not in ("Nederland", ""):
                dataset["fout_spelling_land"] = "ja"
                dataset["controle_waarschuwing"] = "ja"
                if dataset["controle_waarschuwing_detail"] == "":
                    dataset["controle_waarschuwing_detail"] = "foute spelling land in " + item[0]
                else:
                    dataset["controle_waarschuwing_detail"] += ", foute spelling land in " + item[0]                
                if dataset["controle_totaal"] == "goed":
                    dataset["controle_totaal"] = "foute spelling land in " + item[0]
                else:
                    dataset["controle_totaal"] += ", foute spelling land in " + item[0]

    # Controleert op uniciteit van email-naam combinaties.
    if (email_dict_1[dataset["bron_email_contactpersoon_1"].decode("utf-8")] != dataset["bron_naam_contactpersoon_1"] or
        naam_dict_1[dataset["bron_naam_contactpersoon_1"].decode("utf-8")] != dataset["bron_email_contactpersoon_1"]):
        dataset["fout_combinatie_naam_email"] = "ja"
        dataset["controle_waarschuwing"] = "ja"
        if dataset["controle_waarschuwing_detail"] == "":
            dataset["controle_waarschuwing_detail"] = "combinatie naam en email mogelijk fout in contactpersoon 1"
        else:
            dataset["controle_waarschuwing_detail"] += ", combinatie naam en email mogelijk  fout in contactpersoon 1"                
        if dataset["controle_totaal"] == "goed":
            dataset["controle_totaal"] = "combinatie naam en email mogelijk fout in contactpersoon 1"
        else:
            dataset["controle_totaal"] += ", combinatie naam en email mogelijk fout in contactpersoon 1"        

# ---------- Einde metadata-controle ----------

    # Voegt interne of externe metadata toe aan controle_totaal als hulpmiddel bij het interpreteren.
    if dataset["metadata_publiek"] == "Ja":
        dataset["controle_totaal"] = "extern, " + dataset["controle_totaal"]
        if dataset["controle_fout_detail"] != "":
            dataset["controle_fout_detail"] = "extern, " + dataset["controle_fout_detail"]
        if dataset["controle_waarschuwing_detail"] != "":
            dataset["controle_waarschuwing_detail"] = "extern, " + dataset["controle_waarschuwing_detail"]
    if dataset["metadata_publiek"] == "Nee":
        dataset["controle_totaal"] = "intern, " + dataset["controle_totaal"]
        if dataset["controle_fout_detail"] != "":
            dataset["controle_fout_detail"] = "intern, " + dataset["controle_fout_detail"]
        if dataset["controle_waarschuwing_detail"] != "":
            dataset["controle_waarschuwing_detail"] = "intern, " + dataset["controle_waarschuwing_detail"]
    
    # Telt het aantal fouten en waarschuwingen per dataset.
    dataset["controle_fout_aantal"] = dataset["controle_fout_detail"].count(",")
    dataset["controle_waarschuwing_aantal"] = dataset["controle_waarschuwing_detail"].count(",")

# Voegt de namen van de nieuwe kolommen toe aan de originele koptekstvolgorde.
kopteksten = [
        "controle_totaal",
        "controle_fout",
        "controle_fout_aantal",
        "controle_fout_detail",
        "controle_waarschuwing",
        "controle_waarschuwing_aantal",
        "controle_waarschuwing_detail",
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
        "fout_lengte_samenvatting",
        "fout_lengte_titel",
        "fout_spelling_land",
#        "fout_https",
        "fout_combinatie_naam_email"
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
