# Scheduling Deadline Simulator

Ovaj projekat predstavlja simulator za poređenje CPU scheduling algoritama na osnovu real-time mera performansi.

Glavni cilj je analiza kako se različiti algoritmi raspoređivanja ponašaju kada zadaci imaju rokove i koliko često maše rokove i kako se ponašanje menja pod uticajem sporijeg/udaljenog memorijskog tier-a.

Pored klasičnih workload-a sa procesima, projekat podržava i periodične real-time taskove kroz implementaciju RMS (Rate Monotonic Scheduling) algoritma.

## Ideja projekta

Klasične mere poput prosečnog vremena čekanja i prosečnog turnaround vremena nisu dovoljne za real-time sisteme. Kod real-time zadataka bitno je da li proces završava pre svog roka.

Mere za poređenje algoritama:

- Prosečno vreme čekanja (Avg. waiting time)
- Prosečno vreme prolaska zadatka (Avg. turnaround time)
- Prosečno vreme odaziva (Avg. response time)
- Brojač za promašene rokove (Deadline miss count)
- Odnos promašenih rokova (Deadline miss ratio)

Pored osnovnog raspoređivanja, projekat uvodi i pojednostavljen model sporijeg/udaljenog memorijskog tier-a. Procesima koji koriste takav memorijski tier se može povećati efektivno vreme izvršavanja, proporcionalno njihovom memorijskom intenzitetu.

## Implementirani algoritmi:

- FCFS - First-Come, First-Served
- Round Robin
- SPN / SJF - Shortest Process Next / Shortest Job First
- SRT - Shortest Remaining Time
- HRRN - Highest Response Ratio Next
- RMS - Rate Monotonic Scheduling
- EDF - Earliest Deadline First

Prvih 5 algoritama radne nad običnim procesima definisanim kroz `arriva_time`, `burst_time` i `deadline`.

RMS i EDF se koriste za real-time scenarije. RMS je posebno namenjen periodičnim taskovima:

```txt
kraći period = viši prioritet
```

Dok EDF bira proces ili task instancu sa najranijim apsolutnim deadline-om:

```txt
raniji deadline = viši prioritet
```

## Memory penalty model

Projekat ne simulira konkretan hardverski protokol niti stvarnu memorijsku arhitekturu. Sporija ili udaljena memorija je modelovana parametarski, kroz povećanje efektivnog vremena izvršavanja procesa.

- `base_burst_time` - originalno vreme izvršavanja iz workload fajla
- `effective_burst_time` - vreme izvršavanja koje scheduler stvarno koristi nakon primene memorijskog penala

Formula koja se koristi je:

```txt
  effective_burst_time = ceil(base_burst_time * (1 + memory_penalty_factor * memory_intensity))
```

Gde je:

- `memory_penalty_factor` - parametar koji određuje koliko je sporiji memorijski tier skuplji u simulaciji
- `memory_intensity` - koliko je proces osetljiv na memorijske pristupe

Ako je proces u lokalnoj memoriji (DRAM), penal se ne primenjuje.

Svrha modela je da omogući kontrolisanu analizu uticaja sporije memorije na scheduling mere i deadline miss ratio.

## Periodični taskovi, RMS i EDF

Pored običnih procesa, simulator podržava i periodične real-time taskove.

Periodični task se opisuje pomoću:

- `task_id` - identifikator taska
- `period` - period ponavljanja taska
- `execution_time` - vreme izvršavanja svake instance
- `relative_deadline` - rok relativan u odnosu na vreme dolaska instance
- `memory_tier` - memorijski tier taska
- `memory_intensity` - osetljivost na memorijski penal

Primer periodičnog taska:

```json
{
  "task_id": "T1",
  "period": 5,
  "execution_time": 1,
  "relative_deadline": 5,
  "memory_tier": "local_dram",
  "memory_intensity": 0.2
}
```

Generator periodičnih taskova od jednog taska pravi više konkretnih procesnih instanci.

Na primer:
`T1, period = 5, simulation_time = 20`

generiše:

```txt
T1_0 arrival=0
T1_1 arrival=5
T1_2 arrival=10
T1_3 arrival=15
```

RMS je preemptive fixed-priority algoritam. Prioritet se određuje na osnovu periode taska:

```txt
manji period = veći prioritet
```

Zbog toga task sa kraćom periodom može da prekine task sa dužom periodom.

EDF, odnosno Earliest Deadline First, je preemptive dynamic-priority algoritam.

Za razliku od RMS-a, EDF ne dodeljuje fiksan prioritet na osnovu periode taska. Umesto toga, u svakom trenutku bira dostupnu procesnu instancu sa najranijim apsolutnim deadline-om.

Pravilo EDF algoritma je:

