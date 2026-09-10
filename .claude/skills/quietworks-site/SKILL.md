---
name: quietworks-site
description: Edit, preview, re-record or deploy the Quietworks marketing site (boneydsilva.com) - the plain HTML/CSS/JS site that sells WorkQueue. Use for any change to public/, the demo film, the screenshots, pricing or copy, and for "why is the video not seeking", "the page jumps", "deploy the site", or adding a page for a new tool.
---

# Quietworks site

`D:\BoneysNewWebsiteProcessAutoamation` — plain HTML, CSS and JS. **No npm, no
framework.** What is in `public/` is exactly what is served. Live at
<https://boneydsilva.com> on Cloudflare Workers static assets.

There is **one build step**, and it only writes static HTML:
`python tools\build_i18n.py` generates the eleven translated languages, the
36 state pages, the sitemap and robots.txt. Run it after touching anything
under `tools/content/`, and run `python tools\build_i18n.py --check` before
deploying — it fails if `public/` is out of date.

Deploy is `git add -A; git commit; git push` — Cloudflare rebuilds in about
40 seconds. Only `public/` is published; `tools/`, `deploy/` and the READMEs
stay private. The repo is `boneydsilva/QuiteWorks` (the name misspells the
brand; leave it).

## Preview

```powershell
python tools\preview.py          # http://localhost:8000
```

Always this, never `python -m http.server`: the site uses clean URLs
(`/workqueue`, not `/workqueue.html`) because that is what Cloudflare serves,
and `preview.py` applies the same rule, serves the real 404 page, and answers
Range requests so the demo film can be seeked locally.

## The shape of it

| | |
|---|---|
| Tokens for every colour, radius, width | top of `public/assets/css/site.css` |
| Email, WhatsApp number, form key | `SITE` block at the top of `public/assets/js/site.js` |
| CSS sections | numbered `/* --- 1. Tokens */` … keep them in order and renumber if you insert one |
| JS sections | numbered the same way, each an `initX()` called from one `DOMContentLoaded` |

Header, footer and nav are **copy-pasted into the five hand-written English
pages**. Change one, change all five — and then run the build, because the
generated pages have their own copy from `build_i18n.py`. If the two drift the
site looks like two sites.

The build owns three blocks inside those English pages, between
`<!-- qw:hreflang -->`, `<!-- qw:langpicker -->` and `<!-- qw:jsonld -->`.
Do not hand-edit inside a marker; edit the builder. Delete a marker and the
build stops rather than quietly dropping the block.

Dark mode lives in three blocks that must stay in step: `:root`,
`@media (prefers-color-scheme: dark) :root:not([data-theme="light"])`, and
`:root[data-theme="dark"]`.

## Rules the site holds itself to

- **No testimonials, customer counts or invented numbers.** There are no
  customers yet. Inventing one loses the first deal that asks for a reference.
- **Nothing that claims to be a capture unless it is one.** The film and the
  screenshots say plainly what they are, and where the names are invented.
- **No cookie banner, no analytics, no payment integration** — all deliberate.
  Plausible or Cloudflare Web Analytics need no banner if he ever wants numbers.
- Every screenshot needs real `alt` text and explicit `width`/`height`, or the
  page jumps while images load.

## The English-only landing pages

Eight more, under `tools/content/pages.py` and rendered by `build_landing()`:
`/employee-task-tracker`, `/work-tracker`, `/task-management-software`, and
`/alternatives/` with a page each for Jira, Trello, Asana and "a WhatsApp
group and an Excel sheet". They exist because the rest of the site is written
brand-first and nobody searches for "team software that runs on your own
Wi-Fi".

- **English only, and staying that way.** These phrases are typed in English
  in India. Their `hreflang` set is one entry; the picker sends the other
  eleven languages to their own `/workqueue`.
- **The copy is not in `strings/`.** It is data in `pages.py`, a list of
  `(kind, dict)` blocks — hero, prose, cards, checks, steps, spec, table,
  shots, links, callout — rendered into the components the site already has.
  The vocabulary is documented above `build_landing()`. `**bold**` and
  `[text](/href)` work inside any string; nothing else does.
- **Every comparison page says who should not switch,** and three rows of
  every comparison table go against WorkQueue. Delete that and they become
  eight pages of the same advertisement, which is what Google demotes and
  what readers stop believing.
- **Other people's products are described qualitatively.** No competitor
  prices or plan limits — they change, and a stale claim about someone else's
  product is worse than no claim.
- The English footer carries one link the other eleven do not
  (`/alternatives/`). That is the only place the twelve footers differ, and
  it differs because the pages genuinely do not exist elsewhere.

## Twelve languages and 36 states

133 pages in all. Full detail in
**`tools/README.md`**; the parts worth knowing before you touch anything:

| | |
|---|---|
| Languages | `tools/content/langs.py` — English + hi mr bn ta te kn ml gu pa or as |
| States | `tools/content/states.py` — 28 states, 8 union territories |
| Copy | `tools/content/strings/<lang>.py` — 434 keys, `en.py` is the reference |
| URLs | `/pricing`, `/hi/pricing`, `/india`, `/india/maharashtra`, `/mr/india/maharashtra` |

