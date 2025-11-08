#!/usr/bin/env python3
import argparse
import time
import json
import re
import zipfile
from pathlib import Path

TEMPLATE = """license_token = "{tok}"

[license]
public_key = \"\"\"
{pub}\"\"\"
"""

QS = """# Git-Pal — Quickstart (Pro)
1) Install: pip install {wheel}
2) Create config file and paste:
{cfg}
3) Set editor: git config --global sequence.editor "git-pal"
4) Run: git rebase -i HEAD~5
"""

def sanitize(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", s)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--email", required=True)
    ap.add_argument("--token-file", required=True)
    ap.add_argument("--public-key", default="licensor_keys/gp_issuer_public.pem")
    ap.add_argument("--dist-dir", default="dist")
    ap.add_argument("--out-dir", default="buyer_builds")
    args = ap.parse_args()

    dist = Path(args.dist_dir)
    out = Path(args.out_dir)
    out.mkdir(exist_ok=True)
    wheel = sorted(dist.glob("git_pal-*.whl"))[-1]
    tok = Path(args.token_file).read_text().strip()
    pub = Path(args.public_key).read_text()

    cfg = TEMPLATE.format(pub=pub, tok=tok)
    tag = f"GitPal-Pro-{sanitize(args.email)}-{int(time.time())}"
    bundle = out / tag
    bundle.mkdir(parents=True, exist_ok=True)

    (bundle/wheel.name).write_bytes(wheel.read_bytes())
    (bundle/"config.toml").write_text(cfg, encoding="utf-8")
    (bundle/"QUICKSTART.txt").write_text(QS.format(wheel=wheel.name, cfg=cfg), encoding="utf-8")
    (bundle/"PURCHASE.json").write_text(json.dumps({"email": args.email, "issued_at": int(time.time())}, indent=2), encoding="utf-8")

    z = out/f"{tag}.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zp:
        for p in bundle.iterdir():
            zp.write(p, arcname=p.name)
    print(z)

if __name__ == "__main__":
    main()
