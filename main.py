# Imports the datetime class so the code can store current timestamps.
from datetime import datetime
# Imports Path to safely build file and folder paths.
from pathlib import Path
# Imports json to convert JSON strings to Python objects and Python objects to JSON strings.
import json
# Imports shutil to copy uploaded file data into local files.
import shutil
# Imports uuid to generate unique SOS alert codes.
import uuid

# Starts importing required classes and helpers from FastAPI.
from fastapi import (
    # Injects dependencies like the database session into route functions.
    Depends,
    # Creates the main FastAPI application instance.
    FastAPI,
    # Defines file upload fields in request forms.
    File,
    # Defines normal form fields in multipart/form-data requests.
    Form,
    # Represents an uploaded file received from the client.
    UploadFile,
    # Raises an HTTP error response when uploaded audio is invalid.
    HTTPException,
    # Represents a WebSocket client connection.
    WebSocket,
    # Exception raised when a WebSocket client disconnects.
    WebSocketDisconnect,
# Ends the FastAPI import list.
)
# Imports StaticFiles so uploaded images can be served from a public URL path.
from fastapi.staticfiles import StaticFiles
# Imports SQLAlchemy Session type for database operations.
from sqlalchemy.orm import Session

# Imports database Base metadata, engine connection, and get_db dependency.
from database import Base, engine, get_db
# Starts importing all database models used by this API file.
from models import (
    # Device model stores registered Android/device information.
    Device,
    # EmergencyContact model stores emergency contact details.
    EmergencyContact,
    # LocationLog model stores device or SOS location history.
    LocationLog,
    # ReceiverLog model is imported for receiver-related logging usage.
    ReceiverLog,
    # ReceiverNotification model is imported for receiver notification records.
    ReceiverNotification,
    # SOSAlert model stores main SOS alert records.
    SOSAlert,
    # SOSAlertImage model stores multiple uploaded images for one SOS alert.
    SOSAlertImage,
    # SosAlertAudio model stores uploaded emergency voice recordings for one SOS alert.
    SosAlertAudio,
    # SMSLog model stores SMS sending result logs.
    SMSLog,
    # User model stores sender or receiver user details.
    User,
# Ends the models import list.
)

# Gets the folder path where this Python file is located.
BASE_DIR = Path(__file__).resolve().parent
# Creates the uploads folder path inside the current project folder.
UPLOAD_DIR = BASE_DIR / "uploads"
# Creates the uploads folder if it does not already exist.
UPLOAD_DIR.mkdir(exist_ok=True)

# Creates a separate folder path for uploaded emergency voice recordings.
AUDIO_UPLOAD_DIR = UPLOAD_DIR / "audio"
# Creates the audio upload folder if it does not already exist.
AUDIO_UPLOAD_DIR.mkdir(exist_ok=True)

# Stores the allowed audio MIME types accepted from the mobile app.
ALLOWED_AUDIO_MIME_TYPES = {
    # Android .m4a / AAC recording usually comes as audio/mp4.
    "audio/mp4",
    # Some clients may send .m4a with this MIME type.
    "audio/m4a",
    # AAC audio MIME type.
    "audio/aac",
    # MP3 audio MIME type, allowed for testing or future support.
    "audio/mpeg",
    # Android 3GP audio MIME type.
    "audio/3gpp",
    # AMR audio MIME type.
    "audio/amr",
    # Some Android/React Native uploads may send this generic MIME type.
    "application/octet-stream",
}

# Sets the maximum allowed SOS voice recording size to 10 MB.
MAX_AUDIO_SIZE_BYTES = 10 * 1024 * 1024

# Creates the FastAPI application and sets the API title.
app = FastAPI(title="Women Safety Local Server")

# Makes the uploads folder publicly accessible through the /uploads URL path.
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Creates database tables from SQLAlchemy models if they do not already exist.
Base.metadata.create_all(bind=engine)


# Defines a helper class to manage all active WebSocket connections.
class ConnectionManager:
    # Runs when a new ConnectionManager object is created.
    def __init__(self):
        # Stores the currently connected WebSocket clients.
        self.active_connections: list[WebSocket] = []

    # Accepts and stores a new WebSocket connection.
    async def connect(self, websocket: WebSocket):
        # Accepts the WebSocket handshake from the client.
        await websocket.accept()
        # Adds this WebSocket connection to the active connections list.
        self.active_connections.append(websocket)

    # Removes a WebSocket connection when the client disconnects or fails.
    def disconnect(self, websocket: WebSocket):
        # Checks whether this WebSocket is still present in the active list.
        if websocket in self.active_connections:
            # Removes the WebSocket from the active connections list.
            self.active_connections.remove(websocket)

    # Sends the same data to all connected WebSocket clients.
    async def broadcast(self, data: dict):
        # Stores connections that fail while sending data.
        disconnected = []

        # Loops through every currently active WebSocket connection.
        for connection in self.active_connections:
            # Tries to send the alert data to this connection.
            try:
                # Converts Python dict data to JSON text and sends it through WebSocket.
                await connection.send_text(json.dumps(data, default=str))
            # Handles any send failure, usually caused by a broken/disconnected socket.
            except Exception:
                # Marks this failed connection for removal after the loop.
                disconnected.append(connection)

        # Loops through all failed WebSocket connections.
        for connection in disconnected:
            # Removes each failed connection from the active connections list.
            self.disconnect(connection)


# Creates one shared WebSocket connection manager for the whole app.
manager = ConnectionManager()


# Defines a helper function to generate a short alert code.
def create_alert_code() -> str:
    # Generates a UUID, takes the first 8 characters, and converts them to uppercase.
    return str(uuid.uuid4())[:8].upper()


# Defines a helper function to create a Google Maps link from latitude and longitude.
def get_map_link(latitude: float, longitude: float) -> str:
    # Returns a Google Maps URL with the given latitude and longitude.
    return f"https://maps.google.com/?q={latitude},{longitude}"


