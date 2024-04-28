from flask import Flask, render_template, request, send_file
from io import BytesIO
from flask_mysqldb import MySQL
from mysql.connector import (connection)


app = Flask(__name__)

mysql = MySQL(app)

cnx = connection.MySQLConnection(user='jacobkadari', password='password',
                                 host='127.0.0.1',
                                 database='my_base')

@app.route('/')
def index():
    # Search for items by title
    search_query = request.args.get('search', '')

    cursor = connection.cursor()
    query = "SELECT id, title, description, last_known_location FROM items WHERE title LIKE %s"
    cursor.execute(query, ('%' + search_query + '%',))

    items = cursor.fetchall()
    return render_template('index.html', items=items)

@app.route('/item/<int:item_id>')
def item_details(item_id):
    # Fetch the item by ID
    cursor = connection.cursor()
    query = "SELECT id, title, description, last_known_location, image FROM items WHERE id = %s"
    cursor.execute(query, (item_id,))

    item = cursor.fetchone()
    return render_template('item.html', item=item)

@app.route('/image/<int:item_id>')
def get_image(item_id):
    # Fetch image by item ID
    cursor = connection.cursor()
    query = "SELECT image FROM items WHERE id = %s"
    cursor.execute(query, (item_id,))
    
    image_data = cursor.fetchone()
    
    if image_data and image_data[0]:
        return send_file(BytesIO(image_data[0]), mimetype='image/jpeg')
    else:
        return 'Image not found', 404

if __name__ == "__main__":
    app.run(debug=True)