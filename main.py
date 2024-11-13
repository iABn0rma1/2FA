from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient
import pyotp
import os
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
import time

# Load environment variables
load_dotenv()

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client['2fa_system']
users_collection = db['users']

# Temporary in-memory storage for OTP (for simplicity)
otp_storage = {}

# Email credentials
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

app = FastAPI()

# Initialize Jinja2Templates
templates = Jinja2Templates(directory="templates")

# Serve static files from 
app.mount("/static", StaticFiles(directory="static"), name="static")

# OTP Generation
def send_otp_email(email, otp):
    msg = MIMEText(f"Your OTP is: {otp}")
    msg['From'] = EMAIL_USER
    msg['To'] = email
    msg['Subject'] = "OTP For 2FA"

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, email, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
    finally:
        server.quit()

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    # Check user credentials
    user = users_collection.find_one({"username": username, "password": password})
    if not user:
        raise HTTPException(status_code=404, detail="Invalid credentials")

    # Generate OTP
    totp = pyotp.TOTP(user['secret'])
    otp = totp.now()

    # Store OTP in memory for verification
    otp_storage[username] = {"otp": otp, "timestamp": time.time()}

    # Send OTP email
    send_otp_email(user['email'], otp)

    return templates.TemplateResponse("otp_verification.html", {"request": request, "username": username})

@app.get("/verify_otp", response_class=HTMLResponse)
async def otp_verification_form(request: Request, username: str):
    # Render OTP verification page
    return templates.TemplateResponse("otp_verification.html", {"request": request, "username": username})

@app.post("/verify_otp")
async def verify_otp(request: Request, username: str = Form(...), otp: str = Form(...)):
    # Check if the OTP exists for the given username
    if username not in otp_storage:
        raise HTTPException(status_code=400, detail="OTP session expired")

    stored_otp = otp_storage[username]
    current_time = time.time()

    # Check if OTP is expired (valid for 5 minutes)
    if current_time - stored_otp['timestamp'] > 300:
        del otp_storage[username]  # Clear expired OTP
        raise HTTPException(status_code=400, detail="OTP expired")

    # Validate the OTP
    if stored_otp['otp'] == otp:
        del otp_storage[username]  # Clear OTP after successful verification
        return {"message": "OTP verified successfully!"}
    else:
        raise HTTPException(status_code=400, detail="Invalid OTP")

# Route for handling registration form submission
@app.post("/register_user")
async def register_user(request: Request, username: str = Form(...), password: str = Form(...), email: str = Form(...)):
    # Check if username already exists
    if users_collection.find_one({"username": username}):
        raise HTTPException(status_code=400, detail="Username already taken")

    secret = pyotp.random_base32()
    users_collection.insert_one({
        "username": username,
        "password": password,
        "email": email,
        "secret": secret
    })

    return RedirectResponse(url="/", status_code=303)
