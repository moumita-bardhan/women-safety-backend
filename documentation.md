# Women Safety Backend Project Documentation

## 1. Project Introduction

This backend is part of the **Women Safety System** project.

The main purpose of this backend is to receive emergency data from a mobile app when a user is in danger.

When the user triggers an SOS alert from the mobile app, the mobile app sends location, image, SMS status, and device information to this backend.

The backend then stores that data in MySQL and sends the alert in real time to connected receiver devices using WebSocket.

This backend works like a **local emergency control server**.

---

## 2. What You Are Building

You are building a system where:

1. A sender mobile app registers itself with the backend.
2. The sender app saves emergency contacts.
3. The sender app updates its current location.
4. The sender app triggers an SOS alert during danger.
5. The backend saves the SOS alert in MySQL.
6. The backend saves uploaded emergency images.
7. The backend saves SMS sending logs.
8. The backend creates a Google Maps location link.
9. The backend broadcasts the SOS alert using WebSocket.
10. A receiver app or receiver dashboard gets the alert instantly.

---

## 3. Simple System Flow

```txt
Sender Mobile App
        |
        | Register device
        | Add emergency contacts
        | Update location
        | Trigger SOS
        v
Python FastAPI Backend
        |
        | Save data
        v
MySQL Database
        |
        | Broadcast live alert
        v
Receiver Mobile App / Receiver Dashboard
```

---

## 4. Real-Life Example

Suppose a user clicks the **SOS button** in the mobile app.

The mobile app sends this data to the backend:

```txt
User Name: Student User
Latitude: 22.5726
Longitude: 88.3639
Triggered By: SOS_BUTTON
SMS Status: SENT
Images: Back camera image / Front camera image
SMS Logs: Sent or failed SMS details
```

The backend then:

1. Generates a unique SOS alert code.
2. Creates a Google Maps link.
3. Saves the SOS alert in MySQL.
4. Saves the location in location logs.
5. Saves uploaded images in the `uploads` folder.
6. Saves SMS logs in the database.
7. Runs a fake CNN placeholder function.
8. Broadcasts the SOS alert to all connected WebSocket receivers.

---

## 5. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main backend programming language |
| FastAPI | Creates APIs and WebSocket server |
| Uvicorn | Runs the FastAPI backend server |
| MySQL | Stores users, devices, contacts, alerts, images, and logs |
| SQLAlchemy | Connects Python code with MySQL tables |
| PyMySQL | MySQL driver used by SQLAlchemy |
| python-dotenv | Reads database config from `.env` file |
| python-multipart | Handles form-data and image upload |
| WebSocket | Sends real-time SOS alerts |
| StaticFiles | Serves uploaded SOS images |
| uploads folder | Stores uploaded image files |

---

## 6. Backend Folder Structure

Create your backend folder like this:

```txt
women-safety-python/
│
├── main.py
├── database.py
├── models.py
├── requirements.txt
├── .env
│
├── uploads/
│   └── .gitkeep
│
└── README.md
```

---

## 7. File Explanation

### `main.py`

This is the main backend file.

It contains:

```txt
FastAPI app
API routes
Device registration logic
Location update logic
Emergency contact logic
SOS alert creation logic
Image upload logic
SMS log saving logic
WebSocket connection logic
Alert history API
Device list API
```

This is the file that runs the backend server.

---

### `database.py`

This file connects the backend with MySQL.

It does these things:

```txt
Loads .env file
Reads database host, port, username, password, and database name
Creates database connection URL
Creates SQLAlchemy engine
Creates database session
Creates Base class for models
Provides get_db() dependency
```

The main responsibility is:

```txt
Python Backend <-> MySQL Database
```

---

### `models.py`

This file contains the database table structure.

It defines SQLAlchemy model classes.

Tables defined in this file:

```txt
users
devices
emergency_contacts
sos_alerts
sos_alert_images
sms_logs
location_logs
receiver_logs
receiver_notifications
```

SQLAlchemy uses these model classes to create and manage MySQL tables.

---

### `.env`

This file stores database configuration.

Example:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=women_safety_db
```

This is used so that database credentials are not directly written inside Python code.

---

### `uploads/`

This folder stores uploaded SOS images.

Example:

```txt
uploads/
  A1B2C3D4-back-1.jpg
  A1B2C3D4-front-2.jpg
