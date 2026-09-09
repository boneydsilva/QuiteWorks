# Deploying to Google Cloud (Cloud Storage + HTTPS load balancer)

The Google equivalent of the AWS setup: files in a **Cloud Storage** bucket,
with a **global external HTTPS load balancer** in front for HTTPS, a free
managed certificate, and Cloud CDN.

One thing to know before you choose: the load balancer's forwarding rule costs
roughly **$18 a month** even at zero traffic. AWS CloudFront has no such
standing charge. For a site this size, **AWS works out cheaper** — pick GCP if
the rest of your infrastructure already lives here.

---

## Before you start

1. A Google Cloud project with billing enabled.
2. `gcloud` installed and logged in: `gcloud init`.
3. A domain name you can add DNS records to.

Set these once so the commands below can be pasted as they are:

```powershell
$env:PROJECT = "quietworks"
$env:BUCKET  = "quietworks-site"        # must be globally unique
$env:DOMAIN  = "www.quietworks.in"

gcloud config set project $env:PROJECT
```

---

## 1. Create the bucket and upload

```powershell
gcloud storage buckets create gs://$env:BUCKET `
  --location=asia-south1 `
  --uniform-bucket-level-access

# Anyone can read the files. They are a public website - this is correct here.
gcloud storage buckets add-iam-policy-binding gs://$env:BUCKET `
  --member=allUsers --role=roles/storage.objectViewer

# Serve index.html at / and 404.html for anything missing
gcloud storage buckets update gs://$env:BUCKET `
  --web-main-page-suffix=index.html --web-error-page=404.html
```

Upload, with the same two cache profiles as the AWS setup:

```powershell
$SITE = "D:\BoneysNewWebsiteProcessAutoamation"

gcloud storage rsync "$SITE/assets" "gs://$env:BUCKET/assets" --recursive --delete-unmatched-destination-objects
gcloud storage objects update "gs://$env:BUCKET/assets/**" --cache-control="public,max-age=31536000,immutable"

gcloud storage rsync $SITE "gs://$env:BUCKET" --exclude="^(assets|deploy|tools)/.*|README\.md" --delete-unmatched-destination-objects
gcloud storage objects update "gs://$env:BUCKET/*.html" --cache-control="public,max-age=300"
```

## 2. Reserve an IP and get a certificate

```powershell
gcloud compute addresses create quietworks-ip --global

gcloud compute ssl-certificates create quietworks-cert `
  --domains=$env:DOMAIN --global
```

The certificate stays in `PROVISIONING` until DNS points at the IP — that is
expected. Get the IP now, because you need it for step 4:

```powershell
gcloud compute addresses describe quietworks-ip --global --format="value(address)"
```

## 3. Put the load balancer in front

```powershell
gcloud compute backend-buckets create quietworks-backend `
  --gcs-bucket-name=$env:BUCKET --enable-cdn

gcloud compute url-maps create quietworks-lb `
  --default-backend-bucket=quietworks-backend

gcloud compute target-https-proxies create quietworks-https `
  --url-map=quietworks-lb --ssl-certificates=quietworks-cert

gcloud compute forwarding-rules create quietworks-fr `
  --address=quietworks-ip --global `
  --target-https-proxy=quietworks-https --ports=443
```

Send plain HTTP to HTTPS as well, so nobody lands on a broken link:

```powershell
# PowerShell has no heredoc for gcloud, so write the tiny YAML to a file first.
@"
name: quietworks-redirect
defaultUrlRedirect:
  redirectResponseCode: MOVED_PERMANENTLY_DEFAULT
  httpsRedirect: true
"@ | Out-File -Encoding utf8 "$env:TEMP\redirect.yaml"

gcloud compute url-maps import quietworks-redirect --global --quiet --source="$env:TEMP\redirect.yaml"

gcloud compute target-http-proxies create quietworks-http --url-map=quietworks-redirect
gcloud compute forwarding-rules create quietworks-fr-http `
  --address=quietworks-ip --global --target-http-proxy=quietworks-http --ports=80
```

## 4. Point DNS at the IP

Create an **A record** for your domain pointing at the reserved IP from step 2.

Then wait. The managed certificate goes `PROVISIONING` → `ACTIVE` once Google
can see the DNS, which takes **15 minutes to an hour**, occasionally longer.
Check it with:

```powershell
gcloud compute ssl-certificates describe quietworks-cert --global --format="value(managed.status)"
```

Do not start debugging before it says `ACTIVE`. Almost every "my GCP site is
broken" moment is really "the certificate has not finished".

## 5. Deploy changes after that

```powershell
powershell -ExecutionPolicy Bypass -File .\deploy\deploy-gcp.ps1
```

It uploads both cache profiles and invalidates the CDN.

---

## Rough monthly cost

| Item | Cost |
|---|---|
| Forwarding rule (the load balancer) | **~$18/month, always** |
| Storage (~2 MB) | negligible |
| Egress | ~$0.08–0.12 per GB |
| Managed certificate | free |

**A cheaper alternative:** Firebase Hosting serves the same folder over HTTPS
on a custom domain with a generous free tier and no standing charge —
`firebase init hosting` with this folder as the public directory, then
`firebase deploy`. It is a better fit than the load balancer for a brochure
site if you want to stay inside Google.

## Things that go wrong

- **The root URL returns an XML error instead of the home page.** Backend
  buckets do not always apply the bucket's main-page-suffix setting. Add a path
  rule to the URL map rewriting `/` to `/index.html`, or verify the setting
  stuck with `gcloud storage buckets describe gs://$env:BUCKET --format="value(website)"`.
- **`SSL_ERROR` or a certificate warning** — the certificate is still
  provisioning. See step 4.
- **Edits not showing** — Cloud CDN is still serving the old copy:
  `gcloud compute url-maps invalidate-cdn-cache quietworks-lb --path "/*" --global`
- **404 on every asset** — check the objects are actually at `assets/css/...`
  in the bucket and not nested inside an extra folder from the rsync.
