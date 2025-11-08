#!/usr/bin/env python3
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def main():
    out = Path("licensor_keys")
    out.mkdir(exist_ok=True)
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    (out/"gp_issuer_private.pem").write_bytes(
        key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    )
    (out/"gp_issuer_public.pem").write_bytes(
        key.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
    )
    print("Wrote licensor_keys/gp_issuer_private.pem and gp_issuer_public.pem")

if __name__ == "__main__":
    main()
