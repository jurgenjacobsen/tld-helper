# TLD Helper 🌐
An interactive CLI tool to manage and explore Top-Level Domains (TLDs). It allows you to fetch official IANA lists, filter for buyable suffixes using the Public Suffix List, and perform WHOIS lookups.

## Features
*   **Interactive CLI**: Navigate options using arrow keys and enter.
*   **All TLDs**: Fetches the latest official TLD list from IANA.
*   **Buyable TLDs**: Filters the Public Suffix List to identify potentially registrable domains (excluding private/internal suffixes).
*   **WHOIS Lookup**: Quick domain registration checks directly from the menu.
*   **Auto-Updates**: Integrated GitHub Action keeps the `all_tlds.txt` and `buyable_tlds.txt` updated automatically.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/jurgenjacobsen/tld-helper.git
    cd tld-helper
    ```

2.  **Install dependencies**:
    ```bash
        pip install -r requirements.txt
    ```

## Usage
Run the main script to start the interactive menu:

```bash
python main.py
```

### Menu Options:
*   `Look for all available TLD domains`: Downloads the official IANA list to `all_tlds.txt`.
*   `Look for buyable TLD domains`: Filters the Public Suffix List and saves to `buyable_tlds.txt`.
*   `Run WHOIS`: Enter a domain to see its registration data.

## Automation
This repository uses GitHub Actions to automatically refresh the TLD lists every week. This ensures that `all_tlds.txt` and `buyable_tlds.txt` are always up to date with the latest registry changes.

## License
MIT
