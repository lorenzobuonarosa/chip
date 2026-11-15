# Taiwan vende, la Cina compra

Sankey interattivo del commercio mondiale di **circuiti integrati** (codice HS 8542) nel 2025, per la sezione Radar di Quotidiano Nazionale. A sinistra il Paese d'origine («Chi vende»), a destra il Paese che importa («Chi compra»).

**URL pubblico (GitHub Pages):** https://lorenzobuonarosa.github.io/chip/

## Contenuto del repository

| File | A cosa serve |
|---|---|
| `index.html` | La pagina del grafico: HTML, CSS e JS in un unico file. D3 v7 e d3-sankey da jsDelivr, font Inter da Google Fonts. |
| `data.json` | Tutti i flussi bilaterali (6.724), generato da `prepare_data.py`. |
| `prepare_data.py` | Legge il CSV di Comtrade, costruisce i flussi e stampa i controlli. Usa solo la libreria standard di Python. |
| `data/comtrade_hs8542_2025.csv` | Export originale di UN Comtrade. |
| `embed-example.html` | Pagina di prova con lo snippet iframe: auto-resize e cambio di tema. |
| `.nojekyll` | Dice a GitHub Pages di servire i file così come sono, senza Jekyll. |

## Fonte

UN Comtrade, codice HS 8542 (Electronic integrated circuits), anno 2025, flussi annuali: https://comtradeplus.un.org/TradeFlow

## Metodo

