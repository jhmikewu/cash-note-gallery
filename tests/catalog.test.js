import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync, existsSync } from "node:fs";
import {
  countries,
  defaults,
  filterNotes,
  resolveCountry,
  matchesCountry,
  euroMembers,
  overlapsPeriod,
  groupDenominations,
} from "../src/catalog.js";
const notes = JSON.parse(
  readFileSync(new URL("../src/notes.json", import.meta.url)),
);
test("Indonesian ordinary variants preserve withdrawal and material boundaries", () => {
  const indonesia = filterNotes(notes, { ...defaults, country: "ID" });
  assert.equal(indonesia.length, 26);
  assert.equal(groupDenominations(indonesia).length, 7);
  const old = indonesia.filter((n) => n.circulationEnd === "2008-12-30");
  assert.equal(old.length, 4);
  assert.ok(old.every((n) => overlapsPeriod(n, "2008-12-30", "2008-12-30")));
  assert.ok(old.every((n) => !overlapsPeriod(n, "2008-12-31", "2026-11-03")));
  assert.equal(
    indonesia.find((n) => n.id === "IDR-100000-1999").material,
    "Polymer",
  );
  const revised = indonesia.filter((n) => n.value === 10000);
  assert.equal(revised.length, 5);
  const heroes = indonesia.filter((n) => n.series === "2016 emission");
  assert.equal(heroes.length, 7);
  assert.ok(
    heroes.every(
      (n) => n.circulationStart === "2016-12-19" && n.circulationEnd === null,
    ),
  );
});
test("shelves group values with newest matching variant first", () => {
  const groups = groupDenominations(
    filterNotes(notes, { ...defaults, country: "GB" }),
  );
  assert.deepEqual(
    groups.map((g) => g.note.value),
    [5, 10, 20, 50],
  );
  assert.ok(groups.every((g) => g.note.title === "King Charles III"));
  assert.equal(
    groups.reduce((sum, g) => sum + g.variants.length, 0),
    20,
  );
  const historic = groupDenominations(
    filterNotes(notes, {
      ...defaults,
      country: "GB",
      from: "2000",
      to: "2000",
    }),
  );
  assert.ok(historic.every((g) => g.note.year <= 2000));
  const mixed = groupDenominations([
    { id: "a", currency: "USD", value: 5, year: 2020 },
    { id: "b", currency: "CAD", value: 5, year: 2021 },
  ]);
  assert.equal(mixed.length, 2);
});
test("circulation overlap includes cutoff day but excludes redemption-only periods", () => {
  assert.ok(
    overlapsPeriod(
      { year: 1980, circulationEnd: "2000-01-01" },
      "2000-01-01",
      "2026-11-03",
    ),
  );
  assert.ok(
    !overlapsPeriod(
      { year: 1980, circulationEnd: "1999-12-31" },
      "2000-01-01",
      "2026-11-03",
    ),
  );
  assert.ok(!overlapsPeriod({ year: 2027 }, "2000-01-01", "2026-11-03"));
});
test("UK portrait variants coexist and withdrawn notes leave later year searches", () => {
  const all = filterNotes(notes, {
    ...defaults,
    country: "GB",
    denomination: "20",
  });
  assert.ok(all.some((n) => n.title === "King Charles III"));
  assert.ok(
    all.some(
      (n) => n.title === "Queen Elizabeth II" && n.material === "Polymer",
    ),
  );
  assert.ok(all.some((n) => n.reverseTitle === "Michael Faraday"));
  const later = filterNotes(notes, {
    ...defaults,
    country: "GB",
    from: "2023",
  });
  assert.ok(later.every((n) => n.status !== "Withdrawn"));
});
test("19 countries, euro area and two SARs have complete collections", () => {
  assert.equal(countries.length, 22);
  assert.equal(
    countries.filter((c) => !["EA", "HK", "MO"].includes(c.id)).length,
    19,
  );
  assert.equal(new Set(notes.map((n) => n.id)).size, notes.length);
  for (const c of countries) {
    assert.ok(
      notes.some((n) => n.currency === c.currency),
      c.name,
    );
  }
  for (const n of notes) {
    for (const key of [
      "title",
      "reverseTitle",
      "material",
      "source",
      "front",
      "back",
      "dimensions",
    ])
      assert.ok(n[key], `${n.id}: ${key}`);
    assert.ok(n.year <= 2026);
  }
});
test("US opens with seven denominations in ascending order", () =>
  assert.deepEqual(
    filterNotes(notes, defaults).map((n) => n.value),
    [1, 2, 5, 10, 20, 50, 100],
  ));
