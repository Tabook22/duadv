#!/usr/bin/env python3
"""
CLI Utility for Dhofar University Advisee & Transcript Management
"""

import argparse
import json
import os
import sys
import time
import zipfile
import base64

def get_webdriver(headless=True):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--ignore-ssl-errors=yes")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
        })
    except Exception:
        pass
    driver.implicitly_wait(10)
    return driver

def login_and_navigate(driver, username, password):
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.action_chains import ActionChains
    from bs4 import BeautifulSoup

    print(f"Navigating to Dhofar University SIS login...")
    driver.get("https://web.du.edu.om/ords/f?p=2023")
    
    u_elem = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, 'P101_USERNAME'))
    )
    p_elem = driver.find_element(By.ID, 'P101_PASSWORD')
    btn_elem = driver.find_element(By.CSS_SELECTOR, 'button.t-Button--hot, #B22523398111720799')
    
    actions = ActionChains(driver)
    actions.move_to_element(u_elem).click().send_keys(username).perform()
    time.sleep(0.5)
    actions.move_to_element(p_elem).click().send_keys(password).perform()
    time.sleep(0.5)
    actions.move_to_element(btn_elem).click().perform()
    
    # Wait for login
    WebDriverWait(driver, 15).until(
        lambda d: "login" not in d.current_url.lower() and "101" not in d.current_url
    )
    print(f"Logged in successfully. Current URL: {driver.current_url}")
    
    # Extract signed Advisor Student List link
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    target_href = None
    for a in soup.find_all('a'):
        txt = a.get_text(strip=True)
        href = a.get('href', '')
        if 'Advisor Student List' in txt or 'SIX_ADVISOR_STU_LST_NEW' in href or 'advisor-stu' in href:
            target_href = href
            break
            
    if target_href:
        full_url = target_href if target_href.startswith('http') else f"https://web.du.edu.om/ords/{target_href}"
        print(f"Navigating to Advisor Student List: {full_url}")
        driver.get(full_url)
        time.sleep(3)
    else:
        # Fallback click
        driver.execute_script("""
            var a = Array.from(document.querySelectorAll('a')).find(el => (el.innerText||'').includes('Advisor Student List'));
            if (a) a.click();
        """)
        time.sleep(3)

def extract_students(driver):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    students = []
    tables = soup.select('#advisee_data_panel table, table.a-IRR-table, table')
    
    for table in tables:
        for row in table.find_all('tr'):
            id_cell = row.find(['td', 'th'], {'headers': 'SAP_CODE'})
            if not id_cell:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    id_cell = cells[0]
            if id_cell:
                sid = id_cell.get_text().strip()
                if sid and any(c.isdigit() for c in sid):
                    name_cell = row.find(['td', 'th'], lambda h: h and 'C5454047' in str(h))
                    if not name_cell:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 2:
                            name_cell = cells[1]
                    sname = name_cell.get_text().strip() if name_cell else f"Student {sid}"
                    cells = row.find_all(['td', 'th'])
                    status = cells[2].get_text().strip() if len(cells) > 2 else 'Normal / Good Standing'
                    if not any(s['id'] == sid for s in students):
                        students.append({'id': sid, 'name': ' '.join(sname.split()), 'program': status})
    return students