# Defines a placeholder CNN prediction function for image analysis.
def fake_cnn_prediction(image_path: str | None):
    # Checks whether there is no image path available.
    if not image_path:
        # Returns a default result when no image was uploaded.
        return {
            # Marks the result label as NO_IMAGE.
            "label": "NO_IMAGE",
            # Sets confidence to zero because no prediction was performed.
            "confidence": 0.0,
        }

    # Returns a default result when an image exists but real CNN logic is not implemented.
    return {
        # Marks the result label as UNKNOWN.
        "label": "UNKNOWN",
        # Sets confidence to zero because this is only fake prediction logic.
        "confidence": 0.0,
    }


# Defines a helper function to save one uploaded image file locally.
def save_uploaded_image(alert_code: str, uploaded_image: UploadFile, index: int, camera_type: str):
    # Gets the file extension from the uploaded filename, or uses .jpg if missing.
    extension = Path(uploaded_image.filename or "").suffix or ".jpg"
    # Converts the camera type to lowercase for use inside the filename.
    safe_camera_type = camera_type.lower()

    # Creates a unique image filename using alert code, camera type, image number, and extension.
    filename = f"{alert_code}-{safe_camera_type}-{index + 1}{extension}"
    # Builds the full local file path where the uploaded image will be saved.
    image_file_path = UPLOAD_DIR / filename

    # Opens the target image path in binary write mode.
    with image_file_path.open("wb") as buffer:
        # Copies the uploaded file stream into the local image file.
        shutil.copyfileobj(uploaded_image.file, buffer)

    # Returns the public URL path that can be used to access the uploaded image.
    return f"/uploads/{filename}"


# Defines a helper function to decide the audio file extension.
def get_audio_extension(uploaded_audio: UploadFile) -> str:
    # Gets the uploaded filename or an empty string when no filename is present.
    filename = uploaded_audio.filename or ""
    # Gets the file extension from the uploaded filename and converts it to lowercase.
    extension = Path(filename).suffix.lower()

    # Checks whether the uploaded file already has a supported audio extension.
    if extension in [".m4a", ".mp4", ".aac", ".mp3", ".3gp", ".amr"]:
        # Returns the original safe extension.
        return extension

    # Gets the MIME type sent by the client.
    content_type = uploaded_audio.content_type or ""

    # Uses .m4a for audio/mp4 because Android AAC recording is usually stored as .m4a.
    if content_type == "audio/mp4":
        # Returns .m4a extension.
        return ".m4a"

    # Uses .m4a when the client directly sends audio/m4a.
    if content_type == "audio/m4a":
        # Returns .m4a extension.
        return ".m4a"

    # Uses .aac for AAC audio.
    if content_type == "audio/aac":
        # Returns .aac extension.
        return ".aac"

    # Uses .mp3 for MPEG audio.
    if content_type == "audio/mpeg":
        # Returns .mp3 extension.
        return ".mp3"

    # Uses .3gp for 3GPP audio.
    if content_type == "audio/3gpp":
        # Returns .3gp extension.
        return ".3gp"

    # Uses .amr for AMR audio.
    if content_type == "audio/amr":
        # Returns .amr extension.
        return ".amr"

    # Falls back to .m4a because this is the recommended app recording format.
    return ".m4a"


# Defines a helper function to save one uploaded emergency voice recording locally.
def save_uploaded_audio(alert_code: str, uploaded_audio: UploadFile):
    # Gets the MIME type sent with the audio file, or uses a generic fallback.
    content_type = uploaded_audio.content_type or "application/octet-stream"

    # Checks whether the uploaded audio MIME type is allowed.
    if content_type not in ALLOWED_AUDIO_MIME_TYPES:
        # Stops the request with a clear validation error.
        raise HTTPException(
            # Sends HTTP 400 because the client uploaded an invalid file type.
            status_code=400,
            # Explains which MIME type was rejected.
            detail=f"Invalid audio type: {content_type}",
        )

    # Gets a safe audio extension for the saved file.
    extension = get_audio_extension(uploaded_audio)
    # Creates the audio filename using the alert code and selected extension.
    filename = f"{alert_code}-emergency-audio{extension}"
    # Builds the full local path for the uploaded audio file.
    audio_file_path = AUDIO_UPLOAD_DIR / filename

    # Starts the uploaded audio size counter.
    total_size = 0

    # Opens the target audio path in binary write mode.
    with audio_file_path.open("wb") as buffer:
        # Reads the uploaded audio file in chunks so big files do not load fully into memory.
        while True:
            # Reads up to 1 MB from the uploaded audio stream.
            chunk = uploaded_audio.file.read(1024 * 1024)

            # Stops the loop when there is no more file data.
            if not chunk:
                # Breaks out of the while loop.
                break

            # Adds the current chunk size to the total uploaded size.
            total_size += len(chunk)

            # Checks whether the uploaded audio is larger than the allowed limit.
            if total_size > MAX_AUDIO_SIZE_BYTES:
                # Closes the destination file before deleting it.
                buffer.close()
                # Deletes the partially saved audio file.
                audio_file_path.unlink(missing_ok=True)
                # Stops the request with a clear validation error.
                raise HTTPException(
                    # Sends HTTP 400 because the uploaded file is too large.
                    status_code=400,
                    # Explains the maximum allowed audio size.
                    detail="Audio file is too large. Maximum allowed size is 10 MB.",
                )

            # Writes the current chunk into the saved audio file.
            buffer.write(chunk)

    # Returns audio metadata needed for database saving and API response.
    return {
        # Stores the public URL path for opening the audio file.
        "path": f"/uploads/audio/{filename}",
        # Stores the original client-side filename.
        "original_filename": uploaded_audio.filename,
        # Stores the MIME type sent by the client.
        "mime_type": content_type,
        # Stores the final saved audio size in bytes.
        "size_bytes": total_size,
    }


