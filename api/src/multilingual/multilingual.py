from src.enum.enum import LanguageStatusEnum
from typing import Optional, Dict, Any

# Default language
DEFAULT_LANGUAGE = LanguageStatusEnum.en

# ============================================================================
# MODULE-SPECIFIC TRANSLATIONS
# ============================================================================

# General/Common translations
GENERAL_TRANSLATIONS = {
    "en": {
        "Request successful": "Request successful",
        "Operation completed successfully": "Operation completed successfully",
        "User is available": "User is available",
        "User is not available": "User is not available",
        "Successfully logged out": "Successfully logged out",
    },
    "ar": {
        "Request successful": "تمت العملية بنجاح",
        "Operation completed successfully": "تمت العملية بنجاح",
        "User is available": "المستخدم متاح",
        "User is not available": "المستخدم غير متاح",
        "Successfully logged out": "تم تسجيل الخروج بنجاح",
    },
}

# Authenticate module translations
AUTHENTICATE_TRANSLATIONS = {
    "en": {
        "Login successful": "Login successful",
        "Signup successful": "Signup successful",
        "Password set successfully": "Password set successfully",
        "Password updated successfully": "Password updated successfully",
        "Verify Successfully": "Verify Successfully",
        "OTP sent successfully": "OTP sent successfully",
        "User profile fetched successfully": "User profile fetched successfully",
        "User profile update successfully": "User profile updated successfully",
        "Profile picture updated successfully": "Profile picture updated successfully",
        "Profile accessibility update successfully": "Profile accessibility updated successfully",
        "Profile language update successfully": "Profile language updated successfully",
        "Email updated successfully": "Email updated successfully",
        "Email updated and verified successfully": "Email updated and verified successfully",
        "Phone number updated and verified successfully": "Phone number updated and verified successfully",
        "Tokens refreshed successfully": "Tokens refreshed successfully",
        "Token information retrieved successfully": "Token information retrieved successfully",
        "Email verified successfully": "Email verified successfully",
        "Phone verified successfully": "Phone verified successfully",
        "SMS verified successfully": "SMS verified successfully",
        "WhatsApp verified successfully": "WhatsApp verified successfully",
    },
    "ar": {
        "Login successful": "تم تسجيل الدخول بنجاح",
        "Signup successful": "تم التسجيل بنجاح",
        "Password set successfully": "تم تعيين كلمة المرور بنجاح",
        "Password updated successfully": "تم تحديث كلمة المرور بنجاح",
        "Verify Successfully": "تم التحقق بنجاح",
        "OTP sent successfully": "تم إرسال رمز التحقق بنجاح",
        "User profile fetched successfully": "تم جلب ملف المستخدم بنجاح",
        "User profile update successfully": "تم تحديث ملف المستخدم بنجاح",
        "Profile picture updated successfully": "تم تحديث صورة الملف الشخصي بنجاح",
        "Profile accessibility update successfully": "تم تحديث إعدادات الخصوصية بنجاح",
        "Profile language update successfully": "تم تحديث اللغة بنجاح",
        "Email updated successfully": "تم تحديث البريد الإلكتروني بنجاح",
        "Email updated and verified successfully": "تم تحديث البريد الإلكتروني والتحقق منه بنجاح",
        "Phone number updated and verified successfully": "تم تحديث رقم الهاتف والتحقق منه بنجاح",
        "Tokens refreshed successfully": "تم تحديث الرموز بنجاح",
        "Token information retrieved successfully": "تم جلب معلومات الرمز بنجاح",
        "Email verified successfully": "تم التحقق من البريد الإلكتروني بنجاح",
        "Phone verified successfully": "تم التحقق من الهاتف بنجاح",
        "SMS verified successfully": "تم التحقق من الرسالة النصية بنجاح",
        "WhatsApp verified successfully": "تم التحقق من واتساب بنجاح",
    },
}

# Profile module translations
PROFILE_TRANSLATIONS = {
    "en": {
        "Theme updated successfully": "Theme updated successfully",
        "Account deactivated successfully": "Account deactivated successfully",
        "User settings retrieved successfully": "User settings retrieved successfully",
        "Timezone updated successfully": "Timezone updated successfully",
    },
    "ar": {
        "Theme updated successfully": "تم تحديث المظهر بنجاح",
        "Account deactivated successfully": "تم إلغاء تفعيل الحساب بنجاح",
        "User settings retrieved successfully": "تم جلب إعدادات المستخدم بنجاح",
        "Timezone updated successfully": "تم تحديث المنطقة الزمنية بنجاح",
    },
}

