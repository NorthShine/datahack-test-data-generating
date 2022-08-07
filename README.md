# Fake data generator

This package generates fake sql-like format data from predefined schema.
Data schema is defined using dataclasses. 

# Installation

`
python -m pip install no_spark_in_my_home
`

# Usage

```python
from datetime import datetime
from dataclasses import dataclass
from no_spark_in_my_home.src.generator import FakeDataGenerator


@dataclass
class Dataclass:
    item_id: int
    title: str
    date: datetime
    number: int
    
gen = FakeDataGenerator(
    Dataclass,
    limit=5,
)
spark_dataframe = gen.load()
spark_dataframe.show()
```

### ```FakeDataGenerator``` params:

- ```model```  - dataclass
- ```limit``` - number of records
- ```mask_per_field``` - dict with masks per field. 
Example: ```FakeDataGenerator(..., mask_per_field={"title": "A#### ###."})```
- ```range_per_field``` - dict with ranges per field. Example: ```FakeDataGenerator(..., range_per_field={"number": {"range": range(1, 10)}})```
- ```maxlength_per_field``` - dict with maxlengths for strings per field. Example: ```FakeDataGenerator(..., maxlength_per_field={"field_name": "title", "maxlength": 100, "fixed": True})```. ```fixed=True``` will generate strings with fixed length. ```fixed=False``` will generate strings with non-fixed, but limited lengths.
- ```config``` - path to config. Config should be yaml-formatted.
- ```lang``` - locale. Default - "en"
- ```foreign_keys``` - list of dicts that describes relations. Example: ```FakeDataGenerator(..., foreign_keys=[{"self_field": "item_id", "other_field": "another_item_id", "other_model": OtherDataclass, "other_data": other_dataclass_gen.load(as_dicts=True)}])```

### ```load``` params:

- ```where_clause``` - string with where-clause for post-filtering. Example: ```load(..., where_clause="item_id > 5 and number = 10")```
- ```as_json``` - if True returns generated data as json
- ```as_dicts``` - if True returns generated data as list of dicts

# Building your own package version

In case you want to build your own package version you should follow
this [guide](https://python-packaging-tutorial.readthedocs.io/en/latest/setup_py.html).

And then just build a wheel and install it.

# Making and publishing a new release

1. Update release version in pyproject.toml and setup.py
2. Build package with `python -m build`
3. Publish package with `twine upload dist/*`
