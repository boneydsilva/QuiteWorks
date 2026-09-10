# Quietworks website

The marketing site for Quietworks and its tools. Plain HTML, CSS and JavaScript
— no build step, no npm, no framework. What is in this folder is exactly what
gets uploaded.

```
public/             EVERYTHING IN HERE IS PUBLISHED. Nothing outside it is.
  index.html        Home - the company, the demo film, the approach, the catalogue
  workqueue.html    WorkQueue product page - the page that does the selling
  pricing.html      Pricing, cost comparison, licence terms
  contact.html      Contact form and channels
  404.html          Not-found page
  robots.txt        Search engine rules
  sitemap.xml       Page list for search engines
  assets/
    css/site.css    The entire stylesheet. Tokens at the top control everything.
    js/site.js      Theme toggle, mobile nav, contact form. Config at the top.
    img/            Product screenshots (see tools/) + demo poster + favicon
    video/          The demo film (see tools/)
wrangler.jsonc      Cloudflare assets config (publish dir + 404 handling)
deploy/
  cloudflare.md     How this site is hosted - read this one
  aws.md            Step-by-step AWS hosting (S3 + CloudFront)
  gcp.md            Step-by-step Google Cloud hosting
  deploy-aws.ps1    One-command deploy to AWS
  deploy-gcp.ps1    One-command deploy to Google Cloud
tools/
  README.md         How to regenerate the product screenshots
  preview.py        Local preview that matches how Cloudflare serves the site
  set-site-url.py   Repoints the whole site at a new address, in one command
  seed_demo.py      Fills a throwaway WorkQueue database with demo data
  shoot.py          Drives headless Chrome and saves the 1920x1080 PNGs
```

---

## Preview it locally

With Python already installed:

```powershell
cd D:\BoneysNewWebsiteProcessAutoamation
python tools\preview.py
```

Then open <http://localhost:8000>.

Use this rather than `python -m http.server`. The site uses clean URLs
(`/workqueue`, not `/workqueue.html`) because that is what Cloudflare Pages
serves; the plain server does not understand those and 404s on every page.
`preview.py` applies the same rule Pages does, and serves `404.html` properly.

---

## Before it goes live — the checklist

These are the placeholders. The site will publish without them but should not.

