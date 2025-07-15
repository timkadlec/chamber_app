# chamber_app

**Interní webová aplikace pro správu studentů a orchestrálních projektů.**  
Aplikace slouží pro evidenci skladeb, hráčů a nástrojového obsazení v rámci školních orchestrálních a komorních projektů. Umožňuje snadné přiřazování studentů na základě jejich nástrojového zaměření a konkrétní struktury skladeb.

## Použité technologie

- **Python 3.11**
- **Flask** (webový framework)
- **SQLAlchemy** (ORM)
- **Jinja2** (šablonovací systém)
- **SQLite** (výchozí databáze, snadno nahraditelná PostgreSQL)
- **Tailwind CSS** (frontend)
- **Bootstrap Icons**

## Funkce aplikace

- Přehledná evidence studentů, jejich nástrojů a studijních programů.
- Evidence skladeb včetně konkrétního nástrojového obsazení.
- Možnost vytvoření konkrétního souboru (ansámblu) na základě skladby.
- Výběr a přiřazení konkrétních hráčů (studentů) na jednotlivé pozice.
- Filtrace skladeb podle nástrojového obsazení.
- Uživatelské rozhraní přístupné přes běžný webový prohlížeč.
- Backend navržen jako REST architektura.

## Spuštění aplikace (lokální vývoj)

1. Klonování repozitáře:
   ```
   git clone https://github.com/timkadlec/chamber_app.git
   cd chamber_app
   ```

2. Vytvoření a aktivace virtuálního prostředí:
   ```
   python -m venv venv
   source venv/bin/activate
   ```

3. Instalace závislostí:
   ```
   pip install -r requirements.txt
   ```

4. Spuštění vývojového serveru:
   ```
   flask --app chamber_app run
   ```

5. Aplikace je dostupná na:
   ```
   http://127.0.0.1:5000
   ```

## Ukázky systému

Aplikace je ve fázi aktivního vývoje.  
Ukázkové snímky obrazovek budou přidány později.

## Licence

MIT License
