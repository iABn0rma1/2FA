# The Two-Factor Authentication 2FA System

2FA system is designed to enhance user security by requiring two forms of verification: something the user knows (password) and something the user has (one-time passcode). This system integrates MongoDB for user data management, FastAPI for building the web application, and pyotp for OTP generation. It supports user registration, login, and OTP verification processes, ensuring that only authorized users can access sensitive areas. The system delivers OTPs using emails, and session-based OTP validation for secure access. Security features, including OTP expiration and in-memory OTP storage reduce potential threats.

## **Tech Stack**

- **Backend**: FastAPI
- **Database**: MongoDB
- **OTP Generation**: pyotp (for TOTP)
- **Email Service**: SMTP (Gmail)
- **Frontend**: HTML, CSS, and Jinja2 templates for rendering login and registration pages

## **API Endpoints**

### **1. `/register`** - **Register**
- **Method**: `GET`
- **Description**: Displays the registration page where users can create an account by providing a username, password, and email.

### **2. `/login`** - **Login**
- **Method**: `POST`
- **Description**: Accepts user credentials (username, password) and generates an OTP, sending it to the user's email. The user then proceeds to OTP verification.

### **3. `/verify_otp`** - **OTP Verification**
- **Method**: `GET`
- **Description**: Displays the OTP verification page where users can enter the OTP received in their email.

### **3. `/verify_otp`** - **OTP Verification**
- **Method**: `POST`
- **Description**: Accepts the OTP input from the user and validates it. If valid, the user is authenticated and logged in.

### **4. `/register_user`** - **User Registration**
- **Method**: `POST`
- **Description**: Handles the user registration process. It checks if the username already exists and then stores the user’s details in MongoDB with a secret key for OTP generation.

## **How to Clone and Run the Repo**

### **Step 1: Clone the Repository**

Run the following command:

```bash
git clone https://github.com/iABn0rma1/2FA.git
```

### **Step 2: Install Dependencies**

Create a virtual environment and install the dependencies:

```bash
python3 -m venv venv
source venv/bin/activate  # On Linux/macOS
venv\Scripts\activate     # On Windows
pip install -r requirements.txt
```

### **Step 3: Set Up Environment Variables**

Create a `.env` file and add the following:

```env
MONGO_URI=mongodb://<username>:<password>@<host>:<port>/<dbname>
EMAIL_USER=<your-email>
EMAIL_PASS=<your-email-password>
```

### **Step 4: Run the Application**

Run the FastAPI app with:

```bash
python3 uvicorn main:app --host 0.0.0.0 --port 8000
```

Access the application at `http://localhost:8000`.
