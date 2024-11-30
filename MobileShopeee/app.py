from flask import Flask, request, render_template, redirect, url_for, flash, session, jsonify
import mysql.connector
from mysql.connector import Error
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong key for production

# Database connection function
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            database='mobileshopee',
            user='root',
            password=''
        )
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

# Route to check if the database connection works
@app.route('/check_connection', methods=['GET'])
def check_connection():
    conn = get_db_connection()
    if conn:
        conn.close()  # Close connection after checking
        return jsonify({"message": "Connection successful"})
    else:
        return jsonify({"message": "Connection failed"}), 500

# Route: Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Please fill in all fields.', 'danger')
            return redirect(url_for('login'))

        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                query = "SELECT * FROM users WHERE email = %s AND password = %s"
                cursor.execute(query, (email, password))
                user = cursor.fetchone()

                if user:
                    session['user_id'] = user['id']
                    session['role'] = user['role']
                    flash('Login successful!', 'success')

                    # Redirect based on user role
                    if user['role'] == 'superadmin':
                        return redirect(url_for('superadmin_page'))
                    elif user['role'] == 'admin':
                        return redirect(url_for('admin_page'))
                    else:
                        return redirect(url_for('user_page'))
                else:
                    flash('Invalid email or password.', 'danger')
            except Error as e:
                flash('An error occurred while processing your request.', 'danger')
                print(f"Error: {e}")
            finally:
                connection.close()
        else:
            flash('Unable to connect to the database.', 'danger')
    return render_template('login.html')

# Route: Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not email or not password or not confirm_password:
            flash('Please fill in all fields.', 'danger')
            return redirect(url_for('signup'))

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('signup'))

        # Email format validation
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email format.', 'danger')
            return redirect(url_for('signup'))

        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)

                # Check if email already exists
                check_query = "SELECT * FROM users WHERE email = %s"
                cursor.execute(check_query, (email,))
                if cursor.fetchone():
                    flash('Email is already registered.', 'warning')
                    return redirect(url_for('signup'))

                # Insert new user with default role 'user'
                insert_query = "INSERT INTO users (email, password, role) VALUES (%s, %s, %s)"
                cursor.execute(insert_query, (email, password, 'user'))
                connection.commit()
                flash('Account created successfully! Please log in.', 'success')
                return redirect(url_for('login'))
            except Error as e:
                flash('An error occurred while processing your request.', 'danger')
                print(f"Error: {e}")
            finally:
                connection.close()
        else:
            flash('Unable to connect to the database.', 'danger')
    return render_template('signup.html')

# Route: Superadmin Page
@app.route('/superadmin_page')
def superadmin_page():
    if session.get('role') != 'superadmin':
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))
    return "Welcome to the Superadmin Page!"  # Replace with your superadmin page template

# Route: Admin Page
@app.route('/admin_page')
def admin_page():
    if session.get('role') not in ['admin', 'superadmin']:
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))
    return "Welcome to the Admin Page!"  # Replace with your admin page template

# Route: User Page
@app.route('/user_page')
def user_page():
    if not session.get('user_id'):
        flash('Please log in to continue.', 'danger')
        return redirect(url_for('login'))
    return "Welcome to the User Page!"  # Replace with your user page template

# Route: Homepage
@app.route('/')
@app.route('/homepage')
def homepage():
    return render_template('homepage.html')  # Replace with your homepage template

if __name__ == '__main__':
    app.run(debug=True)