def download_transcripts(driver, output_dir):
    from selenium.webdriver.common.by import By
    os.makedirs(output_dir, exist_ok=True)
    downloaded = []
    
    rows = driver.find_elements(By.CSS_SELECTOR, "#advisee_data_panel table tbody tr, table.a-IRR-table tbody tr")
    row_count = len(rows)
    print(f"Found {row_count} rows in advisee table.")
    
    for i in range(row_count):
        try:
            current_rows = driver.find_elements(By.CSS_SELECTOR, "#advisee_data_panel table tbody tr, table.a-IRR-table tbody tr")
            if i >= len(current_rows):
                break
            row = current_rows[i]
            
            id_cells = row.find_elements(By.CSS_SELECTOR, "td[headers='SAP_CODE'], td:first-child")
            student_id = id_cells[0].text.strip() if id_cells else f"student_{i+1}"
            if not student_id or not any(c.isdigit() for c in student_id):
                continue
                
            transcript_links = row.find_elements(By.XPATH, ".//a[contains(text(), 'Transcript') or contains(@href, 'transcript')]")
            if not transcript_links:
                continue
                
            main_window = driver.current_window_handle
            existing_windows = set(driver.window_handles)
            
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", transcript_links[0])
            time.sleep(3)
            
            new_windows = set(driver.window_handles) - existing_windows
            if new_windows:
                driver.switch_to.window(list(new_windows)[0])
                time.sleep(2)
                
            pdf_data = driver.execute_cdp_cmd("Page.printToPDF", {
                "printBackground": True,
                "paperWidth": 8.27,
                "paperHeight": 11.69,
                "preferCSSPageSize": True
            })
            
            pdf_bytes = base64.b64decode(pdf_data['data'])
            filepath = os.path.join(output_dir, f"{student_id}_transcript.pdf")
            with open(filepath, 'wb') as f:
                f.write(pdf_bytes)
                
            print(f"Saved: {filepath}")
            downloaded.append(filepath)
            
            if new_windows:
                driver.close()
                driver.switch_to.window(main_window)
            else:
                driver.back()
                time.sleep(2)
        except Exception as ex:
            print(f"Error on row {i}: {ex}")
            continue
            
    return downloaded

def main():
    parser = argparse.ArgumentParser(description="Dhofar University Advisee & Transcript Management CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Sync command
    sync_p = subparsers.add_parser("sync", help="Sync advisee student list")
    sync_p.add_argument("--username", required=True, help="DU Staff ID")
    sync_p.add_argument("--password", required=True, help="DU Portal Password")
    sync_p.add_argument("--output", default="data/students.json", help="Path to save students.json")
    
    # Transcripts command
    trans_p = subparsers.add_parser("transcripts", help="Download all advisee transcripts as PDF")
    trans_p.add_argument("--username", required=True, help="DU Staff ID")
    trans_p.add_argument("--password", required=True, help="DU Portal Password")
    trans_p.add_argument("--output-dir", default="data/transcripts", help="Directory to save PDFs")
    
    # All command
    all_p = subparsers.add_parser("all", help="Sync students and download transcripts")
    all_p.add_argument("--username", required=True, help="DU Staff ID")
    all_p.add_argument("--password", required=True, help="DU Portal Password")
    all_p.add_argument("--output-json", default="data/students.json")
    all_p.add_argument("--output-dir", default="data/transcripts")
    
    # Zip command
    zip_p = subparsers.add_parser("zip", help="Bundle downloaded PDFs into ZIP")
    zip_p.add_argument("--transcripts-dir", default="data/transcripts")
    zip_p.add_argument("--output-zip", default="data/advisee_transcripts.zip")
    
    args = parser.parse_args()
    
    if args.command == "zip":
        os.makedirs(os.path.dirname(args.output_zip), exist_ok=True)
        pdf_files = [f for f in os.listdir(args.transcripts_dir) if f.endswith('.pdf')]
        with zipfile.ZipFile(args.output_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
            for f in pdf_files:
                zf.write(os.path.join(args.transcripts_dir, f), arcname=f)
        print(f"Success! Bundled {len(pdf_files)} PDFs into: {args.output_zip}")
        return

    driver = get_webdriver(headless=True)
    try:
        login_and_navigate(driver, args.username, args.password)
        
        if args.command in ["sync", "all"]:
            students = extract_students(driver)
            os.makedirs(os.path.dirname(args.output or args.output_json), exist_ok=True)
            out_file = args.output if args.command == "sync" else args.output_json
            with open(out_file, 'w', encoding='utf-8') as f:
                json.dump(students, f, indent=2, ensure_ascii=False)
            print(f"Success! Extracted {len(students)} advisees to: {out_file}")
            
        if args.command in ["transcripts", "all"]:
            out_dir = args.output_dir
            downloaded = download_transcripts(driver, out_dir)
            print(f"Success! Downloaded {len(downloaded)} transcript PDFs to: {out_dir}")
            
    finally:
        driver.quit()

if __name__ == '__main__':
    main()
