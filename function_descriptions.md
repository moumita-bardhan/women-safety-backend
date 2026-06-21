# Women Safety Local Server - Function Description Documentation

This document explains every function and class method present in the uploaded FastAPI server file.  
The descriptions are based on the function names, decorators, parameters, and implementation logic.

---

## 1. File Purpose

This Python file creates a **FastAPI-based local server** for a women safety application.

Main responsibilities:

- Register Android/mobile devices.
- Store device locations.
- Manage emergency contacts.
- Create SOS alerts with location, images, SMS status, and CNN placeholder result.
- Save alert images locally.
- Broadcast SOS alerts in real time using WebSocket.
- Fetch devices, alerts, and SOS alert details.

---

## 2. Main Application Structure

```text
FastAPI App
├── Uploads setup
│   └── Serves uploaded images from /uploads
├── Database setup
│   └── Creates tables using SQLAlchemy metadata
├── ConnectionManager class
│   └── Handles active WebSocket clients
├── Helper functions
│   ├── create_alert_code()
│   ├── get_map_link()
│   ├── fake_cnn_prediction()
│   └── save_uploaded_image()
├── REST API routes
│   ├── GET  /
│   ├── POST /api/devices/register
│   ├── POST /api/devices/location
│   ├── POST /api/emergency-contacts
│   ├── GET  /api/emergency-contacts/{device_uuid}
│   ├── POST /api/sos
│   ├── GET  /api/alerts
│   ├── GET  /api/devices
│   └── GET  /api/sos-alerts/{alert_code}
└── WebSocket route
    └── WS /ws/alerts
```

---

## 3. Function Index

| No. | Function / Method Name | Type | Purpose |
|---:|---|---|---|
| 1 | `ConnectionManager.__init__()` | Class method | Initializes the active WebSocket connection list. |
| 2 | `ConnectionManager.connect()` | Async class method | Accepts and stores a new WebSocket client connection. |
| 3 | `ConnectionManager.disconnect()` | Class method | Removes a disconnected WebSocket client. |
| 4 | `ConnectionManager.broadcast()` | Async class method | Sends real-time data to all connected WebSocket clients. |
| 5 | `create_alert_code()` | Helper function | Generates a short unique SOS alert code. |
| 6 | `get_map_link()` | Helper function | Builds a Google Maps URL from latitude and longitude. |
| 7 | `fake_cnn_prediction()` | Helper function | Returns a placeholder image prediction result. |
| 8 | `save_uploaded_image()` | Helper function | Saves an uploaded image file into the local uploads folder. |
| 9 | `home()` | API route handler | Checks whether the server is running. |
| 10 | `register_device()` | API route handler | Registers a new device or updates an existing device. |
| 11 | `update_device_location()` | API route handler | Updates a device's latest location and saves a location log. |
| 12 | `create_emergency_contact()` | API route handler | Creates an emergency contact for a registered device. |
| 13 | `get_emergency_contacts()` | API route handler | Fetches emergency contacts for a device UUID. |
| 14 | `create_sos_alert()` | Async API route handler | Creates an SOS alert with location, images, SMS logs, and WebSocket broadcast. |
| 15 | `get_alerts()` | API route handler | Fetches the latest SOS alerts. |
| 16 | `get_devices()` | API route handler | Fetches registered devices. |
| 17 | `get_sos_alert_details()` | API route handler | Fetches full details of one SOS alert by alert code. |
| 18 | `websocket_alerts()` | Async WebSocket handler | Keeps a WebSocket client connected for live alert updates. |

---

# 4. Detailed Function Descriptions

---

## 4.1 `ConnectionManager.__init__()`

```python
def __init__(self):
```

### What this function does

This method runs automatically when a `ConnectionManager` object is created.

It initializes:

```python
self.active_connections: list[WebSocket] = []
```

### Main responsibility

To maintain a list of currently connected WebSocket clients.

### Used for

The server uses this list to know which clients should receive live SOS alert updates.

---

## 4.2 `ConnectionManager.connect()`

```python
async def connect(self, websocket: WebSocket):
```

### What this function does

This async method accepts a new WebSocket connection from a client and stores it in the active connection list.

### Step-by-step flow

1. Accepts the WebSocket handshake using:

