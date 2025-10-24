# Tabs

Tabs allow you to organize content into multiple panels, where only one panel is visible at a time.

## Example

{% tabs %}

{% tab name="Parquet" %}

This is an example of reading Parquet files.

```python
import pandas as pd

df = pd.read_parquet("data.parquet")
```

{% /tab %}

{% tab name="JSON" %}

This is an example of reading JSON files.

```python
import pandas as pd

df = pd.read_json("data.json")
```

{% /tab %}

{% tab name="CSV" %}

This is an example of reading CSV files.

```python
import pandas as pd

df = pd.read_csv("data.csv")
```

{% /tab %}

{% /tabs %}

---

````markdown
{% tabs %}

{% tab name="Parquet" %}

This is an example of reading Parquet files.

```python
import pandas as pd

df = pd.read_parquet("data.parquet")
```

{% /tab %}

{% tab name="JSON" %}

This is an example of reading JSON files.

```python
import pandas as pd

df = pd.read_json("data.json")
```

{% /tab %}

{% tab name="CSV" %}

This is an example of reading CSV files.

```python
import pandas as pd

df = pd.read_csv("data.csv")
```

{% /tab %}

{% /tabs %}
````