```txt
raniji deadline = viši prioritet
```

## Struktura projekta

```txt
os2-scheduling-deadline-simulator/
│
├── data/
│   ├── workload_basic.json
│   ├── workload_spn_vs_hrrn.json
│   ├── workload_remote_memory.json
│   └── periodic_tasks_basic.json
│
├── docs/
│   └── analysis.md
│
├── scheduler/
│   ├── algorithms/
│   │   ├── fcfs.py
│   │   ├── hrrn.py
│   │   ├── rms.py
│   │   ├── edf.py
│   │   ├── rr.py
│   │   ├── spn.py
│   │   └── srt.py
│   │
│   ├── csv_exporter.py
│   ├── memory_penalty.py
│   ├── metrics.py
│   ├── models.py
│   ├── periodic_task_generator.py
│   ├── periodic_task_loader.py
│   ├── timeline.py
│   └── workload_loader.py
│
├── main.py
├── run_experiments.py
├── run_rms.py
├── run_periodic_experiments.py
├── plot_results.py
├── plot_timeline.py
├── requirements.txt
└── README.md
```

## Instalacija

Preporučeno je koristiti Python virtual environment.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Pokretanje jednog workload-a

Default workload:
`python .\main.py`

Pokretanje konkretnog workload-a:
`python .\main.py .\data\workload_basic.json`

Pokretanje workload-a sa podešenim Round Robin kvantumom (default quantum = 2):
`python .\main.py .\data\workload_spn_vs_hrrn.json --quantum 3`

Pokretanje workload-a sa uključenim memory penalty modelom:
`python .\main.py .\data\workload_remote_memory.json --enable-memory-penalty --memory-penalty-factor 0.5 --output-dir .\results\memory_penalty_factor_0_5`

## Pokretanje periodičnih real-time eksperimenata

Periodični real-time eksperimenti se pokreću posebnom skriptom:

```powershell
python .\run_periodic_experiments.py
```

Ova skripta pokreće RMS i EDF nad periodičnim workload-om sa više vrednosti `memory_penalty_factor`.

Rezultati se čuvaju u:

```txt
results/periodic_experiments/
```

Glavni zbirni fajl za periodične eksperimente je:

```txt
results/periodic_experiments/combined_periodic_metrics.csv
```

Primeri pojedinačnih eksperimenata:

```txt
periodic_basic
periodic_memory_penalty_factor_0_25
periodic_memory_penalty_factor_0_5
periodic_memory_penalty_factor_1_0
```

U svakom od ovih eksperimenata se generišu rezultati za RMS i EDF.

## Pokretanje svih eksperimenata:

Svi predefinisani eksperimenti se mogu pokrenuti komandom:
`python .\run_experiments.py`

Ova skripta pokreće više scenarija i generiše rezultate u folderu:
`results/experiments/`

Glavni zbirni fajl:
`results/experiments/combined_metrics.csv`

## Pokretanje periodičnih RMS eksperimenata

Periodični RMS eksperimenti se pokreću posebnom skriptom:

```powershell
python .\run_periodic_experiments.py
```

Ova skripta pokreće RMS nad periodičnim workload-om sa više vrednosti `memory_penalty_factor`.

Rezultati se čuvaju u:

```txt
results/periodic_experiments/
```

Glavni zbirni fajl za periodične eksperimente je:

```txt
results/periodic_experiments/combined_periodic_metrics.csv
```

Primeri pojedinačnih RMS eksperimenata:

```txt
rms_basic
rms_memory_penalty_factor_0_25
rms_memory_penalty_factor_0_5
rms_memory_penalty_factor_1_0
```

## Generisanje grafikona

Nakon pokretanja eksperimenata, grafikoni se generišu komandom:
`python .\plot_results.py`

Grafikoni se čuvaju u:
`results/experiments/plots/`

Generišu se grafikoni za:

- deadline miss ratio
- average waiting time
- average turnaround time
- average response time
- trend deadline miss ratio kroz različite memory penalty faktore

Pored zbirnih grafikona, moguće je generisati i Gantt/timeline prikaz izvršavanja procesa.

Primer za običan workload:

```powershell
python .\plot_timeline.py --input .\results\timeline_test\timeline.csv --output-dir .\results\timeline_test\plots
```

Primer za RMS periodic workload:

```powershell
python .\plot_timeline.py --input .\results\periodic_experiments\rms_memory_penalty_factor_0_5\timeline.csv --output-dir .\results\periodic_experiments\rms_memory_penalty_factor_0_5\plots
```

Timeline prikaz je posebno koristan za preemptive algoritme kao što su Round Robin, SRT, RMS i EDF, jer prikazuje stvarne intervale izvršavanja i prekide procesa.