```python
await websocket.accept()
```

2. Adds the connected WebSocket client to:

```python
self.active_connections
```

### Main responsibility

To register a newly connected WebSocket client so it can receive real-time SOS alerts.

### Used by

```python
websocket_alerts()
```

---

## 4.3 `ConnectionManager.disconnect()`

```python
def disconnect(self, websocket: WebSocket):
```

### What this function does

This method removes a WebSocket client from the active connection list.

### Step-by-step flow

1. Checks whether the WebSocket exists in `self.active_connections`.
2. Removes it if present.

### Main responsibility

To clean up disconnected or failed WebSocket connections.

### Used by

- `broadcast()`
- `websocket_alerts()`

---

## 4.4 `ConnectionManager.broadcast()`

```python
async def broadcast(self, data: dict):
```

### What this function does

This async method sends the same data to every connected WebSocket client.

### Step-by-step flow

1. Loops through all active WebSocket connections.
2. Converts the Python dictionary into JSON text using:

```python
json.dumps(data, default=str)
```

3. Sends the JSON text to each client.
4. If any connection fails, it is added to a temporary `disconnected` list.
5. Failed connections are removed after the loop.

### Main responsibility

To push real-time SOS alert data to all connected receivers.

### Important note

This function silently removes broken WebSocket connections so the server does not keep dead clients in memory.

---

## 4.5 `create_alert_code()`

```python
def create_alert_code() -> str:
```

### What this function does

This helper function generates a short unique alert code for every SOS alert.

### Logic

It creates a UUID, takes the first 8 characters, and converts them to uppercase.

Example output:

```text
A1B2C3D4
```

### Main responsibility

To create a readable unique code that identifies an SOS alert.

### Used by

```python
create_sos_alert()
```

---

## 4.6 `get_map_link()`

```python
def get_map_link(latitude: float, longitude: float) -> str:
```

### What this function does

This helper function creates a Google Maps link from latitude and longitude.

### Example

Input:

```python
latitude = 22.5726
longitude = 88.3639
```

Output:

```text
https://maps.google.com/?q=22.5726,88.3639
```

### Main responsibility

To convert GPS coordinates into a clickable Google Maps location link.

### Used by

- `update_device_location()`
- `create_sos_alert()`

---

## 4.7 `fake_cnn_prediction()`

```python
def fake_cnn_prediction(image_path: str | None):
```

### What this function does

This helper function is a placeholder for future CNN/image analysis logic.

### Current behavior

If no image exists, it returns:

```json
{
  "label": "NO_IMAGE",
  "confidence": 0.0
}
```

If an image exists, it returns:

```json
{
  "label": "UNKNOWN",
  "confidence": 0.0
}
```

### Main responsibility

To simulate CNN prediction until real machine-learning image analysis is implemented.

### Used by

```python
create_sos_alert()
```

### Important note

This is not a real CNN model yet. It only returns fixed/default values.

---

## 4.8 `save_uploaded_image()`

```python
def save_uploaded_image(
    alert_code: str,
    uploaded_image: UploadFile,
    index: int,
    camera_type: str
):
```

### What this function does

This helper function saves one uploaded image file into the local `uploads` folder.

### Parameters

| Parameter | Meaning |
|---|---|
| `alert_code` | Unique SOS alert code used in the image filename. |
| `uploaded_image` | Uploaded image file received from the client. |
| `index` | Image index number. |
| `camera_type` | Camera source, usually `BACK` or `FRONT`. |

### Step-by-step flow

1. Reads the uploaded file extension.
2. Uses `.jpg` if no extension is found.
3. Converts camera type to lowercase.
4. Creates a filename using alert code, camera type, and image order.
5. Saves the uploaded file into the local uploads folder.
6. Returns the public URL path of the image.

### Example output path

```text
/uploads/ABCD1234-back-1.jpg
```

### Main responsibility

To store SOS images locally and return a public image URL path.

### Used by

```python
create_sos_alert()
```

---

# 5. REST API Route Function Descriptions

---

## 5.1 `home()`

```python
@app.get("/")
def home():
```

### Endpoint

```http
GET /
```

### What this function does

This function is a basic server health-check endpoint.

### Response

It returns:

```json
{
  "success": true,
  "message": "Women Safety Local Server is running"
}
```

### Main responsibility

To confirm that the FastAPI server is running.

---

## 5.2 `register_device()`

```python
@app.post("/api/devices/register")
def register_device(...)
```

### Endpoint

```http
POST /api/devices/register
```

### What this function does

This function registers a new device or updates an existing device using `device_uuid`.

### Request form fields

| Field | Required | Description |
|---|---:|---|
| `name` | Yes | Sender/user name. |
| `phone` | No | User phone number. |
| `device_uuid` | Yes | Unique device identifier. |
| `device_name` | No | Device name. Default: `Android Device`. |
| `device_type` | No | Device type. Default: `ANDROID_BOTH`. |
| `fcm_token` | No | Firebase Cloud Messaging token. |

### Flow when device already exists

If a device with the same `device_uuid` is found:

1. Updates device name.
2. Updates device type.
3. Updates FCM token.
4. Updates last connected time.
5. Marks the device as active.
6. Returns the existing user ID and device ID.

### Flow when device is new

If no matching device is found:

1. Creates a new `User` with role `SENDER`.
2. Creates a new `Device` linked to that user.
3. Enables receiver mode by default.
4. Stores the latest connected time.
5. Returns new user ID, device ID, and device UUID.

### Main responsibility

To keep sender device registration data updated and ready for SOS usage.

---

## 5.3 `update_device_location()`

```python
@app.post("/api/devices/location")
def update_device_location(...)
```

### Endpoint

```http
POST /api/devices/location
```

### What this function does

This function updates the latest known location of a registered device.

### Request form fields

| Field | Required | Description |
|---|---:|---|
| `device_uuid` | Yes | Unique device identifier. |
| `latitude` | Yes | Current latitude. |
| `longitude` | Yes | Current longitude. |

### Step-by-step flow

1. Finds the device by `device_uuid`.
2. If the device is missing, returns `"Device not found"`.
3. Creates a Google Maps link from latitude and longitude.
4. Updates the device's latest latitude and longitude.
5. Updates the latest location timestamp.
6. Creates a `LocationLog` record.
7. Saves changes to the database.

### Main responsibility

To store the latest device location and maintain location history.

---

## 5.4 `create_emergency_contact()`

```python
@app.post("/api/emergency-contacts")
def create_emergency_contact(...)
```

### Endpoint

```http
POST /api/emergency-contacts
```

### What this function does

This function creates an emergency contact for a registered device.

### Request form fields

| Field | Required | Description |
|---|---:|---|
| `device_uuid` | Yes | Device UUID of the sender. |
| `contact_name` | Yes | Emergency contact name. |
| `phone` | Yes | Emergency contact phone number. |
| `relation` | No | Relationship with sender. |
| `priority` | No | Priority order. Default: `1`. |

### Step-by-step flow

1. Finds the device by `device_uuid`.
2. If the device does not exist, returns an error.
3. Creates an `EmergencyContact` record.
4. Links the contact to both the user and device.
5. Marks the contact as active.
6. Saves the contact.
7. Returns the saved contact details.

### Main responsibility

To save people who should be contacted during an emergency.

---

## 5.5 `get_emergency_contacts()`

```python
@app.get("/api/emergency-contacts/{device_uuid}")
def get_emergency_contacts(...)
```

### Endpoint

```http
GET /api/emergency-contacts/{device_uuid}
```

### What this function does

This function fetches active emergency contacts for a device.

### Path parameter

| Parameter | Description |
|---|---|
| `device_uuid` | Unique identifier of the device. |

### Step-by-step flow

1. Finds the device by `device_uuid`.
2. If the device is missing, returns an empty list.
3. Fetches active contacts linked with the device.
4. Sorts contacts by priority.
5. Returns the formatted contact list.

### Main responsibility

To return all active emergency contacts for a registered device.

---

## 5.6 `create_sos_alert()`

```python
@app.post("/api/sos")
async def create_sos_alert(...)
```

### Endpoint

```http
POST /api/sos
```

### What this function does

This is the main SOS alert creation function.

It creates an SOS alert with:

- Alert code.
- Sender device details.
- GPS location.
- Google Maps link.
- Uploaded images.
- Camera type information.
- SMS status and SMS logs.
- Placeholder CNN prediction result.
- WebSocket real-time broadcast.

