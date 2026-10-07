"""University system web scraper"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from app.scraper.selectors import SELECTORS
from config import Config

class UniversitySystemManager:
    """Manages interaction with university web system"""
    
    def __init__(self):
        self.driver = None
        self.base_url = Config.UNIVERSITY_BASE_URL
        
    def setup_driver(self):
        """Setup Chrome driver with appropriate options"""
        chrome_options = Options()
        
        if Config.SELENIUM_HEADLESS:
            chrome_options.add_argument("--headless=new")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--ignore-ssl-errors=yes")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        try:
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
            })
        except Exception:
            pass
            
        self.driver.implicitly_wait(10)
        return self.driver
    
    def login_to_system(self, username, password, progress_callback=None):
        """Login to the university system with optional progress reporting"""
        try:
            if progress_callback:
                progress_callback(5, "Initializing", "Starting automated browser and preparing connection...")

            if not self.driver:
                self.setup_driver()
            
            if progress_callback:
                progress_callback(10, "Connecting", f"Connecting to Dhofar University portal ({self.base_url})...")

            self.driver.get(self.base_url)
            
            from selenium.webdriver.common.action_chains import ActionChains
            
            if progress_callback:
                progress_callback(15, "Authenticating", f"Entering advisor credentials for {username}...")

            u_elem = WebDriverWait(self.driver, Config.SELENIUM_TIMEOUT).until(
                EC.presence_of_element_located((By.ID, 'P101_USERNAME'))
            )
            p_elem = self.driver.find_element(By.ID, 'P101_PASSWORD')
            btn_elem = self.driver.find_element(By.CSS_SELECTOR, 'button.t-Button--hot, #B22523398111720799')
            
            # Scroll form into view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", u_elem)
            time.sleep(0.5)
            
            # Real user input simulation via ActionChains
            actions = ActionChains(self.driver)
            actions.move_to_element(u_elem).click().send_keys(username).perform()
            time.sleep(0.5)
            actions.move_to_element(p_elem).click().send_keys(password).perform()
            time.sleep(0.5)
            actions.move_to_element(btn_elem).click().perform()
            
            if progress_callback:
                progress_callback(20, "Verifying Login", "Verifying security session and waiting for portal redirection...")

            # Wait up to 10 seconds for successful redirect away from login page
            try:
                WebDriverWait(self.driver, 10).until(
                    lambda d: "login" not in d.current_url.lower() and "101" not in d.current_url
                )
                current_url = self.driver.current_url
                if progress_callback:
                    progress_callback(25, "Login Successful", f"Authenticated successfully as advisor {username}.")
                return {"status": "success", "message": "Login successful", "url": current_url}
            except Exception:
                pass
            
            # Check for specific APEX error dialog / messages on the page
            error_message = "Invalid login credentials according to university portal."
            try:
                dialogs = self.driver.find_elements(By.CSS_SELECTOR, ".ui-dialog-content, .t-Alert--danger, .a-Notification--error, .t-Alert-body, #P101_ERR_MSG")
                for elem in dialogs:
                    text = elem.text.strip()
                    if text and text != "APEX.DIALOG.OK":
                        error_message = f"University portal response: {text}"
                        break
            except Exception:
                pass
            
            # Save screenshot for debugging
            try:
                import os
                os.makedirs('logs', exist_ok=True)
                self.driver.save_screenshot('logs/login_attempt.png')
            except Exception:
                pass
                
            return {"status": "error", "message": error_message}
                
        except Exception as e:
            return {"status": "error", "message": f"Login error: {str(e)}"}
    
    def navigate_to_student_list(self, progress_callback=None):
        """Navigate to student/advisee list using parsed menu link with valid checksum"""
        try:
            if progress_callback:
                progress_callback(30, "Navigating", "Locating Advisor Student List link with valid session checksum...")

            # 1. Check if already on advisor student list
            if "SIX_ADVISOR_STU_LST" in self.driver.current_url or "400" in self.driver.current_url or ("advisor" in self.driver.current_url.lower() and "student" in self.driver.current_url.lower()):
                if progress_callback:
                    progress_callback(38, "Ready", "Already at Advisee Student List panel.")
                return {"status": "success", "message": "Already on student list"}

            # 2. Extract exact link with valid session checksum from page DOM
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            target_href = None
            
            for a in soup.find_all('a'):
                txt = a.get_text(strip=True)
                href = a.get('href', '')
                if 'Advisor Student List' in txt or 'SIX_ADVISOR_STU_LST_NEW' in href or 'advisor-stu' in href:
                    target_href = href
                    break
                    
            if target_href:
                if not target_href.startswith('http'):
                    if target_href.startswith('/'):
                        full_url = f"https://web.du.edu.om{target_href}"
                    else:
                        full_url = f"https://web.du.edu.om/ords/{target_href}"
                else:
                    full_url = target_href
                    
                if progress_callback:
                    progress_callback(34, "Loading Advisees", "Opening Advisor Student List with authenticated session token...")

                self.driver.get(full_url)
                time.sleep(3)
                
                # Wait for advisee table
                try:
                    WebDriverWait(self.driver, 15).until(
                        lambda d: d.find_elements(By.CSS_SELECTOR, "#advisee_data_panel, table.a-IRR-table, td[headers='SAP_CODE'], .a-IRR-reportView")
                    )
                    if progress_callback:
                        progress_callback(38, "Advisee List Ready", "Student roster table rendered successfully.")
                    return {"status": "success", "message": "Navigated to advisor student list"}
                except Exception:
                    pass
                    
            # 3. Fallback: JavaScript click on Advisor Student List
            if progress_callback:
                progress_callback(35, "Navigating Menu", "Invoking navigation fallback via DOM click...")

            click_js = """
            var elements = Array.from(document.querySelectorAll('a'));
            for (var i = 0; i < elements.length; i++) {
                var el = elements[i];
                var txt = (el.innerText || el.textContent || '').trim();
                var href = el.getAttribute('href') || '';
                if (txt === 'Advisor Student List' || href.includes('SIX_ADVISOR_STU_LST_NEW')) {
                    el.click();
                    return true;
                }
            }
            return false;
            """
            self.driver.execute_script(click_js)
            time.sleep(4)
            
            if self.driver.find_elements(By.CSS_SELECTOR, "#advisee_data_panel, table.a-IRR-table, td[headers='SAP_CODE'], .a-IRR-reportView"):
                if progress_callback:
                    progress_callback(38, "Advisee List Ready", "Navigated to advisor student list.")
                return {"status": "success", "message": "Navigated to advisor student list"}

            return {"status": "error", "message": f"Could not open Advisor Student List. Current URL: {self.driver.current_url}"}
            
        except Exception as e:
            return {"status": "error", "message": f"Navigation error: {str(e)}"}
    
    def extract_student_list(self, progress_callback=None):
        """Extract student data from current page"""
        try:
            if progress_callback:
                progress_callback(40, "Extracting Roster", "Parsing advisee records and academic standings from SIS portal...")

            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            students = self.extract_from_table(soup)
            if not students:
                students = self.extract_from_list(soup) or self.extract_from_divs(soup)
            
            if progress_callback:
                progress_callback(45, "Roster Extracted", f"Successfully extracted {len(students)} advisees from university records.")

            return {
                "status": "success", 
                "students": students, 
                "count": len(students),
                "message": f"Found {len(students)} students"
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Extraction error: {str(e)}"}
    
    def extract_from_table(self, soup):
        """Extract student data from table using SAP_CODE and name headers"""
        students = []
        tables = soup.select('#advisee_data_panel table, table.a-IRR-table, table.t-Report-report, table')
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                # Locate Student ID by SAP_CODE header or first numeric cell
                id_cell = row.find(['td', 'th'], {'headers': 'SAP_CODE'})
                if not id_cell:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        id_cell = cells[0]
                
                if id_cell:
                    student_id = id_cell.get_text().strip()
                    if student_id and any(c.isdigit() for c in student_id):
                        # Locate Student Name
                        name_cell = row.find(['td', 'th'], lambda h: h and 'C5454047' in str(h))
                        if not name_cell:
                            cells = row.find_all(['td', 'th'])
                            if len(cells) >= 2:
                                name_cell = cells[1]
                        
                        student_name = name_cell.get_text().strip() if name_cell else f"Student {student_id}"
                        
                        # Status / Program
                        col3_text = cells[2].get_text().strip() if len(cells) > 2 else None
                        col4_text = cells[3].get_text().strip() if len(cells) > 3 else None
                        
                        standing_val = None
                        program_val = None
                        for val in [col3_text, col4_text]:
                            if not val:
                                continue
                            if any(k in val.lower() for k in ['probation', 'standing', 'removal']):
                                standing_val = val
                            elif any(k in val.lower() for k in ['science', 'engineering', 'diploma', 'bachelor', 'master', 'arts', 'business', 'computer']):
                                program_val = val
                                
                        if not standing_val and col3_text:
                            standing_val = col3_text
                        if not program_val and col4_text:
                            program_val = col4_text
                            
                        # Clean up formatting
                        student_name = ' '.join(student_name.split())
                        
                        # Avoid duplicates
                        if not any(s['id'] == student_id for s in students):
                            students.append({
                                'id': student_id,
                                'name': student_name,
                                'status': standing_val or 'Normal / Good Standing',
                                'program': program_val or 'Computer Science'
                            })
        
        return students
    
    def extract_from_list(self, soup):
        """Extract student data from list elements"""
        return []
    
    def extract_from_divs(self, soup):
        """Extract student data from div containers"""
        return []
    
    def download_transcripts_as_pdf(self, output_dir='data/transcripts', progress_callback=None):
        """Click on Transcript link for each advisee student and export PDF via Chrome CDP"""
        import os, base64
        os.makedirs(output_dir, exist_ok=True)
        downloaded = []
        
        try:
            # Find all table rows
            rows = self.driver.find_elements(By.CSS_SELECTOR, "#advisee_data_panel table tbody tr, table.a-IRR-table tbody tr")
            row_count = len(rows)
            
            if progress_callback:
                progress_callback(48, "Starting Downloads", f"Preparing to download academic transcripts for {row_count} table entries...")

            for i in range(row_count):
                try:
                    # Refetch rows to prevent stale element references
                    current_rows = self.driver.find_elements(By.CSS_SELECTOR, "#advisee_data_panel table tbody tr, table.a-IRR-table tbody tr")
                    if i >= len(current_rows):
                        break
                    row = current_rows[i]
                    
                    # Extract Student ID
                    id_cells = row.find_elements(By.CSS_SELECTOR, "td[headers='SAP_CODE'], td:first-child")
                    student_id = id_cells[0].text.strip() if id_cells else f"student_{i+1}"
                    if not student_id or not any(c.isdigit() for c in student_id):
                        continue
                    
                    # Find Transcript link
                    transcript_links = row.find_elements(By.XPATH, ".//a[contains(text(), 'Transcript') or contains(@href, 'transcript')]")
                    if not transcript_links:
                        continue
                    
                    # Calculate sub-progress: from 48% to 85%
                    if progress_callback and row_count > 0:
                        pct = int(48 + (i / row_count) * 37)
                        progress_callback(pct, "Downloading Transcripts", f"Exporting official PDF transcript for student {student_id} ({i+1} of {row_count})...")

                    transcript_link = transcript_links[0]
                    main_window = self.driver.current_window_handle
                    existing_windows = set(self.driver.window_handles)
                    
                    # Click Transcript link
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", transcript_link)
                    time.sleep(3)
                    
                    # Handle new window / tab if opened
                    new_windows = set(self.driver.window_handles) - existing_windows
                    if new_windows:
                        self.driver.switch_to.window(list(new_windows)[0])
                        time.sleep(2)
                    
                    # Print to PDF using Chrome DevTools Protocol
                    pdf_data = self.driver.execute_cdp_cmd("Page.printToPDF", {
                        "printBackground": True,
                        "paperWidth": 8.27,
                        "paperHeight": 11.69,
                        "marginTop": 0.4,
                        "marginBottom": 0.4,
                        "marginLeft": 0.4,
                        "marginRight": 0.4,
                        "preferCSSPageSize": True
                    })
                    
                    pdf_bytes = base64.b64decode(pdf_data['data'])
                    filepath = os.path.join(output_dir, f"{student_id}_transcript.pdf")
                    with open(filepath, 'wb') as f:
                        f.write(pdf_bytes)
                    
                    downloaded.append({"id": student_id, "filepath": filepath})
                    
                    # Return to advisee list
                    if new_windows:
                        self.driver.close()
                        self.driver.switch_to.window(main_window)
                    else:
                        self.driver.back()
                        time.sleep(2)
                        
                except Exception as ex:
                    print(f"Error downloading transcript for student {i}: {ex}")
                    continue
                    
            if progress_callback:
                progress_callback(85, "Downloads Completed", f"Successfully exported {len(downloaded)} transcript PDFs.")

            return {"status": "success", "count": len(downloaded), "transcripts": downloaded}
            
        except Exception as e:
            return {"status": "error", "message": f"Transcript download failed: {str(e)}"}

    def navigate_to_section_schedule(self):
        """Navigate to Section Schedule page using menu link or DOM query"""
        try:
            # 1. Check if already on section schedule
            cur_url = self.driver.current_url.lower()
            if "section" in cur_url and "sched" in cur_url:
                return {"status": "success", "message": "Already on Section Schedule"}

            # 2. Look for Section Schedule link in DOM
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            target_href = None
            
            for a in soup.find_all('a'):
                txt = a.get_text(strip=True)
                href = a.get('href', '')
                if 'Section Schedule' in txt or 'SECTION_SCHEDULE' in href or 'sec_sched' in href.lower():
                    target_href = href
                    break
                    
            if target_href:
                if not target_href.startswith('http'):
                    if target_href.startswith('/'):
                        full_url = f"https://web.du.edu.om{target_href}"
                    else:
                        full_url = f"https://web.du.edu.om/ords/{target_href}"
                else:
                    full_url = target_href
                    
                self.driver.get(full_url)
                time.sleep(3)
                return {"status": "success", "message": "Navigated to Section Schedule"}

            # 3. Fallback: JavaScript click on Schedule -> Section Schedule
            click_js = """
            var elements = Array.from(document.querySelectorAll('a, button, span, li'));
            for (var i = 0; i < elements.length; i++) {
                var el = elements[i];
                var txt = (el.innerText || el.textContent || '').trim();
                if (txt === 'Section Schedule') {
                    el.click();
                    return true;
                }
            }
            return false;
            """
            self.driver.execute_script(click_js)
            time.sleep(4)
            return {"status": "success", "message": "Clicked Section Schedule"}
        except Exception as e:
            return {"status": "error", "message": f"Navigation error: {str(e)}"}

    def query_and_export_section_schedule(self, semester="Fall 2026-2027", output_pdf="data/policies/Section_Schedule_Fall_2026_2027.pdf"):
        """
        Click QUERY on Section Schedule page, parse offered courses table into structured data,
        and export high-resolution landscape PDF via Chrome DevTools Protocol.
        """
        import os, base64
        os.makedirs(os.path.dirname(output_pdf), exist_ok=True)
        
        try:
            # 1. Click QUERY button
            query_clicked = False
            try:
                buttons = self.driver.find_elements(By.XPATH, "//button[contains(., 'QUERY') or contains(., 'Query')] | //input[@value='QUERY' or @value='Query']")
                if buttons:
                    self.driver.execute_script("arguments[0].click();", buttons[0])
                    query_clicked = True
                    time.sleep(4)
            except Exception:
                pass
                
            if not query_clicked:
                self.driver.execute_script("""
                var btns = Array.from(document.querySelectorAll('button, input[type="button"], input[type="submit"]'));
                for (var b of btns) {
                    var val = (b.value || b.innerText || b.textContent || '').trim().toUpperCase();
                    if (val === 'QUERY') {
                        b.click();
                        return true;
                    }
                }
                return false;
                """)
                time.sleep(4)
                
            time.sleep(2)
            
            # 2. Parse HTML table rows
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            sections = []
            
            tables = soup.find_all('table')
            target_table = None
            for tbl in tables:
                headers = [th.get_text(strip=True).upper() for th in tbl.find_all(['th', 'td'])]
                if any('CRS.#' in h or 'TITLE' in h or 'SECTION' in h or 'INSTRUCTOR' in h for h in headers):
                    target_table = tbl
                    break
                    
            if target_table:
                rows = target_table.find_all('tr')
                current_crs_code = ""
                current_title = ""
                current_credits = "3"

                for row in rows:
                    cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
                    if len(cells) >= 8 and not any('CRS.#' in c.upper() for c in cells):
                        crs_code = cells[0] if len(cells) > 0 else ""
                        title = cells[1] if len(cells) > 1 else ""
                        credits = cells[2] if len(cells) > 2 else ""
                        sec_num = cells[3] if len(cells) > 3 else "1"
                        session_type = cells[4] if len(cells) > 4 else "Morning"
                        lang = cells[5] if len(cells) > 5 else "English"
                        cap = cells[6] if len(cells) > 6 else "30"
                        enr = cells[7] if len(cells) > 7 else "0"
                        instructor = cells[8] if len(cells) > 8 else "TBA"
                        room = cells[9] if len(cells) > 9 else "TBA"
                        days = cells[10] if len(cells) > 10 else "TBA"
                        time_slot = cells[11] if len(cells) > 11 else "TBA"
                        remark = cells[12] if len(cells) > 12 else ""

                        # If course code is provided, update current course context
                        if crs_code and any(c.isdigit() for c in crs_code):
                            current_crs_code = crs_code
                            current_title = title
                            current_credits = credits if credits else "3"
                        
                        # Use active course context if current row is an additional section
                        if current_crs_code and sec_num:
                            sections.append({
                                'course_code': current_crs_code,
                                'title': current_title,
                                'credits': int(current_credits) if str(current_credits).isdigit() else 3,
                                'section': sec_num,
                                'session_type': session_type or "Morning",
                                'language': lang or "English",
                                'capacity': int(cap) if str(cap).isdigit() else 30,
                                'enrolled': int(enr) if str(enr).isdigit() else 0,
                                'instructor': instructor,
                                'room': room,
                                'days': days,
                                'time': time_slot,
                                'remark': remark,
                                'semester': semester
                            })
                            
            # 3. Print to high-resolution landscape PDF via Chrome DevTools Protocol
            pdf_data = self.driver.execute_cdp_cmd("Page.printToPDF", {
                "printBackground": True,
                "paperWidth": 11.69,   # A4 Landscape width
                "paperHeight": 8.27,   # A4 Landscape height
                "marginTop": 0.3,
                "marginBottom": 0.3,
                "marginLeft": 0.3,
                "marginRight": 0.3,
                "preferCSSPageSize": True
            })
            
            pdf_bytes = base64.b64decode(pdf_data['data'])
            with open(output_pdf, 'wb') as f:
                f.write(pdf_bytes)
                
            return {
                "status": "success",
                "count": len(sections),
                "pdf_path": output_pdf,
                "sections": sections
            }
        except Exception as e:
            return {"status": "error", "message": f"Section schedule export failed: {str(e)}"}
    
    def close_driver(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