```

The actual image files are saved inside this folder.

The database stores only the image path.

Example image path saved in database:

```txt
/uploads/A1B2C3D4-back-1.jpg
```

---

## 8. Required Packages

Create `requirements.txt`:

```txt
fastapi
uvicorn[standard]
python-multipart
python-dotenv
sqlalchemy
pymysql
```

Install all packages:

```bash
python -m pip install -r requirements.txt
```

---

## 9. MySQL Database Setup

Before starting the backend, create the database manually.

Open MySQL, phpMyAdmin, or MySQL Workbench and run:

```sql
CREATE DATABASE women_safety_db;
```

Check if the database exists:

```sql
SHOW DATABASES;
```

Important:

SQLAlchemy can create tables automatically, but the database itself must already exist.

If the database does not exist, you may get this error:

```txt
Unknown database 'women_safety_db'
```

---

## 10. Environment File Setup

Create a file named:

```txt
.env
```

Add this:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=women_safety_db
```

If your MySQL root user has a password, add it like this:

```env
DB_PASSWORD=your_mysql_password
```

---

## 11. Database Connection Flow

The backend reads database values from `.env`.

Then it creates a MySQL connection URL like this:

```txt
mysql+pymysql://root:@localhost:3306/women_safety_db
```

Then SQLAlchemy uses this URL to connect with MySQL.

The backend creates a database session using:

```txt
SessionLocal
```

Every API that needs the database receives the DB session from:

```txt
get_db()
```

After the API request is completed, the database session is closed automatically.

---

## 12. Database Design

### 12.1 `users`

This table stores user information.

A user can be:

```txt
SENDER
RECEIVER
ADMIN
```

In the current backend, when a new device is registered, a new sender user is created.

Fields include:

```txt
id
name
phone
email
role
is_active
created_at
```

Example:

```txt
Name: Student User
Phone: 9876543210
Role: SENDER
```

---

### 12.2 `devices`

This table stores device information.

Each mobile device has a unique `device_uuid`.

Fields include:

```txt
id
user_id
device_uuid
device_name
device_type
fcm_token
is_receiver_enabled
last_latitude
last_longitude
last_location_at
last_connected_at
is_active
created_at
```

Allowed device types:

```txt
ANDROID_SENDER
ANDROID_RECEIVER
ANDROID_BOTH
LAPTOP_SERVER
```

Example:

```txt
Device Name: OnePlus Nord 5
Device Type: ANDROID_BOTH
Device UUID: abc-device-123
```

---

### 12.3 `emergency_contacts`

This table stores emergency contact details.

These are the contacts where the mobile app can send SMS during SOS.

Fields include:

```txt
id
user_id
device_id
contact_name
phone
relation
priority
is_active
created_at
```

Example contacts:

```txt
Father
Mother
Brother
Friend
Guardian
```

---

### 12.4 `sos_alerts`

This is the main SOS alert table.

Every emergency alert is stored here.

Fields include:

```txt
id
alert_code
sender_user_id
sender_device_id
triggered_by
status
latitude
longitude
map_link
image_path
sms_status
sms_sent_count
sms_failed_count
sms_sent_at
cnn_label
cnn_confidence
created_at
```

Allowed `triggered_by` values:

```txt
SOS_BUTTON
SHAKE_DETECTION
FALL_DETECTION
CNN_DETECTION
MANUAL_TEST
```

Allowed alert status values:

```txt
TRIGGERED
SENT
RECEIVED
RESOLVED
CANCELLED
```

Allowed SMS status values:

```txt
PENDING
SENT
FAILED
PARTIAL
NOT_REQUIRED
```

---

### 12.5 `sos_alert_images`

This table stores multiple images for one SOS alert.

One SOS alert can have multiple images.

For example:

```txt
Back camera image
Front camera image
```

Fields include:

```txt
id
sos_alert_id
image_path
image_order
camera_type
created_at
```

Allowed camera types:

```txt
BACK
FRONT
```

---

### 12.6 `sms_logs`

This table stores SMS sending result logs.

The mobile app sends SMS from the phone.

After sending SMS, the mobile app sends SMS logs to backend.

Fields include:

```txt
id
sos_alert_id
contact_name
phone
status
error_message
created_at
```

Allowed status values:

```txt
SENT
FAILED
```

---

### 12.7 `location_logs`

This table stores location history.

It can store:

```txt
Normal device location update
SOS alert location
```

Fields include:

```txt
id
device_id
sos_alert_id
latitude
longitude
map_link
created_at
```

This is useful for tracking where the user was during an SOS alert.

---

### 12.8 `receiver_logs`

This table is prepared for receiver-side logs.

