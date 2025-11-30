
ERRORS = {
        # 🌍 General / HTTP Errors (10xx)
        "INVALID_REQUEST": {"code": 1001, "message": "Invalid request payload", "reason": "Malformed or missing parameters"},
        "UNAUTHORIZED": {"code": 1002, "message": "Unauthorized access", "reason": "User is not authenticated or token is invalid"},
        "FORBIDDEN": {"code": 1003, "message": "Permission denied", "reason": "User lacks required permissions"},
        "NOT_FOUND": {"code": 1004, "message": "Requested resource not found", "reason": "The requested entity does not exist"},
        "METHOD_NOT_ALLOWED": {"code": 1005, "message": "HTTP method not allowed", "reason": "Attempted to use an unsupported HTTP method"},
        "TIMEOUT": {"code": 1006, "message": "Request timed out", "reason": "The operation took too long to complete"},
        "CONFLICT": {"code": 1007, "message": "Resource conflict", "reason": "A conflicting resource already exists"},
        "UNPROCESSABLE": {"code": 1008, "message": "Unprocessable entity", "reason": "Server unable to process contained instructions"},
        "TOO_MANY_REQUESTS": {"code": 1009, "message": "Too many requests", "reason": "Rate limit exceeded"},
        "VALIDATION_ERROR": {"code": 1010, "message": "Validation failed", "reason": "One or more input fields failed validation"},
        "INTERNAL_ERROR": {"code": 1014, "message": "Internal server error", "reason": "Unexpected internal failure occurred"},
        "UNKNOWN_ERROR": {"code": 1015, "message": "Unknown error occurred", "reason": "An unspecified error occurred"},
        "NOT_IMPLEMENTED": {"code": 1016, "message": "Not implemented", "reason": "Feature or endpoint not implemented"},
        "INVALID_TOKEN": {"code": 1017, "message": "Invalid or expired token", "reason": "Token expired or signature invalid"},
        "DUPLICATE_ENTRY": {"code": 1018, "message": "Duplicate entry not allowed", "reason": "A similar record already exists"},
        "PAYMENT_FAILED": {"code": 1019, "message": "Payment failed", "reason": "Payment gateway declined or error processing payment"},
        "PAYMENT_DECLINED": {"code": 1020, "message": "Payment declined", "reason": "Payment authorization was denied"},


        # 🔐 Auth / Login / Signup (12xx)
        "AUTH_INVALID_CREDENTIALS": {"code": 1201, "message": "Invalid username or password", "reason": "The provided credentials do not match any registered account"},
        "AUTH_SIGNIN_FAILED": {"code": 1202, "message": "Invalid login credentials", "reason": "Incorrect credentials or service error"},
        "AUTH_SIGNUP_FAILED": {"code": 1203, "message": "Failed to create account", "reason": "Database or validation error"},
        "AUTH_LOGOUT_FAILED": {"code": 1204, "message": "Failed to log out", "reason": "Token invalidation failed"},
        "AUTH_OTP_INVALID": {"code": 1205, "message": "Invalid or expired OTP", "reason": "OTP is incorrect, expired, or has been used"},
        "AUTH_OTP_SEND_FAILED": {"code": 1206, "message": "Failed to send OTP", "reason": "Messaging or email service failure"},
        "AUTH_OTP_VERIFY_FAILED": {"code": 1207, "message": "Failed to verify OTP", "reason": "Incorrect or expired OTP"},
        "AUTH_CHANNEL_UNSUPPORTED": {"code": 1208, "message": "Unsupported authentication channel", "reason": "The requested authentication channel is not available or supported"},
        "AUTH_PASSWORD_UPDATE_FAILED": {"code": 1209, "message": "Failed to update password", "reason": "Database update failed"},
        "AUTH_PASSWORD_INVALID_OLD": {"code": 1210, "message": "Old password is incorrect", "reason": "The provided current password does not match the account password"},
        "AUTH_FORGOT_PASSWORD_FAILED": {"code": 1211, "message": "Failed to reset password", "reason": "Invalid token or email"},
        "AUTH_INVALID_PAYLOAD": {"code": 1212, "message": "Invalid payload", "reason": "Request payload is missing required fields or contains invalid data"},
        "AUTH_PROCESSING_ERROR": {"code": 1213, "message": "Unexpected error during authentication", "reason": "Unhandled exception during auth flow"},
        "AUTH_USER_ALREADY_EXISTS": {"code": 1214, "message": "User already exists", "reason": "A user with this email or phone number already exists", "http_status": 409},
        "TOKEN_DOMAIN_MISMATCH": {"code": 1215, "message": "Token domain mismatch", "reason": "Token was issued for a different domain and cannot be used on this domain", "http_status": 403},
        "AUTH_INVALID_TOKEN": {"code": 1216, "message": "Invalid or missing authentication token", "reason": "Token is missing, malformed, or cannot be decoded"},
        "AUTH_INVALID_REFRESH_TOKEN": {"code": 1217, "message": "Invalid or expired refresh token", "reason": "Refresh token is invalid, expired, or has been revoked"},
        "AUTH_INVALID_TOKEN_TYPE": {"code": 1218, "message": "Invalid token type", "reason": "The provided token is not of the expected type (e.g., access token used where refresh token is required)"},
        "AUTH_TOKEN_REVOKED": {"code": 1219, "message": "Token has been revoked", "reason": "This token has been blacklisted and is no longer valid. Please login again"},
        "AUTH_REFRESH_FAILED": {"code": 1220, "message": "Failed to refresh access token", "reason": "Error occurred while generating new tokens from refresh token"},
        "SESSION_INVALID": {"code": 1221, "message": "Session is invalid or expired", "reason": "The session associated with this token has been revoked, expired, or does not exist"},
        "AUTH_SESSION_MISSING": {"code": 1222, "message": "Session ID not found in token", "reason": "Token does not contain a valid session identifier"},
        "AUTH_SESSION_INVALID": {"code": 1223, "message": "Session has been revoked", "reason": "The session associated with this token has been logged out or invalidated"},
        "AUTH_USER_NOT_FOUND": {"code": 1224, "message": "User ID not found in token", "reason": "Token does not contain a valid user identifier"},
        "AUTH_VERIFICATION_UPDATE_FAILED": {"code": 1225, "message": "Failed to update verification status", "reason": "Database update failed while updating email or phone verification status"},
        "TOKEN_INVALID": {"code": 1226, "message": "Token has been revoked", "reason": "This token has been blacklisted and is no longer valid. Please login again to get a new token"},


        # 💼 User Profile (140x)
        "PROFILE_NOT_FOUND": {"code": 1401, "message": "User profile not found"},               # 404
        "PROFILE_ALREADY_EXISTS": {
                "code": 1402,
                "http_status": 400,
                "message": "User profile already exists",
            },
        "PROFILE_UPDATE_FAILED": {"code": 1402, "message": "Failed to update user profile", "reason": "Database update or validation error"},
        "PROFILE_PICTURE_UPDATE_FAILED": {"code": 1403, "message": "Failed to update profile picture", "reason": "File upload or storage service failed"},
        "PROFILE_EMAIL_CHANGE_FAILED": {"code": 1404, "message": "Failed to change email", "reason": "Email already in use or invalid"},
        "PROFILE_PHONE_CHANGE_FAILED": {"code": 1405, "message": "Failed to change phone", "reason": "Phone number invalid or already used"},
        "PROFILE_PROCESSING_ERROR": {"code": 1402, "message": "Error processing user profile", "reason": "Unexpected profile operation failure"},
        "PROFILE_INVALID_OTP": {"code": 1406, "message": "Invalid or expired OTP"},            # 400
        "PROFILE_INVALID_PAYLOAD": {"code": 1407, "message": "Invalid profile payload"},
        "EMAIL_ALREADY_EXISTS": {"code": 1408, "message": "Email already exists", "reason": "This email is already associated with another user account", "http_status": 400},

        # --- CREATE ERRORS ---
        "CREATE_FAILED": {"code": 1100, "message": "Failed to create resource due to invalid data or constraint violation", "http_status": 400},
        "DUPLICATE_ENTRY": {"code": 1101, "message": "Resource already exists", "http_status": 409},
        "FOREIGN_KEY_VIOLATION": {"code": 1102, "message": "Invalid reference to related data (foreign key constraint failed)", "http_status": 400},

        # --- READ ERRORS ---
        "RESOURCE_NOT_FOUND": {"code": 1200, "message": "Requested resource not found", "http_status": 404},
        "USER_NOT_FOUND": {"code": 1202, "message": "User not found", "http_status": 404},
        "INVALID_QUERY": {"code": 1203, "message": "Invalid filter or query parameters", "http_status": 400},

        # --- UPDATE ERRORS ---
        "UPDATE_FAILED": {"code": 1300, "message": "Failed to update resource", "http_status": 400},
        "CONFLICT_UPDATE": {"code": 1301, "message": "Update conflict — resource modified by another process", "http_status": 409},

        # --- DELETE ERRORS ---
        "DELETE_FAILED": {"code": 1400, "message": "Failed to delete resource", "http_status": 400},
        "RESOURCE_IN_USE": {"code": 1401, "message": "Cannot delete resource because it is in use", "http_status": 409},

        # --- DATABASE / INTERNAL ERRORS ---
        "DATABASE_CONNECTION_FAILED": {"code": 1500, "message": "Database connection failed", "http_status": 500},
        "DATABASE_HEALTH_CHECK_FAILED": {"code": 1504, "message": "Database health check failed", "reason": "Failed to check database health status."},
        "DATABASE_UNHEALTHY": {"code": 1505, "message": "Database unhealthy", "reason": "Database is not responding or is in an unhealthy state."},
        "INTEGRITY_ERROR": {"code": 1501, "message": "Data integrity error (constraint violation)", "http_status": 400},
        "TRANSACTION_ERROR": {"code": 1502, "message": "Transaction rollback due to internal error", "http_status": 500},
        "UNEXPECTED_ERROR": {"code": 1503, "message": "An unexpected database error occurred", "http_status": 500},

        # 🏥 Health Check Errors (1800-1899)
        "HEALTH_CHECK_FAILED": {"code": 1800, "message": "Health check failed", "reason": "Failed to perform health check."},
        "STORAGE_HEALTH_CHECK_FAILED": {"code": 1801, "message": "Storage health check failed", "reason": "Failed to check storage service health status."},
        "STORAGE_UNHEALTHY": {"code": 1802, "message": "Storage unhealthy", "reason": "Storage service is not responding or is in an unhealthy state."},

}
