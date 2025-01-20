# Add a section

Sections allow you to group related pages and API references in the sidebar.

To add a section, specify a `section` in `luma.yaml`.

```
name: mypackage
navigation:
  - section: My section
    contents:
      # You can include both pages and API references in a section.
      - path: example.md
        title: My page
      - ref: luma.examples.Account
```

