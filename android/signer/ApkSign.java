// Signs an APK with the v2 scheme (Android 7+) using apksig, then checks it.
// (apksig 2.3.0's v1 signer does not run on new Java, and Android 7+ does not need v1.)
// Used by tools/build_android.py.
//   java -cp apksig.jar:. ApkSign in.apk out.apk keystore.p12 password alias
import com.android.apksig.ApkSigner;
import com.android.apksig.ApkVerifier;
import java.io.File;
import java.io.FileInputStream;
import java.security.KeyStore;
import java.security.PrivateKey;
import java.security.cert.X509Certificate;
import java.util.Collections;

public class ApkSign {
    public static void main(String[] a) throws Exception {
        File in = new File(a[0]), out = new File(a[1]);
        char[] pass = a[3].toCharArray();
        KeyStore ks = KeyStore.getInstance("PKCS12");
        try (FileInputStream f = new FileInputStream(a[2])) { ks.load(f, pass); }
        PrivateKey key = (PrivateKey) ks.getKey(a[4], pass);
        X509Certificate cert = (X509Certificate) ks.getCertificate(a[4]);
        ApkSigner.SignerConfig signer = new ApkSigner.SignerConfig.Builder(
                "ARENA", key, Collections.singletonList(cert)).build();
        new ApkSigner.Builder(Collections.singletonList(signer))
                .setInputApk(in).setOutputApk(out)
                .setV1SigningEnabled(false).setV2SigningEnabled(true)
                .setMinSdkVersion(24)
                .build().sign();
        ApkVerifier.Result r = new ApkVerifier.Builder(out).setMinCheckedPlatformVersion(24).build().verify();
        if (!r.isVerified()) {
            System.err.println("signature check FAILED: " + r.getErrors());
            System.exit(1);
        }
        System.out.println("signed and verified (v2 " + r.isVerifiedUsingV2Scheme() + ")");
    }
}
