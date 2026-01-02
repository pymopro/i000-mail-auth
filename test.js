const crypto = require('crypto');

function verifySignature(query, clientSecret) {
    const { uid, email, ts, sig } = query;
    const payload = `${uid}:${email.toLowerCase()}:${ts}`;
    const expectedSig = crypto.createHmac('sha256', clientSecret).update(payload).digest('hex');
    
    return expectedSig === sig;
}