## Workload fajlovi

Workload-i se nalaze u `data/` folderu.

Primer procesa:

```json
{
  "pid": "P1",
  "arrival_time": 0,
  "burst_time": 5,
  "deadline": 9,
  "memory_tier": "local_dram",
  "memory_intensity": 0.2
}
```

Polja:

- `pid`— identifikator procesa
- `arrival_time`— vreme dolaska procesa
- `burst_time`— osnovno vreme izvršavanja
- `deadline`— rok do kog proces treba da završi
- `memory_tier`— memorijski tier procesa
- `memory_intensity`— stepen osetljivosti procesa na memorijski penal

## Periodični workload fajlovi

Periodični workload se koristi za RMS algoritam.

Primer:

```json
{
  "simulation_time": 20,
  "tasks": [
    {
      "task_id": "T1",
      "period": 5,
      "execution_time": 1,
      "relative_deadline": 5,
      "memory_tier": "local_dram",
      "memory_intensity": 0.2
    }
  ]
}
```

Polja:

- `simulation_time` - do kog vremena se generišu instance periodičnih taskova
- `tasks` - lista periodičnih taskova
- `task_id` - identifikator periodičnog taska
- `period` - period ponavljanja
- `execution_time` - vreme izvršavanja svake instance
- `relative_deadline` - rok relativan u odnosu na arrival time instance
- `memory_tier` - memorijski tier taska
- `memory_intensity` - stepen osetljivosti na memorijski penal

## Eksperimentalni scenariji

Trenutno postoje sledeći scenariji:

`workload_basic.json`
Osnovni workload za poređenje algoritama.

`workload_spn_vs_hrrn.json`
Scenario koji pokazuje razliku između SPN i HRRN algoritama. SPN favorizuje kraće procese, dok HRRN daje prednost i procesima koji dugo čekaju.

`workload_remote_memory.json`
Scenario sa procesima koji imaju različite memorijske karakteristike. Koristi se za poređenje rezultata bez memorijskog penala i sa različitim vrednostima `memory_penalty_factor`.

`periodic_tasks_basic.json`  
Scenario sa periodičnim real-time taskovima. Koristi se za testiranje RMS algoritma i prikaz preemptive ponašanja periodičnih taskova kroz timeline/Gantt grafikon.

## Rezultati

Za svaki eksperiment generišu se CSV fajlovi:

```txt
metrics.csv
schedule.csv
timeline.csv
```

`metrics.csv` sadrži zbirne mere po algoritmu:

- algorithm_name
- average_waiting_time
- average_turnaround_time
- average_response_time
- deadline_miss_count
- deadline_miss_ratio

`schedule.csv` sadrži detaljne rezultate po procesu:

- algorithm_name
- pid
- arrival_time
- base_burst_time
- effective_burst_time
- deadline
- start_time
- completion_time
- turnaround_time
- waiting_time
- response_time
- deadline_missed
- memory_tier
- memory_intensity

`timeline.csv` sadrži stvarne segmente izvršavanja procesa i koristi se za Gantt/timeline prikaz:

- algorithm_name
- pid
- start_time
- end_time
- duration

## Ograničenja simulacije

Ovaj projekat je simulator, ne realni operativni sistem.

Trenutna ograničenja:

- ne meri stvarno vreme izvršavanja na hardveru
- ne modeluje cache ponašanje
- ne modeluje stvarnu NUMA politiku
- ne modeluje migraciju stranica memorije
- ne modeluje contention na memorijskom bandwidth-u
- ne implementira kernel scheduler
- koristi pojednostavljeni linearni memory penalty model

Zbog toga rezultate treba posmatrati kao analizu ponašanja algoritama pod kontrolisanim uslovima, a ne kao precizno merenje realnog sistema.

## Trenutni status

Implementirana je funkcionalna verzija projekta:

- algoritmi raspoređivanja: FCFS, Round Robin, SPN, SRT, HRRN, RMS i EDF
- JSON workload loader za obične procese
- JSON loader za periodične real-time taskove
- generator procesnih instanci iz periodičnih taskova
- izračunavanje real-time metrika
- memory penalty model za sporiji/udaljeni memorijski tier
- CSV export rezultata
- batch runner za obične eksperimente
- batch runner za periodične RMS eksperimente
- generisanje zbirnih grafikona
- generisanje timeline/Gantt prikaza
- početna analiza rezultata u `docs/analysis.md`

Planirana moguća proširenja:

- dodatni periodic workload scenariji
- automatski grafikoni za `combined_periodic_metrics.csv`
- grupisanje timeline prikaza po originalnom periodic task-u
- dodatna analiza rezultata u seminarskom radu
- Linux user-space eksperiment za merenje jitter-a