It can store whether the receiver device received, opened, or failed to receive an SOS alert.

Fields include:

```txt
id
sos_alert_id
receiver_user_id
receiver_device_id
status
vibrated
sound_played
notification_shown
received_at
```

Allowed status values:

```txt
RECEIVED
OPENED
FAILED
```

Currently, this table exists in the model, but the current backend routes do not write data into this table yet.

---

### 12.9 `receiver_notifications`

This table is prepared for receiver notification records.

Fields include:

```txt
id
sos_alert_id
receiver_device_id
distance_meter
notification_status
created_at
```

Allowed notification status values:

```txt
PENDING
SENT
FAILED
OPENED
ACKNOWLEDGED
```

Currently, this table exists in the model, but the current backend routes do not write data into this table yet.

---

## 13. API Endpoints

Base URL for local laptop:

```txt
http://localhost:8000
```

Base URL for mobile on same Wi-Fi:

```txt
http://LAPTOP_IP:8000
```

Example:

```txt
http://192.168.1.8:8000
```

---

### 13.1 Health Check API

#### Endpoint

```txt
GET /
```

#### Purpose

Checks whether the backend server is running.

#### Example Response

```json
{
  "success": true,
  "message": "Women Safety Local Server is running"
}
```

---

### 13.2 Register Device API

#### Endpoint

```txt
POST /api/devices/register
```

#### Body Type

```txt
multipart/form-data
```

#### Purpose

Registers a new mobile device.

If the device already exists, it updates the device information.

#### Fields

| Field | Type | Required | Description |
|---|---|---:|---|
| `name` | text | Yes | User name |
| `phone` | text | No | User phone number |
| `device_uuid` | text | Yes | Unique device ID from mobile |
| `device_name` | text | No | Device name |
| `device_type` | text | No | Device type |
| `fcm_token` | text | No | Firebase notification token |

#### Example Form Data

```txt
name = Student User
phone = 9876543210
device_uuid = abc-device-123
device_name = OnePlus Nord 5
device_type = ANDROID_BOTH
fcm_token =
```

#### Example Response For New Device

```json
{
  "success": true,
  "message": "Device registered successfully",
  "data": {
    "user_id": 1,
    "device_id": 1,
    "device_uuid": "abc-device-123"
  }
}
```

#### Example Response For Existing Device

```json
{
  "success": true,
  "message": "Device updated successfully",
  "data": {
    "user_id": 1,
    "device_id": 1,
    "device_uuid": "abc-device-123"
  }
}
```

#### Internal Flow

```txt
1. Check device by device_uuid
2. If device exists, update device details
3. If device does not exist, create new user
4. Create new device
5. Link device with user
6. Return user_id, device_id, and device_uuid
```

---

### 13.3 Update Device Location API

#### Endpoint

```txt
POST /api/devices/location
```

#### Body Type

```txt
multipart/form-data
```

#### Purpose

Updates the latest location of a registered device.

It also saves the location into location logs.

#### Fields

| Field | Type | Required | Description |
|---|---|---:|---|
| `device_uuid` | text | Yes | Registered device UUID |
| `latitude` | number | Yes | Current latitude |
| `longitude` | number | Yes | Current longitude |

#### Example Form Data

```txt
device_uuid = abc-device-123
latitude = 22.5726
longitude = 88.3639
```

#### Example Success Response

```json
{
  "success": true,
  "message": "Location updated successfully"
}
```

#### Example Device Not Found Response

```json
{
  "success": false,
  "message": "Device not found"
}
```

#### Internal Flow

```txt
1. Find device by device_uuid
2. Create Google Maps link
3. Update device last_latitude
4. Update device last_longitude
5. Update device last_location_at
6. Save location log
7. Return success response
```

---

### 13.4 Create Emergency Contact API

#### Endpoint

```txt
POST /api/emergency-contacts
```

#### Body Type

```txt
multipart/form-data
```

#### Purpose

Saves an emergency contact for a registered device.

#### Fields

| Field | Type | Required | Description |
|---|---|---:|---|
| `device_uuid` | text | Yes | Registered device UUID |
| `contact_name` | text | Yes | Emergency contact name |
| `phone` | text | Yes | Emergency contact phone |
| `relation` | text | No | Relation with user |
| `priority` | number | No | Contact priority |

#### Example Form Data

```txt
device_uuid = abc-device-123
contact_name = Father
phone = 9876543210
relation = Father
priority = 1
```

#### Example Response

