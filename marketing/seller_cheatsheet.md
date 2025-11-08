# Git-Pal Seller Cheatsheet

## Generate Keys (One-time)
```bash
python tools/gp_keygen.py
```
Output: `licensor_keys/gp_issuer_private.pem` and `gp_issuer_public.pem`

## Issue License (Per Customer)
```bash
python tools/gp_issue_license.py --email buyer@example.com > token.txt
```
Options:
- `--days 365` (default: 1 year)
- `--features pro,custom` (default: "pro")

## Build Distribution
```bash
python -m build
```
Output: `dist/git_pal-1.0.0-py3-none-any.whl` and `git_pal-1.0.0.tar.gz`

## Pack Buyer Bundle
```bash
python tools/gp_pack_buyer.py --email buyer@example.com --token-file token.txt
```
Output: `buyer_builds/GitPal-Pro-buyer-example-com-*.zip`

Bundle contains:
- Wheel file
- Pre-configured config.toml
- QUICKSTART.txt
- PURCHASE.json

## Workflow
1. Generate keys once (keep private key secure!)
2. For each sale:
   - Issue license token
   - Build if needed
   - Pack buyer bundle
   - Send ZIP to customer (manually or via Gumroad automation)
