# Szczęśliwe numerki – ZS Nr 1 Gorlice

Strona zbierająca szczęśliwe numerki z https://www.lukasiewicz.gorlice.pl.
Szkoła pokazuje tylko jeden dzień i nie ma archiwum, więc historia budowana jest od
momentu uruchomienia – nie da się pobrać starszych numerków wstecz.

## Co jest w środku

- `index.html` – strona (zakładki: **Ten tydzień**, **Statystyki**, **Szukaj numerka**)
- `scrape.py` – pobiera numerki ze strony szkoły i dopisuje do `data/numerki.json`
- `data/numerki.json` – zebrana historia (na start: 25.11.2026 → 2 i 24)
- `.github/workflows/scrape.yml` – uruchamia scraper automatycznie co 3 godziny

## Uruchomienie (za darmo, GitHub)

1. Załóż repozytorium na GitHubie i wgraj wszystkie pliki z tego folderu.
2. **Settings → Pages** → Source: *Deploy from a branch* → branch `main`, folder `/ (root)`.
3. **Settings → Actions → General → Workflow permissions** → *Read and write permissions*.
4. Zakładka **Actions** → „Pobierz szczęśliwe numerki” → **Run workflow** (pierwszy test ręczny).

Strona będzie pod adresem `https://TWOJ-LOGIN.github.io/NAZWA-REPO/`.
Częstotliwość zmienisz w `scrape.yml` (linia `cron`, czas UTC).

## Podgląd lokalny

    python3 -m http.server
    # otwórz http://localhost:8000

## Uwagi

- Zakres numerków (do statystyki „najrzadziej”) ustawiasz na stronie, domyślnie 1–35.
- Jeśli szkoła zmieni układ strony, scraper zakończy się błędem (workflow zrobi się czerwony)
  i nic nie nadpisze – wtedy trzeba poprawić funkcję `parse()` w `scrape.py`.
