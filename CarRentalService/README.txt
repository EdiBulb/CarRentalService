Car Rental Service

This project is a simple car rental service application built with Python. It allows users to register, log in, manage car inventories, and handle car rentals.

Getting Started

Prerequisites

Before running this project, you'll need to have Python installed on your computer along with the following packages:
- mysql-connector-python
- bcrypt
- python-dotenv

Installation

1. Clone the repository:
   git clone https://github.com/EdiBulb/CarRentalService.git

2. Navigate to the project directory:
   cd CarRentalService

3. Install the required packages:
   pip install -r requirements.txt

Environment Setup
Create a .env file in the root directory of the project with the following contents:

DB_HOST=localhost
DB_USER=yourusername
DB_PASSWORD=yourpassword
DB_NAME=car_rental_db

Ensure to replace yourusername and yourpassword with your MySQL credentials.

Running the Application

To start the application, run the following command in the terminal at the project's root directory:
python main.py

This will start the application, and you should see the following interface in your terminal:

1. Sign Up
2. Log In
3. Exit
Choose an option:

Follow the on-screen prompts to navigate through the application.

Features
- User registration and login
- Admin and customer role management
- Car inventory management
- Rental operations: creating, approving, and completing rentals

Contributing
Contributions to this project are welcome. Please ensure to update tests as appropriate.
Contribution Guidelines
To contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new branch (git checkout -b feature-branch).
3. Make changes and run tests.
4. Commit your changes (git commit -am 'Add some feature').
5. Push to the branch (git push origin feature-branch).
6. Create a new Pull Request.
Ensure you update the tests and provide documentation on what your feature does and how to use it.

License
This project is licensed under the MIT License - see the LICENSE file for details.

Contact Information
For support or queries, please open an issue on the GitHub issues page or contact us at gnsqud24@naver.com