| Where | What to change | Done? |
|---|---|---|
| `public/assets/js/site.js` | `formAccessKey` — sign up free at [web3forms.com](https://web3forms.com) and paste the key. Until you do, the form falls back to opening the visitor's email app. | **still to do** |
| Site address in canonical, og:url, og:image, robots.txt and sitemap.xml | Run `python tools\set-site-url.py https://your-domain`. One command does all 15 references. | done — set to `https://boneydsilva.com` |
| `public/pricing.html` | The prices, if ₹14,999 / ₹7,500 / ₹4,999 are not what you settled on. | check |
| `public/assets/js/site.js` | `email` and `whatsapp` | done — `boneydsilva@gmail.com`, `919004213100` |
| All `public/*.html` files | The address shown in the footers and on the contact page | done |

A quick way to find what is left:

```powershell
Select-String -Path public\*.html,public\assets\js\*.js,public\robots.txt,public\sitemap.xml -Pattern "quietworks\.in|PASTE-YOUR"
```

Note the WhatsApp number is stored **once**, in `site.js` — every WhatsApp link on
the site is built from it at page load, so there is only one place to change it.

---

## Editing the site

### Changing the brand name

"Quietworks" appears in the `<title>` and `<h1>` of each page, in the header
and footer brand blocks, and in the JS comments. Search and replace across the
`.html` files. The logo is a `<svg>` inline in each header and footer, plus
`public/assets/img/favicon.svg` — three small rectangles you can recolour by editing
`--accent` in the CSS (the favicon has its colour hard-coded because favicons
cannot read CSS variables).

### Changing the colours

Everything comes from the tokens at the top of `public/assets/css/site.css`. Change
`--accent` and the buttons, links, step numbers, badges and highlight boxes all
follow. There are three blocks to keep in step:

1. `:root` — the light palette
2. `@media (prefers-color-scheme: dark) :root:not([data-theme="light"])` — dark for people whose OS asks for it
3. `:root[data-theme="dark"]` — dark for people who pressed the toggle

Set the same values in blocks 2 and 3.

### Adding a new tool

This is designed for it, because more tools are coming.

1. **Copy `public/workqueue.html` to `public/yournewtool.html`** and rewrite the content.
   The structure is worth keeping: hero, what the user sees, feature rows with
   screenshots, a resilience or "how it fits together" section, requirements,
   an honest list of limits, FAQ, call to action.

2. **Add a card to the catalogue** on `public/index.html`. Find the
   `<!-- ===================== Catalogue -->` section and replace one of the
   `tool-card soon` blocks:

   ```html
   <div class="tool-card live reveal">
     <span class="tag tag-live">Available now</span>
     <h3>Your tool</h3>
     <p>One sentence on what it does and who for.</p>
     <a class="btn btn-primary btn-sm" href="/yournewtool">Take a look</a>
   </div>
   ```

3. **Add it to the four navigation bars.** They are copy-pasted into each page
   (the cost of having no build step). Search for `nav-links` and add a link in
   all five HTML files, plus the `Tools` column in each footer. Link to
   `/yournewtool`, not `/yournewtool.html` — the site uses clean URLs.

4. **Add it to `public/sitemap.xml`.**

5. **Add its pricing** as a fourth card in `public/pricing.html`, or give it its own
   pricing page if the model is different.

Once there are four or five tools, the repeated header and footer will start to
hurt. That is the moment to add a tiny build step or move to Astro — not before.

### The demo film on the home page

The "See it work" section under the hero is a real recording of WorkQueue
running, not an animation: `public/assets/video/workqueue-demo.mp4`, 1:07,
1920x1080, about 6 MB. It is two captures cut together --

* the **dashboard**, driven with real mouse and keyboard events and captured
  out of the browser's own compositor, and
* the **employee strip**, grabbed from the top 44 pixels of a Windows desktop
  with a real bar running in them.

Both were recorded against a throwaway demo database, so the task really is
assigned, really is delivered to a PC, and really is completed by the employee
side of the API. The clock in the film is the product's clock.

The page adds three things around it: a poster with a play button, a row of
chapter buttons that seek the video, and a caption under it that follows
along. Those live in `initFilm()` in `site.js` -- the chapter times and their
text are the `FILM_CHAPTERS` array at the top of section 7. If you re-cut the
film, those five timestamps are the only thing that has to change. Everything
still works with JavaScript off: the video keeps its own controls.

The video has `preload="none"`, so a visitor who never presses play downloads
the 64 KB poster and nothing else.

**Why the page fetches the file itself.** Cloudflare's asset server answers a
Range request with the whole file, which makes a streamed `<video>` report
itself as not seekable: the scrub bar does nothing and a chapter button lands
back at zero. So `initFilm()` fetches the mp4, hands the element a `blob:` URL
and plays that, which seeks perfectly. The trade is that playback starts after
the download instead of during it, which is why the button counts the download
in, and why the encode is kept near 6 MB. If the site ever moves somewhere that
honours Range, that whole dance can go and the `<source>` can do the work.

**Re-recording it** is documented with the screenshot tooling in
**[tools/](tools/README.md)** -- same demo database, same three steps, plus a
fourth for the film. It takes about ten minutes, most of it the render.

### Adding screenshots### Adding screenshots

Put the PNG in `public/assets/img/` and reference it inside a `.shot` block:

```html
<figure style="margin:0">
  <div class="shot shot-crop">
    <div class="shot-bar">
      <span class="shot-dot"></span><span class="shot-dot"></span><span class="shot-dot"></span>
      <span class="shot-title">Your app — Screen name</span>
    </div>
    <img src="assets/img/your-shot.png" width="1920" height="1080" loading="lazy"
         alt="Describe what is actually on screen, for people who cannot see it.">
  </div>
  <figcaption class="shot-caption">A sentence pointing at what matters in it.</figcaption>
</figure>
```

`shot-crop` limits tall screenshots to a readable height and fades the bottom.
Drop it for short, wide images like the WorkQueue strip. Always fill in `alt`
and the `width`/`height` — the dimensions stop the page jumping while images load.

The screenshots in `public/assets/img/` are real captures of WorkQueue 4.0.1 running
against a seeded demo database, taken on 10 Sep 2026 at 1920x1080. When the UI
changes, regenerate them with the scripts in **[tools/](tools/README.md)** —
that is one command for the dashboard shots — rather than editing the old
images. If you change what a screenshot shows, check the caption and the `alt`
text still describe it.

---

## Deploying

**Live at <https://boneydsilva.com> — Cloudflare, free, with unlimited
bandwidth.**
Read **[deploy/cloudflare.md](deploy/cloudflare.md)** for the one-time setup.
After that, deploying is:

```powershell
git add -A
git commit -m "what changed"
git push
```

Cloudflare rebuilds within a minute. Only `public/` is served; `deploy/`,
`tools/` and this README stay private.

`deploy/aws.md` and `deploy/gcp.md` cover S3 + CloudFront (~₹100–250/month) and
Cloud Storage behind a load balancer (~₹1,600/month). They are kept because they
work and are written up properly, but neither gives this site anything
Cloudflare Pages does not provide free.

---

## What this site deliberately does not have

- **No testimonials or customer counts.** There are none yet. Inventing them is
  the fastest way to lose a deal when someone asks for a reference.
- **No cookie banner.** Nothing sets a cookie. The only thing stored in the
  browser is the light/dark preference, in `localStorage`, which does not
  require consent.
- **No analytics.** If you want them, Plausible or Cloudflare Web Analytics are
  one script tag and do not need a banner either. Google Analytics does need one.
- **No payment integration.** Buying goes through the contact form on purpose,
  so you talk to the first customers rather than watching a checkout. Add
  Razorpay or Stripe once you know what the objections are.