### Request form fields

| Field | Required | Description |
|---|---:|---|
| `user_name` | Yes | Sender/user name. |
| `latitude` | Yes | SOS latitude. |
| `longitude` | Yes | SOS longitude. |
| `triggered_by` | No | Source of SOS trigger. Default: `SOS_BUTTON`. |
| `sms_status` | No | SMS sending status. Default: `PENDING`. |
| `sms_sent_count` | No | Number of SMS messages sent successfully. |
| `sms_failed_count` | No | Number of failed SMS messages. |
| `sms_logs_json` | No | JSON string containing SMS log objects. |
| `device_uuid` | No | Sender device UUID. |
| `camera_types_json` | No | JSON string containing camera types. |
| `images` | No | Uploaded SOS image files. |

### Step-by-step flow

1. Generates a new alert code using `create_alert_code()`.
2. Creates a Google Maps link using `get_map_link()`.
3. Finds the sender device if `device_uuid` is provided.
4. Parses `camera_types_json`.
5. Saves each uploaded image using `save_uploaded_image()`.
6. Uses the first image as the main alert image.
7. Runs placeholder CNN prediction using `fake_cnn_prediction()`.
8. Creates the main `SOSAlert` database record.
9. Saves all extra images into `SOSAlertImage`.
10. Creates a `LocationLog` record for the SOS location.
11. Parses and saves SMS logs into `SMSLog`.
12. Builds the final SOS response data.
13. Broadcasts the alert to all WebSocket clients.
14. Returns the created SOS alert data.

### Main responsibility

To create a complete SOS event and notify live dashboard/receiver clients immediately.

### Important note

This function is async because it uses WebSocket broadcasting with `await`.

---

## 5.7 `get_alerts()`

```python
@app.get("/api/alerts")
def get_alerts(db: Session = Depends(get_db)):
```

### Endpoint

```http
GET /api/alerts
```

### What this function does

This function fetches the latest SOS alerts.

### Step-by-step flow

1. Fetches the latest 50 SOS alerts.
2. Orders alerts by newest ID first.
3. For each alert, fetches linked images.
4. Formats latitude, longitude, image list, SMS status, CNN data, and creation time.
5. Returns the final alert list.

### Main responsibility

To provide recent SOS alert data for dashboard or admin display.

---

## 5.8 `get_devices()`

```python
@app.get("/api/devices")
def get_devices(db: Session = Depends(get_db)):
```

### Endpoint

```http
GET /api/devices
```

### What this function does

This function fetches registered devices.

### Step-by-step flow

1. Fetches latest 100 devices.
2. Orders devices by newest ID first.
3. Formats device data.
4. Converts latitude and longitude values to float where available.
5. Converts date/time values to ISO string where available.
6. Returns the device list.

### Main responsibility

To provide a list of registered devices and their latest known location information.

---

## 5.9 `get_sos_alert_details()`

```python
@app.get("/api/sos-alerts/{alert_code}")
def get_sos_alert_details(...)
```

### Endpoint

```http
GET /api/sos-alerts/{alert_code}
```

### What this function does

This function fetches detailed data for a single SOS alert using its alert code.

### Path parameter

| Parameter | Description |
|---|---|
| `alert_code` | Unique short code of the SOS alert. |

### Step-by-step flow

1. Finds one SOS alert by `alert_code`.
2. If the alert does not exist, returns a not-found response.
3. Fetches all images linked with the SOS alert.
4. Formats alert ID, location, map link, trigger source, image count, creation time, and image details.
5. Returns the SOS alert details.

### Main responsibility

To display full information for one SOS alert.

---

# 6. WebSocket Function Description

---

## 6.1 `websocket_alerts()`

```python
@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
```

### Endpoint

```text
WS /ws/alerts
```

### What this function does

This function handles live WebSocket connections for real-time SOS alert updates.

### Step-by-step flow

1. Accepts and registers the WebSocket connection using:

```python
await manager.connect(websocket)
```

2. Keeps the connection open using an infinite loop.
3. Waits for incoming text messages from the client.
4. If the client disconnects, catches `WebSocketDisconnect`.
5. Removes the client from the active connection list.

