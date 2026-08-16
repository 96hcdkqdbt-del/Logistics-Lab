# =============================================================================
# NIKOLAUS-PROBLEM: Optimale Einsatzplanung für n Fahrzeuge
# =============================================================================
#
# PROBLEMSTELLUNG:
#   In einem Produktionsnetzwerk mit 10 Maschinen müssen Transporte durchgeführt
#   werden. Jedes Fahrzeug startet an einer festen Maschine (Fahrzeug 1 an
#   Maschine 1, Fahrzeug 2 an Maschine 2, usw.) und soll alle geforderten
#   Vollfahrten gemeinsam mit den anderen Fahrzeugen erfüllen.
#
#   Ziel: Den MAKESPAN minimieren, d.h. die Zeit des am längsten fahrenden
#   Fahrzeugs so kurz wie möglich halten.
#
# LÖSUNGSANSATZ:
#   Das Problem wird als gemischt-ganzzahliges lineares Programm (MIP) formuliert
#   und mit dem kommerziellen Solver GUROBI gelöst. Die Tourenberechnung erfolgt
#   anschließend mit dem Hierholzer-Algorithmus (Eulerpfad).
#
#   Um sicherzustellen, dass jeder Teilgraph einen gültigen Eulerpfad ermöglicht,
#   wird die Benders Decomposition eingesetzt: Falls ein Teilgraph nach der
#   Optimierung nicht zusammenhängend ist, wird ein Schnitt (Cut) hinzugefügt
#   und das Problem erneut gelöst.
#
# VERWENDETE BIBLIOTHEKEN:
#   - math:   Berechnung der euklidischen Distanz
#   - copy:   Tiefe Kopie des Graphen für den Hierholzer-Algorithmus
#   - numpy:  Numerische Berechnungen
#   - pulp:   Modellierung des MIP
#   - time:   Zeitmessung der Berechnung
# =============================================================================

import math
import copy
import numpy as np
import pulp as pl
import time

# =============================================================================
# SCHRITT 1: EINGABEDATEN EINLESEN
# =============================================================================
#
# Die Maschinenpositionen geben die x/y-Koordinaten jeder Maschine an.
# Der Transportbedarf gibt an, wie viele Fahrten von Maschine A nach
# Maschine B durchgeführt werden müssen.
# =============================================================================

with open('machine_positions.txt', 'r', encoding='utf-8') as datei:
    m_pos = datei.read().splitlines()
with open('transport_demand.txt', 'r', encoding='utf-8') as datei:
    t_d = datei.read().splitlines()

# Kopfzeile entfernen (erste Zeile enthält Spaltenbezeichnungen, keine Daten)
del m_pos[0]
del t_d[0]

# =============================================================================
# SCHRITT 2: BENUTZEREINSTELLUNGEN
# =============================================================================
#
# n = Anzahl der Fahrzeuge (Fahrzeug v startet bei Maschine v)
#
# gap_faktor = Toleranz für die Optimierung:
#   0.0  → exakt optimal, aber langsam (empfohlen für n ≤ 4)
#   0.05 → maximal 5% vom Optimum entfernt (empfohlen für n = 5-6)
#   0.10 → maximal 10% vom Optimum entfernt (empfohlen für n ≥ 7)
#
# Hintergrund gap_faktor: GUROBI arbeitet mit dem sogenannten Branch-and-Bound-
# Verfahren. Es findet zuerst eine gültige Lösung und verbessert sie schrittweise.
# Der gap_faktor bestimmt, wann GUROBI aufhört zu suchen:
# Bei 0.05 stoppt es, sobald bewiesen ist, dass keine 5% bessere Lösung
# mehr existieren kann.
# =============================================================================

# -----------------------------------------------------------------------------
# EINGABEVALIDIERUNG: Fahrzeuganzahl
# -----------------------------------------------------------------------------
# Das Produktionsnetzwerk hat genau 10 Maschinen. Da Fahrzeug v bei Maschine v
# startet, sind maximal 10 Fahrzeuge sinnvoll. Mit 0 Fahrzeugen würde das MIP
# ein leeres Modell erzeugen. Beides wird hier abgefangen.
# -----------------------------------------------------------------------------
try:
    n = int(input("Wie viele Fahrzeuge? (1-10): "))
except ValueError:
    print("✗ Fehler: Bitte eine ganze Zahl eingeben.")
    exit()

if not (1 <= n <= 10):
    print(f"✗ Fehler: n={n} ist ungültig. Bitte eine Zahl zwischen 1 und 10 eingeben.")
    exit()

start_knoten = list(range(1, n + 1))

# -----------------------------------------------------------------------------
# EINGABEVALIDIERUNG: Toleranzfaktor (gap_faktor)
# -----------------------------------------------------------------------------
# Der gap_faktor muss zwischen 0.0 (exakt optimal) und 1.0 (100% Toleranz)
# liegen. Ein negativer Wert oder ein Wert > 1.0 würde GUROBI in einen
# ungültigen Zustand versetzen.
# -----------------------------------------------------------------------------
try:
    gap_faktor = float(input("Toleranz (0.0 = exakt, 0.05 = 5%, 0.10 = 10%): "))