# Upload module translations
UPLOAD_TRANSLATIONS = {
    "en": {
        "File uploaded successfully": "File uploaded successfully",
        "File deleted successfully": "File deleted successfully",
    },
    "ar": {
        "File uploaded successfully": "تم تحميل الملف بنجاح",
        "File deleted successfully": "تم حذف الملف بنجاح",
    },
}

# Dashboard module translations
DASHBOARD_TRANSLATIONS = {
    "en": {
        "Dashboard overview retrieved successfully": "Dashboard overview retrieved successfully",
        "User statistics by status retrieved successfully": "User statistics by status retrieved successfully",
        "User statistics by type retrieved successfully": "User statistics by type retrieved successfully",
        "User statistics by auth type retrieved successfully": "User statistics by auth type retrieved successfully",
        "User statistics by country retrieved successfully": "User statistics by country retrieved successfully",
        "User statistics by language retrieved successfully": "User statistics by language retrieved successfully",
        "User growth statistics retrieved successfully": "User growth statistics retrieved successfully",
        "Recent sign-in statistics retrieved successfully": "Recent sign-in statistics retrieved successfully",
        "All dashboard statistics retrieved successfully": "All dashboard statistics retrieved successfully",
    },
    "ar": {
        "Dashboard overview retrieved successfully": "تم جلب نظرة عامة على لوحة التحكم بنجاح",
        "User statistics by status retrieved successfully": "تم جلب إحصائيات المستخدمين حسب الحالة بنجاح",
        "User statistics by type retrieved successfully": "تم جلب إحصائيات المستخدمين حسب النوع بنجاح",
        "User statistics by auth type retrieved successfully": "تم جلب إحصائيات المستخدمين حسب نوع المصادقة بنجاح",
        "User statistics by country retrieved successfully": "تم جلب إحصائيات المستخدمين حسب البلد بنجاح",
        "User statistics by language retrieved successfully": "تم جلب إحصائيات المستخدمين حسب اللغة بنجاح",
        "User growth statistics retrieved successfully": "تم جلب إحصائيات نمو المستخدمين بنجاح",
        "Recent sign-in statistics retrieved successfully": "تم جلب إحصائيات تسجيل الدخول الأخيرة بنجاح",
        "All dashboard statistics retrieved successfully": "تم جلب جميع إحصائيات لوحة التحكم بنجاح",
    },
}

# Health module translations
HEALTH_TRANSLATIONS = {
    "en": {
        "Database is healthy": "Database is healthy",
        "Storage is healthy": "Storage is healthy",
        "System health check completed": "System health check completed",
        "Test exception sent to Sentry": "Test exception sent to Sentry",
        "Test message sent to Sentry": "Test message sent to Sentry",
        "Test async error scheduled": "Test async error scheduled",
    },
    "ar": {
        "Database is healthy": "قاعدة البيانات سليمة",
        "Storage is healthy": "التخزين سليم",
        "System health check completed": "اكتملت فحص صحة النظام",
        "Test exception sent to Sentry": "تم إرسال استثناء الاختبار إلى Sentry",
        "Test message sent to Sentry": "تم إرسال رسالة الاختبار إلى Sentry",
        "Test async error scheduled": "تم جدولة خطأ الاختبار غير المتزامن",
    },
}

