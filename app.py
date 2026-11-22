
from flask import Flask, render_template, redirect, url_for, session, flash, request
import sqlite3
import uuid
import random
from functools import wraps
from datetime import datetime, timedelta

from catalog import restaurants, restaurant_tables

app = Flask(__name__)
app.secret_key = "foodcourt-demo-secret-key-change-before-deployment"

DATABASE = "foodcourt.db"
RESERVATION_DURATION = 60
DINING_DEPOSIT = 100

OFFERS = {
    "WELCOME10": {
        "description": "10% off, maximum discount ₹100",
        "kind": "percent",
        "value": 10,
        "max_discount": 100,
        "minimum": 199
    },
    "FLAT50": {
        "description": "₹50 off orders above ₹299",
        "kind": "flat",
        "value": 50,
        "minimum": 299
    }
}

PAYMENT_METHODS = [
    "UPI", "Wallet", "Net Banking",
    "Credit Card", "Debit Card"
]


#DATABASE:Connects to SQLite
def get_db():
    connection = sqlite3.connect(DATABASE, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


#DATABASE:Adds columns without deleting existing records
def add_column(connection, table, column, definition):
    columns = [
        row["name"]
        for row in connection.execute(f"PRAGMA table_info({table})")
    ]

    if column not in columns:
        connection.execute(
            f"ALTER TABLE {table} ADD COLUMN {column} {definition}"
        )


#DATABASE:Creates and upgrades database tables
def initialize_database():
    connection = get_db()

    connection.executescript("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            restaurant_name TEXT NOT NULL,
            total REAL NOT NULL,
            service_type TEXT NOT NULL,
            payment_status TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL,
            item_name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id)
        );

        CREATE TABLE IF NOT EXISTS payments (
            payment_id TEXT PRIMARY KEY,
            order_id TEXT NOT NULL,
            amount REAL NOT NULL,
            payment_status TEXT NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id)
        );

        CREATE TABLE IF NOT EXISTS reservations (
            reservation_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            restaurant_id TEXT NOT NULL,
            restaurant_name TEXT NOT NULL,
            reservation_date TEXT NOT NULL,
            reservation_time TEXT NOT NULL,
            guests INTEGER NOT NULL,
            table_id TEXT NOT NULL,
            capacity INTEGER NOT NULL,
            status TEXT NOT NULL,
            UNIQUE (restaurant_id, reservation_date, reservation_time, table_id)
        );

        CREATE TABLE IF NOT EXISTS customers (
            customer_id TEXT PRIMARY KEY,
            contact TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL DEFAULT '',
            location TEXT NOT NULL DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS reviews (
            review_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT NOT NULL,
            restaurant_id TEXT NOT NULL,
            order_id TEXT NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(customer_id, order_id),
            FOREIGN KEY(order_id) REFERENCES orders(order_id)
        );

        CREATE TABLE IF NOT EXISTS reservation_payments (
            payment_id TEXT PRIMARY KEY,
            reservation_id TEXT NOT NULL,
            customer_id TEXT NOT NULL,
            amount REAL NOT NULL,
            payment_method TEXT NOT NULL,
            payment_status TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
    """)

    add_column(connection, "orders", "payment_method", "TEXT DEFAULT 'Demo'")
    add_column(connection, "orders", "discount", "REAL DEFAULT 0")
    add_column(connection, "orders", "offer_code", "TEXT DEFAULT ''")
    add_column(connection, "orders", "delivery_address", "TEXT DEFAULT ''")
    add_column(connection, "orders", "created_at", "TEXT DEFAULT ''")
    add_column(connection, "payments", "payment_method", "TEXT DEFAULT 'Demo'")
    add_column(connection, "payments", "created_at", "TEXT DEFAULT ''")
    add_column(connection, "reservations", "deposit_amount", "REAL DEFAULT 0")
    add_column(connection, "reservations", "deposit_status", "TEXT DEFAULT 'Not Paid'")

    connection.commit()
    connection.close()


#CUSTOMER:Returns the logged-in customer's ID
def get_customer_id():
    if not session.get("logged_in"):
        return None
    return session.get("customer_id")


#AUTHENTICATION:Protects pages that require login
def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            session["next_url"] = request.url
            flash("Please log in with OTP to continue.")
            return redirect(url_for("login"))
        return function(*args, **kwargs)
    return wrapper


#RESERVATION:Checks overlapping one-hour reservations
def is_table_available(connection, restaurant_id, reservation_date,
                        reservation_time, table_id):
    requested_start = datetime.strptime(
        reservation_date + " " + reservation_time,
        "%Y-%m-%d %H:%M"
    )
    requested_end = requested_start + timedelta(minutes=RESERVATION_DURATION)

    bookings = connection.execute(
        """SELECT reservation_time FROM reservations
        WHERE restaurant_id=? AND reservation_date=?
        AND table_id=? AND status='Confirmed'""",
        (restaurant_id, reservation_date, table_id)
    ).fetchall()

    for booking in bookings:
        existing_start = datetime.strptime(
            reservation_date + " " + booking["reservation_time"],
            "%Y-%m-%d %H:%M"
        )
        existing_end = existing_start + timedelta(minutes=RESERVATION_DURATION)

        if requested_start < existing_end and requested_end > existing_start:
            return False

    return True


#RESERVATION:Finds the smallest suitable available table
def find_available_table(connection, restaurant_id, reservation_date,
                         reservation_time, guests):
    tables = sorted(
        restaurant_tables.get(restaurant_id, []),
        key=lambda table: table["capacity"]
    )

    for table in tables:
        if table["capacity"] >= guests:
            if is_table_available(
                connection,
                restaurant_id,
                reservation_date,
                reservation_time,
                table["table_id"]
            ):
                return table

    return None


#OFFERS:Calculates a valid discount
def calculate_offer(total, code):
    code = (code or "").strip().upper()

    if not code:
        return 0, ""

    offer = OFFERS.get(code)

    if not offer or total < offer["minimum"]:
        return 0, ""

    if offer["kind"] == "percent":
        discount = min(
            total * offer["value"] / 100,
            offer["max_discount"]
        )
    else:
        discount = offer["value"]

    return round(min(discount, total), 2), code


#CATALOGUE:Returns every cuisine in the restaurant catalogue
def get_all_cuisines():
    return sorted({
        cuisine
        for restaurant in restaurants.values()
        for cuisine in restaurant.get("cuisines", [])
    })


#CATALOGUE:Returns all restaurant categories
def get_all_restaurant_types():
    return sorted({
        restaurant["type"]
        for restaurant in restaurants.values()
    })


@app.context_processor
def global_template_data():
    return {
        "logged_in": bool(session.get("logged_in")),
        "customer_name": session.get("customer_name", "")
    }


#HOME:Displays the main page
@app.route("/")
def home():
    return render_template("index.html", offers=OFFERS)


#FR1:Login using mobile number or email
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        contact = request.form.get("contact", "").strip().lower()

        if not contact or len(contact) < 5:
            flash("Enter a valid mobile number or email address.", "error")
            return redirect(url_for("login"))

        otp = str(random.randint(100000, 999999))

        session.pop("_flashes", None)
        session["otp"] = otp
        session["otp_contact"] = contact
        session["otp_expires"] = (
            datetime.now() + timedelta(minutes=5)
        ).isoformat()

        return redirect(url_for("verify_otp"))

    return render_template("login.html")


#FR1:Verifies the one-time password
@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    if not session.get("otp"):
        flash("Please request a new OTP.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        entered = request.form.get("otp", "").strip()

        try:
            expired = datetime.now() > datetime.fromisoformat(
                session.get("otp_expires", "")
            )
        except (ValueError, TypeError):
            expired = True

        if expired or entered != session.get("otp"):
            flash("Invalid or expired OTP. Please try again.", "error")
            return redirect(url_for("verify_otp"))

        contact = session["otp_contact"]
        connection = get_db()

        customer = connection.execute(
            "SELECT * FROM customers WHERE contact=?",
            (contact,)
        ).fetchone()

        if customer:
            customer_id = customer["customer_id"]
            name = customer["name"]
            location = customer["location"]
        else:
            customer_id = "CUS" + uuid.uuid4().hex[:10].upper()
            name = ""
            location = ""

            connection.execute(
                "INSERT INTO customers(customer_id,contact) VALUES(?,?)",
                (customer_id, contact)
            )
            connection.commit()

        connection.close()

        session["logged_in"] = True
        session["customer_id"] = customer_id
        session["customer_contact"] = contact
        session["customer_name"] = name
        session["location"] = location

        for key in ["otp", "otp_contact", "otp_expires"]:
            session.pop(key, None)

        session.pop("_flashes", None)
        flash("Login successful.", "success")

        return redirect(session.pop("next_url", url_for("home")))

    return render_template(
        "verify_otp.html",
        contact=session.get("otp_contact"),
        demo_otp=session.get("otp")
    )


@app.route("/logout", methods=["POST"])
def logout():
    keys = [
        "logged_in", "customer_id", "customer_contact",
        "customer_name", "location", "otp",
        "otp_contact", "otp_expires"
    ]

    for key in keys:
        session.pop(key, None)

    flash("You have been logged out.")
    return redirect(url_for("home"))


#FR1:View and update customer profile
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        location = request.form.get("location", "").strip()

        if not name:
            flash("Please enter your name.")
            return redirect(url_for("profile"))

        connection = get_db()
        connection.execute(
            "UPDATE customers SET name=?, location=? WHERE customer_id=?",
            (name, location, get_customer_id())
        )
        connection.commit()
        connection.close()

        session["customer_name"] = name
        session["location"] = location

        flash("Profile updated.")
        return redirect(url_for("profile"))

    return render_template(
        "profile.html",
        contact=session.get("customer_contact"),
        name=session.get("customer_name"),
        location=session.get("location")
    )


#FR2:Manually update the selected location
@app.route("/location", methods=["GET", "POST"])
def location():
    if request.method == "POST":
        place = request.form.get("location", "").strip()

        if not place:
            flash("Enter a location.")
            return redirect(url_for("location"))

        session["location"] = place

        if session.get("logged_in"):
            connection = get_db()
            connection.execute(
                "UPDATE customers SET location=? WHERE customer_id=?",
                (place, get_customer_id())
            )
            connection.commit()
            connection.close()

        flash("Location updated.")
        return redirect(url_for("restaurant_list"))

    return render_template(
        "location.html",
        location=session.get("location", "")
    )


#FR3 and FR4:Browse and filter restaurants
@app.route("/restaurants")
def restaurant_list():
    cuisine = request.args.get("cuisine", "").strip()
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    min_rating = request.args.get("rating", type=float)
    max_distance = request.args.get("distance", type=float)
    food_type = request.args.get("food_type", "").strip()
    restaurant_type = request.args.get("restaurant_type", "").strip()
    search = request.args.get("search", "").strip().lower()

    results = []
    connection = get_db()

    for rid, restaurant in restaurants.items():
        menu = restaurant.get("menu", [])
        prices = [item["price"] for item in menu]

        if not prices:
            continue

        avg = connection.execute(
            "SELECT AVG(rating) FROM reviews WHERE restaurant_id=?",
            (rid,)
        ).fetchone()[0]

        rating = round(avg, 1) if avg else restaurant["rating"]

        restaurant_cuisines = restaurant.get(
            "cuisines", [restaurant.get("cuisine", "")]
        )

        if cuisine and cuisine not in restaurant_cuisines:
            continue

        if min_price is not None and max(prices) < min_price:
            continue

        if max_price is not None and min(prices) > max_price:
            continue

        if min_rating is not None and rating < min_rating:
            continue

        if max_distance is not None and restaurant["distance"] > max_distance:
            continue

        if restaurant_type and restaurant["type"] != restaurant_type:
            continue

        if food_type and not any(
            item["food_type"] == food_type for item in menu
        ):
            continue

        haystack = " ".join([
            restaurant["name"],
            restaurant.get("cuisine", ""),
            restaurant.get("type", ""),
            restaurant.get("description", ""),
            " ".join(restaurant_cuisines),
            " ".join(item["name"] for item in menu),
            " ".join(item.get("category", "") for item in menu)
        ]).lower()

        if search and search not in haystack:
            continue

        result = dict(restaurant)
        result.update({
            "id": rid,
            "rating_display": rating,
            "min_price": min(prices),
            "max_price": max(prices)
        })

        results.append(result)

    connection.close()

    results.sort(key=lambda item: item["rating_display"], reverse=True)

    return render_template(
        "restaurants.html",
        restaurants=results,
        filters=request.args,
        cuisines=get_all_cuisines(),
        restaurant_types=get_all_restaurant_types()
    )


#FR3 and FR5:Display a menu, rating and reviews
@app.route("/menu/<restaurant_id>")
def menu(restaurant_id):
    restaurant = restaurants.get(restaurant_id)

    if not restaurant:
        return "Restaurant not found", 404

    connection = get_db()

    reviews = connection.execute(
        """SELECT rating, comment, created_at
        FROM reviews WHERE restaurant_id=?
        ORDER BY review_id DESC""",
        (restaurant_id,)
    ).fetchall()

    avg = connection.execute(
        "SELECT AVG(rating) FROM reviews WHERE restaurant_id=?",
        (restaurant_id,)
    ).fetchone()[0]

    connection.close()

    rating = round(avg, 1) if avg else restaurant["rating"]

    return render_template(
        "menu.html",
        restaurant=restaurant,
        restaurant_id=restaurant_id,
        reviews=reviews,
        rating=rating
    )


#FR8:Add food to cart
@app.route("/add-to-cart/<restaurant_id>/<int:item_index>", methods=["POST"])
@login_required
def add_to_cart(restaurant_id, item_index):
    restaurant = restaurants.get(restaurant_id)

    if not restaurant or item_index < 0 or item_index >= len(restaurant["menu"]):
        return "Item not found", 404

    if session.get("restaurant_id") and session["restaurant_id"] != restaurant_id:
        flash("Your cart already contains items from another restaurant. Clear it first.")
        return redirect(url_for("menu", restaurant_id=restaurant_id))

    item = restaurant["menu"][item_index]

    if not session.get("cart"):
        session["cart"] = []
        session["restaurant_id"] = restaurant_id
        session["restaurant_name"] = restaurant["name"]

    found = False

    for cart_item in session["cart"]:
        if cart_item["name"] == item["name"]:
            cart_item["quantity"] += 1
            found = True
            break

    if not found:
        session["cart"].append({
            "name": item["name"],
            "price": item["price"],
            "quantity": 1
        })

    session.modified = True
    flash(item["name"] + " added to cart!")

    return redirect(url_for("menu", restaurant_id=restaurant_id))


#FR8:Change cart quantity or remove items
@app.route("/update-cart/<int:item_index>/<action>", methods=["POST"])
@login_required
def update_cart(item_index, action):
    cart = session.get("cart", [])

    if item_index < 0 or item_index >= len(cart):
        return redirect(url_for("view_cart"))

    if action == "increase":
        cart[item_index]["quantity"] += 1

    elif action == "decrease":
        cart[item_index]["quantity"] -= 1
        if cart[item_index]["quantity"] <= 0:
            cart.pop(item_index)

    elif action == "remove":
        cart.pop(item_index)

    session["cart"] = cart

    if not cart:
        for key in [
            "restaurant_id", "restaurant_name",
            "service_type", "offer_code", "delivery_address"
        ]:
            session.pop(key, None)

    session.modified = True
    return redirect(url_for("view_cart"))


@app.route("/cart")
def view_cart():
    cart = session.get("cart", [])
    total = sum(item["price"] * item["quantity"] for item in cart)

    return render_template(
        "cart.html",
        cart=cart,
        total=total,
        restaurant_name=session.get("restaurant_name")
    )


#FR7 and FR8:Select service and delivery address
@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    cart = session.get("cart", [])

    if not cart:
        flash("Your cart is empty. Add items before checkout.")
        return redirect(url_for("view_cart"))

    total = sum(item["price"] * item["quantity"] for item in cart)

    if request.method == "POST":
        service = request.form.get("service_type")

        if service not in [
            "Dine-in", "Takeaway / Pickup", "Home Delivery"
        ]:
            flash("Select a valid service method.")
            return redirect(url_for("checkout"))

        address = request.form.get("delivery_address", "").strip()

        if service == "Home Delivery" and len(address) < 8:
            flash("Enter a complete delivery address.")
            return redirect(url_for("checkout"))

        session["service_type"] = service
        session["delivery_address"] = address if service == "Home Delivery" else ""

        return redirect(url_for("checkout"))

    discount, offer_code = calculate_offer(
        total, session.get("offer_code")
    )

    return render_template(
        "checkout.html",
        cart=cart,
        total=total,
        restaurant_name=session.get("restaurant_name"),
        selected_service=session.get("service_type"),
        discount=discount,
        final_total=total - discount,
        offer_code=session.get("offer_code", ""),
        offers=OFFERS
    )


#FR6:Apply an offer code
@app.route("/apply-offer", methods=["POST"])
@login_required
def apply_offer():
    total = sum(
        item["price"] * item["quantity"]
        for item in session.get("cart", [])
    )

    discount, code = calculate_offer(
        total, request.form.get("offer_code")
    )

    if not code:
        session.pop("offer_code", None)
        flash("Invalid offer code or minimum order value not reached.")
    else:
        session["offer_code"] = code
        flash(f"Offer {code} applied. You save ₹{discount:.2f}.")

    return redirect(url_for("checkout"))


#FR9:Simulated payment using selected payment method
@app.route("/payment", methods=["GET", "POST"])
@login_required
def payment():
    cart = session.get("cart", [])

    if not cart or not session.get("service_type"):
        return redirect(url_for("checkout"))

    subtotal = sum(
        item["price"] * item["quantity"]
        for item in cart
    )

    discount, offer_code = calculate_offer(
        subtotal, session.get("offer_code")
    )

    total = round(subtotal - discount, 2)

    if request.method == "POST":
        method = request.form.get("payment_method")

        if method not in PAYMENT_METHODS:
            flash("Select a valid payment method.")
            return redirect(url_for("payment"))

        customer_id = get_customer_id()
        order_id = "FC" + uuid.uuid4().hex[:8].upper()
        payment_id = "PAY" + uuid.uuid4().hex[:8].upper()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        connection = get_db()

        try:
            connection.execute(
                """INSERT INTO orders
                (order_id, customer_id, restaurant_name, total,
                service_type, payment_status, payment_method,
                discount, offer_code, delivery_address, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    order_id, customer_id,
                    session["restaurant_name"], total,
                    session["service_type"], "Successful (Demo)",
                    method, discount, offer_code,
                    session.get("delivery_address", ""), now
                )
            )

            for item in cart:
                connection.execute(
                    """INSERT INTO order_items
                    (order_id, item_name, price, quantity)
                    VALUES (?, ?, ?, ?)""",
                    (
                        order_id, item["name"],
                        item["price"], item["quantity"]
                    )
                )

            connection.execute(
                """INSERT INTO payments
                (payment_id, order_id, amount, payment_status,
                payment_method, created_at)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    payment_id, order_id, total,
                    "Successful (Demo)", method, now
                )
            )

            connection.commit()

        except sqlite3.Error:
            connection.rollback()
            return "Unable to save the order. Please try again.", 500

        finally:
            connection.close()

        session["last_order_id"] = order_id

        for key in [
            "cart", "restaurant_id", "restaurant_name",
            "service_type", "offer_code", "delivery_address"
        ]:
            session.pop(key, None)

        return redirect(url_for("order_confirmation"))

    return render_template(
        "payment.html",
        total=total,
        subtotal=subtotal,
        discount=discount,
        offer_code=offer_code,
        restaurant_name=session.get("restaurant_name"),
        service_type=session.get("service_type"),
        payment_methods=PAYMENT_METHODS
    )


#FR10:Display order confirmation
@app.route("/order-confirmation")
@login_required
def order_confirmation():
    order_id = session.get("last_order_id")

    if not order_id:
        return redirect(url_for("restaurant_list"))

    connection = get_db()

    order = connection.execute(
        "SELECT * FROM orders WHERE order_id=? AND customer_id=?",
        (order_id, get_customer_id())
    ).fetchone()

    items = connection.execute(
        "SELECT * FROM order_items WHERE order_id=?",
        (order_id,)
    ).fetchall()

    connection.close()

    if not order:
        return redirect(url_for("restaurant_list"))

    details = dict(order)
    details["items"] = [dict(item) for item in items]

    return render_template("order_confirmation.html", order=details)


#FR10:Display previous orders
@app.route("/order-history")
@login_required
def order_history():
    connection = get_db()

    orders = connection.execute(
        """SELECT * FROM orders
        WHERE customer_id=?
        ORDER BY created_at DESC, rowid DESC""",
        (get_customer_id(),)
    ).fetchall()

    result = []

    for order in orders:
        details = dict(order)

        items = connection.execute(
            "SELECT * FROM order_items WHERE order_id=?",
            (order["order_id"],)
        ).fetchall()

        details["items"] = [dict(item) for item in items]
        result.append(details)

    connection.close()

    return render_template("order_history.html", orders=result)


#FR5:Display reviews
@app.route("/reviews")
def reviews():
    connection = get_db()

    rows = connection.execute(
        """SELECT reviews.*, customers.name
        FROM reviews
        LEFT JOIN customers
        ON customers.customer_id=reviews.customer_id
        ORDER BY review_id DESC"""
    ).fetchall()

    connection.close()

    return render_template(
        "reviews.html",
        reviews=rows,
        restaurants=restaurants
    )


#FR5:Only customers with a completed order can review
@app.route("/review/<restaurant_id>", methods=["GET", "POST"])
@login_required
def submit_review(restaurant_id):
    if restaurant_id not in restaurants:
        return "Restaurant not found", 404

    connection = get_db()

    eligible = connection.execute(
        """SELECT order_id FROM orders
        WHERE customer_id=? AND restaurant_name=?
        ORDER BY rowid DESC""",
        (get_customer_id(), restaurants[restaurant_id]["name"])
    ).fetchall()

    if request.method == "POST":
        order_id = request.form.get("order_id", "")
        rating = request.form.get("rating", type=int)
        comment = request.form.get("comment", "").strip()

        valid = connection.execute(
            """SELECT order_id FROM orders
            WHERE order_id=? AND customer_id=? AND restaurant_name=?""",
            (order_id, get_customer_id(), restaurants[restaurant_id]["name"])
        ).fetchone()

        already = connection.execute(
            "SELECT review_id FROM reviews WHERE customer_id=? AND order_id=?",
            (get_customer_id(), order_id)
        ).fetchone()

        if (
            not valid or already or
            rating not in range(1, 6) or len(comment) < 3
        ):
            connection.close()
            flash("Choose an eligible order, a 1–5 star rating and a review of at least 3 characters.")
            return redirect(url_for("submit_review", restaurant_id=restaurant_id))

        connection.execute(
            """INSERT INTO reviews
            (customer_id, restaurant_id, order_id, rating, comment, created_at)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (
                get_customer_id(), restaurant_id, order_id,
                rating, comment,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        )

        connection.commit()
        connection.close()

        flash("Your verified review has been submitted.")
        return redirect(url_for("menu", restaurant_id=restaurant_id))

    available = []

    for row in eligible:
        already = connection.execute(
            "SELECT 1 FROM reviews WHERE customer_id=? AND order_id=?",
            (get_customer_id(), row["order_id"])
        ).fetchone()

        if not already:
            available.append(row["order_id"])

    connection.close()

    return render_template(
        "review_form.html",
        restaurant=restaurants[restaurant_id],
        restaurant_id=restaurant_id,
        eligible_orders=available
    )


#FR7:Display reservation form
@app.route("/reservation")
def reservation():
    return render_template("reservation.html", restaurants=restaurants)


#FR7:Check table availability
@app.route("/reservation/check", methods=["POST"])
@login_required
def check_reservation():
    rid = request.form.get("restaurant_id")
    date = request.form.get("reservation_date")
    time = request.form.get("reservation_time")
    guests = request.form.get("guests", type=int)

    if rid not in restaurants or not date or not time or not guests or guests < 1:
        flash("Enter valid reservation details.")
        return redirect(url_for("reservation"))

    try:
        start = datetime.strptime(date + " " + time, "%Y-%m-%d %H:%M")
    except ValueError:
        flash("Enter a valid date and time.")
        return redirect(url_for("reservation"))

    if start <= datetime.now():
        flash("Choose a future date and time.")
        return redirect(url_for("reservation"))

    connection = get_db()

    table = find_available_table(
        connection, rid, date, time, guests
    )

    connection.close()

    if not table:
        return render_template(
            "reservation.html",
            restaurants=restaurants,
            unavailable=True,
            selected_restaurant=rid,
            reservation_date=date,
            reservation_time=time,
            guests=guests
        )

    session["pending_reservation"] = {
        "restaurant_id": rid,
        "restaurant_name": restaurants[rid]["name"],
        "reservation_date": date,
        "reservation_time": time,
        "guests": guests,
        "table_id": table["table_id"],
        "capacity": table["capacity"]
    }

    return render_template(
        "reservation.html",
        restaurants=restaurants,
        available=True,
        pending_reservation=session["pending_reservation"]
    )


#FR7 and FR9:Confirm reservation and record advance deposit
@app.route("/reservation/confirm", methods=["POST"])
@login_required
def confirm_reservation():
    pending = session.get("pending_reservation")

    if not pending:
        return redirect(url_for("reservation"))

    reservation_id = "RS" + uuid.uuid4().hex[:8].upper()
    connection = get_db()

    try:
        connection.execute("BEGIN IMMEDIATE")

        available = is_table_available(
            connection,
            pending["restaurant_id"],
            pending["reservation_date"],
            pending["reservation_time"],
            pending["table_id"]
        )

        if not available:
            connection.rollback()
            flash("This table is no longer available. Select another slot.")
            return redirect(url_for("reservation"))

        connection.execute(
            """INSERT INTO reservations
            (reservation_id, customer_id, restaurant_id, restaurant_name,
            reservation_date, reservation_time, guests, table_id,
            capacity, status, deposit_amount, deposit_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                reservation_id, get_customer_id(),
                pending["restaurant_id"], pending["restaurant_name"],
                pending["reservation_date"], pending["reservation_time"],
                pending["guests"], pending["table_id"],
                pending["capacity"], "Confirmed",
                DINING_DEPOSIT, "Pending"
            )
        )

        connection.commit()

    except sqlite3.IntegrityError:
        connection.rollback()
        flash("That table has already been booked. Select another slot.")
        return redirect(url_for("reservation"))

    finally:
        connection.close()

    session["last_reservation_id"] = reservation_id
    session.pop("pending_reservation", None)

    return redirect(url_for("reservation_confirmation"))


@app.route("/reservation-confirmation")
@login_required
def reservation_confirmation():
    rid = session.get("last_reservation_id")
    connection = get_db()

    booking = connection.execute(
        """SELECT * FROM reservations
        WHERE reservation_id=? AND customer_id=?""",
        (rid, get_customer_id())
    ).fetchone() if rid else None

    connection.close()

    if not booking:
        return redirect(url_for("reservation"))

    return render_template(
        "reservation_confirmation.html",
        booking=booking
    )


#FR9:Pay the reservation advance deposit
@app.route("/reservation-deposit/<reservation_id>", methods=["GET", "POST"])
@login_required
def reservation_deposit(reservation_id):
    connection = get_db()

    booking = connection.execute(
        """SELECT * FROM reservations
        WHERE reservation_id=? AND customer_id=?""",
        (reservation_id, get_customer_id())
    ).fetchone()

    if not booking:
        connection.close()
        return "Reservation not found", 404

    if request.method == "POST":
        method = request.form.get("payment_method")

        if method not in PAYMENT_METHODS:
            connection.close()
            flash("Select a valid payment method.")
            return redirect(
                url_for("reservation_deposit", reservation_id=reservation_id)
            )

        if booking["deposit_status"] != "Paid":
            payment_id = "DP" + uuid.uuid4().hex[:8].upper()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            connection.execute(
                """INSERT INTO reservation_payments
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    payment_id, reservation_id,
                    get_customer_id(), DINING_DEPOSIT,
                    method, "Successful (Demo)", now
                )
            )

            connection.execute(
                "UPDATE reservations SET deposit_status='Paid' WHERE reservation_id=?",
                (reservation_id,)
            )

            connection.commit()

        connection.close()
        flash("Demo advance deposit paid successfully.")
        return redirect(url_for("reservation_history"))

    connection.close()

    return render_template(
        "reservation_deposit.html",
        booking=booking,
        deposit=DINING_DEPOSIT,
        payment_methods=PAYMENT_METHODS
    )


#FR10:Display reservation history
@app.route("/reservation-history")
@login_required
def reservation_history():
    connection = get_db()

    rows = connection.execute(
        """SELECT * FROM reservations
        WHERE customer_id=?
        ORDER BY reservation_date DESC, reservation_time DESC""",
        (get_customer_id(),)
    ).fetchall()

    connection.close()

    return render_template(
        "reservation_history.html",
        reservations=rows
    )


#FR10:Display order and reservation transactions
@app.route("/transactions")
@login_required
def transactions():
    connection = get_db()

    rows = connection.execute(
        """SELECT p.payment_id, p.order_id, p.amount,
        p.payment_status, p.payment_method, p.created_at,
        o.restaurant_name
        FROM payments p
        JOIN orders o ON o.order_id=p.order_id
        WHERE o.customer_id=?

        UNION ALL

        SELECT rp.payment_id, rp.reservation_id AS order_id,
        rp.amount, rp.payment_status, rp.payment_method,
        rp.created_at, r.restaurant_name
        FROM reservation_payments rp
        JOIN reservations r ON r.reservation_id=rp.reservation_id
        WHERE rp.customer_id=?

        ORDER BY created_at DESC""",
        (get_customer_id(), get_customer_id())
    ).fetchall()

    connection.close()

    return render_template(
        "transactions.html",
        transactions=rows
    )


@app.route("/clear-cart", methods=["POST", "GET"])
def clear_cart():
    for key in [
        "cart", "restaurant_id", "restaurant_name",
        "service_type", "offer_code", "delivery_address"
    ]:
        session.pop(key, None)

    flash("Your cart has been cleared.")
    return redirect(url_for("view_cart"))


if __name__ == "__main__":
    initialize_database()
    app.run(debug=True)
