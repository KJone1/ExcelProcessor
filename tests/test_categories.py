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

def create_row(payee="", amount=0.0, category="Unknown"):
    return pd.Series({"Payee": payee, "Amount": amount, "Category": category})

def test_check_reimbursable():
    assert check_reimbursable(create_row("some expense", -50.0)) == "Reimburseable"
    assert check_reimbursable(create_row("work expenses", 50.0)) == "Reimburseable"
    assert check_reimbursable(create_row("shared bills", 100.0)) == "Reimburseable"
    assert check_reimbursable(create_row("normal expense", 50.0)) is None

def test_check_rent():
    assert check_rent(create_row("paybox", 3000.0)) == "Home & Decor"
    assert check_rent(create_row("paybox", 850.0)) == "Home & Decor"
    assert check_rent(create_row("paybox", 100.0)) is None
    assert check_rent(create_row("other", 3000.0)) is None

def test_check_home_decor():
    assert check_home_decor(create_row("online home items")) == "Home & Decor"
    assert check_home_decor(create_row("booom")) == "Home & Decor"
    assert check_home_decor(create_row("random", category="ריהוט ובית")) == "Home & Decor"
    assert check_home_decor(create_row("random")) is None

def test_check_eating_out():
    assert check_eating_out(create_row("poalim wonder")) == "Eating out"
    assert check_eating_out(create_row("מש - קר")) == "Eating out"
    assert check_eating_out(create_row("wolt")) == "Eating out"
    assert check_eating_out(create_row("random", category="מסעדות")) == "Eating out"
    assert check_eating_out(create_row("random", category="מזון מהיר")) == "Eating out"
    assert check_eating_out(create_row("random")) is None

def test_check_education():
    assert check_education(create_row("udemy course")) == "Education & Learning"
    assert check_education(create_row("hit")) == "Education & Learning"
    assert check_education(create_row("סטימצקי")) == "Education & Learning"
    assert check_education(create_row("מכון אקדמי טכנולוגי חולון")) == "Education & Learning"
    assert check_education(create_row("random")) is None

def test_check_transport():
    assert check_transport(create_row("pango")) == "Transport & Car"
    assert check_transport(create_row("פנגו")) == "Transport & Car"
    assert check_transport(create_row("רב-פס")) == "Transport & Car"
    assert check_transport(create_row("random", category="אנרגיה")) == "Transport & Car"
    assert check_transport(create_row("random", category="רכב ותחבורה")) == "Transport & Car"
    assert check_transport(create_row("random")) is None

def test_check_appearance():
    assert check_appearance(create_row("fashion store")) == "Appearance & Grooming"
    assert check_appearance(create_row("barber")) == "Appearance & Grooming"
    assert check_appearance(create_row("random", category="אופנה")) == "Appearance & Grooming"
    assert check_appearance(create_row("random", category="טיוח ויופי")) == "Appearance & Grooming"
    assert check_appearance(create_row("random")) is None

def test_check_vacation():
    assert check_vacation(create_row("hotel booking")) == "Vacation & Travel"
    assert check_vacation(create_row("airbnb")) == "Vacation & Travel"
    assert check_vacation(create_row("חו\"ל")) == "Vacation & Travel"
    assert check_vacation(create_row("חול")) == "Vacation & Travel"
    assert check_vacation(create_row("random")) is None

def test_check_gifts():
    assert check_gifts(create_row("gift card")) == "Gifts & Charity"
    assert check_gifts(create_row("מתנה")) == "Gifts & Charity"
    assert check_gifts(create_row("תרומה")) == "Gifts & Charity"
    assert check_gifts(create_row("random")) is None

def test_check_subscriptions():
    assert check_subscriptions(create_row("google")) == "Subscriptions"
    assert check_subscriptions(create_row("netflix")) == "Subscriptions"
    assert check_subscriptions(create_row("apple.com/bill")) == "Subscriptions"
    assert check_subscriptions(create_row("bitwarden")) == "Subscriptions"
    assert check_subscriptions(create_row("random", category="Subscriptions")) == "Subscriptions"
    assert check_subscriptions(create_row("random")) is None

