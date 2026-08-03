package com.clarium.hrms.security.crypto;

import org.springframework.stereotype.Component;

// Placeholder resolver: swap for a KMS/Vault-backed SecretResolver in production.
// The contract this bean fulfils - keys resolved at runtime, never hard-coded -
// stays the same regardless of which implementation is wired in.
@Component
public class EnvironmentSecretResolver implements SecretResolver {

    @Override
    public String resolveSecret(String secretName) {
        String envVarName = toEnvVarName(secretName);
        String value = System.getenv(envVarName);
        if (value == null || value.isBlank()) {
            throw new IllegalStateException(
                    "Secret '" + secretName + "' is not available; set the " + envVarName
                            + " environment variable via your secrets manager (KMS/Vault) integration");
        }
        return value;
    }

    private String toEnvVarName(String secretName) {
        return secretName.toUpperCase().replaceAll("[^A-Z0-9]", "_");
    }
}
