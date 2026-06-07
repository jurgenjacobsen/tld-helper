import urllib.request
import whois
import questionary
import sys
import os
import random

def get_all_tlds(filename="all_tlds.txt"):
    """Fetches all official IANA TLDs."""
    iana_txt_url = "https://data.iana.org/TLD/tlds-alpha-by-domain.txt"
    print("Fetching all available TLDs from IANA...")
    try:
        req = urllib.request.Request(iana_txt_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = response.read().decode('utf-8')
        
        # Skip the comment line
        tlds = [line.strip().lower() for line in data.splitlines() if not line.startswith('#')]
        
        with open(filename, "w", encoding="utf-8") as f:
            for tld in tlds:
                f.write(f"{tld}\n")
        
        print(f"Done! {len(tlds)} TLDs saved to {filename}")
    except Exception as e:
        print(f"Error fetching all TLDs: {e}")

def get_buyable_tlds(filename="buyable_tlds.txt"):
    """Fetches and filters buyable TLDs from the Public Suffix List."""
    psl_url = "https://publicsuffix.org/list/public_suffix_list.dat"
    print("Fetching and filtering buyable TLDs...")
    
    try:
        req = urllib.request.Request(psl_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            psl_data = response.read().decode('utf-8')

        buyable = []
        is_private_section = False

        for line in psl_data.splitlines():
            line = line.strip()
            if "===BEGIN PRIVATE DOMAINS===" in line:
                is_private_section = True
                continue
            
            if not line or line.startswith('//') or is_private_section:
                continue

            clean_tld = line.lstrip('*').lstrip('!').lstrip('.')
            restricted = {'gov', 'mil', 'edu', 'int', 'arpa', 'local', 'test', 'example', 'invalid'}
            tld_parts = clean_tld.split('.')
            if any(part in restricted for part in tld_parts):
                continue

            buyable.append(clean_tld)

        buyable = sorted(list(set(buyable)))
        with open(filename, "w", encoding="utf-8") as f:
            for tld in buyable:
                f.write(f"{tld}\n")

        print(f"Done! {len(buyable)} potentially buyable suffixes saved to {filename}")

    except Exception as e:
        print(f"Error filtering buyable TLDs: {e}")

def generate_domains_with_word():
    """Prepends a custom word to all buyable TLDs and allows the user to analyze them."""
    word = questionary.text("Enter the word you want to prepend (e.g., 'mybrand'):").ask()
    if not word:
        print("No word entered. Returning to main menu.")
        return
    
    word = word.strip().lower()
    
    filename = "buyable_tlds.txt"
    if not os.path.exists(filename):
        print(f"'{filename}' not found. Fetching and filtering buyable TLDs first...")
        get_buyable_tlds(filename)
        if not os.path.exists(filename):
            print("Failed to generate buyable TLDs. Aborting.")
            return

    try:
        with open(filename, "r", encoding="utf-8") as f:
            tlds = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return

    domains = [f"{word}.{tld}" for tld in tlds]
    output_filename = f"{word}_domains.txt"
    
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            for domain in domains:
                f.write(f"{domain}\n")
        print(f"\nSaved {len(domains)} generated domains to {output_filename}")
    except Exception as e:
        print(f"Error saving generated domains: {e}")
        return

    # Show a random preview of 15 domains
    preview_count = min(15, len(domains))
    preview = random.sample(domains, preview_count)
    print(f"\n--- Random Preview of {preview_count} Domains ---")
    for d in sorted(preview):
        print(f"  {d}")
    print("-------------------------------------------\n")

    # Interactive filtering/searching
    while True:
        action = questionary.select(
            "What would you like to do with the generated list?",
            choices=[
                "Filter domains by keyword/extension",
                "Show more random examples",
                "Run WHOIS on one of these domains",
                "Back to main menu"
            ]
        ).ask()

        if action == "Filter domains by keyword/extension":
            query = questionary.text("Enter keyword or suffix to filter by (e.g. '.co', 'ai', 'app'):").ask()
            if query:
                query = query.strip().lower()
                filtered = [d for d in domains if query in d]
                print(f"\nFound {len(filtered)} matching domains:")
                # Limit console output to 50 items to prevent flooding
                for d in filtered[:50]:
                    print(f"  {d}")
                if len(filtered) > 50:
                    print(f"  ... and {len(filtered) - 50} more (see {output_filename} for the full list)")
                print()
        elif action == "Show more random examples":
            preview = random.sample(domains, preview_count)
            print(f"\n--- Random Preview of {preview_count} Domains ---")
            for d in sorted(preview):
                print(f"  {d}")
            print("-------------------------------------------\n")
        elif action == "Run WHOIS on one of these domains":
            domain_to_check = questionary.text("Enter the specific domain to run WHOIS on:").ask()
            if domain_to_check:
                domain_to_check = domain_to_check.strip().lower()
                print(f"Running WHOIS for {domain_to_check}...")
                try:
                    w = whois.whois(domain_to_check)
                    print("\n--- WHOIS Result ---")
                    print(w)
                    print("--------------------\n")
                except Exception as e:
                    print(f"WHOIS Error: {e}")
        else:
            break

def run_whois():
    """Prompts for a domain and runs a WHOIS lookup."""
    domain = questionary.text("Enter the domain to lookup (e.g., google.com):").ask()
    if domain:
        print(f"Running WHOIS for {domain}...")
        try:
            w = whois.whois(domain)
            print("\n--- WHOIS Result ---")
            print(w)
            print("--------------------\n")
        except Exception as e:
            print(f"WHOIS Error: {e}")

def main_menu():
    """Main interactive menu."""
    while True:
        choice = questionary.select(
            "What would you like to do?",
            choices=[
                "Look for all available TLD domains",
                "Look for buyable TLD domains",
                "Generate domains by prepending a word to buyable TLDs",
                "Run WHOIS",
                "Exit"
            ]
        ).ask()

        if choice == "Look for all available TLD domains":
            get_all_tlds()
        elif choice == "Look for buyable TLD domains":
            get_buyable_tlds()
        elif choice == "Generate domains by prepending a word to buyable TLDs":
            generate_domains_with_word()
        elif choice == "Run WHOIS":
            run_whois()
        elif choice == "Exit":
            print("Goodbye!")
            break
        
        print("\n") # Add some space before the menu appears again

if __name__ == "__main__":
    if "--cli" in sys.argv:
        main_menu()
    else:
        try:
            from tui import TLDHelperTUI
            app = TLDHelperTUI()
            app.run()
        except Exception as e:
            print(f"Error starting TUI, falling back to CLI: {e}")
            main_menu()
