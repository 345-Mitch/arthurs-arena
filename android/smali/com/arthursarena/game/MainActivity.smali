# Arthur's Arena: the whole Android app is this one screen.
#
# It is written in smali (Android's assembly language) so the APK can be
# built without the Android SDK. Same as this Java:
#
#   public class MainActivity extends Activity {
#       private WebView web;
#       protected void onCreate(Bundle b) {
#           super.onCreate(b);
#           getWindow().addFlags(FLAG_KEEP_SCREEN_ON);
#           web = new WebView(this);
#           WebSettings s = web.getSettings();
#           s.setJavaScriptEnabled(true);
#           s.setDomStorageEnabled(true);          // keeps Best and Crown
#           s.setMediaPlaybackRequiresUserGesture(false);
#           web.setBackgroundColor(Color.BLACK);
#           setContentView(web);
#           web.loadUrl("file:///android_asset/index.html");
#           hideBars();
#       }
#       public void onWindowFocusChanged(boolean f) { super...; if (f) hideBars(); }
#       protected void onPause()  { super.onPause();  web.onPause();  }
#       protected void onResume() { super.onResume(); web.onResume(); hideBars(); }
#       protected void onDestroy() { web.destroy(); net.stop(); super.onDestroy(); }
#       private void hideBars() {    // immersive full screen
#           getWindow().getDecorView().setSystemUiVisibility(0x1706);
#       }
#   }

.class public Lcom/arthursarena/game/MainActivity;
.super Landroid/app/Activity;

.field private web:Landroid/webkit/WebView;

# Wi-Fi play with a friend (classes2.dex, from android/java/.../ArenaNet.java)
.field private net:Lcom/arthursarena/game/ArenaNet;

.method public constructor <init>()V
    .registers 1
    invoke-direct {p0}, Landroid/app/Activity;-><init>()V
    return-void
.end method

.method protected onCreate(Landroid/os/Bundle;)V
    .registers 6
    invoke-super {p0, p1}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V

    invoke-virtual {p0}, Lcom/arthursarena/game/MainActivity;->getWindow()Landroid/view/Window;
    move-result-object v0
    const/16 v1, 0x80
    invoke-virtual {v0, v1}, Landroid/view/Window;->addFlags(I)V

    new-instance v0, Landroid/webkit/WebView;
    invoke-direct {v0, p0}, Landroid/webkit/WebView;-><init>(Landroid/content/Context;)V
    iput-object v0, p0, Lcom/arthursarena/game/MainActivity;->web:Landroid/webkit/WebView;

    invoke-virtual {v0}, Landroid/webkit/WebView;->getSettings()Landroid/webkit/WebSettings;
    move-result-object v1
    const/4 v2, 0x1
    invoke-virtual {v1, v2}, Landroid/webkit/WebSettings;->setJavaScriptEnabled(Z)V
    invoke-virtual {v1, v2}, Landroid/webkit/WebSettings;->setDomStorageEnabled(Z)V
    const/4 v3, 0x0
    invoke-virtual {v1, v3}, Landroid/webkit/WebSettings;->setMediaPlaybackRequiresUserGesture(Z)V

    const/high16 v3, -0x1000000
    invoke-virtual {v0, v3}, Landroid/webkit/WebView;->setBackgroundColor(I)V

    # the game page can call window.ArenaNet to host or join a Wi-Fi game
    new-instance v1, Lcom/arthursarena/game/ArenaNet;
    invoke-direct {v1, p0}, Lcom/arthursarena/game/ArenaNet;-><init>(Landroid/content/Context;)V
    iput-object v1, p0, Lcom/arthursarena/game/MainActivity;->net:Lcom/arthursarena/game/ArenaNet;
    const-string v2, "ArenaNet"
    invoke-virtual {v0, v1, v2}, Landroid/webkit/WebView;->addJavascriptInterface(Ljava/lang/Object;Ljava/lang/String;)V

    invoke-virtual {p0, v0}, Lcom/arthursarena/game/MainActivity;->setContentView(Landroid/view/View;)V

    const-string v1, "file:///android_asset/index.html"
    invoke-virtual {v0, v1}, Landroid/webkit/WebView;->loadUrl(Ljava/lang/String;)V

    invoke-direct {p0}, Lcom/arthursarena/game/MainActivity;->hideBars()V
    return-void
.end method

.method public onWindowFocusChanged(Z)V
    .registers 2
    invoke-super {p0, p1}, Landroid/app/Activity;->onWindowFocusChanged(Z)V
    if-eqz p1, :done
    invoke-direct {p0}, Lcom/arthursarena/game/MainActivity;->hideBars()V
    :done
    return-void
.end method

.method protected onPause()V
    .registers 2
    invoke-super {p0}, Landroid/app/Activity;->onPause()V
    iget-object v0, p0, Lcom/arthursarena/game/MainActivity;->web:Landroid/webkit/WebView;
    if-eqz v0, :done
    invoke-virtual {v0}, Landroid/webkit/WebView;->onPause()V
    :done
    return-void
.end method

.method protected onResume()V
    .registers 2
    invoke-super {p0}, Landroid/app/Activity;->onResume()V
    iget-object v0, p0, Lcom/arthursarena/game/MainActivity;->web:Landroid/webkit/WebView;
    if-eqz v0, :done
    invoke-virtual {v0}, Landroid/webkit/WebView;->onResume()V
    :done
    invoke-direct {p0}, Lcom/arthursarena/game/MainActivity;->hideBars()V
    return-void
.end method

.method protected onDestroy()V
    .registers 2
    iget-object v0, p0, Lcom/arthursarena/game/MainActivity;->web:Landroid/webkit/WebView;
    if-eqz v0, :done
    invoke-virtual {v0}, Landroid/webkit/WebView;->destroy()V
    :done
    iget-object v0, p0, Lcom/arthursarena/game/MainActivity;->net:Lcom/arthursarena/game/ArenaNet;
    if-eqz v0, :nonet
    invoke-virtual {v0}, Lcom/arthursarena/game/ArenaNet;->stop()V
    :nonet
    invoke-super {p0}, Landroid/app/Activity;->onDestroy()V
    return-void
.end method

.method private hideBars()V
    .registers 3
    invoke-virtual {p0}, Lcom/arthursarena/game/MainActivity;->getWindow()Landroid/view/Window;
    move-result-object v0
    invoke-virtual {v0}, Landroid/view/Window;->getDecorView()Landroid/view/View;
    move-result-object v0
    const/16 v1, 0x1706
    invoke-virtual {v0, v1}, Landroid/view/View;->setSystemUiVisibility(I)V
    return-void
.end method
