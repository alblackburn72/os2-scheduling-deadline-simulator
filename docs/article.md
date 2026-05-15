# Scheduling Deadline Simulator: analiza CPU raspoređivanja kroz deadline-ove, real-time metrike i memorijski penal

## Uvod

U okviru ovog projekta implementiran je simulator CPU scheduling algoritama sa fokusom na real-time metrike, deadline-ove i ponašanje algoritama u različitim workload scenarijima.

Ideja projekta nije bila da se napravi realni kernel scheduler, već kontrolisano simulaciono okruženje u kome se mogu porediti različiti algoritmi raspoređivanja. Simulator omogućava da se za isti skup procesa pokrene više algoritama, izračunaju metrike, generišu CSV rezultati i prikažu grafikoni i timeline/Gantt dijagrami izvršavanja.

Poseban fokus je stavljen na pitanje:

> Da li algoritam koji ima dobre prosečne performanse zaista dobro radi i kada procesi imaju rokove?

Kod real-time sistema nije dovoljno da prosečno vreme čekanja bude malo. Važno je i da li proces uspeva da se završi pre svog deadline-a.

Zbog toga simulator računa metrike kao što su:

- prosečno vreme čekanja,
- prosečno turnaround vreme,
- prosečno vreme odziva,
- broj promašenih rokova,
- odnos promašenih rokova.

Pored toga, u projekat je dodat i pojednostavljen model sporijeg ili udaljenog memorijskog tier-a. Cilj tog modela je da se ispita kako povećanje efektivnog vremena izvršavanja memorijski intenzivnih procesa utiče na rezultate raspoređivanja.

## Motivacija

U klasičnim primerima scheduling algoritama često se posmatraju metrike kao što su waiting time, turnaround time i response time. One jesu korisne, ali nisu dovoljne kada govorimo o real-time sistemima.

Na primer, proces može relativno brzo dobiti CPU i imati dobar response time, ali ipak završiti posle svog deadline-a. U tom slučaju, iz perspektive real-time sistema, zadatak nije uspešno izvršen.

Zbog toga se u ovom projektu uvodi metrika `deadline_miss_ratio`, koja pokazuje koliki procenat procesa nije završen na vreme.

Ova metrika je posebno korisna za poređenje algoritama koji se na prvi pogled mogu ponašati dobro po prosečnim vrednostima, ali loše po pitanju rokova.

## Šta simulator radi?

Simulator omogućava da se definiše workload kroz JSON fajl, a zatim da se nad tim workload-om pokrenu različiti algoritmi raspoređivanja.

Za svaki algoritam generišu se:

- zbirne metrike,
- detaljni rezultati po procesu,
- timeline izvršavanja,
- grafikoni za poređenje algoritama.

Trenutno su podržani klasični workload-i sa procesima, kao i periodični real-time taskovi.

Kod klasičnih procesa svaki proces ima:

- `pid`,
- `arrival_time`,
- `burst_time`,
- `deadline`,
- `memory_tier`,
- `memory_intensity`.

Kod periodičnih taskova task se definiše kroz:

- `task_id`,
- `period`,
- `execution_time`,
- `relative_deadline`,
- `memory_tier`,
- `memory_intensity`.

Periodični taskovi se zatim pretvaraju u konkretne procesne instance. Na primer, task `T1` sa periodom 5 i vremenom simulacije 20 generiše instance:

```txt
T1_0 arrival=0
T1_1 arrival=5
T1_2 arrival=10
T1_3 arrival=15
```

Na taj način isti sistem može da podrži i obične procese i periodične real-time taskove.

## Implementirani algoritmi

U projektu su implementirani sledeći algoritmi:

- FCFS — First-Come, First-Served,
- Round Robin,
- SPN / SJF — Shortest Process Next / Shortest Job First,
- SRT — Shortest Remaining Time,
- HRRN — Highest Response Ratio Next,
- RMS — Rate Monotonic Scheduling,
- EDF — Earliest Deadline First.

Prvih pet algoritama se koriste za klasične procesne workload-e, dok su RMS i EDF posebno značajni za real-time i periodične taskove.

## FCFS

FCFS izvršava procese redosledom kojim stižu.

Njegova glavna prednost je jednostavnost. Međutim, mana je što dugačak proces može blokirati kraće procese koji stižu posle njega. U workload-ima sa deadline-ovima to može dovesti do toga da kraći i hitniji procesi zakasne, iako bi mogli biti brzo završeni.

