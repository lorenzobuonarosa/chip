#!/usr/bin/env python3
"""
prepare_data.py — Commercio mondiale di circuiti integrati (HS 8542), 2025.

Legge l'export UN Comtrade in data/ e genera data.json con TUTTI i flussi
bilaterali di importazione ("mirror data": origine = partner, destinazione =
Paese dichiarante). La selezione dei Paesi avviene poi nella pagina.

Uso:
    python3 prepare_data.py                       # usa il CSV predefinito
    python3 prepare_data.py data/altro_file.csv   # oppure un CSV specifico

Nessuna dipendenza esterna: solo la libreria standard di Python 3.8+.
Se i controlli finali non tornano, lo script esce con codice 1 e non scrive data.json.
"""

import csv
import json
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_CSV = ROOT / "data" / "comtrade_hs8542_2025.csv"
OUT = ROOT / "data.json"

YEAR = 2025
HS_CODE = "8542"

# Taiwan non dichiara a Comtrade: compare solo come partner "Other Asia, nes".
TAIWAN_COMTRADE = "S19"
TAIWAN_ISO = "TWN"

# Codici Comtrade che non sono Paesi (aree non specificate, zone franche...).
# Si tengono, per non perdere valore nel totale, ma con un nome esplicito.
NON_COUNTRY = {
    "E19": "Altri Paesi europei n.c.a.",
    "F19": "Altri Paesi africani n.c.a.",
    "O19": "Altri Paesi dell'Oceania n.c.a.",
    "A79": "Altri Paesi ALADI n.c.a.",
    "_X": "Aree non specificate",
    "X2": "Zone franche",
    "XX": "Categorie speciali",
}

