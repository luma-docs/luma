# Status codes

The `codes` object defines a mapping from common names for HTTP statuses
to their numerical codes, accessible either as attributes or as dictionary
items.

```python
>>> import requests
>>> requests.codes['temporary_redirect']
307
>>> requests.codes.teapot
418
>>> requests.codes['\o/']
200
```

Some codes have multiple names, and both upper- and lower-case versions of
the names are allowed. For example, `codes.ok`, `codes.OK`, and
`codes.okay` all correspond to the HTTP status code 200.
