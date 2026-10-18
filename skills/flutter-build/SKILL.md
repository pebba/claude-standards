---
name: flutter-build
description: Build a Flutter Android app as a release APK and AAB, locally or in CI. Covers signing with an upload keystore via key.properties, version and build number from pubspec.yaml, stable artifact names, and fixing build/signing/install problems.
when_to_use: Use when the user wants to build an APK or app bundle (AAB), set up Android release signing, asks why an APK won't install over the old one, or mentions "flutter build", "APK bauen", "AAB", "Play Store Upload", "keystore", "signieren".
---

# Flutter build (APK + AAB)

CI builds and publishes releases automatically (`release-flutter.yml` via the repo's `release` workflow). This skill covers local builds and the signing setup that CI relies on.

## Version

- `pubspec.yaml` `version: X.Y.Z+N` is owned by the release workflow: `X.Y.Z` is SemVer and `N` the build number (Android `versionCode`), increased on every release. Don't edit it by hand.
- The build number never appears in release titles or tags.

## Local release build

```bash
flutter pub get
flutter analyze && flutter test
flutter build apk --release        # build/app/outputs/flutter-apk/app-release.apk
flutter build appbundle --release  # build/app/outputs/bundle/release/app-release.aab
```

- The APK is for sideloading. Its stable release asset name is `<app>.apk`, so `releases/latest/download/<app>.apk` always points to the newest build.
- The AAB is for Play Console upload, released as `<app>.aab`.
- Check the result with `unzip -p <apk> META-INF/*.RSA | keytool -printcert | head`. It should show the upload certificate, not "Android Debug".

## Signing (one-time per app)

`android/key.properties` (gitignored; CI writes it from secrets):

```properties
storeFile=app/upload-keystore.jks
storePassword=…
keyAlias=upload
keyPassword=…
```

`android/app/build.gradle.kts`:

```kotlin
import java.util.Properties

val keystoreProperties = Properties().apply {
    val file = rootProject.file("key.properties")
    if (file.exists()) file.inputStream().use { load(it) }
}
val hasReleaseKeystore = keystoreProperties.getProperty("storeFile") != null

android {
    signingConfigs {
        if (hasReleaseKeystore) {
            create("release") {
                storeFile = rootProject.file(keystoreProperties.getProperty("storeFile"))
                storePassword = keystoreProperties.getProperty("storePassword")
                keyAlias = keystoreProperties.getProperty("keyAlias")
                keyPassword = keystoreProperties.getProperty("keyPassword")
            }
        }
    }
    buildTypes {
        release {
            signingConfig = signingConfigs.getByName(if (hasReleaseKeystore) "release" else "debug")
        }
    }
}
```

- Create the keystore once with `keytool -genkey -v -keystore upload-keystore.jks -keyalg RSA -keysize 2048 -validity 10000 -alias upload`. Keep it and its passwords outside the repo, in a password manager. Losing it means users can't update the app anymore.
- CI secrets: `ANDROID_KEYSTORE_BASE64` (`base64 -w0 upload-keystore.jks`), `ANDROID_KEYSTORE_PASSWORD`, `ANDROID_KEY_ALIAS`, `ANDROID_KEY_PASSWORD`. Set them with `gh secret set`.

## Troubleshooting

- **"App not installed" / package conflicts:** the new APK is signed with a different key, usually a debug key from a fresh CI runner. Set the signing secrets. Uninstalling first deletes local app data, so warn the user.
- **Java version errors:** CI uses Java 17 (input `java-version`). Locally, check `flutter doctor -v`.
- **`flutter analyze` fails in CI but not locally:** CI uses `--fatal-infos` in PR checks. Run the same command locally.
- **Formatting check fails:** run `dart format .` and commit the result.