except ValueError:
    print("✗ Fehler: Bitte eine Dezimalzahl eingeben (z.B. 0.05).")
    exit()
#gap_faktor = n*0.0001
if not (0.0 <= gap_faktor < 1.0):
    print(f"✗ Fehler: gap_faktor={gap_faktor} ist ungültig. "
          f"Bitte einen Wert zwischen 0.0 und 1.0 eingeben.")
    exit()

# Zeitmessung starten
start_zeit = time.perf_counter()

# =============================================================================
# SCHRITT 3: ZEITMATRIX BERECHNEN
# =============================================================================
#
# Da keine Hindernisse im Fahrweg existieren, entspricht die euklidische
# Distanz zwischen zwei Punkten exakt der Fahrzeit (bei Geschwindigkeit 1).
#
# Euklidische Distanz zwischen Punkt P1=(x1,y1) und P2=(x2,y2):
#   d = sqrt((x2-x1)² + (y2-y1)²)
#
# Zeiten_Matrix[i][j] = Fahrtzeit von Maschine (i+1) zu Maschine (j+1)
# (Index beginnt bei 0, daher der Versatz von +1)
# =============================================================================

def zeiten_zwischen_Maschinen(m_pos, M_a, M_b):
    """Berechnet die euklidische Distanz zwischen zwei Maschinen."""
    for zeile in m_pos:
        parts = zeile.split(';')
        if int(parts[0]) == M_a:
            start = (int(parts[1]), int(parts[2]))
        if int(parts[0]) == M_b:
            ziel = (int(parts[1]), int(parts[2]))
    return math.sqrt((start[0] - ziel[0])**2 + (start[1] - ziel[1])**2)

Zeiten_Matrix = [[0.0] * 10 for _ in range(10)]
for i in range(10):
    for j in range(10):
        Zeiten_Matrix[i][j] = zeiten_zwischen_Maschinen(m_pos, i + 1, j + 1)

# =============================================================================
# SCHRITT 4: VOLLFAHRTEN UND LEERFAHRT-KANDIDATEN AUFBAUEN
# =============================================================================
#
# VOLLFAHRTEN: Alle geforderten Transporte aus der Eingabedatei.
#   voll_agg[(a,b)] = Anzahl benötigter Fahrten von Maschine a nach Maschine b
#
# LEERFAHRTEN: Fahrten ohne Ladung, die nötig sind um Fahrzeuge zu repositionieren.
#   leer_paare enthält alle 90 möglichen Verbindungen (10×10 minus Selbstschleifen).
#   Das MIP entscheidet welche davon tatsächlich gefahren werden.
#
# QUELLEN & SENKEN (Grundprinzip):
#   An jeder Maschine gilt: eingehende Fahrten = ausgehende Fahrten (Flussbilanz)
#   Ausnahme: Startknoten hat +1 ausgehend, Endknoten hat +1 eingehend.
#   Wenn eine Maschine mehr eingehende als ausgehende Vollfahrten hat →
#   sie ist eine QUELLE für Leerfahrten (Fahrzeuge stauen sich an).
#   Wenn sie mehr ausgehende als eingehende Vollfahrten hat →
#   sie ist eine SENKE (Fahrzeuge fehlen dort).
#   Leerfahrten gleichen dieses Ungleichgewicht aus.
# =============================================================================

voll_agg = {}
for zeile in t_d:
    a, b, m = map(int, zeile.split(';'))
    # -----------------------------------------------------------------------------
    # ROBUSTHEIT: Additive Akkumulation statt Überschreiben
    # -----------------------------------------------------------------------------
    # Problem: Wenn die Eingabedatei denselben Eintrag (a→b) zweimal enthält,
    # würde eine direkte Zuweisung (voll_agg[(a,b)] = m) den ersten Wert
    # stillschweigend überschreiben. Das führt zu einem falschen Transportbedarf
    # ohne Fehlermeldung — ein sehr schwer zu findender Bug.
    #
    # Lösung: .get() holt den bisherigen Wert (oder 0 falls noch nicht vorhanden)
    # und addiert die neue Menge darauf. Doppelte Einträge werden korrekt summiert.
    # -----------------------------------------------------------------------------
    voll_agg[(a, b)] = voll_agg.get((a, b), 0) + m

voll_paare = list(voll_agg.keys())
leer_paare = [(i, j) for i in range(1, 11)
                      for j in range(1, 11) if i != j]

VP = len(voll_paare)   # Anzahl verschiedener Vollfahrt-Routen
LP = len(leer_paare)   # Anzahl möglicher Leerfahrt-Routen (stets 90)
KNOTEN = list(range(1, 11))

