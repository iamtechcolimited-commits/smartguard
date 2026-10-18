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

[buildozer]
log_level = 2

# (important) no need for ndk api stuff now, buildozer will handle it

[app:android]
android.accept_sdk_license_agreement = True