Zbog toga FCFS često nije dobar izbor kada je poštovanje deadline-ova važno.

## Round Robin

Round Robin svakom procesu daje vremenski kvantum. Ako proces ne završi u tom vremenu, vraća se na kraj reda.

Ovaj algoritam često daje dobar response time, jer procesi relativno brzo dobijaju priliku da se izvršavaju. Međutim, dobar response time ne znači automatski i dobar deadline miss ratio.

Round Robin ne uzima u obzir deadline procesa, ukupno preostalo vreme izvršavanja, niti memorijski intenzitet. Zbog toga može brzo dati prvi odgovor procesu, ali ga završiti kasno.

## SPN / SJF

SPN bira najkraći dostupan proces.

Ovaj algoritam može smanjiti prosečno vreme čekanja, jer favorizuje kraće procese. Međutim, pošto nije preemptive, ne može da prekine proces koji je već počeo da se izvršava.

Ako dugačak proces krene prvi, kraći procesi koji stignu kasnije moraju da čekaju, što može biti loše za deadline-sensitive workload-e.

## SRT

SRT je preemptive verzija SPN algoritma.

U svakom trenutku bira proces sa najmanjim preostalim vremenom izvršavanja. Ako stigne novi proces koji ima kraće preostalo vreme od trenutno aktivnog procesa, aktivni proces može biti prekinut.

Zbog toga se SRT često ponaša bolje od SPN-a u workload-ima gde kraći procesi stižu nakon dužih procesa. U eksperimentima se SRT pokazuje kao jedan od stabilnijih algoritama po pitanju deadline ponašanja.

## HRRN

HRRN bira proces sa najvećim response ratio:

```txt
response_ratio = (waiting_time + burst_time) / burst_time
```

Ovim se smanjuje rizik od gladovanja procesa koji dugo čekaju.

Međutim, HRRN nije nužno najbolji izbor za deadline-sensitive workload-e. Algoritam može dati prednost procesu koji dugo čeka, iako postoji drugi proces sa strožim rokom.

Zbog toga je HRRN koristan za fairness, ali ne garantuje dobro ponašanje po pitanju deadline-ova.

## RMS

RMS, odnosno Rate Monotonic Scheduling, koristi se za periodične real-time taskove.

To je preemptive fixed-priority algoritam. Prioritet taska određuje se na osnovu periode:

```txt
kraći period = viši prioritet
```

Ako stigne instanca taska sa kraćom periodom, ona može prekinuti trenutno izvršavanje taska sa nižim prioritetom.

RMS je posebno koristan za prikaz ponašanja periodičnih real-time sistema, jer jasno pokazuje kako se prioriteti definišu unapred na osnovu karakteristika taskova.

## EDF

EDF, odnosno Earliest Deadline First, takođe je preemptive real-time scheduling algoritam, ali za razliku od RMS-a koristi dinamičke prioritete.

EDF u svakom trenutku bira dostupni proces ili task instancu sa najranijim apsolutnim deadline-om.

Pravilo je:

```txt
raniji deadline = viši prioritet
```

RMS i EDF su zanimljivi za poređenje jer predstavljaju dva različita pristupa real-time raspoređivanju:

- RMS koristi fixed-priority pristup,
- EDF koristi dynamic-priority pristup.

U jednostavnim workload-ima, posebno kada su relativni deadline-ovi jednaki periodama, RMS i EDF mogu dati isti raspored. To nije greška, već posledica workload-a. Razlika postaje vidljivija u scenarijima gde task sa dužom periodom ima kraći relativni deadline.

## Memory penalty model

Projekat ne simulira konkretan hardverski protokol niti stvarnu memorijsku arhitekturu.

Umesto toga, sporija ili udaljena memorija je modelovana parametarski. Procesi koji koriste sporiji memorijski tier dobijaju povećano efektivno vreme izvršavanja.

Koriste se dve vrednosti:

- `base_burst_time`,
- `effective_burst_time`.

`base_burst_time` predstavlja originalno vreme izvršavanja procesa iz workload fajla.

`effective_burst_time` predstavlja vreme izvršavanja koje scheduler stvarno koristi nakon primene memorijskog penala.

Formula je:

```txt
effective_burst_time = ceil(base_burst_time * (1 + memory_penalty_factor * memory_intensity))
```

Ako proces koristi lokalnu memoriju, penal se ne primenjuje.

Ako proces koristi udaljeni ili sporiji memorijski tier, njegovo efektivno vreme izvršavanja se povećava u zavisnosti od:

- `memory_penalty_factor`,
- `memory_intensity`.

Ovaj model je pojednostavljena heuristika. Njegova svrha nije precizno modelovanje hardvera, već kontrolisana analiza toga kako povećanje vremena izvršavanja utiče na scheduling metrike i deadline miss ratio.

Važno je da memorijski penal ne utiče samo na proces koji je penalizovan. Ako taj proces duže zauzima CPU, i ostali procesi mogu duže čekati. Zbog toga sporiji memorijski tier može indirektno pogoršati ponašanje celog workload-a.

## Eksperimentalni scenariji

U projektu je definisano više workload scenarija.

### Basic workload

`workload_basic.json` predstavlja osnovni scenario za poređenje algoritama.

U ovom workload-u prvi proces stiže prvi i ima duže vreme izvršavanja, dok kasniji procesi imaju kraće vreme izvršavanja i strože rokove.

Ovaj scenario pokazuje problem kod non-preemptive algoritama: ako dugačak proces krene prvi, kraći procesi moraju da čekaju, što može dovesti do promašivanja deadline-ova.

### SPN vs HRRN workload

`workload_spn_vs_hrrn.json` napravljen je da pokaže razliku između SPN i HRRN algoritama.

SPN favorizuje kraće procese, dok HRRN uzima u obzir i vreme čekanja procesa.

Ovaj scenario pokazuje da algoritam koji je dobar za fairness nije nužno najbolji za deadline-sensitive workload-e.

### Remote memory workload

`workload_remote_memory.json` koristi se za analizu memory penalty modela.

U ovom scenariju postoje procesi sa različitim memorijskim karakteristikama. Neki koriste lokalnu memoriju, dok su drugi označeni kao procesi koji koriste sporiji ili udaljeni memorijski tier.

Eksperimenti se pokreću sa različitim vrednostima `memory_penalty_factor`, kako bi se videlo kako rast efektivnog vremena izvršavanja utiče na rezultate.

### Periodic real-time workload

`periodic_tasks_basic.json` koristi se za RMS i EDF algoritme.

Cilj ovog scenarija je prikaz ponašanja periodičnih real-time taskova. Posebno se posmatra kako taskovi sa višim prioritetom prekidaju taskove sa nižim prioritetom.

Kod osnovnog periodic workload-a RMS i EDF mogu dati isti ili veoma sličan raspored, jer su relativni deadline-ovi jednaki periodama. Zbog toga je dodatno korisno imati poseban workload koji eksplicitno razdvaja ponašanje RMS i EDF algoritama.

## Rezultati

Simulator generiše rezultate u CSV fajlovima:

```txt
metrics.csv
schedule.csv
timeline.csv
```

`metrics.csv` sadrži zbirne metrike po algoritmu.

`schedule.csv` sadrži finalne rezultate po procesu.

`timeline.csv` sadrži stvarne segmente izvršavanja procesa i koristi se za Gantt/timeline prikaz.

Za zbirnu analizu koriste se:

```txt
combined_metrics.csv
combined_periodic_metrics.csv
```

Pored CSV rezultata, projekat generiše i grafikone koji olakšavaju poređenje algoritama.

Grafikoni uključuju:

- deadline miss ratio po algoritmu,
- average waiting time,
- average turnaround time,
- average response time,
- trend kroz različite vrednosti memorijskog penala,
- timeline/Gantt prikaz izvršavanja.

## Grafički prikaz rezultata

Na ovom mestu u WordPress članku ubacuju se slike generisane iz projekta.

### Slika 1 — Basic workload: deadline miss ratio

[UBACI SLIKU: `deadline_miss_basic.png`]

Ovaj grafikon prikazuje poređenje deadline miss ratio vrednosti za osnovni workload.

Poenta grafikona je da se pokaže da algoritmi sa sličnim prosečnim metrikama mogu imati različito ponašanje po pitanju deadline-ova.

### Slika 2 — SPN vs HRRN

[UBACI SLIKU: `deadline_miss_spn_vs_hrrn.png`]

Ovaj grafikon prikazuje scenario u kome SPN i HRRN donose različite odluke.

SPN favorizuje kraći proces, dok HRRN favorizuje proces koji je duže čekao. Zbog toga se može desiti da SPN bolje ispoštuje deadline-ove, dok HRRN bolje tretira fairness.

### Slika 3 — Memory penalty scenario

[UBACI SLIKU: `deadline_miss_memory_penalty_0_5.png`]

