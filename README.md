# Fake data generator

This package generates fake sql-like format data from predefined schema.
Data schema is defined using dataclasses. 

# Installation

`
python -m pip install no_spark_in_my_home
`

# Usage

```python
from no_spark_in_my_home.src.generator import FakeDataGenerator
# your code
```

# Building your own package version

In case you want to build your own package version you should follow
this [guide](https://python-packaging-tutorial.readthedocs.io/en/latest/setup_py.html).

And then just build a wheel and install it.