# Analiza rezultata

Ovaj dokument sadrži kratku interpretaciju prvih rezultata dobijenih pomoću simulatora. Cilj beleženje glavnih zaključaka iz eksperimenata dok su rezultati još sveži.

## 1. Basic workload

`workload_basic.json` predstavlja jednostavan scenario sa 3 procesa:

- `P1` stiže prvi i ima najduže vreme izvršavanja.
- `P2` i `P3` stižu kasnije, ali imaju kraće vreme izvršavanja i strože rokove.

Ovaj scenario pokazuje problem kod neprekidnih algoritama raspoređivanja kao što su FCFS, SPN i HRRN. Pošto su `P1` stiže prvi, algoritmi koji ne mogu da prekinu proces moraju da ga izvrše do koraja. Zbog toga kraći procesi čekaju predugo i mogu da promaše svoje rokove.

Najvažnije iz ovog workload-a je da prosečno vreme čekanja nije dovoljno za procenu ponašanja sistema sa rokovima. Algoritam može imati prihvatljive prosečne metrike, ali i dalje može imati visok deadline miss ratio.

U ovom scenariju SRT se ponaša bolje od ostalih algoritama jer može da prekine duži proces kada stigne kraći proces sa manjim preostalim vremenom izvršavanja. Zbog toga smanjuje broj promašenih rokova u odnosu FCFS, SPN i HRRN.

## 2. SPN vs HRRN workload

`workload_spn_vs_hrrn.json` služi da pokaže razliku između SPN i HRRN algoritama.

SPN bira proces sa najkraćim vremenom izvršavanja među dostupnim procesima. HRRN, sa druge strane, uzima u obzir i vreme čekanja procesa kroz response ratio:

```txt
response_ratio = (waiting_time + burst_time) / burst_time
```

SPN bira kraći proces sa strožijim rokom. HRRN bira proces koji je duže čekao. Zbog toga SPN smanjuje broj promašenih rokova, dok HRRN daje prednost procesu koji je duže čekao, ali time može zakasniti sa izvršavanjem procesa koji ima stroži rok.

HRRN smanjuje rizik od gladovanja procesa koji dugo čekaju, ali nije nužno najbolji izbor za deadline-sensitive workload-e.

Ovaj scenario dobro pokazuje da algoritam koji je dobar za fairness nije nužno najbolji za real-time okruženje.

## 3. Round Robin i response time

Round Robin u više scenarija pokazuje nizak average response time, jer brzo daje CPU vreme različitim procesima.

Međutim, dobar response time ne znači i dobar deadline miss ratio.

Round Robin ravnomerno deli CPU vreme, ali ne uzima u obzir:

- deadline procesa,
- ukupno preostalo vreme izvršavanja,
- memorijski intenzitet,
- prioritet procesa.

Zbog toga može brzo dati prvi odgovor procesu, ali ga završiti kasno. Ovo je posebno važno za real-time sisteme, gde nije dovoljno da proces samo "krene brzo", bitno je da završi pre svog roka.

Round Robin daje bolju odzivnost, ali ne garantuje ispunjenje rokova.

## 4. Memory penalty scenario

`workload_remote_memory.json` uvodi procese sa različitim memorijskim karakteristikama. Neki procesi koriste lokalnu memoriju - `dram`, dok su drugi označeni kao procesi koji koriste sporiji ili udaljeni memorijski tier - `remote`.

U eksperimentima se porede rezultati bez memorijskog penala i rezultati sa različitim vrednostima `memory_penalty_factor`.

Model koristi 2 vrednosti:

```txt
base_burst_time
effective_burst_time
```

`base_burst_time` predstavlja originalno vreme izvršavanja procesa iz workload fajla.

`effective_burst_time` predstavlja vreme izvršavanja nakon primene memorijskog penala. Scheduler koristi upravo ovu vrednost.

Formula je:

```txt
effecitve_burst_time = ceil(base_burst_time * (1 + memory_penalty_factor * memory_intensity))
```

Kada je memory penalty isključen, base_burst_time i effective_burst_time su isti.

Kada je memory penalty uključen, procesi koji koriste sporiji/udaljeni memorijski tier dobijaju veće efektivno vreme izvršavanja. To povećava ukupno trajanje workload-a i može dovesti do većeg broja promašenih rokova.

Važan zaključak je da penalizovnai proces ne utiče samo na sebe. Ako duže zauzima CPU, onda i ostali procesi čekaju duže. Zbog toga memorijski penal može indirektno pogoršati deadline ponašanje i procesa koji sami ne koriste sporiji memorijski tier.

## 5. Ponašanje algoritama pod memory penalty modelom

U memory penalty eksperimentima vidi se povećanje `memory_penalty_factor` uglavnom pogoršava mere kao što su:

- average waiting time,
- average turnaround time,
- deadline miss ratio.

Međutim, efekat nije isti za sve algoritme.

SPN i SRT često ostaju relativno stablini zato što favorizuju kraće procese ili procese sa kraćim preostalim vremenom. Time mogu da završe kraće zadatke ranije, čak i kada neki procesi postanu sporiji zbog memorijskog penala.

HRRN može imati dobre rezultate kada memory penalty nije uključen, ali se njegovo ponašanje može pogoršati kada proces koji je dugo čekao ima povećano efektivno vreme izvršavanja. U tom slučaju HRRN može izabrati proces koji je postao skuplji za izvršavanje što kasnije odlaže druge procese.

Round Robin zadržava dobar response time, ali i dalje može imati loš deadline miss ratio, jer ne razlikuje procese po roku ili po efektivnom vremenu izvršavanja.

## 6. Periodični taskovi i RMS

