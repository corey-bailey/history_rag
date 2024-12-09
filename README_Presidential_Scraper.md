# Presidency Document Scraper

This Python project is a web scraper designed to automate the process of extracting and saving documents from a presidency archive website. The scraper uses Selenium for browser automation and BeautifulSoup for HTML parsing.

---

## Features

- **Automated Navigation**: Traverses through multiple pages of the website.
- **Document Extraction**: Collects and saves the content of each document, along with metadata like the publication date and title.
- **Error Handling**: Handles timeouts, missing elements, and other common web scraping issues gracefully.
- **Logging**: Logs progress and errors to a file (`scraping.log`) for easy debugging and tracking.
- **Filename Sanitization**: Ensures saved filenames are valid and readable.
- **Date Formatting**: Converts dates into a consistent `YYYY-MM-DD` format.

---

## Requirements

The scraper is built using Python and the following libraries:

- `selenium`: For browser automation.
- `bs4` (BeautifulSoup): For parsing HTML content.
- `datetime`: For date manipulation.
- `logging`: For tracking progress and errors.
- `os` and `re`: For file and string operations.
- `time`: For managing delays.

Install the required Python packages using:

```bash
pip install selenium beautifulsoup4