```json
{
  "success": true,
  "message": "Emergency contact saved successfully",
  "data": {
    "id": 1,
    "contact_name": "Father",
    "phone": "9876543210",
    "relation": "Father",
    "priority": 1,
    "is_active": true
  }
}
```

#### Internal Flow

```txt
1. Find device by device_uuid
2. If device is not found, return error
3. Create emergency contact
4. Link contact with user_id and device_id
5. Save contact
6. Return saved contact details
```

---

### 13.5 Get Emergency Contacts API

#### Endpoint

```txt
GET /api/emergency-contacts/{device_uuid}
```

#### Purpose

Fetches active emergency contacts for a device.

Contacts are sorted by priority.

#### Example URL

```txt
http://localhost:8000/api/emergency-contacts/abc-device-123
```

#### Example Response

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "contact_name": "Father",
      "phone": "9876543210",
      "relation": "Father",
      "priority": 1,
      "is_active": true
    }
  ]
}
```

#### Device Not Found Response

```json
{
  "success": false,
  "message": "Device not found",
  "data": []
}
```

---

### 13.6 Create SOS Alert API

#### Endpoint

```txt
POST /api/sos
```

#### Body Type

```txt
multipart/form-data
```

#### Purpose

Creates a new SOS alert.

This is the most important API in this backend.

It saves:

```txt
SOS alert
SOS location
Google Maps link
Uploaded images
SMS status
SMS sent count
SMS failed count
SMS logs
CNN placeholder result
Location log
```

It also broadcasts the alert to all connected WebSocket clients.

#### Fields

| Field | Type | Required | Description |
|---|---|---:|---|
| `user_name` | text | Yes | Sender user name |
| `latitude` | number | Yes | SOS latitude |
| `longitude` | number | Yes | SOS longitude |
| `triggered_by` | text | No | How SOS was triggered |
| `sms_status` | text | No | SMS status |
| `sms_sent_count` | number | No | Number of SMS sent |
| `sms_failed_count` | number | No | Number of SMS failed |
| `sms_logs_json` | text | No | SMS logs JSON string |
| `device_uuid` | text | No | Sender device UUID |
| `camera_types_json` | text | No | Camera type JSON string |
| `images` | file | No | One or multiple SOS images |

#### Allowed `triggered_by` Values

```txt
SOS_BUTTON
SHAKE_DETECTION
FALL_DETECTION
CNN_DETECTION
MANUAL_TEST
```

#### Allowed `sms_status` Values

```txt
PENDING
SENT
FAILED
PARTIAL
NOT_REQUIRED
```

#### Example Form Data Without Image

```txt
user_name = Student User
latitude = 22.5726
longitude = 88.3639
triggered_by = MANUAL_TEST
sms_status = PENDING
sms_sent_count = 0
sms_failed_count = 0
device_uuid = abc-device-123
camera_types_json = []
sms_logs_json = []
```

#### Example Form Data With Images

```txt
user_name = Student User
latitude = 22.5726
longitude = 88.3639
triggered_by = SOS_BUTTON
sms_status = SENT
sms_sent_count = 1
sms_failed_count = 0
device_uuid = abc-device-123
camera_types_json = ["BACK", "FRONT"]
sms_logs_json = [{"name":"Father","phone":"9876543210","status":"SENT"}]
images = back-camera-image.jpg
images = front-camera-image.jpg
```

#### Example Success Response

```json
{
  "success": true,
  "message": "SOS alert created successfully",
  "data": {
    "type": "SOS_ALERT",
    "id": 1,
    "alert_code": "A1B2C3D4",
    "user_name": "Student User",
    "latitude": 22.5726,
    "longitude": 88.3639,
    "map_link": "https://maps.google.com/?q=22.5726,88.3639",
    "image_path": "/uploads/A1B2C3D4-back-1.jpg",
    "images": [
      {
        "path": "/uploads/A1B2C3D4-back-1.jpg",
        "camera_type": "BACK",
        "order": 1
      },
      {
        "path": "/uploads/A1B2C3D4-front-2.jpg",
        "camera_type": "FRONT",
        "order": 2
      }
    ],
    "image_count": 2,
    "sms_status": "SENT",
    "sms_sent_count": 1,
    "sms_failed_count": 0,
    "cnn_label": "UNKNOWN",
    "cnn_confidence": 0.0,
    "triggered_by": "SOS_BUTTON",
    "created_at": "2026-05-26T10:30:00"
  }
}
```

---

### 13.7 Get Alert History API

#### Endpoint

```txt
GET /api/alerts
```

#### Purpose

Returns the latest 50 SOS alerts.

Newest alerts come first.

#### Example Response

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "alert_code": "A1B2C3D4",
      "latitude": 22.5726,
      "longitude": 88.3639,
      "map_link": "https://maps.google.com/?q=22.5726,88.3639",
      "image_path": "/uploads/A1B2C3D4-back-1.jpg",
      "images": [
        {
          "image_path": "/uploads/A1B2C3D4-back-1.jpg",
          "camera_type": "BACK",
          "image_order": 1
        }
      ],
      "image_count": 1,
      "sms_status": "SENT",
      "sms_sent_count": 1,
      "sms_failed_count": 0,
      "cnn_label": "UNKNOWN",
      "cnn_confidence": 0.0,
      "triggered_by": "SOS_BUTTON",
      "created_at": "2026-05-26T10:30:00"
    }
  ]
}
```

