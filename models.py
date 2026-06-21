from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    DECIMAL,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


# This class stores the main user information like sender, receiver, or admin.
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    role = Column(Enum("SENDER", "RECEIVER", "ADMIN"), nullable=False, default="SENDER")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)


# This class stores device information connected with a user.
class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    device_uuid = Column(String(150), nullable=False, unique=True)
    device_name = Column(String(100), nullable=True)

    device_type = Column(
        Enum("ANDROID_SENDER", "ANDROID_RECEIVER", "ANDROID_BOTH", "LAPTOP_SERVER"),
        nullable=False,
        default="ANDROID_BOTH",
    )

    fcm_token = Column(Text, nullable=True)
    is_receiver_enabled = Column(Boolean, default=True)

    last_latitude = Column(DECIMAL(10, 8), nullable=True)
    last_longitude = Column(DECIMAL(11, 8), nullable=True)
    last_location_at = Column(DateTime, nullable=True)
    last_connected_at = Column(DateTime, nullable=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)


# This class stores emergency contacts linked with a user and device.
class EmergencyContact(Base):
    __tablename__ = "emergency_contacts"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=True)

    contact_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    relation = Column(String(50), nullable=True)
    priority = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.now)


# This class stores the main SOS alert details like location, status, image, SMS, CNN result, and audio relation.
class SOSAlert(Base):
    __tablename__ = "sos_alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_code = Column(String(20), nullable=False, unique=True)

    sender_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    sender_device_id = Column(Integer, ForeignKey("devices.id"), nullable=True)

    triggered_by = Column(
        Enum(
            "SOS_BUTTON",
            "SHAKE_DETECTION",
            "FALL_DETECTION",
            "CNN_DETECTION",
            "MANUAL_TEST",
        ),
        nullable=False,
    )

    status = Column(
        Enum("TRIGGERED", "SENT", "RECEIVED", "RESOLVED", "CANCELLED"),
        default="TRIGGERED",
    )

    latitude = Column(DECIMAL(10, 8), nullable=True)
    longitude = Column(DECIMAL(11, 8), nullable=True)
    map_link = Column(Text, nullable=True)

    image_path = Column(Text, nullable=True)

    sms_status = Column(
        Enum("PENDING", "SENT", "FAILED", "PARTIAL", "NOT_REQUIRED"),
        default="PENDING",
    )
    sms_sent_count = Column(Integer, default=0)
    sms_failed_count = Column(Integer, default=0)
    sms_sent_at = Column(DateTime, nullable=True)

    cnn_label = Column(String(50), nullable=True)
    cnn_confidence = Column(DECIMAL(5, 4), nullable=True)

    created_at = Column(DateTime, default=datetime.now)

    # Links one SOS alert with its uploaded voice/audio records.
    audios = relationship(
        "SosAlertAudio",
        back_populates="sos_alert",
        cascade="all, delete-orphan",
    )


# This class stores multiple images uploaded for a single SOS alert.
class SOSAlertImage(Base):
    __tablename__ = "sos_alert_images"

    id = Column(Integer, primary_key=True, index=True)
    sos_alert_id = Column(Integer, ForeignKey("sos_alerts.id"), nullable=False)

    image_path = Column(Text, nullable=False)
    image_order = Column(Integer, default=1)
    camera_type = Column(Enum("BACK", "FRONT"), nullable=False)

    created_at = Column(DateTime, default=datetime.now)


# This class stores SMS sending logs for each SOS alert.
class SMSLog(Base):
    __tablename__ = "sms_logs"

    id = Column(Integer, primary_key=True, index=True)
    sos_alert_id = Column(Integer, ForeignKey("sos_alerts.id"), nullable=False)

    contact_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=False)
    status = Column(Enum("SENT", "FAILED"), nullable=False)
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.now)


# This class stores location history for devices and SOS alerts.
class LocationLog(Base):
    __tablename__ = "location_logs"

    id = Column(Integer, primary_key=True, index=True)

    device_id = Column(Integer, ForeignKey("devices.id"), nullable=True)
    sos_alert_id = Column(Integer, ForeignKey("sos_alerts.id"), nullable=True)

    latitude = Column(DECIMAL(10, 8), nullable=False)
    longitude = Column(DECIMAL(11, 8), nullable=False)
    map_link = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.now)


# This class stores logs about how receiver devices handled an SOS alert.
class ReceiverLog(Base):
    __tablename__ = "receiver_logs"

    id = Column(Integer, primary_key=True, index=True)

    sos_alert_id = Column(Integer, ForeignKey("sos_alerts.id"), nullable=False)
    receiver_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    receiver_device_id = Column(Integer, ForeignKey("devices.id"), nullable=True)

    status = Column(Enum("RECEIVED", "OPENED", "FAILED"), default="RECEIVED")
    vibrated = Column(Boolean, default=False)
    sound_played = Column(Boolean, default=False)
    notification_shown = Column(Boolean, default=False)

    received_at = Column(DateTime, default=datetime.now)


# This class stores notification records sent to receiver devices for SOS alerts.
class ReceiverNotification(Base):
    __tablename__ = "receiver_notifications"

    id = Column(Integer, primary_key=True, index=True)

    sos_alert_id = Column(Integer, ForeignKey("sos_alerts.id"), nullable=False)
    receiver_device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)

    distance_meter = Column(DECIMAL(10, 2), nullable=True)

    notification_status = Column(
        Enum("PENDING", "SENT", "FAILED", "OPENED", "ACKNOWLEDGED"),
        default="PENDING",
    )

    created_at = Column(DateTime, default=datetime.now)


# This class stores uploaded emergency voice/audio files for one SOS alert.
class SosAlertAudio(Base):
    __tablename__ = "sos_alert_audios"

    id = Column(Integer, primary_key=True, index=True)

    sos_alert_id = Column(
        Integer,
        ForeignKey("sos_alerts.id"),
        nullable=False,
        index=True,
    )

    audio_path = Column(String(500), nullable=False)
    original_filename = Column(String(255), nullable=True)
    mime_type = Column(String(100), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    size_bytes = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Correct relationship name is SOSAlert because your class is class SOSAlert(Base).
    sos_alert = relationship(
        "SOSAlert",
        back_populates="audios",
    )