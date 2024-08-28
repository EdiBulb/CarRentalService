import mysql.connector
import datetime
import bcrypt # 비밀번호 보안 강화
from dotenv import load_dotenv
import os

load_dotenv()  # 환경 변수 로드

# 환경 변수 사용
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')


# 데이터베이스 연결 설정
def create_connection():
    # 환경변수를 가져온다.
    host = os.getenv('DB_HOST')
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    database = os.getenv('DB_NAME')

    # 접속 시도가 실패할 수도 있으니 try 문을 사용
    try:
        conn = mysql.connector.connect(
            # 가져온 환경변수로 DB 접속을 시도한다.
            host=host,
            user=user,
            password=password,
            database=database
        )
        return conn # 연결된 객체를 반환한다. 이 연결객체 conn을 통해서 데이터베이스에 쿼리를 보내거나 데이터를 가져올 수 있다.

    # DB 접속 실패시 에러메세지
    except mysql.connector.Error as err:
        print("Database connection failed:", err)
        return None
    

# 비밀번호 보안 강화
def hash_password(password):
    salt = bcrypt.gensalt() # 해싱을 위한 솔트 생성
    return bcrypt.hashpw(password.encode('utf-8'), salt) # 인코딩한 password와 salt를 이용하여 해싱

# 비밀번호 확인
def check_password(stored_password, provided_password):
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password) # 일치하는지 비교하고 True or False를 반환


    

# User 클래스 정의
class User:
    def __init__(self, user_id: int, name: str, email: str):
        self.user_id = user_id
        self.name = name
        self.email = email
    

    '''고민중 - 어떤 기능을 넣을 수 있을지...?'''
    def display_info(self):
        print(f"Name: {self.name}, Email: {self.email}")

    # 다형성
    def perform_task(self):
        raise NotImplementedError("Each subclass must implement this method.")


# Customer 클래스(상속)
class Customer(User):
    def __init__(self, user_id: int, name: str, email: str):
        super().__init__(user_id, name, email)
        self.role = 'customer'

    # 다형성
    def perform_task(self):
        print(f"\nThere are {self.role}'s task.")

# Admin 클래스(상속)
class Admin(User):
    def __init__(self, user_id: int, name: str, email: str):
        super().__init__(user_id, name, email)
        self.role = 'admin'

    # 다형성
    def perform_task(self):
        print(f"\nThere are {self.role}'s task.")

# 싱글턴 디자인 패턴
class SingletonMeta(type):
    """
    싱글톤 메타클래스를 정의하여 모든 매니저 클래스에서 사용할 수 있게 합니다.
    """
    _instances = {} # 클래스 타입에 대한 싱글톤 인스턴스를 저장
    
    def __call__(cls, *args, **kwargs): # 클래스 인스턴스를 생성할 때 호출됨
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
    
# UserManager 클래스 정의 - 유저 등록 및 로그인 DB 작업
class UserManager(metaclass=SingletonMeta):
    def __init__(self, db_connection):
        self.conn = db_connection
        self.cursor = self.conn.cursor()
    
    # User DB에 등록하기
    def register_user(self, name: str, email: str, password: str, role: str):
        # 회원가입 시, User 가 customer나 admin 이 아니라면
        if role not in ['customer', 'admin']:
            raise ValueError("Role must be 'customer' or 'admin'")

        # 비밀번호 해싱
        hashed_password = hash_password(password)

        try:
            # User 데이터 DB에 입력
            self.cursor.execute("INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)", (name, email, hashed_password, role))
            self.conn.commit() # 작업 완료 명령어

            print(f"\nUser {name} registered successfully with role {role}.")
            # 잘못된 데이터 입력인 경우
        except mysql.connector.Error as err:
            raise ValueError(f"Database error: {err}")

    # 로그인 하기
    def login(self, email: str, password: str):
        # Users 테이블에서 정보 가져오기
        self.cursor.execute("SELECT user_id, name, password, role FROM users WHERE email = %s", (email,)) #이메일 가져오기
        result = self.cursor.fetchone() # 가져오기
        
        # 로그인 성공
        if result: # 일치하는 이메일이 있으면
            user_id, name, stored_password, role = result
            # 해싱 비밀번호와 일치하는지 확인하기
            if check_password(stored_password.encode('utf-8'), password):
                # 비밀번호는 객체에 저장하지 않고, 로그인 성공 후 즉시 폐기
                print(f"\nLogged in as {name} with role {role}")
                if role == 'admin':
                    return Admin(user_id, name, email) # Admin 객체를 리턴
                else:
                    return Customer(user_id, name, email) # Customer 객체를 리턴
            else:
                raise ValueError("Incorrect password")
        # 로그인 실패
        else:
            raise ValueError("Incorrect email or password")
        
        

