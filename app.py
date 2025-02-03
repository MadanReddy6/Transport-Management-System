from flask import Flask, request, redirect, url_for, render_template, session, jsonify, flash
import mysql.connector
import os
import requests
from werkzeug.utils import secure_filename
import random
import smtplib
from flask_mail import Mail, Message
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText


app = Flask(__name__)

app.secret_key = 'your secret key'
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# connecting database
try:
    conn = mysql.connector.connect(
        host='localhost',
        user="root",
        password='Reddy@656',
        database='Transportation'
    )
    cursor = conn.cursor(dictionary=True)

except mysql.connector.Error as e:
    print('Error connecting to MySQL database:', e)
    
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}




app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = '19512varsha@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'nultjpikbivsgljc'  # Use environment variable for the password

mail = Mail(app)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/registor_page')
def registor_page():
    return render_template('Register form.html')

@app.route('/Login')
def Login():
    return render_template('login.html')

@app.route('/Contactus')
def Contactus():
    return render_template('Contactus.html')


@app.route('/CarrierDB')
def CarrierDB():
    return render_template('CarrierDB.html')

@app.route('/ForwarderDB')
def ForwarderDB():
    try:
        # Fetch data related to the forwarder from the database if needed
        # cursor.execute('SELECT * FROM some_table WHERE some_condition')
        # data = cursor.fetchall()
        return render_template('ForwarderDB.html')  # , data=data if needed
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'msg': 'Failed to load ForwarderDB', 'error': str(e)}), 500

@app.route('/about')
def about():
    return render_template('About.html')

@app.route('/freight')
def freight():
    return render_template('AddTransportation.html')

@app.route('/ChangePasswordPage')
def ChangePasswordPage():
    return render_template('ChangePassword.html')


@app.route('/TransportDetails_page')
def TransportDetails_page():
    return render_template('TransportDetails.html')

@app.route('/my_account_page')
def my_account_page():
    return render_template('my_account.html')

@app.route('/forgot_password_page')
def forgot_password_page():
    return render_template('forgot_password.html')



@app.route('/Register', methods=['POST'])
def Register():
    if request.method == 'POST':
        try:
            Registered_as = request.form.get('Registered_as', '')
            login_id = request.form.get('Loginid', '')
            password = request.form.get('Password', '')
            name = request.form.get('name', '')
            email = request.form.get('Email', '')
            phone = request.form.get('mobilenum', '')
            date_of_birth = request.form.get('dob', '')
            address_line1 = request.form.get('address1', '')
            address_line2 = request.form.get('address2', '')
            country = request.form.get('Country', '')
            state = request.form.get('State', '')
            city = request.form.get('City', '')
            photo = request.files.get('photo', None)

            # Debugging statements
            print(f"Received data: Registered_as={Registered_as}, login_id={login_id}, password={password}, name={name}, email={email}, phone={phone}, date_of_birth={date_of_birth}, address_line1={address_line1}, address_line2={address_line2}, country={country}, state={state}, city={city}, photo={photo}")

            cursor.execute('SELECT * FROM Users WHERE login_id = %s', (login_id,))
            account = cursor.fetchone()
            cursor.fetchall()
            if account:
                return jsonify({'msg': 'Account already exists!'}), 400
            else:
                if photo:
                    photo_filename = secure_filename(photo.filename)
                    photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
                else:
                    photo_filename = None
                
                cursor1 = conn.cursor()
                cursor2 = conn.cursor()
                
                cursor1.execute('INSERT INTO Users (register_as, login_id, password) VALUES (%s, %s, %s)', (Registered_as, login_id, password))
                user_id = cursor1.lastrowid
                print(f"Inserted into Users: user_id={user_id}")

                cursor2.execute('INSERT INTO User_Details (user_id, full_name, email, mobile_number, date_of_birth, address_line1, address_line2, country, state, city, photo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (user_id, name, email, phone, date_of_birth, address_line1, address_line2, country, state, city, photo_filename))
                print(f"Inserted into User_Details: user_id={user_id}, full_name={name}, email={email}, mobile_number={phone}, date_of_birth={date_of_birth}, address_line1={address_line1}, address_line2={address_line2}, country={country}, state={state}, city={city}, photo={photo_filename}")

                conn.commit()
                cursor1.close()
                cursor2.close()
                
                return jsonify({'msg': 'You have successfully registered!', 'redirect_url': url_for('index')}), 200
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'msg': 'An error occurred', 'error': str(e)}), 500
            
    return jsonify({'msg': 'Invalid request method'}), 400



