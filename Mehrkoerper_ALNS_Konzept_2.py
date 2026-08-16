import random 
import math
import pandas as pd
import copy
import csv
import statistics as stat
import time
import msvcrt
import itertools

def test_schleife(Verhältnis, w_gesamt, w_max, w_std):
    start_zeit = time.perf_counter()
    #1. Als erstes müssen die Listen eingelesen werden 
    # diesmal als Objekt, damit jede Fahrt diekekt über ein Index aufgerufen werden kann 
    with open ('machine_positions.txt', 'r', encoding='utf-8') as datei:
        m_pos = datei.read().splitlines()
    with open ('transport_demand.txt', 'r' ,encoding='utf-8') as datei:
        t_d = datei.read().splitlines()

    del m_pos[0]
    del t_d[0]

    anz_zeilen = len(t_d)
    fahrplan = [[ 0 for _ in range (4)] for _ in range (anz_zeilen)]  # Leere Liste für Fahrplan erstellen
    Fahrplan = [] # Leere Liste für Fahrplan erstellen, in der später die Zeilen mit Mehrfachaufträgen gespeichert werden, damit sie später auseinandergehalten werden können

    M_pos = [] #Leere Liste für Maschinenpositionen erstellen
    T_D = []    #Leere Liste für Transportbedarf erstellen

    for zeile in m_pos:
        spalte = zeile.split(';')
        zahl_zeile = [int(wert) for wert in spalte] 
        M_pos.append(zahl_zeile[:]) # Umwandeln der Liste an in integer und hinzufügen zur Liste M_pos

    for zeile in t_d:
        spalte = zeile.split(';')
        zahl_zeile = [int(wert) for wert in spalte]
        T_D.append(zahl_zeile[:]) # Umwandeln der Liste an in integer und hinzufügen zur Liste T_D

    for i in range(anz_zeilen): #Bauen des fahrplans durch Vergleichen der Machinenpositionen mit den Stationen im Transportbedarf
        k = 0
        while T_D[i][0] != M_pos[k][0]:
            k = k+1

        if T_D[i][0] == M_pos[k][0]:
            fahrplan[i][0]  = M_pos[k][1]
            fahrplan[i][1] = M_pos[k][2]

        k = 0
        while T_D[i][1] != M_pos[k][0]:
            k = k+1
        if T_D[i][1] == M_pos[k][0]:
            fahrplan[i][2]  = M_pos[k][1]
            fahrplan[i][3] = M_pos[k][2]

    Fahrt_ID = 1
    for i in range(anz_zeilen):
        add = T_D[i][2] # hinzufügen aller Zeilen, die Mehr wie einen Auftrag vonm A nach B haben     
        Fahrzeit_des_Auftrages = 0
        Leerzeit_um_Auftrag = 0
        Leerzeit_zum_aktuellen_Auftrag = 0
        Platzhalter_für_Positions_wechsel = 0
        Platzhalter_Regret_Wert = 0 # mal schauen, ob für Rergret 1 beiden Einfügeoptionen oder mehr berücksichtigt werden müssen
        for j in range(add):
            aktuelle_Zeile = [Fahrt_ID,fahrplan[i][0], fahrplan[i][1], fahrplan[i][2], fahrplan[i][3],Fahrzeit_des_Auftrages,Leerzeit_um_Auftrag,Platzhalter_für_Positions_wechsel,Platzhalter_Regret_Wert,Leerzeit_zum_aktuellen_Auftrag] # Fahrt_ID wird hinzugefügt, damit die Zeilen später auseinandergehalten werden können, da sie die gleiche Fahrt von A nach B darstellen
            Fahrplan.append(aktuelle_Zeile[:]) # Fahrt_ID wird hinzugefügt, damit die Zeilen später auseinandergehalten werden können, da sie die gleiche Fahrt von A nach B darstellen
            Fahrt_ID +=1

    #Aufteilung der x Fahrten auf n Fahrzeuge 

    Anz_Fahrzeuge = 5


    #Auftragsplan erstellen mit Header der Fahrzeuge
    Auftragsplan = []
    Fahrzeug_Id = 0
    Start_x = 0
    Start_y = 0
    x = [50,30,60,60,50,10,50,60,10,40]
    y = [10,30,5,10,30,30,20,35,20,5]

    aktuelles_Ende_x = 0
    aktuelles_Ende_y = 0
    Fahrzeit = 0 #=Vollzeit+Leerzeit_zum_aktuellen_Auftrag
    Vollzeit = 0
    Leerzeit_um_Auftrag = 0 # als Maß, wie gut ein Auftrag an dieser Stelle passt
    Leerzeit_zum_aktuellen_Auftrag = 0 # zur Bestimmung der tatsächlichen Leerzeit im Auftragsplan
    for i in range(Anz_Fahrzeuge):
        aktuelles_Fahrzeug = []
        Start_x = x[i]
        Start_y = y[i]
        header = [Fahrzeug_Id,Start_x,Start_y,aktuelles_Ende_x,aktuelles_Ende_y,Fahrzeit,Vollzeit,Leerzeit_zum_aktuellen_Auftrag]
        aktuelles_Fahrzeug.append(header[:])
        Auftragsplan.append(aktuelles_Fahrzeug)
        Fahrzeug_Id +=1

    a = 0
    for i in range(len(Fahrplan)):
        neue_zeile = Fahrplan[i]
        Auftragsplan[a].append(neue_zeile)
        a +=1
        if a == Anz_Fahrzeuge:
            a = 0

    def zeit_2_Punkte(Zeile1,Zeile2):
        x_ab , y_ab = Zeile1[3],Zeile1[4]
        x_an, y_an = Zeile2[1],Zeile2[2]
        Fahrzeit = math.sqrt((x_an-x_ab)**2+(y_an-y_ab)**2)

        return Fahrzeit

    def aktualisiere_route(route):
        # Spezialfall: Route ist leer oder enthält nur den Header
        if len(route) <= 1:
            if len(route) == 1:
                route[0][5] = 0  # Fahrzeit Gesamt
                route[0][6] = 0  # Vollzeit Gesamt
                route[0][7] = 0  # Leerzeit Gesamt
                route[0][3] = route[0][1]  # Ende_x = Start_x
                route[0][4] = route[0][2]  # Ende_y = Start_y
            return route

        # 1. Vollzeit für jeden Auftrag berechnen
        for j in range(len(route) - 1):
            Vollzeit = zeit_2_Punkte(Zeile1=route[j+1], Zeile2=route[j+1])
            route[j+1][5] = Vollzeit

        # 2. Leerzeit um Auftrag für jeden Auftrag (dein Kriterium für worst_removal)
        if len(route) == 2:  # Spezialfall: Genau 1 Auftrag in der Route
            Leerzeit_vor = math.sqrt((route[0][1] - route[1][1])**2 + (route[0][2] - route[1][2])**2)
            route[1][6] = Leerzeit_vor  # Keine Nachfolge-Leerzeit vorhanden
        else:
            for j in range(len(route) - 1):
                if j == 0:
                    Leerzeit_vor = math.sqrt((route[0][1] - route[1][1])**2 + (route[0][2] - route[1][2])**2)
                    Leerzeit_nach = zeit_2_Punkte(Zeile1=route[j+1], Zeile2=route[j+2])
                elif j == len(route) - 2:
                    Leerzeit_vor = zeit_2_Punkte(Zeile1=route[j], Zeile2=route[j+1])
                    Leerzeit_nach = 0
                else:
                    Leerzeit_vor = zeit_2_Punkte(Zeile1=route[j], Zeile2=route[j+1])
                    Leerzeit_nach = zeit_2_Punkte(Zeile1=route[j+1], Zeile2=route[j+2])
                
                route[j+1][6] = Leerzeit_vor + Leerzeit_nach

        # 3. Leerzeit zum Auftrag (tatsächliche Leerzeit vor dem Auftrag)
        for j in range(len(route) - 1):
            if j == 0:
                Leerzeit = math.sqrt((route[0][1] - route[1][1])**2 + (route[0][2] - route[1][2])**2)
                route[1][9] = Leerzeit
            else:
                Leerzeit = zeit_2_Punkte(Zeile1=route[j], Zeile2=route[j+1])
                route[j+1][9] = Leerzeit

        # 4. Gesamtsummen im Header des Fahrzeugs (Zeile 0) aktualisieren
        Gesamt_Fahrzeit = 0
        Gesamt_Leerzeit = 0
        for j in range(len(route) - 1):
            Gesamt_Fahrzeit += route[j+1][5]
            Gesamt_Leerzeit += route[j+1][9]

        route[0][5] = Gesamt_Fahrzeit + Gesamt_Leerzeit
        route[0][6] = Gesamt_Fahrzeit
        route[0][7] = Gesamt_Leerzeit

        # Aktuelle Endkoordinaten des Fahrzeugs auf den Endpunkt des letzten Auftrags setzen
        route[0][3] = route[-1][3]
        route[0][4] = route[-1][4]

        return route


    def fahrzeit_aktualisieren(Auftragsplan):
        for i in range(len(Auftragsplan)):
            Auftragsplan[i] = aktualisiere_route(Auftragsplan[i])
        return Auftragsplan

    def komplette_fahrzeit(Auftragsplan):
        #gibt komplette zeit und Zeit des längsten Fahrzeugplan zurück
        komplette_Fahrzeit = 0
        längste_Fahrzeit = 0
        Leerzeit = 0
        Fahrzeit = 0
        for i in range(len(Auftragsplan)):
            komplette_Fahrzeit = komplette_Fahrzeit + Auftragsplan[i][0][5]

        for i in range(len(Auftragsplan)):
            Leerzeit = Leerzeit + Auftragsplan[i][0][7]
            Fahrzeit = Fahrzeit + Auftragsplan[i][0][6]

        
        längste_Fahrzeit = max(fzg[0][5] for fzg in Auftragsplan)

        return komplette_Fahrzeit,längste_Fahrzeit,Leerzeit,Fahrzeit

    def komplette_fahrzeit_route(route):
        komplette_fahrzeit = 0
        for i in range(len(route)-1):
            komplette_fahrzeit = komplette_fahrzeit + route[i+1][5]

        return komplette_fahrzeit

    def summe_Auftragsplan(Auftragsplan):
        Summe = 0
        länge = 0
        for i in range(len(Auftragsplan)):
            länge = länge + len(Auftragsplan[i])-1
            for j in range(len(Auftragsplan[i])-1):
                Summe = Auftragsplan[i][j+1][0] + Summe
        Summe = Summe/länge

        return Summe




    Auftragsplan = fahrzeit_aktualisieren(Auftragsplan)  

    def stand_dev_zeit(Auftragsplan):
        zeit = [fahrzeug[0][5] for fahrzeug in Auftragsplan]
        return stat.pstdev(zeit)

    def delta_zeit_berechnen(route,j,neues_element):
        aktuelle_zeit = route[0][5]
        # Zeit des Auftrages selbst
        vollzeit_neu = neues_element[5]

        vorgänger = route[j-1]

        if j == 1:
            leerzeit_vor = math.sqrt((vorgänger[1] - neues_element[1])**2 + (vorgänger[2] - neues_element[2])**2)
        else:
            leerzeit_vor = zeit_2_Punkte(Zeile1=vorgänger, Zeile2=neues_element)

        leerzeit_nach = 0
        leerzeit_ersparnis = 0

        if j<len(route):
            nachfolger = route[j]
            leerzeit_nach = zeit_2_Punkte(Zeile1=neues_element, Zeile2=nachfolger)

            if j == 1:
                leerzeit_ersparnis = math.sqrt((vorgänger[1] - nachfolger[1])**2 + (vorgänger[2] - nachfolger[2])**2)
            else:
                leerzeit_ersparnis = zeit_2_Punkte(Zeile1=vorgänger, Zeile2=nachfolger)

        delta_zeit = aktuelle_zeit + vollzeit_neu + leerzeit_vor + leerzeit_nach - leerzeit_ersparnis
        return delta_zeit

    #als erstes Funktion, die einen Fahzeit ausgleich mittels verschiebung von einzelnen Fahrten schaut
    #Zeit zum Auftrag ist dynamisch und abhängig von der Position 
    #Zeit des Auftrages an sich nicht 
    #deswegen Ausgleichfunktion nur über die länge der Aufträge an sich 

    def fahrzeit_ausgleich(Auftragsplan):
        Auftragsplan_kopie = copy.deepcopy(Auftragsplan)
        Summe_alt = summe_Auftragsplan(Auftragsplan_kopie)
        Summe_Vollzeit = 0
        for i in range(len(Auftragsplan_kopie)):
            Summe_Vollzeit = Summe_Vollzeit + Auftragsplan_kopie[i][0][5]
        
        Durchschnitt = Summe_Vollzeit/Anz_Fahrzeuge
        Auftragsplan_kopie.sort(key = lambda x:x[0][5],reverse = True)
        #print(Durchschnitt)
        #print(stand_dev_zeit(Auftragsplan_kopie))

        stand_dev_vor = stand_dev_zeit(Auftragsplan_kopie)

        for i in range(len(Auftragsplan_kopie)):
            if Auftragsplan_kopie[i][0][5] > (Durchschnitt+Durchschnitt*0.05):
                Auftragsplan_länge = len(Auftragsplan_kopie[i])
                j =  len(Auftragsplan_kopie[i]) -1
                while j >=1:
                    Test_plan = copy.deepcopy(Auftragsplan_kopie)
                    Auftragsplan_zwischen = greedy_für_worst_removal(Test_plan,Auftragsplan_kopie[i][j])
                    
                    stand_dev_nach = stand_dev_zeit(Auftragsplan_zwischen)
                    #print(stand_dev_nach)

                    if stand_dev_nach<stand_dev_vor:
                        stand_dev_vor = stand_dev_nach
                        #print(stand_dev_nach)
                        Auftragsplan_kopie = copy.deepcopy(Auftragsplan_zwischen) 
                        Auftragsplan_kopie = fahrzeit_aktualisieren(Auftragsplan_kopie)
                        j = len(Auftragsplan_kopie[i]) -1 
                    else:
                        j -=1

        Summe_neu = summe_Auftragsplan(Auftragsplan_kopie)

        if abs(Summe_neu-Summe_alt) < 1e-5:
            #print("kein Datenverlust --> Ausgleich")
            Auftragsplan = copy.deepcopy(Auftragsplan_kopie)
        elif Summe_neu != Summe_alt:
            print("Datenverlust --> Ausgleich")

        return Auftragsplan                          

                
        
    def worst_removal(Auftragsplan,anz_worst_removal,repair_fct):
        Summe_alt = summe_Auftragsplan(Auftragsplan)
        # Funktion, die die schlimmsten Aufträge entfernt und an einer besseren Stelle wieder einbaut 
        # erstmal Auftragsplan kopieren 
        Auftragsplan_kopie = copy.deepcopy(Auftragsplan)#Kopie, in der Elemente gelöscht und ergänzt werden 
        Auftragsplan_kopie_schlimmste = copy.deepcopy(Auftragsplan)# Kopie um die schlimmsten Elemente zu finden 
        
        for i in range(len(Auftragsplan_kopie_schlimmste)):
            Auftragsplan_kopie_schlimmste[i] = Auftragsplan_kopie_schlimmste[i][1:]
            Auftragsplan_kopie_schlimmste[i].sort(key = lambda x:x[6], reverse = True)

        worst_elemente = []
        for i in range(len(Auftragsplan_kopie_schlimmste)):
            for j in range(anz_worst_removal):
                neue_zeile = Auftragsplan_kopie_schlimmste[i][j]
                worst_elemente.append(neue_zeile[:])

        worst_elemente.sort(key= lambda x:x[6], reverse= True)
        worst_elemente = worst_elemente[:anz_worst_removal]
        #print(*worst_elemente,sep='\n')
        if repair_fct == greedy_für_worst_removal:
            Auftragsplan_kopie = greedy_für_worst_removal(Auftragsplan_kopie,worst_elemente)

        if repair_fct == regret_instertion:
            Auftragsplan_kopie = regret_instertion(Auftragsplan_kopie,worst_elemente)
        

        Summe_neu = summe_Auftragsplan(Auftragsplan_kopie)
        if abs(Summe_neu-Summe_alt) < 1e-5:
            #print(f"kein Datenverlust --> Worst removal, {repair_fct} ")
            Auftragsplan = copy.deepcopy(Auftragsplan_kopie)
        elif Summe_neu != Summe_alt:
            print("Datenverlust--> Worst Removal")


        return Auftragsplan



    def greedy_für_worst_removal(Auftragsplan_kopie,worst_elemente):

        anz_entfernt = 0
        anz_insert = 0
        if len(worst_elemente) > 0 and not isinstance(worst_elemente[0], list):
            for i in range(len(Auftragsplan_kopie)):
                Auftragsplan_kopie[i] = [row for row in Auftragsplan_kopie[i] if row != worst_elemente]
                worst_elemente_länge = 1
        else:
            ids_in_worst_elemente = {row[0] for row in worst_elemente if row[0] != 0}
            for i in range(len(Auftragsplan_kopie)):
                header = Auftragsplan_kopie[i][0]
                task = Auftragsplan_kopie[i][1:]
                Auftragsplan_kopie[i] = [header]+[row for row in task if row[0] not in ids_in_worst_elemente]
                worst_elemente_länge = len(worst_elemente)

            
        

        for k in range(worst_elemente_länge):
            
            if len(worst_elemente)>0 and not isinstance(worst_elemente[0], list):
                worst_element = worst_elemente
            else:
                worst_element = worst_elemente[k]

            zeit_vor = float('inf')
            zeit_nach = 0
            best_i = -1
            best_j = -1

            for i in random.sample(range(len(Auftragsplan_kopie)),len(Auftragsplan_kopie)):
                aktuelle_route = Auftragsplan_kopie[i]
                for j in range(1,len(Auftragsplan_kopie[i])+1):
                    zeit_nach = delta_zeit_berechnen(aktuelle_route,j,worst_element)
                    if zeit_nach < zeit_vor:
                        zeit_vor = zeit_nach
                        #print(zeit_nach)
                        best_i = i
                        best_j = j                    


            if best_i != -1:
                Auftragsplan_kopie[best_i].insert(best_j,worst_element)
                Auftragsplan_kopie[best_i] = aktualisiere_route(Auftragsplan_kopie[best_i])

            
        Auftragsplan_kopie = fahrzeit_aktualisieren(Auftragsplan_kopie)
        return Auftragsplan_kopie

    def regret_instertion(Auftragsplan_kopie,worst_elemente):
        for i in range(len(worst_elemente)):
            worst_elemente[i][8] = 0#Regretwert zurücksetzten 

        for i in range(len(worst_elemente)):
            worst_element = worst_elemente[i]
            zeit_vor = 0
            zeit_nach = 0
            zeit_vor_nach = 0
            Regret_Lager = []
            alte_zeit = float('inf')
            for j in range(len(Auftragsplan_kopie)):
                for k in range(len(Auftragsplan_kopie[j])-1):
                    if k == 0:
                        zeit_vor =  math.sqrt((worst_element[1]-Auftragsplan_kopie[j][0][1])**2+(worst_element[2]-Auftragsplan_kopie[j][0][2])**2)
                        zeit_nach = zeit_2_Punkte(Zeile1=worst_element,Zeile2=Auftragsplan_kopie[j][k+1])

                    elif k == len(Auftragsplan_kopie[j])-2:
                        zeit_vor = zeit_2_Punkte(Zeile1= Auftragsplan_kopie[j][k+1],Zeile2=worst_element)
                        zeit_nach = 0
                    elif k > 0 and k < len(Auftragsplan_kopie[j])-2:
                        zeit_vor = zeit_2_Punkte(Zeile1= Auftragsplan_kopie[j][k],Zeile2=worst_element)
                        zeit_nach = zeit_2_Punkte(Zeile1=worst_element, Zeile2=Auftragsplan_kopie[j][k+1])

                    zeit_vor_nach = zeit_vor+zeit_nach
                    Regret_Lager.append(zeit_vor_nach)
                    if zeit_vor_nach<alte_zeit:
                        alte_zeit = zeit_vor_nach
                        

            Regret_Lager.sort(key = lambda x:x )
            worst_elemente[i][8] = Regret_Lager[1]-Regret_Lager[0]

        worst_elemente.sort(key = lambda x:x[8], reverse = True)

        Auftragsplan_kopie = greedy_für_worst_removal(Auftragsplan_kopie,worst_elemente)

        return Auftragsplan_kopie


    def cluster_build(Auftragsplan,anz_cluster_extension_regret,anz_cluster_insertion,anz_cluster_extension_greedy,ausgewählte_repair):
        # bauen von Cluster und dann sinnvolle erweiterung mit Elementen, die nicht in einem Cluster sind  
        #dort wo Auftragsplan [i][j][6] == 0 --> plus Fahrt vor und danach
        # Alle Elemente sichern, die nicht in einem Cluster sind 
        Auftragsplan_kopie = copy.deepcopy(Auftragsplan)
        Summe_alt = summe_Auftragsplan(Auftragsplan_kopie)
        elemente_ohne_Cluster = []
        Cluster_dict = []
        Cluster_liste = []

        for i in range(len(Auftragsplan_kopie)):
            aktuelle_route = list(Auftragsplan_kopie[i])
            anz_aufträge = len(aktuelle_route)

            if anz_aufträge == 0:
                continue

            for j in range(1,len(aktuelle_route)):
                aktueller_auftrag = aktuelle_route[j]
                hat_vorgänger = False
                hat_nachfolger = False

                if j == 1:
                    if aktuelle_route[0][1] == aktueller_auftrag[1] and aktuelle_route[0][2] == aktueller_auftrag[2]:
                        hat_vorgänger = True

                else:
                    vorhäriger_Auftrags = aktuelle_route[j-1]
                    if vorhäriger_Auftrags[3] == aktueller_auftrag[1] and vorhäriger_Auftrags[4] == aktueller_auftrag[2]:
                        hat_vorgänger = True

                if j == len(aktuelle_route)-1: 
                    hat_nachfolger = False
                else:
                    nachfolge_Auftrags = aktuelle_route[j+1]
                    if aktueller_auftrag[3] == nachfolge_Auftrags[1] and aktueller_auftrag[4] == nachfolge_Auftrags[2]:
                        hat_nachfolger = True

                if not hat_vorgänger and not hat_nachfolger:
                    elemente_ohne_Cluster.append(aktueller_auftrag[:])
                    
                    

        #print(*elemente_ohne_Cluster,sep='\n')
        #print(len(elemente_ohne_Cluster))

        # Elemente sortieren nach schlimmster Leerzeit oder regret Faktor und dann bestmöglich einbauen 
        # bzw Cluster neu anordnen
        Auftragsplan_kopie_ohne_Cluster = copy.deepcopy(Auftragsplan_kopie)
        Auftragsplan_kopie_nur_Cluster = copy.deepcopy(Auftragsplan_kopie)
        ids_in_elemente_ohen_cluster = {row[0] for row in elemente_ohne_Cluster if row[0] != 0}
        # Funktion für Neuanordnung der Cluster

        for i in range(len(Auftragsplan_kopie)):
            neue_zeile = [row for row in Auftragsplan_kopie[i][1:] if row[0] not in ids_in_elemente_ohen_cluster]
            Cluster_liste.extend(neue_zeile)

        #print(*Cluster_liste,sep='\n')

        Cluster_id = 0
        aktuelles_Cluster = []
        for i in range(len(Auftragsplan_kopie)):
            route = Auftragsplan_kopie[i]
            for j in range(1,len(route)):
                aktueller_auftrag=route[j]

                if aktueller_auftrag[0] in ids_in_elemente_ohen_cluster:
                    if len(aktuelles_Cluster) > 1:
                        aktuelles_Cluster[0][3] = aktuelles_Cluster[-1][3]
                        aktuelles_Cluster[0][4] = aktuelles_Cluster[-1][4]
                        Cluster_dict.append(aktuelles_Cluster)
                        Cluster_id +=1
                    aktuelles_Cluster = []
                    continue
                if len(aktuelles_Cluster) == 0:
                    cluster_header = [Cluster_id, aktueller_auftrag[1],aktueller_auftrag[2],0,0,0,0,0,0,0]
                    aktuelles_Cluster.append(cluster_header)
                    aktuelles_Cluster.append(aktueller_auftrag[:])

                else:
                    letzter_auftrag = aktuelles_Cluster[-1]
                    if letzter_auftrag[3] == aktueller_auftrag[1] and letzter_auftrag[4] == aktueller_auftrag[2]:
                        aktuelles_Cluster.append(aktueller_auftrag[:])
                    else:
                        aktuelles_Cluster[0][3] = letzter_auftrag[3]
                        aktuelles_Cluster[0][4] = letzter_auftrag[4]
                        Cluster_dict.append(aktuelles_Cluster)

                        Cluster_id +=1
                        cluster_header = [Cluster_id, aktueller_auftrag[1],aktueller_auftrag[2],0,0,0,0,0,0,0]
                        aktuelles_Cluster = [cluster_header, aktueller_auftrag[:]]

            if len(aktuelles_Cluster)>1:
                aktuelles_Cluster[0][3] = aktuelles_Cluster[-1][3]
                aktuelles_Cluster[0][4] = aktuelles_Cluster[-1][4]
                Cluster_dict.append(aktuelles_Cluster)
                Cluster_id +=1
            aktuelles_Cluster = []

        #print(*Cluster_dict,sep='\n')

        # Einmal können Cluster in Fahrplan ohne Cluster eingebaut werden und einmal können Elemente ohne Cluster in Fahrplan mit nur Cluster eingebaut werden 
        # Auftragsplan ohne Cluster bzw mit Cluster:
        
        # for i in range(len(Auftragsplan_kopie)):
        #     header = Auftragsplan_kopie[i][0]
        #     task = Auftragsplan_kopie[i][1:]

        #     Auftragsplan_kopie_nur_Cluster[i] = [header] + [row for row in task if row[0] not in ids_in_elemente_ohen_cluster]
        #     Auftragsplan_kopie_ohne_Cluster[i] = [header] + [row for row in task if row[0] in ids_in_elemente_ohen_cluster]

        
        if ausgewählte_repair == cluster_greedy:
            Auftragsplan_kopie = cluster_greedy(Auftragsplan_kopie,Cluster_dict,elemente_ohne_Cluster,anz_cluster_insertion = min(anz_cluster_insertion,len(Cluster_dict))) # Cluster so einfügen das Fahrzeit verkürzt wird, sortiert nach regret wert
        
        if ausgewählte_repair == cluster_extension_regret:
            Auftragsplan_kopie=cluster_extension_regret(Auftragsplan_kopie,elemente_ohne_Cluster,anz_cluster_extension_regret = min(anz_cluster_extension_regret,len(elemente_ohne_Cluster))) # Einfügen nach einem regret wert oder länsgter Leerfahrt um
        
        if ausgewählte_repair == cluster_extension_greedy:
            Auftragsplan_kopie=cluster_extension_greedy(Auftragsplan_kopie,elemente_ohne_Cluster,anz_cluster_extension_greedy = min(anz_cluster_extension_greedy,len(elemente_ohne_Cluster)))

        Summe_neu = summe_Auftragsplan(Auftragsplan_kopie)
        if abs(Summe_neu-Summe_alt) < 1e-5:
            #print(f"kein Datenverlust --> Cluster Build,{ausgewählte_repair} ")
            Auftragsplan = copy.deepcopy(Auftragsplan_kopie)
        elif Summe_neu != Summe_alt:
            print("Datenverlust--> Cluster Build")

        Auftragsplan = fahrzeit_aktualisieren(Auftragsplan)

        return Auftragsplan


    def cluster_greedy(Auftragsplan_kopie,Cluster_dict,elemente_ohne_Cluster,anz_cluster_insertion):
        # Cluster so einbauen, dass sie best möglich sitzen
        # bestimmen von regret wert
        Auftragsplan_ohne_Cluster = copy.deepcopy(Auftragsplan_kopie)
        ids_in_elemente_ohne_cluster = {row[0] for row in elemente_ohne_Cluster if row[0] != 0}
        for i in range(len(Auftragsplan_kopie)):
            header = Auftragsplan_kopie[i][0]
            task = Auftragsplan_kopie[i][1:]

            Auftragsplan_ohne_Cluster[i] = [header] + [row for row in task if row[0] in ids_in_elemente_ohne_cluster]

        for i in range(len(Cluster_dict)):
            aktueller_header = Cluster_dict[i][1] # --> für Positionssuche
            zeit_vor = float('inf')
            Regret_Lager =[]
            for j in range(len(Auftragsplan_ohne_Cluster)):
                
                for k in range(1,len(Auftragsplan_ohne_Cluster[j])+1):
                    test_route = list(Auftragsplan_ohne_Cluster[j])
                    test_route.insert(k,aktueller_header)
                    test_route = aktualisiere_route(test_route)
                    zeit_nach = test_route[0][5]

                    if zeit_nach<zeit_vor:
                        zeit_vor = zeit_nach
                    
                    Regret_Lager.append(zeit_nach)
                        
            Regret_Lager.sort(key = lambda x:x)
            Cluster_dict[i][0][5] = Regret_Lager[1] - Regret_Lager[0]
        
        Cluster_dict.sort(key = lambda x:x[0][5] , reverse = True)


        for i in range(len(Cluster_dict)):
            aktuelles_Cluster = Cluster_dict[i][1:] #--> zum einbauen ohne Header
            aktueller_header = Cluster_dict[i][1] # --> für Positionssuche
            zeit_vor = float('inf')
            best_k = -1
            best_j = -1
            
            for j in random.sample(range(len(Auftragsplan_ohne_Cluster)),len(Auftragsplan_ohne_Cluster)):
                
                for k in range(1,len(Auftragsplan_ohne_Cluster[j])+1):
                    test_route = list(Auftragsplan_ohne_Cluster[j])
                    test_route.insert(k,aktueller_header)
                    test_route = aktualisiere_route(test_route)
                    zeit_nach = test_route[0][5]

                    if zeit_nach<zeit_vor:
                        zeit_vor = zeit_nach
                        best_k = k
                        best_j = j
                        

            if best_k != -1:
                for h in range(len(aktuelles_Cluster)):
                    Auftragsplan_ohne_Cluster[best_j].insert(best_k+h,aktuelles_Cluster[h])

                Auftragsplan_ohne_Cluster = fahrzeit_aktualisieren(Auftragsplan_ohne_Cluster)

        return Auftragsplan_ohne_Cluster

    def cluster_extension_greedy(Auftragsplan_kopie,elemente_ohne_Cluster,anz_cluster_extension_greedy):
        # elemente_ohne_cluster nach längster Leerfahrt sortieren und abschneiden
        elemente_ohne_Cluster.sort(key = lambda x:x[6], reverse = True)
        elemente_ohne_Cluster = elemente_ohne_Cluster[:anz_cluster_extension_greedy]

        Auftragsplan_kopie_nur_Cluster = copy.deepcopy(Auftragsplan_kopie)

        ids_in_elemente_ohen_cluster = {row[0] for row in elemente_ohne_Cluster if row[0] != 0}

        for i in range(len(Auftragsplan_kopie)):
            header = Auftragsplan_kopie[i][0]
            task = Auftragsplan_kopie[i][1:]
            Auftragsplan_kopie_nur_Cluster[i] = [header] + [row for row in task if row[0] not in ids_in_elemente_ohen_cluster]

        for i in range(len(elemente_ohne_Cluster)):
            aktuelles_element = elemente_ohne_Cluster[i]
            zeit_alt = float('inf')
            best_j = -1
            best_k = -1
            zeit_nach = 0
            for j in random.sample(range(len(Auftragsplan_kopie_nur_Cluster)),len(Auftragsplan_kopie_nur_Cluster)):
                for k in range(1,len(Auftragsplan_kopie_nur_Cluster[j])+1):
                    test_route = copy.deepcopy(Auftragsplan_kopie_nur_Cluster[j])
                    test_route.insert(k,aktuelles_element)
                    test_route = aktualisiere_route(test_route)
                    zeit_nach = test_route[0][5]

                    if zeit_nach<zeit_alt:
                        zeit_alt = zeit_nach
                        best_j = j
                        best_k = k

            if best_k != -1:
                Auftragsplan_kopie_nur_Cluster[best_j].insert(best_k, aktuelles_element)
                Auftragsplan_kopie_nur_Cluster = fahrzeit_aktualisieren(Auftragsplan_kopie_nur_Cluster)

            
        return Auftragsplan_kopie_nur_Cluster

            

                    

    def cluster_extension_regret(Auftragsplan_kopie,elemente_ohne_Cluster,anz_cluster_extension_regret):
        Auftragsplan_kopie_nur_Cluster = copy.deepcopy(Auftragsplan_kopie)
        ids_in_elemente_ohen_cluster = {row[0] for row in elemente_ohne_Cluster if row[0] != 0}

        for i in range(len(Auftragsplan_kopie)):
            header = Auftragsplan_kopie[i][0]
            task = Auftragsplan_kopie[i][1:]
            Auftragsplan_kopie_nur_Cluster[i] = [header] + [row for row in task if row[0] not in ids_in_elemente_ohen_cluster]
        
        # regret werte bestimmen für alle Elemente 

        for i in range(len(elemente_ohne_Cluster)):
            aktuelles_element = elemente_ohne_Cluster[i]
            zeit_alt = float('inf')
            Regret_lager = []
            for j in range(len(Auftragsplan_kopie_nur_Cluster)):            
                for k in range(1,len(Auftragsplan_kopie_nur_Cluster[j])+1):
                    test_route = list(Auftragsplan_kopie_nur_Cluster[j])
                    test_route.insert(k,aktuelles_element)
                    test_route = aktualisiere_route(test_route)
                    zeit_nach = test_route[0][5]

                    if zeit_nach < zeit_alt:
                        zeit_alt = zeit_nach

                    Regret_lager.append(zeit_alt)
            
            elemente_ohne_Cluster[i][8] = Regret_lager[1]-Regret_lager[0]

        elemente_ohne_Cluster.sort(key = lambda x:x[8], reverse = True)
        elemente_ohne_Cluster = elemente_ohne_Cluster[:anz_cluster_extension_regret]

        # Auftragsplan ohne Cluster jetzt wirklich nur ohne die erstellen, die eingesetzt werde sollen

        Auftragsplan_kopie_nur_Cluster = copy.deepcopy(Auftragsplan_kopie)
        ids_in_elemente_ohen_cluster = {row[0] for row in elemente_ohne_Cluster if row[0] != 0}

        for i in range(len(Auftragsplan_kopie)):
            header = Auftragsplan_kopie[i][0]
            task = Auftragsplan_kopie[i][1:]
            Auftragsplan_kopie_nur_Cluster[i] = [header] + [row for row in task if row[0] not in ids_in_elemente_ohen_cluster]


        for i in range(len(elemente_ohne_Cluster)):
            aktuelles_element = elemente_ohne_Cluster[i]
            zeit_alt = float('inf')
            best_j = -1
            best_k = -1
            zeit_nach = 0
            for j in random.sample(range(len(Auftragsplan_kopie_nur_Cluster)),len(Auftragsplan_kopie_nur_Cluster)):
                for k in range(1,len(Auftragsplan_kopie_nur_Cluster[j])+1):
                    test_route = list(Auftragsplan_kopie_nur_Cluster[j])
                    test_route.insert(k,aktuelles_element)
                    test_route = aktualisiere_route(test_route)
                    zeit_nach = test_route[0][5]

                    if zeit_nach<zeit_alt:
                        zeit_alt = zeit_nach
                        best_j = j
                        best_k = k

            if best_k != -1:
                Auftragsplan_kopie_nur_Cluster[best_j].insert(best_k, aktuelles_element)
                Auftragsplan_kopie_nur_Cluster = fahrzeit_aktualisieren(Auftragsplan_kopie_nur_Cluster)

            
        return Auftragsplan_kopie_nur_Cluster
                    



        # entwerder einsetzten über regret oder über greedy 



    rho = 0.2
    Segement_länge = 5

    des_functions = [worst_removal, fahrzeit_ausgleich, cluster_build]
    repair_function_worst_removal = [greedy_für_worst_removal, regret_instertion]
    repair_function_cluster_build = [cluster_extension_greedy,cluster_extension_regret,cluster_greedy]

    

    def kosten_berechnen (Auftragsplan, w_gesamt, w_max, w_std):
        gesamte_zeit,längste_Zeit,_,_ = komplette_fahrzeit(Auftragsplan)
        std_dev = stand_dev_zeit(Auftragsplan)

        kosten = (w_gesamt * gesamte_zeit) + (w_max * längste_Zeit) + (w_std * std_dev)
        return kosten

    global_best = kosten_berechnen(Auftragsplan,w_gesamt,w_max,w_std)

    def update_scores(des_functions, points_fct, usage_fct):
            for i in range(len(des_functions)):
                if usage_fct[i] > 0: 
                    performance = points_fct[i] / usage_fct[i] # Leistung der Funktion basierend auf den Punkten pro Nutzung
                    des_functions[i] = des_functions[i] * (1 - rho) + performance * rho # Aktualisierung der Punktzahl der Funktion basierend auf ihrer Leistung

                points_fct[i] = 0 # Punkte zurücksetzen für die nächste Runde
                usage_fct[i] = 0 # Nutzung zurücksetzen für die nächste Runde

                for j in range(len(des_functions)):
                    if des_functions[j] < 0.1: # Punktzahl auf 0.1 begrenzen, um zu verhindern, dass Funktionen komplett ausgeschlossen werden
                        
                        des_functions[j] = 0.1
                

            return des_functions


    def Hauptschleife(Auftragsplan,des_fct_scores,repair_fct_worst_scores,repair_fct_cluster_scores):
        # Hauptschleife mit Score System für das AlNS 

        # eine Funktion zufällig auf Grund ihrers Scroes auswählen

        idx_repair_worst = -1
        idx_repair_cluster = -1

        idx = random.choices(range(len(des_functions)), weights=des_fct_scores, k=1)[0] # zufällige Auswahl einer Funktion basierend auf den Punkten der Funktionen
        ausgewählte_Funktion = des_functions[idx]

        avg_score = sum(des_fct_scores)/len(des_fct_scores) # Durchschnittspunktzahl aller Funktionen, um zu entscheiden, ob Punkte angepasst werden müssen
        aktuelle_itt = max(1,math.ceil(des_fct_scores[idx]*(des_fct_scores[idx]/avg_score))) # Anzahl der Iterationen, die vergangen sein müssen, damit Punkte angepasst werden, abhängig von der Punktzahl der Funktion


        if ausgewählte_Funktion == fahrzeit_ausgleich:
            usage_fct[idx] +=1
            Auftragsplan = fahrzeit_ausgleich(Auftragsplan)
            Auftragsplan = fahrzeit_aktualisieren(Auftragsplan)

        if ausgewählte_Funktion == worst_removal:
            usage_fct[idx] +=1
            idx_repair_worst = random.choices(range(len(repair_function_worst_removal)), weights = repair_fct_worst_scores, k = 1)[0]
            ausgewählte_repair = repair_function_worst_removal[idx_repair_worst]
            usage_fct_worst[idx_repair_worst] +=1
            avg_score = sum(des_fct_scores)/len(des_fct_scores) # Durchschnittspunktzahl aller Funktionen, um zu entscheiden, ob Punkte angepasst werden müssen
            aktuelle_itt = max(1,math.ceil(des_fct_scores[idx_repair_worst]*(des_fct_scores[idx_repair_worst]/avg_score)))
            min_anzahl = min(len(fahrzeug) - 1 for fahrzeug in Auftragsplan)
            aktuelle_itt = min(aktuelle_itt,min_anzahl) # Anzahl der Iterationen, die vergangen sein müssen, damit Punkte angepasst werden, abhängig von der Punktzahl der Funktion

            Auftragsplan = worst_removal(Auftragsplan,anz_worst_removal = aktuelle_itt,repair_fct=ausgewählte_repair)
            Auftragsplan = fahrzeit_aktualisieren(Auftragsplan)

        if ausgewählte_Funktion == cluster_build:
            usage_fct[idx] +=1
            idx_repair_cluster = random.choices(range(len(repair_fct_cluster_scores)), weights = repair_fct_cluster_scores, k = 1)[0]
        
            usage_fct_cluster[idx_repair_cluster] +=1

            avg_score = sum(des_fct_scores)/len(des_fct_scores) # Durchschnittspunktzahl aller Funktionen, um zu entscheiden, ob Punkte angepasst werden müssen
            aktuelle_itt = max(1,math.ceil(des_fct_scores[idx_repair_cluster]*(des_fct_scores[idx_repair_cluster]/avg_score))) # Anzahl der Iterationen, die vergangen sein müssen, damit Punkte angepasst werden, abhängig von der Punktzahl der Funktion
            
            

            Auftragsplan = cluster_build(Auftragsplan,anz_cluster_extension_regret = aktuelle_itt,anz_cluster_insertion = aktuelle_itt,anz_cluster_extension_greedy = aktuelle_itt,ausgewählte_repair = repair_function_cluster_build[idx_repair_cluster])
            Auftragsplan = fahrzeit_aktualisieren(Auftragsplan)


        return Auftragsplan,idx,idx_repair_worst,idx_repair_cluster,usage_fct,usage_fct_worst,usage_fct_cluster




    # Besten Fahrplan erstmal mit dem Ausgangsfahrplan belegen 
    best_Auftragsplan = copy.deepcopy(Auftragsplan)

    opt_anz = 0 
    opt_anz_grenze = 500

     # Verhältnis von Leerzeit zu Vollzeit
    aktuelles_Verhältnis = 1

    temp = 100
    rate = 0.995

    des_fct_scores = [1.0,1.0,1.0] # Punkte für destroy
    usage_fct = [0,0,0]
    points_fct = [0.0,0.0,0.0]

    repair_fct_worst_scores = [1.0,1.0] # Punkte für worst_repair funktionen
    usage_fct_worst = [0.0,0.0]
    points_fct_worst =  [0.0,0.0]

    repair_fct_cluster_scores = [1.0,1.0,1.0] # Punkte für Cluster repair funktionen
    usage_fct_cluster = [0.0,0.0,0.0]
    points_fct_cluster = [0,0,0]

    anz_cluster_repair = [1,1,1]
    taste_gedrückt = False
    zeit_limit = 300

    zeit = 0
    while aktuelles_Verhältnis > Verhältnis and taste_gedrückt == False and zeit<zeit_limit:
        zeit = time.perf_counter() - start_zeit
        taste = msvcrt.kbhit() # Überprüfen, ob eine Taste gedrückt wurde
        if taste:
            gedrückte_Taste = msvcrt.getch() # Lesen der gedrückten Taste
            if gedrückte_Taste == b't': 
                taste_gedrückt = True
        Summe_alt = summe_Auftragsplan(Auftragsplan)
        globale_Laufzeit_alt = kosten_berechnen(Auftragsplan, w_gesamt, w_max, w_std)
        Auftragsplan_alt = copy.deepcopy(Auftragsplan)
        for _ in range(Segement_länge):
            Auftragsplan, idx,idx_repair_worst,idx_repair_cluster,usage_fct,usage_fct_worst,usage_fct_cluster = Hauptschleife(Auftragsplan,des_fct_scores,repair_fct_worst_scores,repair_fct_cluster_scores)
            aktuelles_Verhältnis = komplette_fahrzeit(Auftragsplan)[2]/komplette_fahrzeit(Auftragsplan)[0]
            Tabelle_scores_fct.append(des_fct_scores.copy())

        Summe_neu = summe_Auftragsplan(Auftragsplan)
        globale_Laufzeit_neu = kosten_berechnen(Auftragsplan, w_gesamt, w_max, w_std)

        if Summe_alt == Summe_neu:
            #print("Summe Fahrplan unverändert")
            if globale_Laufzeit_neu<global_best:
                points_fct[idx] +=15
                if idx_repair_worst != -1:points_fct_worst[idx_repair_worst] += 15
                if idx_repair_cluster != -1:points_fct_cluster[idx_repair_cluster] +=15
                global_best = globale_Laufzeit_neu
                best_Auftragsplan = copy.deepcopy(Auftragsplan)
                print(f"aktuelle Fahrzeit: {komplette_fahrzeit(Auftragsplan)}, beste Fahrzeit: {komplette_fahrzeit(Auftragsplan)[1]}, Punkte: {des_fct_scores}")
                opt_anz = 0
                print(f"aktuelles_Verhältnis:{aktuelles_Verhältnis}") 
            elif globale_Laufzeit_neu < globale_Laufzeit_alt:
                points_fct[idx] +=8
                if idx_repair_worst != -1:points_fct_worst[idx_repair_worst] += 8
                if idx_repair_cluster != -1:points_fct_cluster[idx_repair_cluster] +=8
                opt_anz = 0
            elif globale_Laufzeit_neu> globale_Laufzeit_alt:
                verschlechterung = globale_Laufzeit_neu-globale_Laufzeit_alt

                if temp > 0.0001:
                    wahrscheinlichkeit = math.exp(-verschlechterung/temp)
                else:
                    wahrscheinlichkeit = 0

                if random.random() < wahrscheinlichkeit:
                    points_fct[idx] +=1
                    if idx_repair_worst != -1:points_fct_worst[idx_repair_worst] += 1
                    if idx_repair_cluster != -1:points_fct_cluster[idx_repair_cluster] +=1
                        
                else:
                    points_fct[idx] -=2
                    if idx_repair_worst!=-1:points_fct_worst[idx_repair_worst] -=2
                    if idx_repair_cluster!=-1:points_fct_cluster[idx_repair_cluster] -=2
                    Auftragsplan = copy.deepcopy(Auftragsplan_alt)
                    Auftragsplan = fahrzeit_aktualisieren(Auftragsplan)
                    opt_anz +=1

        temp = temp*rate       
        des_fct_scores = update_scores(des_fct_scores, points_fct , usage_fct)
        repair_fct_worst_scores = update_scores(repair_fct_worst_scores,points_fct_worst,usage_fct_worst)
        repair_fct_cluster_scores = update_scores(repair_fct_cluster_scores,points_fct_cluster,usage_fct_cluster)

        
        

        restart_limit = 100
        if opt_anz >= restart_limit:
            print("restart")
            Auftragsplan = copy.deepcopy(Auftragsplan_alt)
            temp = 50.0
            opt_anz = 0
            des_fct_scores = [1.0,1.0,1.0]

    end_zeit = time.perf_counter()

    zeit = end_zeit - start_zeit
    return best_Auftragsplan, zeit,Tabelle_scores_fct,komplette_fahrzeit(best_Auftragsplan)[1]


