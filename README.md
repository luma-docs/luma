<div align="center">
<hr>

### **✨ Luma: Next-gen Python documentation✨**

[![PyPI version](https://badge.fury.io/py/luma-docs.svg)](https://badge.fury.io/py/luma-docs)
![versions](https://img.shields.io/pypi/pyversions/luma-docs.svg)
[![Documentation](https://img.shields.io/badge/Documentation%20-Introduction%20-%20%23007ec6)](https://luma-docs.org/)
[![Discord](https://img.shields.io/discord/1335378384754311294?color=%237289da&label=Discord)](https://discord.gg/YJmCGJp6)

</div>

---

<img width="1624" height="954" alt="image" src="https://github.com/user-attachments/assets/99c6dc32-dd97-4cd4-b298-16d5969a79e3" />

Luma is better way to write Python documentation. It's a modern replacement for
[Sphinx](https://www.sphinx-doc.org/en/master/) that's built on the same [tooling
Stripe uses](https://markdoc.dev/) for their documentation.

Key benefits of Luma:

- **Markdown-native**: Avoid Sphinx’s obscure syntax.
- **Built for Python**: API generation and cross-referencing work out-of-the-box.
- **Live rendering**: Preview your changes as you write.

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

Join [our Discord](https://discord.gg/YJmCGJp6) to acquire an API key. Then, run the
`deploy` command to publish your documentation.

```
luma deploy
```

After a minute, your documentation will be accessible at
`https://{your-package}.luma-docs.org`.