# CarManager 클래스 - 자동차 관리
class CarManager(metaclass=SingletonMeta):
    def __init__(self, db_connection):
        self.conn = db_connection
        self.cursor = self.conn.cursor()

    # 자동차 추가
    def add_car(self, make, model, year, mileage, available_now, min_rent_period, max_rent_period):
        try:
            # Insert query 문
            self.cursor.execute("INSERT INTO cars (make, model, year, mileage, available_now, min_rent_period, max_rent_period) VALUES (%s, %s, %s, %s, %s, %s, %s)", (make, model, year, mileage, available_now, min_rent_period, max_rent_period))
            self.conn.commit() 
            print("Car added successfully.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")

    # 자동차 업데이트
    def update_car(self, car_id, make, model, year, mileage, available_now, min_rent_period, max_rent_period):
        try:
            self.cursor.execute("UPDATE cars SET make=%s, model=%s, year=%s, mileage=%s, available_now=%s, min_rent_period=%s, max_rent_period=%s WHERE car_id=%s", (make, model, year, mileage, available_now, min_rent_period, max_rent_period, car_id))
            self.conn.commit()

            # 전 query 에 영향받는 행의 수가 1개 이상이면, 바뀌었다는 뜻이므로
            if self.cursor.rowcount > 0: 
                print("Car updated successfully.")
            # 변화가 없을 시, update x
            else:
                print("Car not found.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")

    # 자동차 삭제
    def delete_car(self, car_id):
        try:
            # 삭제 query 문
            self.cursor.execute('DELETE FROM cars WHERE car_id=%s', (car_id,))
            self.conn.commit()
            # 영향받는 행의 수가 1개 이상이면, 삭제되었다는 뜻이므로
            if self.cursor.rowcount > 0:
                print("Car deleted successfully.")
            # 변화가 없을 시, delete x
            else:
                print("Car not found.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")


    # 자동차 리스트 조회
    def list_cars(self):
        print("car_id, make, model, year, mileage, available_now, min_rent_period, max_rent_period\n") # 내가 추가함
        self.cursor.execute('SELECT * FROM cars')
        cars = self.cursor.fetchall() # 쿼리문 데이터 배열 형식으로 가져오기 - fetchall()
        for car in cars:
            print(car)

# Rental Manager 클래스 
class RentalManager(metaclass=SingletonMeta):
    def __init__(self, db_connection):
        self.conn = db_connection
        self.cursor = self.conn.cursor()

    # Rental 예약 만들기
    def create_rental(self, car_id, user_id, start_date, end_date):

        # 날짜 문자열을 datetime.date 객체로 변환
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

        # 대여 가능 여부 확인
        self.cursor.execute("SELECT available_now FROM cars WHERE car_id = %s", (car_id,))
        available = self.cursor.fetchone()
        
        # 대여 불가인 경우
        if not available[0]:
            print("This car is not available for rental.")
            return
        
        # 대여 가능한 경우
        # 대여 요금 계산 (하루 50달러)
        days = (end_date - start_date).days + 1
        total_fee = days * 50
        
        # rentals 테이블에 대여된 카 입력
        try:
            self.cursor.execute("INSERT INTO rentals (car_id, user_id, start_date, end_date, total_fee, status) VALUES (%s, %s, %s, %s, %s, 'on process')", (car_id, user_id, start_date, end_date, total_fee))
            self.conn.commit()
            print("Rental created successfully. Total fee: ${:.2f}".format(total_fee))
        except mysql.connector.Error as err:
            print(f"Error: {err}")

    '''
    잠깐 - 대여된 차가 status가 cancelled 인 경우에도 보여줘야할까? 생각해볼 것
    '''
    # 대여된 차 리스트
    def list_rentals(self):
        self.cursor.execute("SELECT * FROM rentals")
        rentals = self.cursor.fetchall()

        # 대여된 차가 없을 시
        if len(rentals) == 0:
            print("\nYou do not have booking yet")

        # 대여된 차가 있을 시
        else: 
            for rental in rentals:
                print(rental)

    '''대여 관리 파트 추가'''
    # 대여 요청 승인
    def approve_rental(self, rental_id):
        try:
            self.cursor.execute("UPDATE rentals SET status = 'active' WHERE rental_id = %s AND status = 'on process'", (rental_id,))
            self.conn.commit()

            # 영향받는 행의 수가 1개 이상이면, 승인되었다는 뜻이므로
            if self.cursor.rowcount > 0:
                print("Rental approved successfully.")
            else:
                print("Rental not found or already processed.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")

    # 대여 요청 취소
    def cancel_rental(self, rental_id):
        try:
            self.cursor.execute("UPDATE rentals SET status = 'cancelled' WHERE rental_id = %s", (rental_id,))
            self.conn.commit()

            # 영향받는 행의 수가 1개 이상이면, 삭제되었다는 뜻이므로
            if self.cursor.rowcount > 0:
                print("Rental cancelled successfully.")
            else:
                print("Rental not found.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")

    # 대여 완료(종료)
    def complete_rental(self, rental_id):
        try:
            self.cursor.execute("UPDATE rentals SET status = 'completed' WHERE rental_id = %s", (rental_id,))
            self.conn.commit()

            # 영향받는 행의 수가 1개 이상이면, 대여완료되었다는 뜻이므로
            if self.cursor.rowcount > 0:
                print("Rental completed successfully.")
            else:
                print("Rental not found.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")

