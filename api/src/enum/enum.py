from enum import Enum

class AdsShowTypeEnum(str, Enum):
    private = "private"
    public = "public"
    combo = "combo"

class UserStatusEnum(str, Enum):
    DRAFT = "Draft"              # Not Verified
    PUBLISHED = "Published"      # Active & Verified
    VERIFIED = "Verified"        # Verified
    INACTIVE = "Inactive"        # Suspended
    DELETED = "Deleted"          # Deleted

class UserStatusAuthEnum(str, Enum):
    INACTIVE = "Inactive"
    ACTIVE = "Active"
    SUSPENDED = "Suspended"
    DELETED = "Deleted"

class ProfileAccessibilityEnum(str, Enum):
    public = "public"
    private = "private"

class UserTypeEnum(str, Enum):
    admin = "admin"
    customer = "customer"
    business = "business"

class ThemeEnum(str, Enum):
    light = "light"
    dark = "dark"
    dynamic = "dynamic"

class AuthTypeEnum(str, Enum):
    phone = "phone"
    google = "google"
    apple = "apple"
    anonymous = "anonymous"
    email = "email"

class AdminLanguageStatusEnum(str, Enum):
    en = "en"
    ar = "ar"
    ind = "ind"
    fr = "fr"
    es = "es"
    de = "de"
    it = "it"
    pt = "pt"

class RegenerationCases(Enum):
    """
    Enum for regeneration cases
    """
    NEW_GENERATION = 1
    CURRENT_USER_REGENERATING_CONTENT = 2
    REGENERATION = 3
    OTHER_USER_REGENERATING_CONTENT = 4

class GenderEnum(str, Enum):
    male = "male"
    female = "female"

class SkinToneEnum(str, Enum):
    dark = "dark"
    fair = "fair"

class AgeGroupEnum(str, Enum):
    child = "child"
    teenager = "teenager"
    adult = "adult"
    elder = "elder"

# --- Admin / Actions ---
class AdminActionEnum(str, Enum):
    Pending = "Pending"
    Reviewing = "Reviewing"
    Updated = "Updated"
    Inprogress = "Inprogress"
    Rejected = "Rejected"
    Approved = "Approved"
    Created = "Created"

class RowStatusEnum(str, Enum):
    Draft = "Draft"
    Published = "Published"
    Deleted = "Deleted"
    Scheduled = "Scheduled"

# --- Ads / Content ---
class AdsContentTypeEnum(str, Enum):
    Image = "Image"
    Video = "Video"

class AdsPlacementEnum(str, Enum):
    IntroScreen = "Intro Screen"
    GenerationScreen = "Generation Screen"
    GeneratedScreen = "Generated Screen"

class ContentVisibilityEnum(str, Enum):
    published = "published"
    archived = "archived"
    restricted = "restricted"

# --- Payment / Wallet ---
class CurrencyTypeEnum(str, Enum):
    KWD = "KWD"
    USD = "USD"
    INR = "INR"

class PaymentGatewayEnum(str, Enum):
    Tap = "Tap"
    Paypal = "Paypal"
    Cash = "Cash"
    GPay = "GPay"
    ApplePay = "Apple Pay"
    RevenueCat = "RevenueCat"

class PaymentStatusEnum(str, Enum):
    captured = "captured"
    completed = "completed"
    failed = "failed"
    expired = "expired"
    refunded = "refunded"
    CAPTURED = "CAPTURED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"
    REFUNDED = "REFUNDED"
    CANCELLED = "CANCELLED"
    INITIATED = "INITIATED"
    DECLINED = "DECLINED"
    INITIAL_PURCHASE = "INITIAL_PURCHASE"
    RENEWAL = "RENEWAL"
    CANCELLATION = "CANCELLATION"
    UNCANCELLATION = "UNCANCELLATION"
    NON_RENEWING_PURCHASE = "NON_RENEWING_PURCHASE"
    SUBSCRIPTION_PAUSED = "SUBSCRIPTION_PAUSED"
    ABANDONED = "ABANDONED"
    abandoned = "abandoned"
    TIMEDOUT = "TIMEDOUT"


class WalletTransactionTypeEnum(str, Enum):
    add = "add"
    subtract = "subtract"
    debit = "debit"
    credit = "credit"


