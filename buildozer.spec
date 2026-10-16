[app]
title = Smart Guard Mobile
package.name = smartguard
package.domain = com.possiblesolutions.smartguard
source.dir = .
source.include_exts = py,kv,json
version = 1.0
requirements = python3,kivy==2.3.0,plyer,androidstorage4kivy,pyjnius
orientation = portrait
[app:android]
android.permissions = CAMERA,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,VIBRATE,SEND_SMS,RECEIVE_SMS,ACCESS_BACKGROUND_LOCATION
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license_agreement = True
[buildozer]
log_level = 2
warn_on_root = 1
