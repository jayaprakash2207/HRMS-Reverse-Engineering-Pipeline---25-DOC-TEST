package com.clarium.hrms.security.crypto;

@FunctionalInterface
public interface SecretResolver {

    String resolveSecret(String secretName);
}
