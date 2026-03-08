import pandas as pd
from src.core.categories import (
    map_category, 
    check_reimbursable, 
    check_rent, 
    check_eating_out,
    check_education,
    check_vacation,
    check_home_decor,
    check_transport,
    check_appearance,
    check_gifts,
    check_subscriptions,
    check_electronics,
    check_groceries,
    check_government,
    check_health,
    check_telecom,
    check_entertainment
)
from returns.maybe import Some, Nothing

def create_row(payee="", amount=0.0, category="Unknown"):
    return pd.Series({"Payee": payee, "Amount": amount, "Category": category})

def test_check_reimbursable():
    assert check_reimbursable(create_row("some expense", -50.0)) == Some("Reimbursable Expenses")
    assert check_reimbursable(create_row("work expenses", 50.0)) == Some("Reimbursable Expenses")
    assert check_reimbursable(create_row("shared bills", 100.0)) == Some("Reimbursable Expenses")
    assert check_reimbursable(create_row("normal expense", 50.0)) == Nothing

def test_check_rent():
    assert check_rent(create_row("paybox", 3000.0)) == Some("Rent and Utilities")
    assert check_rent(create_row("paybox", 850.0)) == Some("Rent and Utilities")
    assert check_rent(create_row("paybox", 100.0)) == Nothing
    assert check_rent(create_row("other", 3000.0)) == Nothing

def test_check_home_decor():
    assert check_home_decor(create_row("online home items")) == Some("Home and Decor")
    assert check_home_decor(create_row("booom")) == Some("Home and Decor")
    assert check_home_decor(create_row("random", category="ריהוט ובית")) == Some("Home and Decor")
    assert check_home_decor(create_row("random")) == Nothing

def test_check_eating_out():
    assert check_eating_out(create_row("poalim wonder")) == Some("Eating Out")
    assert check_eating_out(create_row("מש - קר")) == Some("Eating Out")
    assert check_eating_out(create_row("wolt")) == Some("Eating Out")
    assert check_eating_out(create_row("random", category="מסעדות")) == Some("Eating Out")
    assert check_eating_out(create_row("random", category="מזון מהיר")) == Some("Eating Out")
    assert check_eating_out(create_row("random")) == Nothing

def test_check_education():
    assert check_education(create_row("udemy course")) == Some("Education and Learning")
    assert check_education(create_row("hit")) == Some("Education and Learning")
    assert check_education(create_row("סטימצקי")) == Some("Education and Learning")
    assert check_education(create_row("מכון אקדמי טכנולוגי חולון")) == Some("Education and Learning")
    assert check_education(create_row("random")) == Nothing

def test_check_transport():
    assert check_transport(create_row("pango")) == Some("Transport and Car")
    assert check_transport(create_row("פנגו")) == Some("Transport and Car")
    assert check_transport(create_row("רב-פס")) == Some("Transport and Car")
    assert check_transport(create_row("random", category="אנרגיה")) == Some("Transport and Car")
    assert check_transport(create_row("random", category="רכב ותחבורה")) == Some("Transport and Car")
    assert check_transport(create_row("random")) == Nothing

def test_check_appearance():
    assert check_appearance(create_row("fashion store")) == Some("Appearance and Grooming")
    assert check_appearance(create_row("barber")) == Some("Appearance and Grooming")
    assert check_appearance(create_row("random", category="אופנה")) == Some("Appearance and Grooming")
    assert check_appearance(create_row("random", category="טיוח ויופי")) == Some("Appearance and Grooming")
    assert check_appearance(create_row("random")) == Nothing

def test_check_vacation():
    assert check_vacation(create_row("hotel booking")) == Some("Vacation and Travel")
    assert check_vacation(create_row("airbnb")) == Some("Vacation and Travel")
    assert check_vacation(create_row("חו\"ל")) == Some("Vacation and Travel")
    assert check_vacation(create_row("חול")) == Some("Vacation and Travel")
    assert check_vacation(create_row("random")) == Nothing

def test_check_gifts():
    assert check_gifts(create_row("gift card")) == Some("Gifts and Charity")
    assert check_gifts(create_row("מתנה")) == Some("Gifts and Charity")
    assert check_gifts(create_row("תרומה")) == Some("Gifts and Charity")
    assert check_gifts(create_row("random")) == Nothing

