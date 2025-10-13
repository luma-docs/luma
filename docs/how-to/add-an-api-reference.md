# Add an API reference

API references are automatically generated and document specific Python functions and
classes.

To add a reference, specify a `reference` in `luma.yaml` and list the APIs you want to
include in that reference.

```yaml
name: mypackage
navigation:
  - reference: Example reference
    apis:
      # Example of referencing a function
      - luma.examples.fib
      # Example of referencing a class
      - luma.examples.Account
```