# 유저 회원가입 기능
def sign_up(user_manager):
    name = input("Enter your name: ")
    email = input("Enter your email: ")
    password = input("Enter your password: ")
    role = input("Enter your role (customer/admin): ")

    if role not in ['customer', 'admin']:
        print("Invalid role specified. Role must be 'customer' or 'admin'.")
        return
    
    try:
        user_manager.register_user(name, email, password, role) # DB에 정보 보내기
    except ValueError as ve:
        print(f"Error: {ve}")

# 유저 로그인 기능
def log_in(user_manager):
    email = input("Enter your email: ")
    password = input("Enter your password: ")
    try:
        return user_manager.login(email, password) # DB에 정보 보내고 Admin 객체나 Customer 객체를 리턴 받음
    except ValueError as ve:
        print(f"Error: {ve}")
        return None
    
# 초기화면
def main_menu(user_manager, car_manager, rental_manager):
    while True:

        print("\n1. Sign Up")
        print("2. Log In")
        print("3. Exit")
        choice = input("Choose an option: ")

        # sign up
        if choice == '1':
            sign_up(user_manager) # sign_up 메소드 부른 뒤, 회원정보 입력 후, 정보를 DB에 입력
        # Log in
        elif choice == '2':
            user = log_in(user_manager) # log_in 메소드 부른 뒤, 회원 정보 체크하고 Admin 혹은 Customer 객체 리턴
            if user:
                if user.role == 'admin': # 객체가 admin 인 경우
                    admin_menu(user, car_manager, rental_manager)
                elif user.role == 'customer': # 객체가 customer 인 경우
                    customer_menu(user, rental_manager)
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice, please try again.")


# admin 로그인인 경우, 관리자 메뉴가 나타남
def admin_menu(user, car_manager, rental_manager):
    while True:

        user.perform_task() # 다형성

        print("\n1. Add Car")
        print("2. Update Car")
        print("3. Delete Car")
        print("4. List Cars")
        print("5. Approve Rental")
        print("6. Cancel Rental")
        print("7. Complete Rental")
        print("8. Logout")
        
        choice = input("Select an option: ")
        if choice == '8':
            print("Logging out...")
            break
        # admin_actions 중 하나라면, 
        elif choice in admin_actions:
            admin_actions[choice](user, car_manager, rental_manager)
        else:
            print("Invalid choice, please try again.")

# admin_actions 딕셔너리
admin_actions = {
    '1': lambda user, car_manager, _: car_manager.add_car(), # 1을 선택하는 경우, car_manager의 add_car() 메소드를 호출해서 새로운 차량 추가
    '2': lambda user, car_manager, _: car_manager.update_car(), # 2을 선택하는 경우, car_manager의 update_car() 메소드를 호출해서 새로운 차량 정보 업데이트
    '3': lambda user, car_manager, _: car_manager.delete_car(), # 3을 선택하는 경우, car_manager의 delete_car() 메소드를 호출해서 차량 삭제
    '4': lambda user, car_manager, _: car_manager.list_cars(), # 4을 선택하는 경우, car_manager의 list_cars() 메소드를 호출해서 등록된 차량 보여줌
    '5': lambda user, _, rental_manager: rental_manager.approve_rental(), # 5을 선택하는 경우, rental_manager의 approve_rental() 메소드를 호출해서 대여 요청 승인
    '6': lambda user, _, rental_manager: rental_manager.cancel_rental(), # 6을 선택하는 경우, rental_manager의 cancel_rental() 메소드를 호출해서 대여 요청 취소
    '7': lambda user, _, rental_manager: rental_manager.complete_rental() # 7을 선택하는 경우, rental_manager의 complete_rental() 메소드를 호출해서 대여 완료
}

# customer 로그인인 경우, 고객 메뉴가 나타남
def customer_menu(user, rental_manager):
    while True:

        user.perform_task() # 다형성

        print("\n1. Rent a Car")
        print("2. View Rentals")
        print("3. Logout")
        
        choice = input("Select an option: ")
        if choice == '3':
            print("Logging out...")
            break
        elif choice in customer_actions:
            customer_actions[choice](user, rental_manager)
        else:
            print("Invalid choice, please try again.")



customer_actions = {
    '1': lambda user, rental_manager: rental_manager.create_rental(), # 1을 선택할 경우, rental_manager의 create_rental() 메소드를 호출해서 새로운 대여를 생성한다.
    '2': lambda user, rental_manager: rental_manager.list_rentals() # 2를 선택할 경우, rental_manager의 list_rentals() 메소드를 호출해서 사용자가 현재까지 진행한 모든 대여 목록을 조회한다.
}

if __name__ == "__main__":


    conn = create_connection() # DB 연결 시도
    if conn is None:
        print("Failed to connect to the database.")
    else:
        print("Database connection successful.")
        # 연결 성공 후, UserManager 등의 클래스 인스턴스 생성
        user_manager = UserManager(conn)
        car_manager = CarManager(conn)
        rental_manager = RentalManager(conn)
        main_menu(user_manager, car_manager, rental_manager)
        conn.close()
    

