package android.net.wifi;
public class WifiManager {
    public class MulticastLock {
        public void acquire() { }
        public void release() { }
        public void setReferenceCounted(boolean b) { }
    }
    public MulticastLock createMulticastLock(String tag) { return null; }
}
