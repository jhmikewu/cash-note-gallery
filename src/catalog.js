export const countries = [
  ["US", "United States", "USD", "US dollar", "🇺🇸"],
  ["CN", "China", "CNY", "Chinese yuan", "🇨🇳"],
  ["DE", "Germany", "EUR", "Euro", "🇩🇪"],
  ["JP", "Japan", "JPY", "Japanese yen", "🇯🇵"],
  ["GB", "United Kingdom", "GBP", "Pound sterling", "🇬🇧"],
  ["IN", "India", "INR", "Indian rupee", "🇮🇳"],
  ["FR", "France", "EUR", "Euro", "🇫🇷"],
  ["RU", "Russia", "RUB", "Russian ruble", "🇷🇺"],
  ["IT", "Italy", "EUR", "Euro", "🇮🇹"],
  ["BR", "Brazil", "BRL", "Brazilian real", "🇧🇷"],
  ["CA", "Canada", "CAD", "Canadian dollar", "🇨🇦"],
  ["KR", "South Korea", "KRW", "South Korean won", "🇰🇷"],
  ["MX", "Mexico", "MXN", "Mexican peso", "🇲🇽"],
  ["AU", "Australia", "AUD", "Australian dollar", "🇦🇺"],
  ["ES", "Spain", "EUR", "Euro", "🇪🇸"],
  ["TR", "Türkiye", "TRY", "Turkish lira", "🇹🇷"],
  ["ID", "Indonesia", "IDR", "Indonesian rupiah", "🇮🇩"],
  ["NL", "Netherlands", "EUR", "Euro", "🇳🇱"],
  ["SA", "Saudi Arabia", "SAR", "Saudi riyal", "🇸🇦"],
  ["CH", "Switzerland", "CHF", "Swiss franc", "🇨🇭"],
].map(([id, name, currency, currencyName, flag], i) => ({
  id,
  name,
  currency,
  currencyName,
  flag,
  rank: i + 1,
}));
export const rankingSource =
  "https://www.visualcapitalist.com/the-worlds-largest-economies-by-gdp-in-2026/";
export const defaults = {
  country: "US",
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
  const currency = countries.find((c) => c.id === filters.country)?.currency;
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
        (!filters.from || Number(filters.from) <= 2026) &&
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
export function denomination(note) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: note.currency,
    maximumFractionDigits: note.value % 1 ? 1 : 0,
  }).format(note.value);
}
