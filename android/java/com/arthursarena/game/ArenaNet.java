package com.arthursarena.game;

import android.content.Context;
import android.net.nsd.NsdManager;
import android.net.nsd.NsdServiceInfo;
import android.net.wifi.WifiManager;
import android.util.Log;
import android.webkit.JavascriptInterface;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.Inet4Address;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.NetworkInterface;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Enumeration;
import java.util.LinkedList;
import java.util.List;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.LinkedBlockingQueue;

/**
 * Wi-Fi play for Arthur's Arena. The game page (JavaScript) calls these methods as window.ArenaNet.
 * One phone hosts (a TCP server, advertised on the local network with NSD / mDNS), the other finds it
 * and joins. After that both sides just send and receive lines of text; the game page does the rest.
 * Critical moments are logged under the tag ArenaNet (adb logcat -s ArenaNet).
 */
public class ArenaNet {
    static final String TYPE = "_arthursarena._tcp.";
    static final int PORT = 47123;
    static final String TAG = "ArenaNet";

    private final Context context;
    private final NsdManager nsd;
    private WifiManager.MulticastLock lock;

    private volatile String status = "idle";
    private volatile String error = "";
    private ServerSocket server;
    private Socket socket;
    private final ConcurrentLinkedQueue<String> inbox = new ConcurrentLinkedQueue<String>();
    private LinkedBlockingQueue<String> outbox = new LinkedBlockingQueue<String>();

    private NsdManager.RegistrationListener registration;
    private NsdManager.DiscoveryListener discovery;
    private final List<String[]> found = Collections.synchronizedList(new ArrayList<String[]>());
    private final LinkedList<NsdServiceInfo> toResolve = new LinkedList<NsdServiceInfo>();
    private boolean resolving = false;

    public ArenaNet(Context context) {
        this.context = context.getApplicationContext();
        this.nsd = (NsdManager) this.context.getSystemService(Context.NSD_SERVICE);
    }

