# Requests: HTTP for Humans™

Release v2.32.5. ([Installation](/user/install))

![Requests Downloads Per Month Badge](https://static.pepy.tech/badge/requests/month)
![License Badge](https://img.shields.io/pypi/l/requests.svg)
![Wheel Support Badge](https://img.shields.io/pypi/wheel/requests.svg)
![Python Version Support Badge](https://img.shields.io/pypi/pyversions/requests.svg)

**Requests** is an elegant and simple HTTP library for Python, built for human beings.

---

**Behold, the power of Requests**:

```python
>>> r = requests.get('https://api.github.com/user', auth=('user', 'pass'))
>>> r.status_code
200
>>> r.headers['content-type']
'application/json; charset=utf8'
>>> r.encoding
'utf-8'
>>> r.text
'{"type":"User"...'
>>> r.json()
{'private_gists': 419, 'total_private_repos': 77, ...}
```

See [similar code, sans Requests](https://gist.github.com/973705).

**Requests** allows you to send HTTP/1.1 requests extremely easily.
There's no need to manually add query strings to your
URLs, or to form-encode your POST data. Keep-alive and HTTP connection pooling
are 100% automatic, thanks to [urllib3](https://github.com/urllib3/urllib3).

<!-- ## Beloved Features

Requests is ready for today's web.

- Keep-Alive & Connection Pooling
- International Domains and URLs
- Sessions with Cookie Persistence
- Browser-style SSL Verification
- Automatic Content Decoding
- Basic/Digest Authentication
- Elegant Key/Value Cookies
- Automatic Decompression
- Unicode Response Bodies
- HTTP(S) Proxy Support
- Multipart File Uploads
- Streaming Downloads
- Connection Timeouts
- Chunked Requests
- `.netrc` Support

Requests officially supports Python 3.9+, and runs great on PyPy. -->
