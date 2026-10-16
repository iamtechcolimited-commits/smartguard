from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, NumericProperty
from kivy.clock import Clock
from kivy.lang import Builder
import os, json, hashlib, datetime, smtplib, threading, time, glob, base64, socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

try:
    from plyer import camera, gps
    from android.storage import app_storage_path
    from android.permissions import request_permissions, Permission
    from jnius import autoclass
    IS_ANDROID = True
    BASE_DIR = app_storage_path()
    request_permissions([Permission.CAMERA, Permission.ACCESS_FINE_LOCATION, Permission.ACCESS_COARSE_LOCATION, Permission.SEND_SMS, Permission.READ_SMS])
except:
    IS_ANDROID = False
    BASE_DIR = os.path.join(os.path.expanduser("~"), "SmartGuardMobile")
    os.makedirs(BASE_DIR, exist_ok=True)

CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
LOG_FILE = os.path.join(BASE_DIR, "audit_log.txt")
PHOTO_DIR = os.path.join(BASE_DIR, "Evidence")
os.makedirs(PHOTO_DIR, exist_ok=True)

MAX_TRIES = 3
LOCKOUT_TIME = 60
current_gps = {"lat": None, "lon": None, "address": "Getting location..."}

def hash_pin(pin): return hashlib.sha256(pin.encode()).hexdigest()
def encrypt_simple(text, key="SmartGuardMW"):
    enc = bytes([ord(c) ^ ord(key[i % len(key)]) for i, c in enumerate(text)])
    return base64.b64encode(enc).decode()
def decrypt_simple(enc_str, key="SmartGuardMW"):
    try:
        enc = base64.b64decode(enc_str.encode())
        return "".join([chr(b ^ ord(key[i % len(key)])) for i, b in enumerate(enc)])
    except: return ""

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f: return json.load(f)
        except: pass
    default = {
        "user_pin_hash": hash_pin("1234"),
        "master_pin_hash": hash_pin("8592"),
        "email": {"sender": "", "app_pass_enc": "", "receiver": "", "enabled": False},
        "sms": {"receiver_number": "", "enabled": True},
        "trial_start": time.time()
    }
    save_config(default)
    return default

def save_config(data):
    with open(CONFIG_FILE, "w") as f: json.dump(data, f, indent=2)

def log_attempt(msg):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {msg} | GPS: {current_gps}\n")
    except: pass

def has_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except: return False

def gps_on_location(**kwargs):
    global current_gps
    lat = kwargs.get('lat'); lon = kwargs.get('lon')
    if lat and lon:
        current_gps['lat'] = lat; current_gps['lon'] = lon
        current_gps['address'] = f"{lat:.6f}, {lon:.6f} | https://maps.google.com/?q={lat},{lon}"

def start_gps():
    try:
        if IS_ANDROID:
            gps.configure(on_location=gps_on_location)
            gps.start(minTime=1000, minDistance=1)
    except Exception as e: log_attempt(f"GPS Fail: {e}")

def get_real_location_text():
    if current_gps['lat'] and current_gps['lon']:
        return f"LAT: {current_gps['lat']:.6f}, LON: {current_gps['lon']:.6f}\nMaps: https://maps.google.com/?q={current_gps['lat']},{current_gps['lon']}"
    else:
        return f"{current_gps['address']} (No GPS fix yet)"

def send_sms_alert(location_text):
    cfg = load_config()
    sms_cfg = cfg.get("sms", {})
    if not sms_cfg.get("enabled"): return False
    number = sms_cfg.get("receiver_number","").strip()
    if not number: return False
    try:
        if IS_ANDROID:
            SmsManager = autoclass('android.telephony.SmsManager')
            sms_manager = SmsManager.getDefault()
            short_msg = f"INTRUDER! https://maps.google.com/?q={current_gps['lat']},{current_gps['lon']} Time:{datetime.datetime.now().strftime('%H:%M')}" if current_gps['lat'] else f"SmartGuard ALERT! Intruder! {location_text[:100]} Time:{datetime.datetime.now().strftime('%H:%M')}"
            sms_manager.sendTextMessage(number, None, short_msg, None, None)
            log_attempt(f"SMS SENT to {number}")
            return True
        else:
            log_attempt(f"SMS SIMULATED to {number}")
            return True
    except Exception as e:
        log_attempt(f"SMS FAILED: {e}")
        return False