    private static String quote(String s) {
        StringBuilder b = new StringBuilder("\"");
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c == '"' || c == '\\') b.append('\\');
            if (c < 32) { b.append(' '); continue; }
            b.append(c);
        }
        return b.append('"').toString();
    }

    private void multicast(boolean on) {
        try {
            if (on && lock == null) {
                WifiManager wifi = (WifiManager) context.getSystemService(Context.WIFI_SERVICE);
                lock = wifi.createMulticastLock("arthurs-arena");
                lock.setReferenceCounted(false);
                lock.acquire();
            } else if (!on && lock != null) {
                lock.release();
                lock = null;
            }
        } catch (Throwable t) { /* discovery may still work */ }
    }

    /** Everything the page needs in one JSON string. */
    @JavascriptInterface
    public String state() {
        StringBuilder b = new StringBuilder("{\"status\":").append(quote(status))
                .append(",\"error\":").append(quote(error)).append(",\"ip\":").append(quote(myIp())).append(",\"found\":[");
        synchronized (found) {
            for (int i = 0; i < found.size(); i++) {
                String[] f = found.get(i);
                if (i > 0) b.append(',');
                b.append("{\"name\":").append(quote(f[0])).append(",\"host\":").append(quote(f[1]))
                 .append(",\"port\":").append(f[2]).append('}');
            }
        }
        return b.append("]}").toString();
    }

    /** All lines received since the last call, separated by newlines. */
    @JavascriptInterface
    public String poll() {
        StringBuilder b = new StringBuilder();
        String line;
        while ((line = inbox.poll()) != null) {
            if (b.length() > 0) b.append('\n');
            b.append(line);
        }
        return b.toString();
    }

    @JavascriptInterface
    public void send(String line) {
        if (socket != null) outbox.offer(line);
    }

    @JavascriptInterface
    public String myIp() {
        try {
            for (Enumeration<NetworkInterface> e = NetworkInterface.getNetworkInterfaces(); e.hasMoreElements();) {
                NetworkInterface n = e.nextElement();
                if (!n.isUp() || n.isLoopback()) continue;
                for (Enumeration<InetAddress> a = n.getInetAddresses(); a.hasMoreElements();) {
                    InetAddress addr = a.nextElement();
                    if (addr instanceof Inet4Address && !addr.isLoopbackAddress()) return addr.getHostAddress();
                }
            }
        } catch (Throwable t) { /* no network */ }
        return "";
    }

    /** Wait for a friend to join. name is shown in the friend's list of games. */
    @JavascriptInterface
    public void host(final String name) {
        stop();
        status = "hosting";
        error = "";
        multicast(true);
        new Thread(new Runnable() {
            public void run() {
                try {
                    ServerSocket s = new ServerSocket();
                    s.setReuseAddress(true);
                    try {
                        s.bind(new InetSocketAddress(PORT));
                    } catch (Throwable t) {
                        s.bind(new InetSocketAddress(0));
                    }
                    server = s;
                    Log.i(TAG, "hosting '" + name + "' on port " + s.getLocalPort() + " at " + myIp());
                    advertise(name, s.getLocalPort());
                    Socket c = s.accept();
                    Log.i(TAG, "friend joined from " + c.getInetAddress());
                    connected(c);
                } catch (Throwable t) {
                    if (!"idle".equals(status)) {
                        status = "error";
                        error = String.valueOf(t.getMessage());
                        Log.w(TAG, "hosting failed: " + error);
                    }
                }
            }
        }).start();
    }

    private void advertise(String name, int port) {
        try {
            NsdServiceInfo info = new NsdServiceInfo();
            info.setServiceName(name);
            info.setServiceType(TYPE);
            info.setPort(port);
            registration = new NsdManager.RegistrationListener() {
                public void onRegistrationFailed(NsdServiceInfo i, int code) { Log.w(TAG, "could not advertise the game: " + code); }
                public void onUnregistrationFailed(NsdServiceInfo i, int code) { }
                public void onServiceRegistered(NsdServiceInfo i) { Log.i(TAG, "game advertised as " + i.getServiceName()); }
                public void onServiceUnregistered(NsdServiceInfo i) { }
            };
            nsd.registerService(info, NsdManager.PROTOCOL_DNS_SD, registration);
        } catch (Throwable t) { /* the friend can still type the address */ }
    }

    /** Look for games on this Wi-Fi. Results appear in state().found. */
    @JavascriptInterface
    public void find() {
        stopFinding();
        found.clear();
        multicast(true);
        try {
            discovery = new NsdManager.DiscoveryListener() {
                public void onStartDiscoveryFailed(String t, int code) { error = "search failed " + code; Log.w(TAG, error); }
                public void onStopDiscoveryFailed(String t, int code) { }
                public void onDiscoveryStarted(String t) { }
                public void onDiscoveryStopped(String t) { }
                public void onServiceFound(NsdServiceInfo info) {
                    Log.i(TAG, "found " + info.getServiceName());
                    synchronized (toResolve) { toResolve.add(info); }
                    resolveNext();
                }
                public void onServiceLost(NsdServiceInfo info) {
                    synchronized (found) {
                        for (int i = found.size() - 1; i >= 0; i--) {
                            if (found.get(i)[0].equals(info.getServiceName())) found.remove(i);
                        }
                    }
                }
            };
            nsd.discoverServices(TYPE, NsdManager.PROTOCOL_DNS_SD, discovery);
        } catch (Throwable t) { error = "search failed"; }
    }

    private void resolveNext() {
        NsdServiceInfo next;
        synchronized (toResolve) {
            if (resolving || toResolve.isEmpty()) return;
            resolving = true;
            next = toResolve.removeFirst();
        }
        try {
            nsd.resolveService(next, new NsdManager.ResolveListener() {
                public void onResolveFailed(NsdServiceInfo i, int code) { Log.w(TAG, "could not resolve " + i.getServiceName() + ": " + code); done(); }
                public void onServiceResolved(NsdServiceInfo i) {
                    InetAddress h = i.getHost();
                    if (h != null) {
                        String[] row = {i.getServiceName(), h.getHostAddress(), String.valueOf(i.getPort())};
                        Log.i(TAG, "resolved " + row[0] + " at " + row[1] + ":" + row[2]);
                        synchronized (found) {
                            for (int k = found.size() - 1; k >= 0; k--) {
                                if (found.get(k)[0].equals(row[0])) found.remove(k);
                            }
                            found.add(row);
                        }
                    }
                    done();
                }
                void done() {
                    synchronized (toResolve) { resolving = false; }
                    resolveNext();
                }
            });
        } catch (Throwable t) {
            synchronized (toResolve) { resolving = false; }
        }
    }

    private void stopFinding() {
        if (discovery != null) {
            try { nsd.stopServiceDiscovery(discovery); } catch (Throwable t) { }
            discovery = null;
        }
    }

    /** Join a friend's game (from state().found, or an address typed in). */
    @JavascriptInterface
    public void join(final String host, final int port) {
        stopFinding();
        status = "joining";
        error = "";
        Log.i(TAG, "joining " + host + ":" + (port > 0 ? port : PORT));
        new Thread(new Runnable() {
            public void run() {
                try {
                    Socket c = new Socket();
                    c.connect(new InetSocketAddress(host, port > 0 ? port : PORT), 6000);
                    connected(c);
                } catch (Throwable t) {
                    status = "error";
                    error = "could not join " + host;
                    Log.w(TAG, error + ": " + t.getMessage());
                }
            }
        }).start();
    }

    private void connected(final Socket c) throws Exception {
        c.setTcpNoDelay(true);
        socket = c;
        Log.i(TAG, "connected to " + c.getInetAddress());
        outbox = new LinkedBlockingQueue<String>();
        status = "connected";
        final LinkedBlockingQueue<String> out = outbox;
        new Thread(new Runnable() {
            public void run() {
                try {
                    OutputStream os = c.getOutputStream();
                    while (socket == c) {
                        String line = out.take();
                        os.write((line + "\n").getBytes("UTF-8"));
                        os.flush();
                    }
                } catch (Throwable t) { lost(c); }
            }
        }).start();
        new Thread(new Runnable() {
            public void run() {
                try {
                    BufferedReader r = new BufferedReader(new InputStreamReader(c.getInputStream(), "UTF-8"), 65536);
                    String line;
                    while ((line = r.readLine()) != null) inbox.add(line);
                } catch (Throwable t) { /* closed */ }
                lost(c);
            }
        }).start();
    }

    private void lost(Socket c) {
        if (socket == c) {
            socket = null;
            status = "lost";
            Log.w(TAG, "connection lost");
            try { c.close(); } catch (Throwable t) { }
        }
    }

    /** Hang up and stop hosting or searching. */
    @JavascriptInterface
    public void stop() {
        if (!"idle".equals(status)) Log.i(TAG, "stop (was " + status + ")");
        status = "idle";
        stopFinding();
        if (registration != null) {
            try { nsd.unregisterService(registration); } catch (Throwable t) { }
            registration = null;
        }
        try { if (server != null) server.close(); } catch (Throwable t) { }
        server = null;
        Socket c = socket;
        socket = null;
        try { if (c != null) c.close(); } catch (Throwable t) { }
        outbox.offer("");
        inbox.clear();
        multicast(false);
    }
}
