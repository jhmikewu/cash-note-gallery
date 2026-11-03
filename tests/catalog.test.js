import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync, existsSync } from "node:fs";
import { countries, defaults, filterNotes } from "../src/catalog.js";
const notes = JSON.parse(
  readFileSync(new URL("../src/notes.json", import.meta.url)),
);
test("20 economies each have a complete nonempty collection", () => {
  assert.equal(countries.length, 20);
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
test("euro countries share designs without duplicating records", () =>
  assert.deepEqual(
    filterNotes(notes, { ...defaults, country: "DE" }),
    filterNotes(notes, { ...defaults, country: "FR" }),
  ));
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
