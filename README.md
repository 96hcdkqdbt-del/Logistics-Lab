# Transportplanung: ALNS & Nikolaus-Problem

Dieses Repository enthält drei Python-Skripte zur Lösung eines Fahrzeug-Transportplanungsproblems in einem Produktionsnetzwerk: Ein oder mehrere Fahrzeuge müssen eine Menge geforderter Transporte ("Vollfahrten") zwischen Maschinen abfahren. Ziel ist es, die Gesamtfahrzeit (bzw. den Makespan) durch möglichst wenige und kurze Leerfahrten zu minimieren.

Alle drei Skripte lesen dieselben zwei Eingabedateien ein und exportieren am Ende einen validierbaren Fahrplan.

## Skripte im Überblick

| Skript | Ansatz | Fahrzeuge |
|---|---|---|
| `Einkoerper_ALNS.py` | Metaheuristik (ALNS) | 1 |
| `Mehrkoerper_ALNS_Konzept_2.py` | Metaheuristik (ALNS) | n (mehrere) |
| `Nikolaus_final_v2.py` | Exaktes MIP-Modell (Solver) + Hierholzer-Algorithmus | n (mehrere) |

---

### 1. `Einkoerper_ALNS.py`
Löst das Problem für **ein einzelnes Fahrzeug** mit einem Adaptive-Large-Neighborhood-Search-Verfahren (ALNS):
- Baut aus dem Transportbedarf zunächst einen initialen Fahrplan.
- Entfernt iterativ die "schlechtesten" Fahrten (`worst_removal`) und fügt sie mit unterschiedlichen Strategien wieder ein (`greed_repair`, `regret_instertion`, clusterbasierte Verfahren).
- Bewertet die Verfahren laufend über ein Scoring-System (Simulated-Annealing-artige Akzeptanz von Verschlechterungen) und passt so die Auswahlwahrscheinlichkeit der Operatoren adaptiv an.
- Exportiert am Ende den optimierten Fahrplan sowie eine CSV mit dem Verlauf der Operator-Scores.

### 2. `Mehrkoerper_ALNS_Konzept_2.py`
Erweiterung des Einkörper-Ansatzes auf **mehrere Fahrzeuge** (Standard: 5, siehe `Anz_Fahrzeuge`):
- Gleiche ALNS-Grundlogik (Removal-/Repair-Operatoren, Cluster-Aufbau, adaptives Scoring), jedoch zusätzlich mit einem Lastausgleich zwischen den Fahrzeugen (`fahrzeug_ausgleich`) und einer Zielfunktion, die neben der Gesamtfahrzeit auch die maximale Fahrzeit und die Standardabweichung zwischen den Fahrzeugen berücksichtigt (Gewichtung über `w_gesamt`, `w_max`, `w_std`).
- Exportiert den finalen Auftragsplan sowie Ergebnis- und Score-Tabellen als CSV.

### 3. `Nikolaus_final_v2.py`
Löst das Problem **exakt** als gemischt-ganzzahliges lineares Programm (MIP):
- Formuliert das Problem mit `pulp` (Solver: CBC/GUROBI) als Flussproblem mit Makespan-Minimierung.
- Fahrzeug *v* startet fest an Maschine *v*.
- Stellt über eine Benders-Decomposition sicher, dass jeder Fahrzeug-Teilgraph zusammenhängend ist (sonst wird ein Cut hinzugefügt und erneut gelöst).
- Berechnet aus der Lösung mit dem **Hierholzer-Algorithmus** einen gültigen Eulerpfad (die tatsächliche Route) je Fahrzeug.
- Fragt bei Ausführung interaktiv die Anzahl der Fahrzeuge (`n`, 1–10) und den Optimierungs-Toleranzfaktor (`gap_faktor`) ab.
- Exportiert den Fahrplan als Textdatei `<n>Fahrzeuge_schedule_Gap_Faktor_<gap_faktor>.txt`.

---

## Voraussetzungen

- **Python 3.x**
- Benötigte Pakete:
  ```
  pip install pandas numpy pulp
  ```
- ⚠️ **Windows-only:** `Einkoerper_ALNS.py` und `Mehrkoerper_ALNS_Konzept_2.py` nutzen das Modul `msvcrt` (Tastaturabfrage zum Abbrechen der Optimierung per Taste `t`). Diese Skripte laufen daher **nicht ohne Anpassung unter macOS/Linux** – dort müsste die entsprechende `msvcrt`-Abfrage entfernt oder ersetzt werden.
- `Nikolaus_final_v2.py` nutzt standardmäßig den in `pulp` enthaltenen CBC-Solver (`PULP_CBC_CMD`). Der Code-Kommentar erwähnt GUROBI als ursprünglich vorgesehenen kommerziellen Solver; für dessen Nutzung wäre eine gültige GUROBI-Installation/Lizenz sowie eine Anpassung des Solver-Aufrufs nötig.

## Eingabedateien

Alle drei Skripte erwarten im Arbeitsverzeichnis zwei Textdateien mit Header-Zeile, `;`-getrennt:

**`machine_positions.txt`**
```
machine_id;x;y
1;50;10
2;30;30
...
```

**`transport_demand.txt`**
```
von;nach;anzahl
1;3;2
...
```
(`von`/`nach` = Maschinen-IDs, `anzahl` = Anzahl geforderter Vollfahrten zwischen diesen Maschinen)

## Ausführung

```bash
python Einkoerper_ALNS.py
python Mehrkoerper_ALNS_Konzept_2.py
python Nikolaus_final_v2.py   # fragt interaktiv nach Fahrzeuganzahl und Toleranz
```

## Ausgabedateien

| Skript | Fahrplan-Export | Zusatz-Exporte |
|---|---|---|
| `Einkoerper_ALNS.py` | `Fahrplan_schedule.txt` | `Ergbnis_Tabelle_scores_fct_Einkörper.csv` |
| `Mehrkoerper_ALNS_Konzept_2.py` | `schedule_alns.txt` | `Ergbnis_Tabelle_Mehrkörper_AlNS.csv`, `Tabelle_Scores_fct.csv` |
| `Nikolaus_final_v2.py` | `<n>Fahrzeuge_schedule_Gap_Faktor_<gap_faktor>.txt` (bzw. `..._UNVOLLSTAENDIG.txt` bei Abbruch) | – |

Die exportierten Fahrpläne folgen dem Format `vehicle_id;location/machine_id;unload;load` und sind für die Prüfung mit einem separaten `validations.py`-Skript vorgesehen (wird von den hier enthaltenen Skripten vorausgesetzt, ist aber nicht Teil dieses Repositories).

## Hinweis

Die Kommentare und Variablennamen in den Skripten sind auf Deutsch gehalten. Einige Codeteile (z. B. Testschleifen über verschiedene Verhältnis-/Gewichtungswerte) sind in den Dateien auskommentiert und können bei Bedarf für Parameterstudien reaktiviert werden.
