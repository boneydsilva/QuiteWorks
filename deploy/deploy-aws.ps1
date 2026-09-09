# Deploy the Quietworks site to S3 and invalidate CloudFront.
#
#   powershell -ExecutionPolicy Bypass -File .\deploy\deploy-aws.ps1
#
# Fill in the three values below once. Everything else is automatic.

$Bucket         = "quietworks-site"                 # your S3 bucket name
$DistributionId = "E1234567890ABC"                  # your CloudFront distribution ID
$SiteRoot       = Join-Path (Split-Path -Parent $PSScriptRoot) "public"  # only this folder ships

# --- checks ---------------------------------------------------------------

if (-not (Get-Command aws -ErrorAction SilentlyContinue)) {
    Write-Host "The AWS CLI is not installed, or not on PATH." -ForegroundColor Red
    Write-Host "Get it from https://aws.amazon.com/cli/ then run 'aws configure'."
    exit 1
}

if ($Bucket -eq "quietworks-site" -or $DistributionId -eq "E1234567890ABC") {
    Write-Host "Edit the Bucket and DistributionId at the top of this script first." -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path (Join-Path $SiteRoot "index.html"))) {
    Write-Host "Cannot find index.html in $SiteRoot - is the public folder still there?" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Deploying $SiteRoot" -ForegroundColor Cyan
Write-Host "        to s3://$Bucket" -ForegroundColor Cyan
Write-Host ""

# --- 1. assets: cached hard, they change name when they change ------------

Write-Host "[1/3] Uploading assets..." -ForegroundColor Green
aws s3 sync $SiteRoot "s3://$Bucket" `
    --exclude "*" --include "assets/*" `
    --cache-control "public,max-age=31536000,immutable" `
    --delete
if ($LASTEXITCODE -ne 0) { Write-Host "Asset upload failed." -ForegroundColor Red; exit 1 }

# --- 2. pages: short cache so edits appear quickly ------------------------

Write-Host ""
Write-Host "[2/3] Uploading pages..." -ForegroundColor Green
aws s3 sync $SiteRoot "s3://$Bucket" `
    --exclude "assets/*" `
    --cache-control "public,max-age=300" `
    --delete
if ($LASTEXITCODE -ne 0) { Write-Host "Page upload failed." -ForegroundColor Red; exit 1 }

# --- 3. clear the CDN -----------------------------------------------------

Write-Host ""
Write-Host "[3/3] Invalidating CloudFront..." -ForegroundColor Green
$result = aws cloudfront create-invalidation --distribution-id $DistributionId --paths "/*" | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) { Write-Host "Invalidation failed." -ForegroundColor Red; exit 1 }

Write-Host ""
Write-Host "Done. Invalidation $($result.Invalidation.Id) is in progress." -ForegroundColor Cyan
Write-Host "Changes are usually live within a minute."
Write-Host ""
