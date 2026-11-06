package android.content;
public abstract class Context {
    public static final String NSD_SERVICE = "servicediscovery";
    public static final String WIFI_SERVICE = "wifi";
    public abstract Object getSystemService(String name);
    public abstract Context getApplicationContext();
}