---

### 13.8 Get Registered Devices API

#### Endpoint

```txt
GET /api/devices
```

#### Purpose

Returns the latest 100 registered devices.

Newest devices come first.

#### Example Response

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "user_id": 1,
      "device_uuid": "abc-device-123",
      "device_name": "OnePlus Nord 5",
      "device_type": "ANDROID_BOTH",
      "is_receiver_enabled": true,
      "last_latitude": 22.5726,
      "last_longitude": 88.3639,
      "last_location_at": "2026-05-26T10:30:00",
      "last_connected_at": "2026-05-26T10:00:00"
    }
  ]
}
```

---

### 13.9 Get SOS Alert Details API

#### Endpoint

```txt
GET /api/sos-alerts/{alert_code}
```

#### Purpose

Fetches details of a single SOS alert by alert code.

#### Example URL

```txt
http://localhost:8000/api/sos-alerts/A1B2C3D4
```

#### Example Response

```json
{
  "success": true,
  "message": "SOS alert details fetched successfully",
  "data": {
    "id": 1,
    "alert_code": "A1B2C3D4",
    "user_name": "",
    "latitude": "22.57260000",
    "longitude": "88.36390000",
    "map_link": "https://maps.google.com/?q=22.5726,88.3639",
    "triggered_by": "SOS_BUTTON",
    "image_count": 2,
    "created_at": "2026-05-26T10:30:00",
    "images": [
      {
        "id": 1,
        "image_url": "/uploads/A1B2C3D4-back-1.jpg",
        "image_path": "/uploads/A1B2C3D4-back-1.jpg",
        "camera_type": "BACK",
        "image_order": 1
      }
    ]
  }
}
```

#### Not Found Response

```json
{
  "success": false,
  "message": "SOS alert not found",
  "data": null
}
```

---

### 13.10 WebSocket Alert API

#### Endpoint

```txt
ws://localhost:8000/ws/alerts
```

For mobile or another device on same Wi-Fi:

```txt
ws://LAPTOP_IP:8000/ws/alerts
```

Example:

```txt
ws://192.168.1.8:8000/ws/alerts
```

#### Purpose

Receiver devices connect to this WebSocket.

When a new SOS alert is created, the backend sends the SOS alert instantly to all connected receivers.

#### Example WebSocket Message

```json
{
  "type": "SOS_ALERT",
  "id": 1,
  "alert_code": "A1B2C3D4",
  "user_name": "Student User",
  "latitude": 22.5726,
  "longitude": 88.3639,
  "map_link": "https://maps.google.com/?q=22.5726,88.3639",
  "image_path": "/uploads/A1B2C3D4-back-1.jpg",
  "images": [
    {
      "path": "/uploads/A1B2C3D4-back-1.jpg",
      "camera_type": "BACK",
      "order": 1
    }
  ],
  "image_count": 1,
  "sms_status": "SENT",
  "sms_sent_count": 1,
  "sms_failed_count": 0,
  "cnn_label": "UNKNOWN",
  "cnn_confidence": 0.0,
  "triggered_by": "SOS_BUTTON",
  "created_at": "2026-05-26T10:30:00"
}
```

---

## 14. How SOS API Works Internally

When `/api/sos` is called, the backend performs these steps:

---

### Step 1: Generate Alert Code

The backend creates a unique alert code.

Example:

```txt
A1B2C3D4
```

This code is used to identify one SOS alert.

---

### Step 2: Create Google Maps Link

The backend creates a map link from latitude and longitude.

Format:

```txt
https://maps.google.com/?q=latitude,longitude
```

Example:

```txt
https://maps.google.com/?q=22.5726,88.3639
```

---

### Step 3: Find Sender Device

If `device_uuid` is provided, the backend searches the device table.

If the device is found, the SOS alert is linked with:

```txt
sender_user_id
sender_device_id
```

If the device is not found, the SOS alert can still be created, but sender device information will be empty.

---

### Step 4: Parse Camera Types

The backend reads:

```txt
camera_types_json
```

Example:

```json
["BACK", "FRONT"]
```

This tells the backend which uploaded image came from which camera.

If invalid camera type is found, backend uses:

```txt
BACK
```

---

### Step 5: Save Uploaded Images

The backend saves uploaded images inside:

```txt
uploads/
```

Image filename format:

```txt
alertcode-cameratype-index.extension
```

Example:

```txt
A1B2C3D4-back-1.jpg
A1B2C3D4-front-2.jpg
```

The backend returns image path like this:

```txt
/uploads/A1B2C3D4-back-1.jpg
```

---

### Step 6: Run CNN Placeholder

Currently, real CNN detection is not implemented.

The backend has a fake CNN function.

If no image exists, it returns:

```json
{
  "label": "NO_IMAGE",
  "confidence": 0.0
}
```

If image exists, it returns:

```json
{
  "label": "UNKNOWN",
  "confidence": 0.0
}
```

Later, this can be replaced with a real CNN model.

---

### Step 7: Save SOS Alert

The backend saves the main SOS alert in:

```txt
sos_alerts
```

This stores:

```txt
alert_code
sender_user_id
sender_device_id
location
map link
main image path
SMS status
CNN result
created time
```

---

### Step 8: Save SOS Images

For every uploaded image, the backend creates one record in:

```txt
sos_alert_images
```

This allows one SOS alert to have multiple images.

---

### Step 9: Save Location Log

The backend saves location history in:

```txt
location_logs
```

This stores the SOS alert location.

---

### Step 10: Save SMS Logs

The backend reads:

```txt
sms_logs_json
```

Example:

```json
[
  {
    "name": "Father",
    "phone": "9876543210",
    "status": "SENT"
  },
  {
    "name": "Brother",
    "phone": "9876543211",
    "status": "FAILED",
    "errorMessage": "SMS permission denied"
  }
]
```

Then it saves each SMS result in:

```txt
sms_logs
```

---

### Step 11: Broadcast Alert

After saving the SOS alert, the backend sends the alert to all connected WebSocket clients.

Receivers can then:

```txt
Show alert
Play sound
Vibrate
Show location
Open Google Maps
Show uploaded image
```

---

## 15. Run The Backend

Go to your backend folder:

```bash
cd women-safety-python
```

Run:

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Explanation:

| Part | Meaning |
|---|---|
| `python -m uvicorn` | Runs FastAPI server |
| `main:app` | Uses `app` object from `main.py` |
| `--host 0.0.0.0` | Allows mobile devices to connect |
| `--port 8000` | Runs server on port 8000 |
| `--reload` | Restarts server when code changes |

---

## 16. Test Backend In Browser

Open:

```txt
http://localhost:8000
```

Expected response:

```json
{
  "success": true,
  "message": "Women Safety Local Server is running"
}
```

Open:

```txt
http://localhost:8000/api/alerts
```

Expected response:

```json
{
  "success": true,
  "data": []
}
```

or existing alerts if SOS alerts are already created.

---

## 17. Test APIs From Swagger

FastAPI gives automatic API documentation.

Open:

```txt
http://localhost:8000/docs
```

From Swagger, you can test:

```txt
Register device
Update location
Create emergency contact
Get emergency contacts
Create SOS alert
Upload SOS images
Get alerts
Get devices
Get SOS alert details
```

---

## 18. Test APIs From Postman Or Hoppscotch

Most POST APIs use:

```txt
multipart/form-data
```

Use form-data for:

```txt
/api/devices/register
/api/devices/location
/api/emergency-contacts
/api/sos
```

Do not send JSON body for these APIs because the backend is reading values using FastAPI `Form`.

---

## 19. Full Testing Flow Without Mobile App

### Step 1: Register Device

```txt
POST http://localhost:8000/api/devices/register
```

Form-data:

```txt
name = Student User
phone = 9876543210
device_uuid = abc-device-123
device_name = OnePlus Nord 5
device_type = ANDROID_BOTH
fcm_token =
```

---

### Step 2: Add Emergency Contact

```txt
POST http://localhost:8000/api/emergency-contacts
```

Form-data:

```txt
device_uuid = abc-device-123
contact_name = Father
phone = 9876543210
relation = Father
priority = 1
```

---

### Step 3: Check Emergency Contacts

```txt
GET http://localhost:8000/api/emergency-contacts/abc-device-123
```

---

### Step 4: Update Device Location

```txt
POST http://localhost:8000/api/devices/location
```

Form-data:

```txt
device_uuid = abc-device-123
latitude = 22.5726
longitude = 88.3639
```

---

### Step 5: Create SOS Alert

```txt
POST http://localhost:8000/api/sos
```

Form-data:

```txt
user_name = Student User
latitude = 22.5726
longitude = 88.3639
triggered_by = SOS_BUTTON
sms_status = SENT
sms_sent_count = 1
sms_failed_count = 0
device_uuid = abc-device-123
camera_types_json = ["BACK"]
sms_logs_json = [{"name":"Father","phone":"9876543210","status":"SENT"}]
images = select image file
```

---

### Step 6: Check Alert History

```txt
GET http://localhost:8000/api/alerts
```

---

### Step 7: Check Registered Devices

```txt
GET http://localhost:8000/api/devices
```

---

## 20. Test SOS API Using PowerShell

Without image:

```powershell
curl -X POST "http://localhost:8000/api/sos" `
  -F "user_name=Test User" `
  -F "latitude=22.5726" `
  -F "longitude=88.3639" `
  -F "triggered_by=MANUAL_TEST" `
  -F "sms_status=PENDING" `
  -F "sms_sent_count=0" `
  -F "sms_failed_count=0" `
  -F "device_uuid=abc-device-123" `
  -F "camera_types_json=[]" `
  -F "sms_logs_json=[]"
