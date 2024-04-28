from flask import Flask, render_template, request, send_file, flash, redirect, session
from io import BytesIO
import sqlite3
from datetime import date

from helpers import login_required

app = Flask(__name__)
database = sqlite3.connect('spot.db')
db = database.cursor()

app.secret_key = 'KANUJ IS A FAT FUCKING HEADASS WHO IS ALSO SLEEPING RIGHT NOW'

# Connection parameters
conn_params = {
    'host': "localhost",
    'user': "root",
    'password': "password",
    'database': "my_base"
}

# Index route with search functionality
@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == "GET":
        # with pymysql.connect(**conn_params) as conn:
        #     with conn.cursor() as cursor:
        #         query = "SELECT id, title, description, last_known_location, reward, date_posted FROM items"
        #         cursor.execute(query)
        #         items = cursor.fetchall()
        items = db.execute("SELECT * FROM items")
        return render_template("dashboard.html", items=items)

    else:
        search_query = request.form.get('search')
        # Connect to MySQL
        # with pymysql.connect(**conn_params) as conn:
        #     with conn.cursor() as cursor:
        #         cursor.execute("SELECT id, title, description, last_known_location, reward, date_posted, image_reference FROM items WHERE title LIKE %s", [search_query])
        #         items = cursor.fetchall()
        #         # for item in items:
        #         #     item[7]
        items = db.execute("SELECT * FROM items WHERE title LIKE (?)", (search_query))
        return render_template('dashboard.html', items=items)
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    session.clear()

    if request.method == "GET":
        return render_template("register.html")
    
    else:
        if not request.form.get("email"):
            flash("Must provide email!", 'error')
            redirect("/register")   

        elif not request.form.get("password"):
            flash("Must provide password!", 'error')
            redirect("/register")

        elif not request.form.get("confirm_password"):
            flash("Must provide password confirmation", 'error')
            redirect("/register")

        elif request.form.get("password") != request.form.get("confirm_password"):
            flash("Passwords must match!", 'error')
            redirect("/register")   
        
        email = request.form.get("email")
        password = request.form.get("password")

        # with pymysql.connect(**conn_params) as conn:
        #     with conn.cursor() as cursor:
        #         query = "SELECT email FROM users WHERE email = %s"
        #         cursor.execute(query, email)
        #         items = cursor.fetchall()

        items = db.execute("SELECT email FROM users WHERE email = (?)", (email))
        
        if len(items) != 0:
            flash("There is already an account associated with this email.", 'error')
            return redirect("/register")

        # with pymysql.connect(**conn_params) as conn:
        #     with conn.cursor() as cursor:
        #         query = "INSERT INTO users (email, password) VALUES (%s, %s)"
        #         cursor.execute(query, [email, password])
        db.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        return redirect("/")

@app.route('/account', methods=['GET', 'POST'])
def account():
    if request.method == "GET":
        # with pymysql.connect(**conn_params) as conn:
        #         with conn.cursor() as cursor:
        #             cursor.execute("SELECT first_name, last_name, email FROM users WHERE email = %s", [session["email"]])
        #             items = cursor.fetchall()
        items = db.execute("SELECT first_name, last_name, email FROM users WHERE email = (?)", (session['email']))
        return render_template("account.html", items=items)

    else:
        # with pymysql.connect(**conn_params) as conn:
        #         with conn.cursor() as cursor:
        #             # query = "SELECT email, password FROM users WHERE email = jdoe@example.com"
        first = request.form.get("first")
        last = request.form.get("last")
        email = request.form.get("email")
        if not email:
            email = session['email']

        # cursor.execute('UPDATE users (first_name, last_name, email) VALUES (%s, %s, %s) WHERE email = %s;' [first, last, email, session['email']])
        db.execute("UPDATE users first_name=(?), last_name=(?), email=(?)", (first, last, email))
        session["email"] = email        

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        if not request.form.get('email') or not request.form.get('password'):
            flash("Enter in all the details to proceed!")
            return redirect("/login")
        else:
            # with pymysql.connect(**conn_params) as conn:
            #     with conn.cursor() as cursor:
                    # query = "SELECT email, password FROM users WHERE email = jdoe@example.com"
            email = request.form.get("email")
                    # cursor.execute(query)
            items = db.execute("SELECT email, password FROM users WHERE email=(?)", (email))


            if len(items) != 1 or not items[0][1] == request.form.get('password'):
                flash("Invalid username or password!")
            else:
                session["email"] = items[0][0]
                flash("The session email is: " + items[0][0])
                return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/add", methods=['POST'])
def add():
    title = request.form.get("title")
    description = request.form.get("description")
    location = request.form.get("")
    picture = request.files("picture")
    reward = request.form.get("reward")
    today = date.today()

    # with pymysql.connect(**conn_params) as conn:
    #     with conn.cursor() as cursor:
    #         cursor.execute("SELECT user_id FROM users WHERE email = %s", [session["email"]])
    #         items = cursor.fetchall()
    #         id = items[0][0]
    #         cursor.execute("INSERT INTO items (title, reward, description, date_posted, user_id, last_known_location, image_reference) VALUES (%s, %s, %s, %s, %s, %s, %s)", [title, reward, description, today, id, last_location, render_file, reward])
    db.execute("INSERT INTO items (title, description, reward, date_posted, location, image_reference, user_id) VALUES (?, ?, ?, ?, ?, ?, ?)", (title, description, reward, today, location, picture, session['email']))

    return redirect("/")


# # Route for displaying item details
# @app.route('/item/<int:item_id>')
# def item_details(item_id):
#     # with pymysql.connect(**conn_params) as conn:
#     #     with conn.cursor() as cursor:
#     #         query = "SELECT id, title, description, last_known_location, image_reference FROM items WHERE id = %s"
#     #         cursor.execute(query, (item_id,))
#     #         item = cursor.fetchone()


#     return render_template('item.html', item=item)

# # Route for fetching image data
# @app.route('/image/<int:item_id>')
# def get_image(item_id):
#     with pymysql.connect(**conn_params) as conn:
#         with conn.cursor() as cursor:
#             query = "SELECT image_reference FROM items WHERE id = %s"
#             cursor.execute(query, (item_id,))
#             image_reference = cursor.fetchone()

#     # Check if image reference is valid and return image data
#     if image_reference and image_reference[0]:
#         # Open the referenced image file
#         with open(image_reference[0], 'rb') as img_file:
#             image_data = img_file.read()
        
#         return send_file(BytesIO(image_data), mimetype='image/jpeg')
#     else:
#         return 'Image not found', 404

# Run the Flask application
if __name__ == "__main__":
    app.run(debug=True)
    