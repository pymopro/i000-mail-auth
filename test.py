import hmac, hashlib

def verify_signature(uid, email, ts, sig, client_secret):
    payload = f"{uid}:{email.lower()}:{ts}"
    expected_sig = hmac.new(
        client_secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_sig, sig)