# Nomi italiani (ISO 3166-1 alpha-3). Base: CLDR italiano, con alcune forme
# giornalistiche (Malesia, Hong Kong, Repubblica Ceca...).
NAMES_IT = {
    'TWN': 'Taiwan',
    'ABW': 'Aruba', 'AFG': 'Afghanistan', 'AGO': 'Angola', 'AIA': 'Anguilla',
    'ALB': 'Albania', 'AND': 'Andorra', 'ARE': 'Emirati Arabi Uniti', 'ARG': 'Argentina',
    'ARM': 'Armenia', 'ASM': 'Samoa Americane', 'ATA': 'Antartide', 'ATF': 'Terre Australi Francesi',
    'ATG': 'Antigua e Barbuda', 'AUS': 'Australia', 'AUT': 'Austria', 'AZE': 'Azerbaigian',
    'BDI': 'Burundi', 'BEL': 'Belgio', 'BEN': 'Benin', 'BES': 'Bonaire, Sint Eustatius e Saba',
    'BFA': 'Burkina Faso', 'BGD': 'Bangladesh', 'BGR': 'Bulgaria', 'BHR': 'Bahrein',
    'BHS': 'Bahamas', 'BIH': 'Bosnia ed Erzegovina', 'BLM': 'Saint-Barthélemy', 'BLR': 'Bielorussia',
    'BLZ': 'Belize', 'BMU': 'Bermuda', 'BOL': 'Bolivia', 'BRA': 'Brasile',
    'BRB': 'Barbados', 'BRN': 'Brunei', 'BTN': 'Bhutan', 'BVT': 'Isola Bouvet',
    'BWA': 'Botswana', 'CAF': 'Repubblica Centrafricana', 'CAN': 'Canada', 'CCK': 'Isole Cocos',
    'CHE': 'Svizzera', 'CHL': 'Cile', 'CHN': 'Cina', 'CIV': "Costa d'Avorio",
    'CMR': 'Camerun', 'COD': 'Rep. Dem. del Congo', 'COG': 'Congo', 'COK': 'Isole Cook',
    'COL': 'Colombia', 'COM': 'Comore', 'CPV': 'Capo Verde', 'CRI': 'Costa Rica',
    'CUB': 'Cuba', 'CUW': 'Curaçao', 'CXR': 'Isola Christmas', 'CYM': 'Isole Cayman',
    'CYP': 'Cipro', 'CZE': 'Repubblica Ceca', 'DEU': 'Germania', 'DJI': 'Gibuti',
    'DMA': 'Dominica', 'DNK': 'Danimarca', 'DOM': 'Repubblica Dominicana', 'DZA': 'Algeria',
    'ECU': 'Ecuador', 'EGY': 'Egitto', 'ERI': 'Eritrea', 'ESH': 'Sahara Occidentale',
    'ESP': 'Spagna', 'EST': 'Estonia', 'ETH': 'Etiopia', 'FIN': 'Finlandia',
    'FJI': 'Figi', 'FLK': 'Isole Falkland', 'FRA': 'Francia', 'FRO': 'Isole Faroe',
    'GAB': 'Gabon', 'GBR': 'Regno Unito', 'GEO': 'Georgia', 'GHA': 'Ghana',
    'GIB': 'Gibilterra', 'GIN': 'Guinea', 'GMB': 'Gambia', 'GNB': 'Guinea-Bissau',
    'GNQ': 'Guinea Equatoriale', 'GRC': 'Grecia', 'GRD': 'Grenada', 'GRL': 'Groenlandia',
    'GTM': 'Guatemala', 'GUM': 'Guam', 'GUY': 'Guyana', 'HKG': 'Hong Kong',
    'HMD': 'Isole Heard e McDonald', 'HND': 'Honduras', 'HRV': 'Croazia', 'HTI': 'Haiti',
    'HUN': 'Ungheria', 'IDN': 'Indonesia', 'IND': 'India', 'IOT': "Territorio britannico dell'Oceano Indiano",
    'IRL': 'Irlanda', 'IRN': 'Iran', 'IRQ': 'Iraq', 'ISL': 'Islanda',
    'ISR': 'Israele', 'ITA': 'Italia', 'JAM': 'Giamaica', 'JOR': 'Giordania',
    'JPN': 'Giappone', 'KAZ': 'Kazakistan', 'KEN': 'Kenya', 'KGZ': 'Kirghizistan',
    'KHM': 'Cambogia', 'KNA': 'Saint Kitts e Nevis', 'KOR': 'Corea del Sud', 'KWT': 'Kuwait',
    'LAO': 'Laos', 'LBN': 'Libano', 'LBR': 'Liberia', 'LBY': 'Libia',
    'LCA': 'Saint Lucia', 'LKA': 'Sri Lanka', 'LSO': 'Lesotho', 'LTU': 'Lituania',
    'LUX': 'Lussemburgo', 'LVA': 'Lettonia', 'MAC': 'Macao', 'MAR': 'Marocco',
    'MDA': 'Moldavia', 'MDG': 'Madagascar', 'MDV': 'Maldive', 'MEX': 'Messico',
    'MHL': 'Isole Marshall', 'MKD': 'Macedonia del Nord', 'MLI': 'Mali', 'MLT': 'Malta',
    'MMR': 'Myanmar', 'MNE': 'Montenegro', 'MNG': 'Mongolia', 'MNP': 'Isole Marianne Settentrionali',
    'MOZ': 'Mozambico', 'MRT': 'Mauritania', 'MSR': 'Montserrat', 'MUS': 'Mauritius',
    'MWI': 'Malawi', 'MYS': 'Malesia', 'NAM': 'Namibia', 'NCL': 'Nuova Caledonia',
    'NER': 'Niger', 'NGA': 'Nigeria', 'NIC': 'Nicaragua', 'NLD': 'Paesi Bassi',
    'NOR': 'Norvegia', 'NPL': 'Nepal', 'NRU': 'Nauru', 'NZL': 'Nuova Zelanda',
    'OMN': 'Oman', 'PAK': 'Pakistan', 'PAN': 'Panama', 'PCN': 'Isole Pitcairn',
    'PER': 'Perù', 'PHL': 'Filippine', 'PLW': 'Palau', 'PNG': 'Papua Nuova Guinea',
    'POL': 'Polonia', 'PRK': 'Corea del Nord', 'PRT': 'Portogallo', 'PRY': 'Paraguay',
    'PSE': 'Palestina', 'PYF': 'Polinesia Francese', 'QAT': 'Qatar', 'ROU': 'Romania',
    'RUS': 'Russia', 'RWA': 'Ruanda', 'SAU': 'Arabia Saudita', 'SDN': 'Sudan',
    'SEN': 'Senegal', 'SGP': 'Singapore', 'SHN': "Sant'Elena", 'SLB': 'Isole Salomone',
    'SLE': 'Sierra Leone', 'SLV': 'El Salvador', 'SMR': 'San Marino', 'SOM': 'Somalia',
    'SPM': 'Saint-Pierre e Miquelon', 'SRB': 'Serbia', 'SSD': 'Sud Sudan', 'STP': 'São Tomé e Príncipe',
    'SUR': 'Suriname', 'SVK': 'Slovacchia', 'SVN': 'Slovenia', 'SWE': 'Svezia',
    'SWZ': 'Eswatini', 'SXM': 'Sint Maarten', 'SYC': 'Seychelles', 'SYR': 'Siria',
    'TCA': 'Isole Turks e Caicos', 'TCD': 'Ciad', 'TGO': 'Togo', 'THA': 'Thailandia',
    'TJK': 'Tagikistan', 'TKL': 'Tokelau', 'TKM': 'Turkmenistan', 'TLS': 'Timor Est',
    'TON': 'Tonga', 'TTO': 'Trinidad e Tobago', 'TUN': 'Tunisia', 'TUR': 'Turchia',
    'TUV': 'Tuvalu', 'TZA': 'Tanzania', 'UGA': 'Uganda', 'UKR': 'Ucraina',
    'UMI': 'Isole minori degli Stati Uniti', 'URY': 'Uruguay', 'USA': 'Stati Uniti', 'UZB': 'Uzbekistan',
    'VAT': 'Città del Vaticano', 'VCT': 'Saint Vincent e Grenadine', 'VEN': 'Venezuela', 'VGB': 'Isole Vergini Britanniche',
    'VNM': 'Vietnam', 'VUT': 'Vanuatu', 'WLF': 'Wallis e Futuna', 'WSM': 'Samoa',
    'YEM': 'Yemen', 'ZAF': 'Sudafrica', 'ZMB': 'Zambia', 'ZWE': 'Zimbabwe',
}

