import datetime
import hashlib
import hmac
import urllib.parse
from typing import Dict, Optional

class AWSRequestSigner:
    """AWS Signature Version 4 authentication."""
    
    def __init__(self, access_key: str, secret_key: str, region: str = 'eu-west-1', service: str = 'execute-api'):
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.service = service

    def _sign(self, key: bytes, msg: str) -> bytes:
        """Create HMAC-SHA256 signature."""
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

    def _get_signature_key(self, date_stamp: str) -> bytes:
        """Generate the signing key for AWS signature v4."""
        k_date = self._sign(f'AWS4{self.secret_key}'.encode('utf-8'), date_stamp)
        k_region = self._sign(k_date, self.region)
        k_service = self._sign(k_region, self.service)
        k_signing = self._sign(k_service, 'aws4_request')
        return k_signing

    def _get_canonical_headers(self, headers: Dict[str, str]) -> tuple[str, str]:
        """Create canonical headers and signed headers string."""
        canonical_headers = []
        for key, value in sorted(headers.items()):
            canonical_headers.append(f"{key.lower()}:{value.strip()}")
        return ('\n'.join(canonical_headers) + '\n', ';'.join(sorted(key.lower() for key in headers)))

    def sign_request(
        self,
        method: str,
        url: str,
        data: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """Sign an HTTP request with AWS Signature Version 4."""
        
        # Initialize headers if None
        headers = headers or {}
        
        # Parse URL
        parsed_url = urllib.parse.urlparse(url)
        host = parsed_url.netloc
        canonical_uri = parsed_url.path or '/'
        canonical_querystring = parsed_url.query

        # Prepare dates
        t = datetime.datetime.utcnow()
        amz_date = t.strftime('%Y%m%dT%H%M%SZ')
        date_stamp = t.strftime('%Y%m%d')

        # Add required headers
        headers.update({
            'host': host,
            'x-amz-date': amz_date
        })

        # Get canonical headers
        canonical_headers, signed_headers = self._get_canonical_headers(headers)

        # Create payload hash
        payload_hash = hashlib.sha256((data or '').encode('utf-8')).hexdigest()

        # Create canonical request
        canonical_request = '\n'.join([
            method,
            canonical_uri,
            canonical_querystring,
            canonical_headers,
            signed_headers,
            payload_hash
        ])

        # Create string to sign
        algorithm = 'AWS4-HMAC-SHA256'
        credential_scope = f"{date_stamp}/{self.region}/{self.service}/aws4_request"
        string_to_sign = '\n'.join([
            algorithm,
            amz_date,
            credential_scope,
            hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
        ])

        # Calculate signature
        signing_key = self._get_signature_key(date_stamp)
        signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

        # Create authorization header
        authorization_header = (
            f"{algorithm} Credential={self.access_key}/{credential_scope}, "
            f"SignedHeaders={signed_headers}, Signature={signature}"
        )

        # Add authorization header to request headers
        headers['Authorization'] = authorization_header
        
        return headers