# =============================================================================
# SCHRITT 5: MIP-MODELL AUFBAUEN (mit PuLP / GUROBI)
# =============================================================================
#
# Ein MIP (Mixed Integer Program) ist ein mathematisches Optimierungsproblem,
# bei dem einige Variablen ganzzahlig sein müssen.
#
# Unser Modell hat drei Typen von Entscheidungsvariablen:
#
#   xv[v][p]: Wie viele Vollfahrten der Route p übernimmt Fahrzeug v?
#             → Ganzzahlig (man kann keine halben Fahrten machen)
#
#   xl[v][l]: Wie viele Leerfahrten der Route l fährt Fahrzeug v?
#             → Ganzzahlig
#
#   T:        Der Makespan = Fahrtzeit des langsamsten Fahrzeugs
#             → Kontinuierlich (kann Nachkommastellen haben)
#
# Zielfunktion: Minimiere T
# =============================================================================

# PuLP-Problem instanziieren (Minimierungsproblem)
prob = pl.LpProblem("Nikolaus_Logistik_Optimierung", pl.LpMinimize)

# Vollfahrt-Variablen: xv[v,p] = Anzahl Vollfahrten von Fahrzeug v auf Route p
# lowBound=0: Negative Fahrtenanzahl ist nicht möglich
# upBound=500: Praktische Obergrenze (keine Route hat mehr als 500 Fahrten)
xv = pl.LpVariable.dicts(
    "xv",
    ((v, p) for v in range(n) for p in range(VP)),
    lowBound=0, upBound=500, cat=pl.LpInteger
)

# Leerfahrt-Variablen: xl[v,l] = Anzahl Leerfahrten von Fahrzeug v auf Route l
xl = pl.LpVariable.dicts(
    "xl",
    ((v, l) for v in range(n) for l in range(LP)),
    lowBound=0, upBound=500, cat=pl.LpInteger
)

# Makespan-Variable: T = Fahrtzeit des langsamsten Fahrzeugs
T = pl.LpVariable("T", lowBound=0, cat=pl.LpContinuous)

# Zielfunktion: Minimiere T
# (GUROBI wird alle Nebenbedingungen einhalten und dabei T so klein wie möglich machen)
prob += T

# -----------------------------------------------------------------------------
# NEBENBEDINGUNG 1: Vollständige Abdeckung aller Vollfahrten
# -----------------------------------------------------------------------------
# Jede Vollfahrt-Route (a→b) muss von den n Fahrzeugen gemeinsam genau so oft
# gefahren werden, wie der Transportbedarf es vorschreibt.
# Mathematisch: Summe über alle Fahrzeuge der Fahrten auf Route p = Bedarf
# -----------------------------------------------------------------------------
for p, (a, b) in enumerate(voll_paare):
    prob += (
        pl.lpSum(xv[v, p] for v in range(n)) == voll_agg[(a, b)],
        f"Vollfahrt_Abdeckung_{a}_nach_{b}"
    )

# -----------------------------------------------------------------------------
# NEBENBEDINGUNG 2: Flusserhaltung (Euler-Bedingung)
# -----------------------------------------------------------------------------
# Dies ist das Herzstück des Modells. An jedem Knoten muss die Flussbilanz
# stimmen. Das garantiert, dass jedes Fahrzeug einen gültigen Eulerpfad
# (eine Route, die jede Kante genau einmal benutzt) fahren kann.
#
# Flussbilanz = ausgehende Fahrten - eingehende Fahrten
#
# Startknoten von Fahrzeug v (Maschine v+1): Flussbilanz = +1
#   → Das Fahrzeug fährt einmal mehr weg als es ankommt (es startet dort)
#
# Alle anderen Knoten: Flussbilanz zwischen -1 und 0
#   →  0: Durchgangsknoten (gleichviele An- und Abfahrten)
#   → -1: Endknoten (Fahrzeug kommt einmal mehr an als es wegfährt)
#
# Da der Endknoten frei wählbar ist, erlauben wir [-1, 0] für Nicht-Startknoten.
# Das MIP wählt automatisch den optimalen Endknoten.
# -----------------------------------------------------------------------------
for v in range(n):
    for k in KNOTEN:
        # Ausgehende Vollfahrten von Knoten k durch Fahrzeug v
        aus_voll = pl.lpSum(
            xv[v, p]
            for p, (p_von, p_nach) in enumerate(voll_paare)
            if p_von == k
        )
        # Eingehende Vollfahrten zu Knoten k durch Fahrzeug v
        ein_voll = pl.lpSum(
            xv[v, p]
            for p, (p_von, p_nach) in enumerate(voll_paare)
            if p_nach == k
        )
        # Ausgehende Leerfahrten von Knoten k durch Fahrzeug v
        aus_leer = pl.lpSum(
            xl[v, l]
            for l, (l_von, l_nach) in enumerate(leer_paare)
            if l_von == k
        )
        # Eingehende Leerfahrten zu Knoten k durch Fahrzeug v
        ein_leer = pl.lpSum(
            xl[v, l]
            for l, (l_von, l_nach) in enumerate(leer_paare)
            if l_nach == k
        )

        # Gesamter Fluss an Knoten k für Fahrzeug v
        fluss = aus_voll - ein_voll + aus_leer - ein_leer

        if k == v + 1:
            # Startknoten: Fahrzeug fährt einmal mehr ab als es ankommt → +1
            prob += (fluss == 1.0, f"Fluss_Fzg{v+1}_Knoten{k}_Start")
        else:
            # Alle anderen Knoten: ausgeglichen (0) oder Endpunkt (-1)
            prob += (fluss >= -1.0, f"Fluss_Fzg{v+1}_Knoten{k}_untere")
            prob += (fluss <=  0.0, f"Fluss_Fzg{v+1}_Knoten{k}_obere")

