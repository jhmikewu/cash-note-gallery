export const countries = [
  ["US", "United States", "USD", "US dollar", "🇺🇸"],
  ["CN", "China", "CNY", "Chinese yuan", "🇨🇳"],
  ["HK", "Hong Kong SAR, China", "HKD", "Hong Kong dollar", "🇭🇰"],
  ["MO", "Macau SAR, China", "MOP", "Macanese pataca", "🇲🇴"],
  ["EA", "Euro area", "EUR", "Euro", "🇪🇺"],
  ["JP", "Japan", "JPY", "Japanese yen", "🇯🇵"],
  ["GB", "United Kingdom", "GBP", "Pound sterling", "🇬🇧"],
  ["IN", "India", "INR", "Indian rupee", "🇮🇳"],
  ["RU", "Russia", "RUB", "Russian ruble", "🇷🇺"],
  ["BR", "Brazil", "BRL", "Brazilian real", "🇧🇷"],
  ["CA", "Canada", "CAD", "Canadian dollar", "🇨🇦"],
  ["KR", "South Korea", "KRW", "South Korean won", "🇰🇷"],
  ["MX", "Mexico", "MXN", "Mexican peso", "🇲🇽"],
  ["AU", "Australia", "AUD", "Australian dollar", "🇦🇺"],
  ["TR", "Türkiye", "TRY", "Turkish lira", "🇹🇷"],
  ["ID", "Indonesia", "IDR", "Indonesian rupiah", "🇮🇩"],
  ["SA", "Saudi Arabia", "SAR", "Saudi riyal", "🇸🇦"],
  ["CH", "Switzerland", "CHF", "Swiss franc", "🇨🇭"],
  ["PL", "Poland", "PLN", "Polish złoty", "🇵🇱"],
  ["AR", "Argentina", "ARS", "Argentine peso", "🇦🇷"],
  ["IL", "Israel", "ILS", "Israeli new shekel", "🇮🇱"],
  ["SE", "Sweden", "SEK", "Swedish krona", "🇸🇪"],
].map(([id, name, currency, currencyName, flag], i) => ({
  id,
  name,
  currency,
  currencyName,
  flag,
  rank: i + 1,
}));
export const rankingSource =
  "https://www.visualcapitalist.com/the-128-trillion-global-economy-in-2026/";
export const euroMembers = {
  AT: "Austria",
  BE: "Belgium",
  BG: "Bulgaria",
  HR: "Croatia",
  CY: "Cyprus",
  EE: "Estonia",
  FI: "Finland",
  FR: "France",
  DE: "Germany",
  GR: "Greece",
  IE: "Ireland",
  IT: "Italy",
  LV: "Latvia",
  LT: "Lithuania",
  LU: "Luxembourg",
  MT: "Malta",
  NL: "Netherlands",
  PT: "Portugal",
  SK: "Slovakia",
  SI: "Slovenia",
  ES: "Spain",
};
export function resolveCountry(id) {
  if (Object.hasOwn(euroMembers, id)) return "EA";
  return countries.some((c) => c.id === id) ? id : "US";
}
export function matchesCountry(country, query) {
  const names =
    country.id === "EA"
      ? Object.values(euroMembers).join(" ") + " Eurozone"
      : country.id === "CN"
        ? "Mainland China"
        : country.id === "MO"
          ? "Macao"
          : "";
  return `${country.name} ${country.currency} ${names}`
    .toLowerCase()
    .includes(query.toLowerCase());
}
export const defaults = {
  country: "US",
  region: "mainland",
  query: "",
  material: "all",
  denomination: "all",
  status: "all",
  orientation: "all",
  from: "",
  to: "",
  sort: "value",
};
export function filterNotes(notes, filters) {
  const currency = collectionFor(filters.country, filters.region).currency;
  return notes
    .filter(
      (n) =>
        (!currency || n.currency === currency) &&
        (filters.material === "all" || n.material === filters.material) &&
        (filters.denomination === "all" ||
          n.value === Number(filters.denomination)) &&
        (filters.status === "all" || n.status === filters.status) &&
        (filters.orientation === "all" ||
          n.orientation === filters.orientation) &&
        overlapsPeriod(n, "2000-01-01", "2026-11-03") &&
        (!filters.from ||
          Number(filters.from) <=
            Number((n.circulationEnd || "2026").slice(0, 4))) &&
        (!filters.to || n.year <= Number(filters.to)) &&
        (!filters.from ||
          !filters.to ||
          Number(filters.from) <= Number(filters.to)) &&
        `${n.value} ${n.currency} ${n.title} ${n.reverseTitle} ${n.series}`
          .toLowerCase()
          .includes(filters.query.toLowerCase()),
    )
    .sort((a, b) =>
      filters.sort === "newest"
        ? b.year - a.year
        : filters.sort === "descending"
          ? b.value - a.value
          : a.currency.localeCompare(b.currency) || a.value - b.value,
    );
}
// Dates are inclusive. A null end means no withdrawal has been recorded.
// Year-only source dates stay year-only instead of inventing a day/month.
export function overlapsPeriod(note, from, to) {
  const start = note.circulationStart || String(note.year);
  const end = note.circulationEnd;
  return (
    `${start.length === 4 ? start + "-01-01" : start}` <= to &&
    (!end || `${end.length === 4 ? end + "-12-31" : end}` >= from)
  );
}
export function circulationLabel(note) {
  return `${note.year}–${note.circulationEnd ? note.circulationEnd.slice(0, 4) : "present"}`;
}
export function groupDenominations(notes) {
  const groups = new Map();
  for (const note of notes) {
    const key = `${note.currency}-${note.value}`;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(note);
  }
  return [...groups.values()].map((variants) => {
    variants.sort(
      (a, b) =>
        (b.circulationStart || String(b.year)).localeCompare(
          a.circulationStart || String(a.year),
        ) || a.id.localeCompare(b.id),
    );
    return { note: variants[0], variants };
  });
}
export function collectionFor(country) {
  return countries.find((c) => c.id === resolveCountry(country));
}
export function denomination(note) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: note.currency,
    maximumFractionDigits: note.value % 1 ? 1 : 0,
  }).format(note.value);
}