# Permissions module translations
PERMISSIONS_TRANSLATIONS = {
    "en": {
        "Permissions retrieved successfully": "Permissions retrieved successfully",
        "Permission retrieved successfully": "Permission retrieved successfully",
        "Permission created successfully": "Permission created successfully",
        "Permission updated successfully": "Permission updated successfully",
        "Permission deleted successfully": "Permission deleted successfully",
        "Groups retrieved successfully": "Groups retrieved successfully",
        "Group retrieved successfully": "Group retrieved successfully",
        "Group created successfully": "Group created successfully",
        "Group updated successfully": "Group updated successfully",
        "Group deleted successfully": "Group deleted successfully",
        "Permissions assigned successfully": "Permissions assigned successfully",
        "User groups retrieved successfully": "User groups retrieved successfully",
        "User permissions retrieved successfully": "User permissions retrieved successfully",
        "Groups assigned successfully (user role flags updated)": "Groups assigned successfully (user role flags updated)",
    },
    "ar": {
        "Permissions retrieved successfully": "تم جلب الأذونات بنجاح",
        "Permission retrieved successfully": "تم جلب الإذن بنجاح",
        "Permission created successfully": "تم إنشاء الإذن بنجاح",
        "Permission updated successfully": "تم تحديث الإذن بنجاح",
        "Permission deleted successfully": "تم حذف الإذن بنجاح",
        "Groups retrieved successfully": "تم جلب المجموعات بنجاح",
        "Group retrieved successfully": "تم جلب المجموعة بنجاح",
        "Group created successfully": "تم إنشاء المجموعة بنجاح",
        "Group updated successfully": "تم تحديث المجموعة بنجاح",
        "Group deleted successfully": "تم حذف المجموعة بنجاح",
        "Permissions assigned successfully": "تم تعيين الأذونات بنجاح",
        "User groups retrieved successfully": "تم جلب مجموعات المستخدم بنجاح",
        "User permissions retrieved successfully": "تم جلب أذونات المستخدم بنجاح",
        "Groups assigned successfully (user role flags updated)": "تم تعيين المجموعات بنجاح (تم تحديث علامات دور المستخدم)",
    },
}

# Activity module translations
ACTIVITY_TRANSLATIONS = {
    "en": {
        "Activity log created successfully": "Activity log created successfully",
        "Activity logs retrieved successfully": "Activity logs retrieved successfully",
        "Activity log retrieved successfully": "Activity log retrieved successfully",
        "User activity logs retrieved successfully": "User activity logs retrieved successfully",
        "Your activity logs retrieved successfully": "Your activity logs retrieved successfully",
    },
    "ar": {
        "Activity log created successfully": "تم إنشاء سجل النشاط بنجاح",
        "Activity logs retrieved successfully": "تم جلب سجلات النشاط بنجاح",
        "Activity log retrieved successfully": "تم جلب سجل النشاط بنجاح",
        "User activity logs retrieved successfully": "تم جلب سجلات نشاط المستخدم بنجاح",
        "Your activity logs retrieved successfully": "تم جلب سجلات نشاطك بنجاح",
    },
}

# Analytics module translations
ANALYTICS_TRANSLATIONS = {
    "en": {
        # Add analytics-specific messages here
    },
    "ar": {
        # Add analytics-specific messages here
    },
}

# ============================================================================
# MERGE ALL MODULE TRANSLATIONS
# ============================================================================

