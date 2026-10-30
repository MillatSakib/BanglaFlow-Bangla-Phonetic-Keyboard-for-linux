#!/usr/bin/env bash
# ==============================================================================
# Helper to decrypt Launchpad PGP confirmation email token
# ==============================================================================

echo "Paste the encrypted text block from Launchpad email (starting with -----BEGIN PGP MESSAGE-----"
echo "and ending with -----END PGP MESSAGE-----), then press Ctrl+D:"
echo "----------------------------------------------------------------------------------"

gpg --decrypt

