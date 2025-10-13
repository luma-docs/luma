---
title: Quickstart
---

# Luma: Next-gen Python documentation

Luma is a better way to write Python documentation. It's a modern replacement for
[Sphinx](https://www.sphinx-doc.org/en/master/) that's built on the same [tooling
Stripe uses](https://markdoc.dev/) for their documentation.

Key benefits of Luma:

- **Markdown-native**. Avoid Sphinx’s obscure syntax.
- **Built for Python**. API generation and cross-referencing work out-of-the-box.
- **Live rendering**. Preview your changes as you write.

## Getting started

### Install Luma

To install Luma, install the package from PyPI:

```bash
pip install luma-docs
```

### Create a new Luma project

Once you've installed Luma, run the `init` command, and answer the prompts:

```bash
luma init
```

After running the command, you'll see a `docs/` folder in your current working
directory.

### Run the development server

`cd` into the `docs/` folder, and run the `dev` command to start the local development
server. Then, open the printed address in your browser. The address is usually
`http://localhost:3000/`.

```bash
cd docs
luma dev
```

Hit `Ctrl + C` to stop the development server.

### Publish your documentation

Join [our Discord](https://discord.gg/e7TP6nqCS5) to acquire an API key. Then, run the `deploy` command to publish
your documentation.

```
luma deploy
```

After a minute, your documentation will be accessible at
`https://{your-package}.luma-docs.org`.
