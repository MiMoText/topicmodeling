# Erklärung zu enthaltenen Dateien in results

## Das Korpus rom18_test besteht aus den 5 Romanen Abbes_Voyage, Beauharnais_Lettres, Beaumont_Clarice, Benoist_Elisabeth, Benouville_Pensees

### rom18-test_fr_mitADV
* POS-Tagging mit dem französischen Sprachmodell von TreeTagger; Adverben wurden für das Topic Modeling mitausgewählt

### rom18-test_fr_ohneADV
* POS-Tagging mit dem französischen Sprachmodell von TreeTagger; Adverben wurden NICHT für das Topic Modeling berücksichtigt

### rom18-test_presto
* POS-Tagging mit dem Sprachmodell presto für frz. Texte des 16. und 17. Jh. 

### pilot_mod200_fr_10_500
* Pilotkorpus (15 Romane)
* teilmodernisiert (200 häufigste Fehler)
* POS-Tagging mit dem frz. Modell von TreeTagger
* 10 topics und 500 Iterationen

### pilot_mod200_fr_10_500_expStop
* Pilotkorpus (15 Romane)
* teilmodernisiert (200 häufigste Fehler)
* POS-Tagging mit dem frz. Modell von TreeTagger
* 10 topics und 500 Iterationen
* erweiterte Stopwortliste

## Mit der Datei visualization.html lassen sich die Topics im Browser visualisieren