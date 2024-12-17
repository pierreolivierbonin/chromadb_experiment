from enum import Enum

from fastapi import FastAPI


app = FastAPI()


# requirements:
# 1) having a decorated POST operation function to send data to the vector database,
# 2) having a decorated GET operation function to fetch data from the vector database

"""
Available operation decorated functions:
@app.post()
@app.put()
@app.deleted()
@app.options()
@app.head()
@app.patch()
@app.trace()
Reference: https://fastapi.tiangolo.com/tutorial/first-steps/#define-a-path-operation-decorator
"""


@app.get("/")  # this is our "path operation function"
async def root():
    return {"message": "Hollow World..."}


# type is automatically checked and data validation is performed behind the scene by Pydantic
@app.get("/items/{item_id}")  # you can declare path "parameters" or "variables" like so
async def read_item(item_id: int):
    return {"item_id": item_id}


# path operations are evaluated in order, so you need to make sure the path for '/users/me' is declared beofre 'users/{user_id}'
# otherwise the path for '/users/{user_id} would match also for '/users/me'


# also, you cannot define the same path operation twice. If so, the first one will prevail.
@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}


@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}


# If you have a path operation that receives a path parameter,
# but you want the possible valid path parameter values to be predefined (i.e. a limited number of classes that will not change),
# you can use a standard Python Enum
class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


@app.get("/models/{model_name}")
async def get_model(
    model_name: ModelName,  # we use type annotation to validate it is the expected data type
):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}
    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}
    return {"model_name": model_name, "message": "have some residuals for desert"}


"""Query Parameters: When you declare other function parameters that are not part of the path parameters, 
they are automatically interpreted as "query" parameters.

The query is the set of key-value pairs that go after the ? in a URL, separated by & characters.

For example, in the URL, that an example would be: http://127.0.0.1:8000/items/?skip=0&limit=10
"""

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]


"""
As query parameters are not a fixed part of a path, they can be optional and can have default values.

In the example above they have default values of skip=0 and limit=10.

Can also set it to a default value of None like below...
"""


@app.get("/items/{item_id}")
async def read_item(item_id: str, q: str | None = None):
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}


"""You can declare multiple path parameters and query parameters at the same time, FastAPI knows which is which.

And you don't have to declare them in any specific order.

They will be detected by name:"""


@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int, item_id: str, q: str | None = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item


""" Required parameters vs optional parameters: works just like Python always works, i.e.
when you assign a default value, then the parameter is optional. Otherwise, it is required."""


@app.get("/items/{item_id}")
async def read_user_item(item_id: str, needy: str):
    item = {"item_id": item_id, "needy": needy}
    return item


# http://127.0.0.1:8000/items/foo-item will produce an error because you didn't add the required parameter 'needy'
# this will work: http://127.0.0.1:8000/items/foo-item?needy=sooooneedy