# Registers the root health-check API endpoint.
@app.get("/")
# Defines the function that handles GET / requests.
def home():
    # Returns a simple success response showing the server is running.
    return {
        # Shows that the request was successful.
        "success": True,
        # Sends a readable server status message.
        "message": "Women Safety Local Server is running",
    }


# Registers the API endpoint used to register or update a device.
@app.post("/api/devices/register")
# Defines the device registration route handler.
def register_device(
    # Reads the user's name from form-data and makes it required.
    name: str = Form(...),
    # Reads the phone number from form-data and defaults to an empty string.
    phone: str = Form(""),
    # Reads the unique device UUID from form-data and makes it required.
    device_uuid: str = Form(...),
    # Reads the device name from form-data and defaults to Android Device.
    device_name: str = Form("Android Device"),
    # Reads the device type from form-data and defaults to ANDROID_BOTH.
    device_type: str = Form("ANDROID_BOTH"),
    # Reads the FCM token from form-data and defaults to an empty string.
    fcm_token: str = Form(""),
    # Injects the database session using the get_db dependency.
    db: Session = Depends(get_db),
# Ends the function parameter list.
):
    # Searches for an existing device using the given device UUID.
    device = db.query(Device).filter(Device.device_uuid == device_uuid).first()

    # Checks whether the device already exists in the database.
    if device:
        # Updates the saved device name.
        device.device_name = device_name
        # Updates the saved device type.
        device.device_type = device_type
        # Updates the saved FCM token.
        device.fcm_token = fcm_token
        # Stores the current time as the latest connected time.
        device.last_connected_at = datetime.now()
        # Marks the device as active.
        device.is_active = True

        # Saves the updated device data into the database.
        db.commit()
        # Reloads the updated device record from the database.
        db.refresh(device)

        # Returns a success response for the updated device.
        return {
            # Shows that the update was successful.
            "success": True,
            # Sends a readable update message.
            "message": "Device updated successfully",
            # Starts the response data object.
            "data": {
                # Sends the user ID linked with this device.
                "user_id": device.user_id,
                # Sends the device database ID.
                "device_id": device.id,
                # Sends the device UUID.
                "device_uuid": device.device_uuid,
            # Ends the response data object.
            },
        # Ends the response object.
        }

    # Creates a new user object for a newly registered device.
    user = User(
        # Stores the sender user's name.
        name=name,
        # Stores the sender user's phone number.
        phone=phone,
        # Sets the user role as SENDER.
        role="SENDER",
    # Ends the User object creation.
    )

    # Adds the new user object to the database session.
    db.add(user)
    # Saves the new user into the database.
    db.commit()
    # Reloads the user so generated fields like id become available.
    db.refresh(user)

    # Creates a new device object linked with the newly created user.
    device = Device(
        # Links the device with the created user ID.
        user_id=user.id,
        # Stores the unique device UUID.
        device_uuid=device_uuid,
        # Stores the device name.
        device_name=device_name,
        # Stores the device type.
        device_type=device_type,
        # Stores the FCM token.
        fcm_token=fcm_token,
        # Enables receiver feature for this device by default.
        is_receiver_enabled=True,
        # Stores the current time as the latest connected time.
        last_connected_at=datetime.now(),
    # Ends the Device object creation.
    )

    # Adds the new device object to the database session.
    db.add(device)
    # Saves the new device into the database.
    db.commit()
    # Reloads the device so generated fields like id become available.
    db.refresh(device)

    # Returns a success response for the newly registered device.
    return {
        # Shows that the registration was successful.
        "success": True,
        # Sends a readable registration message.
        "message": "Device registered successfully",
        # Starts the response data object.
        "data": {
            # Sends the newly created user ID.
            "user_id": user.id,
            # Sends the newly created device ID.
            "device_id": device.id,
            # Sends the registered device UUID.
            "device_uuid": device.device_uuid,
        # Ends the response data object.
        },
    # Ends the response object.
    }


# Registers the API endpoint used to update a device's latest location.
@app.post("/api/devices/location")
# Defines the location update route handler.
def update_device_location(
    # Reads the device UUID from form-data and makes it required.
    device_uuid: str = Form(...),
    # Reads the latitude from form-data and makes it required.
    latitude: float = Form(...),
    # Reads the longitude from form-data and makes it required.
    longitude: float = Form(...),
    # Injects the database session using the get_db dependency.
    db: Session = Depends(get_db),
# Ends the function parameter list.
):
    # Searches for the device by its UUID.
    device = db.query(Device).filter(Device.device_uuid == device_uuid).first()

    # Checks whether the device does not exist.
    if not device:
        # Returns an error response when the device is not found.
        return {
            # Shows that the request failed.
            "success": False,
            # Sends a readable not-found message.
            "message": "Device not found",
        # Ends the response object.
        }

    # Creates a Google Maps link using the submitted location.
    map_link = get_map_link(latitude, longitude)

    # Updates the device's latest latitude.
    device.last_latitude = latitude
    # Updates the device's latest longitude.
    device.last_longitude = longitude
    # Updates the time when the location was last received.
    device.last_location_at = datetime.now()

    # Starts adding a location log record to the database session.
    db.add(
        # Creates a new location log entry.
        LocationLog(
            # Links this location log to the current device.
            device_id=device.id,
            # Stores the latitude.
            latitude=latitude,
            # Stores the longitude.
            longitude=longitude,
            # Stores the generated Google Maps link.
            map_link=map_link,
        # Ends the LocationLog object creation.
        )
    # Ends the db.add call.
    )

    # Saves the device update and location log into the database.
    db.commit()

    # Returns a success response after saving the location.
    return {
        # Shows that the request was successful.
        "success": True,
        # Sends a readable location update message.
        "message": "Location updated successfully",
    # Ends the response object.
    }


