# Group pages in the sidenav

Sections allow you to group related pages and API references in the sidebar.

To add a section, specify a `section` in `luma.yaml`.

```yaml
name: mypackage
navigation:
  - section: My section
    contents:
      # You can include both pages and API references in a section.
      - example.md
      - reference: Example reference
        apis:
          - luma.examples.Account
```