```

After that, open:

```txt
http://localhost:8000/api/alerts
```

You should see the new alert.

---

## 21. Test With Image Upload

Use Postman or Hoppscotch.

Method:

```txt
POST
```

URL:

```txt
http://localhost:8000/api/sos
```

Body type:

```txt
form-data
```

Fields:

```txt
user_name          Test User
latitude           22.5726
longitude          88.3639
triggered_by       MANUAL_TEST
sms_status         PENDING
sms_sent_count     0
sms_failed_count   0
device_uuid        abc-device-123
camera_types_json  ["BACK"]
sms_logs_json      []
images             Select JPG/PNG file
```

If successful:

1. Image is saved in `uploads/`.
2. Image path is saved in MySQL.
3. `/api/alerts` shows the image path.
4. Image can be opened from browser.

Example:

```txt
http://localhost:8000/uploads/A1B2C3D4-back-1.jpg
```

---

## 22. Test WebSocket

WebSocket URL:

```txt
ws://localhost:8000/ws/alerts
```

For mobile or another laptop on same Wi-Fi:

```txt
ws://LAPTOP_IP:8000/ws/alerts
```

Example:

```txt
ws://192.168.1.8:8000/ws/alerts
```

Simple browser test:

```html
<script>
  const socket = new WebSocket("ws://localhost:8000/ws/alerts");

  socket.onopen = () => {
    console.log("WebSocket connected");
  };

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log("New SOS Alert:", data);
  };

  socket.onclose = () => {
    console.log("WebSocket disconnected");
  };
