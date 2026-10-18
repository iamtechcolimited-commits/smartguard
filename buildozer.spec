[app]
title = SmartGuard
package.name = smartguard
package.domain = com.malawi.smartguard

source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.exclude_exts = spec

version = 1.0

requirements = python3,kivy==2.3.1,plyer,pillow,androidstorage4kivy

orientation = portrait

[buildozer]
log_level = 2

[app:android]
fullscreen = 0
android.permissions = INTERNET,SEND_SMS,RECEIVE_SMS,READ_SMS,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,ACCESS_BACKGROUND_LOCATION,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.accept_sdk_license_agreement = True
android.archs = arm64-v8a, armeabi-v7a
p4a.bootstrap = sdl2
