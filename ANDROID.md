# Arthur's Arena on Android

`dist/arthurs-arena.apk` is the Legends game as an Android app, with a thumb joystick. It plays full screen and sideways, needs no internet, and remembers the **Best** score and the **Golden Crown**. It works on Android 7.0 or newer, on phones and tablets.

## Controls on a phone or tablet

During a fight the app shows game-pad controls, and you can use both thumbs at once. The joystick sits on the left and the buttons in a round cluster on the right. The fight is drawn wide between them, with the lower half of the controls over the bottom of the screen (mostly the floor).

- **Joystick (left thumb):** put your thumb anywhere in the bottom-left corner and the stick appears under it. Push left or right to walk; push further to walk faster. **Flick it up to jump.**
- **Buttons (right thumb):** **PUNCH** (bottom), **KICK** (right), **JUMP** (top), **DODGE** (left). Tap for a quick hit. **Hold** PUNCH for a METEOR PUNCH or KICK for a SKY KICK, then let go. Tap KICK twice for a WHIRLWIND KICK (a HELICOPTER KICK in the air).
- **In BRAWL**, push the joystick **down** to drop through a thin platform. You can jump twice: once on the ground and once in the air.
- **POWER** (purple, left of DODGE): your power level's move. It says LOCKED until power level 2, and a ring fills while it recharges.
- **FIRE** (big red button, bottom left of the others): hold it to charge a fireball. The button fills up gold, and glows at full power. Let go to shoot.
- **SUPER** (above the buttons) glows gold when your super move is ready.
- Each button gives a tiny buzz when you press it.

The space round the game is filled with the stage's own scenery (mirrored outward from the edges, a little darker), so there are no black bars. Screens with words on them, like the title, just stretch their edges instead.

During a fight the names, health bars, SUPER bar and score sit in a bar across the very top of the screen, from edge to edge, with the ✕ in the middle; in BRAWL the four fighters' damage % and lives are there. The game is drawn just below, so nothing covers the fight.

Menus (STORY, ARCADE, picking a fighter, SKIP, RETRY, HOME, ✕) are still tapped on the game screen. On a computer, the game keeps its own buttons and the keyboard works too.

## Play a friend over Wi-Fi

Two phones or tablets with the app can play one BRAWL together: you are fighter 1, your friend is fighter 2, and two computer fighters join in.

1. Both phones on the **same Wi-Fi**. No Wi-Fi? Turn on one phone's **hotspot** and join it with the other. No internet is used.
2. On both phones: **BRAWL**, then the fighter screen shows **📶 PLAY A FRIEND** (top left). Tap it.
3. One phone taps **HOST A GAME**. The other taps **JOIN A GAME** and then the game that appears (for example *ARENA 42*). If it doesn't appear, type the number shown on the host's screen (like `192.168.1.5`) and tap JOIN.
4. Each phone picks a fighter. The host can also pick the STAGE. The match starts as soon as both have picked.
   It's friend against friend (with two computer fighters causing trouble): as soon as one of you is out of lives, the other wins.
5. After the match tap **REMATCH** on both phones to go again, or **LEAVE**. The ✕ at the top also leaves (your friend is told).

How it works: both phones run exactly the same match at the same time ("lockstep"). Each frame they swap only the buttons pressed, and they use the same random numbers, so the match is the same on both screens. Your buttons count about a tenth of a second after you press them, so they have time to reach the other phone. Both phones must have the **same version** of the game; the app checks. Bluetooth isn't used: the game runs in a web view, which can't use Bluetooth, but a phone's hotspot works the same way without a router.

Things to know:

- Your own progress (Best, power level, the Golden Crown) is kept. A Wi-Fi match is played with the host's power level and difficulty, and a win gives you power XP as usual.
- If the phones ever get out of step (rare), the match stops with a message; tap PLAY A FRIEND to go again.
- Only BRAWL can be played over Wi-Fi.

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
- Version 3.5 (play a friend over Wi-Fi) installs over earlier versions and keeps the Best score, difficulty, power level and sound setting.
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
- `android/java/.../ArenaNet.java` is the Wi-Fi helper the page calls as `window.ArenaNet`: it hosts a game (a TCP server on port 47123, advertised on the local network with Android's network service discovery), finds games, joins one, and passes lines of text both ways. It is compiled with `javac` against small stand-ins for the few Android classes it uses (`android/stubs`), then `dx` turns it into `classes2.dex`. The app now asks for network permissions (Wi-Fi state, multicast for finding games, and internet for the local connection).
- The lockstep engine is in `tools/package_html.js` (`NET_JS`). The host sends a seed and a copy of its game; both phones then drive the game themselves, frame by frame, with a frame clock instead of the real clock, seeded `pick random`, and one pass of the scripts per frame. Every second they compare a checksum of the fighters.
- `tools/test_wifi.js` plays a Wi-Fi BRAWL between two copies of the page in a browser, with a stand-in for `ArenaNet`, and checks they stay in step (`WIFI_FULL=1` plays a whole match and a rematch).