@app.route('/add_transportation', methods=['POST'])
def add_transportation():
    if 'loggedin' not in session:
        return jsonify({'msg': 'User not logged in'}), 401

    login_id = session['login_id']
    cursor.execute('SELECT user_id FROM Users WHERE login_id = %s', (login_id,))
    user = cursor.fetchone()
    if not user:
        return jsonify({'msg': 'User not found'}), 404

    user_id = user['user_id']
    title = request.form.get('title', '').strip()
    from_city = request.form.get('PickupCity', '').strip()
    to_city = request.form.get('DeliveryCity', '').strip()
    quantity = request.form.get('quantity', '').strip()
    pickup_date = request.form.get('pickup_date', '').strip()
    delivery_date = request.form.get('delivery_date', '').strip()
    publishing_date = request.form.get('publishing_date', '').strip()
    pickup_country = request.form.get('PickupCountry', '').strip()
    delivery_country = request.form.get('DeliveryCountry', '').strip()
    length_cm = request.form.get('length_cm', '').strip()
    width_cm = request.form.get('width_cm', '').strip()
    height_cm = request.form.get('height_cm', '').strip()
    price = request.form.get('price', '').strip()
    weight_kg = request.form.get('weight_kg', '').strip()
    image = request.files.get('image', None)
    pickup_address = request.form.get('pickup_address', '').strip()
    drop_address = request.form.get('drop_address', '').strip()
    description = request.form.get('description', '').strip()

    if image:
        image_filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        image.save(image_path)
    else:
        image_filename = None

    try:
        cursor.execute('''
            INSERT INTO Transport (user_id, title, from_city, to_city, quantity, pickup_date, delivery_date, publishing_date, pickup_country, delivery_country, length_cm, width_cm, height_cm, price, weight_kg, image, pickup_address, drop_address, description, archive)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0)
        ''', (user_id, title, from_city, to_city, quantity, pickup_date, delivery_date, publishing_date, pickup_country, delivery_country, length_cm, width_cm, height_cm, price, weight_kg, image_filename, pickup_address, drop_address, description))

        conn.commit()
        return jsonify({'msg': 'Transportation added successfully', 'redirect_url': url_for('ForwarderDB')}), 200
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({'msg': 'Failed to add transportation', 'error': str(err)}), 500
    return

from flask import session

@app.route('/archive_page')
def archive_page():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'msg': 'User not logged in'}), 401

        page = request.args.get('page', 1, type=int)
        per_page = 3
        search = request.args.get('search', '', type=str)

        query = '''
            SELECT t.transport_id, t.title, u.full_name, u.mobile_number, u.email, t.publishing_date, t.from_city, t.to_city, t.quantity, t.pickup_date, t.delivery_date, t.publishing_date, t.pickup_country, t.delivery_country, t.length_cm, t.width_cm, t.height_cm, t.price, t.weight_kg, t.image, t.pickup_address, t.drop_address, t.description
            FROM Transport t
            JOIN User_Details u ON t.user_id = u.user_id
            WHERE t.archive = 1 AND t.user_id = %s
        '''
        params = [user_id]
        if search:
            wildcard_search = f'%{search}%'
            query += ' AND t.title LIKE %s'
            params.append(wildcard_search)

        cursor.execute(query, params)
        archived_transports = cursor.fetchall()
        total = len(archived_transports)
        archived_transports = archived_transports[(page - 1) * per_page: page * per_page]

        return render_template('archive.html', transports=archived_transports, page=page, per_page=per_page, total=total, search=search, min=min)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'msg': 'Failed to load archived transports', 'error': str(e)}), 500

@app.route('/PlaceOrder_page/<int:transport_id>')
def PlaceOrder_page(transport_id):
    try:
        cursor.execute('''
            SELECT t.transport_id, t.title, t.publishing_date, t.from_city, t.to_city, t.quantity, t.pickup_date, t.delivery_date, t.publishing_date, t.pickup_country, t.delivery_country, t.length_cm, t.width_cm, t.height_cm, t.price, t.weight_kg, t.image, t.pickup_address, t.drop_address, t.description
            FROM Transport t
            JOIN User_Details u ON t.user_id = u.user_id
            WHERE t.transport_id = %s
        ''', (transport_id,))
        transport = cursor.fetchone()
        if not transport:
            return jsonify({'msg': 'Transport not found'}), 404
        return render_template('PlaceOrder.html', transport=transport)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'msg': 'Failed to load transport details', 'error': str(e)}), 500