1. **Dati mirror.** Si usano solo le righe `flowDesc = Import`. Ogni riga diventa un flusso dal partner (Paese d'origine) al dichiarante (Paese che compra). Le righe con partner `W00` (World) sono totali e vengono escluse. Il metodo serve perché **Taiwan non dichiara a Comtrade**: compare solo come partner, con il codice `S19` «Other Asia, nes», che qui diventa `TWN` «Taiwan».
2. **Taiwan e Vietnam** non risultano tra i Paesi dichiaranti per il 2025, quindi compaiono solo a sinistra, come Paesi che vendono.
3. **Hong Kong** fa soprattutto da porto di transito verso la Cina continentale. L'interruttore «Unisci Hong Kong alla Cina» somma i due territori, e allora i flussi tra Cina e Hong Kong diventano flussi interni («Cina e Hong Kong» → «Cina e Hong Kong»).
4. **Cina → Cina** (57,0 miliardi): chip cinesi reimportati, per esempio dopo il confezionamento all'estero o il passaggio nelle zone franche. È visibile di default e si può nascondere con un interruttore. Se Hong Kong è unita alla Cina, l'interruttore nasconde tutto il flusso interno (153,0 miliardi).
5. Alcuni codici partner di Comtrade non sono Paesi («Areas, nes», «Free Zones», «Other Europe, nes»…). Restano nei dati con un nome italiano esplicito, per non perdere valore: in tutto valgono circa 0,25 miliardi.
6. I valori sono in dollari correnti (`primaryValue`), mostrati in miliardi con un decimale. Le percentuali si calcolano sul totale delle importazioni bilaterali con le impostazioni correnti (1.202,5 miliardi di default).
7. I flussi sotto la soglia (default 1 miliardo) non entrano nel grafico; il loro valore è indicato sotto il grafico. I Paesi non selezionati confluiscono in «Altri Paesi». La soglia si applica dopo l'aggregazione, quindi un flusso verso «Altri Paesi» resta visibile se nel complesso supera la soglia.

## Parametri URL

Tutti facoltativi; la pagina li aggiorna da sola quando si cambiano i filtri, quindi per preparare una vista filtrata basta aprire il grafico su GitHub Pages, scegliere i filtri e copiare l'indirizzo dalla barra del browser.

| Parametro | Valori | Effetto |
|---|---|---|
| `theme` | `light`, `dark` | Forza il tema. Ha la precedenza su postMessage e sul tema di sistema. |
| `bg` | `solid`, `transparent` | Sfondo in tema scuro: `#121212` (default) o trasparente. |
| `da` | codici ISO3 separati da virgola | Paesi di partenza (es. `TWN,KOR,CHN`). Taiwan è `TWN`. |
| `a` | codici ISO3 separati da virgola | Paesi di arrivo (es. `CHN,HKG,USA`). |
| `soglia` | numero da 0 a 10 | Soglia minima in miliardi (es. `2.5`). |
| `altri` | `0` | Nasconde «Altri Paesi»: restano solo gli scambi tra i Paesi scelti. |
| `hk` | `1` | Unisce Hong Kong alla Cina. |
| `cc` | `0` | Nasconde il flusso Cina → Cina. |

Esempi:

- `https://lorenzobuonarosa.github.io/chip/?da=TWN,KOR&a=CHN,USA`
- `https://lorenzobuonarosa.github.io/chip/?da=TWN,KOR,JPN,USA&a=CHN,HKG&altri=0&theme=dark`
- `https://lorenzobuonarosa.github.io/chip/?hk=1&cc=0&soglia=2`

Senza `da` e `a` la pagina mostra i primi 10 Paesi per lato (8 sotto i 600 px di larghezza).

**Un solo Paese.** Se su un lato è scelto un solo Paese (per esempio `?a=ITA`), quel lato mostra solo quel Paese, senza «Altri Paesi», e la soglia non si applica, così si vedono anche i flussi piccoli. Se l'altro lato non è stato scelto a mano, mostra i primi 10 partner di quel Paese (8 su mobile), più «Altri Paesi». Esempi: `?a=ITA` (da chi compra l'Italia), `?da=ITA` (a chi vende l'Italia), `?da=ITA&a=DEU` (un solo flusso).

## Tema

Ordine di decisione:

1. parametro `?theme=light|dark` nell'URL;
2. messaggio dalla pagina ospite: `iframe.contentWindow.postMessage({ type: "theme", value: "light" | "dark" }, "*")`; facoltativi `value: "auto"` per tornare al tema di sistema e `background: "transparent" | "solid"`;
3. `prefers-color-scheme` del sistema, ascoltato in tempo reale.

Tutti i colori sono variabili CSS in cima a `index.html` (`:root` per il chiaro, `:root[data-theme="dark"]` per lo scuro).

## Messaggi verso la pagina ospite

L'iframe invia alla pagina che lo contiene:

- `{ source: "qn-radar-chip", type: "ready" }` all'avvio, così l'ospite può rispondere con il tema;
- `{ source: "qn-radar-chip", type: "resize", height: <px> }` a ogni cambio di altezza (anche quando si aprono i filtri o il pannello di un Paese).

## Snippet da incollare nel CMS

```html
<iframe
  id="qn-chip-sankey"
  src="https://lorenzobuonarosa.github.io/chip/"
  title="Taiwan vende, la Cina compra: importazioni di circuiti integrati nel 2025"
  style="width:100%;height:760px;border:0;display:block;"
  scrolling="no"
  loading="lazy"></iframe>
<script>
(function () {
  var iframe = document.getElementById('qn-chip-sankey');
  var ORIGIN = 'https://lorenzobuonarosa.github.io';

  function siteTheme() {
    // ADATTARE: come il sito di QN sa se è in tema scuro
    return document.documentElement.classList.contains('dark') ? 'dark' : 'light';
  }
  function sendTheme() {
    if (iframe.contentWindow) {
      iframe.contentWindow.postMessage({ type: 'theme', value: siteTheme() }, ORIGIN);
    }
  }
  window.addEventListener('message', function (e) {
    if (e.source !== iframe.contentWindow || e.origin !== ORIGIN) return;
    var d = e.data || {};
    if (d.type === 'resize' && d.height) iframe.style.height = d.height + 'px';
    if (d.type === 'ready') sendTheme();
  });
  iframe.addEventListener('load', sendTheme);
  // Da chiamare quando il lettore cambia tema sul sito:
  window.qnChipSetTheme = sendTheme;
})();
</script>
```

Quando il sito cambia tema basta chiamare `window.qnChipSetTheme()`, oppure inviare direttamente:

```js
document.getElementById('qn-chip-sankey').contentWindow
  .postMessage({ type: 'theme', value: 'dark' }, 'https://lorenzobuonarosa.github.io');
```

Se nella stessa pagina ci sono più grafici, dare a ogni iframe un `id` diverso e duplicare lo script cambiando l'`id`.

## Aggiornare i dati

1. Scaricare da [Comtrade TradeFlow](https://comtradeplus.un.org/TradeFlow) l'export annuale con HS 8542, tutti i dichiaranti, tutti i partner, flussi Import ed Export, in CSV.
2. Salvarlo in `data/` (per esempio sostituendo `data/comtrade_hs8542_2025.csv`).
3. Lanciare:

   ```bash
   python3 prepare_data.py
   ```

   Oppure, con un altro file:

   ```bash
   python3 prepare_data.py data/nuovo_file.csv
   ```

4. Leggere i controlli stampati. Se uno risulta `ERRORE`, lo script **non** scrive `data.json`. Per un anno diverso vanno aggiornati `YEAR` e i valori in `EXPECTED` dentro `prepare_data.py`, oltre a titolo, sottotitolo, fonte e nota in `index.html`.
5. Fare commit e push di `data.json` e del CSV: GitHub Pages si aggiorna in un paio di minuti.

Per provare in locale serve un piccolo server, perché `fetch('data.json')` non funziona aprendo il file direttamente:

```bash
python3 -m http.server 8000
```

Poi aprire http://localhost:8000/ oppure http://localhost:8000/embed-example.html.

## Pubblicazione con GitHub Pages

1. Portare i file sul branch `main` (merge del branch di lavoro, per esempio con una pull request).
2. Su GitHub aprire il repository `lorenzobuonarosa/chip` → **Settings** → **Pages**.
3. In **Build and deployment** → **Source** scegliere **Deploy from a branch**.
4. In **Branch** scegliere `main` e la cartella `/ (root)`, poi **Save**.
5. Attendere 1-2 minuti: in alto nella stessa pagina compare «Your site is live at https://lorenzobuonarosa.github.io/chip/».
6. Verificare l'URL, poi incollare lo snippet nel CMS.

Nota: con un account GitHub gratuito, Pages funziona solo se il repository è pubblico.
