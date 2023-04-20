from fastapi import FastAPI, HTTPException
from typing import List
from pydantic import BaseModel
import sqlite3
from fastapi.middleware.cors import CORSMiddleware

# define the cart item model
class CartItem(BaseModel):
 
    product_id: int
    quantity: int
    name: str
    price: float
    type: str
    picture_url: str
    description: str
    category: str
    gender: str


# define the cart model
class Cart(BaseModel):
    user_id: str
    items: List[CartItem]

# create a connection to the cart database
conn = sqlite3.connect("cart.db")
cur = conn.cursor()

# create the cart table if it doesn't already exist
cur.execute("CREATE TABLE IF NOT EXISTS Cart (product_id INTEGER, quantity INTEGER)")
origins = ["*"]  # Replace this with the list of allowed origins

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.post("/cart/add-item/{user_id}")
def add_item_to_cart(user_id: int, cart_item: CartItem):
    # create a new database connection
    conn = sqlite3.connect("cart.db")
    with conn:
        # check if the item is already in the cart
        cur = conn.cursor()
        cur.execute("SELECT Product_quantity FROM Cart WHERE User_id=? AND Product_id=?", (user_id, cart_item.product_id,))
        row = cur.fetchone()
        if row is None:
            # if the item is not in the cart, insert a new row
          cur.execute("INSERT INTO Cart (User_id, Product_id, Product_name, Product_price, Product_quantity, Product_type, Product_picture_url, Product_description, Product_category, Product_gender) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (user_id, cart_item.product_id, cart_item.name, cart_item.price, cart_item.quantity, cart_item.type, cart_item.picture_url, cart_item.description, cart_item.category, cart_item.gender))
        else:
            # if the item is already in the cart, update the quantity
            cur.execute("UPDATE Cart SET Product_quantity=? WHERE User_id=? AND Product_id=?", (row[0]+cart_item.quantity, user_id, cart_item.product_id))
    # close the database connection
    conn.close()
    return {"message": "Item added to cart."}

@app.delete("/cart/remove-item/{product_id}/{user_id}")
def remove_item_from_cart(product_id: int, user_id: int):
    conn = sqlite3.connect("cart.db")
    with conn:
        # check if the item is already in the cart
        cur = conn.cursor()
        # check if the item is in the cart for the given user
        cur.execute("SELECT Product_quantity FROM Cart WHERE Product_id=? and user_id=?", (product_id, user_id))
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Item not found in cart.")
        # if the item is in the cart for the given user, delete the row
        cur.execute("DELETE FROM Cart WHERE Product_id=? and user_id=?", (product_id, user_id))
        cur.close()
    return {"message": "Item removed from cart."}

@app.delete("/cart/remove/{user_id}")
def remove_items_from_cart(user_id: int):
    conn = sqlite3.connect("cart.db")
    with conn:
        # Check if the user has any items in the cart
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM Cart WHERE user_id=?", (user_id,))
        count = cur.fetchone()[0]
        if count == 0:
            raise HTTPException(status_code=404, detail="Cart is empty.")
        # Delete all rows in Cart table for given user ID
        cur.execute("DELETE FROM Cart WHERE user_id=?", (user_id,))
        cur.close()
    return {"message": "All items removed from cart."}




@app.get("/cart/{user_id}")
def get_cart(user_id: int):
    # create a new database connection
    conn = sqlite3.connect("cart.db")
    with conn:
        cur = conn.cursor()
        # get all rows from the cart table for the specified user
        cur.execute("SELECT * FROM Cart WHERE User_id=?", (user_id,))
        rows = cur.fetchall()
        products = []
        for row in rows:
            products.append({"id": row[1], "name": row[2], "quantity": row[4], "price": row[3],"type":row[5],"picture_url":row[6],"description":row[7],"category":row[8]})
            
        return products


# checkout cart
