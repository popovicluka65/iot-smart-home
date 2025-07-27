# IoT Project – Group 1, Team 4

## Team Members

- **SV4/2021** Luka Popović  
- **SV5/2021** Matija Popović

---

## 🚀 Installation and Running the Application

### 1. Clone the Repository

```bash
git clone git@github.com:kzi-nastava/iot-2024-group-1-team-4.git
```

---

### 2. Start Docker Infrastructure

Open a terminal and run:

```bash
cd ./infrastructure
docker-compose up
```

---

### 3. Set Up and Run the Backend Server

Open a **new terminal** and run:

```bash
python -m venv venv
venv\Scripts\activate      # On Windows
pip install -r requirements.txt
cd ./server
python ./server.py
```

---

### 4. Run the RPI Simulators

Open **three new terminal windows**, and run each of the following commands separately:

```bash
python ./RPI1.py
```

```bash
python ./RPI2.py
```

```bash
python ./RPI3.py
```

---

### 5. Run the Frontend (Angular App)

Open a **new terminal** and run:

```bash
cd ./front
ng serve
```

Then open the following link in your browser:

👉 [http://127.0.0.1:4200/](http://127.0.0.1:4200/)



# Standardni projekat

Projektni zadatak ima za cilj implementaciju uređaja pametne kuće. 

---

## Sistem pametne kuće

Sadrži tri Raspberry PI uređaja, koji su povezani sa različitim senzorima i aktuatorima. Spisak senzora i aktuatora dat je u tabeli:

| PI   | Kod    | Naziv                               |
|------|--------|-------------------------------------|
| PI1  | DS1    | Door Sensor (Button)               |
|      | DL     | Door Light (LED diode)             |
|      | DUS1   | Door Ultrasonic Sensor             |
|      | DB     | Door Buzzer                        |
|      | DPIR1  | Door Motion Sensor                 |
|      | DMS    | Door Membrane Switch               |
|      | RPIR1, RPIR2 | Room PIR                     |
|      | RDH1, RDHT2  | Room DHT                     |
| PI2  | DS2    | Door sensor (Button)              |
|      | DUS2   | Door Ultrasonic Sensor             |
|      | DPIR2  | Door Motion Sensor                 |
|      | GDHT   | Garage DHT                         |
|      | GLCD   | Garage LCD                         |
|      | GSG    | Gun Safe Gyro (Gyroscope)          |
|      | RPIR3  | Room PIR                           |
|      | RDHT3  | Room DHT                           |
| PI3  | RPIR4  | Room PIR                           |
|      | RDHT4  | Room DHT                           |
|      | BB     | Bedroom buzzer                     |
|      | B4SD   | Bedroom 4 Digit 7 Segment Display  |
|      | BIR    | Bedroom Infrared                   |
|      | BRGB   | Bedroom RGB                        |

---

## Kontrolna tačka 1

Za prvu kontrolnu tačku, potrebno je:

- Implementirati skriptu koja se pokreće na uređaju **PI1**.
- Omogućiti konfiguraciju skripte, tako da se bilo koji uređaj može, a ne mora simulirati.
- Ulazne podatke sa svakog senzora potrebno je ispisati u konzoli.
- Omogućiti upravljanje aktuatorima sa Raspberry PI uređaja kroz konzolnu aplikaciju.

---

## Kontrolna tačka 2

Za drugu kontrolnu tačku, potrebno je:

- Proširiti skriptu sa KT1.
- Dodati konfiguraciju skripte koja sadrži:
  - na kojem PI-u radi,
  - ime uređaja (možete dodati još informacija).
- Proširiti logiku sa slanjem izmjerenih/simuliranih vrijednosti **MQTT protokolom** na određeni **topic**:
  - topic može biti konfigurabilan ili zakucan za svaki tip senzora,
  - prilikom slanja specificirati tag da li je vrijednost simulirana ili nije.
- Slanje izmjerenih vrijednosti treba da se vrši u **batch-evima putem daemon niti** (ili procesa).
  - može biti jedna nit za sve senzore,
  - ili više niti po tipu senzora.
- Skripta ne smije ući u deadlock, a zaključavanja mutex-ima moraju biti minimalna.
- Implementirati server (npr. **Flask**) koji će:
  - preuzimati poruke iz MQTT broker-a,
  - čuvati ih u **InfluxDB** bazi podataka.
- Vizualizacija podataka pomoću **Grafana** alata:
  - svaki tip senzora ima svoj panel za prikaz.

---

## Odbrana projekta

Potrebno je:

- Implementirati skripte koje se pokreću na **sva tri PI uređaja**.
- Omogućiti konfiguraciju skripti, tako da se bilo koji uređaj (PI, senzor, aktuator) može simulirati.
- Implementirati serversku aplikaciju koja:
  - prima podatke putem MQTT,
  - skladišti ih u InfluxDB,
  - omogućava vizualizaciju u Grafani.
- **Implementirati logiku na osnovu ulaza senzora:**

### ALARM
- Predstavlja stanje uzbune u objektu.
- Tokom ovog stanja, potrebno je da **DB** i **BB** budu uključeni.
- Događaje ulaska i izlaska u ovo stanje čuvati u bazi i prikazati u Grafani, kao i obavijestiti korisnika putem Web aplikacije.
- Iz ovog stanja izlazi se unosom **PIN-a** na **DMS-u** ili putem Web aplikacije.

### Logika senzora:
1. Kada **DPIR1** detektuje pokret, uključiti **DL1** na 10 sekundi.
2. Kada **DPIR1** detektuje pokret, na osnovu distance sa **DUS1** u prethodnih par sekundi ustanoviti da li osoba ulazi ili izlazi iz objekta.
   - Isto važi za **DPIR2** i **DUS2**.
   - Čuvati brojno stanje osoba u objektu.
3. Ukoliko se detektuje signal sa **DS1** ili **DS2** na duže od 5 sekundi, uključiti ALARM dok se stanje DS-a ne promijeni.
4. Omogućiti aktivaciju sigurnosnog alarma putem **DMS** komponente.
   - Kada se unese četvorocifreni PIN kod, sistem se nakon 10 sekundi aktivira.
   - Ukoliko je sistem aktivan, nakon signala na **DS1** ili **DS2**, uključiti ALARM ukoliko se ne detektuje ispravan PIN na DMS.
   - Unosom PIN-a ALARM se isključuje i sistem se deaktivira.
5. Ukoliko je brojno stanje osoba jednako nuli, a detektovan je pokret na **RPIR1-4**, uključuje se ALARM.
6. Ukoliko **GSG** detektuje značajan pomeraj, uključiti ALARM.
7. Prikazati temperaturu i vlažnost vazduha sa **GDHT** na **GLCD-u**.
8. Prikazati trenutno vreme na **B4SD-u**.
9. Omogućiti podešavanja budilnika:
    - Putem Web aplikacije podesiti vreme za buđenje.
    - Kada je budilnik aktivan, aktivirati **BB** dok se budilnik ne isključi.
    - Tokom rada budilnika, prikaz na **B4SD** treperi na 0.5s.
    - Budilnik se gasi putem Web aplikacije.
    - Bonus: implementirati melodiju za buđenje.
10. Omogućiti uključivanje, isključivanje i upravljanje bojama **BRGB** sijalice putem daljinskog i **BIR** senzora, kao i putem Web aplikacije.