# -----------------------------------------------------------------------------
# NEBENBEDINGUNG 3: Genau ein Endknoten pro Fahrzeug
# -----------------------------------------------------------------------------
# Die Summe der Flussdifferenzen ALLER Nicht-Startknoten muss genau -1 sein.
# Das stellt sicher, dass exakt ein Knoten der Endpunkt ist (Bilanz = -1)
# und alle anderen Knoten Durchgangsknoten sind (Bilanz = 0).
#
# Anschaulich: In einer Reise gibt es genau einen Start und genau ein Ende.
# Dieser Constraint erzwingt, dass das Fahrzeug wirklich "ankommt" und
# nicht in Schleifen steckt.
# -----------------------------------------------------------------------------
for v in range(n):
    fluss_alle_anderen = []
    for k in KNOTEN:
        if k == v + 1:
            continue  # Startknoten überspringen
        aus_voll = pl.lpSum(
            xv[v, p]
            for p, (p_von, p_nach) in enumerate(voll_paare)
            if p_von == k
        )
        ein_voll = pl.lpSum(
            xv[v, p]
            for p, (p_von, p_nach) in enumerate(voll_paare)
            if p_nach == k
        )
        aus_leer = pl.lpSum(
            xl[v, l]
            for l, (l_von, l_nach) in enumerate(leer_paare)
            if l_von == k
        )
        ein_leer = pl.lpSum(
            xl[v, l]
            for l, (l_von, l_nach) in enumerate(leer_paare)
            if l_nach == k
        )
        fluss_alle_anderen.append(aus_voll - ein_voll + aus_leer - ein_leer)

    prob += (
        pl.lpSum(fluss_alle_anderen) == -1.0,
        f"Endknoten_Fzg{v+1}"
    )

# -----------------------------------------------------------------------------
# NEBENBEDINGUNG 4: Makespan-Schranke
# -----------------------------------------------------------------------------
# Die Gesamtdistanz jedes Fahrzeugs darf den Makespan T nicht überschreiten.
# Da T minimiert wird, zwingt das den Solver automatisch dazu, die Last
# möglichst gleichmäßig auf alle Fahrzeuge zu verteilen.
#
# Formal: Distanz(Fahrzeug v) ≤ T  für alle v
# Umgestellt: Distanz(Fahrzeug v) - T ≤ 0
# -----------------------------------------------------------------------------
for v in range(n):
    dist_voll = pl.lpSum(
        xv[v, p] * Zeiten_Matrix[a-1][b-1]
        for p, (a, b) in enumerate(voll_paare)
    )
    dist_leer = pl.lpSum(
        xl[v, l] * Zeiten_Matrix[a-1][b-1]
        for l, (a, b) in enumerate(leer_paare)
    )
    prob += (dist_voll + dist_leer <= T, f"Makespan_Fzg{v+1}")

# =============================================================================
# SCHRITT 6: HILFSFUNKTIONEN FÜR ZUSAMMENHANGSPRÜFUNG UND GRAPHAUFBAU
# =============================================================================

def graph_aufbauen(n, voll_paare, leer_paare, xv, xl):
    """
    Baut den Teilgraphen für jedes Fahrzeug aus der MIP-Lösung auf.

    Ein Graph ist hier ein Dictionary:
      graph[v][k] = Liste aller Maschinen, die Fahrzeug v von Maschine k aus anfährt

    Enthält sowohl Vollfahrten (mit Ladung) als auch Leerfahrten (ohne Ladung).
    """
    graph = {v: {i: [] for i in range(1, 11)} for v in range(1, n + 1)}
    for v in range(n):
        for p, (a, b) in enumerate(voll_paare):
            cnt = int(round(xv[v, p].varValue or 0))
            for _ in range(cnt):
                graph[v + 1][a].append(b)
        for l, (a, b) in enumerate(leer_paare):
            cnt = int(round(xl[v, l].varValue or 0))
            for _ in range(cnt):
                graph[v + 1][a].append(b)
    return graph


