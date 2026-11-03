import React, { useState, useEffect, useRef } from "react";
import { createRoot } from "react-dom/client";
import {
  Globe2,
  Search,
  SlidersHorizontal,
  ArrowUpRight,
  X,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  ArrowLeftRight,
  ChevronLeft,
  ChevronRight,
  Library,
  Info,
  Maximize,
  Menu,
} from "lucide-react";
import {
  countries,
  euroMembers,
  resolveCountry,
  matchesCountry,
  collectionFor,
  defaults,
  filterNotes,
  denomination,
  rankingSource,
} from "./catalog";
import notes from "./notes.json";
import "./style.css";

function NoteImage({ note, side = "front", ...props }) {
  const [failed, setFailed] = useState(false);
  useEffect(() => setFailed(false), [note.id, side]);
  return failed || !note[side] ? (
    <div className="image-missing">
      <strong>{denomination(note)}</strong>
      <span>Image unavailable</span>
      <small>See the issuing bank in note details.</small>
    </div>
  ) : (
    <img
      src={note[side]}
      alt={`${denomination(note)} ${side}: ${side === "front" ? note.title : note.reverseTitle}`}
      onError={() => setFailed(true)}
      {...props}
    />
  );
}
function Modal({ children, onClose, label, className = "" }) {
  const ref = useRef(null);
  useEffect(() => {
    const old = document.activeElement;
    ref.current.showModal();
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = "";
      old?.focus();
    };
  }, []);
  return (
    <dialog
      ref={ref}
      aria-label={label}
      className={className}
      onCancel={onClose}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      {children}
    </dialog>
  );
}
function Viewer({ note, onClose, onNavigate }) {
  const [side, setSide] = useState("front"),
    [zoom, setZoom] = useState(1),
    [pan, setPan] = useState({ x: 0, y: 0 });
  const drag = useRef(null);
  useEffect(() => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
    setSide("front");
  }, [note.id]);
  const changeZoom = (z) => {
    setZoom(Math.max(1, Math.min(4, z)));
    setPan({ x: 0, y: 0 });
  };
  return (
    <Modal
      onClose={onClose}
      label={`${denomination(note)} detail view`}
      className="viewer"
    >
      <div className="viewer-top">
        <span>
          <Library size={19} /> The collection / {note.currency}
        </span>
        <button
          className="icon-button"
          onClick={onClose}
          aria-label="Close note"
        >
          <X />
        </button>
      </div>
      <div className="viewer-body">
        <div className="view-workspace">
          <div className="side-tabs">
            <button
              className={side === "front" ? "selected" : ""}
              onClick={() => {
                setSide("front");
                changeZoom(1);
              }}
            >
              Front
            </button>
            <button
              className={side === "back" ? "selected" : ""}
              onClick={() => {
                setSide("back");
                changeZoom(1);
              }}
            >
              Back
            </button>
          </div>
          <div
            className="zoom-stage"
            onPointerDown={(e) => {
              if (zoom > 1) {
                drag.current = { x: e.clientX - pan.x, y: e.clientY - pan.y };
                e.currentTarget.setPointerCapture(e.pointerId);
              }
            }}
            onPointerMove={(e) => {
              if (drag.current)
                setPan({
                  x: e.clientX - drag.current.x,
                  y: e.clientY - drag.current.y,
                });
            }}
            onPointerUp={() => (drag.current = null)}
            onPointerCancel={() => (drag.current = null)}
          >
            <div
              className={`zoom-image ${(side === "back" ? note.backOrientation || note.orientation : note.orientation) === "Vertical" ? "vertical" : ""}`}
              style={{
                transform: `translate(${pan.x}px,${pan.y}px) scale(${zoom})`,
              }}
            >
              <NoteImage note={note} side={side} draggable="false" />
            </div>
          </div>
          <div className="zoom-tools">
            <button
              aria-label="Zoom out"
              disabled={zoom === 1}
              onClick={() => changeZoom(zoom - 0.5)}
            >
              <ZoomOut size={18} />
            </button>
            <span>{Math.round(zoom * 100)}%</span>
            <button
              aria-label="Zoom in"
              disabled={zoom === 4}
              onClick={() => changeZoom(zoom + 0.5)}
            >
              <ZoomIn size={18} />
            </button>
            <i />
            <button aria-label="Reset zoom" onClick={() => changeZoom(1)}>
              <Maximize size={18} />
            </button>
            <button
              aria-label="Flip note"
              onClick={() => setSide(side === "front" ? "back" : "front")}
            >
              <ArrowLeftRight size={18} />
            </button>
          </div>
          <p className="zoom-hint">
            {zoom > 1
              ? "Drag the note to explore its details."
              : "Zoom in to discover the finer details."}
          </p>
        </div>
        <aside className="note-details">
          <span className="currency-label">{note.currency} banknote</span>
          <h2>{denomination(note)}</h2>
          <h3>{side === "front" ? note.title : note.reverseTitle}</h3>
          <span
            className={`status ${note.status === "Issued" ? "" : "secondary"}`}
          >
            <b /> {note.status === "Issued" ? "In circulation" : note.status}
          </span>
          <dl>
            <div>
              <dt>Series</dt>
              <dd>{note.series}</dd>
            </div>
            <div>
              <dt>Active years</dt>
              <dd>{note.year} – present</dd>
            </div>
            <div>
              <dt>Material</dt>
              <dd>{note.material}</dd>
            </div>
            <div>
              <dt>Dimensions</dt>
              <dd>{note.dimensions} mm</dd>
            </div>
            <div>
              <dt>Orientation</dt>
              <dd>
                {side === "back"
                  ? note.backOrientation || note.orientation
                  : note.orientation}
              </dd>
            </div>
          </dl>
          <p>{note.description}</p>
          <a href={note.source} target="_blank" rel="noreferrer">
            Issuing bank / reference <ArrowUpRight size={16} />
          </a>
          {note.imageSource && (
            <a href={note.imageSource} target="_blank" rel="noreferrer">
              Image attribution <ArrowUpRight size={16} />
            </a>
          )}
        </aside>
      </div>
      <div className="viewer-bottom">
        <button onClick={() => onNavigate(-1)}>
          <ChevronLeft size={17} /> Previous note
        </button>
        <span>Educational collection</span>
        <button onClick={() => onNavigate(1)}>
          Next note <ChevronRight size={17} />
        </button>
      </div>
    </Modal>
  );
}
function About({ onClose }) {
  return (
    <Modal onClose={onClose} label="About the collection" className="about">
      <button
        className="icon-button close-about"
        aria-label="Close collection notes"
        onClick={onClose}
      >
        <X />
      </button>
      <Globe2 size={32} />
      <h2>A world in your hands.</h2>
      <p>
        Small pieces of paper. Extraordinary stories. Cash Note brings the
        everyday art of currency into one collection.
      </p>
      <h3>What’s on the shelves</h3>
      <p>
        19 countries and the euro area selected from the IMF October 2026
        nominal GDP ranking, counting the euro area once at its first country’s
        position and continuing down the ranking to fill the remaining places.
        This first collection features a representative current design for each
        denomination, rather than every signature, printing or older valid
        series. UK coverage is Bank of England notes.
      </p>
      <p>
        Hong Kong SAR, China and Macau SAR, China are two additional entries,
        bringing the list to 22 members. China uses CNY, Hong Kong uses HKD and
        Macau uses MOP. SAR banknotes use one representative issuer per
        denomination: Bank of China, plus Hong Kong’s government-issued $10.
        Other authorised issuers’ designs also circulate. Taiwan is outside this
        catalogue’s scope; Sweden fills the twentieth member position.
      </p>
      <h3>One euro-area collection</h3>
      <p>
        The euro area includes {Object.values(euroMembers).join(", ")}. These 21
        countries use the euro as their national currency. As of November 3,
        2026, none also uses its former national currency as parallel legal
        tender. Bulgaria’s temporary euro/lev cash circulation ended on January
        31, 2026. Exchangeable old notes and voluntary shop acceptance of
        foreign currency do not make a currency legal tender.
      </p>
      <a
        href="https://www.ecb.europa.eu/euro/intro/html/index.en.html"
        target="_blank"
        rel="noreferrer"
      >
        Euro-area membership & currencies <ArrowUpRight size={16} />
      </a>
      <p>
        “Active years” means the illustrated design’s introduction through
        today, not the date printed on an individual note. Year filters find
        designs active during any part of your chosen range. Notes marked “Not
        issued” or “Withdrawing” can still be legal tender.
      </p>
      <h3>Sources & imagery</h3>
      <p>
        Each note links to its issuing bank or reference and its image source.
        Images are educational reference reproductions; currency artwork remains
        subject to its issuer’s reproduction rules. Some source images are low
        resolution, and zoom cannot recover detail absent from the original.
      </p>
      <a href={rankingSource} target="_blank" rel="noreferrer">
        View the GDP ranking <ArrowUpRight size={16} />
      </a>
      <p className="muted">
        Catalogue researched November 3, 2026. This is a curated snapshot, not a
        live legal-tender register.
      </p>
    </Modal>
  );
}
function App() {
  const [f, setF] = useState(() => {
      const p = new URLSearchParams(location.search);
      return {
        ...defaults,
        country: resolveCountry(
          p.get("country") === "CN" && ["HK", "MO"].includes(p.get("region"))
            ? p.get("region")
            : p.get("country"),
        ),
      };
    }),
    [countrySearch, setCountrySearch] = useState(""),
    [side, setSide] = useState("front"),
    [selected, setSelected] = useState(null),
    [about, setAbout] = useState(false),
    [mobile, setMobile] = useState(false),
    [expanded, setExpanded] = useState(false);
  const country = countries.find((c) => c.id === f.country),
    collection = collectionFor(f.country, f.region),
    filtered = filterNotes(notes, f),
    available = notes.filter((n) => n.currency === collection.currency);
  const update = (k, v) => setF((p) => ({ ...p, [k]: v }));
  const selectCountry = (id) => {
    setF({ ...defaults, country: id });
    setMobile(false);
    const u = new URL(location);
    u.searchParams.set("country", id);
    u.searchParams.delete("region");
    history.replaceState(null, "", u);
    window.scrollTo({ top: 0 });
  };
  const active = Object.keys(defaults).filter(
    (k) => !["country", "region", "sort"].includes(k) && f[k] !== defaults[k],
  ).length;
  return (
    <>
      <header className="topbar">
        <a className="brand" href="./">
          <span className="brand-icon">
            <Library size={24} />
          </span>
          cash note<span className="brand-dot">.</span>
        </a>
        <nav>
          <span className="nav-active">The collection</span>
          <button onClick={() => setAbout(true)}>
            About the project <ArrowUpRight size={15} />
          </button>
        </nav>
        <span className="header-note">
          <Globe2 size={17} /> One world. Many stories.
        </span>
      </header>
      <div className="app-layout">
        <aside className={`country-sidebar ${mobile ? "mobile-open" : ""}`}>
          <div className="sidebar-title">
            <h2>Explore members</h2>
            <span>{countries.length}</span>
            <button
              className="mobile-close icon-button"
              onClick={() => setMobile(false)}
              aria-label="Close countries"
            >
              <X size={18} />
            </button>
          </div>
          <label className="country-search">
            <Search size={16} />
            <input
              aria-label="Find a country"
              placeholder="Find a country…"
              value={countrySearch}
              onChange={(e) => setCountrySearch(e.target.value)}
            />
          </label>
          <div className="country-list">
            {countries
              .filter((c) => matchesCountry(c, countrySearch))
              .map((c) => (
                <button
                  key={c.id}
                  className={`country-button ${c.id === f.country ? "current" : ""}`}
                  onClick={() => selectCountry(c.id)}
                >
                  <span className="flag">{c.flag}</span>
                  <span>{c.name}</span>
                  <small>{c.currency}</small>
                </button>
              ))}
            {!countries.some((c) => matchesCountry(c, countrySearch)) && (
              <p className="no-countries">No members found.</p>
            )}
          </div>
          <div className="sidebar-foot">
            <Globe2 size={18} />
            <p>
              19 countries · Euro area · 2 SARs
              <button onClick={() => setAbout(true)}>
                How we curate <ArrowUpRight size={13} />
              </button>
            </p>
          </div>
        </aside>
        <main>
          <section className="intro">
            <div>
              <span className="intro-label">The banknote collection</span>
              <h1>A world in your hands.</h1>
              <p>
                Discover the art, history, and identity in everyday currency.
              </p>
            </div>
            <div className="collection-stamp">
              <Globe2 size={28} />
              <span>
                {countries.length} members
                <br />
                <b>Countless stories</b>
              </span>
            </div>
          </section>
          <section className="country-heading">
            <div className="country-identity">
              <span className="large-flag">{country.flag}</span>
              <div>
                <h2>{country.name}</h2>
                <p>
                  {collection.currencyName} <span>{collection.currency}</span>
                </p>
              </div>
            </div>
            <div className="country-heading-right">
              <span className="status">
                <b /> Current collection
              </span>
              <button
                className="mobile-country"
                onClick={() => setMobile(true)}
              >
                <Menu size={17} /> Countries
              </button>
            </div>
          </section>
          {country.id === "EA" && (
            <details className="currency-scope">
              <summary>One currency across 21 countries</summary>
              <p>{Object.values(euroMembers).join(", ")}.</p>
              <p>
                The euro is their national currency; no former national currency
                remains parallel legal tender. See collection notes for
                changeover details.
              </p>
            </details>
          )}
          <section className="filters" aria-label="Filter banknotes">
            <div className="filter-main">
              <label className="note-search">
                <Search size={17} />
                <input
                  placeholder="Search notes, people, landmarks…"
                  aria-label="Search banknotes"
                  value={f.query}
                  onChange={(e) => update("query", e.target.value)}
                />
              </label>
              <label className="select-wrap">
                <span>Denomination</span>
                <select
                  aria-label="Denomination"
                  value={f.denomination}
                  onChange={(e) => update("denomination", e.target.value)}
                >
                  <option value="all">All values</option>
                  {available.map((n) => (
                    <option key={n.id} value={n.value}>
                      {denomination(n)}
                    </option>
                  ))}
                </select>
              </label>
              <label className="select-wrap">
                <span>Material</span>
                <select
                  aria-label="Material"
                  value={f.material}
                  onChange={(e) => update("material", e.target.value)}
                >
                  <option value="all">All materials</option>
                  {[...new Set(notes.map((n) => n.material))].map((m) => (
                    <option key={m}>{m}</option>
                  ))}
                </select>
              </label>
              <button
                className={`more-filters ${expanded ? "active" : ""}`}
                onClick={() => setExpanded(!expanded)}
                aria-expanded={expanded}
              >
                <SlidersHorizontal size={17} />
                <span>More filters</span>
                {active > 0 && <b>{active}</b>}
              </button>
            </div>
            {expanded && (
              <div className="filter-extra">
                <fieldset>
                  <legend>Active year range</legend>
                  <input
                    type="number"
                    min="1900"
                    max="2026"
                    aria-label="Active from year"
                    placeholder="From"
                    value={f.from}
                    onChange={(e) => update("from", e.target.value)}
                  />
                  <span>–</span>
                  <input
                    type="number"
                    min="1900"
                    max="2026"
                    aria-label="Active to year"
                    placeholder="To"
                    value={f.to}
                    onChange={(e) => update("to", e.target.value)}
                  />
                </fieldset>
                <label>
                  Issue status
                  <select
                    aria-label="Issue status"
                    value={f.status}
                    onChange={(e) => update("status", e.target.value)}
                  >
                    <option value="all">All active notes</option>
                    <option value="Issued">Currently issued</option>
                    <option value="Not issued">No longer issued</option>
                    <option value="Withdrawing">Being withdrawn</option>
                  </select>
                </label>
                <label>
                  Orientation
                  <select
                    aria-label="Orientation"
                    value={f.orientation}
                    onChange={(e) => update("orientation", e.target.value)}
                  >
                    <option value="all">All orientations</option>
                    <option>Horizontal</option>
                    <option>Vertical</option>
                  </select>
                </label>
                <button
                  className="reset"
                  onClick={() =>
                    setF({ ...defaults, country: f.country, region: f.region })
                  }
                >
                  <RotateCcw size={15} /> Reset filters
                </button>
              </div>
            )}
          </section>
          <div className="shelf-toolbar">
            <span aria-live="polite">
              <strong>{filtered.length}</strong> banknotes{" "}
              <span className="subtle">on the shelf</span>
              {active > 0 && (
                <button
                  className="clear-inline"
                  onClick={() =>
                    setF({ ...defaults, country: f.country, region: f.region })
                  }
                >
                  Clear filters <X size={12} />
                </button>
              )}
            </span>
            <div>
              <div className="side-switch">
                <button
                  className={side === "front" ? "selected" : ""}
                  onClick={() => setSide("front")}
                >
                  Front
                </button>
                <button
                  className={side === "back" ? "selected" : ""}
                  onClick={() => setSide("back")}
                >
                  Back
                </button>
              </div>
              <select
                aria-label="Sort banknotes"
                value={f.sort}
                onChange={(e) => update("sort", e.target.value)}
              >
                <option value="value">Value: low to high</option>
                <option value="descending">Value: high to low</option>
                <option value="newest">Newest design first</option>
              </select>
            </div>
          </div>
          <section
            className="shelves"
            aria-label={`${country.name} banknote shelf`}
          >
            {filtered.map((n) => (
              <article className="note-card" key={n.id}>
                <button
                  className={`note-display ${(side === "back" ? n.backOrientation || n.orientation : n.orientation) === "Vertical" ? "vertical" : ""}`}
                  onClick={() => setSelected(n)}
                  aria-label={`Inspect ${denomination(n)}`}
                >
                  <NoteImage note={n} side={side} loading="lazy" />
                  <span className="inspect">
                    <ZoomIn size={16} /> Take a closer look
                  </span>
                </button>
                <div className="shelf-plank" />
                <div className="note-caption">
                  <div>
                    <h3>{denomination(n)}</h3>
                    <p>{side === "front" ? n.title : n.reverseTitle}</p>
                  </div>
                  <span>
                    {n.year}
                    <br />
                    <small>{n.material}</small>
                  </span>
                </div>
              </article>
            ))}
          </section>
          {!filtered.length && (
            <div className="empty">
              <Search size={32} />
              <h2>No notes on this shelf.</h2>
              <p>Try another value, material, or year range.</p>
              <button
                onClick={() =>
                  setF({ ...defaults, country: f.country, region: f.region })
                }
              >
                Reset filters
              </button>
            </div>
          )}
          <footer>
            <span>
              <Info size={14} /> A closer look at the money we pass by.
            </span>
            <button onClick={() => setAbout(true)}>
              Collection notes & sources <ArrowUpRight size={14} />
            </button>
          </footer>
        </main>
      </div>
      {selected && (
        <Viewer
          note={selected}
          onClose={() => setSelected(null)}
          onNavigate={(d) => {
            const i = filtered.findIndex((n) => n.id === selected.id);
            setSelected(filtered[(i + d + filtered.length) % filtered.length]);
          }}
        />
      )}
      {about && <About onClose={() => setAbout(false)} />}
    </>
  );
}
createRoot(document.getElementById("root")).render(<App />);