Pored klasičnih procesa, simulator podržava i periodične real-time taskove.

Periodični task se ne pojavljuje samo jednom, već se ponavlja u pravilnim vremenskim intervalima. Na primer, task `T1` sa periodom `5` i vremenom simulacije `20` generiše sledeće procesne instance:

```txt
T1_0 arrival=0
T1_1 arrival=5
T1_2 arrival=10
T1_3 arrival=15
```

Ove instance se zatim raspoređuju pomoću RMS algoritma.

RMS, odnosno Rate Monotonic Scheduling, je preemptive fixed-priority algoritam. Prioritet taska zavisi od njegove periode:
`kraći period = viši prioritet`

To znači da task sa kraćom periodom može da prekine izvršavanje taska sa dužom periodom.

U trenutnom periodic workload-u postoje 3 taska:

```txt
T1: period = 5,  execution_time = 1
T2: period = 10, execution_time = 3
T3: period = 20, execution_time = 5
```

Prioriteti su zato:
`T1 > T2 > T3`

U timeline prikazu se vidi da `T3_0`, kao task sa najnižim prioritetom, može biti prekinut više puta kada stignu instance `T1` ili `T2`.

Ovo pokazuje glavnu razliku između RMS-a i običnih neprekidnih algoritama: RMS je namenjen periodičnim real-time zadacima i može da reaguje na dolazak novih instanci taskova višeg prioriteta.

## 7. Timeline / Gantt prikaz

Simulator sada čuva i stvarne segmente izvršavanja procesa kroz `timeline.csv`.

Ovo je posebno važno za preemptive algoritme kao što su:

- Round Robin,
- SRT,
- RMS.

Kod neprekidnih algoritama proces se uglavnom izvršava u jednom kontinuiranom bloku. Međutim, kod preemptive algoritama proces može biti prekinut i nastavljen kasnije.

Na primer, kod SRT algoritma jedan proces može imati:

```txt
P1: 0-1
P1: 7-14
```

To znači da je proces počeo da se izvršava, zatim je bio prekinut, pa je nastavljen kasnije.

Slično tome, kod RMS algoritma niže-prioritetni periodic task može biti prekinut kada stigne nova instanca taska sa kraćom periodom.

Timeline/Gantt prikaz je koristan zato što objašnjava zašto algoritmi imaju određene metrike. CSV metrike pokazuju rezultat, dok timeline pokazuje redosled izvršavanja koji je doveo do tog rezultata.

## 8. Najstabilniji algoritmi u dosadašnjim eksperimentima

Na osnovu trenutnih scenarija, SRT se pokazuje kao jedan od najstabilnijih algoritama u pogledu deadline ponašanja.

Razlog je to što SRT u svakom trenutku bira proces sa najmanjim preostalim vremenom izvršavanja. To mu omogućava da brzo završi kraće procese i smanji prosečno vreme čekanja i turnaround time.

SPN takođe može dati dobre rezultate, ali pošto je non-preemptive algoritam, može imati problem ako dugačak proces počne pre nego što stignu kraći ili hitniji procesi.

HRRN je koristan za fairness i smanjuje gladovanja, ali nije uvek najbolji za deadline-sensitive scenarije.

Round Robin je koristna za odzivnost, ali ne i za garantovanje rokova.

FCFS je najjednostavniji, ali često najosetljiviji na problem dugog procesa koji izgladnjuje ostale.

## 9. Ograničenja trenutne analize

Trenutni simulator koristi pojednostavljen model izvršavanja procesa. Rezultate treba posmatrati kao analizu ponašanja algoritama pod kontrolisanim uslovima, a ne kao precizno merenje realnog operativnog sistema.

Glavna ograničenja su:

- simulator ne meri stvarno vreme izvršavanja na hardveru,
- ne modeluje cache ponašanje,
- ne modeluje stvarnu NUMA politiku,
- ne modeluje migraciju memorijskih stranica,
- ne modeluje contention na memorijskom bandwidth-u,
- ne implementira kernel scheduler,
- memory penalty model je linearna heuristika,
- periodic task model trenutno koristi jednostavno generisanje instanci do zadatog `simulation_time`,
- RMS eksperimenti trenutno nisu automatski uključeni u glavni `run_experiments.py`.

Zbog toga je cilj simulatora da pokaže trendove i relativne razlike između algoritama, a ne da predvidi tačne performanse realnog sistema.

## 10. Zaključci trenutne verzije

Trenutna verzija simulatora pokazuje nekoliko važnih stvari:

1. Algoritmi sa dobrim prosečnim merama ne moraju imati dobar deadline miss ratio.
2. Round Robin daje dobar response time, ali ne garantuje završavanje pre roka.
3. SRT često poboljšava deadline ponašanje jer može da prekine duže procese.
4. SPN može biti dobar za kratke procese, ali može loše reagovati ako dugačak proces počne prvi.
5. HRRN poboljšava fairness, ali nije uvek najbolji za deadline-sensitive procese.
6. Sporiji/udaljeni memorijski tier može povećati efektivno vreme izvršavanja procesa.
7. Memorijski penal može indirektno pogoršati i procese koji sami nisu penalizovani, jer duže čekaju na CPU.
8. RMS omogućava analizu periodičnih real-time taskova.
9. Kod RMS-a taskovi sa kraćom periodom imaju viši prioritet i mogu da prekinu taskove sa dužom periodom.
10. Timeline/Gantt prikaz je koristan za razumevanje preemptive algoritama, jer prikazuje stvarne intervale izvršavanja i prekide procesa.

Ovi zaključci predstavljaju osnovu za dalji seminarski rad i za proširenje simulatora dodatnim periodic workload scenarijima.
