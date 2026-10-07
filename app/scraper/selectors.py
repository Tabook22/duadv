"""CSS and XPath selectors for university system"""

# Dhofar University Oracle APEX & Standard Selectors
SELECTORS = {
    # Login page selectors
    'username_field': "//input[@id='P101_USERNAME'] | //input[@type='text' and not(@type='hidden')]",
    'password_field': "//input[@id='P101_PASSWORD'] | //input[@type='password' and not(@type='hidden')]",
    'login_button': "//button[contains(@class, 't-Button--hot') or contains(., 'Sign In') or @type='submit'] | //input[@type='submit']",
    
    # Navigation selectors
    'menu_button': "//button[@id='t_Button_navControl'] | //button[contains(@class, 't-Header-navBtn')]",
    'student_list_links': [
        "//span[contains(text(), 'Advisor Student List')]/ancestor::a",
        "//a[contains(@href, 'six-advisor-stu-lst-new')]",
        "//a[contains(@href, 'SIX_ADVISOR_STU')]",
        "//a[contains(@class, 'a-Menu-label') and contains(., 'Advisor Student List')]",
        "//a[contains(@class, 't-MegaMenu-labelWrap') and contains(., 'Advisor Student List')]",
        "//span[contains(@class, 't-MegaMenu-label') and contains(text(), 'Advisor Student List')]/ancestor::a",
        "//a[contains(text(), 'Advisor Student List')]",
        "//a[contains(@href, 'advisor-student-list')]",
        "//a[contains(text(), 'Advisee Student List')]"
    ],
    
    # Student data selectors
    'student_table': "//div[@id='advisee_data_panel']//table | //table[contains(@class, 'a-IRR-table')] | //table[contains(@class, 't-Report-report')]",
    'student_rows': ".//tr[position()>1]",  # Skip header row
    'student_id_cell': ".//td[@headers='SAP_CODE'] | .//td[1] | .//th[1]",
    'student_name_cell': ".//td[contains(@headers, 'C54540470')] | .//td[2] | .//th[2]",
    'transcript_link': ".//a[contains(text(), 'Transcript')] | .//a[contains(@href, 'transcript')]"
}

# CSS selectors as backup
CSS_SELECTORS = {
    'username_field': '#P101_USERNAME, input[name="P101_USERNAME"], input[name="username"], #username, input[type="text"]',
    'password_field': '#P101_PASSWORD, input[name="P101_PASSWORD"], input[name="password"], #password, input[type="password"]',
    'login_button': 'button.t-Button--hot, button[type="submit"], input[type="submit"], button:contains("Sign In")'
}

