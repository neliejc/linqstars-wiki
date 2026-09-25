# FTPS certificate chain

`perfectssl.pem` is the public PerfectSSL intermediate certificate issued by
DigiCert Global Root G2. It contains no private key or login credentials.

Source: https://cacerts.digicert.com/PerfectSSL.crt (DER, converted to PEM).
Verified against the local trusted CA store with `openssl verify`.

The FTPS server at `vserver119.axc.eu:21` supplied only its leaf certificate
when checked on 2026-09-25. The deployment step supplies the missing intermediate
using `NODE_EXTRA_CA_CERTS`; `security: strict` remains enabled. A Node TLS
handshake verified both the certificate and hostname with this configuration.

Ask the hosting provider to configure the complete FTPS certificate chain.
Once that is corrected, this workaround can be removed after verifying a
connection without the extra certificate.
