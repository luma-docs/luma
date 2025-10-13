# Add a page

Pages are for general prose in your documentation, used to cover topics beyond
auto-generated API references.

To add a page, create a Markdown file in your `docs/` folder.

```bash
touch docs/example.md
```

Then, specify the path in `luma.yaml`.

```yaml
name: mypackage
navigation:
  # Paths are relative to the `docs/` folder.
  - example.md
```

You can also specify files in subdirectories.

```yaml
name: mypackage
navigation:
  - my-folder/nested-example.md
```

By default, Luma uses the first heading as the page's title in the sidenav. To override
the title, specify a title in the page's frontmatter:

```markdown
---
title: My custom title
---

# Page heading

...
```
