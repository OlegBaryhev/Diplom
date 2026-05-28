LOGS = {
    "logs": {"all_subsections": ["read", "edit", "delete"]},
    "brand_log": {"all_subsections": ["read", "delete"]},
    "category_log": {"all_subsections": ["read", "delete"]},
    "order_log": {"all_subsections": ["read", "delete"]},
    "product_log": {"all_subsections": ["read", "delete"]},
    "user_log": {"all_subsections": ["read", "delete"]},
}

SUPERUSER_PERMISSIONS = {
    "home": {"all_subsections": ["read"]},
    "products": {"all_subsections": ["read", "write", "edit", "delete", "buy", "download", "recalculate"]},
    "orders": {"all_subsections": ["read", "write", "edit", "delete"]},
    "carts": {"all_subsections": ["read", "write", "edit", "delete"]},
    "profile": {"all_subsections": ["read", "write", "edit", "delete", "status", "change-role"]},
    "analogs": {"all_subsections": ["read", "write", "edit", "delete"]},
    "recalculate_history": {"all_subsections": ["read", "write", "edit", "delete"]},
    "users_control": {"all_subsections": ["read", "write", "edit", "delete", "status", "change-role", "download"]},
    "more": {"all_subsections": ["read"]},
    "categories": {"all_subsections": ["read", "write", "edit", "delete"]},
    "brands": {"all_subsections": ["read", "write", "edit", "delete"]},
    "roles": {"all_subsections": ["read", "write", "edit", "delete"]},
} | LOGS

MODERATOR_PERMISSIONS = {
    "home": {"all_subsections": ["read"]},
    "products": {"all_subsections": ["read", "edit", "write", "delete", "buy", "download"]},
    "profile": {"all_subsections": ["read", "write", "edit", "delete", "status", "change-role"]},
    "more": {"all_subsections": ["read"]},
    "categories": {"all_subsections": ["read", "edit", "write", "delete"]},
    "brands": {"all_subsections": ["read", "edit", "write", "delete"]},
    "orders": {"all_subsections": ["read", "edit", "delete"]},
}

GUEST_PERMISSIONS = {
    "home": {"all_subsections": ["read"]},
    "products": {"all_subsections": ["read", "buy"]},
    "profile": {"all_subsections": ["read", "write", "edit", "delete", "status", "change-role"]},
    "more": {"all_subsections": ["read"]},
    "categories": {"all_subsections": ["read"]},
    "brands": {"all_subsections": ["read"]},
}