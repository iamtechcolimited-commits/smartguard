[app]
title = SmartGuard
package.name = smartguard
package.domain = com.malawi.smartguard

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
source.exclude_exts = spec,md

version = 1.0
version.regex = __version__ = ['"]([^'"]+)['"]
version.filename = %(source.dir)s/main.py

requirements = python3,kivy==2.3.1,plyer,Pillow,androidstorage4kivy,android

orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

[app:android]
fullscreen = 0
p4a.bootstrap = sdl2
p4a.branch = master
android.branch = master

android.permissions = INTERNET,SEND_SMS,RECEIVE_SMS,READ_SMS,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,ACCESS_BACKGROUND_LOCATION,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.accept_sdk_license_agreement = True

android.archs = arm64-v8a
android.ant = auto

android.allow_backup = True

# uncomment to add app icon and presplash
#android.icon = icon.png
#android.presplash = presplash.png

[app:android:arm64-v8a]
# extra options for this arch if needed

[app:android:armeabi-v7a]
# extra options for this arch if needed
