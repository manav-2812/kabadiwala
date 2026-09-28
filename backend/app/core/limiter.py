from slowapi import Limiter
from slowapi.util import get_remote_address

# §1.6: Shared rate limiter for API endpoints
limiter = Limiter(key_func=get_remote_address)
