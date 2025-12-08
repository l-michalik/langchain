from enum import Enum

COLORS = {
    "BLUE": "\033[34m",
    "GREEN": "\033[32m",
    "YELLOW": "\033[33m",
    "RED": "\033[31m",
    "CYAN": "\033[36m",
    "MAGENTA": "\033[35m",
    "WHITE": "\033[37m",
    "BLACK": "\033[30m",
    "BRIGHT_BLUE": "\033[94m",
    "BRIGHT_GREEN": "\033[92m",
    "BRIGHT_YELLOW": "\033[93m",
    "BRIGHT_RED": "\033[91m",
    "BRIGHT_CYAN": "\033[96m",
    "BRIGHT_MAGENTA": "\033[95m",
    "BRIGHT_WHITE": "\033[97m",
    "RESET": "\033[0m",
}

class WorkTypes(str, Enum):
    ARTWORK_ADAPTATIONS     = "Artwork Adaptations"
    ARTWORKING              = "Artworking"
    ANIMATED_BANNERS        = "Animated Banners"
    BROCHURES               = "Brochures"
    CORPORATE_PRESENTATIONS = "Corporate Presentations"
    CREATIVE_PRESENTATIONS  = "Creative Presentations"
    DIGITAL_ADVERTS         = "Digital Adverts"
    EMAIL_DESIGNS           = "Email Designs"
    FLYERS                  = "Flyers"
    HTML5_BANNER_DESIGNS    = "HTML5 Banner Designs"
    LEAFLETS                = "Leaflets"
    PITCH_DOCUMENTS         = "Pitch Documents"
    REPORTS                 = "Reports"
    RICH_MEDIA_BANNERS      = "Rich Media Banners"
    STATIC_BANNERS          = "Static Banners"
    TEMPLATE_ADAPTATIONS    = "Template Adaptations"
    COLOR_CORRECTION        = "Color Correction"
    RETOUCHING              = "Retouching"
    CUTOUT_MASKING          = "Cutout / Masking"
    AI_GEN_IMAGES           = "AI Gen images"