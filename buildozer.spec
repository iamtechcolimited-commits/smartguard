[app]
title = Smart Guard
package.name = smartguard
package.domain = com.smartguard.app
source.dir = .
source.include_exts = py,kv,json
version = 1.0
requirements = python3,kivy,plyer,pyjnius
orientation = portrait
fullscreen = 0

[app:android]
android.permissions = CAMERA,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,INTERNET,VIBRATE,SEND_SMS,RECEIVE_SMS
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license_agreement = True

[buildozer]
log_level = 2
warn_on_root = 1
