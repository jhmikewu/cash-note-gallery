<img src="assets/icon.svg" width="64" height="64" alt="">

# Cash Note

Each shelf item groups one currency and denomination, showing its newest matching design. Open an item to browse its variants using the left thumbnail rail. Filters apply before grouping, so historical or material searches show only matching variants. Detail navigation moves between denominations; selecting a variant resets its zoom and displays that design’s dates and sources.

A responsive banknote gallery with a wooden shelf presentation, country browsing, and an interactive front/back inspection view.

## Run locally

Requires Node.js 18+ (Node.js 22 recommended).

```sh
npm ci
npm run dev
```

```sh
npm test
npm run build
npm run preview
```

The static production site is generated in `dist/`. Vite uses relative asset paths, so it can be hosted under a repository subdirectory as well as a domain root. No backend, account, or API key is required.

## Features

- 22 sidebar entries: 19 countries, the euro area counted once, and Hong Kong SAR and Macau SAR of China. The United States is selected by default.
- Fixed-in-view top bar and country panel, with an independently scrollable member list.
- Country search and shareable `?country=XX` links.
- Denomination, material, active year range, issue status, and orientation filters.
- Search portraits, landmarks, currencies, and series; sort by denomination or design introduction.
- Front/back shelf views and a modal with 100–400% zoom, pointer/touch pan, reset, and previous/next navigation.
- Responsive mobile country selector, native modal focus handling, Escape dismissal, reduced-motion support, and image error fallbacks.
- Per-note metadata, reference links, and original image URLs.

## Catalogue scope and sources

The 20 members follow the **IMF October 2026 nominal GDP projections**, as [tabulated by Visual Capitalist](https://www.visualcapitalist.com/the-128-trillion-global-economy-in-2026/), with collection scope adjustments. Count the euro area once at Germany’s position, skip subsequent euro-area countries, exclude Taiwan from this catalogue, and continue until there are 20 members. The additional members are Poland, Argentina, Israel and Sweden. The euro area’s position is a browsing convention, not a separate calculation of aggregate GDP. There are 278 curated banknotes and 556 locally bundled images. The UK collection covers Bank of England notes, not the separate Scottish and Northern Irish issuers.

Hong Kong SAR, China (HKD), and Macau SAR, China (MOP) are separate sidebar entries beside China (CNY), bringing the list to 22 entries: 19 countries, one euro area, and two SARs. Direct links use `?country=HK` and `?country=MO`; earlier `?country=CN&region=HK` or `region=MO` links still open the appropriate SAR. Hong Kong includes all three authorised banks’ 2003, 2010 and 2018 series plus government paper/polymer $10 notes; Macau includes current BOC/BNU designs and their preceding major series. Older ordinary issues remain to be added. Sources: [HKMA](https://www.hkma.gov.hk/eng/key-functions/money/hong-kong-currency/notes/), [AMCM](https://www.amcm.gov.mo/en/currency/currency-in-circulation-in-macao/banknotes/new-series), and [Sveriges Riksbank](https://www.riksbank.se/en-gb/payments--cash/notes--coins/notes/valid-banknotes/). `scripts/add-sar-collections.py` maintains these additions and removes the excluded TWD records.

The [ECB lists 21 euro-area countries](https://www.ecb.europa.eu/euro/intro/html/index.en.html), including Bulgaria from January 2026. At the snapshot date none retains its former national currency as parallel legal tender. Bulgaria’s temporary lev/euro dual circulation ended on January 31, 2026. Exchangeability of old notes and voluntary acceptance by shops are distinct from legal-tender status. Member-country searches and old country links (such as `?country=DE`) resolve to the Euro area collection.

The additional collections use denomination and introduction-date references from [NBP](https://nbp.pl/banknoty-i-monety/banknoty-obiegowe/), [CBC](https://www.cbc.gov.tw/public/data/issue/money/a1/t02.html), [BCRA](https://www.bcra.gob.ar/billetes-y-monedas-en-vigencia/) and [Bank of Israel](https://www.boi.org.il/en/economic-roles/banknotes-and-coins/third-series-of-the-new-shekel-2014/). Their attributed scans are from Banknote Museum. `scripts/expand-members.py` adds these reviewed records without rebuilding the original catalogue.

The catalogue includes current designs and researched historical variants whose circulation overlaps **1 January 2000 through 3 November 2026**, inclusive. Coverage is curated and still expanding, not a complete inventory of every qualifying design. Signature and serial-number changes are not separate variants. Introduction dates describe the design, not a specimen's printed date. `circulationStart` and `circulationEnd` use ISO dates when known, or a year when that is the available precision. A null end records no established withdrawal date. Year filters overlap the recorded circulation interval; withdrawal and redemption deadlines are separate. `Withdrawn` means circulation has ended, while `Not issued` records an older design that remains valid.

The first [ordinary-series expansion](docs/ordinary-series-expansion.md) adds 77 designs through `scripts/add-ordinary-series.py` and its checked-in reviewed manifest.

Historical additions are maintained by `scripts/add-historical-variants.py` (UK), `scripts/add-world-variants.py` (reviewed Wikipedia research rows), and `scripts/add-commonwealth-variants.py` (issuer/museum sources). They preserve existing IDs. See [reproduction research](docs/reproduction-research.md) for image-rule checks and unresolved restrictions. Required SPECIMEN marks are retained; source availability is not treated as blanket permission for unmarked use.

`src/notes.json` contains catalogue metadata and source URLs. Primary sources include the US Currency Education Program, ECB, Bank of England, Bank of Japan, Bank of Canada, Reserve Bank of Australia, RBI, Banco Central do Brasil, Bank of Korea, Banco de México, Bank Indonesia, Bank of Russia, and Swiss National Bank. Wikipedia reference tables and Banknote Museum supplement image and design metadata. Original currency artwork and third-party scans retain their respective rights; no blanket image license is implied. Source-provided specimen markings are preserved. Some reference images limit the detail available at high zoom.

`scripts/research.py` and `scripts/build-catalog.py` document the initial research process. They require the Python Beautiful Soup HTML parser and Requests library in an isolated environment. They are maintenance aids, not build dependencies; running the builder replaces the curated JSON and requires a subsequent manual review and image-cache pass. `scripts/cache-images.py` downloads reference images, verifies their file signatures, and records their original URLs. `scripts/cache-thumbnails.py` provides a display-size Wikimedia fallback when original downloads are throttled. Run `node scripts/verify-images.mjs` to verify the local cache. The checked-in catalogue is the source of truth for normal builds.

## Structure

- `src/main.jsx`: gallery, filters, country navigation, and note viewer.
- `src/style.css`: responsive shelf design.
- `src/catalog.js`: country ranking, formatting, and filter logic.
- `src/notes.json`: curated note records and image provenance.
- `public/notes/`: cached reference images.
- `tests/catalog.test.js`: catalogue coverage and filter behavior.
- `.github/workflows/check.yml`: build and tests on pushes and pull requests.

Created in [T3 Code](https://t3.codes).

The [Indonesia ordinary-series batch](docs/indonesia-series-expansion.md) adds 19 earlier designs, including the complete 2016 series and the 1999 polymer Rp100,000.
