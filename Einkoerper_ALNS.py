#Ziel ist es ein AlNS Program
# Grundlage dafür ist eine vorsortieret Liste mit Hilfe einer Einkörper AlNS Problematik
# Liste wird in ihre Cluster zerlegt und bestmöglich auf alle Fahrzeuge aufgeteilt

import random 
import math
import pandas as pd
import copy
import csv
import time 
import numpy as np
import msvcrt


def Einkörper_AlNS(angestrebtes_Verhältnis):

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
        Platzhalter_für_Positions_wechsel = 0
        Platzhalter_Regret_Wert = 0 # mal schauen, ob für Rergret 1 beiden Einfügeoptionen oder mehr berücksichtigt werden müssen
        for j in range(add):
            aktuelle_Zeile = [Fahrt_ID,fahrplan[i][0], fahrplan[i][1], fahrplan[i][2], fahrplan[i][3],Fahrzeit_des_Auftrages,Leerzeit_um_Auftrag,Platzhalter_für_Positions_wechsel,Platzhalter_Regret_Wert] # Fahrt_ID wird hinzugefügt, damit die Zeilen später auseinandergehalten werden können, da sie die gleiche Fahrt von A nach B darstellen
            Fahrplan.append(aktuelle_Zeile[:]) # Fahrt_ID wird hinzugefügt, damit die Zeilen später auseinandergehalten werden können, da sie die gleiche Fahrt von A nach B darstellen
            Fahrt_ID +=1


    Zeile1 = []
    Zeile2 = []



    def Vollzeit_berechnen(Fahrplan):
        for i in range(len(Fahrplan)):
            x1 = Fahrplan[i][1]
            y1 = Fahrplan[i][2]
            x2 = Fahrplan[i][3]
            y2 = Fahrplan[i][4]

            fahrzeit = math.sqrt((x2-x1)**2+(y2-y1)**2)

            Fahrplan[i][5] = fahrzeit

        return Fahrplan

    Fahrplan = Vollzeit_berechnen(Fahrplan)

    #2. Funktion, die die Fahrzeit zwischen zwei Punkten bestimmt

    def fahrzeit_aktuallisieren(Fahrplan):
        for i in range(len(Fahrplan)):
            if i == 0:
                x2 = Fahrplan[i][3]
                y2 = Fahrplan[i][4]
                x_nach = Fahrplan[i+1][1]
                y_nach = Fahrplan[i+1][2]
                leerzeit = math.sqrt((x_nach-x2)**2+(y_nach-y2)**2)

                Fahrplan[i][6] = leerzeit

            if i>0 and i< len(Fahrplan)-1:
                x1 = Fahrplan[i][1]
                y1 = Fahrplan[i][2]
                x2 = Fahrplan[i][3]
                y2 = Fahrplan[i][4]

                x_vor = Fahrplan[i-1][3]
                y_vor = Fahrplan[i-1][4]
                x_nach = Fahrplan[i+1][1]
                y_nach = Fahrplan[i+1][2]
                leerzeit = math.sqrt((x1-x_vor)**2+(y1-y_vor)**2)+math.sqrt((x_nach-x2)**2+(y_nach-y2)**2)

                Fahrplan[i][6] = leerzeit

            if i == len(Fahrplan)-1:
                x1 = Fahrplan[i][1]
                y1 = Fahrplan[i][2]
                    
                x_vor = Fahrplan[i-1][3]
                y_vor = Fahrplan[i-1][4]

                leerzeit = math.sqrt((x_vor-x1)**2+(y_vor-y1)**2)

                Fahrplan[i][6] = leerzeit

        return Fahrplan
        
    def zeit_2_Punkt(Zeile1,Zeile2): # Zeile1 der Start der Leerfahrt und Zeile2 Ende der Leerfahrt
        Zeit_2_Punkte = 0
        
        x_vor = Zeile1[3]
        y_vor = Zeile1[4]
        x_nach = Zeile2[1]
        y_nach = Zeile2[2]

        Zeit_2_Punkte = math.sqrt((x_nach-x_vor)**2+(y_nach-y_vor)**2)

        return Zeit_2_Punkte

    def fahrzeit(Fahrplan):
        Fahrzeit = 0
        Zeit_voll = 0
        Zeit_leer = 0
        for i in range(len(Fahrplan)):
            Zeit_voll = Zeit_voll + Fahrplan[i][5]
            if i>0:
                Zeit_leer = Zeit_leer + zeit_2_Punkt(Zeile1 = Fahrplan[i-1], Zeile2= Fahrplan[i])

        Fahrzeit = Zeit_voll+Zeit_leer
        return Fahrzeit,Zeit_voll,Zeit_leer




    def index_summe(Fahrplan):
        Index_Summe = 0
        for i in range(len(Fahrplan)):
            Index_Summe = Index_Summe + Fahrplan[i][0]

        Index_Summe = Index_Summe/len(Fahrplan)
        return Index_Summe

    def regret_instertion(Fahrplan_kopie,worst_elemente):
        for i in range(len(worst_elemente)):
            worst_elemente[i][8] = 0

        for i in range(len(worst_elemente)):
            feld_Leerzeit_Regret = []
            Regret = 0.0
            neue_Leerzeit = 0
            for j in range(len(Fahrplan_kopie)+1):
                
                zeit_vor = 0
                zeit_nach = 0
                

                if j == 0:             
                    zeit_nach = zeit_2_Punkt(Zeile1 = worst_elemente[i],Zeile2 = Fahrplan_kopie[j])

                elif j>0 and j<len(Fahrplan_kopie)-1:
                    zeit_vor = zeit_2_Punkt(Zeile1 = Fahrplan_kopie[j-1],Zeile2 = worst_elemente[i])
                    zeit_nach = zeit_2_Punkt(Zeile1 = worst_elemente[i], Zeile2=Fahrplan_kopie[j])

                elif j == len(Fahrplan_kopie):
                    zeit_vor = zeit_2_Punkt(Zeile1 =Fahrplan_kopie[j-1], Zeile2=worst_elemente[i])

                neue_Leerzeit = zeit_vor+zeit_nach

                neue_zeile = [neue_Leerzeit,j]
                feld_Leerzeit_Regret.append(neue_zeile[:])

            feld_Leerzeit_Regret.sort(key = lambda x:x[0])
            Regret = feld_Leerzeit_Regret[1][0] - feld_Leerzeit_Regret[0][0]
            
            
            worst_elemente[i][8] = Regret

        worst_elemente.sort(key = lambda x:x[8], reverse = True)

        for i in range (len(worst_elemente)):
            alte_Leerzeit = float('inf')
            neue_Leerzeit = 0
            zeit_vor = 0
            zeit_nach = 0
            for j in range(len(Fahrplan_kopie)):
                if j == 0:             
                    zeit_nach = zeit_2_Punkt(Zeile1 = worst_elemente[i],Zeile2 = Fahrplan_kopie[j])
                    zeit_vor = 0

                elif j>0 and j<len(Fahrplan_kopie):
                    zeit_vor = zeit_2_Punkt(Zeile1 = Fahrplan_kopie[j-1],Zeile2 = worst_elemente[i])
                    zeit_nach = zeit_2_Punkt(Zeile1 = worst_elemente[i], Zeile2=Fahrplan_kopie[j])

                elif j == len(Fahrplan_kopie):
                    zeit_vor = zeit_2_Punkt(Zeile1 =Fahrplan_kopie[j-1], Zeile2=worst_elemente[i])
                    zeit_nach = 0

                neue_Leerzeit = zeit_vor+zeit_nach

                if neue_Leerzeit<alte_Leerzeit:
                    alte_Leerzeit = neue_Leerzeit
                    worst_elemente[i][7] = j #Position, an der das Element eingebaut werden soll

            Fahrplan_kopie.insert(worst_elemente[i][7],worst_elemente[i])
            Fahrplan_kopie = fahrzeit_aktuallisieren(Fahrplan_kopie)
                    
                # beste_Position bestimmt
                # Regret Wert setzt sich aus der ersten un zweiten Einfüge Option zusammen
                # Leerzeit vor der letzten Itteration merken

        return Fahrplan_kopie




    def greed_repair(Fahrplan_kopie,worst_elemente):

        k = min(5,len(worst_elemente))
        top_bereich = worst_elemente[:k]
        random.shuffle(top_bereich)
        worst_elemente[:k] = top_bereich


        for i in range (len(worst_elemente)):
            alte_Leerzeit = float('inf')
            neue_Leerzeit = 0
            zeit_vor = 0
            zeit_nach = 0
            for j in range(len(Fahrplan_kopie)):
                if j == 0:             
                    zeit_nach = zeit_2_Punkt(Zeile1 = worst_elemente[i],Zeile2 = Fahrplan_kopie[j])
                    zeit_vor = 0

                elif j>0 and j<len(Fahrplan_kopie):
                    zeit_vor = zeit_2_Punkt(Zeile1 = Fahrplan_kopie[j-1],Zeile2 = worst_elemente[i])
                    zeit_nach = zeit_2_Punkt(Zeile1 = worst_elemente[i], Zeile2=Fahrplan_kopie[j])

                elif j == len(Fahrplan_kopie):
                    zeit_vor = zeit_2_Punkt(Zeile1 =Fahrplan_kopie[j-1], Zeile2=worst_elemente[i])
                    zeit_nach = 0

                neue_Leerzeit = zeit_vor+zeit_nach

                if neue_Leerzeit<alte_Leerzeit:
                    alte_Leerzeit = neue_Leerzeit
                    worst_elemente[i][7] = j #Position, an der das Element eingebaut werden soll

            Fahrplan_kopie.insert(worst_elemente[i][7],worst_elemente[i])
            Fahrplan_kopie = fahrzeit_aktuallisieren(Fahrplan_kopie)
                    
                # beste_Position bestimmt
                # Regret Wert setzt sich aus der ersten un zweiten Einfüge Option zusammen
                # Leerzeit vor der letzten Itteration merken

        return Fahrplan_kopie



    def worst_removal(Fahrplan,anz_worst_removal,ausgewählte_repair_1):
        Fahrplan_kopie = copy.deepcopy(Fahrplan)
        Fahrplan_kopie.sort(key = lambda x:x[6], reverse = True)
        worst_elemente = Fahrplan_kopie[:anz_worst_removal]
        worst_elemente.sort(key = lambda x:x[0], reverse = True)    

        ids_in_worst_elemente = {row[0] for row in worst_elemente if row[0] != 0}
        Fahrplan_kopie = [row for row in Fahrplan_kopie if row[0] not in ids_in_worst_elemente]
        Fahrplan_kopie = fahrzeit_aktuallisieren(Fahrplan_kopie)

        Fahrplan_kopie = fahrzeit_aktuallisieren(Fahrplan_kopie)
        if ausgewählte_repair_1 == greed_repair:
            Fahrplan_kopie = greed_repair(Fahrplan_kopie,worst_elemente)

        if ausgewählte_repair_1 == regret_instertion:
            Fahrplan_kopie = regret_instertion(Fahrplan_kopie,worst_elemente)

        # zurückgegeben wird liste mit regret werden und Positionen, an denen der wert gefunden wurde sortiert nach den Regret Werten
        # Einbau nach den Regret werden an der für das Element besten Stelle --> Regret werte als Orientierung darüber, wie wichtig es ist den Wert einzubauen

        Index_Summe_Kopie = index_summe(Fahrplan_kopie)
        Index_Summe_orginal = index_summe(Fahrplan)

        if Index_Summe_Kopie == Index_Summe_orginal:
            Fahrplan = [row[:] for row in Fahrplan_kopie]

        elif Index_Summe_Kopie != Index_Summe_orginal:
            print("Summe_verändert")
            Fahrplan = [row[:] for row in Fahrplan]

        return Fahrplan 

    def cluster_insertion(Fahrplan_kopie,Cluster_dict):
        #einfügen der Cluster stumpf nach Leerzeit

        anz_inster = 0
        for i in range(len(Cluster_dict)):
            Fahrplan_kopie = fahrzeit_aktuallisieren(Fahrplan_kopie)
            info_Cluster = Cluster_dict[i][0]
            zeit_vor = 0
            zeit_nach = 0
            zeit_vor_nach = 0
            alte_Leerzeit = float('inf')
            for j in range(len(Fahrplan_kopie)):
                if j == 0:
                    zeit_vor = 0
                    zeit_nach = zeit_2_Punkt(Zeile1=info_Cluster,Zeile2=Fahrplan_kopie[j])
                if j>0 and j< len(Fahrplan_kopie):
                    zeit_vor = zeit_2_Punkt(Zeile1 = Fahrplan_kopie[j-1], Zeile2= info_Cluster)
                    zeit_nach = zeit_2_Punkt(Zeile1=info_Cluster, Zeile2= Fahrplan_kopie[j])

                if j == len(Fahrplan_kopie):
                    zeit_vor = zeit_2_Punkt(Zeile1 = Fahrplan_kopie[j-1], Zeile2= info_Cluster)
                    zeit_nach = 0

                zeit_vor_nach = zeit_vor + zeit_nach
                if zeit_vor_nach<alte_Leerzeit:
                    alte_Leerzeit = zeit_vor_nach
                    Cluster_dict[i][0][6] = j

            
            for k in range(len(Cluster_dict[i])-1):
                neue_zeile = Cluster_dict[i][k+1]
                anz_inster +=1
                Fahrplan_kopie.insert(Cluster_dict[i][0][6]+k,neue_zeile)

        #print(f"anz insertion:{anz_inster}")
            
        return Fahrplan_kopie

    def cluster_extension(Fahrplan_kopie,Cluster_dict):
        Index_alt = index_summe(Fahrplan_kopie)

        Fahrplan_kopie.sort(key = lambda x:x[6], reverse = True)
        k = min(len(Fahrplan_kopie)-2,10)
        worst_elemente = Fahrplan_kopie[:k]



        for i in range(len(worst_elemente)):
            element_fahrplan = worst_elemente[i]
            zeit_vor = 0
            zeit_nach = 0        

            for j in range(len(Cluster_dict)):
                element_cluster = Cluster_dict[j][0]
                zeit_vor = zeit_2_Punkt(Zeile1=element_fahrplan,Zeile2=element_cluster)
                zeit_nach = zeit_2_Punkt(Zeile1 = element_cluster, Zeile2= element_fahrplan)

                if zeit_vor <5:
                    Cluster_dict[j].insert(1,element_fahrplan)
                    Cluster_dict[j][0][1:2] = element_fahrplan[1:2]
                    Fahrplan_kopie.remove(element_fahrplan)
                    break

                if zeit_nach <5:
                    Cluster_dict[j].insert(len(Cluster_dict[j])-1,element_fahrplan)
                    Cluster_dict[j][0][3:4] = element_fahrplan[3:4]
                    Fahrplan_kopie.remove(element_fahrplan)
                    break
            

        Fahrplan_kopie = cluster_insertion(Fahrplan_kopie,Cluster_dict)

        return Fahrplan_kopie
                


    def cluster_build(Fahrplan,ausgewählte_cluster):
        Fahrplan_kopie = copy.deepcopy(Fahrplan)
        Leerzeit = 0
        a = 0
        anz_Cluster = 0
        Cluster_liste=[]
        Cluster_dict = []
        for i in range(len(Fahrplan_kopie)-1):
            Leerzeit = zeit_2_Punkt(Zeile1=Fahrplan_kopie[i],Zeile2=Fahrplan_kopie[i+1])
            if Leerzeit == 0 and a == 0:
                neue_zeile = Fahrplan_kopie[i]
                Cluster_liste.append(neue_zeile[:])
                a = 1
                b = i

            if Leerzeit <10e-9 and a == 1 and i != b:
                neue_zeile = Fahrplan_kopie[i]
                Cluster_liste.append(neue_zeile[:])

            if Leerzeit != 0 and a == 1:
                neue_zeile = Fahrplan_kopie[i]
                Cluster_liste.append(neue_zeile[:])
                neue_zeile = [-1,0,0,0,0,0,0,0]
                anz_Cluster += 1
                Cluster_liste.append(neue_zeile[:])
                a = 0

        Cluster_liste.append([-1,0,0,0,0,0,0,0])

        
        # 1. Sammle alle IDs, die in Cluster verschoben werden
        ids_im_cluster = {row[0] for row in Cluster_liste if row[0] != -1}

        # 2. Erstelle einen neuen Fahrplan, der nur die Elemente enthält, die KEINE Cluster-IDs haben
        # Das ist viel sicherer als .remove()
        Fahrplan_kopie = [row for row in Fahrplan_kopie if row[0] not in ids_im_cluster]

        

        Fahrplan_kopie = fahrzeit_aktuallisieren(Fahrplan_kopie)

        Cluster_id = 0
        a = 0
        anz_elemente = 0
        for i in range(len(Cluster_liste)):
            Start_Cluster_x = 0
            Start_Cluster_y = 0
            Ende_Cluster_x = 0
            Ende_Cluster_y = 0
            Leerzeit_um = 0
            Pos_einfügen = 0
            regret_wert = 0
            aktuelles_Cluster = []

            if Cluster_liste[i][0] == -1:
                Ende_Cluster_x = Cluster_liste[i-1][3]
                Ende_Cluster_y = Cluster_liste[i-1][4]
                Start_Cluster_x = Cluster_liste[a][1]
                Start_Cluster_y = Cluster_liste[a][2]
                länge_Cluster = i-a
                if länge_Cluster > 0:
                    Cluster_id += 1
                    neue_zeile = [Cluster_id,Start_Cluster_x,Start_Cluster_y,Ende_Cluster_x,Ende_Cluster_y,Leerzeit_um,Pos_einfügen,regret_wert]
                    aktuelles_Cluster.append(neue_zeile[:])
                    for j in range(länge_Cluster):
                        neue_zeile = Cluster_liste[a+j]
                        anz_elemente += 1
                        aktuelles_Cluster.append(neue_zeile[:])

                    a = i+1
                    Cluster_dict.append(aktuelles_Cluster[:])
        
        if ausgewählte_cluster == cluster_insertion:
            Fahrplan_kopie = cluster_insertion(Fahrplan_kopie,Cluster_dict)
        
        if ausgewählte_cluster == cluster_extension:
            Fahrplan_kopie = cluster_extension(Fahrplan_kopie,Cluster_dict)


        Index_Summe_Kopie = index_summe(Fahrplan_kopie)
        Index_Summe_orginal = index_summe(Fahrplan)

        if Index_Summe_Kopie == Index_Summe_orginal:
            Fahrplan = [row[:] for row in Fahrplan_kopie]

        elif Index_Summe_Kopie != Index_Summe_orginal:
            print("Summe_verändert,cluster build")
            print(*Cluster_liste,sep='\n')
            Fahrplan = [row[:] for row in Fahrplan]

        return Fahrplan

    def random_removal(Fahrplan):
        Fahrplan_kopie = copy.deepcopy(Fahrplan)
        Index_Summe_alt = index_summe(Fahrplan_kopie)

        stelle_remove = random.randint(50,len(Fahrplan_kopie)-1)
        random_objekt = []

        for i in range(stelle_remove): 
            if Fahrplan_kopie[stelle_remove-i][6] != 0:
                random_objekt = Fahrplan_kopie[stelle_remove-i]
                break
        
        if random_objekt != []:
            Fahrplan_kopie.remove(random_objekt)

        alte_Leerzeit = float('inf')
        neue_Leerzeit = 0
        zeit_vor = 0
        zeit_nach = 0
        for j in range(len(Fahrplan_kopie)):
            if random_objekt == []:
                break
            if j == 0:             
                zeit_nach = zeit_2_Punkt(Zeile1 = random_objekt,Zeile2 = Fahrplan_kopie[j])
                zeit_vor = 0

            elif j>0 and j<len(Fahrplan_kopie):
                zeit_vor = zeit_2_Punkt(Zeile1 = Fahrplan_kopie[j-1],Zeile2 = random_objekt)
                zeit_nach = zeit_2_Punkt(Zeile1 = random_objekt, Zeile2=Fahrplan_kopie[j])

            elif j == len(Fahrplan_kopie):
                zeit_vor = zeit_2_Punkt(Zeile1 =Fahrplan_kopie[j-1], Zeile2=random_objekt)
                zeit_nach = 0

            neue_Leerzeit = zeit_vor+zeit_nach

            if neue_Leerzeit<alte_Leerzeit:
                alte_Leerzeit = neue_Leerzeit
                random_objekt[7] = j #Position, an der das Element eingebaut werden soll

        if random_objekt!=[]:
            
            Fahrplan_kopie.insert(random_objekt[7],random_objekt)
        Fahrplan_kopie = fahrzeit_aktuallisieren(Fahrplan_kopie)
                    
        

        Index_Summe_neu = index_summe(Fahrplan_kopie)

        if Index_Summe_alt == Index_Summe_neu:
            Fahrplan = [row[:] for row in Fahrplan_kopie]

        elif Index_Summe_alt != Index_Summe_neu:
            print("Summe_verändert,random")
            Fahrplan = [row[:] for row in Fahrplan]

        return Fahrplan

            

        
    #Scores system für Funktionen

    functions = [worst_removal,cluster_build,random_removal]
    anz_itt = [1,1,1]
    anz_worst_removal = 10

    scores_anz_itt = [1,1,1]

    scores_fct = [1.0,1.0,1.0]
    usage_fct = [0.0,0.0,0.0]
    points_fct = [0.0,0.0,0.0]

    repair_1 = [greed_repair,regret_instertion]

    scores_repair_1 = [1.0,1.0]
    usage_repair_1= [0,0]
    points_repair_1 = [0.0,0.0]

    cluster = [cluster_insertion,cluster_extension]

    scores_repair_cluster = [0,1.0]
    usage_repair_cluster = [0,0]
    points_repair_cluster = [0.0,0.0]


    rho = 0.05
        
    globale_Laufzeit_neu = fahrzeit(Fahrplan)[0]
    globale_Laufzeit_alt = fahrzeit(Fahrplan)[0]

            
    def führe_optimierung_durch(Fahrplan,anz_worst_removal):
        # als erstes muss eine Funktion zufällig und durch ihren Wahrscheinlichkeitswert ausgewählt werden 

        idx = random.choices(range(len(functions)), weights=scores_fct, k=1)[0] # zufällige Auswahl einer Funktion basierend auf den Punkten der Funktionen
        ausgewählte_Funktion = functions[idx]

        repair_idx = random.choices(range(len(repair_1)), weights=scores_repair_1, k=1)[0]
        ausgewählte_repair_1 = repair_1[repair_idx]

        cluster_idx = random.choices(range(len(cluster)), weights=scores_repair_cluster, k=1)[0]
        ausgewählte_cluster = cluster[cluster_idx]

        avg_score = sum(scores_fct)/len(scores_fct) # Durchschnittspunktzahl aller Funktionen, um zu entscheiden, ob Punkte angepasst werden müssen
        aktuelle_itt = max(1,math.ceil(scores_anz_itt[idx]*(scores_fct[idx]/avg_score))) # Anzahl der Iterationen, die vergangen sein müssen, damit Punkte angepasst werden, abhängig von der Punktzahl der Funktion


        if ausgewählte_Funktion == worst_removal:
            usage_fct[0] +=1
            anz_worst_removal_itt = aktuelle_itt
            if ausgewählte_repair_1 == greed_repair:
                usage_repair_1[0] +=1

            if ausgewählte_repair_1 == regret_instertion:
                usage_repair_1[1] +=1
            
            anz_worst_removal=  max(5,min(math.ceil(anz_worst_removal*(scores_fct[1]/avg_score)),math.ceil(len(Fahrplan)*0.3))) # Anzahl der Reparaturen, die bei der worst_removal durchgeführt werden, abhängig von der Punktzahl der Funktion
            

            for _ in range(anz_worst_removal_itt):
                Fahrplan = worst_removal(Fahrplan,anz_worst_removal,ausgewählte_repair_1)
                Fahrplan = fahrzeit_aktuallisieren(Fahrplan)

            

        if ausgewählte_Funktion == cluster_build:
            usage_fct[1] +=1   

            if ausgewählte_cluster == cluster_insertion:
                usage_repair_cluster[0] +=1

            if ausgewählte_cluster == cluster_extension:
                usage_repair_cluster[1] +=1 

            anz_cluster_build = aktuelle_itt

            for _ in range(anz_cluster_build):
                Fahrplan = cluster_build(Fahrplan,ausgewählte_cluster)
                Fahrplan = fahrzeit_aktuallisieren(Fahrplan)

        if ausgewählte_Funktion == random_removal:
            usage_fct[2] +=1
            anz_random_removal = aktuelle_itt

            for _ in range(anz_random_removal):
                Fahrplan = random_removal(Fahrplan)
                Fahrplan = fahrzeit_aktuallisieren(Fahrplan)


        return  idx, Fahrplan, repair_idx, cluster_idx, usage_fct,usage_repair_1,usage_repair_cluster

    #5.3 Funktion zur Auswerung der Ergebnisse

    def update_scores(scores_fct, points_fct, usage_fct):
        for i in range(len(scores_fct)):
            if usage_fct[i] > 0: 
                performance = points_fct[i] / usage_fct[i] # Leistung der Funktion basierend auf den Punkten pro Nutzung
                scores_fct[i] = scores_fct[i] * (1 - rho) + performance * rho # Aktualisierung der Punktzahl der Funktion basierend auf ihrer Leistung

            points_fct[i] = 0 # Punkte zurücksetzen für die nächste Runde
            usage_fct[i] = 0 # Nutzung zurücksetzen für die nächste Runde

        for j in range(len(scores_fct)):
            if scores_fct[j] < 0.1: # Punktzahl auf 0.1 begrenzen, um zu verhindern, dass Funktionen komplett ausgeschlossen werden
                    
                scores_fct[j] = 0.1
            

        return scores_fct

    best_Fahrplan = [row[:] for row in Fahrplan] # Erstellen einer Kopie des Fahrplans, als lokales Maximum
    Summe_alt = index_summe(Fahrplan)
    orginal_Laufzeit = fahrzeit(Fahrplan)
    opt_anz = 0
    opt_anz_grenze = 500  #Maximale Anzahl an Iterationen, in denen sich die fahrzeit nicht verbessert

    temp = 100.0
    rate = 0.995

    global_best = fahrzeit(Fahrplan)[0]
    
    aktuelles_Verhältnis = 1

    Segment_länge = 50

    
    taste_gedrückt = False


    while angestrebtes_Verhältnis< aktuelles_Verhältnis and taste_gedrückt == False: # Optimierung läuft, bis eine Verbesserung von 80% der ursprünglichen Laufzeit erreicht ist oder die Anzahl der Iterationen ohne Verbesserung die Grenze erreicht hat
        globale_Laufzeit_alt = fahrzeit(Fahrplan)[0]
        Fahrplan_alt = [row[:] for row in Fahrplan] # Erstellen einer Kopie des Fahrplans, um diesen später zu vergleichen
        taste = msvcrt.kbhit() # Überprüfen, ob eine Taste gedrückt wurde
        if taste:
            gedrückte_Taste = msvcrt.getch() # Lesen der gedrückten Taste
            if gedrückte_Taste == b't': 
                taste_gedrückt = True

        for _ in range(Segment_länge):
            idx, Fahrplan ,repair_idx, cluster_idx, usage_fct, usage_repair_1, usage_repair_cluster= führe_optimierung_durch(Fahrplan,anz_worst_removal)

            globale_Laufzeit_neu = fahrzeit(Fahrplan)[0]

            Summe_neu = index_summe(Fahrplan)

            if Summe_alt != Summe_neu: # Überprüfen, ob sich die Summe der Elemente im Fahrplan verändert hat, um Datenverlust zu erkennen
                print("Datenverlust erkannt! Optimierung wird abgebrochen.")
                print(f"Funktion: {functions[idx].__name__}")
                Fahrplan = [row[:] for row in best_Fahrplan] # Wiederherstellen des Fahrplans aus dem lokalen Maximum
                
            if Summe_alt == Summe_neu:
                #print("Summe Fahrplan unverändert")
                if globale_Laufzeit_neu<global_best:
                    points_fct[idx] +=30
                    points_repair_1[repair_idx] += 30
                    points_repair_cluster[cluster_idx] +=30
                    global_best = globale_Laufzeit_neu
                    best_Fahrplan = [row[:] for row in Fahrplan]
                    Fahrplan = copy.deepcopy(best_Fahrplan)
                    fahrzeit(Fahrplan)
                    opt_anz = 0
                    
                    print(f"aktuelle Fahrzeit: {globale_Laufzeit_neu}, beste Fahrzeit: {global_best}, Punkte: {scores_fct}")
                    aktuelles_Verhältnis = fahrzeit(best_Fahrplan)[2]/fahrzeit(best_Fahrplan)[1]
                    print(f"Verhältns Leerzeit/Vollzeit:{aktuelles_Verhältnis}")
                elif globale_Laufzeit_neu < globale_Laufzeit_alt:
                    points_fct[idx] +=15
                    points_repair_1[repair_idx] += 15
                    points_repair_cluster[cluster_idx] +=15
                    opt_anz = 0
                elif globale_Laufzeit_neu> globale_Laufzeit_alt:
                    verschlechterung = globale_Laufzeit_neu-globale_Laufzeit_alt

                    if temp > 0.0001:
                        wahrscheinlichkeit = math.exp(-verschlechterung/temp)
                    else:
                        wahrscheinlichkeit = 0

                    if random.random() < wahrscheinlichkeit:
                        points_fct[idx] +=1
                        points_repair_1[repair_idx] += 1
                        points_repair_cluster[cluster_idx] +=1
                        
                    else:
                        points_fct[idx] +=0.5
                        points_repair_1[repair_idx] +=0.5
                        points_repair_cluster[cluster_idx] +=0.5
                        Fahrplan = [row[:] for row in Fahrplan_alt]
                        Fahrplan = fahrzeit_aktuallisieren(Fahrplan)
                        opt_anz +=1

        temp = temp*rate       
        scores_fct = update_scores(scores_fct, points_fct, usage_fct)
        scores_repair_1 = update_scores(scores_repair_1,points_repair_1,usage_repair_1)
        scores_repair_cluster = update_scores(scores_repair_cluster,points_repair_cluster,usage_repair_cluster)
        Tabelle_scores_fct.append(scores_fct[:])
        restart_limit = 100
        if opt_anz >= restart_limit:
            print("restart")
            Fahrplan = copy.deepcopy(best_Fahrplan)
            temp = 50.0
            opt_anz = 0
            scores_fct = [1.0,1.0,1.0]
        
    end_zeit = time.perf_counter()
    #print(f"Optimierung abgeschlossen! Beste gefundene Fahrzeit: {fahrzeit(best_Fahrplan)}")
    #print(f"das Programm hat:{end_zeit-start_zeit:.6f} sek gebraucht")

    return (end_zeit-start_zeit), Fahrplan, Tabelle_scores_fct

