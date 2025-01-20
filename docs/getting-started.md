---
title: Getting started
---

# Luma: Modern Python documentation

Luma is better way to document your Python library. It's a modern replacement for 
[Sphinx](https://www.sphinx-doc.org/en/master/).

Here are some of the key benefits of Luma:
- **Easier to use**. Markdown-native and easy to configure. Avoid Sphinx’s steep learning curve. 
- Iterate faster. Development server. No need to manually rebuild. 
- *Python-specific functionality*. Automatic function and class reference generation
  and easy cross-referencing.


## Installing Luma

To install Luma, run the following command:

```bash
pip install luma-docs
```

##  Quickstart

### Create a new Luma project

Once you've installed Luma, run the `init` command, and answer the prompts:

```bash
luma init
```

After running the command, you should see a `docs/` folder in your current working 
directory.

### Run the development server

`cd` into the `docs/` folder, and run the `dev` command to start the local development 
server. Then, open the printed address in your browser. The address is usually 
`http://localhost:3000/`.

```bash
cd docs
luma dev
```

### Publish your documentation

Hit `Ctrl + C` to stop the development server. Then, run the `deploy` command to deploy
your documentation.

```
luma deploy
```

After a minute, your documentation will be accessible on the Internet at an address
like `TODO`.
