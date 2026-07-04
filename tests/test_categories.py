import pandas as pd
from src.core.categories import (
    map_category, 
    check_reimbursable, 
    check_rent, 
    check_keywords
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
    assert check_keywords(create_row("online home items"), "Home & Decor") == "Home & Decor"
    assert check_keywords(create_row("booom"), "Home & Decor") == "Home & Decor"
    assert check_keywords(create_row("random", category="ריהוט ובית"), "Home & Decor") == "Home & Decor"
    assert check_keywords(create_row("random"), "Home & Decor") is None

def test_check_eating_out():
    assert check_keywords(create_row("poalim wonder"), "Eating out") == "Eating out"
    assert check_keywords(create_row("מש - קר"), "Eating out") == "Eating out"
    assert check_keywords(create_row("wolt"), "Eating out") == "Eating out"
    assert check_keywords(create_row("random", category="מסעדות"), "Eating out") == "Eating out"
    assert check_keywords(create_row("random", category="מזון מהיר"), "Eating out") == "Eating out"
    assert check_keywords(create_row("random"), "Eating out") is None

def test_check_education():
    assert check_keywords(create_row("udemy course"), "Education & Learning") == "Education & Learning"
    assert check_keywords(create_row("hit"), "Education & Learning") == "Education & Learning"
    assert check_keywords(create_row("סטימצקי"), "Education & Learning") == "Education & Learning"
    assert check_keywords(create_row("מכון אקדמי טכנולוגי חולון"), "Education & Learning") == "Education & Learning"
    assert check_keywords(create_row("white hit"), "Education & Learning") is None
    assert check_keywords(create_row("random"), "Education & Learning") is None

def test_check_transport():
    assert check_keywords(create_row("pango"), "Transport & Car") == "Transport & Car"
    assert check_keywords(create_row("פנגו"), "Transport & Car") == "Transport & Car"
    assert check_keywords(create_row("רב-פס"), "Transport & Car") == "Transport & Car"
    assert check_keywords(create_row("random", category="אנרגיה"), "Transport & Car") == "Transport & Car"
    assert check_keywords(create_row("random", category="רכב ותחבורה"), "Transport & Car") == "Transport & Car"
    assert check_keywords(create_row("random"), "Transport & Car") is None

def test_check_appearance():
    assert check_keywords(create_row("fashion store"), "Appearance & Grooming") == "Appearance & Grooming"
    assert check_keywords(create_row("barber"), "Appearance & Grooming") == "Appearance & Grooming"
    assert check_keywords(create_row("random", category="אופנה"), "Appearance & Grooming") == "Appearance & Grooming"
    assert check_keywords(create_row("random", category="טיפוח ויופי"), "Appearance & Grooming") == "Appearance & Grooming"
    assert check_keywords(create_row("random"), "Appearance & Grooming") is None

def test_check_vacation():
    assert check_keywords(create_row("hotel booking"), "Vacation & Travel") == "Vacation & Travel"
    assert check_keywords(create_row("airbnb"), "Vacation & Travel") == "Vacation & Travel"
    assert check_keywords(create_row("חו\"ל"), "Vacation & Travel") == "Vacation & Travel"
    assert check_keywords(create_row("חול"), "Vacation & Travel") == "Vacation & Travel"
    assert check_keywords(create_row("random", category="תיירות"), "Vacation & Travel") == "Vacation & Travel"
    assert check_keywords(create_row("חולון"), "Vacation & Travel") is None
    assert check_keywords(create_row("random"), "Vacation & Travel") is None

def test_check_gifts():
    assert check_keywords(create_row("gift card"), "Gifts & Charity") == "Gifts & Charity"
    assert check_keywords(create_row("מתנה"), "Gifts & Charity") == "Gifts & Charity"
    assert check_keywords(create_row("תרומה"), "Gifts & Charity") == "Gifts & Charity"
    assert check_keywords(create_row("random"), "Gifts & Charity") is None

def test_check_subscriptions():
    assert check_keywords(create_row("google"), "Subscriptions") == "Subscriptions"
    assert check_keywords(create_row("netflix"), "Subscriptions") == "Subscriptions"
    assert check_keywords(create_row("apple.com/bill"), "Subscriptions") == "Subscriptions"
    assert check_keywords(create_row("bitwarden"), "Subscriptions") == "Subscriptions"
    assert check_keywords(create_row("random", category="Subscriptions"), "Subscriptions") == "Subscriptions"
    assert check_keywords(create_row("random"), "Subscriptions") is None

def test_check_electronics():
    assert check_keywords(create_row("gadget"), "Electronics & Gadgets") == "Electronics & Gadgets"
    assert check_keywords(create_row("ksp"), "Electronics & Gadgets") == "Electronics & Gadgets"
    assert check_keywords(create_row("קי.אס.פי."), "Electronics & Gadgets") == "Electronics & Gadgets"
    assert check_keywords(create_row("random"), "Electronics & Gadgets") is None

def test_check_groceries():
    assert check_keywords(create_row("קרמה +"), "Groceries") == "Groceries"
    assert check_keywords(create_row("random", category="מזון ומשקאות"), "Groceries") == "Groceries"
    assert check_keywords(create_row("random", category="מזון מהיר"), "Groceries") == "Groceries"
    assert check_keywords(create_row("random"), "Groceries") is None

def test_check_government():
    assert check_keywords(create_row("עיריית"), "Government & Municipal") == "Government & Municipal"
    assert check_keywords(create_row("random", category="מוסדות"), "Government & Municipal") == "Government & Municipal"
    assert check_keywords(create_row("random"), "Government & Municipal") is None

def test_check_health():
    assert check_keywords(create_row("iherb"), "Health & Cosmetics") == "Health & Cosmetics"
    assert check_keywords(create_row("random", category="רפואה ובריאות"), "Health & Cosmetics") == "Health & Cosmetics"
    assert check_keywords(create_row("random"), "Health & Cosmetics") is None

def test_check_telecom():
    assert check_keywords(create_row("random", category="תקשורת ומחשבים"), "Telecom") == "Telecom"
    assert check_keywords(create_row("random"), "Telecom") is None

def test_check_social_fun():
    assert check_keywords(create_row("random", category="אירועים"), "Social & Fun") == "Social & Fun"
    assert check_keywords(create_row("random", category="פנאי בילוי"), "Social & Fun") == "Social & Fun"
    assert check_keywords(create_row("schnitt"), "Social & Fun") == "Social & Fun"
    assert check_keywords(create_row("random"), "Social & Fun") is None

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