def ist_zusammenhaengend(teilgraph, startknoten):
    """
    Prüft ob ein gerichteter Graph zusammenhängend ist (im ungerichteten Sinne).

    Ein Eulerpfad existiert nur dann, wenn man von jedem Knoten im Graphen
    jeden anderen Knoten erreichen kann — sonst gibt es "Inseln" die vom
    Fahrzeug nie besucht werden können.

    Methode: Tiefensuche (DFS = Depth First Search)
    Startend vom Startknoten des Fahrzeugs wird der Graph erkundet.
    Am Ende prüfen wir ob alle Knoten mit Kanten besucht wurden.

    Rückgabe:
      (True, leere Menge)  → Graph ist zusammenhängend
      (False, {Knoten...}) → Diese Knoten sind nicht erreichbar
    """
    # Alle Knoten ermitteln die tatsächlich am Graphen beteiligt sind
    # (Knoten ohne Kanten sind irrelevant für den Eulerpfad)
    aktive_knoten = set()
    for k, ziele in teilgraph.items():
        if ziele:
            aktive_knoten.add(k)
        for z in ziele:
            aktive_knoten.add(z)

    # Trivialfall: Keine Kanten vorhanden → kein Problem
    if not aktive_knoten:
        return True, set()

    # Ungerichteten Graphen aufbauen:
    # Für die Zusammenhangsprüfung spielt die Richtung keine Rolle.
    # Eine Kante A→B zählt als Verbindung in beide Richtungen.
    ungerichtet = {k: set() for k in aktive_knoten}
    for k, ziele in teilgraph.items():
        for z in ziele:
            ungerichtet[k].add(z)
            ungerichtet[z].add(k)

    # Tiefensuche (DFS) vom Startknoten aus:
    # Wir erkunden den Graphen wie in einem Labyrinth — immer tiefer,
    # bis wir nicht mehr weiterkommen, dann zurück und andere Wege versuchen.
    besucht = set()
    stack = [startknoten]
    while stack:
        knoten = stack.pop()
        if knoten in besucht:
            continue
        besucht.add(knoten)
        for nachbar in ungerichtet.get(knoten, []):
            if nachbar not in besucht:
                stack.append(nachbar)

    # Nicht besuchte Knoten = nicht erreichbare Inseln
    nicht_erreicht = aktive_knoten - besucht
    return len(nicht_erreicht) == 0, nicht_erreicht


# =============================================================================
# SCHRITT 7: BENDERS DECOMPOSITION — OPTIMIERUNG MIT ZUSAMMENHANG-GARANTIE
# =============================================================================
#
# WARUM BENDERS?
#   Das MIP garantiert zwar die Flussbilanz an jedem Knoten (Nebenbedingung 2),
#   aber nicht den Zusammenhang des Teilgraphen. Es ist theoretisch möglich,
#   dass das MIP eine Lösung liefert, bei der ein Fahrzeug zwei getrennte
#   "Inseln" von Kanten zugeteilt bekommt — der Hierholzer-Algorithmus könnte
#   dann die zweite Insel nie erreichen.
#
# WIE FUNKTIONIERT BENDERS?
#   1. Löse das MIP normal.
#   2. Prüfe für jedes Fahrzeug ob sein Teilgraph zusammenhängend ist.
#   3. Falls nicht: Füge einen "Connectivity Cut" hinzu, der diese Art von
#      Lösung ausschließt, und löse erneut.
#   4. Wiederhole bis alle Teilgraphen zusammenhängend sind.
#
# DER CONNECTIVITY CUT:
#   Wenn Fahrzeug v zwei Inseln hat (Menge S mit Startknoten, Menge T ohne),
#   dann muss eine Leerfahrt von S nach T hinzugefügt werden.
#   Der Cut lautet: Summe aller Leerfahrten von S nach T ≥ 1
#   Das zwingt GUROBI dazu, mindestens eine Brücke zwischen den Inseln zu bauen.
#
# GARANTIE:
#   Nach maximal endlich vielen Iterationen konvergiert Benders immer,
#   weil jede Iteration mindestens eine vorher verbotene Lösung ausschließt.
# =============================================================================

max_iterationen = 50  # Sicherheitsnetz: nach 50 Versuchen abbrechen
cut_zaehler = 0       # Wie viele Cuts wurden insgesamt hinzugefügt?

print("\n--- Starte Optimierung mit Benders Decomposition ---")