class WalletTransactionUsageTypeEnum(str, Enum):
    textToImage = "textToImage"
    textToVideo = "textToVideo"
    referral = "referral"
    refund = "refund"
    share = "share"
    conversational_ai = "conversational_ai"
    train = "/train"
    generate_txt2img = "/generate/txt2img"
    generate_sadtalker = "/generate/sadtalker"
    generate_outpaint = "/generate/outpaint"
    video_swap = "/video-swap"
    avatar = "avatar"
    videoTo3D = "videoTo3D"
    swap = "swap"
    txt2img = "txt2img"
    sadtalker = "sadtalker"
    outpaint = "outpaint"
    video_dash_swap = "video-swap"  # duplicate name, used dash
    img2img = "img2img"
    txt2vid = "txt2vid"
    img2vid = "img2vid"
    product_design = "product_design"
    in_app_purchase = "in_app_purchase"
    tts = "tts"
    imageToImage = "imageToImage"
    imageToVideo = "imageToVideo"
    videoToVideo = "videoToVideo"
    ImageGeneration="ImageGeneration"
    VideoGeneration="VideoGeneration"
    AudioGeneration="AudioGeneration"
    CartoonGeneration="CartoonGeneration"
    Purchased="Purchased"
    Refund="Refund"
    Cancelled="Cancelled"
    Reward="Reward"
    Like="Like"
    Comment="Comment"
    Follow="Follow"
    Mention="Mention"
    Share="Share"
    Post="Post"

# --- Notifications / Reactions ---
class NotificationTypeEnum(str, Enum):
    reaction = "reaction"
    comment = "comment"
    mention = "mention"
    share = "share"
    follow = "follow"
    generation = "generation"
    reward = "reward"
    engagement = "engagement"
    system = "system"

class ReactionTypeEnum(str, Enum):
    dislike = "dislike"
    okay = "okay"
    like = "like"
    veryNice = "veryNice"
    hot = "hot"

# --- Device / App ---
class DeviceStatusEnum(str, Enum):
    active = "active"
    inactive = "inactive"

class AppStoreTypeEnum(str, Enum):
    play_store = "play_store"
    app_store = "app_store"

class AppTypeEnum(str, Enum):
    screens = "screens"
    mobile = "mobile"

# AuthTypeEnum is now imported from admin if available

class ConnectionStatusEnum(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class FileTypeEnum(str, Enum):
    image = "image"
    video = "video"
    audio = "audio"

class StoreTypeEnum(str, Enum):
    play_store = "play_store"
    app_store = "app_store"

# --- Generation / AI ---
class GenerationModelEnum(str, Enum):
    SAMPLER = "SAMPLER"
    MODEL = "MODEL"

class GenerationStatusEnum(str, Enum):
    IN_QUEUE = "IN_QUEUE"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    PHOTOBOOTH = "PHOTOBOOTH"

class GenerationTypeEnum(str, Enum):
    textToVideo = "textToVideo"
    textToImage = "textToImage"
    avatar = "avatar"
    videoTo3D = "videoTo3D"
    product_design = "product_design"
    imageToImage = "imageToImage"
    imageToVideo = "imageToVideo"

class GenerationTypeEnum2(str, Enum):
    ImageGeneration = "ImageGeneration"
    VideoGeneration = "VideoGeneration"
    AudioGeneration = "AudioGeneration"
    CartoonGeneration = "CartoonGeneration"

# --- Misc ---
class LanguageEnum(str, Enum):
    en = "en"
    ar = "ar"
    in_ = "in"  # 'in' is a Python keyword

class PrintStatusEnum(str, Enum):
    to_print = "to_print"
    printing = "printing"
    failed = "failed"
    printed = "printed"
    total = "total"

class ReactionTypeEnum(str, Enum):
    dislike = "dislike"
    okay = "okay"
    like = "like"
    veryNice = "veryNice"
    hot = "hot"

class ReportStatusEnum(str, Enum):
    pending = "pending"
    under_review = "under_review"
    resolved = "resolved"
    rejected = "rejected"
    blocked = "blocked"

# Use admin LanguageStatusEnum if available, otherwise create alias
try:
    LanguageStatusEnum = AdminLanguageStatusEnum
except NameError:
    class LanguageStatusEnum(str, Enum):
        en = "en"
        ar = "ar"
        ind = "ind"
        fr = "fr"
        es = "es"
        de = "de"
        it = "it"
        pt = "pt"


class PackageTypeEnum(str, Enum):
    SUBSCRIPTION = "subscription"
    ONE_TIME = "one_time"


class PackageRenewDurationTypeEnum(str, Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class PackageEntitlementTypeEnum(str, Enum):
    BASIC = "basic"
    ADVANCED = "advanced"
    PROFESSIONAL = "professional"


class PackageAvailablePlatformTypeEnum(str, Enum):
    PLAY_STORE = "play_store"
    APP_STORE = "app_store"


class LeonardoStyleEnum(str, Enum):
    BOKEH = "BOKEH"
    CINEMATIC = "CINEMATIC"
    CINEMATIC_CLOSEUP = "CINEMATIC_CLOSEUP"
    CREATIVE = "CREATIVE"
    FASHION = "FASHION"
    FILM = "FILM"
    FOOD = "FOOD"
    HDR = "HDR"
    LONG_EXPOSURE = "LONG_EXPOSURE"
    MACRO = "MACRO"