def _merge_translations(*translation_dicts: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    """
    Merge multiple translation dictionaries into one.

    Args:
        *translation_dicts: Variable number of translation dictionaries to merge

    Returns:
        Merged translation dictionary
    """
    merged = {}
    for lang in ["en", "ar"]:  # Add more languages as needed
        merged[lang] = {}
        for trans_dict in translation_dicts:
            if lang in trans_dict:
                merged[lang].update(trans_dict[lang])
    return merged

# Main translations dictionary (merged from all modules)
TRANSLATIONS = _merge_translations(
    GENERAL_TRANSLATIONS,
    AUTHENTICATE_TRANSLATIONS,
    PROFILE_TRANSLATIONS,
    UPLOAD_TRANSLATIONS,
    DASHBOARD_TRANSLATIONS,
    HEALTH_TRANSLATIONS,
    PERMISSIONS_TRANSLATIONS,
    ACTIVITY_TRANSLATIONS,
    ANALYTICS_TRANSLATIONS,
)

# ============================================================================
# ERROR TRANSLATIONS (Module-specific)
# ============================================================================

# General errors
GENERAL_ERROR_TRANSLATIONS = {
    "en": {
        "Invalid request payload": "Invalid request payload",
        "Unauthorized access": "Unauthorized access",
        "Permission denied": "Permission denied",
        "Requested resource not found": "Requested resource not found",
        "HTTP method not allowed": "HTTP method not allowed",
        "Request timed out": "Request timed out",
        "Resource conflict": "Resource conflict",
        "Unprocessable entity": "Unprocessable entity",
        "Too many requests": "Too many requests",
        "Validation failed": "Validation failed",
        "Internal server error": "Internal server error",
        "Unknown error occurred": "Unknown error occurred",
        "Not implemented": "Not implemented",
        "Invalid or expired token": "Invalid or expired token",
        "Duplicate entry not allowed": "Duplicate entry not allowed",
        "Payment failed": "Payment failed",
        "Payment declined": "Payment declined",
        "Failed to create resource due to invalid data or constraint violation": "Failed to create resource due to invalid data or constraint violation",
        "Resource already exists": "Resource already exists",
        "Invalid reference to related data (foreign key constraint failed)": "Invalid reference to related data (foreign key constraint failed)",
        "User not found": "User not found",
        "Invalid filter or query parameters": "Invalid filter or query parameters",
        "Failed to update resource": "Failed to update resource",
        "Update conflict — resource modified by another process": "Update conflict — resource modified by another process",
        "Failed to delete resource": "Failed to delete resource",
        "Cannot delete resource because it is in use": "Cannot delete resource because it is in use",
        "Database connection failed": "Database connection failed",
        "Database health check failed": "Database health check failed",
        "Database unhealthy": "Database unhealthy",
        "Data integrity error (constraint violation)": "Data integrity error (constraint violation)",
        "Transaction rollback due to internal error": "Transaction rollback due to internal error",
        "An unexpected database error occurred": "An unexpected database error occurred",
    },
    "ar": {
        "Invalid request payload": "بيانات الطلب غير صحيحة",
        "Unauthorized access": "وصول غير مصرح به",
        "Permission denied": "تم رفض الإذن",
        "Requested resource not found": "المورد المطلوب غير موجود",
        "HTTP method not allowed": "طريقة HTTP غير مسموحة",
        "Request timed out": "انتهت مهلة الطلب",
        "Resource conflict": "تعارض في المورد",
        "Unprocessable entity": "كيان غير قابل للمعالجة",
        "Too many requests": "طلبات كثيرة جداً",
        "Validation failed": "فشل التحقق",
        "Internal server error": "خطأ في الخادم الداخلي",
        "Unknown error occurred": "حدث خطأ غير معروف",
        "Not implemented": "غير مطبق",
        "Invalid or expired token": "رمز غير صالح أو منتهي الصلاحية",
        "Duplicate entry not allowed": "الإدخال المكرر غير مسموح",
        "Payment failed": "فشلت عملية الدفع",
        "Payment declined": "تم رفض الدفع",
        "Failed to create resource due to invalid data or constraint violation": "فشل إنشاء المورد بسبب بيانات غير صحيحة أو انتهاك قيد",
        "Resource already exists": "المورد موجود بالفعل",
        "Invalid reference to related data (foreign key constraint failed)": "مرجع غير صالح للبيانات ذات الصلة (فشل قيد المفتاح الخارجي)",
        "User not found": "المستخدم غير موجود",
        "Invalid filter or query parameters": "معاملات التصفية أو الاستعلام غير صحيحة",
        "Failed to update resource": "فشل تحديث المورد",
        "Update conflict — resource modified by another process": "تعارض في التحديث - تم تعديل المورد بواسطة عملية أخرى",
        "Failed to delete resource": "فشل حذف المورد",
        "Cannot delete resource because it is in use": "لا يمكن حذف المورد لأنه قيد الاستخدام",
        "Database connection failed": "فشل الاتصال بقاعدة البيانات",
        "Database health check failed": "فشل فحص صحة قاعدة البيانات",
        "Database unhealthy": "قاعدة البيانات غير سليمة",
        "Data integrity error (constraint violation)": "خطأ في تكامل البيانات (انتهاك قيد)",
        "Transaction rollback due to internal error": "تراجع المعاملة بسبب خطأ داخلي",
        "An unexpected database error occurred": "حدث خطأ غير متوقع في قاعدة البيانات",
    },
}

# Auth errors
AUTH_ERROR_TRANSLATIONS = {
    "en": {
        "Invalid username or password": "Invalid username or password",
        "Invalid login credentials": "Invalid login credentials",
        "Failed to create account": "Failed to create account",
        "Failed to log out": "Failed to log out",
        "Invalid or expired OTP": "Invalid or expired OTP",
        "Failed to send OTP": "Failed to send OTP",
        "Failed to verify OTP": "Failed to verify OTP",
        "Unsupported authentication channel": "Unsupported authentication channel",
        "Failed to update password": "Failed to update password",
        "Old password is incorrect": "Old password is incorrect",
        "Failed to reset password": "Failed to reset password",
        "Invalid payload": "Invalid payload",
        "Unexpected error during authentication": "Unexpected error during authentication",
        "User already exists": "User already exists",
        "Token domain mismatch": "Token domain mismatch",
        "Invalid or missing authentication token": "Invalid or missing authentication token",
        "Invalid or expired refresh token": "Invalid or expired refresh token",
        "Invalid token type": "Invalid token type",
        "Token has been revoked": "Token has been revoked",
        "Failed to refresh access token": "Failed to refresh access token",
        "Session is invalid or expired": "Session is invalid or expired",
        "Session ID not found in token": "Session ID not found in token",
        "Session has been revoked": "Session has been revoked",
        "User ID not found in token": "User ID not found in token",
        "Failed to update verification status": "Failed to update verification status",
    },
    "ar": {
        "Invalid username or password": "اسم المستخدم أو كلمة المرور غير صحيحة",
        "Invalid login credentials": "بيانات تسجيل الدخول غير صحيحة",
        "Failed to create account": "فشل إنشاء الحساب",
        "Failed to log out": "فشل تسجيل الخروج",
        "Invalid or expired OTP": "رمز OTP غير صالح أو منتهي الصلاحية",
        "Failed to send OTP": "فشل إرسال رمز OTP",
        "Failed to verify OTP": "فشل التحقق من رمز OTP",
        "Unsupported authentication channel": "قناة المصادقة غير مدعومة",
        "Failed to update password": "فشل تحديث كلمة المرور",
        "Old password is incorrect": "كلمة المرور القديمة غير صحيحة",
        "Failed to reset password": "فشل إعادة تعيين كلمة المرور",
        "Invalid payload": "بيانات غير صحيحة",
        "Unexpected error during authentication": "خطأ غير متوقع أثناء المصادقة",
        "User already exists": "المستخدم موجود بالفعل",
        "Token domain mismatch": "عدم تطابق نطاق الرمز",
        "Invalid or missing authentication token": "رمز المصادقة غير صالح أو مفقود",
        "Invalid or expired refresh token": "رمز التحديث غير صالح أو منتهي الصلاحية",
        "Invalid token type": "نوع الرمز غير صالح",
        "Token has been revoked": "تم إلغاء الرمز",
        "Failed to refresh access token": "فشل تحديث رمز الوصول",
        "Session is invalid or expired": "الجلسة غير صالحة أو منتهية الصلاحية",
        "Session ID not found in token": "معرف الجلسة غير موجود في الرمز",
        "Session has been revoked": "تم إلغاء الجلسة",
        "User ID not found in token": "معرف المستخدم غير موجود في الرمز",
        "Failed to update verification status": "فشل تحديث حالة التحقق",
    },
}

# Profile errors
PROFILE_ERROR_TRANSLATIONS = {
    "en": {
        "User profile not found": "User profile not found",
        "User profile already exists": "User profile already exists",
        "Failed to update user profile": "Failed to update user profile",
        "Failed to update profile picture": "Failed to update profile picture",
        "Failed to change email": "Failed to change email",
        "Failed to change phone": "Failed to change phone",
        "Error processing user profile": "Error processing user profile",
        "Invalid profile payload": "Invalid profile payload",
        "Email already exists": "Email already exists",
    },
    "ar": {
        "User profile not found": "ملف المستخدم غير موجود",
        "User profile already exists": "ملف المستخدم موجود بالفعل",
        "Failed to update user profile": "فشل تحديث ملف المستخدم",
        "Failed to update profile picture": "فشل تحديث صورة الملف الشخصي",
        "Failed to change email": "فشل تغيير البريد الإلكتروني",
        "Failed to change phone": "فشل تغيير رقم الهاتف",
        "Error processing user profile": "خطأ في معالجة ملف المستخدم",
        "Invalid profile payload": "بيانات الملف الشخصي غير صحيحة",
        "Email already exists": "البريد الإلكتروني موجود بالفعل",
    },
}

# Media/Upload errors
MEDIA_ERROR_TRANSLATIONS = {
    "en": {
        "Media file not found": "Media file not found",
        "Failed to upload media": "Failed to upload media",
        "Unsupported media type": "Unsupported media type",
        "Media file too large": "Media file too large",
        "Unexpected error during media uploading..": "Unexpected error during media uploading..",
        "Unexpected error during media deleting..": "Unexpected error during media deleting..",
        "At least one of 'url' or 'file' must be provided...": "At least one of 'url' or 'file' must be provided...",
    },
    "ar": {
        "Media file not found": "ملف الوسائط غير موجود",
        "Failed to upload media": "فشل تحميل الوسائط",
        "Unsupported media type": "نوع الوسائط غير مدعوم",
        "Media file too large": "ملف الوسائط كبير جداً",
        "Unexpected error during media uploading..": "خطأ غير متوقع أثناء تحميل الوسائط",
        "Unexpected error during media deleting..": "خطأ غير متوقع أثناء حذف الوسائط",
        "At least one of 'url' or 'file' must be provided...": "يجب توفير 'url' أو 'file' على الأقل",
    },
}

# Health errors
HEALTH_ERROR_TRANSLATIONS = {
    "en": {
        "Health check failed": "Health check failed",
        "Storage health check failed": "Storage health check failed",
        "Storage unhealthy": "Storage unhealthy",
    },
    "ar": {
        "Health check failed": "فشل فحص الصحة",
        "Storage health check failed": "فشل فحص صحة التخزين",
        "Storage unhealthy": "التخزين غير سليم",
    },
}

# Database errors
DATABASE_ERROR_TRANSLATIONS = {
    "en": {
        "Supabase API responded with an error": "Supabase API responded with an error",
        "Supabase HTTP error occurred": "Supabase HTTP error occurred",
    },
    "ar": {
        "Supabase API responded with an error": "استجابة Supabase API بخطأ",
        "Supabase HTTP error occurred": "حدث خطأ HTTP في Supabase",
    },
}

# Permissions errors
PERMISSIONS_ERROR_TRANSLATIONS = {
    "en": {
        "Permission not found": "Permission not found",
        "Failed to create permission": "Failed to create permission",
        "Failed to update permission": "Failed to update permission",
        "Failed to delete permission": "Failed to delete permission",
        "Group not found": "Group not found",
        "Failed to create group": "Failed to create group",
        "Failed to update group": "Failed to update group",
        "Failed to delete group": "Failed to delete group",
        "Failed to assign permissions to group": "Failed to assign permissions to group",
        "Failed to assign groups to user": "Failed to assign groups to user",
    },
    "ar": {
        "Permission not found": "الإذن غير موجود",
        "Failed to create permission": "فشل إنشاء الإذن",
        "Failed to update permission": "فشل تحديث الإذن",
        "Failed to delete permission": "فشل حذف الإذن",
        "Group not found": "المجموعة غير موجودة",
        "Failed to create group": "فشل إنشاء المجموعة",
        "Failed to update group": "فشل تحديث المجموعة",
        "Failed to delete group": "فشل حذف المجموعة",
        "Failed to assign permissions to group": "فشل تعيين الأذونات للمجموعة",
        "Failed to assign groups to user": "فشل تعيين المجموعات للمستخدم",
    },
}

# Analytics errors
ANALYTICS_ERROR_TRANSLATIONS = {
    "en": {
        # Add analytics-specific errors here
    },
    "ar": {
        # Add analytics-specific errors here
    },
}

# Payments errors
PAYMENTS_ERROR_TRANSLATIONS = {
    "en": {
        # Add payments-specific errors here
    },
    "ar": {
        # Add payments-specific errors here
    },
}

# Recommendations errors
RECOMMENDATIONS_ERROR_TRANSLATIONS = {
    "en": {
        # Add recommendations-specific errors here
    },
    "ar": {
        # Add recommendations-specific errors here
    },
}

# GenerativeAI errors
GENERATIVEAI_ERROR_TRANSLATIONS = {
    "en": {
        # Add generativeai-specific errors here
    },
    "ar": {
        # Add generativeai-specific errors here
    },
}

# History errors
HISTORY_ERROR_TRANSLATIONS = {
    "en": {
        # Add history-specific errors here
    },
    "ar": {
        # Add history-specific errors here
    },
}

# Merge all error translations
ERROR_TRANSLATIONS = _merge_translations(
    GENERAL_ERROR_TRANSLATIONS,
    AUTH_ERROR_TRANSLATIONS,
    PROFILE_ERROR_TRANSLATIONS,
    MEDIA_ERROR_TRANSLATIONS,
    DATABASE_ERROR_TRANSLATIONS,
    HEALTH_ERROR_TRANSLATIONS,
    PERMISSIONS_ERROR_TRANSLATIONS,
    ANALYTICS_ERROR_TRANSLATIONS,
    PAYMENTS_ERROR_TRANSLATIONS,
    RECOMMENDATIONS_ERROR_TRANSLATIONS,
    GENERATIVEAI_ERROR_TRANSLATIONS,
    HISTORY_ERROR_TRANSLATIONS,
)

# ============================================================================
# TRANSLATION FUNCTIONS
# ============================================================================

def normalize_language(lang_value: Any) -> str:
    """
    Normalize language value from enum or string to lowercase string.

    Args:
        lang_value: Language value (can be enum, string, etc.)

    Returns:
        Normalized language code (lowercase string)
    """
    if not lang_value:
        return DEFAULT_LANGUAGE

    # Handle enum values
    if hasattr(lang_value, 'value'):
        lang = str(lang_value.value).lower().strip()
    else:
        lang = str(lang_value).lower().strip()

    # Validate language exists in translations
    if lang in TRANSLATIONS:
        return lang

    # Fallback to default if invalid
    return DEFAULT_LANGUAGE


def translate_message(message: str, language: str = DEFAULT_LANGUAGE) -> str:
    """
    Translate a success message to the specified language.

    Args:
        message: Original message in English
        language: Target language code (default: 'en')

    Returns:
        Translated message or original if translation not found
    """
    if not message:
        return message

    language = language.lower().strip() if language else DEFAULT_LANGUAGE

    # Return original if language is English or not supported
    if language == "en" or language not in TRANSLATIONS:
        return message

    # Get translation
    translations = TRANSLATIONS.get(language, {})
    translated = translations.get(message, message)

    # Return translated message (or original if not found)
    return translated


def translate_error(error_message: str, language: str = DEFAULT_LANGUAGE) -> str:
    """
    Translate an error message to the specified language.

    Args:
        error_message: Original error message in English
        language: Target language code (default: 'en')

    Returns:
        Translated error message or original if translation not found
    """
    if not error_message:
        return error_message

    language = language.lower() if language else DEFAULT_LANGUAGE

    # Return original if language is English or not supported
    if language == "en" or language not in ERROR_TRANSLATIONS:
        return error_message

    # Get translation
    translations = ERROR_TRANSLATIONS.get(language, {})
    return translations.get(error_message, error_message)


def translate_json_data(data: Any, language: str = DEFAULT_LANGUAGE) -> Any:
    """
    Recursively translate string values in JSON data structures.
    Translates both keys and values based on language.

    Args:
        data: JSON-serializable data (dict, list, str, etc.)
        language: Target language code

    Returns:
        Translated data structure
    """
    if language == "en" or language not in TRANSLATIONS:
        return data

    if isinstance(data, dict):
        translated = {}
        for key, value in data.items():
            # Translate key if it's a string
            translated_key = translate_message(str(key), language) if isinstance(key, str) else key
            # Recursively translate value
            translated[translated_key] = translate_json_data(value, language)
        return translated

    elif isinstance(data, list):
        return [translate_json_data(item, language) for item in data]

    elif isinstance(data, str):
        # Translate string value
        return translate_message(data, language)

    else:
        # Return as-is for other types (int, float, bool, None, etc.)
        return data


def get_language(language: Optional[str] = 'en') -> str:
    """
    Get language with priority: provided language > request.state.language > default.
    Simplified version - just pass language string directly.

    Args:
        language: Language code string (e.g., "en", "ar")
        request: Optional FastAPI Request object to extract language from state

    Returns:
        Language code (default: 'en')
    """
    # Priority 1: Explicitly provided language (highest priority)
    if language:
        lang = str(language).lower().strip()
        # Validate language exists in translations
        if lang in TRANSLATIONS:
            return lang
    # Fallback to default if invalid
    return DEFAULT_LANGUAGE
