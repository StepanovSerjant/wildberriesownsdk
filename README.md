## wildberriesownsdk (own SDK for Wildberries)

[![PyPI version](https://badge.fury.io/py/wildberriesownsdk.svg)](https://pypi.python.org/pypi/wildberriesownsdk)
[![Supported versions](https://img.shields.io/pypi/pyversions/wildberriesownsdk.svg)](https://pypi.python.org/pypi/wildberriesownsdk)
[![License](https://img.shields.io/github/license/StepanovSerjant/wildberriesownsdk)](https://github.com/StepanovSerjant/wildberriesownsdk/blob/master/LICENSE)
[![Doc](https://readthedocs.org/projects/wildberriesownsdk/badge/?version=latest&style=flat)](https://wildberriesownsdk.readthedocs.io)

Python client and framework for Wildberries marketplace. *NOT OFFICIAL*

📚 [Documentation Wildberries API](https://dev.wildberries.ru/docs/openapi/api-information)

### Quickstart

1. **Install wildberriesownsdk.**

```shell
pip install wildberriesownsdk 
```

2. You are ready to init your first connector

```python
from wildberriesownsdk import WBAPIConnector


# init connector
connector = WBAPIConnector(api_key="somekey")

# upload image by path
connector.upload_image_to_article(
    article="somewbarticle",
    file="somedir/somefile.png",
    image_number=1, 
)

# or foo
connector.foo()
```

3. Also you can use default WB API action behavior with overriding or not. For example, this sdk does not implement ... action.
But give you ability to implement it easily :)

```python
```