</script>
```

When `/api/sos` is called, this WebSocket receives the SOS alert data instantly.

---

## 23. Find Laptop IP Address

If testing from mobile, do not use:

```txt
localhost
```

On mobile, `localhost` means the mobile device itself.

You need your laptop IP.

On Windows, open PowerShell and run:

```powershell
ipconfig
```

Find:

```txt
IPv4 Address . . . . . . . . . . : 192.168.1.8
```

Use this IP in mobile app:

```txt
http://192.168.1.8:8000
```

WebSocket:

```txt
ws://192.168.1.8:8000/ws/alerts
```

---

## 24. Same Wi-Fi Requirement

Your laptop and mobile must be connected to the same network.

Recommended options:

```txt
Laptop hotspot ON
Mobile connected to laptop hotspot
```

or:

```txt
Laptop and mobile connected to same Wi-Fi router
```

If they are not on the same network, the mobile app cannot call the laptop backend.

---

## 25. Important Android Note

If your mobile app is calling local HTTP URL like this:

```txt
http://192.168.1.8:8000
```

Android may block HTTP cleartext traffic.

For React Native Android, add this in Android manifest:

```xml
android:usesCleartextTraffic="true"
```

Without this, API calls may fail even if the backend is running.

---

## 26. Common Errors And Solutions

### 26.1 Unknown Database Error

Error:

```txt
Unknown database 'women_safety_db'
```

Reason:

```txt
Database does not exist.
```

Fix:

```sql
CREATE DATABASE women_safety_db;
```

---

### 26.2 Access Denied Error

Error:

```txt
Access denied for user 'root'@'localhost'
```

Reason:

```txt
Wrong MySQL username or password.
```

Fix:

Check `.env`:

```env
DB_USER=root
DB_PASSWORD=your_correct_password
```

---

### 26.3 Mobile Cannot Connect To Backend

Possible reasons:

```txt
Laptop and mobile are not on same Wi-Fi
Wrong laptop IP
Backend not running with --host 0.0.0.0
Windows Firewall is blocking Python
```

Fix:

Run backend like this:

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Use laptop IPv4 address:

```txt
http://192.168.1.8:8000
```

Allow Python in Windows Firewall if popup appears.

---

### 26.4 React Native Fetch Failed

Possible reasons:

```txt
Wrong IP address
Backend not running
Phone not connected to same Wi-Fi
Android blocked HTTP request
```

Fix:

Use:

```txt
http://LAPTOP_IP:8000
```

Not:

```txt
http://localhost:8000
```

Also add:

```xml
android:usesCleartextTraffic="true"
```

---

### 26.5 Image Upload Not Working

Possible reasons:

```txt
python-multipart is not installed
Wrong field name
Body type is not multipart/form-data
```

Fix:

Install:

```bash
python -m pip install python-multipart
```

Use field name:

```txt
images
```

---

### 26.6 Uploaded Image Not Opening

Check returned image path:

```txt
/uploads/A1B2C3D4-back-1.jpg
```

Open with full URL:

```txt
http://localhost:8000/uploads/A1B2C3D4-back-1.jpg
```

From mobile network:

```txt
http://LAPTOP_IP:8000/uploads/A1B2C3D4-back-1.jpg
```

---

### 26.7 Device Not Found

This happens when you call contact or location API before registering the device.

Fix:

First call:

```txt
POST /api/devices/register
```

Then call:

```txt
POST /api/devices/location
POST /api/emergency-contacts
```

---

## 27. Current Project Status

Currently, this backend supports:

```txt
FastAPI server
MySQL database
Device registration
Device location update
Emergency contact creation
Emergency contact listing
SOS alert creation
Multiple image upload
SMS log saving
Location log saving
Alert history
Device list
Single SOS alert details
WebSocket real-time SOS alert
CNN placeholder
```

---

## 28. Current Limitations

The current backend is good for local testing and project demo.

But for production, these things should be improved:

```txt
No login system
No JWT authentication
No role-based access
No request validation beyond basic FastAPI typing
No Alembic migration
No real CNN model
No push notification sending
No receiver acknowledgement API
No alert status update API
No emergency contact update/delete API
No pagination beyond fixed limit
No cloud image storage
No production deployment configuration
```

---

## 29. Future Features

You can add later:

```txt
User login
JWT authentication
Admin dashboard
Receiver dashboard
Real CNN model
Live location tracking
Push notification using Firebase
Nearby receiver detection
Emergency contact edit/delete
Alert status update
Receiver acknowledgement
Alert resolved/cancelled flow
Image storage in cloud
Production deployment
```

---

## 30. Beginner-Level Explanation

This backend is like an emergency control room.

The mobile app is like a panic button.

When the user clicks SOS:

1. The mobile app sends emergency data to the backend.
2. The backend saves the data in MySQL.
3. The backend creates a Google Maps link.
4. The backend saves uploaded images.
5. The backend saves SMS results.
6. The backend sends the alert to receiver devices in real time.

The database is used so that no SOS alert is lost.

WebSocket is used so that receivers get alerts immediately without refreshing the page.

The `uploads` folder is used to store emergency images.

---

## 31. Final Summary

This backend is the center of the Women Safety System.

It connects:

```txt
Sender mobile app
Receiver mobile app
MySQL database
SOS alert system
Image upload system
SMS log system
Location tracking system
WebSocket real-time alert system
```

The backend receives SOS alerts, stores them, and broadcasts them instantly.

Main local URL:

```txt
http://localhost:8000
```

Mobile same Wi-Fi URL:

```txt
http://LAPTOP_IP:8000
```

Swagger API docs:

```txt
http://localhost:8000/docs
```

WebSocket URL:

```txt
ws://localhost:8000/ws/alerts
```