# Registers the API endpoint used to create an emergency contact.
@app.post("/api/emergency-contacts")
# Defines the create emergency contact route handler.
def create_emergency_contact(
    # Reads the device UUID from form-data and makes it required.
    device_uuid: str = Form(...),
    # Reads the contact name from form-data and makes it required.
    contact_name: str = Form(...),
    # Reads the emergency contact phone number from form-data and makes it required.
    phone: str = Form(...),
    # Reads the relation from form-data and defaults to an empty string.
    relation: str = Form(""),
    # Reads the priority from form-data and defaults to 1.
    priority: int = Form(1),
    # Injects the database session using the get_db dependency.
    db: Session = Depends(get_db),
# Ends the function parameter list.
):
    # Searches for the device using the given device UUID.
    device = db.query(Device).filter(Device.device_uuid == device_uuid).first()

    # Checks whether the device is missing.
    if not device:
        # Returns an error response when the device is not registered.
        return {
            # Shows that the request failed.
            "success": False,
            # Sends a readable message asking to register the device first.
            "message": "Device not found. Please register device first.",
        # Ends the response object.
        }

    # Creates a new emergency contact object.
    contact = EmergencyContact(
        # Links the contact to the user attached to the device.
        user_id=device.user_id,
        # Links the contact to the current device.
        device_id=device.id,
        # Stores the contact name.
        contact_name=contact_name,
        # Stores the contact phone number.
        phone=phone,
        # Stores the relationship text.
        relation=relation,
        # Stores the contact priority order.
        priority=priority,
        # Marks the contact as active.
        is_active=True,
    # Ends the EmergencyContact object creation.
    )

    # Adds the contact object to the database session.
    db.add(contact)
    # Saves the contact into the database.
    db.commit()
    # Reloads the contact so generated fields like id become available.
    db.refresh(contact)

    # Returns a success response with the saved contact details.
    return {
        # Shows that the contact was saved successfully.
        "success": True,
        # Sends a readable contact saved message.
        "message": "Emergency contact saved successfully",
        # Starts the contact data object.
        "data": {
            # Sends the contact database ID.
            "id": contact.id,
            # Sends the saved contact name.
            "contact_name": contact.contact_name,
            # Sends the saved phone number.
            "phone": contact.phone,
            # Sends the saved relation.
            "relation": contact.relation,
            # Sends the saved priority.
            "priority": contact.priority,
            # Sends the active status.
            "is_active": contact.is_active,
        # Ends the contact data object.
        },
    # Ends the response object.
    }


# Registers the API endpoint used to fetch emergency contacts by device UUID.
@app.get("/api/emergency-contacts/{device_uuid}")
# Defines the get emergency contacts route handler.
def get_emergency_contacts(
    # Gets the device UUID from the URL path.
    device_uuid: str,
    # Injects the database session using the get_db dependency.
    db: Session = Depends(get_db),
# Ends the function parameter list.
):
    # Searches for the device using the URL device UUID.
    device = db.query(Device).filter(Device.device_uuid == device_uuid).first()

    # Checks whether the device was not found.
    if not device:
        # Returns an error response with an empty contacts list.
        return {
            # Shows that the request failed.
            "success": False,
            # Sends a readable device not found message.
            "message": "Device not found",
            # Sends an empty data list because no device means no contacts.
            "data": [],
        # Ends the response object.
        }

    # Starts a query to fetch active emergency contacts for this device.
    contacts = (
        # Creates a query on the EmergencyContact table.
        db.query(EmergencyContact)
        # Applies filters to get only active contacts for this device.
        .filter(
            # Keeps contacts linked with this device ID.
            EmergencyContact.device_id == device.id,
            # Keeps only active contacts.
            EmergencyContact.is_active == True,
        # Ends the filter condition list.
        )
        # Sorts contacts by priority in ascending order.
        .order_by(EmergencyContact.priority.asc())
        # Executes the query and returns all matching contacts.
        .all()
    # Ends the contacts query expression.
    )

    # Returns the fetched emergency contacts.
    return {
        # Shows that the request was successful.
        "success": True,
        # Starts a list response built from the contacts query result.
        "data": [
            # Starts one contact response object.
            {
                # Sends the contact ID.
                "id": item.id,
                # Sends the contact name.
                "contact_name": item.contact_name,
                # Sends the contact phone number.
                "phone": item.phone,
                # Sends the contact relation.
                "relation": item.relation,
                # Sends the contact priority.
                "priority": item.priority,
                # Sends the contact active status.
                "is_active": item.is_active,
            # Ends one contact response object.
            }
            # Loops through each emergency contact found in the database.
            for item in contacts
        # Ends the list response.
        ],
    # Ends the response object.
    }