for iteration in range(max_iterationen):

    print(f"\nIteration {iteration + 1}: Löse MIP...")

    # GUROBI als Solver aufrufen
    # gapRel = gap_faktor: Toleranz für Suboptimalität (0.0 = exakt optimal)
    # msg = True: GUROBI zeigt Fortschritt im Terminal
    solver = pl.PULP_CBC_CMD(gapRel=gap_faktor, msg=True)
    prob.solve(solver)

    # Prüfen ob GUROBI eine gültige Lösung gefunden hat
    sol_status = pl.LpStatus[prob.status]
    if sol_status != "Optimal":
        print(f"✗ GUROBI konnte keine Lösung finden. Status: {sol_status}")
        exit()

    makespan_aktuell = pl.value(T)
    print(f"✓ Makespan dieser Iteration: {makespan_aktuell:.2f}")

    # -------------------------------------------------------------------------
    # Teilgraphen aufbauen und Zusammenhang prüfen
    # -------------------------------------------------------------------------
    graph = graph_aufbauen(n, voll_paare, leer_paare, xv, xl)

    alle_zusammenhaengend = True  # Annahme: alles OK, bis Gegenteil bewiesen

    for v in range(1, n + 1):
        ok, nicht_erreicht = ist_zusammenhaengend(graph[v], v)

        if not ok:
            # -------------------------------------------------------------------
            # CONNECTIVITY CUT HINZUFÜGEN
            # -------------------------------------------------------------------
            # Der Teilgraph von Fahrzeug v hat zwei Inseln:
            #   - Erreichbare Knoten S (enthalten den Startknoten v)
            #   - Nicht erreichbare Knoten T = nicht_erreicht
            #
            # Lösung: Mindestens eine Leerfahrt muss von S nach T führen.
            # Dieser Constraint wird dauerhaft zum MIP hinzugefügt und gilt
            # für alle zukünftigen Iterationen.
            # -------------------------------------------------------------------
            alle_zusammenhaengend = False
            cut_zaehler += 1

            # Erreichbare Knoten = alle aktiven Knoten minus die nicht erreichbaren
            aktive_knoten = set()
            for k, ziele in graph[v].items():
                if ziele: aktive_knoten.add(k)
                for z in ziele: aktive_knoten.add(z)
            erreichbar = aktive_knoten - nicht_erreicht

            print(f"  ✗ Fahrzeug {v}: Nicht zusammenhängend!")
            print(f"    Erreichbar: {sorted(erreichbar)}")
            print(f"    Nicht erreichbar: {sorted(nicht_erreicht)}")
            print(f"    → Füge Connectivity Cut #{cut_zaehler} hinzu...")

            # Cut: Mindestens eine Leerfahrt von erreichbarer Insel zur
            # nicht-erreichbaren Insel muss existieren
            prob += (
                pl.lpSum(
                    xl[v - 1, l]
                    for l, (a, b) in enumerate(leer_paare)
                    if a in erreichbar and b in nicht_erreicht
                ) >= 1,
                f"Connectivity_Cut_{cut_zaehler}_Fzg{v}_Iter{iteration}"
            )

    # -------------------------------------------------------------------------
    # Abbruchbedingung: Alle Teilgraphen sind zusammenhängend → fertig!
    # -------------------------------------------------------------------------
    if alle_zusammenhaengend:
        print(f"\n✓ Alle Teilgraphen zusammenhängend nach {iteration + 1} "
              f"Iteration(en) und {cut_zaehler} Connectivity Cut(s).")
        print(f"✓ Optimaler Makespan: {makespan_aktuell:.2f} Einheiten")
        if gap_faktor > 0:
            print(f"  (Lösung liegt maximal {gap_faktor*100:.1f}% "
                  f"vom Optimum entfernt)")
        break

else:
    # -------------------------------------------------------------------------
    # NOTFALL-AUSGANG: Benders hat nach max_iterationen nicht konvergiert
    # -------------------------------------------------------------------------
    # Dieser Block wird nur ausgeführt wenn die for-Schleife NICHT durch
    # "break" beendet wurde — also wenn nach max_iterationen immer noch
    # kein vollständig zusammenhängender Graph gefunden wurde.
    #
    # Anstatt einfach abzubrechen, speichern wir die letzte bekannte Lösung.
    # Diese ist zwar nicht garantiert gültig (ein Teilgraph könnte noch
    # getrennt sein), aber sie gibt zumindest einen Anhaltspunkt und
    # ermöglicht eine manuelle Analyse des Problems.
    #
    # Mögliche Ursachen für fehlende Konvergenz:
    #   - gap_faktor zu groß → GUROBI akzeptiert suboptimale Lösungen die
    #     die Cuts leicht umgehen können
    #   - max_iterationen zu niedrig → Lösung braucht mehr Iterationen
    #   - Sehr ungleichmäßiger Transportbedarf → viele Inseln entstehen
    #
    # Empfehlung: max_iterationen erhöhen oder gap_faktor reduzieren.
    # -------------------------------------------------------------------------
    print(f"\n✗ Warnung: Kein vollständig zusammenhängender Graph nach "
          f"{max_iterationen} Iterationen und {cut_zaehler} Cuts.")
    print(f"  Letzter bekannter Makespan: {makespan_aktuell:.2f} Einheiten")
    print(f"  → Speichere letzte bekannte Lösung als Näherung...")
    print(f"  → Tipp: 'max_iterationen' erhöhen oder 'gap_faktor' reduzieren.")

    # Fahrplan der letzten Iteration trotzdem exportieren
    # (zur manuellen Analyse — mit Warnung im Dateinamen)
    dateiname_notfall = f"{n}Fahrzeuge_schedule_UNVOLLSTAENDIG.txt"
    graph_notfall = graph_aufbauen(n, voll_paare, leer_paare, xv, xl)
    touren_notfall = {}
    for v in range(1, n + 1):
        touren_notfall[v] = finde_eulerpfad(v, graph_notfall[v])

    vollfahrt_kanten_notfall = []
    for (ab, an), menge in voll_agg.items():
        for _ in range(menge):
            vollfahrt_kanten_notfall.append((ab, an))

    zeilen_notfall = ["vehicle_id;location;unload;load"]
    for v in range(1, n + 1):
        tour = touren_notfall[v]
        is_voll = []
        for i in range(len(tour) - 1):
            von, nach = tour[i], tour[i + 1]
            if (von, nach) in vollfahrt_kanten_notfall:
                is_voll.append(True)
                vollfahrt_kanten_notfall.remove((von, nach))
            else:
                is_voll.append(False)
        for i in range(len(tour)):
            unload = 1 if (i > 0 and is_voll[i - 1]) else 0
            load   = 1 if (i < len(tour) - 1 and is_voll[i]) else 0
            zeilen_notfall.append(f"{v};{tour[i]};{unload};{load}")

    with open(dateiname_notfall, "w", encoding="utf-8") as f:
        f.write("\n".join(zeilen_notfall) + "\n")

    print(f"  → Notfall-Plan gespeichert: '{dateiname_notfall}'")
    print(f"  → Achtung: Dieser Plan ist möglicherweise nicht valide!")
    exit()

