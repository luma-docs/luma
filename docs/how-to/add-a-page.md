# Add a page

Pages are for general prose in your documentation, used to cover topics beyond 
auto-generated API references.

To add a page, create a Markdown file in your `docs/` folder.

```bash
touch docs/example.md
```

Then, specify the `path` and `title` in `luma.yaml`.

```yaml
name: mypackage
navigation:
  # Paths are relative to the `docs/` folder.
  - path: example.md
    title: My page
```

You can also specify files in subdirectories.

```yaml
name: mypackage
navigation:
  - path: my-folder/nested-example.md
    title: My nested page
```