@app.route('/AllOffers_page')
def AllOffers_page():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 3
        search = request.args.get('search', '', type=str)

        query = '''
            SELECT o.offer_id, o.transport_id, o.image, o.requestor_name, o.email, o.contact_number, o.freight_title, o.publishing_date, c.full_name AS carrier_name, c.email AS carrier_email, c.mobile_number AS carrier_contact, o.message
            FROM Offer o
            JOIN Transport t ON o.transport_id = t.transport_id
            JOIN User_Details c ON t.user_id = c.user_id
            WHERE c.user_id = %s
        '''
        params = [session['user_id']]
        if search:
            wildcard_search = f'%{search}%'
            query += ' AND o.freight_title LIKE %s'
            params.append(wildcard_search)

        cursor.execute(query, params)
        offers = cursor.fetchall()
        total = len(offers)
        offers = offers[(page - 1) * per_page: page * per_page]

        return render_template('AllOffers.html', offers=offers, page=page, per_page=per_page, total=total, search=search, min=min)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'msg': 'Failed to load offers', 'error': str(e)}), 500


@app.route('/TransportDetails/<int:transport_id>')
def TransportDetails(transport_id):
    try:
        cursor.execute('''
            SELECT t.transport_id, t.title, t.publishing_date, t.from_city, t.to_city, t.quantity, t.pickup_date, t.delivery_date, t.pickup_address, t.drop_address, t.description, t.image, u.full_name as requistor_name, u.email, u.mobile_number as contact_number
            FROM Transport t
            JOIN User_Details u ON t.user_id = u.user_id
            WHERE t.transport_id = %s
        ''', (transport_id,))
        transport = cursor.fetchone()
        if not transport:
            return jsonify({'msg': 'Transport not found'}), 404
        return render_template('TransportDetails.html', transport=transport)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'msg': 'Failed to load transport details', 'error': str(e)}), 500

# all freight in carrier
@app.route('/AllFreights')
def AllFreights():
    return render_template('AllFreights.html')

@app.route('/AllFreightInCarrier')
def AllFreightInCarrier():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 4
        search = request.args.get('search', '', type=str)

        query = '''
            SELECT t.transport_id, t.title, t.publishing_date, t.from_city, t.to_city, t.quantity,t.price, t.pickup_date, t.delivery_date, t.pickup_address, t.drop_address, t.description, t.image, u.full_name as requistor_name, u.email, u.mobile_number as contact_number
            FROM Transport t
            JOIN User_Details u ON t.user_id = u.user_id
        '''
        params = []
        if search:
            wildcard_search = f'%{search}%'
            query += ' WHERE t.title LIKE %s'
            params.append(wildcard_search)

        cursor.execute(query, params)
        freights = cursor.fetchall()
        total = len(freights)
        freights = freights[(page - 1) * per_page: page * per_page]
        print(f"Freights: {freights}")

        if not freights:
            flash('No records found', 'danger')
            
        return render_template('AllFreightInCarrier.html', freights=freights, page=page, per_page=per_page, total=total, search=search, min=min)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'msg': 'Failed to load freights', 'error': str(e)}), 500

# Replace this with your actual API key
API_KEY = 'ZGJNbFJ6ZkZpWHBoR3pvZnlJb09wUVZIQmdJOXlRS0VHSDJ6dUpsdg=='
BASE_URL = "https://api.countrystatecity.in/v1"

