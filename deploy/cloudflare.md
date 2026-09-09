# Deploying to Cloudflare Pages

This is the cheapest correct way to host this site: **free, permanently**, with
unlimited bandwidth, free SSL, a free custom domain, and a CDN that is fast from
India. There is no standing charge to forget about.

The site publishes from GitHub. Once it is connected, deploying is `git push` —
Cloudflare rebuilds within about a minute.

**Only `public/` is served.** Everything else in this repo — `deploy/`,
`tools/`, this README — stays private, because Cloudflare is told that `public`
is the output directory.

---

## One-time setup

### 1. Put the site on GitHub

From the site folder:

```powershell
cd D:\BoneysNewWebsiteProcessAutoamation
git init
git add -A
git commit -m "Quietworks website"
```

Create an **empty** repository at <https://github.com/new> — no README, no
`.gitignore`, no licence, or the first push will be rejected. Private is fine;
Cloudflare can read private repos once you authorise it.

Then, with `NAME` as the repository name you chose:

```powershell
git branch -M main
git remote add origin https://github.com/boneydsilva/NAME.git
git push -u origin main
```

### 2. Connect Cloudflare Pages

1. Sign up at <https://dash.cloudflare.com/sign-up> (free, no card).
2. **Compute (Workers & Pages)** → **Create** → **Pages** →
   **Connect to Git**.
3. Authorise GitHub and pick the repository.
4. Set the build settings — these matter:

   | Setting | Value |
   |---|---|
   | Framework preset | **None** |
   | Build command | *(leave completely empty)* |
   | Build output directory | **`public`** |
   | Root directory | *(leave as `/`)* |

5. **Save and Deploy.**

A minute later the site is live. Depending on how Cloudflare provisions it you
get either `https://<project>.pages.dev` or `https://<project>.<account>.workers.dev`
— this one is the workers.dev kind. Either URL is permanent and free, so you can
send it to people today, before you own a domain.

`wrangler.jsonc` in the repo root sets the assets directory and the 404
behaviour. Leave it alone unless you rename the project.

### 3. Deploying changes after that

```powershell
git add -A
git commit -m "what changed"
git push
```

That is the whole deploy. Cloudflare builds every push to `main`, and every
other branch becomes its own preview URL, which is a genuinely useful way to
look at a change before it goes live.

---

## Clean URLs

Pages serves `/workqueue`, and 307-redirects `/workqueue.html` to it. The site's
links, canonical tags and sitemap all use the clean form, so nothing redirects
in normal use. Two things follow from that:

- Link to `/pricing`, never `/pricing.html`, when you add pages.
- Preview locally with `python tools\preview.py`, not `python -m http.server` —
  the plain server does not resolve clean URLs and 404s on every page.

---

## Adding your domain later

When you have bought one:

1. Cloudflare dashboard → your Pages project → **Custom domains** → **Set up a
   custom domain** → enter `quietworks.in` (and add `www.quietworks.in` as a
   second one).
2. Cloudflare tells you which nameservers or CNAME records to set at your
   registrar. If you move the domain's nameservers to Cloudflare, everything —
   DNS, SSL, redirects — is handled for you and stays free.
3. The certificate is issued automatically, usually within minutes.

**Then update the site to match**, or search engines will keep being told the
canonical address is the placeholder:

- `public/*.html` — the `<link rel="canonical">`, `og:url` and `og:image` tags
- `public/robots.txt` — the `Sitemap:` line
- `public/sitemap.xml` — all four `<loc>` entries

One command does all of it:

```powershell
python tools\set-site-url.py https://www.quietworks.in
```

Then commit and push. Run `python tools\set-site-url.py --check` any time to see
what the site currently claims its address is.

---

## What it costs

| Item | Cost |
|---|---|
| Hosting, bandwidth, SSL, CDN | **free** |
| `*.pages.dev` subdomain | **free** |
| Custom domain on Cloudflare | **free** (the domain registration itself is not) |
| A domain, from any registrar | roughly ₹900–1,300 a year |

The free tier's only real limit is 500 builds a month, which is about 16 deploys
a day, every day.

---

## Things that go wrong

- **The deployed site shows a file listing, or 404s on every page** — the build
  output directory is not set to `public`. Fix it in
  **Settings → Builds & deployments** and redeploy.
- **`git push` is rejected as non-fast-forward** — the GitHub repo was created
  with a README. Either `git pull --rebase origin main` and push again, or
  delete the repo and recreate it empty.
- **The 404 page does not appear** (an empty body, so the browser shows its own
  error page) — this project deploys as a Worker with static assets, where
  `not_found_handling` is off by default. That is what `wrangler.jsonc` at the
  repo root is for; keep the `"not_found_handling": "404-page"` line. Check with
  `curl -s https://your-site/nope | wc -c` — a few thousand bytes means it is
  working, zero means it is not.
- **An edit is not showing** — check the deployment actually succeeded in the
  Pages dashboard, then hard-reload. Pages purges its own cache on deploy, so a
  stale page is nearly always a failed build.

---

## The other guides in this folder

`aws.md` and `gcp.md` describe S3 + CloudFront (~₹100–250/month) and Cloud
Storage behind a load balancer (~₹1,600/month). Both work and both are written
up properly, but neither buys this site anything Cloudflare Pages does not give
away. Use them if you need the site inside an AWS or GCP account for some other
reason.
