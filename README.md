# IN-MCA_Scarlata
This is a duplicate of the University project for Natural interaction and affective computing.

Unfortunately i don't have the rights on the videos and csv of the COHFACE dataset, so i invite you to use a dataset of your own, or request the dataset to them.

Here the old readme


# Progetto di Interazione Naturale & Modelli di Computazione affettiva

## Dipendenze

I moduli possono essere scaricati tramite ```pip install x```

- [opencv-python 3.4.1](https://www.lfd.uci.edu/~gohlke/pythonlibs/#opencv)
- [numpy 1.14.3-mkl](https://www.lfd.uci.edu/~gohlke/pythonlibs/#opencv)
- matplotlib 2.2.2
- mdp 3.5
- scipy 1.0.1
- pandas 0.22.0

**nota**: nei collegamenti ci sono i link da cui scaricare i file whl

## Uso degli script

1. mettere i file video nella cartella "video"
2. mettere i file csv nella cartella "csv"
3. Mettersi nella cartella dello script e avviarlo su shell 
  
    1. Per usare "**hrComparison.py**" (hrDynComparison è analogo) andare nella cartella "source" (dopo aver eseguito i primi due passi) e avviare lo script. Il nome dei file devono essere inseriti senza il persorso. Per "interval scale" si intende la scala di tempo delle misurazioni effettuate sul file csv. <br/>
    Per esempio, per avviare lo script sul file "data.avi" (già nella cartella video) basta inserire "data.avi", stessa cosa per data.csv. <br/>
    Per l'interval scale, se la misurazione è stata effettuata in secondi, inserire "1", se è stata effettuata in millisecondi inserire "1000". <br/>
    Nota : usando -d si posso ricevere informazione aggiuntive.  `python hrComparison.py -d`
	Nota bis: usando -s si salvano le distanze medie nell'apposito file. es. `python hrComparison.py -s`
    2. per usare gli script "**hrFrom__.py**" nella cartella "tests",  inserire "-v" e il nome del video nella cartella video. <br/>
    Per esempio per utilizzare lo script "hrFromHrv.py" sul video "data.avi" inserire il comando 
    `python hrFromHrv.py -v data.avi`
    3. Per usare lo script **hrMeanDistancePlotter.py** andare nella cartella "source", inserire "-f" e il nome dei file con i risultati in "source". Per esempio, per utilizzare lo script sul file "resultsVideoHr.csv" inserire il comando  `python hrMeanDistancePlotter.py -f resultsVideoHr.csv`

	
### Esempi di input
**hrComparison.py**
Per fare la misurazione sul video "data.avi", i cui dati sono nel file "data.csv" in cui la misurazione è stata fatta in secondi, i valori da inserire saranno rispettivamente: "data.avi", "data.csv", "1".
  
Per fare la misurazione sul video "10_1.avi" (altro dataset), i cui dati sono nel file "physio_1.csv" in cui la misurazione è stata fatta in millisecondi, i valori da inserire saranno rispettivamente : "10_1.avi","physio_1.csv", "1000" <br/>
Per vedere il plot dei valori hr calcolati (sia dai metodi che dell'hr truth) a fine script, inserire il comando `python hrComparison.py -d`

Per fare la misurazione sul video data.avi che è nel percorso relativo (da video) \1\3, inserire "1\\3\\data.avi" su Windows (analogo su Linux con le differenze di path)


v0.0