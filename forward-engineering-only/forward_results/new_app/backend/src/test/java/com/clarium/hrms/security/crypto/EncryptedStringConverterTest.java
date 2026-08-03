package com.clarium.hrms.security.crypto;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.Base64;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

/**
 * Exercises the AES-256-GCM capability described in the README as "not yet
 * attached to any entity" - it is unit tested standalone against a stub
 * {@link SecretResolver} rather than through JPA, since no entity applies
 * {@code @Convert} to it yet.
 */
class EncryptedStringConverterTest {

    private static final String TEST_KEY_SECRET_NAME = "test/pii-encryption-key";
    private static final String TEST_KEY_BASE64 = Base64.getEncoder().encodeToString(new byte[32]);

    private EncryptedStringConverter converter;

    @BeforeEach
    void setUp() {
        SecretResolver stubResolver = name -> {
            assertThat(name).isEqualTo(TEST_KEY_SECRET_NAME);
            return Optional.of(TEST_KEY_BASE64);
        };
        EncryptionProperties properties = new EncryptionProperties();
        properties.setKeySecretName(TEST_KEY_SECRET_NAME);
        EncryptionKeyProvider keyProvider = new EncryptionKeyProvider(stubResolver, properties);
        converter = new EncryptedStringConverter(keyProvider);
    }

    @Test
    void encryptsAndDecryptsRoundTrip() {
        String plaintext = "123-45-6789";

        String ciphertext = converter.convertToDatabaseColumn(plaintext);
        String decrypted = converter.convertToEntityAttribute(ciphertext);

        assertThat(ciphertext).isNotEqualTo(plaintext);
        assertThat(decrypted).isEqualTo(plaintext);
    }

    @Test
    void nullAttributePassesThroughAsNullWithoutInvokingCrypto() {
        assertThat(converter.convertToDatabaseColumn(null)).isNull();
        assertThat(converter.convertToEntityAttribute(null)).isNull();
    }

    @Test
    void emptyStringRoundTrips() {
        String ciphertext = converter.convertToDatabaseColumn("");
        assertThat(converter.convertToEntityAttribute(ciphertext)).isEqualTo("");
    }

    @Test
    void encryptingTheSamePlaintextTwiceProducesDifferentCiphertext() {
        String plaintext = "same-value";

        String first = converter.convertToDatabaseColumn(plaintext);
        String second = converter.convertToDatabaseColumn(plaintext);

        assertThat(first).isNotEqualTo(second);
        assertThat(converter.convertToEntityAttribute(first)).isEqualTo(plaintext);
        assertThat(converter.convertToEntityAttribute(second)).isEqualTo(plaintext);
    }

    @Test
    void tamperedCiphertextFailsAuthenticatedDecryption() {
        String ciphertext = converter.convertToDatabaseColumn("123-45-6789");
        byte[] raw = Base64.getDecoder().decode(ciphertext);
        raw[raw.length - 1] ^= 0x01; // flip the last byte inside the GCM auth tag / ciphertext
        String tampered = Base64.getEncoder().encodeToString(raw);

        assertThatThrownBy(() -> converter.convertToEntityAttribute(tampered))
                .isInstanceOf(RuntimeException.class);
    }

    @Test
    void keyIsResolvedThroughTheConfiguredSecretNameNotHardCoded() {
        // Regression guard for the exact defect this capability exists to close:
        // BRD §4 flags a hard-coded SSN encryption key as a business-critical gap.
        SecretResolver resolverAssertingLookupHappened = name -> Optional.of(TEST_KEY_BASE64);
        EncryptionProperties properties = new EncryptionProperties();
        properties.setKeySecretName("some/other-key-name");
        EncryptionKeyProvider keyProvider = new EncryptionKeyProvider(resolverAssertingLookupHappened, properties);
        EncryptedStringConverter otherConverter = new EncryptedStringConverter(keyProvider);

        String ciphertext = otherConverter.convertToDatabaseColumn("value");

        assertThat(otherConverter.convertToEntityAttribute(ciphertext)).isEqualTo("value");
    }

    @Test
    void missingSecretFailsFastRatherThanFallingBackToADefaultKey() {
        SecretResolver missingResolver = name -> Optional.empty();
        EncryptionProperties properties = new EncryptionProperties();
        properties.setKeySecretName(TEST_KEY_SECRET_NAME);
        EncryptionKeyProvider keyProvider = new EncryptionKeyProvider(missingResolver, properties);
        EncryptedStringConverter converterWithMissingKey = new EncryptedStringConverter(keyProvider);

        assertThatThrownBy(() -> converterWithMissingKey.convertToDatabaseColumn("value"))
                .isInstanceOf(IllegalStateException.class);
    }
}
