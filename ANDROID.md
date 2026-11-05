# Arthur's Arena on Android

`dist/arthurs-arena.apk` is the Legends game as an Android app, with a thumb joystick. It plays full screen and sideways, needs no internet, and remembers the **Best** score and the **Golden Crown**. It works on Android 7.0 or newer, on phones and tablets.

## Controls on a phone or tablet

During a fight the app shows game-pad controls, and you can use both thumbs at once. The joystick sits on the left and the buttons in a round cluster on the right, and the fight is drawn between them, so the controls never cover the fighters.

- **Joystick (left thumb):** put your thumb anywhere in the bottom-left corner and the stick appears under it. Push left or right to walk; push further to walk faster. **Flick it up to jump.**
- **Buttons (right thumb):** **PUNCH** (bottom), **KICK** (right), **JUMP** (top), **DODGE** (left). Tap for a quick hit. **Hold** PUNCH for a METEOR PUNCH or KICK for a SKY KICK, then let go. Tap KICK twice for a WHIRLWIND KICK (a HELICOPTER KICK in the air).
- **In BRAWL**, push the joystick **down** to drop through a thin platform. You can jump twice: once on the ground and once in the air.
- **POWER** (purple, left of DODGE): your power level's move. It says LOCKED until power level 2, and a ring fills while it recharges.
- **FIRE** (big red button, bottom left of the others): hold it to charge a fireball. The button fills up gold, and glows at full power. Let go to shoot.
- **SUPER** (above the buttons) glows gold when your super move is ready.
- Each button gives a tiny buzz when you press it.

Menus (STORY, ARCADE, picking a fighter, SKIP, RETRY, HOME, ✕) are still tapped on the game screen. On a computer, the game keeps its own buttons and the keyboard works too.

## Install it (do this on each phone or tablet)

1. On the phone or tablet, open this link in Chrome:
   `https://github.com/345-Mitch/arthurs-arena/raw/ccr-efe15747-5cfrbv/dist/arthurs-arena.apk`
   (Once this branch is merged, swap `ccr-efe15747-5cfrbv` for `main`.)
2. Chrome may say the file might be harmful. Tap **Download anyway**.
3. Open the download. Android asks to allow installs from Chrome: tap **Settings**, turn on **Allow from this source**, then go back.
4. Tap **Install**. If Play Protect says it doesn't know the developer, tap **More details**, then **Install anyway**. It says this because the app isn't from the Play Store.
5. Open **Arthur's Arena** from the home screen.

You can turn **Allow from this source** back off afterwards.

To update later, install the new APK the same way. It installs over the old one and keeps the Best score.

## Play in a browser instead

`dist/arthurs-arena.html` is the same game as one web page. Download it and open it in any browser, on a phone, tablet or computer. It works offline too.

## Good to know

- Scratch on its own only follows one finger, so the joystick and buttons are part of the app's page, not Scratch sprites. They set the same variables the Scratch buttons do (`Want Punch` and so on, plus `Joy X` for walking). `Touch Pad` = 1 tells the game to hide its own buttons.
- Version 3.0 (the round button cluster back, smaller) installs over earlier versions and keeps the Best score, difficulty, power level and sound setting.
- The Android back button closes the game.
- The app is signed with a debug key (`android/debug.keystore`, password `arthursarena`). That's fine for installing at home. The Play Store would need a private key.

## Rebuild it (for Mitch)

After changing the game (`python3 tools/build_legends_sb3.py`):

```bash
npm install --prefix /tmp/scratch-tools @turbowarp/packager@3.14.0
NODE_PATH=/tmp/scratch-tools/node_modules python3 tools/build_android.py
```

This writes `dist/arthurs-arena.html` and `dist/arthurs-arena.apk`. It needs Java (JDK 17 or newer) and Node, but not the Android SDK. The first run downloads the build tools from Maven Central: aapt2 (inside apktool), smali and apksig. Raise `VERSION_CODE` in `tools/build_android.py` for each new release.

How the app is made:

- `tools/package_html.js` turns the `.sb3` into one offline web page with the TurboWarp packager. It also adds a few lines that save Best and Crown on the device.
- `android/` holds the app: the manifest, the icon, and one screen (`MainActivity.smali`) that shows that page full screen.
