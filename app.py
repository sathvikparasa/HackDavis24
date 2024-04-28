from flask import Flask, render_template, request, send_file, flash, redirect, session
from io import BytesIO
import sqlite3
import os
from werkzeug.utils import secure_filename
import base64
from datetime import date

# Flask application setup
app = Flask(__name__)
app.secret_key = 'KANUJ IS A FAT FUCKING HEADASS WHO IS ALSO SLEEPING RIGHT NOW'  # Use a secure, unique key
app.config['UPLOAD_FOLDER'] = 'uploads'  # Set the upload folder path

# File extension allowed for uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# SQLite database setup
def get_db_connection():
    conn = sqlite3.connect('spot.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    return conn

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    # Your login logic here
    # For now, we'll just redirect to the dashboard
    session['email'] = request.form.get('email')  # Assuming you have a 'users' table with an 'email' column
    return redirect('/')

# Index route with search functionality
@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()  # Open a new connection
    cursor = conn.cursor()

    if request.method == "GET":
        items = cursor.execute("SELECT * FROM items").fetchall()
        conn.close()  # Close the connection after use
        return render_template("dashboard.html", items=items)

    search_query = request.form.get('search')
    items = cursor.execute("SELECT * FROM items WHERE title LIKE ?", (f"%{search_query}%",)).fetchall()
    conn.close()  # Close the connection after use
    return render_template("dashboard.html", items=items)


@app.route('/oldest', methods=['GET', 'POST'])
def oldest():
    conn = get_db_connection()  # Open a new connection
    cursor = conn.cursor()

    if request.method == "GET":
        items = cursor.execute("SELECT * FROM items ORDER BY date_posted DESC").fetchall()
        conn.close()  # Close the connection after use
        return render_template("oldest.html", items=items)

    search_query = request.form.get('search')
    items = cursor.execute("SELECT * FROM items WHERE title LIKE ? ORDER BY date_posted DESC", (f"%{search_query}%",)).fetchall()
    conn.close()  # Close the connection after use
    return render_template("oldest.html", items=items)


@app.route('/reward', methods=['GET', 'POST'])
def reward():
    conn = get_db_connection()  # Open a new connection
    cursor = conn.cursor()

    if request.method == "GET":
        items = cursor.execute("SELECT * FROM items ORDER BY reward DESC").fetchall()
        conn.close()  # Close the connection after use
        return render_template("reward.html", items=items)

    search_query = request.form.get('search')
    items = cursor.execute("SELECT * FROM items WHERE title LIKE ? ORDER BY reward DESC;", (f"%{search_query}%",)).fetchall()
    conn.close()  # Close the connection after use
    return render_template("reward.html", items=items)


# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    session.clear()  # Clear session on registration attempt
    if request.method == "GET":
        return render_template("register.html")

    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        flash("Email and password are required!", 'error')
        return redirect("/register")

    confirm_password = request.form.get("confirm_password")

    if password != confirm_password:
        flash("Passwords must match!", 'error')
        return redirect("/register")

    conn = get_db_connection()  # Open a new connection
    cursor = conn.cursor()

    existing_user = cursor.execute("SELECT email FROM users WHERE email = ?", (email,)).fetchone()

    if existing_user:
        flash("An account with this email already exists.", 'error')
        conn.close()  # Close the connection
        return redirect("/register")

    cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
    conn.commit()  # Commit changes
    conn.close()  # Close the connection after use

    flash("Registration successful!", 'success')
    return redirect("/")

# Route for fetching image data
@app.route('/image/<int:item_id>')
def get_image(item_id):
    conn = get_db_connection()  # Open a new connection
    cursor = conn.cursor()

    image_reference = cursor.execute("SELECT image_reference FROM items WHERE id = ?", (item_id,)).fetchone()
    
    if image_reference and image_reference['image_reference']:
        image_data = base64.b64decode(image_reference['image_reference'])
        conn.close()  # Close the connection
        return send_file(BytesIO(image_data), mimetype='image/jpeg')
    else:
        conn.close()  # Close the connection
        return 'Image not found', 404

# Route for user logout
@app.route("/logout")
def logout():
    session.clear()  # Clear the session
    flash("Logged out successfully.", 'success')
    return redirect("/login")  # Redirect to login after logout

# Route to add an item
@app.route("/add", methods=['POST'])
def add():
    if 'email' not in session:
        flash("You must be logged in to add an item.", 'error')
        return redirect("/login")

    title = request.form.get("title")
    description = request.form.get("description")
    reward = request.form.get("reward")
    location = request.form.get("location")

    # Handling image uploads
    file = request.files.get("picture")  # Get the image
    if file and allowed_file(file.filename):  # If a file is provided and has an allowed extension
        filename = secure_filename(file.filename)  # Sanitize the filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)  # Save the file
    else:
        filename = None  # No image uploaded

    today = date.today()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO items (title, description, reward, date_posted, location, email, image_reference) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (title, description, reward, today, location, session['email'], filename)
    )

    conn.commit()  # Commit the transaction
    conn.close()

    flash("Item added successfully!", 'success')
    return redirect("/")

# Route to display user account information
@app.route("/account", methods=['GET', 'POST'])
def account():
    if 'email' not in session:
        flash("You must be logged in to access your account.", 'error')
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch user information from the database
    user_info = cursor.execute("SELECT * FROM users WHERE email = ?", (session['email'],)).fetchone()

    if request.method == 'POST':
        # Update user information
        first_name = request.form.get("first")
        last_name = request.form.get("last")
        email = request.form.get("email")

        # Update the user information in the database
        cursor.execute("UPDATE users SET first_name = ?, last_name = ?, email = ? WHERE email = ?",
                       (first_name, last_name, email, session['email']))
        conn.commit()
        flash("Account information updated successfully!", 'success')

    conn.close()

    return render_template("account.html", user_info=user_info)

# Route to display user's posts
@app.route("/posts")
def user_posts():
    if 'email' not in session:
        flash("You must be logged in to view your posts.", 'error')
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch user's posts from the database
    user_posts = cursor.execute("SELECT * FROM items WHERE email = ?", (session['email'],)).fetchall()

    conn.close()

    return render_template("user_posts.html", user_posts=user_posts)

# Run the Flask application
if __name__ == "__main__":
    app.run(debug=True)