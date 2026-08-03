package com.clarium.hrms.common.dto;

import java.util.List;

public record ApiError(String code, String message, List<ErrorDetail> details, String traceId) {
}
