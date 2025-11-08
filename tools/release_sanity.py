#!/usr/bin/env python3
import argparse
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path

WHEEL_GLOB = "git_pal-*.whl"
SDIST_GLOB = "git_pal-*.tar.gz"

def run(cmd, **kw):
    r = subprocess.run(cmd, text=True, capture_output=True, **kw)
    if r.returncode != 0:
        raise SystemExit(f"CMD FAIL: {' '.join(cmd)}\nSTDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}")
    return r

def find_one(p: Path, pattern: str) -> Path:
    items = sorted(p.glob(pattern))
    if not items:
        raise SystemExit(f"❌ Missing artifact: {pattern}")
    return items[-1]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--email", default="buyer@example.com")
    ap.add_argument("--zip", help="Path to buyer zip (optional). If absent, will pack via tools/gp_pack_buyer.py")
    args = ap.parse_args()

    repo = Path.cwd()
    dist = repo / "dist"
    buyer = repo / "buyer_builds"

    # 1) Build artifacts
    # Skip wheel upgrade to avoid debian package conflict
    run([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "build", "--user"])
    run([sys.executable, "-m", "build"])
    wheel = find_one(dist, WHEEL_GLOB)
    sdist = find_one(dist, SDIST_GLOB)

    # 2) Issue token if needed
    priv_dir = repo / "licensor_keys"
    if not (priv_dir / "gp_issuer_private.pem").exists():
        run([sys.executable, "tools/gp_keygen.py"])
    tok_path = repo / "token.txt"
    if not tok_path.exists():
        run([sys.executable, "tools/gp_issue_license.py", "--email", args.email], stdout=tok_path.open("w"))

    # 3) Build buyer ZIP unless provided
    if not args.zip:
        run([sys.executable, "tools/gp_pack_buyer.py", "--email", args.email, "--token-file", str(tok_path)])
        zip_path = sorted(buyer.glob("GitPal-Pro-*.zip"))[-1]
    else:
        zip_path = Path(args.zip)
    if not zip_path.exists():
        raise SystemExit("❌ Buyer ZIP not found")

    # 4) Inspect ZIP names (no secrets)
    with zipfile.ZipFile(zip_path, "r") as z:
        names = z.namelist()
    assert any(re.match(rf"{WHEEL_GLOB.replace('*', '.*')}$", Path(n).name) for n in names), "Wheel missing in ZIP"
    banned = ("gp_issuer_private.pem", "licensor_keys/", "buyer_builds/", "token.txt")
    assert not any(any(b in n for b in banned) for n in names), f"❌ ZIP leaks private assets: {names}"

    # 5) Create clean venv, install wheel from ZIP, run CLI help
    tmp = Path(tempfile.mkdtemp(prefix="gp_release_"))
    try:
        # extract wheel + config for a sandboxed install
        with zipfile.ZipFile(zip_path, "r") as z:
            for n in names:
                z.extract(n, tmp)
        whl = find_one(tmp, WHEEL_GLOB)
        cfg = tmp / "config.toml"

        # sandbox config: XDG points inside tmp
        xdg = tmp / "xdg"
        (xdg / "git-pal").mkdir(parents=True, exist_ok=True)
        (xdg / "git-pal" / "config.toml").write_text(cfg.read_text(), encoding="utf-8")
        env = os.environ.copy()
        env["XDG_CONFIG_HOME"] = str(xdg)

        # venv
        venv = tmp / ".venv"
        run([sys.executable, "-m", "venv", str(venv)])
        py = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        pip = venv / ("Scripts/pip.exe" if os.name == "nt" else "bin/pip")
        run([str(py), "-m", "pip", "install", "--upgrade", "pip"])
        run([str(pip), "install", str(whl)])

        # Verify license and write receipt (offline by design - no network calls)
        offline_probe = f"""
from pathlib import Path
from git_pal.licensing import verify_license, write_receipt
from git_pal.config import get_config_path
lic = verify_license()
print(f"License verified: {{lic.sub}}, features={{lic.features}}")
# Write receipt like the TUI does on first run
cfg_dir = get_config_path().parent
write_receipt(getattr(lic, 'purchase_id', None), lic.sub, cfg_dir)
print(f"Receipt written to {{cfg_dir}}")
"""
        run([str(py), "-c", offline_probe], env=env)

        # CLI help should succeed (non-interactive)
        run([str(py), "-c", "import subprocess; subprocess.check_call(['git-pal','--help'])"], env=env)

        # receipt.json created?
        receipt = xdg / "git-pal" / "receipt.json"
        assert receipt.exists(), "receipt.json not created"
        data = json.loads(receipt.read_text())
        for key in ("sub_hint","purchase_id","machine","ts"):
            assert key in data, f"receipt key missing: {key}"
        assert "@" not in data["sub_hint"], "sub_hint must be obfuscated"

        # EULA included in sdist?
        with tarfile.open(sdist, "r:gz") as tar:
            names = tar.getnames()
        assert any(n.endswith("EULA.txt") for n in names), "EULA.txt not found in sdist"

        print("✅ Release sanity passed.")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    main()