Ovaj grafikon prikazuje ponašanje algoritama kada je uključen memory penalty model.

Povećano efektivno vreme izvršavanja memorijski intenzivnih procesa može povećati broj promašenih rokova.

### Slika 4 — Memory penalty trend

[UBACI SLIKU: `memory_penalty_deadline_trend.png`]

Ovaj grafikon prikazuje trend deadline miss ratio vrednosti kroz različite vrednosti `memory_penalty_factor`.

Cilj je da se vidi kako povećavanje memorijskog penala utiče na različite algoritme.

### Slika 5 — RMS timeline prikaz

[UBACI SLIKU: `rms_timeline_memory_penalty_0_5.png`]

Timeline prikaz pokazuje stvarne intervale izvršavanja periodičnih taskova.

Kod RMS algoritma jasno se vidi da task sa nižim prioritetom može biti prekinut kada stigne instanca taska sa višim prioritetom.

## Timeline / Gantt prikaz

Timeline prikaz je dodat da bi se bolje objasnilo ponašanje preemptive algoritama.

Za svaki segment izvršavanja beleži se:

- `pid`,
- `start_time`,
- `end_time`,
- `duration`.

Ovo je posebno korisno za algoritme kao što su:

- Round Robin,
- SRT,
- RMS,
- EDF.

Kod ovih algoritama proces ne mora biti izvršen u jednom kontinuiranom bloku. Može početi, biti prekinut, pa nastaviti kasnije.

Zbirne metrike pokazuju rezultat, ali timeline pokazuje kako je do tog rezultata došlo.

## Analiza rezultata

Eksperimenti pokazuju nekoliko važnih stvari.

Prvo, prosečne metrike nisu dovoljne za real-time sisteme. Algoritam može imati dobar average waiting time ili response time, a ipak loš deadline miss ratio.

Drugo, Round Robin često daje dobar response time, ali ne garantuje poštovanje deadline-ova. To je zato što Round Robin ravnomerno deli CPU vreme, ali ne zna ništa o rokovima procesa.

Treće, SRT se često ponaša dobro u deadline-sensitive scenarijima, jer može prekinuti duži proces i završiti kraće procese ranije.

Četvrto, HRRN smanjuje rizik od gladovanja procesa, ali nije uvek najbolji za workload-e sa strožim rokovima.

Peto, memory penalty model pokazuje da povećanje efektivnog vremena izvršavanja jednog procesa može uticati i na druge procese. Ako penalizovani proces duže zauzima CPU, ostali procesi duže čekaju.

Šesto, RMS i EDF omogućavaju analizu periodičnih real-time taskova. RMS koristi fiksne prioritete na osnovu periode, dok EDF koristi dinamičke prioritete na osnovu najranijeg deadline-a.

## Ograničenja

Ovaj projekat je simulator, ne realni operativni sistem.

Trenutna ograničenja su:

- simulator ne meri stvarno vreme izvršavanja na hardveru,
- ne implementira kernel scheduler,
- ne modeluje cache ponašanje,
- ne modeluje stvarnu NUMA politiku,
- ne modeluje migraciju memorijskih stranica,
- ne modeluje contention na memorijskom bandwidth-u,
- memory penalty model je pojednostavljena linearna heuristika,
- rezultati zavise od izabranih workload scenarija.

Zbog toga rezultate treba posmatrati kao analizu trendova i relativnih razlika između algoritama, a ne kao precizno merenje realnog sistema.

## Zaključak

Projekat pokazuje da se ponašanje scheduling algoritama značajno razlikuje u zavisnosti od workload-a.

Algoritam koji ima dobre prosečne metrike ne mora imati dobar deadline miss ratio. Ovo je posebno važno u real-time sistemima, gde završavanje pre roka može biti važnije od prosečnih vrednosti.

Preemptive algoritmi kao što su SRT, RMS i EDF mogu bolje reagovati u scenarijima gde je potrebno brzo odgovoriti na dolazak novih zadataka ili taskova sa višim prioritetom.

Memory penalty model pokazuje da sporiji ili udaljeni memorijski tier može povećati efektivno vreme izvršavanja procesa i indirektno pogoršati deadline ponašanje celog workload-a.

Trenutna verzija simulatora predstavlja osnovu za dalje eksperimente, dodatne workload scenarije i detaljniju analizu real-time scheduling algoritama.

## Link ka projektu

[UBACI LINK KA GITHUB REPOZITORIJUMU]