def test_check_subscriptions():
    assert check_subscriptions(create_row("google")) == Some("Subscriptions")
    assert check_subscriptions(create_row("netflix")) == Some("Subscriptions")
    assert check_subscriptions(create_row("apple.com/bill")) == Some("Subscriptions")
    assert check_subscriptions(create_row("bitwarden")) == Some("Subscriptions")
    assert check_subscriptions(create_row("random", category="Subscriptions")) == Some("Subscriptions")
    assert check_subscriptions(create_row("random")) == Nothing

def test_check_electronics():
    assert check_electronics(create_row("gadget")) == Some("Electronics and Gadgets")
    assert check_electronics(create_row("ksp")) == Some("Electronics and Gadgets")
    assert check_electronics(create_row("קי.אס.פי.")) == Some("Electronics and Gadgets")
    assert check_electronics(create_row("random")) == Nothing

def test_check_groceries():
    assert check_groceries(create_row("קרמה +")) == Some("Groceries")
    assert check_groceries(create_row("random", category="מזון ומשקאות")) == Some("Groceries")
    assert check_groceries(create_row("random", category="מזון מהיר")) == Some("Groceries")
    assert check_groceries(create_row("random")) == Nothing

def test_check_government():
    assert check_government(create_row("עיריית")) == Some("Government & Municipal")
    assert check_government(create_row("random", category="מוסדות")) == Some("Government & Municipal")
    assert check_government(create_row("random")) == Nothing

def test_check_health():
    assert check_health(create_row("iherb")) == Some("Health and Cosmetics")
    assert check_health(create_row("random", category="רפואה ובריאות")) == Some("Health and Cosmetics")
    assert check_health(create_row("random")) == Nothing

def test_check_telecom():
    assert check_telecom(create_row("random", category="תקשורת ומחשבים")) == Some("Telecom")
    assert check_telecom(create_row("random")) == Nothing

def test_check_entertainment():
    assert check_entertainment(create_row("random", category="אירועים")) == Some("Entertainment and Fun")
    assert check_entertainment(create_row("random")) == Nothing

def test_map_category_integration():
    # Test the full chain with tricky cases
    
    # 1. Reimbursable (Negative amount)
    assert map_category(create_row("Wolt", -49.0, "מסעדות")) == "Reimbursable Expenses"
    
    # 2. Rent vs Misc (Paybox)
    # Paybox with large amount -> Rent
    assert map_category(create_row("Paybox", 3000.0, "שונות")) == "Rent and Utilities"
    assert map_category(create_row("Paybox", 850.0, "שונות")) == "Rent and Utilities"
    # Paybox with small amount and 'שונות' -> Misc (Default)
    assert map_category(create_row("Paybox", 50.0, "שונות")) == "Misc and One-offs"
    
    # 3. Bit (Misc)
    # Bit with 'שונות' -> Misc (Default)
    assert map_category(create_row("Bit", 100.0, "שונות")) == "Misc and One-offs"
    
    # 4. Hebrew Keywords
    assert map_category(create_row("מכון אקדמי טכנולוגי חולון", 1331.66, "מוסדות")) == "Education and Learning"
    assert map_category(create_row("הי ביז poalim wonder", 92.0, "תעשיה ומכירות")) == "Eating Out"
    assert map_category(create_row("IHERB IHERB.COM", 236.38, "מזון ומשקאות")) == "Health and Cosmetics"
    
    # 5. Subscriptions
    assert map_category(create_row("Google Our Groceries", 3.3, "תקשורת ומחשבים")) == "Subscriptions"
    assert map_category(create_row("Netflix", 50.0, "Unknown")) == "Subscriptions"
    
    # 6. Fallbacks
    assert map_category(create_row("Random Store", 100.0, "שונות")) == "Misc and One-offs"
    assert map_category(create_row("", 100.0, "")) == "Misc and One-offs"
    assert map_category(create_row("Random Store", 100.0, None)) == "Misc and One-offs"
    assert map_category(create_row("Random Store", 100.0, "nan")) == "Misc and One-offs"
    assert map_category(create_row("Random Store", 100.0, "NaN")) == "Misc and One-offs"
    
    # 7. Case Sensitivity
    assert map_category(create_row("wolt", 50.0, "Unknown")) == "Eating Out"
    assert map_category(create_row("WOLT", 50.0, "Unknown")) == "Eating Out"
