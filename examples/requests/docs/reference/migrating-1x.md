# Migrating to 1.x

This section details the main differences between 0.x and 1.x and is meant
to ease the pain of upgrading.

## API Changes

- `Response.json` is now a callable and not a property of a response.

  ```python
  import requests
  r = requests.get('https://api.github.com/events')
  r.json()   # This *call* raises an exception if JSON decoding fails
  ```

- The `Session` API has changed. Sessions objects no longer take parameters.
  `Session` is also now capitalized, but it can still be
  instantiated with a lowercase `session` for backwards compatibility.

  ```
  s = requests.Session()    # formerly, session took parameters
  s.auth = auth
  s.headers.update(headers)
  r = s.get('https://httpbin.org/headers')
  ```

- All request hooks have been removed except 'response'.

- Authentication helpers have been broken out into separate modules. See
  [requests-oauthlib](https://github.com/requests/requests-oauthlib) and [requests-kerberos](https://github.com/requests/requests-kerberos).

- The parameter for streaming requests was changed from `prefetch` to
  `stream` and the logic was inverted. In addition, `stream` is now
  required for raw response reading.

  ```python
  # in 0.x, passing prefetch=False would accomplish the same thing
  r = requests.get('https://api.github.com/events', stream=True)
  for chunk in r.iter_content(8192):
      ...
  ```

- The `config` parameter to the requests method has been removed. Some of
  these options are now configured on a `Session` such as keep-alive and
  maximum number of redirects. The verbosity option should be handled by
  configuring logging.

  ```python
  import requests
  import logging

  # Enabling debugging at http.client level (requests->urllib3->http.client)
  # you will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
  # the only thing missing will be the response.body which is not logged.
  try: # for Python 3
      from http.client import HTTPConnection
  except ImportError:
      from httplib import HTTPConnection
  HTTPConnection.debuglevel = 1

  logging.basicConfig() # you need to initialize logging, otherwise you will not see anything from requests
  logging.getLogger().setLevel(logging.DEBUG)
  requests_log = logging.getLogger("urllib3")
  requests_log.setLevel(logging.DEBUG)
  requests_log.propagate = True

  requests.get('https://httpbin.org/headers')
  ```

## Licensing

One key difference that has nothing to do with the API is a change in the
license from the [ISC](https://opensource.org/licenses/ISC) license to the [Apache 2.0](https://opensource.org/licenses/Apache-2.0) license. The Apache 2.0
license ensures that contributions to Requests are also covered by the Apache
2.0 license.