def send_email_alert(photo_path, test_mode=False):
    cfg = load_config()
    email_cfg = cfg.get("email", {})
    if not email_cfg.get("enabled") and not test_mode: 
        if not test_mode: send_sms_alert(get_real_location_text())
        return False
    if not email_cfg.get("sender") or not email_cfg.get("receiver"): 
        send_sms_alert(get_real_location_text())
        return False
    app_pass = decrypt_simple(email_cfg.get("app_pass_enc",""))
    if not app_pass: 
        send_sms_alert(get_real_location_text())
        return False
    try:
        location_text = get_real_location_text()
        msg = MIMEMultipart()
        msg['From'] = email_cfg['sender']
        msg['To'] = email_cfg['receiver']
        msg['Subject'] = "SmartGuard Test GPS+SMS!" if test_mode else "SmartGuard - INTRUDER + GPS + PHOTO"
        body = f"""SMARTGUARD MOBILE v1.0
Time: {datetime.datetime.now()}
REAL LOCATION:
{location_text}
SMS Fallback: {'Enabled to ' + cfg.get('sms',{}).get('receiver_number','') if cfg.get('sms',{}).get('enabled') else 'Disabled'}
I AM - Possible Solutions Ltd
"""
        msg.attach(MIMEText(body, 'plain'))
        if photo_path and os.path.exists(photo_path):
            try:
                with open(photo_path, 'rb') as fb:
                    img = MIMEImage(fb.read())
                    msg.attach(img)
            except: pass
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=15)
        server.starttls()
        server.login(email_cfg['sender'], app_pass)
        server.send_message(msg)
        server.quit()
        log_attempt("EMAIL SENT")
        send_sms_alert(location_text)
        return True
    except Exception as e:
        log_attempt(f"EMAIL FAILED ({e}) - Trying SMS")
        send_sms_alert(get_real_location_text())
        return False

