# reference: https://fastapi.tiangolo.com/tutorial/body/

from fastapi import FastAPI
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


app = FastAPI()


# @app.post("/items/")
# async def create_item(item: Item):
#     return item


""" With just that Python type declaration, FastAPI will:

Read the body of the request as JSON.
Convert the corresponding types (if needed).
Validate the data.
If the data is invalid, it will return a nice and clear error, indicating exactly where and what was the incorrect data.
Give you the received data in the parameter item.
As you declared it in the function to be of type Item, you will also have all the editor support (completion, etc) for all of the attributes 
and their types. Generate JSON Schema definitions for your model, you can also use them anywhere else you like if it makes sense for your project.
Those schemas will be part of the generated OpenAPI schema, and used by the automatic documentation UIs."""


@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict
