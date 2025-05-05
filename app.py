from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="OnlineStore"
    )

@app.route('/')
def index():
    return render_template('index.html')

# ====== Users ======
@app.route('/users')
def list_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM User")
    users = cursor.fetchall()
    conn.close()
    return render_template('users.html', users=users)

@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.form['name']
    address = request.form['address']
    email = request.form['email']
    password = request.form['password']
    user_type = request.form['user_type']
    phone = request.form['phone']

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Insert user (AUTO_INCREMENT ID + hashed password)
        cursor.execute("""
            INSERT INTO User (Name, Address, Email, Password, User_type)
            VALUES (%s, %s, %s, SHA2(%s, 256), %s)
        """, (name, address, email, password, user_type))

        user_id = cursor.lastrowid  # Get auto-generated ID

        # Insert phone number
        cursor.execute("INSERT INTO User_PhoneNum (User_ID, UPhone_num) VALUES (%s, %s)", (user_id, phone))

        # Optional: Insert into Customer or Admin table based on user_type
        if user_type == 'Customer':
            cursor.execute("INSERT INTO Customer (User_ID) VALUES (%s)", (user_id,))
        elif user_type == 'Admin':
            cursor.execute("INSERT INTO Admin (User_ID, Admin_role) VALUES (%s, %s)", (user_id, 'Standard'))

        conn.commit()
        return redirect('/users')
    except Exception as e:
        conn.rollback()
        return f"Error: {str(e)}"
    finally:
        conn.close()


@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        email = request.form['email']
        user_type = request.form['user_type']

        cursor.execute(
            "UPDATE User SET Name=%s, Address=%s, Email=%s, User_type=%s WHERE User_ID=%s",
            (name, address, email, user_type, user_id)
        )
        conn.commit()
        conn.close()
        return redirect('/users')

    else:  # GET: Show form with current data
        cursor.execute("SELECT * FROM User WHERE User_ID = %s", (user_id,))
        user = cursor.fetchone()
        conn.close()
        return render_template('edit_user.html', user=user)


@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM User WHERE User_ID = %s", (user_id,))
    conn.commit()
    conn.close()
    return redirect('/users')

# ====== Products ======
@app.route('/products')
def list_products():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Product")
    products = cursor.fetchall()
    conn.close()
    return render_template('products.html', products=products)

@app.route('/add_product', methods=['POST'])
def add_product():
    category = request.form['category']
    name = request.form['name']
    stock = int(request.form['stock'])
    price = float(request.form['price'])
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Product (Category, Name, Stock, Price) VALUES (%s, %s, %s, %s)",
        (category, name, stock, price)
    )
    conn.commit()
    conn.close()
    return redirect('/products')

@app.route('/edit_product/<int:product_id>', methods=['POST'])
def edit_product(product_id):
    category = request.form['category']
    name = request.form['name']
    stock = int(request.form['stock'])
    price = float(request.form['price'])
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Product SET Category=%s, Name=%s, Stock=%s, Price=%s WHERE Product_ID=%s",
        (category, name, stock, price, product_id)
    )
    conn.commit()
    conn.close()
    return redirect('/products')

@app.route('/delete_product/<int:product_id>')
def delete_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product WHERE Product_ID = %s", (product_id,))
    conn.commit()
    conn.close()
    return redirect('/products')

# ====== Orders ======
@app.route('/orders')
def list_orders():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Orders")
    orders = cursor.fetchall()
    conn.close()
    return render_template('orders.html', orders=orders)

@app.route('/add_order', methods=['POST'])
def add_order():
    order_date = request.form['order_date']
    user_id = int(request.form['user_id'])
    status = request.form['status']
    total_amount = float(request.form['total_amount'])
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Orders (Order_date, User_ID, Status, Total_amount) VALUES (%s, %s, %s, %s)",
        (order_date, user_id, status, total_amount)
    )
    conn.commit()
    conn.close()
    return redirect('/orders')

@app.route('/edit_order/<int:order_id>', methods=['POST'])
def edit_order(order_id):
    order_date = request.form['order_date']
    user_id = int(request.form['user_id'])
    status = request.form['status']
    total_amount = float(request.form['total_amount'])
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Orders SET Order_date=%s, User_ID=%s, Status=%s, Total_amount=%s WHERE Order_ID=%s",
        (order_date, user_id, status, total_amount, order_id)
    )
    conn.commit()
    conn.close()
    return redirect('/orders')

@app.route('/delete_order/<int:order_id>')
def delete_order(order_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Orders WHERE Order_ID = %s", (order_id,))
    conn.commit()
    conn.close()
    return redirect('/orders')

# ====== Receipts ======
@app.route('/receipts')
def list_receipts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Receipt")
    receipts = cursor.fetchall()
    conn.close()
    return render_template('receipts.html', receipts=receipts)

@app.route('/add_receipt', methods=['POST'])
def add_receipt():
    order_id = int(request.form['order_id'])
    total_amount = float(request.form['total_amount'])
    receipt_date = request.form['receipt_date']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Receipt (Order_ID, Total_amount, Receipt_date) VALUES (%s, %s, %s)",
        (order_id, total_amount, receipt_date)
    )
    conn.commit()
    conn.close()
    return redirect('/receipts')

@app.route('/edit_receipt/<int:receipt_id>', methods=['POST'])
def edit_receipt(receipt_id):
    order_id = int(request.form['order_id'])
    total_amount = float(request.form['total_amount'])
    receipt_date = request.form['receipt_date']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Receipt SET Order_ID=%s, Total_amount=%s, Receipt_date=%s WHERE Receipt_ID=%s",
        (order_id, total_amount, receipt_date, receipt_id)
    )
    conn.commit()
    conn.close()
    return redirect('/receipts')

@app.route('/delete_receipt/<int:receipt_id>')
def delete_receipt(receipt_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Receipt WHERE Receipt_ID = %s", (receipt_id,))
    conn.commit()
    conn.close()
    return redirect('/receipts')

# ====== Payments ======
@app.route('/payments')
def list_payments():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Payment")
    payments = cursor.fetchall()
    conn.close()
    return render_template('payments.html', payments=payments)

@app.route('/add_payment', methods=['POST'])
def add_payment():
    receipt_id = int(request.form['receipt_id'])
    payment_id = int(request.form['payment_id'])
    payment_status = request.form['payment_status']
    payment_method = request.form['payment_method']
    user_id = int(request.form['user_id'])
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Payment (Receipt_ID, Payment_ID, Payment_status, Payment_method, User_ID) VALUES (%s, %s, %s, %s, %s)",
        (receipt_id, payment_id, payment_status, payment_method, user_id)
    )
    conn.commit()
    conn.close()
    return redirect('/payments')

@app.route('/edit_payment/<int:receipt_id>/<int:payment_id>', methods=['POST'])
def edit_payment(receipt_id, payment_id):
    payment_status = request.form['payment_status']
    payment_method = request.form['payment_method']
    user_id = int(request.form['user_id'])
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Payment SET Payment_status=%s, Payment_method=%s, User_ID=%s WHERE Receipt_ID=%s AND Payment_ID=%s",
        (payment_status, payment_method, user_id, receipt_id, payment_id)
    )
    conn.commit()
    conn.close()
    return redirect('/payments')

@app.route('/delete_payment/<int:receipt_id>/<int:payment_id>')
def delete_payment(receipt_id, payment_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM Payment WHERE Receipt_ID = %s AND Payment_ID = %s",
        (receipt_id, payment_id)
    )
    conn.commit()
    conn.close()
    return redirect('/payments')

# ====== User Phones ======
@app.route('/phones')
def list_phones():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM User_PhoneNum ORDER BY User_ID")
    phones = cursor.fetchall()
    conn.close()
    return render_template('phones.html', phones=phones)

@app.route('/add_phone', methods=['POST'])
def add_phone():
    user_id = int(request.form['user_id'])
    phone = request.form['phone']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO User_PhoneNum (User_ID, UPhone_num) VALUES (%s, %s)",
        (user_id, phone)
    )
    conn.commit()
    conn.close()
    return redirect('/phones')

@app.route('/edit_phone/<int:user_id>/<phone>', methods=['POST'])
def edit_phone(user_id, phone):
    new_phone = request.form['new_phone']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE User_PhoneNum SET UPhone_num=%s WHERE User_ID=%s AND UPhone_num=%s",
        (new_phone, user_id, phone)
    )
    conn.commit()
    conn.close()
    return redirect('/phones')

@app.route('/delete_phone/<int:user_id>/<phone>')
def delete_phone(user_id, phone):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM User_PhoneNum WHERE User_ID = %s AND UPhone_num = %s",
        (user_id, phone)
    )
    conn.commit()
    conn.close()
    return redirect('/phones')

# ====== Order Items (Contains) ======
@app.route('/contains')
def list_contains():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Contains ORDER BY Order_ID")
    items = cursor.fetchall()
    conn.close()
    return render_template('contains.html', items=items)

@app.route('/add_contains', methods=['POST'])
def add_contains():
    order_id = int(request.form['order_id'])
    product_id = int(request.form['product_id'])
    quantity = int(request.form['quantity'])
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Contains (Order_ID, Product_ID, Quantity) VALUES (%s, %s, %s)",
        (order_id, product_id, quantity)
    )
    conn.commit()
    conn.close()
    return redirect('/contains')

@app.route('/edit_contains/<int:order_id>/<int:product_id>', methods=['POST'])
def edit_contains(order_id, product_id):
    quantity = int(request.form['quantity'])
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Contains SET Quantity=%s WHERE Order_ID=%s AND Product_ID=%s",
        (quantity, order_id, product_id)
    )
    conn.commit()
    conn.close()
    return redirect('/contains')

@app.route('/delete_contains/<int:order_id>/<int:product_id>')
def delete_contains(order_id, product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM Contains WHERE Order_ID = %s AND Product_ID = %s",
        (order_id, product_id)
    )
    conn.commit()
    conn.close()
    return redirect('/contains')

if __name__ == '__main__':
    app.run(debug=True)