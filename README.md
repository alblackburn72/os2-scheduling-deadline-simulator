# Scheduling Deadline Simulator

Ovaj projekat predstavlja simulator za poređenje uobičajenih CPU algoritama za raspoređivanje na osnovu real-time mera performansi.

Glavni cilj je analiza kako se različiti algoritmi raspoređivanja ponašaju kada zadaci imaju rokove i koliko često maše iste pod uticajem sporijeg/udaljenog memorijskog tier-a.

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

- FCFS
- Round Robin
- SPN / SJF
- SRT
- HRRN

## Memory penalty model

Projekat ne simulira konkretan hardverski protokol niti stvarnu memorijsku arhitekturu. Sporija ili udaljena memorija je modelovana parametarski, kroz povećanje efektivnog vremena izvršavanja procesa.

- `base_burst_time` - originalno vreme izvršavanja iz workload fajla
- `effective_burst_time` - vreme izvršavanja koje scheduler stvarno korisit nakon primene memorijskog penala

Formula koja se koristi je:

```txt
  effective_burst_time = ceil(base_burst_time * (1 + memory_penalty_factor * memory_intensity))
```

Gde je:

- memory_penalty_factor - parametar koji određuje koliko je sporiji memorijski tier skuplji u simulaciji
- memory_intensity - koliko je proces osetljiv na memorijske pristupe

Ako je proces u lokalnoj memoriji (DRAM), penal se ne primenjuje.

Svrha modela je da omogući kontrolisanu analizu uticaja sporije memorije na scheduling mere i deadline miss ratio.

## Struktura projekta

```txt
os2-scheduling-deadline-simulator/
│
├── data/
│ ├── workload_basic.json
│ ├── workload_spn_vs_hrrn.json
│ └── workload_remote_memory.json
│
├── scheduler/
│ ├── algorithms/
│ │ ├── fcfs.py
│ │ ├── hrrn.py
│ │ ├── rr.py
│ │ ├── spn.py
│ │ └── srt.py
│ │
│ ├── csv_exporter.py
│ ├── memory_penalty.py
│ ├── metrics.py
│ ├── models.py
│ └── workload_loader.py
│
├── main.py
├── run_experiments.py
├── plot_results.py
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

## Pokretanje svih eksperimenata:

Svi predefinisani eksperimenti se mogu pokrenuti komandom:
`python .\run_experiments.py`

Ova skripta pokreće više scenarija i generiše rezultate u folderu:
`results/experiments/`

Glavni zbirni fajl:
`results/experiments/combined_metrics.csv`

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

## Eksperimentalni scenariji

Trenutno postoje sledeći scenariji:

`workload_basic.json`
Osnovni workload za poređenje algoritama.

`workload_spn_vs_hrrn.json`
Scenario koji pokazuje razliku između SPN i HRRN algoritama. SPN favorizuje kraće procese, dok HRRN daje prednost i procesima koji dugo čekaju.

`workload_remote_memory.json`
Scenario sa procesima koji imaju različite memorijske karakteristike. Koristi se za poređenje rezultata bez memorijskog penala i sa različitim vrednostima `memory_penalty_factor`.

## Rezultati

Za svaki eksperiment generišu se 2 CSV fajla:
`metrics.csv
schedule.csv`

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

Implementirana je prva funkcionalna verzija projekta:

- algoritmi raspoređivanja
- JSON workload loader
- izračunavanje metrika
- memory penalty model
- CSV export
- batch runner za eksperimente
- generisanje grafikona

Planirana moguća proširenja:

- RMS algoritam za periodične real-time zadatke
- generisanje Gantt/timeline prikaza
- dodatni workload scenariji
- bolja analiza rezultata u posebnom dokumentu
- Linux user-space eksperiment za merenje jitter-a
