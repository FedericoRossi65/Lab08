from database.impianto_DAO import ImpiantoDAO
from model.impianto_DTO import Impianto
from datetime import datetime

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._impianti = None
        self.load_impianti()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_impianti(self):
        """ Carica tutti gli impianti e li setta nella variabile self._impianti """
        self._impianti = ImpiantoDAO.get_impianti()

    def get_consumo_medio(self, mese:int):
        """
        Calcola, per ogni impianto, il consumo medio giornaliero per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome dell'impianto, media), es. (Impianto A, 123)
        """

        for impianto in self._impianti:
            impianto.get_consumi() # chiamo il metodo per riempire la lista di valori
        lista_valori = []
        for impianto in self._impianti:

            count = 0
            somma = 0
            for consumo in impianto.lista_consumi:
                data = consumo.data
                if data.month == mese:
                    somma = somma + consumo.kwh
                    count += 1
            if count > 0: # condizione per evitare la divisione per zero
                media = round(somma / count,2) # tronco il valore alla 2 cifra decimale
            else:
                media = 0
            lista_valori.append((impianto.nome, media))
        return lista_valori









    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di interventi nei primi 7 giorni
        :return: sequenza di nomi impianto ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        consumi_settimana = self.__get_consumi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, consumi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {impianto.id: impianto.nome for impianto in self._impianti}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, self.__costo_ottimo

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_impianto, costo_corrente, consumi_settimana):
        """ Implementa la ricorsione """

        COSTO_SPOSTAMENTO = 5
        ids_impianti = list(consumi_settimana.keys()) # mi creo una lista cosi da avere in seguito i due id impianto



        #caso base dove verifico se è il giorno 8, che è il segnale di stop
        if giorno == 8: # completatto la sequeza di 7 giorni

            #  confronto il suo costo totale (costo_corrente) con il miglior costo trovato fin ad adesso (self.__costo_ottimo).
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo:
                # Aggiorniamo i valori  della classe nel costruttore
                self.__costo_ottimo = costo_corrente# salvo una copia della sequenza parziale

                self.__sequenza_ottima = list(sequenza_parziale)
                #termine delle operazioni su questo ramo


            return



        #parte ricorsiva devo iterare su tutte le scelte possibili dei due impianti.
        for id_impianto_scelto in ids_impianti:

            #calcolo il costo di questa scelta per oggi (giorno)

            #dove costo = costoenergia+costospostamento
            indice_giorno = giorno - 1 #per avere l'indice giusto
            costo_energia = consumi_settimana[id_impianto_scelto][indice_giorno]


            costo_spostamento = 0

            if ultimo_impianto is not None and id_impianto_scelto != ultimo_impianto: #condizione per la quale ho un costo di spostamento(dal testo)[non è il primo giorno (ultimo impianto non è none)]
                                                                                        # e l'impianto di oggi è diverso da quello di ieri)
                costo_spostamento = COSTO_SPOSTAMENTO

            costo_di_oggi = costo_energia + costo_spostamento

            # lancio la chiamata ricorsiva per DOMANI (giorno + 1)
            nuovo_costo_totale = costo_corrente + costo_di_oggi

            # aggiungo la scelta corrente alla sequenza parziale
            sequenza_parziale.append(id_impianto_scelto)

            self.__ricorsione(
                sequenza_parziale,  # passo la sequenza aggiornata
                giorno + 1,  # er il giorno successivo
                id_impianto_scelto,  # impianto di oggi è l'ultimo_impianto di domani
                nuovo_costo_totale,  # costo accumulato aggiornato
                consumi_settimana,

            )

            sequenza_parziale.pop()# backtrack, rimuoviamo la scelta appena fatta!!!!!!!!


    def __get_consumi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i consumi dei primi 7 giorni del mese selezionato per ciascun impianto.
        :return: un dizionario: {id_impianto: [kwh_giorno1, ..., kwh_giorno7]}

        """
        consumi = {}

        for imp in self._impianti:
            # crea una lista di 7 elementi, tutti 0 per evitare errori sugli indici
            consumi[imp.id] = [0] * 7

            #popola la lista nelle posizioni corrette
            for consumo in imp.lista_consumi:
                data = consumo.data
                if data.month == mese and 1 <= data.day <= 7:
                    indice = data.day - 1 # calcola l'indice giusto

                    #sovrascrive gli 0 con i valori e se non ce il valore rimane 0
                    consumi[imp.id][indice] = consumo.kwh


        return consumi




