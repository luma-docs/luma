# Migrating to 2.x

Compared with the 1.0 release, there were relatively few backwards
incompatible changes, but there are still a few issues to be aware of with
this major release.

For more details on the changes in this release including new APIs, links
to the relevant GitHub issues and some of the bug fixes, read Cory's [blog](https://lukasa.co.uk/2013/09/Requests_20/)
on the subject.

## API Changes

- There were a couple changes to how Requests handles exceptions.
  `RequestException` is now a subclass of `IOError` rather than
  `RuntimeError` as that more accurately categorizes the type of error.
  In addition, an invalid URL escape sequence now raises a subclass of
  `RequestException` rather than a `ValueError`.

  ```python
  requests.get('http://%zz/')   # raises requests.exceptions.InvalidURL
  ```

  Lastly, `httplib.IncompleteRead` exceptions caused by incorrect chunked
  encoding will now raise a Requests `ChunkedEncodingError` instead.

- The proxy API has changed slightly. The scheme for a proxy URL is now
  required.

  ```python
  proxies = {
  "http": "10.10.1.10:3128",    # use http://10.10.1.10:3128 instead
  }

  # In requests 1.x, this was legal, in requests 2.x,
  #  this raises requests.exceptions.MissingSchema
  requests.get("http://example.org", proxies=proxies)
  ```

## Behavioural Changes

- Keys in the `headers` dictionary are now native strings on all Python
  versions, i.e. bytestrings on Python 2 and unicode on Python 3. If the
  keys are not native strings (unicode on Python 2 or bytestrings on Python 3)
  they will be converted to the native string type assuming UTF-8 encoding.

- Values in the `headers` dictionary should always be strings. This has
  been the project's position since before 1.0 but a recent change
  (since version 2.11.0) enforces this more strictly. It's advised to avoid
  passing header values as unicode when possible.
