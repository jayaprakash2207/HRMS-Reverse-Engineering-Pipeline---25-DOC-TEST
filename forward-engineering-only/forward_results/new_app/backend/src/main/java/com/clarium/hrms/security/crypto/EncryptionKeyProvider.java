package com.clarium.hrms.security.crypto;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;
import java.util.Base64;

@Component
@RequiredArgsConstructor
public class EncryptionKeyProvider {

    private static final String KEY_ALGORITHM = "AES";

    private final SecretResolver secretResolver;
    private final EncryptionProperties encryptionProperties;

    private volatile SecretKey cachedKey;

    public SecretKey getPiiEncryptionKey() {
        SecretKey key = cachedKey;
        if (key == null) {
            synchronized (this) {
                key = cachedKey;
                if (key == null) {
                    key = resolveKey();
                    cachedKey = key;
                }
            }
        }
        return key;
    }

    private SecretKey resolveKey() {
        String base64Key = secretResolver.resolveSecret(encryptionProperties.keySecretName());
        byte[] decoded = Base64.getDecoder().decode(base64Key);
        return new SecretKeySpec(decoded, KEY_ALGORITHM);
    }
}
