#!/usr/bin/env python3
import argparse
import time
import uuid
import jwt
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--email", required=True)
    ap.add_argument("--days", type=int, default=365)
    ap.add_argument("--features", default="pro")
    ap.add_argument("--private-key", default="licensor_keys/gp_issuer_private.pem")
    ap.add_argument("--issuer", default="git-pal-licensing")
    args = ap.parse_args()

    priv = Path(args.private_key).read_text()
    now = int(time.time())
    payload = {
        "sub": args.email,
        "iss": args.issuer,
        "iat": now,
        "nbf": now,
        "exp": now + 86400*args.days,
        "features": [x.strip() for x in args.features.split(",") if x.strip()],
        "purchase_id": str(uuid.uuid4()),
    }
    print(jwt.encode(payload, priv, algorithm="RS256"))

if __name__ == "__main__":
    main()
