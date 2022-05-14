# Dict Search
This module provides an interface to search over a list of dictionaries in a
similar style to mongo db

```python  
values = DictSearch().dict_search(
        data, {
        "$or": 
            [
                {"liab": {"non_cur": {"a": {"$gt": 10000}}}}, 
                {"assets": {"curr": {"a": 1}}},
            ]
        }
    )
```

Low level operators
High level operators (use a container not a dict)
Array Operators 
Match operators (if search key dict -> used as high levle operator, else  used as array operator)
Array Selectors