- **Every core page exists in all twelve.** A state page exists in English
  always, and in that state's own language only where the two differ — Goa
  works in English, so it has one page, not two. `hreflang` lists only what
  really exists; the picker still offers twelve and sends the rest to that
  language's `/india`.
- **The build refuses a half-finished translation.** Every strings file must
  carry exactly the keys `en.py` has.
- **`{state}` cannot just take a case ending** in most of these languages.
  Four different patterns are in use and a new template has to pick one — the
  table is in `tools/README.md`. Read the generated `<h1>` before believing a
  template: `महाराष्ट्र मधील` and `தமிழ்நாடு-இல்` were both wrong, and both
  looked fine in the Python.
- **Nothing redirects on language.** `offerLanguage()` shows one dismissible
  line when the browser asks for a language this page exists in, once per
  browser. Being moved somewhere you cannot read, because of a header you have
  never seen, is worse than the English you expected.

## The demo film

`public/assets/video/workqueue-demo.mp4` — 1:07, 1920x1080, ~7 MB, the second
section of the home page. Real footage of WorkQueue 4.0.1, not an animation.
Poster: `public/assets/img/demo-poster.jpg`.

Re-recording is three commands, documented step by step in
**`tools/README.md`** (seed → serve → `record_demo.py` → `compose_demo.py`).
What is worth knowing before you start:

- **It needs a real bar running on this PC.** The strip in the film is a
  genuine Windows AppBar. `record_demo.py` borrows it — names it Asha Rao,
  empties its queue — and **puts it back** at the end. If it dies half way,
  clear the name and delete the demo tasks from the Machines tab yourself.
- **Headless Chrome only manages ~2.6 fps** on the screencast. The recorder
  uses an ordinary window parked off-screen (`--window-position=-2400,0`
  plus the occlusion flags) which gives ~6 fps. Do not "fix" it back to
  headless.
- **The shot list is the top half of `compose_demo.py`** — one entry per shot
  naming the seconds of recording it plays, the camera (centre and width, in
  the dashboard's CSS pixels) at each end of the move, and the caption.
  Check framing with `python tools\compose_demo.py <dir> still 7 25 36 58`
  rather than sitting through a five minute render.
- **If you re-cut the film, the five timestamps live in the markup**, on the
  `<button data-film-at data-film-text>` chapter buttons — in `index.html` and
  in every generated home page, because each language has its own captions.
  Change `h_film_cap1..5` and the `at` values in `build_i18n.py`, then
  rebuild. `initFilm()` reads whatever is in the DOM.
- The music is synthesised from sine partials in `tools/score_demo.py`.
  Nothing sampled, nothing licensed. Keep it that way: no stock music.

### Cloudflare does not answer Range requests

Workers static assets return the **whole file** for a `Range:` request.
Verified at origin with `CF-Cache-Status: MISS`. A streamed `<video>` therefore
reports `seekable.end === 0` — the scrub bar does nothing and every chapter
button lands back at zero.

So `initFilm()` fetches the mp4 and plays a `blob:` URL, which seeks perfectly.
The cost is that playback starts after the download, which is why the button
counts the download in and why the encode is held near 7 MB (CRF 24). If the
site ever moves somewhere that honours Range, that whole dance can go.

Test it, do not assume:

```powershell
curl.exe -s -D - -H "Range: bytes=100-199" -o NUL https://boneydsilva.com/assets/video/workqueue-demo.mp4
# 206 + Content-Range = seekable; 200 + the full Content-Length = not
```

## Screenshots

Real captures of WorkQueue on seeded demo data — regenerate them rather than
editing the old ones. `tools/README.md` has the three steps. The employee strip
cannot be captured headlessly (it is a native AppBar): grab the **top 44 pixels
of the screen**, the band Windows reserves, which nothing can overlap. Anything
else grabbed from this screen is unreliable — the terminal renders above other
windows.

To let people open a screenshot full size, wrap the `.shot` in
`<a class="shot-zoom" href="…" data-zoom>`; `initZoom()` upgrades it to an
overlay and the link still works with JavaScript off.

## Before saying a change works

```powershell
python tools\build_i18n.py           # or --check, if you changed no content
python tools\audit_seo.py            # all 125 pages, no browser needed
python tools\preview.py 8021         # then, in a second window:
python tools\check_console.py 8021
```

`audit_seo.py` walks every page for one `<h1>`, sane title and description
lengths, a canonical matching where the file is, internal links that resolve,
`hreflang` sets that are reciprocal, and a sitemap that agrees with the tree.
`check_console.py` loads one page of every kind in headless Chrome and asserts
**zero console messages** — the rule this site has always held itself to,
now across twelve languages.

Then check the thing you changed in both themes and at 390 / 760 / 1280 px,
and if it was copy in a language you do not read, read the generated `<h1>`
rather than trusting the template.

Watch for **layout that changes height while the page is idle** — an animating
section that grows by a card pushes the page under the reader. Sample the
element's height over a full cycle and assert it is constant.

## Still open

- `formAccessKey` in `site.js` is still `PASTE-YOUR-…`. Until it is set, the
  contact form falls back to a `mailto:`. Free key from web3forms.com.
- The rest of the pre-launch checklist is the table in `README.md`.

**This repo is public.** Anything written here ships to GitHub, so keep
commercial thinking — pricing rationale, licensing gaps, deal notes — out of
it and in the conversation instead.