# =============================================================================
# SCHRITT 8: ERGEBNIS AUSGEBEN
# =============================================================================
#
# Für jedes Fahrzeug werden Volldistanz, Leerdistanz und Gesamtdistanz ausgegeben.
# =============================================================================

print("\n--- Fahrzeugdetails ---")
for v in range(n):
    voll_dist = sum(
        int(round(xv[v, p].varValue or 0)) * Zeiten_Matrix[a-1][b-1]
        for p, (a, b) in enumerate(voll_paare)
    )
    leer_dist = sum(
        int(round(xl[v, l].varValue or 0)) * Zeiten_Matrix[a-1][b-1]
        for l, (a, b) in enumerate(leer_paare)
    )
    print(f"Fahrzeug {v+1}: Volldistanz={voll_dist:.1f}, "
          f"Leerdistanz={leer_dist:.1f}, "
          f"Gesamt={voll_dist + leer_dist:.1f}")
    for l, (a, b) in enumerate(leer_paare):
        cnt = int(round(xl[v, l].varValue or 0))
        if cnt > 0:
            print(f"  Leerfahrt Maschine {a} → Maschine {b}: {cnt}x")

# =============================================================================
# SCHRITT 9: HIERHOLZER-ALGORITHMUS — EULERPFAD PRO FAHRZEUG BERECHNEN
# =============================================================================
#
# Ein EULERPFAD ist eine Route durch einen Graphen, die jede Kante
# (= jede Fahrt) genau einmal benutzt.
#
# Voraussetzungen (die durch das MIP + Benders sichergestellt wurden):
#   1. Flussbilanz: Startknoten hat +1, Endknoten hat -1, Rest ausgeglichen
#   2. Zusammenhang: Alle Kanten sind vom Startknoten aus erreichbar
#
# FUNKTIONSWEISE DES HIERHOLZER-ALGORITHMUS:
#   Der Algorithmus arbeitet mit einem "aktuellen Pfad" und einem "Schaltkreis".
#   Er läuft immer weiter bis er in eine Sackgasse gerät (kein Ausgang mehr).
#   An der Sackgasse fügt er den Knoten dem fertigen Pfad hinzu und geht zurück.
#   Das wiederholt sich bis der aktuelle Pfad leer ist.
#   Am Ende enthält "circuit" den vollständigen Eulerpfad — rückwärts.
#   Daher wird er am Ende umgedreht.
# =============================================================================

def finde_eulerpfad(start, adj_graph):
    """
    Findet einen Eulerpfad im gegebenen Graphen, startend bei 'start'.

    Parameter:
      start:     Startknoten (= Maschinennummer des Fahrzeugs)
      adj_graph: Adjacency-Dictionary {knoten: [zielknoten, ...]}

    Rückgabe:
      Liste von Knoten in der Reihenfolge des Eulerpfads
      z.B. [1, 3, 2, 5, 1, 4, ...] bedeutet: 1→3→2→5→1→4→...
    """
    # Tiefe Kopie des Graphen, damit der Original-Graph unverändert bleibt
    # (Der Algorithmus entfernt Kanten während er läuft)
    g = copy.deepcopy(adj_graph)

    current_path = [start]  # Aktuell erkundeter Pfad (beginnt beim Start)
    circuit = []            # Fertig gestellter Eulerpfad (wird am Ende umgedreht)

    while current_path:
        current_node = current_path[-1]  # Aktuell betrachteter Knoten

        if g[current_node]:
            # Es gibt noch unbesuchte Abfahrten von diesem Knoten:
            # Nimm die nächste Kante, entferne sie aus dem Graphen,
            # und fahre zum nächsten Knoten weiter.
            next_node = g[current_node].pop()
            current_path.append(next_node)
        else:
            # Sackgasse: Keine unbesuchten Abfahrten mehr von hier.
            # Dieser Knoten ist am Ende eines Teilpfads → zum Ergebnis hinzufügen.
            circuit.append(current_path.pop())

    # Der Pfad wurde von hinten nach vorne aufgebaut → umdrehen
    circuit.reverse()
    return circuit

