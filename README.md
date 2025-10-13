<div align="center">
<img src="docs/combined.svg" alt="Luma Logo" width="300px">
<hr>

### **✨ A better way to write Python documentation✨**
[![PyPI version](https://badge.fury.io/py/luma-docs.svg)](https://badge.fury.io/py/luma-docs)
![versions](https://img.shields.io/pypi/pyversions/luma-docs.svg)
[![Documentation](https://img.shields.io/badge/Documentation%20-Introduction%20-%20%23007ec6)](https://luma-docs.org/)
[![Discord](https://img.shields.io/discord/1335378384754311294?color=%237289da&label=Discord)](https://discord.gg/YJmCGJp6)
</div>

---

Luma is a better way to write Python documentation. It's a modern replacement for 
[Sphinx](https://www.sphinx-doc.org/en/master/) that's built on the same tooling Stripe
uses for their documentation.

Here are the key benefits of Luma:
- **Easy to use**. Markdown-native and simple to configure. Avoid Sphinx’s obscure 
  syntax.
- **Iterate rapidly**. Built-in development server and publishing. No need to set up 
  hosting.
- **Built for Python**. Automatically generate function and class references with 
  seamless cross-referencing.

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