Tabelle_scores_fct = []
_,Fahrplan,Tabelle_scores_fct = Einkörper_AlNS(angestrebtes_Verhältnis= 0.01)

# test_anz = 10
# test_Verhältnis_1 = np.geomspace(0.8, 0.08, num = 20)
# test_Verhältnis_2 = np.geomspace(0.079, 0.071, num=20)
# test_Verhältnis = np.concatenate((test_Verhältnis_1, test_Verhältnis_2))

# Ergebnis_speicher = [[0 for _ in range(len(test_Verhältnis))] for _ in range(test_anz)] # --> Speichern, wie lange das Programm jeweils gebraucht hat
# # pro Testprozentsatz werden 10 Wiederholungen gemacht


with open("Ergbnis_Tabelle_scores_fct_Einkörper.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter=",")
    writer.writerows(Tabelle_scores_fct)

# for i in range (len(test_Verhältnis)):
#     for j in range(test_anz):
#         Ergebnis_speicher[j][i], Fahrplan = Einkörper_AlNS(test_Verhältnis[i])
#         print(f"das Aktuelle geteste Verhältnis ist{test_Verhältnis[i]}")
#         print(f"aktuelle Zeit:{Ergebnis_speicher[j][i]}")


import csv

def exportiere_validierungs_fahrplan(Fahrplan, output_filename="schedule.txt", machine_positions_file="machine_positions.txt"):
    """
    Wandelt den generierten Fahrplan in das gültige Format für validations.py um.
    """
    if not Fahrplan:
        print("Fahrplan ist leer!")
        return

    # 1. Maschinenpositionen einlesen, um (X, Y) Koordinaten auf IDs zu mappen
    coord_to_id = {}
    with open(machine_positions_file, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()
        
    # Prüfen, ob ein Header in der Datei existiert
    start_idx = 0
    try:
        int(lines[0].split(';')[0])
    except ValueError:
        start_idx = 1 # Header überspringen
        
    for line in lines[start_idx:]:
        parts = line.strip().split(';')
        if len(parts) >= 3:
            loc_id = int(parts[0])
            x = int(parts[1])
            y = int(parts[2])
            coord_to_id[(x, y)] = loc_id
            
    # 2. Events generieren (Startpunkt, Be- und Entladungen)
    events = []
    vehicle_id = 1         # Da es ein Einkörper-Problem ist, ist die ID immer 1
    start_location_id = 1  # validations.py fordert, dass Fahrzeug 1 an Station 1 startet
    
    # Prüfen, ob die erste Fahrt zufällig schon an Station 1 beginnt
    first_start_x, first_start_y = Fahrplan[0][1], Fahrplan[0][2]
    first_start_id = coord_to_id.get((first_start_x, first_start_y))
    
    if first_start_id != start_location_id:
        # Dummy-Start-Event einfügen: Leere Fahrt von Station 1 zur ersten Maschine
        events.append({'loc': start_location_id, 'load': 0, 'unload': 0})
        
    for fahrt in Fahrplan:
        start_x, start_y = fahrt[1], fahrt[2]
        end_x, end_y = fahrt[3], fahrt[4]
        
        start_id = coord_to_id.get((start_x, start_y))
        end_id = coord_to_id.get((end_x, end_y))
        
        if start_id is None or end_id is None:
            print(f"Fehler: Koordinaten nicht gefunden: Start({start_x},{start_y}), Ziel({end_x},{end_y})")
            continue
            
        # Load Event an der Startposition
        events.append({'loc': start_id, 'load': 1, 'unload': 0})
        # Unload Event an der Zielposition
        events.append({'loc': end_id, 'load': 0, 'unload': 1})
        
    # 3. Events zusammenfassen (Verhindert den Fehler: "cannot visit the same location twice in a row")
    merged_events = []
    for ev in events:
        if not merged_events:
            merged_events.append(ev)
        else:
            last_ev = merged_events[-1]
            if last_ev['loc'] == ev['loc']:
                # Wenn wir schon an der Station sind, kombiniere Load und Unload
                last_ev['load'] = max(last_ev['load'], ev['load'])
                last_ev['unload'] = max(last_ev['unload'], ev['unload'])
            else:
                merged_events.append(ev)
                
    # 4. In die finale Liste umwandeln: [vehicle_id, location, unload, load]
    final_schedule = []
    for ev in merged_events: 
        final_schedule.append([vehicle_id, ev['loc'], ev['unload'], ev['load']])
    
    # 5. In CSV exportieren
    with open(output_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(["vehicle_id", "location", "unload", "load"]) # Optionaler Header
        writer.writerows(final_schedule)
        
    print(f"Validierungs-Fahrplan wurde erfolgreich in '{output_filename}' gespeichert.")
    return final_schedule
# with open("Ergbnis_Tabelle.csv", "w", newline="", encoding="utf-8") as f:
#     writer = csv.writer(f, delimiter=",")
#     writer.writerow(Ergebnis_speicher)


exportiere_validierungs_fahrplan(Fahrplan,output_filename = "Fahrplan_schedule.txt",machine_positions_file = "machine_positions.txt")

    
# Cluster sollten im besten Falle nicht zerschnitten werden 
# jedes fahrzeug hat eine Startposition un d