@app.route('/countries', methods=['GET'])
def get_countries():
    error = None
    url = f"{BASE_URL}/countries"
    headers = {"X-CSCAPI-KEY": API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print("API Response:", response.json())  # Debugging
        countries = [{"id": country["iso2"], "name": country["name"]} 
                     for country in response.json()]
        return jsonify(countries)
    else:
        print("Error fetching countries:", response.status_code, response.text)  # Debugging
        error = "Failed to fetch countries"
        return jsonify({"error": error}), response.status_code

# Fetch states by country
@app.route('/countries/<country_code>/states', methods=['GET'])
def get_states(country_code):
    error = None
    url = f"{BASE_URL}/countries/{country_code}/states"
    headers = {"X-CSCAPI-KEY": API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        states = [{"id": state["iso2"], "name": state["name"]} 
                  for state in response.json()]
        return jsonify(states)
    else:
        error = "Failed to fetch states"
        return jsonify({"error": error}), response.status_code

# Fetch cities by state and country
@app.route('/countries/<country_code>/states/<state_code>/cities', methods=['GET'])
def get_cities(country_code, state_code):
    error = None
    url = f"{BASE_URL}/countries/{country_code}/states/{state_code}/cities"
    headers = {"X-CSCAPI-KEY": API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        cities = [{"id": city["id"], "name": city["name"]} for city in response.json()]
        return jsonify(cities)
    else:
        error = "Failed to fetch cities"
        return jsonify({"error": error}), response.status_code
# login page

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        id = request.form['Id']
        password = request.form['Password']
        print(f'--------------------{id} {password}')
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE login_id = %s AND password = %s', (id, password,))
        account = cursor.fetchone()
        print(f'--------------------{account}')
        if account:
            session['loggedin'] = True
            session['login_id'] = account['login_id']
            session['user_id'] = account['user_id']
            session['Registered_as'] = account['register_as']
            print(f"--------------------{session['login_id']}")
            # session['full_name'] = account['full_name']
            Registered_as = account['register_as']
            print(f'*********************{Registered_as}')
            if Registered_as == 'Carrier':
                return jsonify({'redirect_url': url_for('CarrierDB')}), 200
            elif Registered_as == 'Forwarder':
                return jsonify({'redirect_url': url_for('ForwarderDB')}), 200
        else:
            flash('Incorrect username / password!', 'danger')
            return jsonify({'msg': 'Incorrect username / password!'}), 401
        
    return render_template('login.html', msg=msg), 200

#logout


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('login_id', None)
    session.pop('full_name', None)
    return redirect(url_for('index'))

@app.route('/change_password', methods=['POST'])
def change_password():
    if 'loggedin' not in session:
        flash('User not logged in', 'danger')
        return jsonify({'msg': 'User not logged in'}), 401

    user_id = session['user_id']
    current_password = request.form.get('currentPassword', '')
    new_password = request.form.get('newPassword', '')

    cursor.execute('SELECT password FROM Users WHERE user_id = %s', (user_id,))
    user = cursor.fetchone()
    if not user or user['password'] != current_password:
        flash('Current password is incorrect', 'danger')
        return jsonify({'msg': 'Current password is incorrect'}), 400

    try:
        cursor.execute('UPDATE Users SET password = %s WHERE user_id = %s', (new_password, user_id))
        conn.commit()
        flash('Password changed successfully!', 'success')
        return jsonify({'msg': 'Password changed successfully'}), 200
    except mysql.connector.Error as err:
        flash('Failed to change password', 'danger')
        return jsonify({'msg': 'Failed to change password', 'error': str(err)}), 500


@app.route('/transportreport_page')
def transportreport_page():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 3
        search = request.args.get('search', '', type=str)
        user_id = session['user_id']

        query = '''
            SELECT t.transport_id, t.title, t.publishing_date, t.from_city, t.to_city, t.quantity, t.pickup_date, t.delivery_date, t.pickup_address, t.drop_address, t.description, t.image, u.full_name as requistor_name, u.email, u.mobile_number as contact_number
            FROM Transport t
            JOIN User_Details u ON t.user_id = u.user_id
            WHERE t.user_id = %s AND t.archive = 0
        '''
        params = [user_id]
        if search:
            wildcard_search = f'%{search}%'
            query += ' AND t.title LIKE %s'
            params.append(wildcard_search)
        
        cursor.execute(query, params)
        transports = cursor.fetchall()
        print("=============",transports)
        total = len(transports)
        transports = transports[(page - 1) * per_page: page * per_page]

        return render_template('Transportreport.html', transports=transports, page=page, per_page=per_page, total=total, search=search, min=min)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'msg': 'Failed to load transport report', 'error': str(e)}), 500

@app.route('/all_freights')
def all_freights():
    try:
        cursor.execute('''
            SELECT t.transport_id, t.title, t.publishing_date, t.from_city, t.to_city, t.quantity, t.pickup_date, t.delivery_date, t.pickup_address, t.drop_address, t.description, t.image, u.full_name as requistor_name, u.email, u.mobile_number as contact_number
            FROM Transport t
            JOIN User_Details u ON t.user_id = u.user_id
        ''')
        freights = cursor.fetchall()
        print(f"/////////////aLLFreights: {freights}")
        return render_template('AllFreights.html', freights=freights)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'msg': 'Failed to load freights', 'error': str(e)}), 500

