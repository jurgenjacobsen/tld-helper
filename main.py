import urllib.request
import whois
import questionary
import sys

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
            restricted = ['gov', 'mil', 'edu', 'int', 'arpa', 'local', 'test', 'example', 'invalid']
            if any(clean_tld == r or clean_tld.endswith('.' + r) for r in restricted):
                continue

            buyable.append(clean_tld)

        buyable = sorted(list(set(buyable)))
        with open(filename, "w", encoding="utf-8") as f:
            for tld in buyable:
                f.write(f"{tld}\n")

        print(f"Done! {len(buyable)} potentially buyable suffixes saved to {filename}")

    except Exception as e:
        print(f"Error filtering buyable TLDs: {e}")

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
                "Run WHOIS",
                "Exit"
            ]
        ).ask()

        if choice == "Look for all available TLD domains":
            get_all_tlds()
        elif choice == "Look for buyable TLD domains":
            get_buyable_tlds()
        elif choice == "Run WHOIS":
            run_whois()
        elif choice == "Exit":
            print("Goodbye!")
            break
        
        print("\n") # Add some space before the menu appears again

if __name__ == "__main__":
    main_menu()