# Registers the API endpoint used to create an SOS alert.
@app.post("/api/sos")
# Defines the async route handler for SOS alert creation.
async def create_sos_alert(
    # Reads the sender/user name from form-data and makes it required.
    user_name: str = Form(...),
    # Reads the SOS latitude from form-data and makes it required.
    latitude: float = Form(...),
    # Reads the SOS longitude from form-data and makes it required.
    longitude: float = Form(...),
    # Reads who triggered the SOS and defaults to SOS_BUTTON.
    triggered_by: str = Form("SOS_BUTTON"),
    # Reads the SMS status and defaults to PENDING.
    sms_status: str = Form("PENDING"),
    # Reads the number of successfully sent SMS messages and defaults to 0.
    sms_sent_count: int = Form(0),
    # Reads the number of failed SMS messages and defaults to 0.
    sms_failed_count: int = Form(0),
    # Reads SMS logs as a JSON string and defaults to an empty JSON array.
    sms_logs_json: str = Form("[]"),
    # Reads the optional device UUID and defaults to an empty string.
    device_uuid: str = Form(""),
    # Reads camera types as a JSON string and defaults to an empty JSON array.
    camera_types_json: str = Form("[]"),
    # Reads uploaded SOS images from multipart/form-data and defaults to an empty list.
    images: list[UploadFile] = File([]),
    # Reads one optional emergency voice recording from multipart/form-data.
    audio: UploadFile | None = File(None),
    # Reads optional audio duration in seconds from form-data.
    audio_duration_seconds: int | None = Form(None),
    # Reads optional audio MIME type from form-data.
    audio_mime_type: str = Form(""),
    # Injects the database session using the get_db dependency.
    db: Session = Depends(get_db),
# Ends the function parameter list.
):
    # Generates a unique short alert code for this SOS.
    alert_code = create_alert_code()
    # Creates a Google Maps link using the SOS latitude and longitude.
    map_link = get_map_link(latitude, longitude)

    # Initializes sender_device as None before checking the submitted device UUID.
    sender_device = None

    # Checks whether the request included a device UUID.
    if device_uuid:
        # Searches for the sender device by device UUID.
        sender_device = db.query(Device).filter(Device.device_uuid == device_uuid).first()

    # Tries to parse the submitted camera types JSON string.
    try:
        # Converts the camera types JSON string into a Python list.
        camera_types = json.loads(camera_types_json)
    # Handles invalid camera types JSON.
    except Exception:
        # Uses an empty list when the JSON parsing fails.
        camera_types = []

    # Initializes a list that will store information about saved uploaded images.
    saved_images = []

    # Loops through all uploaded images with their index number.
    for index, uploaded_image in enumerate(images):
        # Gets the matching camera type by index, or uses BACK as default.
        camera_type = camera_types[index] if index < len(camera_types) else "BACK"

        # Validates that camera type is only BACK or FRONT.
        if camera_type not in ["BACK", "FRONT"]:
            # Falls back to BACK if the camera type is invalid.
            camera_type = "BACK"

        # Saves the uploaded image locally and gets its public image path.
        image_path = save_uploaded_image(
            # Passes the generated alert code for filename creation.
            alert_code=alert_code,
            # Passes the uploaded image file object.
            uploaded_image=uploaded_image,
            # Passes the image index number.
            index=index,
            # Passes the validated camera type.
            camera_type=camera_type,
        # Ends the save_uploaded_image call.
        )

        # Adds metadata of the saved image into the saved_images list.
        saved_images.append(
            # Starts one saved image metadata object.
            {
                # Stores the public image path.
                "path": image_path,
                # Stores whether the image came from BACK or FRONT camera.
                "camera_type": camera_type,
                # Stores image order starting from 1.
                "order": index + 1,
            # Ends one saved image metadata object.
            }
        # Ends the saved_images append call.
        )

    # Picks the first uploaded image path as the main image path, or None if no image exists.
    first_image_path = saved_images[0]["path"] if saved_images else None

    # Runs the placeholder CNN prediction logic using the first image path.
    cnn_result = fake_cnn_prediction(first_image_path)

    # Creates the main SOS alert database object.
    sos_alert = SOSAlert(
        # Stores the generated alert code.
        alert_code=alert_code,
        # Stores sender user ID when a matching sender device exists.
        sender_user_id=sender_device.user_id if sender_device else None,
        # Stores sender device ID when a matching sender device exists.
        sender_device_id=sender_device.id if sender_device else None,
        # Stores what triggered this SOS alert.
        triggered_by=triggered_by,
        # Sets the SOS alert status as TRIGGERED.
        status="TRIGGERED",
        # Stores SOS latitude.
        latitude=latitude,
        # Stores SOS longitude.
        longitude=longitude,
        # Stores the Google Maps location link.
        map_link=map_link,
        # Stores the first image path as the main image path.
        image_path=first_image_path,
        # Stores the SMS sending status.
        sms_status=sms_status,
        # Stores count of sent SMS messages.
        sms_sent_count=sms_sent_count,
        # Stores count of failed SMS messages.
        sms_failed_count=sms_failed_count,
        # Stores SMS sent time only when SMS status is SENT or PARTIAL.
        sms_sent_at=datetime.now() if sms_status in ["SENT", "PARTIAL"] else None,
        # Stores the CNN label result.
        cnn_label=cnn_result["label"],
        # Stores the CNN confidence result.
        cnn_confidence=cnn_result["confidence"],
    # Ends the SOSAlert object creation.
    )

    # Adds the SOS alert object to the database session.
    db.add(sos_alert)
    # Saves the SOS alert so it gets a database ID.
    db.commit()
    # Reloads the SOS alert so generated fields like id and created_at become available.
    db.refresh(sos_alert)

    # Initializes audio_data as None because audio upload is optional.
    audio_data = None

    # Checks whether the mobile app sent an emergency voice recording.
    if audio is not None and audio.filename:
        # Saves the uploaded audio file locally and gets its metadata.
        saved_audio = save_uploaded_audio(
            # Passes the generated alert code for filename creation.
            alert_code=alert_code,
            # Passes the uploaded audio file object.
            uploaded_audio=audio,
        # Ends the save_uploaded_audio call.
        )

        # Creates a database record for the uploaded SOS audio.
        audio_record = SosAlertAudio(
            # Links this audio record to the saved SOS alert ID.
            sos_alert_id=sos_alert.id,
            # Stores the public audio file path.
            audio_path=saved_audio["path"],
            # Stores the original uploaded filename.
            original_filename=saved_audio["original_filename"],
            # Stores the submitted MIME type when available, otherwise detected upload MIME type.
            mime_type=audio_mime_type or saved_audio["mime_type"],
            # Stores the audio duration sent by the mobile app.
            duration_seconds=audio_duration_seconds,
            # Stores the uploaded audio file size in bytes.
            size_bytes=saved_audio["size_bytes"],
        # Ends the SosAlertAudio object creation.
        )

        # Adds the audio record to the database session.
        db.add(audio_record)
        # Saves the audio record so it gets a database ID.
        db.commit()
        # Reloads the audio record so generated fields like id and created_at become available.
        db.refresh(audio_record)

        # Builds the audio response object for API response and WebSocket broadcast.
        audio_data = {
            # Sends the audio database ID.
            "id": audio_record.id,
            # Sends the public audio URL path.
            "audio_url": audio_record.audio_path,
            # Sends the stored audio path.
            "audio_path": audio_record.audio_path,
            # Sends the audio MIME type.
            "mime_type": audio_record.mime_type,
            # Sends the audio duration in seconds.
            "duration_seconds": audio_record.duration_seconds,
            # Sends the audio size in bytes.
            "size_bytes": audio_record.size_bytes,
        # Ends the audio_data object.
        }

    # Loops through every saved image metadata object.
    for image in saved_images:
        # Adds a separate SOSAlertImage record for this saved image.
        db.add(
            # Creates the SOS alert image database object.
            SOSAlertImage(
                # Links this image to the saved SOS alert ID.
                sos_alert_id=sos_alert.id,
                # Stores the image path.
                image_path=image["path"],
                # Stores the image display/order number.
                image_order=image["order"],
                # Stores the camera type for this image.
                camera_type=image["camera_type"],
            # Ends the SOSAlertImage object creation.
            )
        # Ends the db.add call for SOSAlertImage.
        )

    # Adds a location log record for the SOS alert location.
    db.add(
        # Creates a new LocationLog object.
        LocationLog(
            # Links the log to the sender device ID when sender device exists.
            device_id=sender_device.id if sender_device else None,
            # Links the log to the SOS alert ID.
            sos_alert_id=sos_alert.id,
            # Stores the SOS latitude.
            latitude=latitude,
            # Stores the SOS longitude.
            longitude=longitude,
            # Stores the Google Maps link.
            map_link=map_link,
        # Ends the LocationLog object creation.
        )
    # Ends the db.add call for LocationLog.
    )

    # Tries to parse SMS logs JSON received from the client.
    try:
        # Converts the SMS logs JSON string into a Python list.
        sms_logs = json.loads(sms_logs_json)
    # Handles invalid SMS logs JSON.
    except Exception:
        # Uses an empty list when JSON parsing fails.
        sms_logs = []

    # Loops through each SMS log object from the parsed SMS logs list.
    for sms_log in sms_logs:
        # Adds one SMS log database record.
        db.add(
            # Creates the SMSLog database object.
            SMSLog(
                # Links this SMS log to the saved SOS alert.
                sos_alert_id=sos_alert.id,
                # Stores the emergency contact name from the SMS log object.
                contact_name=sms_log.get("name"),
                # Stores the emergency contact phone number from the SMS log object.
                phone=sms_log.get("phone"),
                # Stores the SMS status, defaulting to SENT when missing.
                status=sms_log.get("status", "SENT"),
                # Stores the SMS error message if available.
                error_message=sms_log.get("errorMessage"),
            # Ends the SMSLog object creation.
            )
        # Ends the db.add call for SMSLog.
        )

    # Saves SOS images, location log, SMS logs, and any pending SOS data into the database.
    db.commit()

    # Builds the response and WebSocket broadcast data for the new SOS alert.
    sos_data = {
        # Identifies this real-time message as an SOS alert event.
        "type": "SOS_ALERT",
        # Sends the saved SOS alert database ID.
        "id": sos_alert.id,
        # Sends the generated alert code.
        "alert_code": alert_code,
        # Sends the user name received from the request.
        "user_name": user_name,
        # Sends the SOS latitude.
        "latitude": latitude,
        # Sends the SOS longitude.
        "longitude": longitude,
        # Sends the Google Maps link.
        "map_link": map_link,
        # Sends the main image path.
        "image_path": first_image_path,
        # Sends the full list of saved image metadata.
        "images": saved_images,
        # Sends the total number of uploaded images.
        "image_count": len(saved_images),
        # Sends the uploaded emergency audio metadata, or None when no audio was uploaded.
        "audio": audio_data,
        # Tells the receiver whether this SOS alert has emergency audio.
        "has_audio": audio_data is not None,
        # Sends the SMS status.
        "sms_status": sms_status,
        # Sends the sent SMS count.
        "sms_sent_count": sms_sent_count,
        # Sends the failed SMS count.
        "sms_failed_count": sms_failed_count,
        # Sends the CNN label result.
        "cnn_label": cnn_result["label"],
        # Sends the CNN confidence result.
        "cnn_confidence": cnn_result["confidence"],
        # Sends what triggered this SOS.
        "triggered_by": triggered_by,
        # Sends the SOS created time as an ISO formatted string.
        "created_at": sos_alert.created_at.isoformat(),
    # Ends the sos_data object.
    }

    # Sends the new SOS alert data to all connected WebSocket clients.
    await manager.broadcast(sos_data)

    # Returns the SOS alert creation success response.
    return {
        # Shows that the SOS alert was created successfully.
        "success": True,
        # Sends a readable success message.
        "message": "SOS alert created successfully",
        # Sends the newly created SOS alert response data.
        "data": sos_data,
    # Ends the response object.
    }


