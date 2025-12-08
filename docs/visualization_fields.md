# Wizualizacja danych na mapie

---

## 1. Ogólna idea

Mapa ma pokazywać różne typy danych przestrzennych:

- **pogoda i jakość powietrza**
- **kolejki do lekarzy NFZ**
- później też np. **rowery**, **korki**, **siłownie**, **paliwa**, itd.

Każda warstwa na mapie:
- ma swój **kolor lub ikonę**
- po kliknięciu pokazuje **popup** z najważniejszymi informacjami
- można ją włączyć/wyłączyć w razie potrzeby

---

## 2. Jakość powietrza i pogoda


### Co pokazujemy:

- temperatura, wilgotność, ciśnienie
- **jakość powietrza**:
    - **PM2.5** (pył zawieszony w powietrzu, wielkość cząstek: do 2,5 mikrometra),
    - **PM10** (pył zawieszony w powietrzu, wielkość cząstek: do 10 mikrometrów),
    - **AQI** (Air Quality Index – czyli ogólny indeks jakości powietrza) skala 1-5:
        - 5 🟢 bardzo dobra 
        - 4 🟢 dobra 
        - 3 🟡 umiarkowana 
        - 2 🟠 zła 
        - 1 🔴 bardzo zła


Popup przykładowo:

```
Śródmieście
Temperatura: 13°C

Jakość powietrza: DOBRA
PM2.5: 18 µg/m³
PM10: 24 µg/m³
```

**Ikony:**
- pogoda np. słoneczko
- smog np. chmurka XD

---

## 3. Lekarze i kolejki (NFZ)

- jaka specjalizacja (np. kardiolog)
- średni czas oczekiwania
- liczba placówek w pobliżu

W popupie:

```
Kardiolog - Warszawa
Średni czas oczekiwania: 47 dni
Najkrótszy czas: 12 dni
Placówki w okolicy: 8
```

**Kolory:**

- **zielony** → krótko (do 2 tygodni)
- **żółty** → średnio (2–8 tygodni)
- **czerwony** → długo (powyżej 8 tygodni)

Ikona:
- np. krzyż medyczny

---

## 4. Warstwy, przełączanie, interakcja

Użytkownik może włączać/wyłączać warstwy:

- Pogoda / jakość powietrza
- Lekarze
- w przyszłości: rowery, korki, siłownie itp.

Każda warstwa ma własną ikonę i kolor, żeby łatwo było ogarnąć, co jest czym.

Kliknięcie w ikonę → popup z informacjami.

---

## 5. Co z nowymi kategoriami danych? (np. siłownie)

Ma to być **uniwersalne**.

Założenie:
> każda nowa kategoria danych dostarcza razem z danymi także **zamysł wizualizacji** np. podpowiedziany przez LLM.

Czyli np. „siłownie” mogłyby pokazywać:

- nazwę siłowni
- godziny otwarcia

Ikona: 💪 albo hantel  
Kolor: np. w zależności od obłożenia

```
🟢 mało ludzi
🟡 średnio
🔴 tłok
```

- provider mówi, jakie dane pokazać (pola do popupu itp.),
- frontend ma jedną uniwersalną ikonkę (pineska/kółko),
- kolor jest automatycznie dobierany do kategorii tak, żeby się nie dublował. 
- (albo może po zadaniu pytania niech LLM od razu podpowiada np kolor i ikonę (?))
---



## 6. Podsumowanie

- Mapa pokazuje różne typy danych (pogoda, jakość powietrza, lekarze, itd.)
- Każdy typ ma:
  - swój kolor
  - własną ikonę
  - kluczowe informacje w popupie

- Dla jakości powietrza:
  - ważna jest **interpretacja** (dobra/zła) a nie same liczby
  - kolory: zielony → czerwony

- Dla lekarzy:
  - kolory wg czasu oczekiwania

- Można włączyć/wyłączyć warstwy

- Jeśli pojawią się nowe kategorie (np. siłownie), to też:
  - dostają własny kolor/ikonę
  - pokazują tylko **najważniejsze dane**
  - informacje te dostarczane w providerze - jest to jeszcze do zrobienia