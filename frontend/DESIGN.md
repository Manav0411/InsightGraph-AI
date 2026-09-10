# InsightGraph design system — "Warm Editorial"

The visual language for both the public landing (`components/landing/`) and the
signed-in app. This file is the source of truth; the landing already follows it,
the app is being migrated surface by surface.

## Palette

Unchanged — the warm-cream / forest-green M3 tokens already in
`src/app/globals.css` (`--color-*`, `:root` = light, `.dark` = dark) and exposed
through Tailwind as `bg-surface`, `text-on-surface`, `text-primary`,
`border-outline-variant`, etc. Do **not** introduce new color literals; the one
exception is the dark "machine" panel (`#111a14` family), which is intentionally
constant across themes — see `Card variant="inset"`.

## Type — three faces, three jobs

Loaded via the `@import` at the top of `globals.css`. Tailwind utilities:

| Utility | Face | Use for |
|---|---|---|
| `font-display` | Instrument Serif (400 + italic only) | `h1`/`h2`, page titles, section heads, the briefing masthead. Set an italic fragment in headlines for emphasis (`<em>`). Never `font-bold` — it has one weight. |
| `font-reader` | Newsreader (400–600) | All running prose, card bodies, FAQ answers, `h3`/`h4`. |
| `font-mono` | Spline Sans Mono | The machine voice **and** all UI chrome: eyebrows, labels, buttons, chips, nav, counts, the run log, data readouts. There is no separate sans. |

Legacy `font-headline` (Literata) / `font-body` (Nunito Sans) still exist for
not-yet-migrated screens. Remove them from `tailwind.config.js` once every
surface is migrated.

Sentence case for headings and body. UPPERCASE only for small mono eyebrow
labels (~11px, `tracking-[0.12em]`).

## Surfaces

- Cards: `rounded-2xl`, hairline border (`border-outline-variant/40`), soft
  ambient shadow (`.ds-shadow`, theme-aware, defined in `globals.css`).
- **No hard offset shadows** (`shadow-[2px_2px_0_...]`) and **no gradient
  fills** — both are the old look being removed.
- Interactive cards: `.ds-shadow-lift` + `hover:-translate-y-0.5` (1px–2px lift,
  nothing bouncier).
- Dark inset panel (the pipeline "machine"): `Card variant="inset"`.

## Interactive

- Buttons: `rounded-lg`, mono, accent fill for primary with a soft glow
  (`shadow-[0_6px_18px_-6px_rgba(74,124,89,0.38)]`). Variants: `primary`,
  `outline`, `ghost`, `subtle`.
- Chips: pill (`rounded-full`), mono. Selected = soft `bg-primary/10` +
  `border-primary/40` + `text-primary` (**not** a hard green fill). Muted /
  excluded = dashed border + strike-through.
- Focus: always a visible `focus-visible:ring-2 ring-primary` ring.

## Rhythm

- `PageShell` owns page width + gutters + vertical padding. `width`: `narrow`
  (prose), `default`, `wide` (grids / the reader).
- Left-aligned. Generous whitespace. Hairline section dividers
  (`border-outline-variant/30`).
- Quiet inline data — `TREND 4.4 · SQI 61` as mono text, never boxed metric
  tiles.

## Motion

Restrained. A one-time load reveal at most; hover = 1px lift; the landing's
pipeline recovery edge animates its dash (it encodes a loop). Everything under
`prefers-reduced-motion`.

## Primitives — `src/components/ui/`

`Button`, `Card`, `Chip`, `SectionHeader`, `PageShell` + `PageHeader`,
`SignalCard`, `TextInput`. Import from `../components/ui`. Live reference at
`/style-guide` (dev only).

## Migration plan (screen by screen, one PR each)

1. **Foundation** — token layer + primitives + this doc. _(this PR)_
2. **Nav + Intelligence Reader** — `app/layout.js` signed-in nav,
   `components/IntelligenceReader.js`.
3. **History + history detail** — `app/history/page.js`, `app/history/[id]/`.
   Drop the fabricated `generateNarrative` copy and the decorative timeline
   gradient.
4. **Preferences + onboarding** — `app/preferences/page.js`,
   `app/onboarding/page.js`. Both become `Chip`-driven.
5. **Admin** — `app/admin/mission-control/`, `app/admin/analytics/`. Fold in the
   fabricated-telemetry cleanup.

Each step: migrate the screen to the primitives, delete its bespoke class
strings, verify `npm run build` + both themes + mobile, ship as its own PR.
