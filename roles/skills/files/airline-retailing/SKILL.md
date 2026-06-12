---
name: airline-retailing
description: Domain reference for airline distribution and retailing — NDC, ONE Order, Offers & Orders, the legacy PNR/e-ticket/EMD model, GDS/PSS industry roles, servicing flows, and look-to-book economics. Load before designing, implementing, or reviewing ANY airline-domain feature, model, API, or story. Defines the ubiquitous language for the order platform.
---

# Airline Retailing — Domain Reference

Load this before touching anything airline-shaped. The domain is full of overloaded
terms and 1960s legacy concepts; this skill defines what we mean and which concepts
are allowed inside our platform.

## Industry Map — Who Is Who

- **Airline** — owns inventory (seats) and, in modern retailing, computes its own
  offers and prices.
- **PSS (Passenger Service System)** — the airline's hosted core: reservations,
  inventory, departure control. Amadeus Altéa, Sabre SabreSonic, Navitaire. The PSS
  is the system of record for the airline's seats and bookings. *We are not a PSS.*
- **GDS (Global Distribution System)** — legacy marketplace between airlines and
  travel sellers (Amadeus, Sabre, Travelport). In the legacy model the GDS itself
  constructs fares from filed data and checks availability. *We are not a legacy GDS.*
- **Aggregator** — modern equivalent: normalizes many airline NDC APIs behind one
  API (e.g. Duffel). *This is our category.*
- **Seller** — OTA (online travel agency), TMC (corporate travel management
  company), travel app, AI agent. *These are our customers.*
- **Data/standards bodies** — IATA (standards: NDC, ONE Order, settlement via BSP),
  ATPCO (filed fares and rules), OAG/Cirium (schedules, status). Access to filed
  data and settlement is licensed/accredited, not open.

## Legacy Record Model (understand it; do not adopt it)

A single trip is scattered across three record types:

- **PNR (Passenger Name Record)** — the reservation: passengers, segments, SSRs,
  contact data. Lives in the airline PSS/GDS. Identified by a 6-char record locator.
- **E-ticket (ETKT)** — a *financial document* (13-digit number) holding flight
  coupons; the artifact that revenue accounting, interline billing, and BSP/ARC
  settlement are built on.
- **EMD (Electronic Miscellaneous Document)** — a separate financial document for
  ancillaries (bags, seats, fees).

The three reference each other and drift out of sync; reconciling them is a large
share of industry servicing pain. **Platform rule: these concepts exist only inside
connector adapters for legacy integrations. They never appear in the canonical
model, public APIs, events, or database schemas.**

## Modern Retailing — NDC and ONE Order

- **NDC (New Distribution Capability)** — IATA's API standard for distribution.
  Key inversion vs legacy: *the airline computes and returns finished, priced
  offers*; the consumer does not construct fares. Messages we care about:
  `AirShopping` (search → offers), `OfferPrice` (firm up an offer),
  `SeatAvailability`, `ServiceList` (ancillaries), `OrderCreate`, `OrderRetrieve`,
  `OrderChange`, `OrderCancel`, `OrderReshop` (servicing: what can change and at
  what cost). NDC is XML-schema based with significant **version fragmentation**
  (17.2, 18.1, 21.3, …) and per-airline quirks/certification — connectors must
  isolate version differences completely.
- **Offers & Orders** — IATA's umbrella program: everything is an Offer (airline-
  priced, expiring) that becomes an Order when accepted.
- **ONE Order** — the record standard: a single Order replaces PNR + ETKT + EMD.
  Adoption is early (industry ambition ~2030; pioneers like Finnair; vendors:
  Amadeus Nevio, SabreMosaic). The blocker is accounting: tickets are how airlines
  recognize revenue and settle — order-based accounting is the hard migration.
  **We are Order-native internally from day one; we have no legacy to migrate.**

## Canonical Vocabulary (the ubiquitous language)

- **Offer** — an airline-priced, *expiring* proposal (price + conditions + services).
  Offers are quotes, not entitlements; they die at TTL. Only the airline that made
  an offer can honor it.
- **Order** — the accepted offer; OUR system of record for the customer's trip.
  Contains OrderItems, Passengers, Payments, and references to airline-side records.
- **Airline Order Reference** — the airline-side record backing part of our Order
  (an airline order ID, or a PNR locator via a legacy connector). One customer
  Order may wrap N airline orders (one per carrier). Keeping our Order consistent
  with N airline-side states is the platform's core correctness problem.
- **Journey / Segment / Leg** — Journey: passenger's origin→destination intent;
  Segment: one flight number's portion; Leg: one takeoff-to-landing. A segment can
  span legs (direct flight with a stop); a journey spans segments (connections).