# Controlli attesi (miliardi di dollari) e tolleranza.
EXPECTED = {
    "totale": 1202.0,
    "origine_top": ("TWN", 388.0),
    "importatore_top": ("CHN", 425.0),
    "flusso_top": (("TWN", "CHN"), 152.5),
}
TOLERANCE = 0.01  # ±1%


def iso(code: str) -> str:
    code = (code or "").strip()
    return TAIWAN_ISO if code == TAIWAN_COMTRADE else code


def name_it(code: str, fallback: str) -> str:
    if code in NAMES_IT:
        return NAMES_IT[code]
    if code in NON_COUNTRY:
        return NON_COUNTRY[code]
    print(f"  ! nome italiano mancante per {code} ({fallback}): uso il nome inglese")
    return fallback


def bn(v: float) -> str:
    return f"{v / 1e9:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")


def close(actual: float, expected: float) -> bool:
    return abs(actual - expected) <= expected * TOLERANCE


def main() -> int:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CSV
    print(f"Lettura di {src.relative_to(ROOT) if src.is_relative_to(ROOT) else src}")

    flows = defaultdict(float)          # (origine, destinazione) -> USD
    labels = {}                         # ISO -> nome originale Comtrade
    reporters = set()
    world_total = 0.0
    n_rows = n_import = 0

    # utf-8-sig rimuove il BOM iniziale
    with open(src, encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            n_rows += 1
            if row["flowDesc"] != "Import":
                continue
            if row.get("cmdCode", HS_CODE) != HS_CODE or str(row.get("refYear", YEAR)) != str(YEAR):
                continue
            n_import += 1
            value = float(row["primaryValue"] or 0)
            reporter = iso(row["reporterISO"])
            partner = iso(row["partnerISO"])
            reporters.add(reporter)
            labels[reporter] = row["reporterDesc"]
            if partner == "W00":            # totale "World": solo per controllo
                world_total += value
                continue
            labels[partner] = "Taiwan" if partner == TAIWAN_ISO else row["partnerDesc"]
            flows[(partner, reporter)] += value

    total = sum(flows.values())
    by_origin = defaultdict(float)
    by_dest = defaultdict(float)
    for (o, d), v in flows.items():
        by_origin[o] += v
        by_dest[d] += v

    countries = {}
    for code in sorted(set(by_origin) | set(by_dest)):
        countries[code] = {
            "name": name_it(code, labels.get(code, code)),
            "reporter": code in reporters,
            "aggregate": code in NON_COUNTRY,
            "export": round(by_origin.get(code, 0.0)),
            "import": round(by_dest.get(code, 0.0)),
        }

    flow_list = sorted(
        ([o, d, round(v)] for (o, d), v in flows.items() if v > 0),
        key=lambda f: -f[2],
    )

    # ------------------------------------------------------------- controlli
    top_o = max(by_origin.items(), key=lambda kv: kv[1])
    top_d = max(by_dest.items(), key=lambda kv: kv[1])
    top_f = max(flows.items(), key=lambda kv: kv[1])
    cn_cn = flows.get(("CHN", "CHN"), 0.0)

    print(f"Righe lette: {n_rows:,}  ·  righe Import: {n_import:,}".replace(",", "."))
    print(f"Flussi bilaterali: {len(flow_list):,}".replace(",", ".") + f"  ·  Paesi/aree: {len(countries)}"
          f"  ·  Paesi dichiaranti: {len(reporters)}")
    print("Controlli (miliardi di dollari):")
    checks = [
        ("Totale importazioni bilaterali", f"{bn(total)}", "≈ 1.202",
         close(total / 1e9, EXPECTED["totale"])),
        ("Primo Paese d'origine", f"{countries[top_o[0]]['name']} {bn(top_o[1])}", "Taiwan ≈ 388",
         top_o[0] == EXPECTED["origine_top"][0] and close(top_o[1] / 1e9, EXPECTED["origine_top"][1])),
        ("Primo importatore", f"{countries[top_d[0]]['name']} {bn(top_d[1])}", "Cina ≈ 425",
         top_d[0] == EXPECTED["importatore_top"][0] and close(top_d[1] / 1e9, EXPECTED["importatore_top"][1])),
        ("Flusso maggiore",
         f"{countries[top_f[0][0]]['name']} → {countries[top_f[0][1]]['name']} {bn(top_f[1])}",
         "Taiwan → Cina ≈ 152,5",
         top_f[0] == EXPECTED["flusso_top"][0] and close(top_f[1] / 1e9, EXPECTED["flusso_top"][1])),
    ]
    for label, got, exp, ok in checks:
        print(f"  [{'OK' if ok else 'ERRORE'}] {label}: {got}  (atteso {exp})")
    print(f"  [info] Somma righe 'World' dei dichiaranti: {bn(world_total)}"
          f"  (differenza dal bilaterale: {bn(abs(world_total - total))})")
    print(f"  [info] Flusso Cina → Cina (reimportazioni): {bn(cn_cn)}")
    print(f"  [info] Taiwan dichiarante: {'sì' if 'TWN' in reporters else 'no'}"
          f"  ·  Vietnam dichiarante: {'sì' if 'VNM' in reporters else 'no'}")

    if not all(ok for *_, ok in checks):
        print("\nI controlli non tornano: data.json NON è stato scritto.")
        return 1

    out = {
        "meta": {
            "title": "Importazioni di circuiti integrati per origine e destinazione",
            "source": "UN Comtrade",
            "source_url": "https://comtradeplus.un.org/TradeFlow",
            "hs_code": HS_CODE,
            "year": YEAR,
            "unit": "USD",
            "method": "mirror data: solo righe Import, origine = partner, destinazione = dichiarante",
            "generated": date.today().isoformat(),
            "total": round(total),
            "flow_fields": ["origin", "destination", "value_usd"],
        },
        "countries": countries,
        "flows": flow_list,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"\nScritto {OUT.name}: {OUT.stat().st_size / 1024:,.0f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