# Registers the API endpoint used to fetch recent SOS alerts.
@app.get("/api/alerts")
# Defines the get alerts route handler.
def get_alerts(db: Session = Depends(get_db)):
    # Fetches the latest 50 SOS alerts ordered by newest ID first.
    alerts = db.query(SOSAlert).order_by(SOSAlert.id.desc()).limit(50).all()

    # Initializes the final response list.
    response_data = []

    # Loops through each SOS alert record.
    for item in alerts:
        # Starts a query to fetch images attached to the current SOS alert.
        alert_images = (
            # Creates a query on the SOSAlertImage table.
            db.query(SOSAlertImage)
            # Filters images by the current SOS alert ID.
            .filter(SOSAlertImage.sos_alert_id == item.id)
            # Sorts images by image order in ascending order.
            .order_by(SOSAlertImage.image_order.asc())
            # Executes the query and returns all matching images.
            .all()
        # Ends the alert images query expression.
        )

        # Starts a query to fetch the first audio recording attached to the current SOS alert.
        alert_audio = (
            # Creates a query on the SosAlertAudio table.
            db.query(SosAlertAudio)
            # Filters audio records by the current SOS alert ID.
            .filter(SosAlertAudio.sos_alert_id == item.id)
            # Sorts audio records by ID in ascending order.
            .order_by(SosAlertAudio.id.asc())
            # Executes the query and returns the first matching audio record.
            .first()
        # Ends the alert audio query expression.
        )

        # Builds the audio response object only when an audio record exists.
        audio_data = (
            # Starts one audio response object.
            {
                # Sends the audio database ID.
                "id": alert_audio.id,
                # Sends the public audio URL path.
                "audio_url": alert_audio.audio_path,
                # Sends the stored audio path.
                "audio_path": alert_audio.audio_path,
                # Sends the audio MIME type.
                "mime_type": alert_audio.mime_type,
                # Sends the audio duration in seconds.
                "duration_seconds": alert_audio.duration_seconds,
                # Sends the audio size in bytes.
                "size_bytes": alert_audio.size_bytes,
            # Ends one audio response object.
            }
            # Uses the audio object only when alert_audio exists.
            if alert_audio
            # Uses None when this alert does not have audio.
            else None
        # Ends audio_data expression.
        )

        # Adds the formatted SOS alert object to the response list.
        response_data.append(
            # Starts one SOS alert response object.
            {
                # Sends the SOS alert ID.
                "id": item.id,
                # Sends the SOS alert code.
                "alert_code": item.alert_code,
                # Sends latitude as float when available, otherwise None.
                "latitude": float(item.latitude) if item.latitude else None,
                # Sends longitude as float when available, otherwise None.
                "longitude": float(item.longitude) if item.longitude else None,
                # Sends the stored Google Maps link.
                "map_link": item.map_link,
                # Sends the main SOS image path.
                "image_path": item.image_path,
                # Starts the list of image objects for this SOS alert.
                "images": [
                    # Starts one image response object.
                    {
                        # Sends the image path.
                        "image_path": image.image_path,
                        # Sends the camera type.
                        "camera_type": image.camera_type,
                        # Sends the image order.
                        "image_order": image.image_order,
                    # Ends one image response object.
                    }
                    # Loops through every image linked with this SOS alert.
                    for image in alert_images
                # Ends the images list.
                ],
                # Sends the total number of images for this alert.
                "image_count": len(alert_images),
                # Sends the first emergency audio record for this alert, or None.
                "audio": audio_data,
                # Tells the client whether this alert has emergency audio.
                "has_audio": audio_data is not None,
                # Sends the SMS status.
                "sms_status": item.sms_status,
                # Sends the sent SMS count.
                "sms_sent_count": item.sms_sent_count,
                # Sends the failed SMS count.
                "sms_failed_count": item.sms_failed_count,
                # Sends the CNN label.
                "cnn_label": item.cnn_label,
                # Sends CNN confidence as float when available, otherwise None.
                "cnn_confidence": float(item.cnn_confidence) if item.cnn_confidence else None,
                # Sends what triggered the SOS.
                "triggered_by": item.triggered_by,
                # Sends the SOS created time as an ISO formatted string.
                "created_at": item.created_at.isoformat(),
            # Ends one SOS alert response object.
            }
        # Ends response_data append call.
        )

    # Returns the list of recent SOS alerts.
    return {
        # Shows that the request was successful.
        "success": True,
        # Sends the formatted SOS alert list.
        "data": response_data,
    # Ends the response object.
    }


