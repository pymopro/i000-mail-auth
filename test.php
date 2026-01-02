function verifySignature($uid, $email, $ts, $sig, $clientSecret) {
    $payload = "$uid:" . strtolower($email) . ":$ts";
    $expectedSig = hash_hmac('sha256', $payload, $clientSecret);
    
    return hash_equals($expectedSig, $sig);
}
