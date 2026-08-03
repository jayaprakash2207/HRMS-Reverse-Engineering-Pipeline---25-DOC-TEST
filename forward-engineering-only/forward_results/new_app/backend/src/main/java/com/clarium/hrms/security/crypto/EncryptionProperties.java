package com.clarium.hrms.security.crypto;

import jakarta.validation.constraints.NotBlank;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.validation.annotation.Validated;

@Validated
@ConfigurationProperties(prefix = "app.security.encryption")
public record EncryptionProperties(@NotBlank String keySecretName) {
}