### Main responsibility

To keep dashboard/receiver clients connected so they can receive SOS alerts instantly.

### Used with

```python
manager.broadcast(sos_data)
```

When a new SOS alert is created, `create_sos_alert()` broadcasts the alert data to all clients connected through this WebSocket route.

---

# 7. Function Flow Summary

## 7.1 Device registration flow

```text
register_device()
├── Check device by device_uuid
├── If exists
│   ├── Update device data
│   └── Return existing user/device IDs
└── If new
    ├── Create User
    ├── Create Device
    └── Return new user/device IDs
```

## 7.2 Location update flow

```text
update_device_location()
├── Find device
├── Generate map link
├── Update latest location on Device
├── Insert LocationLog
└── Return success
```

## 7.3 Emergency contact flow

```text
create_emergency_contact()
├── Find device
├── Create EmergencyContact
└── Return saved contact

get_emergency_contacts()
├── Find device
├── Fetch active contacts
├── Sort by priority
└── Return contacts
```

## 7.4 SOS alert flow

```text
create_sos_alert()
├── Generate alert code
├── Generate map link
├── Find sender device
├── Parse camera types
├── Save uploaded images
├── Run fake CNN prediction
├── Create SOSAlert
├── Save SOSAlertImage records
├── Save LocationLog
├── Save SMSLog records
├── Broadcast through WebSocket
└── Return SOS alert response
```

## 7.5 Real-time WebSocket flow

```text
websocket_alerts()
├── Accept client connection
├── Store connection in manager
├── Keep connection alive
└── Remove client when disconnected

manager.broadcast()
├── Send data to all active clients
└── Remove failed clients
```

---

# 8. Notes and Improvement Suggestions

## 8.1 Add real CNN model later

Current function:

```python
fake_cnn_prediction()
```

is only placeholder logic. Later, this can be replaced with a real image classification or safety detection model.

## 8.2 Add stronger validation

Currently many route handlers return plain dictionaries for errors. In production, it is better to use:

```python
HTTPException
```

for proper HTTP status codes.

## 8.3 Avoid duplicate emergency contacts

`create_emergency_contact()` currently creates a new contact every time. You may add duplicate checking using phone number and device ID.

## 8.4 Secure uploaded image handling

`save_uploaded_image()` should ideally validate:

- File type.
- File size.
- Allowed extensions.
- MIME type.

## 8.5 Store full image URLs if needed

Currently image paths are returned like:

```text
/uploads/image-name.jpg
```

For mobile apps, you may need to convert this into a full URL, for example:

```text
http://server-ip:port/uploads/image-name.jpg
```

---

# 9. Quick API Reference

| Method | Endpoint | Function |
|---|---|---|
| GET | `/` | `home()` |
| POST | `/api/devices/register` | `register_device()` |
| POST | `/api/devices/location` | `update_device_location()` |
| POST | `/api/emergency-contacts` | `create_emergency_contact()` |
| GET | `/api/emergency-contacts/{device_uuid}` | `get_emergency_contacts()` |
| POST | `/api/sos` | `create_sos_alert()` |
| GET | `/api/alerts` | `get_alerts()` |
| GET | `/api/devices` | `get_devices()` |
| GET | `/api/sos-alerts/{alert_code}` | `get_sos_alert_details()` |
| WS | `/ws/alerts` | `websocket_alerts()` |

---

# 10. Quick Helper Reference

| Function | Description |
|---|---|
| `create_alert_code()` | Generates an 8-character uppercase SOS alert code. |
| `get_map_link()` | Creates a Google Maps link from latitude and longitude. |
| `fake_cnn_prediction()` | Returns placeholder CNN prediction data. |
| `save_uploaded_image()` | Saves uploaded SOS images into the local uploads folder. |

---

# 11. Quick Class Reference

| Class | Description |
|---|---|
| `ConnectionManager` | Manages WebSocket clients and broadcasts live SOS alerts. |

| Method | Description |
|---|---|
| `__init__()` | Initializes the active connection list. |
| `connect()` | Accepts and stores a WebSocket connection. |
| `disconnect()` | Removes a WebSocket connection. |
| `broadcast()` | Sends data to all active WebSocket clients. |