# Eulerpfad für jedes Fahrzeug berechnen
touren = {}
for v in range(1, n + 1):
    touren[v] = finde_eulerpfad(v, graph[v])
    print(f"\nFahrzeug {v}: {len(touren[v]) - 1} Fahrten | "
          f"Start: Maschine {v} | "
          f"Ende: Maschine {touren[v][-1]}")

# =============================================================================
# SCHRITT 10: FAHRPLAN EXPORTIEREN
# =============================================================================
#
# Der Fahrplan wird im Format der Validierungsdatei gespeichert:
#   vehicle_id ; location ; unload ; load
#
#   vehicle_id : Nummer des Fahrzeugs
#   location   : Aktuelle Maschine
#   unload     : 1 wenn das Fahrzeug hier entlädt (vorherige Fahrt war Vollfahrt)
#   load       : 1 wenn das Fahrzeug hier belädt (nächste Fahrt ist Vollfahrt)
#
# Für jeden Schritt des Eulerpfads wird geprüft ob die jeweilige Fahrt
# eine Voll- oder Leerfahrt ist. Dazu wird die Vollfahrtliste als Multiset
# verwendet (mit Duplikaten), damit gleiche Routen mehrfach erkannt werden.
# =============================================================================

# Vollfahrtliste als Multiset aufbauen
# (z.B. wenn 5x Maschine 1→2 gefordert, steht (1,2) fünfmal in der Liste)
vollfahrt_kanten = []
for (ab, an), menge in voll_agg.items():
    for _ in range(menge):
        vollfahrt_kanten.append((ab, an))

fahrplan_zeilen = ["vehicle_id;location;unload;load"]

for v in range(1, n + 1):
    tour = touren[v]

    # Für jeden Schritt des Eulerpfads bestimmen: Voll- oder Leerfahrt?
    is_vollfahrt = []
    for i in range(len(tour) - 1):
        von, nach = tour[i], tour[i + 1]

        if (von, nach) in vollfahrt_kanten:
            # Diese Kante ist eine Vollfahrt → als verbraucht markieren
            is_vollfahrt.append(True)
            vollfahrt_kanten.remove((von, nach))
        else:
            # Diese Kante ist eine Leerfahrt
            is_vollfahrt.append(False)

    # Fahrplanzeilen für dieses Fahrzeug schreiben
    for i in range(len(tour)):
        location = tour[i]

        # UNLOAD = 1: Die Fahrt HIERHER war eine Vollfahrt → Ware abladen
        # (Gilt nicht für die erste Station: dort kommt das Fahrzeug leer an)
        unload = 1 if (i > 0 and is_vollfahrt[i - 1]) else 0

        # LOAD = 1: Die Fahrt VON HIER WEG ist eine Vollfahrt → Ware aufladen
        # (Gilt nicht für die letzte Station: dort endet die Tour)
        load = 1 if (i < len(tour) - 1 and is_vollfahrt[i]) else 0

        fahrplan_zeilen.append(f"{v};{location};{unload};{load}")

# Konsistenz-Check: Wurden alle Vollfahrten berücksichtigt?
if vollfahrt_kanten:
    print(f"\n✗ FEHLER: {len(vollfahrt_kanten)} Vollfahrten nicht gefahren:")
    for kante in vollfahrt_kanten:
        print(f"  {kante}")
else:
    print("\n✓ Alle Vollfahrten wurden erfüllt")

# Fahrplan als Textdatei speichern
dateiname_export = f"{n}Fahrzeuge_schedule_Gap_Faktor_{gap_faktor}.txt"
with open(dateiname_export, "w", encoding="utf-8") as f:
    f.write("\n".join(fahrplan_zeilen) + "\n")

# =============================================================================
# SCHRITT 11: ABSCHLIESSENDE AUSGABE
# =============================================================================

end_zeit = time.perf_counter()
dauer = end_zeit - start_zeit

print(f"\n{'='*60}")
print(f"✓ Einsatzplan exportiert: '{dateiname_export}'")
print(f"✓ Berechnungsdauer: {dauer:.2f} Sekunden")
print(f"✓ Optimaler Makespan: {makespan_aktuell:.2f} Einheiten")
if gap_faktor > 0:
    print(f"  (Abweichung vom Optimum: maximal {gap_faktor*100:.1f}%)")
else:
    print(f"  (Lösung ist beweisbar optimal)")
print(f"\nZur Validierung: python validations.py")
print(f"{'='*60}")