test("euro area occupies one member and preserves country links and search", () => {
  assert.equal(countries.filter((c) => c.currency === "EUR").length, 1);
  const euro = countries.find((c) => c.id === "EA");
  for (const [id, name] of Object.entries(euroMembers)) {
    assert.equal(resolveCountry(id), "EA");
    assert.ok(matchesCountry(euro, name));
    assert.deepEqual(
      filterNotes(notes, { ...defaults, country: id }),
      filterNotes(notes, { ...defaults, country: "EA" }),
    );
  }
  assert.equal(
    groupDenominations(filterNotes(notes, { ...defaults, country: "EA" }))
      .length,
    7,
  );
});
test("replacement members contain the current denomination sets and local images", () => {
  for (const [country, values] of Object.entries({
    PL: [10, 20, 50, 100, 200, 500],
    SE: [20, 50, 100, 200, 500, 1000],
    AR: [10, 20, 50, 100, 200, 500, 1000, 2000, 10000, 20000],
    IL: [20, 50, 100, 200],
  })) {
    const collection = filterNotes(notes, { ...defaults, country });
    assert.deepEqual(
      collection.map((n) => n.value),
      values,
    );
    for (const n of collection)
      for (const side of ["front", "back"]) {
        assert.ok(n[side].startsWith("./notes/"));
        assert.ok(
          existsSync(new URL("../public/" + n[side].slice(2), import.meta.url)),
        );
      }
  }
});
test("year range uses interval overlap and rejects reversed ranges", () => {
  assert.deepEqual(
    filterNotes(notes, { ...defaults, from: "2000", to: "2005" }).map(
      (n) => n.value,
    ),
    [1, 2, 20, 50],
  );
  assert.equal(
    filterNotes(notes, { ...defaults, from: "2020", to: "2000" }).length,
    0,
  );
});
test("China SARs have separate entries and independent currencies", () => {
  assert.ok(!countries.some((c) => c.id === "TW"));
  assert.ok(!notes.some((n) => n.currency === "TWD"));
  for (const [country, currency] of [
    ["CN", "CNY"],
    ["HK", "HKD"],
    ["MO", "MOP"],
  ]) {
    const result = filterNotes(notes, { ...defaults, country });
    assert.equal(groupDenominations(result).length, 6);
    assert.ok(result.every((n) => n.currency === currency));
  }
  assert.equal(resolveCountry("HK"), "HK");
  assert.ok(
    matchesCountry(
      countries.find((c) => c.id === "MO"),
      "Macau",
    ),
  );
});
test("combined material, denomination and text filters", () => {
  assert.equal(
    filterNotes(notes, {
      ...defaults,
      country: "GB",
      material: "Polymer",
      denomination: "50",
      query: "Turing",
    })[0].id,
    "GBP-50",
  );
  assert.equal(
    filterNotes(notes, { ...defaults, material: "Polymer" }).length,
    0,
  );
});
test("withdrawn-from-issue notes remain discoverable", () => {
  assert.equal(
    filterNotes(notes, {
      ...defaults,
      country: "DE",
      status: "Not issued",
    }).some((n) => n.value === 500),
    true,
  );
  assert.equal(
    filterNotes(notes, { ...defaults, country: "IN", status: "Withdrawing" })[0]
      .value,
    2000,
  );
});
test("vertical orientation and newest ordering work", () => {
  assert.equal(
    filterNotes(notes, {
      ...defaults,
      country: "CH",
      orientation: "Vertical",
    }).filter((n) => n.status !== "Withdrawn").length,
    6,
  );
  assert.equal(
    filterNotes(notes, { ...defaults, sort: "newest" })[0].value,
    100,
  );
});
test("ordinary issuer variants share shelves and respect actual introduction dates", () => {
  const hk = filterNotes(notes, {
    ...defaults,
    country: "HK",
    denomination: "20",
  });
  assert.equal(groupDenominations(hk).length, 1);
  assert.equal(hk.length, 9);
  assert.ok(hk.some((n) => n.issuer === "HSBC"));
  assert.ok(hk.some((n) => n.issuer === "Standard Chartered Bank (Hong Kong)"));
  const early = filterNotes(notes, { ...defaults, country: "HK", to: "2003" });
  assert.deepEqual([...new Set(early.map((n) => n.value))], [10, 100, 500]);
  const macau = filterNotes(notes, {
    ...defaults,
    country: "MO",
    query: "Ultramarino",
  });
  assert.equal(macau.length, 12);
});
test("Swiss recall boundaries preserve cutoff-year eligibility", () => {
  const sixth = notes.filter(
    (n) => n.currency === "CHF" && n.series === "Sixth series",
  );
  assert.equal(sixth.length, 6);
  assert.ok(sixth.every((n) => overlapsPeriod(n, "2000-01-01", "2000-04-30")));
  assert.ok(sixth.every((n) => !overlapsPeriod(n, "2000-05-01", "2026-11-03")));
  const later = filterNotes(notes, {
    ...defaults,
    country: "CH",
    from: "2022",
  });
  assert.equal(later.length, 6);
});