@app.route('/forwarders_freights')
def forwarders_freights():
    try:
        cursor.execute('''
            SELECT t.transport_id, t.title, t.publishing_date, t.from_city, t.to_city, t.quantity, t.pickup_date, t.delivery_date, t.pickup_address, t.drop_address, t.description, t.image, u.full_name as requistor_name, u.email, u.mobile_number as contact_number
            FROM Transport t
            JOIN User_Details u ON t.user_id = u.user_id
            WHERE u.register_as = 'Forwarder'
        ''')
        freights = cursor.fetchall()
        print(f"/////////////aLLFreights: {freights}")
        return render_template('ForwardersFreights.html', freights=freights)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'msg': 'Failed to load forwarders freights', 'error': str(e)}), 500

@app.route('/place_order', methods=['POST'])
def place_order():
    if 'loggedin' not in session:
        return jsonify({'msg': 'User not logged in'}), 401

    transport_id = request.form.get('transport_id')
    order_details = request.form.get('orderDetails')
    message = request.form.get('message')
    print(f'=================={transport_id} {order_details} {message}')

    if not transport_id or not order_details:
        return jsonify({'msg': 'Transport ID and Order Details are required'}), 400

    try:
        # Fetch transport details using a separate cursor
        cursor1 = conn.cursor(dictionary=True)
        cursor1.execute('''
            SELECT t.image, t.title AS freight_title, t.publishing_date, u.full_name AS requestor_name, u.email, u.mobile_number AS contact_number
            FROM Transport t
            JOIN User_Details u ON t.user_id = u.user_id
            WHERE t.transport_id = %s
        ''', (transport_id,))
        transport = cursor1.fetchone()
        cursor1.close()
        print(f".....................{transport}")

        if not transport:
            return jsonify({'msg': 'Transport not found'}), 404

        # Fetch carrier details using the logged-in user's ID
        cursor2 = conn.cursor(dictionary=True)
        cursor2.execute('''
            SELECT full_name, email, mobile_number
            FROM User_Details
            WHERE user_id = %s
        ''', (session['user_id'],))
        carrier = cursor2.fetchone()
        cursor2.close()
        print(f"Carrier details: {carrier}")

        if not carrier:
            return jsonify({'msg': 'Carrier not found'}), 404

        # Insert into Offer table using the main cursor
        cursor.execute('''
            INSERT INTO Offer (transport_id, image, freight_title, publishing_date, requestor_name, email, contact_number, message)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (transport_id, transport['image'], transport['freight_title'], transport['publishing_date'], carrier['full_name'], carrier['email'], carrier['mobile_number'], message))
        conn.commit()
        flash('Order placed successfully!', 'success')
        return redirect(url_for('AllFreightInCarrier'))
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flash('Failed to place order', 'danger')
        return redirect(url_for('AllFreightInCarrier'))

@app.route('/update_account', methods=['POST'])
def update_account():
    if 'loggedin' not in session:
        return jsonify({'msg': 'User not logged in'}), 401

    user_id = session['user_id']
    full_name = request.form.get('full_name', '')
    email = request.form.get('email', '')
    mobile_number = request.form.get('mobile_number', '')
    date_of_birth = request.form.get('date_of_birth', '')
    address_line1 = request.form.get('address_line1', '')
    address_line2 = request.form.get('address_line2', '')
    country = request.form.get('country', '')
    state = request.form.get('state', '')
    city = request.form.get('city', '')
    photo = request.files.get('photo', None)

    try:
        if photo:
            photo_filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
        else:
            cursor.execute('SELECT photo FROM User_Details WHERE user_id = %s', (user_id,))
            photo_filename = cursor.fetchone()['photo']

        cursor.execute('''
            UPDATE User_Details
            SET full_name = %s, email = %s, mobile_number = %s, date_of_birth = %s, address_line1 = %s, address_line2 = %s, country = %s, state = %s, city = %s, photo = %s
            WHERE user_id = %s
        ''', (full_name, email, mobile_number, date_of_birth, address_line1, address_line2, country, state, city, photo_filename, user_id))
        conn.commit()
        flash('Account updated successfully!', 'success')
        return redirect(url_for('my_account'))
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flash('Failed to update account', 'danger')
        return redirect(url_for('my_account'))

@app.route('/my_account')
def my_account():
    if 'loggedin' not in session:
        return redirect(url_for('Login'))

    user_id = session['user_id']
    try:
        cursor.execute('''
            SELECT u.login_id, u.register_as, d.full_name, d.email, d.mobile_number, d.date_of_birth, d.address_line1, d.address_line2, d.country, d.state, d.city, d.photo
            FROM Users u
            JOIN User_Details d ON u.user_id = d.user_id
            WHERE u.user_id = %s
        ''', (user_id,))
        user = cursor.fetchone()
        print(f"User details: {user}")
        if not user:
            return jsonify({'msg': 'User not found'}), 404
        return render_template('my_account.html', user=user)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'msg': 'Failed to load user details', 'error': str(e)}), 500


@app.route('/archive_transport', methods=['POST'])
def archive_transport():
    if 'loggedin' not in session:
        flash('User not logged in', 'danger')
        return jsonify({'msg': 'User not logged in'}), 401

    transport_id = request.form.get('transport_id')
    try:
        cursor.execute('UPDATE Transport SET archive = 1 WHERE transport_id = %s', (transport_id,))
        conn.commit()
        flash('Transport archived successfully!', 'success')
        return redirect(url_for('transportreport_page'))
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flash('Failed to archive transport', 'danger')
        return redirect(url_for('transportreport_page'))

@app.route('/unarchive_transport', methods=['POST'])
def unarchive_transport():
    if 'loggedin' not in session:
        flash('User not logged in', 'danger')
        return jsonify({'msg': 'User not logged in'}), 401
    user_id = session['user_id']
    transport_id = request.form.get('transport_id')
    try:
        cursor.execute('UPDATE Transport SET archive = 0 WHERE transport_id = %s', (transport_id,))
        conn.commit()
        flash('Transport unarchived successfully!', 'success')
        return redirect(url_for('archive_page'))
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flash('Failed to unarchive transport', 'danger')
        return redirect(url_for('archive_page'))

@app.route('/user_orders_page')
def user_orders_page():
    return render_template('userorders.html')

@app.route('/user_orders')
def user_orders():
    if 'loggedin' not in session:
        return redirect(url_for('Login'))

    login_id = session['login_id']
    print(f"login id: {login_id}")
    try:
        cursor.execute('''
            SELECT o.offer_id, o.image, o.freight_title, t.from_city, t.to_city, t.quantity, t.price, t.pickup_country, t.delivery_country, t.pickup_date, t.delivery_date, t.description
            FROM Offer o
            JOIN Transport t ON o.transport_id = t.transport_id
            WHERE o.offer_id = %s
        ''', (login_id,))
        orders = cursor.fetchall()
        print(f"User orders: {orders}")
        if not orders:
            # flash('No orders found', 'info')
            pass
        return render_template('userorders.html', orders=orders)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'msg': 'Failed to load user orders', 'error': str(e)}), 500

@app.route('/edit_order/<int:offer_id>', methods=['GET', 'POST'])
def edit_order(offer_id):
    if 'loggedin' not in session:
        return redirect(url_for('Login'))

    if request.method == 'POST':
        # Handle form submission for editing the order
        # ... handle form data and update the order in the database ...
        return redirect(url_for('user_orders'))

    try:
        cursor.execute('''
            SELECT o.offer_id, o.transport_id, o.image, o.freight_title, t.from_city, t.to_city, t.quantity, t.price, t.pickup_country, t.delivery_country
            FROM Offer o
            JOIN Transport t ON o.transport_id = t.transport_id
            WHERE o.offer_id = %s
        ''', (offer_id,))
        order = cursor.fetchone()
        if not order:
            return jsonify({'msg': 'Order not found'}), 404
        return render_template('edit_order.html', order=order)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'msg': 'Failed to load order details', 'error': str(e)}), 500
    
    
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        # Create the email content
        msg = Message(subject, sender=app.config['MAIL_USERNAME'], recipients=['19512varsha@gmail.com'])
        msg.body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
        print("==========================",msg)

        try:
            mail.send(msg)
            flash('Your message has been sent successfully!', 'success')
        except Exception as e:
            # logging.error("Error sending email: %s", e)
            flash('An error occurred while sending your message. Please try again later.', 'danger')

        return redirect(url_for('contact'))

    return render_template('Contactus.html')

if __name__ == '__main__':
    app.run(debug=True)


