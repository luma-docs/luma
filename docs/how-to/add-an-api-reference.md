# Add an API reference

API references are automatically generated and document specific Python functions and 
classes.

To add a reference, specify a `ref` in `luma.yaml`.

```yaml
name: mypackage
navigation:
  # Example of referencing a function
  - ref: luma.examples.fib
  # Example of referencing a class
  - ref: luma.examples.Account
```

Luma places references in the `reference/` subpath. For example, you can access the
reference for `fib` at mypackage.luma-docs.org/reference/luma.examples.fib.
