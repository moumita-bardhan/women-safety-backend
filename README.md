# Women Safety Local Server Backend Documentation

This backend is a local FastAPI server for a Women Safety application.

It is used to:

- Register mobile devices
- Save emergency contacts
- Update device location
- Create SOS alerts
- Upload SOS images
- Save SMS sending logs
- Store location history
- Show SOS alerts
- Show registered devices
- Send live SOS alerts through WebSocket

---

# 1. Technology Used

This backend uses:

- Python
- FastAPI
- SQLAlchemy
- MySQL
- PyMySQL
- python-dotenv
- WebSocket
- Multipart form-data
- Local file upload storage

---

# 2. Main Files

Your backend mainly has these files:

```txt
project/
│
├── main.py
├── models.py
├── database.py
├── .env
└── uploads/