# Deploying to AWS (S3 + CloudFront)

This site is plain files, so the cheapest correct way to host it is a **private S3
bucket** with **CloudFront** in front. CloudFront gives you HTTPS, a free
certificate, and a CDN. Expect roughly **$1–3 a month** at small traffic; the
free tier covers most of the first year.

The bucket stays private. Only CloudFront can read it, via Origin Access
Control. Never make the bucket public — you do not need to, and it is the single
most common way static sites get defaced.

---

## Before you start

1. An AWS account.
2. The AWS CLI installed and logged in: `aws configure` (or `aws sso login`).
3. A domain name. If it is not already in Route 53, you will be editing DNS
   wherever you bought it.

Pick your names now and use them consistently below:

| Placeholder | Example |
|---|---|
| `BUCKET` | `quietworks-site` (must be globally unique) |
| `DOMAIN` | `quietworks.in` |
| `WWW` | `www.quietworks.in` |
| `REGION` | `ap-south-1` (Mumbai) |

---

## 1. Create the bucket

```powershell
aws s3api create-bucket `
  --bucket BUCKET `
  --region ap-south-1 `
  --create-bucket-configuration LocationConstraint=ap-south-1

aws s3api put-public-access-block `
  --bucket BUCKET `
  --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

Do **not** enable S3 static website hosting. CloudFront reads the bucket
directly through its private REST endpoint.

## 2. Upload the site

```powershell
# Long cache for things that never change under the same name
aws s3 sync "D:\BoneysNewWebsiteProcessAutoamation" s3://BUCKET `
  --exclude "*" --include "assets/*" `
  --cache-control "public,max-age=31536000,immutable" `
  --delete

# Short cache for the pages themselves, so edits go live quickly
aws s3 sync "D:\BoneysNewWebsiteProcessAutoamation" s3://BUCKET `
  --exclude "assets/*" --exclude "deploy/*" --exclude "tools/*" --exclude "README.md" `
  --cache-control "public,max-age=300" `
  --delete
```

`deploy/`, `tools/` and `README.md` are excluded on purpose — they are for you,
not for visitors.

## 3. Get a certificate

The certificate for CloudFront **must be in `us-east-1`**, whatever region your
bucket is in. This catches everybody once.

```powershell
aws acm request-certificate `
  --domain-name DOMAIN `
  --subject-alternative-names WWW `
  --validation-method DNS `
  --region us-east-1
```

Open ACM in the `us-east-1` console, copy the CNAME records it shows, and add
them at your DNS provider. Validation usually completes within a few minutes.
Copy the certificate ARN when it says **Issued**.

## 4. Create the CloudFront distribution

Console is genuinely easier than the CLI here. In CloudFront → **Create
distribution**:

| Setting | Value |
|---|---|
| Origin domain | pick your bucket from the list (the `.s3.` one, **not** the website endpoint) |
| Origin access | **Origin access control settings** → Create new OAC → then **Copy policy** |
| Viewer protocol policy | Redirect HTTP to HTTPS |
| Allowed HTTP methods | GET, HEAD |
| Cache policy | CachingOptimized |
| Compress objects automatically | Yes |
| Alternate domain names (CNAMEs) | `DOMAIN` and `WWW` |
| Custom SSL certificate | the ACM certificate from step 3 |
| Default root object | `index.html` |
| Price class | "Use only North America, Europe, Asia…" is fine and cheaper |

When it offers **Copy policy** after creating the OAC, paste that policy into
S3 → your bucket → Permissions → Bucket policy. That one step is what lets
CloudFront read a private bucket.

### Error pages

Distribution → **Error pages** → Create custom error response:

| Setting | Value |
|---|---|
| HTTP error code | 403: Forbidden |
| Customize error response | Yes |
| Response page path | `/404.html` |
| HTTP Response code | 404 |

Add the same for **404: Not Found**. S3 returns 403 rather than 404 for missing
objects in a private bucket, so without the 403 rule your 404 page never shows.

## 5. Point DNS at it

Copy the distribution domain (`d111111abcdef8.cloudfront.net`).

**In Route 53:** create an **A record → Alias → Alias to CloudFront
distribution** for both `DOMAIN` and `WWW`.

**Elsewhere:** create a CNAME from `www` to the distribution domain. Root
domains cannot be CNAMEs — use your registrar's ALIAS/ANAME record if it has
one, or move DNS to Route 53.

## 6. Deploy changes after that

Run `deploy-aws.ps1` (in this folder). Fill in the three variables at the top
once, then it is a single command every time:

```powershell
powershell -ExecutionPolicy Bypass -File .\deploy\deploy-aws.ps1
```

It syncs both cache profiles and invalidates the CloudFront cache so your edits
are live in about a minute.

---

## Rough monthly cost

| Item | Cost |
|---|---|
| S3 storage (~2 MB) | negligible |
| S3 requests | pennies |
| CloudFront first 1 TB out | free tier covers the first year; ~$0.09/GB after |
| Route 53 hosted zone | $0.50 per month, if you use it |
| ACM certificate | free |

A site this size with a few thousand visitors a month lands near **$1**.

## Things that go wrong

- **AccessDenied on every page** — the OAC bucket policy was not pasted into
  S3. Redo the end of step 4.
- **Certificate not selectable** — it was created outside `us-east-1`. Request
  it again in `us-east-1`.
- **Edits not showing** — CloudFront is still serving the cached copy. The
  deploy script invalidates it; if you uploaded by hand, run
  `aws cloudfront create-invalidation --distribution-id ID --paths "/*"`.
- **The SVG favicon does not appear** — check its content type is
  `image/svg+xml`:
  `aws s3 cp s3://BUCKET/assets/img/favicon.svg s3://BUCKET/assets/img/favicon.svg --content-type image/svg+xml --metadata-directive REPLACE`