# Registers the API endpoint used to fetch registered devices.
@app.get("/api/devices")
# Defines the get devices route handler.
def get_devices(db: Session = Depends(get_db)):
    # Fetches the latest 100 devices ordered by newest ID first.
    devices = db.query(Device).order_by(Device.id.desc()).limit(100).all()

    # Returns the registered devices response.
    return {
        # Shows that the request was successful.
        "success": True,
        # Starts a list response built from the fetched devices.
        "data": [
            # Starts one device response object.
            {
                # Sends the device database ID.
                "id": item.id,
                # Sends the user ID linked with the device.
                "user_id": item.user_id,
                # Sends the device UUID.
                "device_uuid": item.device_uuid,
                # Sends the device name.
                "device_name": item.device_name,
                # Sends the device type.
                "device_type": item.device_type,
                # Sends whether receiver mode is enabled for this device.
                "is_receiver_enabled": item.is_receiver_enabled,
                # Sends last latitude as float when available, otherwise None.
                "last_latitude": float(item.last_latitude) if item.last_latitude else None,
                # Sends last longitude as float when available, otherwise None.
                "last_longitude": float(item.last_longitude) if item.last_longitude else None,
                # Sends last location timestamp as ISO string when available.
                "last_location_at": item.last_location_at.isoformat() if item.last_location_at else None,
                # Sends last connected timestamp as ISO string when available.
                "last_connected_at": item.last_connected_at.isoformat() if item.last_connected_at else None,
            # Ends one device response object.
            }
            # Loops through every fetched device.
            for item in devices
        # Ends the devices list.
        ],
    # Ends the response object.
    }

