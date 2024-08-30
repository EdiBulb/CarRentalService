import mysql.connector
import datetime
import bcrypt # enhancing password security
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables

# Use environment variables
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')


# Set up database connection
def create_connection():
    # Retrieve environment variables
    host = os.getenv('DB_HOST')
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    database = os.getenv('DB_NAME')

    # Use a try statement as the connection attempt may fail.
    try:
        # Connect if the database exists.
        conn = mysql.connector.connect(
            # Attempt to connect to the database using the retrieved environment variables.
            host=host, 
            user=user, 
            password=password, 
            database=database
        )
        return conn # Return the connected object. Through this connection object conn, you can send queries to the database or retrieve data from it.
    
    except mysql.connector.Error as err:
        if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            # Create the database if it does not exist
            conn = mysql.connector.connect(host=host, user=user, password=password)
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE {database}")
            conn.database = database
            create_tables(conn)
            return conn

        # Print an error message if the database connection fails
        else:
            print("Database connection failed:", err)
            return None

# Set up default tables.
def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE users (
        user_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255),
        email VARCHAR(255) UNIQUE,
        password VARCHAR(255),
        role ENUM('admin', 'customer')
    )""")
    cursor.execute("""
    CREATE TABLE cars (
        car_id INT AUTO_INCREMENT PRIMARY KEY,
        make VARCHAR(255),
        model VARCHAR(255),
        year YEAR,
        mileage INT,
        available_now BOOLEAN,
        min_rent_period INT,
        max_rent_period INT
    )""")
    cursor.execute("""
    CREATE TABLE rentals (
        rental_id INT AUTO_INCREMENT PRIMARY KEY,
        car_id INT,
        user_id INT,
        start_date DATE,
        end_date DATE,
        total_fee DECIMAL(10, 2),
        status ENUM('on process', 'active', 'completed', 'cancelled', 'returned'),
        FOREIGN KEY (car_id) REFERENCES cars(car_id),
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )""")
    conn.commit()

    

# Enhance password security
def hash_password(password):
    salt = bcrypt.gensalt() # Generate salt for hashing
    return bcrypt.hashpw(password.encode('utf-8'), salt) # Perform hashing using the encoded password and salt

# Verify the password
def check_password(stored_password, provided_password):
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password) # compare the passwords to check if they match and return True or False


    

# Define the User class
class User:
    def __init__(self, user_id: int, name: str, email: str):
        self.user_id = user_id
        self.name = name
        self.email = email
    

    # Polymorphism
    def perform_task(self):
        raise NotImplementedError("Each subclass must implement this method.")


# Customer class (inheritance)
class Customer(User):
    def __init__(self, user_id: int, name: str, email: str):
        super().__init__(user_id, name, email)
        self.role = 'customer'

    # Polymorphism
    def perform_task(self):
        print(f"\nThere are {self.role}'s task.")

# Admin class (inheritance)
class Admin(User):
    def __init__(self, user_id: int, name: str, email: str):
        super().__init__(user_id, name, email)
        self.role = 'admin'

    # Polymorphism
    def perform_task(self):
        print(f"\nThere are {self.role}'s task.")

# Singleton design pattern
class SingletonMeta(type):
    """
    Define a Singleton metaclass to be used by all manager classes
    """
    _instances = {} # Store the Singleton instance for the class type
    
    def __call__(cls, *args, **kwargs): # Called when creating a class instance
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
    
# Define the UserManager class - handles database operations for user registration and login
class UserManager(metaclass=SingletonMeta):
    def __init__(self, db_connection):
        self.conn = db_connection
        self.cursor = self.conn.cursor()
    
    # Register in the User database.
    def register_user(self, name: str, email: str, password: str, role: str):
        # If the User is neither a customer nor an admin during registration
        if role not in ['customer', 'admin']:
            raise ValueError("Role must be 'customer' or 'admin'")

        # Password hashing
        hashed_password = hash_password(password)

        try:
            # Insert User data into the database.
            self.cursor.execute("INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)", (name, email, hashed_password, role))
            self.conn.commit() # Command to complete the operation

            print(f"\nUser {name} registered successfully with role {role}.")
            # In case of incorrect data input.
        except mysql.connector.Error as err:
            raise ValueError(f"Database error: {err}")

    # Log in
    def login(self, email: str, password: str):
        # Retrieve information from the Users table
        self.cursor.execute("SELECT user_id, name, password, role FROM users WHERE email = %s", (email,)) #Retrieve the email
        result = self.cursor.fetchone() 
        
        # Login successful
        if result: # If a matching email is found
            user_id, name, stored_password, role = result
            # Check if it matches the hashed password
            if check_password(stored_password.encode('utf-8'), password):
                # Do not store the password in the object; discard it immediately after a successful login
                print(f"\nLogged in as {name} with role {role}")
                if role == 'admin':
                    return Admin(user_id, name, email) # Return the Admin object
                else:
                    return Customer(user_id, name, email) # Return the Customer object
            else:
                raise ValueError("Incorrect password")
        # Login failed
        else:
            raise ValueError("Incorrect email or password")
        
        

# CarManager class - Handles car management
class CarManager(metaclass=SingletonMeta):
    def __init__(self, db_connection):
        self.conn = db_connection
        self.cursor = self.conn.cursor()

    # Add a car (Admin's option)
    def add_car(self, make, model, year, mileage, available_now, min_rent_period, max_rent_period):
        try:
            # Insert query statement
            self.cursor.execute("INSERT INTO cars (make, model, year, mileage, available_now, min_rent_period, max_rent_period) VALUES (%s, %s, %s, %s, %s, %s, %s)", (make, model, year, mileage, available_now, min_rent_period, max_rent_period))
            self.conn.commit() 
            print("Car added successfully.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")

    # Update a car (Admin's option)
    def update_car(self, car_id, make, model, year, mileage, available_now, min_rent_period, max_rent_period):
        try:
            self.cursor.execute("UPDATE cars SET make=%s, model=%s, year=%s, mileage=%s, available_now=%s, min_rent_period=%s, max_rent_period=%s WHERE car_id=%s", (make, model, year, mileage, available_now, min_rent_period, max_rent_period, car_id))
            self.conn.commit()

            # If the number of rows affected by the previous query is one or more, it means that a change has been made
            if self.cursor.rowcount > 0: 
                print("Car updated successfully.")
            # if there are no changes
            else:
                print("Car not found.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")

    # Delete a car (Admin's option)
    def delete_car(self, car_id):
        try:
            # Delete query statement
            self.cursor.execute('DELETE FROM cars WHERE car_id=%s', (car_id,))
            self.conn.commit()
            # If the number of affected rows is one or more, it means that the deletion was successful
            if self.cursor.rowcount > 0:
                print("Car deleted successfully.")
            # if there are no changes
            else:
                print("Car not found.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")


    # Retrieve the car list (Admin's option)
    def list_cars(self):
        print("car_id, make, model, year, mileage, available_now, min_rent_period, max_rent_period\n")
        self.cursor.execute('SELECT * FROM cars')
        cars = self.cursor.fetchall()
        for car in cars:
            print(car)

# Rental Manager class 
class RentalManager(metaclass=SingletonMeta):
    def __init__(self, db_connection):
        self.conn = db_connection
        self.cursor = self.conn.cursor()

    # Create a rental booking (Customer's option)
    def create_rental(self, car_id, user_id, start_date, end_date):

        # Convert the date string into a datetime.date object
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

        # Check availability for rental
        self.cursor.execute("SELECT available_now FROM cars WHERE car_id = %s", (car_id,))
        available = self.cursor.fetchone()
        
        # In case of unavailability for rental
        if not available[0]:
            print("This car is not available for rental.")
            return
        
        # In case of availability for rental.
        # Calculate rental fee ($50 per day)
        days = (end_date - start_date).days + 1
        total_fee = days * 50
        
        # Insert the requested rental car into the rentals table - status: on process
        try:
            self.cursor.execute("INSERT INTO rentals (car_id, user_id, start_date, end_date, total_fee, status) VALUES (%s, %s, %s, %s, %s, 'on process')", (car_id, user_id, start_date, end_date, total_fee))
            self.conn.commit()
            print("Rental created successfully. Total fee: ${:.2f}".format(total_fee))
        except mysql.connector.Error as err:
            print(f"Error: {err}")

    
    # List of rented cars (Customer's option)
    def list_rentals(self):
        self.cursor.execute("SELECT * FROM rentals WHERE status <> 'returned'")
        rentals = self.cursor.fetchall()

        # If there are no rented cars
        if len(rentals) == 0:
            print("\nYou do not have booking yet")

        # If there are rented cars
        else: 
            print("\n[rental_id, car_id, user_id, start_date, end_date, total_fee, status]\n")
            for rental in rentals:
                start_date_formatted = rental[3].strftime('%Y-%m-%d')  # Convert to 'YYYY-MM-DD' format
                end_date_formatted = rental[4].strftime('%Y-%m-%d')    # Convert to 'YYYY-MM-DD' format
                print(f"{rental[0]}, {rental[1]}, {rental[2]}, {start_date_formatted}, {end_date_formatted}, {rental[5]}, {rental[6]}")

    # Approve rental request. (Admin's option)
    def approve_rental(self, rental_id):
        try:
            self.cursor.execute("UPDATE rentals SET status = 'active' WHERE rental_id = %s AND status = 'on process'", (rental_id,))
            self.conn.commit()

            # If the number of affected rows is one or more, it means the approval was successful
            if self.cursor.rowcount > 0:
                print("Rental approved successfully.")
            else:
                print("Rental not found or already processed.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")

    # Cancel rental request (Admin's option)
    def cancel_rental(self, rental_id):
        try:
            self.cursor.execute("UPDATE rentals SET status = 'cancelled' WHERE rental_id = %s", (rental_id,))
            self.conn.commit()

            # If the number of affected rows is one or more, it means that the deletion was successful
            if self.cursor.rowcount > 0:
                print("Rental cancelled successfully.")
            else:
                print("Rental not found.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")

    # Complete (end) the rental (Admin's option)
    def complete_rental(self, rental_id):
        try:
            self.cursor.execute("UPDATE rentals SET status = 'completed' WHERE rental_id = %s", (rental_id,))
            self.conn.commit()

            # If the number of affected rows is one or more, it means the rental has been completed
            if self.cursor.rowcount > 0:
                print("Rental completed successfully.")
            else:
                print("Rental not found.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")

     # Process rental return (Customer's option)
    def return_rental(self, rental_id):
        try:
            self.cursor.execute("UPDATE rentals SET status = 'returned' WHERE rental_id = %s", (rental_id,))
            self.conn.commit()

            # If the number of affected rows is one or more, it means the car has been successfully returned
            if self.cursor.rowcount > 0:
                print("Rental returned successfully.")
            else:
                print("Rental not found.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")

# User registration feature.
def sign_up(user_manager):
    name = input("Enter your name: ")
    email = input("Enter your email: ")
    password = input("Enter your password: ")
    role = input("Enter your role (customer/admin): ")

    if role not in ['customer', 'admin']:
        print("Invalid role specified. Role must be 'customer' or 'admin'.")
        return
    
    try:
        user_manager.register_user(name, email, password, role) # Send information to the database
    except ValueError as ve:
        print(f"Error: {ve}")

# User login feature
def log_in(user_manager):
    email = input("Enter your email: ")
    password = input("Enter your password: ")
    try:
        return user_manager.login(email, password) # Send information to the database and receive an Admin or Customer object in return
    except ValueError as ve:
        print(f"Error: {ve}")
        return None
    
# Initial screen
def main_menu(user_manager, car_manager, rental_manager):
    while True:

        print("\n1. Sign Up")
        print("2. Log In")
        print("3. Exit")
        choice = input("Choose an option: ")

        # sign up
        if choice == '1':
            # After calling the sign_up method, enter the member information and save it to the database.
            sign_up(user_manager) 
        # Log in
        elif choice == '2':
            # After calling the log_in method, verify the member information and return either an Admin or Customer object.
            user = log_in(user_manager) 
            if user:
                if user.role == 'admin': # If the object is an Admin
                    admin_menu(user, car_manager, rental_manager)
                elif user.role == 'customer': # If the object is a Customer
                    customer_menu(user, rental_manager)
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice, please try again.")


# If the user is an admin, the admin menu is displayed.
def admin_menu(user, car_manager, rental_manager):
    while True:

        user.perform_task() # Polymorphism

        print("\n1. Add Car")
        print("2. Update Car")
        print("3. Delete Car")
        print("4. List Cars")
        print("5. Approve Rental")
        print("6. Cancel Rental")
        print("7. Complete Rental")
        print("8. Logout")
        
        choice = input("Select an option: ")

        # When option 1 is selected, call the add_car() method of car_manager to add a new car
        if choice == '1':
            make = input("Enter car make: ")
            model = input("Enter car model: ")
            year = input("Enter car year: ")
            mileage = input("Enter car mileage: ")
            
            available_now_input = input("Is the car available now? (yes/no): ")
            available_now = 1 if available_now_input.lower() =='yes' else 0

            min_rent_period = input("Enter minimum rental period (days): ")
            max_rent_period = input("Enter maximum rental period (days): ")
            car_manager.add_car(make, model, year, mileage, available_now, min_rent_period, max_rent_period)
        # When option 2 is selected, call the update_car() method of car_manager to update the information of an existing car
        elif choice == '2':
            car_id = input("Enter car ID to update: ")
            make = input("Enter new car make: ")
            model = input("Enter new car model: ")
            year = input("Enter new car year: ")
            mileage = input("Enter new car mileage: ")
            
            available_now_input = input("Is the car available now? (yes/no): ")
            available_now = 1 if available_now_input.lower() =='yes' else 0

            min_rent_period = input("Enter minimum rental period (days): ")
            max_rent_period = input("Enter maximum rental period (days): ")
            car_manager.update_car(car_id, make, model, year, mileage, available_now, min_rent_period, max_rent_period)
        # When option 3 is selected, call the delete_car() method of car_manager to delete a car
        elif choice == '3':
            car_id = input("Enter car ID to delete: ")
            car_manager.delete_car(car_id)
        # When option 4 is selected, call the list_cars() method of car_manager to display the registered cars.
        elif choice == '4':
            car_manager.list_cars()
        # When option 5 is selected, call the approve_rental() method of rental_manager to approve the reservation
        elif choice == '5':
            rental_id = input("Enter rental ID to approve: ")
            rental_manager.approve_rental(int(rental_id))
        # When option 6 is selected, call the cancel_rental() method of rental_manager to cancel the reservation.
        elif choice == '6':
            rental_id = input("Enter rental ID to cancel: ")
            rental_manager.cancel_rental(int(rental_id))
        # When option 7 is selected, call the complete_rental() method of rental_manager to complete the reservation
        elif choice == '7':
            rental_id = input("Enter rental ID to complete: ")
            rental_manager.complete_rental(int(rental_id))
        # When option 8 is selected, log out
        elif choice == '8':
            print("Logging out...")
            break
        else:
            print("Invalid choice, please try again.")



# If the user is a customer, the customer menu is displayed.
def customer_menu(user, rental_manager):
    while True:

        user.perform_task() # Polymorphism

        print("\n1. Rent a Car")
        print("2. View Rentals")
        print("3. Return a Car")
        print("4. Logout")
        
        choice = input("Select an option: ")
        if choice == '4':
            print("Logging out...")
            break
        # If option 1 is selected, call the create_rental() method of the rental_manager to create a new rental
        elif choice == '1': 
            car_id = input("Enter car ID to rent: ")
            start_date = input("Enter start date (YYYY-MM-DD): ")
            end_date = input("Enter end date (YYYY-MM-DD): ")
            rental_manager.create_rental(int(car_id), user.user_id, start_date, end_date)
        # If option 2 is selected, call the list_rentals() method of the rental_manager to view all rentals the user has made so far.
        elif choice == '2': 
            print("\n[rental_id, car_id, user_id, start_date, end_date, total_fee, status]\n")
            rental_manager.list_rentals()
        # If option 3 is selected, call the return_rental() method of the rental_manager to return the car that the user has rented
        elif choice == '3':
                rental_id = input("Enter rental ID to return: ")
                rental_manager.return_rental(int(rental_id))
        else:
            print("Invalid choice, please try again.")


if __name__ == "__main__":


    conn = create_connection() # Attempt to connect to the database.
    
    if conn:
        print("Database connection successful.")
        # After successfully connecting, create instances of classes such as `UserManager`.
        user_manager = UserManager(conn)
        car_manager = CarManager(conn)
        rental_manager = RentalManager(conn)
        main_menu(user_manager, car_manager, rental_manager)
        conn.close()
    else:
        print("Failed to initialize database.")

