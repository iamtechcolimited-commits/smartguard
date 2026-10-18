[app]
title = SmartGuard
package.name = smartguard
package.domain = com.smartguard.app

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 0.1

requirements = python3,kivy
orientation = portrait
fullscreen = 0
android.permissions = INTERNET

android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.build_tools_version = 33.0.2
android.accept_sdk_license_agreement = True

[buildozer]
log_level = 2