def test_check_electronics():
    assert check_electronics(create_row("gadget")) == "Electronics & Gadgets"
    assert check_electronics(create_row("ksp")) == "Electronics & Gadgets"
    assert check_electronics(create_row("קי.אס.פי.")) == "Electronics & Gadgets"
    assert check_electronics(create_row("random")) is None

def test_check_groceries():
    assert check_groceries(create_row("קרמה +")) == "Groceries"
    assert check_groceries(create_row("random", category="מזון ומשקאות")) == "Groceries"
    assert check_groceries(create_row("random", category="מזון מהיר")) == "Groceries"
    assert check_groceries(create_row("random")) is None

def test_check_government():
    assert check_government(create_row("עיריית")) == "Government & Municipal"
    assert check_government(create_row("random", category="מוסדות")) == "Government & Municipal"
    assert check_government(create_row("random")) is None

def test_check_health():
    assert check_health(create_row("iherb")) == "Health & Cosmetics"
    assert check_health(create_row("random", category="רפואה ובריאות")) == "Health & Cosmetics"
    assert check_health(create_row("random")) is None

def test_check_telecom():
    assert check_telecom(create_row("random", category="תקשורת ומחשבים")) == "Telecom"
    assert check_telecom(create_row("random")) is None

def test_check_entertainment():
    assert check_entertainment(create_row("random", category="אירועים")) == "Entertainment & Events"
    assert check_entertainment(create_row("random")) is None

def test_map_category_integration():
    # Test the full chain with tricky cases
    
    # 1. Reimbursable (Negative amount)
    assert map_category(create_row("Wolt", -49.0, "מסעדות")) == "Reimburseable"
    
    # 2. Rent vs Misc (Paybox)
    # Paybox with large amount -> Rent
    assert map_category(create_row("Paybox", 3000.0, "שונות")) == "Home & Decor"
    assert map_category(create_row("Paybox", 850.0, "שונות")) == "Home & Decor"
    # Paybox with small amount and 'שונות' -> Misc (Default)
    assert map_category(create_row("Paybox", 50.0, "שונות")) == "Misc & One-offs"
    
    # 3. Bit (Misc)
    # Bit with 'שונות' -> Misc (Default)
    assert map_category(create_row("Bit", 100.0, "שונות")) == "Misc & One-offs"
    
    # 4. Hebrew Keywords
    assert map_category(create_row("מכון אקדמי טכנולוגי חולון", 1331.66, "מוסדות")) == "Education & Learning"
    assert map_category(create_row("הי ביז poalim wonder", 92.0, "תעשיה ומכירות")) == "Eating out"
    assert map_category(create_row("IHERB IHERB.COM", 236.38, "מזון ומשקאות")) == "Health & Cosmetics"
    
    # 5. Subscriptions
    assert map_category(create_row("Google Our Groceries", 3.3, "תקשורת ומחשבים")) == "Subscriptions"
    assert map_category(create_row("Netflix", 50.0, "Unknown")) == "Subscriptions"
    
    # 6. Fallbacks
    assert map_category(create_row("Random Store", 100.0, "שונות")) == "Misc & One-offs"
    assert map_category(create_row("", 100.0, "")) == "Misc & One-offs"
    assert map_category(create_row("Random Store", 100.0, None)) == "Misc & One-offs"
    assert map_category(create_row("Random Store", 100.0, "nan")) == "Misc & One-offs"
    assert map_category(create_row("Random Store", 100.0, "NaN")) == "Misc & One-offs"
    
    # 7. Case Sensitivity
    assert map_category(create_row("wolt", 50.0, "Unknown")) == "Eating out"
    assert map_category(create_row("WOLT", 50.0, "Unknown")) == "Eating out"
