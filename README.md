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
###Low level operators
These operators provide the basic logic to perform matching queries

Let's assume these documents in order to exemplify these 
````python
data = [
        {
            "name": "Jane",
            "courses": {"A": True},
            "classes": {"maths": 10, "pe": 8, "english": 5},
        },
        {
            "name": "Akira",
            "courses": {"A": True, "B": {"A": True}},
            "classes": {"maths": 7, "pe": 3, "english": 10},
        },
        {
            "name": "Ajame",
            "courses": {"C": True},
            "classes": {"maths": 10, "pe": 10, "english": 6},
        },
    ]
````


####Not equal - $ne:

````python 
    query = {"name": {"$ne": "Ajame"}}
````
````python
{'classes': {'english': 5, 'maths': 10, 'pe': 8},
 'courses': {'A': True},
 'name': 'Jane'}


{'classes': {'english': 10, 'maths': 7, 'pe': 3},
 'courses': {'A': True, 'B': {'A': True}},
 'name': 'Akira'}
````
    
####Less then - $lt:
````python 
    query = {"classes": {"maths": {"$lt": 10}}}
````
````python
{'classes': {'english': 10, 'maths': 7, 'pe': 3},
 'courses': {'A': True, 'B': {'A': True}},
 'name': 'Akira'}
````
    
####Less then or equal - $lte:
````python 
    query = {"classes": {"english": {"$lte": 7}}}
````
````python
{'classes': {'english': 5, 'maths': 10, 'pe': 8},
 'courses': {'A': True},
 'name': 'Jane'}


{'classes': {'english': 6, 'maths': 10, 'pe': 10},
 'courses': {'C': True},
 'name': 'Ajame'}
````
####Greater then - $gt:
````python 
    query = {"classes": {"pe": {"$gt": 3}}}
````
````python
{'classes': {'english': 5, 'maths': 10, 'pe': 8},
 'courses': {'A': True},
 'name': 'Jane'}


{'classes': {'english': 6, 'maths': 10, 'pe': 10},
 'courses': {'C': True},
 'name': 'Ajame'}
````
####Greater then or equal - $gte:
````python 
    query = {"classes": {"english": {"$gte": 6}}}
````
````python
{'classes': {'english': 10, 'maths': 7, 'pe': 3},
 'courses': {'A': True, 'B': {'A': True}},
 'name': 'Akira'}


{'classes': {'english': 6, 'maths': 10, 'pe': 10},
 'courses': {'C': True},
 'name': 'Ajame'}

````
####In - $in:
````python 
    query = {"classes": {"pe": {"$in": [3, 8]}}}
````
````python
{'classes': {'english': 5, 'maths': 10, 'pe': 8},
 'courses': {'A': True},
 'name': 'Jane'}


{'classes': {'english': 10, 'maths': 7, 'pe': 3},
 'courses': {'A': True, 'B': {'A': True}},
 'name': 'Akira'}
````
####Not in - $nin:
````python 
    query = {"classes": {"pe": {"$nin": [3, 8]}}}
````
````python
{'classes': {'english': 6, 'maths': 10, 'pe': 10},
 'courses': {'C': True},
 'name': 'Ajame'}
````
####Regex - $regex:
````python 
    query = {"name": {"$regex": r".*?[jJ].*?"}}
````
````python
{'classes': {'english': 5, 'maths': 10, 'pe': 8},
 'courses': {'A': True},
 'name': 'Jane'}


{'classes': {'english': 6, 'maths': 10, 'pe': 10},
 'courses': {'C': True},
 'name': 'Ajame'}
````
####Expr - $expr:
Through $expr we can pass a function that will be applied to the value we are comparing.

````python 
    query = {"classes": {"$expr": (lambda x: sum(x.values()), 26)}}
````
````python
    {'classes': {'english': 6, 'maths': 10, 'pe': 10},
     'courses': {'C': True},
     'name': 'Ajame'}
````
Any low level operation can be passed too
````python 
    query = {"classes": {"$expr": (lambda x: sum(x.values()), {"$lte": 20})}}
````
````python
    {'classes': {'english': 10, 'maths': 7, 'pe': 3},
    'courses': {'A': True, 'B': {'A': True}},
    'name': 'Akira'}
````

###High level operators
These operators let us aggregate the logic of several low level operators into one
####And - $and:
####Or - $or:
####Xor - $xor:
####Not - $not:

###Logging
This library makes use of the *logging* module. Initialize the class with any
key word argument that would be normally passed to *logging.basicConfig*

```python  
values = DictSearch(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler()]).dict_search(data, query)
```
###match
True if the condition is matched n times or more.

TODO
- tests
- document in tests
- setup.py in detail
- future optional projection in query