class LockScreen(Screen):
    status_text = StringProperty("Enter PIN")
    gps_text = StringProperty("GPS: Starting...")
    attempts = NumericProperty(0)
    def on_enter(self):
        Clock.schedule_interval(self.update_gps_label, 1)
        start_gps()
    def update_gps_label(self, dt):
        if current_gps['lat']: self.gps_text = f"GPS: OK {current_gps['lat']:.4f}, {current_gps['lon']:.4f}"
        else: self.gps_text = f"GPS: {current_gps['address'][:40]}"
    def check_pin(self):
        pin = self.ids.pin_input.text.strip()
        if not pin: return
        cfg = load_config()
        if hash_pin(pin) in [cfg['user_pin_hash'], cfg['master_pin_hash']]:
            log_attempt("ACCESS GRANTED")
            self.attempts = 0
            self.manager.current = "dashboard"
        else:
            self.attempts += 1
            log_attempt(f"FAILED {self.attempts}/{MAX_TRIES}")
            self.status_text = f"Wrong {self.attempts}/{MAX_TRIES} - Photo+GPS+SMS sent!"
            self.capture_intruder()
            self.ids.pin_input.text = ""
            if self.attempts >= MAX_TRIES: self.start_lockout()
    def capture_intruder(self):
        try:
            filename = os.path.join(PHOTO_DIR, f"intruder_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
            if IS_ANDROID: camera.take_picture(filename=filename, on_complete=lambda x: self.on_photo_taken(filename))
            else: open(filename, 'a').close(); self.on_photo_taken(filename)
        except: pass
    def on_photo_taken(self, path):
        if has_internet():
            threading.Thread(target=send_email_alert, args=(path, False), daemon=True).start()
        else:
            threading.Thread(target=send_sms_alert, args=(get_real_location_text(),), daemon=True).start()
            threading.Thread(target=send_email_alert, args=(path, False), daemon=True).start()
    def start_lockout(self):
        self.ids.unlock_btn.disabled = True
        remaining = LOCKOUT_TIME
        def countdown(dt):
            nonlocal remaining
            if remaining > 0:
                self.status_text = f"LOCKED {remaining}s"
                remaining -= 1
                return True
            else:
                self.attempts = 0
                self.status_text = "Ready"
                self.ids.unlock_btn.disabled = False
                return False
        Clock.schedule_interval(countdown, 1)

class DashboardScreen(Screen):
    email_status = StringProperty("Email: OFF | SMS: ON")
    gps_status = StringProperty("GPS: Starting...")
    def on_enter(self):
        self.refresh_logs(); self.load_fields()
        Clock.schedule_interval(self.update_gps_status, 1)
        start_gps()
    def update_gps_status(self, dt):
        self.gps_status = get_real_location_text()
        self.ids.gps_label.text = self.gps_status
    def refresh_logs(self):
        try:
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, "r") as f: self.ids.log_label.text = f.read()[-4000:]
            photos = glob.glob(os.path.join(PHOTO_DIR, "*.jpg"))
            self.ids.photo_count.text = f"Evidence: {len(photos)} | Internet: {'YES' if has_internet() else 'NO - SMS will be used'}"
        except: pass
    def load_fields(self):
        cfg = load_config()
        email_cfg = cfg.get("email", {}); sms_cfg = cfg.get("sms", {})
        self.ids.sender_input.text = email_cfg.get("sender","")
        self.ids.receiver_input.text = email_cfg.get("receiver","")
        self.ids.sms_number_input.text = sms_cfg.get("receiver_number","")
        if email_cfg.get("app_pass_enc"): self.ids.app_pass_input.text = "**** saved ****"
        self.email_status = f"Email: {'ON' if email_cfg.get('enabled') else 'OFF'} | SMS: {'ON' if sms_cfg.get('enabled') else 'OFF'}"
        self.ids.email_switch.active = email_cfg.get("enabled", False)
        self.ids.sms_switch.active = sms_cfg.get("enabled", True)
    def save_all(self):
        cfg = load_config()
        sender = self.ids.sender_input.text.strip()
        receiver = self.ids.receiver_input.text.strip()
        app_pass_raw = self.ids.app_pass_input.text.strip()
        sms_number = self.ids.sms_number_input.text.strip()
        if "****" in app_pass_raw: enc = cfg['email'].get("app_pass_enc","")
        else: enc = encrypt_simple(app_pass_raw) if app_pass_raw else cfg['email'].get("app_pass_enc","")
        cfg['email'] = {"sender": sender, "app_pass_enc": enc, "receiver": receiver, "enabled": self.ids.email_switch.active}
        cfg['sms'] = {"receiver_number": sms_number, "enabled": self.ids.sms_switch.active}
        save_config(cfg)
        self.ids.email_status_label.text = f"Saved! SMS to {sms_number}"
        self.email_status = f"Email: {'ON' if self.ids.email_switch.active else 'OFF'} | SMS: {'ON' if self.ids.sms_switch.active else 'OFF'}"
    def test_all(self):
        self.ids.email_status_label.text = "Testing Email + SMS..."
        def do_test():
            send_sms_alert(get_real_location_text())
            ok = send_email_alert(None, test_mode=True)
            def update(dt): self.ids.email_status_label.text = f"Test Done! SMS sent + Email {'OK' if ok else 'check but SMS works'}"
            Clock.schedule_once(update, 0)
        threading.Thread(target=do_test, daemon=True).start()

class SmartGuardApp(App):
    def build(self):
        Builder.load_file("smartguard.kv")
        sm = ScreenManager()
        sm.add_widget(LockScreen(name="lock"))
        sm.add_widget(DashboardScreen(name="dashboard"))
        return sm
    def on_start(self): start_gps()

SmartGuardApp().run()
