import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

products_db = myclient["products"]
order_management_db = myclient["order_management"]


def get_product(code):
    products_coll = products_db["products"]
    product = products_coll.find_one({"code":code})
    return product

def get_products():
    product_list = []
    products_coll = products_db["products"]
    for p in products_coll.find({}):
        product_list.append(p)

    return product_list

def get_branch(code):
    branches_coll = products_db["branches"]
    branches = branches_coll.find_one({"code":code})
    return branches[code]

def get_branches():
    branch_list = []
    branches_coll = products_db["branches"]
    for p in branches_coll.find({}):
        branch_list.append(p)

    return branch_list

def get_user(username):
    customers_coll = order_management_db['customers']
    user=customers_coll.find_one({"username":username})
    return user

def update_pass(username,new_password):
    customers_coll = order_management_db['customers']
    customers_coll.update_one({"username":username}, {"$set":{"password":new_password}})


def create_order(order):
    orders_coll = order_management_db['orders']
    orders_coll.insert(order)

def get_past_orders(username):
    orders_coll = order_management_db['orders']
    order_list = []
    for o in orders_coll.find({"username":username}):
        order_list.append(o)

    return order_list 
