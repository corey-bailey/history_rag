from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import time
import logging
import os
import re
from datetime import datetime

class PresidencyDocumentScraper:
    def __init__(self):
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename='scraping.log'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize the webdriver
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)
        
        # Create output directory if it doesn't exist
        self.output_dir = "presidential_documents"
        os.makedirs(self.output_dir, exist_ok=True)

    def convert_date_format(self, date_str):
        """Convert date from 'Month DD, YYYY' to 'YYYY-MM-DD' format"""
        try:
            # Parse the date string
            date_obj = datetime.strptime(date_str, '%B %d, %Y')
            # Return formatted date
            return date_obj.strftime('%Y-%m-%d')
        except ValueError as e:
            self.logger.error(f"Error parsing date '{date_str}': {str(e)}")
            return "0000-00-00"
        
    def sanitize_filename(self, filename):
        """Remove invalid characters from filename"""
        # Replace invalid filename characters with underscores
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove or replace any other problematic characters
        sanitized = sanitized.replace('\n', ' ').replace('\r', ' ')
        # Limit filename length
        return sanitized[:240] if len(sanitized) > 240 else sanitized
        
    def start_scraping(self, base_url):
        """Main scraping function that coordinates the entire process"""
        try:
            self.driver.get(base_url)
            current_page = 1
            
            while True:
                self.logger.info(f"Processing page {current_page}")
                
                # Get all document links on current page
                document_links = self.get_document_links()
                
                # Process each document on the current page
                for link in document_links:
                    try:
                        # Store the link text before clicking
                        link_text = link.text.strip()
                        
                        # Click the document link
                        link.click()
                        time.sleep(2)  # Wait for page to load
                        
                        # Extract and save document information
                        self.extract_and_save_document(link_text)
                        
                        # Go back to the list
                        self.driver.back()
                        time.sleep(2)  # Wait for page to load
                        
                    except Exception as e:
                        self.logger.error(f"Error processing document: {str(e)}")
                        self.driver.get(base_url + f"?page={current_page}")
                        continue
                
                # Try to go to next page
                if not self.go_to_next_page():
                    break
                    
                current_page += 1
                
        except Exception as e:
            self.logger.error(f"Fatal error: {str(e)}")
        finally:
            self.cleanup()
            
    def get_document_links(self):
        """Get all document links on the current page"""
        try:
            links = self.wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, ".views-field-title a")
                )
            )
            return links
        except TimeoutException:
            self.logger.error("Timeout waiting for document links")
            return []
            
    def extract_and_save_document(self, link_text):
        """Extract information from the document page and save to file"""
        try:
            # Wait for content to load
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "field-docs-content"))
            )
            
            # Get document metadata
            try:
                date_element = self.driver.find_element(By.CLASS_NAME, "date-display-single")
                date = date_element.text.strip()
                formatted_date = self.convert_date_format(date)
            except NoSuchElementException:
                date = "NO_DATE"
                formatted_date = "0000-00-00"
            
            # Create filename using date and title
            filename = f"{formatted_date}_{self.sanitize_filename(link_text)}.txt"
            filepath = os.path.join(self.output_dir, filename)
            
            # Get the main content
            try:
                content_element = self.driver.find_element(By.CLASS_NAME, "field-docs-content")
                content = content_element.text
            except NoSuchElementException:
                content = "NO CONTENT FOUND"
            
            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Date: {date}\n")
                f.write(f"Title: {link_text}\n")
                f.write("="*80 + "\n\n")
                f.write(content)
            
            self.logger.info(f"Saved document to: {filename}")
            
        except TimeoutException:
            self.logger.error("Timeout waiting for document content")
        except Exception as e:
            self.logger.error(f"Error saving document: {str(e)}")
            
    def go_to_next_page(self):
        """Attempt to go to the next page of results"""
        try:
            next_link = self.driver.find_element(
                By.CSS_SELECTOR, "a[title='Go to next page']"
            )
            next_link.click()
            time.sleep(2)  # Wait for page to load
            return True
        except NoSuchElementException:
            self.logger.info("No more pages to process")
            return False
            
    def cleanup(self):
        """Clean up resources"""
        try:
            self.driver.quit()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")

if __name__ == "__main__":
    BASE_URL = "https://www.presidency.ucsb.edu/people/president/george-w-bush"
    scraper = PresidencyDocumentScraper()
    scraper.start_scraping(BASE_URL)