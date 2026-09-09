# Deploy the Quietworks site to Cloud Storage and invalidate Cloud CDN.
#
#   powershell -ExecutionPolicy Bypass -File .\deploy\deploy-gcp.ps1
#
# Fill in the three values below once. Everything else is automatic.

$Bucket   = "quietworks-site"                 # your Cloud Storage bucket name
$UrlMap   = "quietworks-lb"                   # your load balancer URL map, or "" to skip the CDN flush
$SiteRoot = Join-Path (Split-Path -Parent $PSScriptRoot) "public"  # only this folder ships

# --- checks ---------------------------------------------------------------

if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Host "gcloud is not installed, or not on PATH." -ForegroundColor Red
    Write-Host "Get it from https://cloud.google.com/sdk then run 'gcloud init'."
    exit 1
}

if ($Bucket -eq "quietworks-site") {
    Write-Host "Edit the Bucket at the top of this script first." -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path (Join-Path $SiteRoot "index.html"))) {
    Write-Host "Cannot find index.html in $SiteRoot - is the public folder still there?" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Deploying $SiteRoot" -ForegroundColor Cyan
Write-Host "        to gs://$Bucket" -ForegroundColor Cyan
Write-Host ""

# --- 1. assets: cached hard ----------------------------------------------

Write-Host "[1/4] Uploading assets..." -ForegroundColor Green
gcloud storage rsync (Join-Path $SiteRoot "assets") "gs://$Bucket/assets" `
    --recursive --delete-unmatched-destination-objects
if (-not $?) { Write-Host "Asset upload failed." -ForegroundColor Red; exit 1 }

gcloud storage objects update "gs://$Bucket/assets/**" `
    --cache-control="public,max-age=31536000,immutable" --quiet

# --- 2. pages: short cache ------------------------------------------------

Write-Host ""
Write-Host "[2/4] Uploading pages..." -ForegroundColor Green
gcloud storage rsync $SiteRoot "gs://$Bucket" `
    --exclude="^assets/.*" `
    --delete-unmatched-destination-objects
if (-not $?) { Write-Host "Page upload failed." -ForegroundColor Red; exit 1 }

# --- 3. cache headers on the pages ---------------------------------------

Write-Host ""
Write-Host "[3/4] Setting cache headers..." -ForegroundColor Green
gcloud storage objects update "gs://$Bucket/*.html" `
    --cache-control="public,max-age=300" --quiet

# --- 4. clear the CDN -----------------------------------------------------

if ($UrlMap) {
    Write-Host ""
    Write-Host "[4/4] Invalidating Cloud CDN..." -ForegroundColor Green
    gcloud compute url-maps invalidate-cdn-cache $UrlMap --path "/*" --global --async --quiet
} else {
    Write-Host ""
    Write-Host "[4/4] Skipping CDN invalidation (no UrlMap set)." -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "Done. Changes are usually live within a minute." -ForegroundColor Cyan
Write-Host ""