- **Service** — anything sold beyond the flight: bag, seat, ancillary.
- **Passenger types** — ADT (adult), CHD (child), INF (infant, often no seat).
  Pricing and document rules differ per type.
- **Cabin vs RBD** — cabin is physical (economy/business); RBD (booking class,
  one letter: Y, J, …) is the inventory/pricing bucket within a cabin.
- **Fare family / branded fare** — airline product tier (refundability, bags,
  changes) attached to an offer.
- **Codeshare** — flight sold under one airline's code, operated by another.
  Always model marketing vs operating carrier separately.
- **Interline / virtual interlining** — interline: airlines agree to carry across
  carriers under one contract; virtual interlining: a platform combines airlines
  with NO such agreement — separate contracts, no airline-protected connections;
  the platform owns the misconnect risk. Never present a virtual interline as a
  protected connection.

## Servicing Flows (where the labor and the moat are)

- **Voluntary change** — customer-initiated. NDC flow: `OrderReshop` (options +
  change cost) → accept → `OrderChange`. Price difference + change fee may apply.
- **Cancel/refund** — refundability is per fare/per service; outcomes include cash
  refund, voucher, or forfeiture; taxes are often refundable when the fare is not.
- **Involuntary / schedule change** — airline-initiated (retiming, cancellation,
  equipment change). Arrives airline-side first: the platform must *detect* it
  (notification or polling), reconcile its Order, and drive customer choice
  (accept / alternative / refund). Different rules apply: usually free rebooking.
- **IRROPS (irregular operations)** — day-of disruption (weather, technical).
  Time-critical rebooking; the disruption-agent use case.
- **Reissue pricing** — recalculating an already-partly-flown or changed booking is
  notoriously harder than initial pricing. In NDC, the airline computes it
  (`OrderReshop`); never attempt to compute reissue values platform-side.

## Operating Constraints

- **Look-to-book** — shopping requests outnumber bookings ~1000:1. Airlines
  rate-limit and may charge per query. The shopping cache (TTL by route/carrier
  volatility, stale-while-revalidate) is a core system, and its hit rate is the
  platform's cost structure.
- **Offer TTL** — offers expire in minutes; an order attempt against a dead offer
  fails. Design for re-shop-and-retry, surface TTLs in the API.
- **Compliance shapes the data model** — GDPR (passenger data retention and
  minimization), PCI-DSS (tokenize payment cards; keep the platform out of PAN
  scope), APIS/Secure Flight (passport/visa fields governments require airlines to
  transmit — the Passenger model must carry them).

## Platform Rules (non-negotiable)

1. **Order-native**: the canonical model is Offer/Order/Service. No PNR, ticket, or
   EMD concepts outside connector internals.
2. **The airline is the source of truth for price and inventory.** We never compute
   fares, availability, or reissue values; we consume, normalize, cache, and
   orchestrate.
3. **XML never crosses the connector boundary.** Connectors translate NDC (any
   version) and legacy formats into the canonical model at the edge.
4. **Every airline-facing operation is idempotent and reconciliation-safe** —
   duplicate sends, timeouts with unknown outcome, and airline-side state drift are
   normal, not exceptional.
5. **Money and personal data are modeled first-class** — Payment state, refund
   outcomes, and APIS fields are schema, not JSON blobs.

## Glossary (quick reference)

| Term | Meaning |
|---|---|
| ADT/CHD/INF | Passenger types: adult / child / infant |
| APIS | Advance Passenger Information System — government-mandated passenger data |
| ATPCO | Fare-filing body for legacy distribution |
| BSP/ARC | IATA / US agency settlement systems (accreditation required) |
| DCS | Departure Control System (check-in, boarding) — PSS territory |
| EMD | Electronic Miscellaneous Document — legacy ancillary financial doc |
| GDS | Global Distribution System (Amadeus/Sabre/Travelport) |
| IRROPS | Irregular operations — day-of disruption |
| NDC | New Distribution Capability — IATA distribution API standard |
| ONE Order | IATA standard replacing PNR+ETKT+EMD with a single Order |
| PNR | Passenger Name Record — legacy reservation record |
| PSS | Passenger Service System — airline's core hosted system |
| RBD | Reservation Booking Designator — booking class letter |
| SSR | Special Service Request (wheelchair, meal, …) |
| TMC | Travel Management Company (corporate agency) |

## Related Skills

- [/modulith-template](../modulith-template/SKILL.md) — where modules like order, shopping, servicing, connectors live
- [/api-design](../api-design/SKILL.md) — the public API must speak this vocabulary
- [/business-analysis](../business-analysis/SKILL.md) — stories use the ubiquitous language defined here
