package android.util;
/** Compile-time stand-in for android.util.Log (the real one is in Android). */
public final class Log {
    public static int i(String tag, String msg) { System.out.println(tag + ": " + msg); return 0; }
    public static int w(String tag, String msg) { System.out.println(tag + " (warning): " + msg); return 0; }
}
