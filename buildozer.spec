[app]
title = Personal Optimizer
package.name = personaloptimizer
package.domain = org.gopimadhav
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

# Requirements: Added 'google-generativeai' and 'pillow' for your AI logic
requirements = python3,kivy,pillow,certifi,chardet,idna,requests,urllib3

orientation = portrait
fullscreen = 0

# Android specific
android.permissions = CAMERA, INTERNET, WRITE_EXTERNAL_STORAGE
android.api = 31
android.minapi = 21
android.sdk = 31
android.ndk = 25b
android.skip_update = False
android.accept_sdk_license = True

# We need this for the Gemini API to make secure HTTPS calls
android.meta_data = com.google.android.gms.vision.DEPENDENCIES=barcode

[buildozer]
log_level = 2
warn_on_root = 1
