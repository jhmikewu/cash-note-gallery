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
} from "../src/catalog.js";
const notes = JSON.parse(
  readFileSync(new URL("../src/notes.json", import.meta.url)),
);
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
  assert.equal(filterNotes(notes, { ...defaults, country: "EA" }).length, 7);
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
    assert.equal(result.length, 6);
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
    filterNotes(notes, { ...defaults, country: "DE", status: "Not issued" })[0]
      .value,
    500,
  );
  assert.equal(
    filterNotes(notes, { ...defaults, country: "IN", status: "Withdrawing" })[0]
      .value,
    2000,
  );
});
test("vertical orientation and newest ordering work", () => {
  assert.equal(
    filterNotes(notes, { ...defaults, country: "CH", orientation: "Vertical" })
      .length,
    6,
  );
  assert.equal(
    filterNotes(notes, { ...defaults, sort: "newest" })[0].value,
    100,
  );
});