# Registers the API endpoint used to fetch one SOS alert by alert code.
@app.get("/api/sos-alerts/{alert_code}")
# Defines the SOS alert details route handler.
def get_sos_alert_details(
    # Gets the alert code from the URL path.
    alert_code: str,
    # Injects the database session using the get_db dependency.
    db: Session = Depends(get_db),
# Ends the function parameter list.
):
    # Searches for one SOS alert using the given alert code.
    sos_alert = db.query(SOSAlert).filter(SOSAlert.alert_code == alert_code).first()

    # Checks whether no SOS alert was found for this code.
    if not sos_alert:
        # Returns a not-found response for missing SOS alert.
        return {
            # Shows that the request failed.
            "success": False,
            # Sends a readable not-found message.
            "message": "SOS alert not found",
            # Sends null data because there is no SOS alert record.
            "data": None,
        # Ends the response object.
        }

    # Starts a query to fetch all images attached to this SOS alert.
    alert_images = (
        # Creates a query on the SOSAlertImage table.
        db.query(SOSAlertImage)
        # Filters images by this SOS alert ID.
        .filter(SOSAlertImage.sos_alert_id == sos_alert.id)
        # Sorts images by image order in ascending order.
        .order_by(SOSAlertImage.image_order.asc())
        # Executes the query and returns all matching images.
        .all()
    # Ends the alert images query expression.
    )

    # Starts a query to fetch all audio recordings attached to this SOS alert.
    alert_audios = (
        # Creates a query on the SosAlertAudio table.
        db.query(SosAlertAudio)
        # Filters audio records by this SOS alert ID.
        .filter(SosAlertAudio.sos_alert_id == sos_alert.id)
        # Sorts audio records by ID in ascending order.
        .order_by(SosAlertAudio.id.asc())
        # Executes the query and returns all matching audio records.
        .all()
    # Ends the alert audios query expression.
    )

    # Returns the SOS alert details response.
    return {
        # Shows that the request was successful.
        "success": True,
        # Sends a readable success message.
        "message": "SOS alert details fetched successfully",
        # Starts the SOS alert details data object.
        "data": {
            # Sends the SOS alert database ID.
            "id": sos_alert.id,
            # Sends the SOS alert code.
            "alert_code": sos_alert.alert_code,
            # Sends an empty user name because this value is not fetched here.
            "user_name": "",
            # Sends latitude as string when available, otherwise empty string.
            "latitude": str(sos_alert.latitude) if sos_alert.latitude is not None else "",
            # Sends longitude as string when available, otherwise empty string.
            "longitude": str(sos_alert.longitude) if sos_alert.longitude is not None else "",
            # Sends the map link, or empty string when missing.
            "map_link": sos_alert.map_link or "",
            # Sends the trigger source, or empty string when missing.
            "triggered_by": sos_alert.triggered_by or "",
            # Sends the total number of images attached to this alert.
            "image_count": len(alert_images),
            # Sends the total number of audio recordings attached to this alert.
            "audio_count": len(alert_audios),
            # Tells the client whether this alert has emergency audio.
            "has_audio": len(alert_audios) > 0,
            # Starts formatting created_at only when it exists.
            "created_at": sos_alert.created_at.isoformat()
            # Checks whether created_at is available.
            if sos_alert.created_at
            # Returns empty string when created_at is missing.
            else "",
            # Starts the list of image details.
            "images": [
                # Starts one image details response object.
                {
                    # Sends the image database ID.
                    "id": image.id,
                    # Sends the image URL path, or empty string when missing.
                    "image_url": image.image_path or "",
                    # Sends the image path, or empty string when missing.
                    "image_path": image.image_path or "",
                    # Sends the camera type, or empty string when missing.
                    "camera_type": image.camera_type or "",
                    # Sends the image order.
                    "image_order": image.image_order,
                # Ends one image details response object.
                }
                # Loops through all images attached to this SOS alert.
                for image in alert_images
            # Ends the images list.
            ],
            # Starts the list of audio details.
            "audios": [
                # Starts one audio details response object.
                {
                    # Sends the audio database ID.
                    "id": audio_item.id,
                    # Sends the public audio URL path, or empty string when missing.
                    "audio_url": audio_item.audio_path or "",
                    # Sends the stored audio path, or empty string when missing.
                    "audio_path": audio_item.audio_path or "",
                    # Sends the original uploaded filename, or empty string when missing.
                    "original_filename": audio_item.original_filename or "",
                    # Sends the audio MIME type, or empty string when missing.
                    "mime_type": audio_item.mime_type or "",
                    # Sends the audio duration in seconds.
                    "duration_seconds": audio_item.duration_seconds,
                    # Sends the audio size in bytes.
                    "size_bytes": audio_item.size_bytes,
                    # Starts formatting created_at only when it exists.
                    "created_at": audio_item.created_at.isoformat()
                    # Checks whether created_at is available.
                    if audio_item.created_at
                    # Returns empty string when created_at is missing.
                    else "",
                # Ends one audio details response object.
                }
                # Loops through all audio records attached to this SOS alert.
                for audio_item in alert_audios
            # Ends the audios list.
            ],
        # Ends the SOS alert details data object.
        },
    # Ends the response object.
    }




# Registers the WebSocket endpoint used for live SOS alert updates.
@app.websocket("/ws/alerts")
# Defines the WebSocket route handler.
async def websocket_alerts(websocket: WebSocket):
    # Accepts the WebSocket connection and stores it in the manager.
    await manager.connect(websocket)

    # Keeps the WebSocket connection open until the client disconnects.
    try:
        # Starts an infinite loop to keep listening for incoming WebSocket messages.
        while True:
            # Waits for text from the client so the connection remains active.
            await websocket.receive_text()
    # Handles the case when the WebSocket client disconnects.
    except WebSocketDisconnect:
        # Removes the disconnected WebSocket from the active connections list.
        manager.disconnect(websocket)