Tabelle_scores_fct = []
test_anz = 5


Ergebnis_tabelle_Mehrkörper_alns = []


test_kosten_faktoren = [
    [float(w1), float(w2), float(w3)]
    for w1, w2, w3 in sorted({
        (w1 // math.gcd(w1, w2, w3), w2 // math.gcd(w1, w2, w3), w3 // math.gcd(w1, w2, w3))
        for w1, w2, w3 in itertools.product(range(4), repeat=3)
        if not (w1 == 0 and w2 == 0 and w3 == 0)
    })
]

                    
for j in range(len(test_kosten_faktoren)):
    neue_zeile = [test_kosten_faktoren[j][0], test_kosten_faktoren[j][1], test_kosten_faktoren[j][2],0,0]
    Ergebnis_tabelle_Mehrkörper_alns.append(neue_zeile)
    laufzeit_speicher = 0
    Ergebnis_tabelle_Mehrkörper_alns_speicher = 0
    for i in range(test_anz):
        Auftragsplan, laufzeit ,Tabelle_scores_fct,längste_Fahrzeit= test_schleife(Verhältnis=0.15,w_gesamt = test_kosten_faktoren[j][0], w_max = test_kosten_faktoren[j][1], w_std = test_kosten_faktoren[j][2])
        Ergebnis_tabelle_Mehrkörper_alns_speicher = Ergebnis_tabelle_Mehrkörper_alns_speicher + längste_Fahrzeit        
        laufzeit_speicher = laufzeit_speicher + laufzeit

    Ergebnis_tabelle_Mehrkörper_alns_speicher = Ergebnis_tabelle_Mehrkörper_alns_speicher/test_anz
    laufzeit_speicher = laufzeit_speicher/test_anz
    Ergebnis_tabelle_Mehrkörper_alns[j][3] = Ergebnis_tabelle_Mehrkörper_alns_speicher
    Ergebnis_tabelle_Mehrkörper_alns[j][4] = laufzeit_speicher

    print(Ergebnis_tabelle_Mehrkörper_alns[j])
    
 

with open("Ergbnis_Tabelle_Mehrkörper_AlNS.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter=";")
    for wert in Ergebnis_tabelle_Mehrkörper_alns:
        writer.writerow([wert])

with open("Tabelle_Scores_fct.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter=";")
    for scores in Tabelle_scores_fct:
        writer.writerow(scores)

x = [50,30,60,60,50,10,50,60,10,40]
y = [10,30,5,10,30,30,20,35,20,5]
pos = [1,2,3,4,5,6,7,8,9,10]

def create_schedule_alns(Auftragsplan, dateiname):
    """
    Erstellt aus dem aktuellen Auftragsplan eine valide schedule_alns.txt,
    die blockweise nach Fahrzeugen sortiert ist und alle Regeln der validations.py erfüllt.
    """
    # Globale Koordinaten-Arrays aus deinem Skript zur Identifikation der Maschinen-IDs
    x_coords = [50, 30, 60, 60, 50, 10, 50, 60, 10, 40]
    y_coords = [10, 30, 5, 10, 30, 30, 20, 35, 20, 5]

    def get_machine_id(x_val, y_val):
        for idx, (mx, my) in enumerate(zip(x_coords, y_coords)):
            if mx == x_val and my == y_val:
                return idx + 1
        return None

    lines = ["vehicle_id;machine_id;unload;load"]

    for fzg_idx in range(len(Auftragsplan)):
        # Im Validierungsskript sind Fahrzeug-IDs 1-basiert (passend zum Start-Ladepunkt)
        vehicle_id = fzg_idx + 1
        route = Auftragsplan[fzg_idx]
        
        # Jedes Fahrzeug beginnt an seiner entsprechenden Heimatstation
        curr_machine = vehicle_id
        stops = [{'machine': vehicle_id, 'unload': 0, 'load': 0}]
        
        # Alle zugewiesenen Aufträge des Fahrzeugs durchgehen (route[0] ist der Header)
        orders = route[1:]
        for order in orders:
            start_x, start_y = order[1], order[2]
            dest_x, dest_y = order[3], order[4]
            
            s_mach = get_machine_id(start_x, start_y)
            d_mach = get_machine_id(dest_x, dest_y)
            
            # Falls wir bereits an der Startmaschine stehen (z.B. nach vorherigem Unload)
            # modifizieren wir den letzten Stopp, um die Aktionen sauber in einer Zeile zu vereinen
            if s_mach == curr_machine:
                stops[-1]['load'] = 1
            else:
                # Leerfahrt zur Startmaschine des neuen Auftrags
                stops.append({'machine': s_mach, 'unload': 0, 'load': 1})
                curr_machine = s_mach
                
            # Fahrt zur Zielmaschine des Auftrags zum Entladen
            stops.append({'machine': d_mach, 'unload': 1, 'load': 0})
            curr_machine = d_mach
            
        # Generierte Stopps für dieses Fahrzeug in das finale Ausgabeformat übersetzen
        for stop in stops:
            lines.append(f"{vehicle_id};{stop['machine']};{stop['unload']};{stop['load']}")

    # Schreiben der Textdatei
    with open(dateiname, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines) + "\n")
    
    print(f"Datei '{dateiname}' wurde erfolgreich für das Validierungstool generiert.")

create_schedule_alns(Auftragsplan,dateiname='schedule_alns.txt')