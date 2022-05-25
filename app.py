from flask import Flask, redirect
from flask import render_template
from flask import request
from flask import session
import database as db
import authentication
import logging
import ordermanagement as om

app = Flask(__name__)

# Set the secret key to some random bytes.
# Keep this really secret!
app.secret_key = b's@g@d@c0ff33!'

logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.INFO)

@app.route('/')
def index():
    return render_template('index.html', page="Index")

@app.route('/products')
def products():
    product_list = db.get_products()
    return render_template('products.html', page="Products", product_list=product_list)

@app.route('/productdetails')
def productdetails():
    code = request.args.get('code', '')
    product = db.get_product(int(code))

    return render_template('productdetails.html', code=code, product=product)

@app.route('/branches')
def branches():
    branch_list = db.get_branches()
    return render_template('branches.html', page="Branches", branch_list=branch_list)

@app.route('/branchdetails')
def branchdetails():
    code = request.args.get('code', '')
    branch = db.get_branch(int(code))

    return render_template('branchdetails.html', code=code, branch=branch)

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html', page="About Us")

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/auth', methods = ['GET', 'POST'])
def auth():
    username = request.form.get('username')
    password = request.form.get('password')

    is_successful, user = authentication.login(username, password)
    app.logger.info('%s', is_successful)
    if(is_successful):
        session["user"] = user
        return redirect('/')
    else:
        error = "Invalid username or password. Please try again."
        return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop("user",None)
    session.pop("cart",None)
    return redirect('/')

@app.route('/addtocart')
def addtocart():
    code = request.args.get('code', '')
    product = db.get_product(int(code))
    item=dict()
    # A click to add a product translates to a
    # quantity of 1 for now

    item["qty"] = 1
    item["name"] = product["name"]
    item["subtotal"] = product["price"]*item["qty"]
    item["code"] = code

    if(session.get("cart") is None):
        session["cart"]={}

    cart = session["cart"]
    cart[code]=item
    session["cart"]=cart
    return redirect('/cart')

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/updatecartitem', methods = ['GET', 'POST'])
def updatecartitem():
    qty = request.form.get("qty")
    code = request.form.get("code")
    update = request.form.get("Update")
    delete = request.form.get("Delete")
    product = db.get_product(int(code))
    item = dict()

    if update == 'Update':
        item["qty"] = int(qty)
        item["name"] = product["name"]
        item["subtotal"] = product["price"]*item["qty"]
        item["code"] = code

        cart = session["cart"]
        cart[code] = item
        session["cart"] = cart

        return redirect('/cart')

    elif delete == 'Delete':
        cart = session["cart"]
        cart.pop(code, None)
        session["cart"] = cart

        return redirect('/cart')

@app.route('/checkout')
def checkout():
    # clear cart in session memory upon checkout
    om.create_order_from_cart()
    session.pop("cart",None)
    return redirect('/ordercomplete')

@app.route('/ordercomplete')
def ordercomplete():
    return render_template('ordercomplete.html')

@app.route('/changepassword')
def changepassword():
    return render_template('changepassword.html')

@app.route('/changepass', methods = ['GET', 'POST'])
def changepass():
    curr_password = request.form.get("curr_password")
    new_password = request.form.get("new_password")
    new_password2 = request.form.get("new_password2")
    user = session["user"]
    username = user["username"]
    temp_user =  db.get_user(username)
    password = temp_user["password"]

    if(password == curr_password):
        if(new_password == new_password2):
            db.update_pass(username,new_password)
            success = "Password changed successfully."
            return render_template('changepassword.html',success=success)
        else:
            error2 = "New passwords don't match."
            return render_template('changepassword.html',error2=error2)
    else:
        error1 = "Password is incorrect."
        return render_template('changepassword.html',error1=error1)

@app.route('/pastorders')
def past_orders():
    user = session["user"]
    username = user["username"]
    orders = db.get_past_orders(username)
    order = dict()
    if(session.get("order") is None):
	    session["order"] = {}

    for o in range(len(orders)):
        temp_order = orders[o]
        temp_details = temp_order["details"]

        order1 = temp_details
        order["qty"] = temp_details["qty"]
        order["name"] = temp_details["name"]
        order["subtotal"] = temp_details["subtotal"]

        past_orders = session["order"]
        past_orders[o] = order
        session["order"] = past_orders
    return render_template('pastorders.html',order1=order1)
