<img src="assets/icon.svg" width="64" height="64" alt="">

# Cash Note

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

- 20 collection members selected by nominal GDP, with the euro area counted once and the United States selected by default.
- Fixed-in-view top bar and country panel, with an independently scrollable member list.
- Country search and shareable `?country=XX` links.
- Denomination, material, active year range, issue status, and orientation filters.
- Search portraits, landmarks, currencies, and series; sort by denomination or design introduction.
- Front/back shelf views and a modal with 100–400% zoom, pointer/touch pan, reset, and previous/next navigation.
- Responsive mobile country selector, native modal focus handling, Escape dismissal, reduced-motion support, and image error fallbacks.
- Per-note metadata, reference links, and original image URLs.

## Catalogue scope and sources

The 20 members follow the **IMF October 2026 nominal GDP projections**, as [tabulated by Visual Capitalist](https://www.visualcapitalist.com/the-128-trillion-global-economy-in-2026/). Walk down the country ranking, count the euro area once at Germany’s position, skip subsequent euro-area countries, and continue until there are 20 members. This adds Poland, Taiwan, Argentina and Israel. The euro area’s position is a browsing convention, not a separate calculation of aggregate GDP. There are 122 representative banknotes and 244 locally bundled images. The UK collection covers Bank of England notes, not the separate Scottish and Northern Irish issuers.

The [ECB lists 21 euro-area countries](https://www.ecb.europa.eu/euro/intro/html/index.en.html), including Bulgaria from January 2026. At the snapshot date none retains its former national currency as parallel legal tender. Bulgaria’s temporary lev/euro dual circulation ended on January 31, 2026. Exchangeability of old notes and voluntary acceptance by shops are distinct from legal-tender status. Member-country searches and old country links (such as `?country=DE`) resolve to the Euro area collection.

The additional collections use denomination and introduction-date references from [NBP](https://nbp.pl/banknoty-i-monety/banknoty-obiegowe/), [CBC](https://www.cbc.gov.tw/public/data/issue/money/a1/t02.html), [BCRA](https://www.bcra.gob.ar/billetes-y-monedas-en-vigencia/) and [Bank of Israel](https://www.boi.org.il/en/economic-roles/banknotes-and-coins/third-series-of-the-new-shekel-2014/). Their attributed scans are from Banknote Museum. `scripts/expand-members.py` adds these reviewed records without rebuilding the original catalogue.

This first edition curates **one representative current design per selected denomination**, not every still-valid historical series, signature, commemorative, or printing variety. It is a research snapshot dated **2026-11-03**, not a live register of legal tender. Active years refer to the illustrated design's introduction, not a specimen's printed series date. Range filtering uses interval overlap with introduction–2026. A note can remain valid while no longer being issued or while being withdrawn from circulation; those statuses are deliberately distinct.

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
