import os
import asyncio
import random
import whois
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Input, Button, Label, OptionList, RichLog
from textual.worker import get_current_worker

# Import existing functions from main
from main import get_all_tlds, get_buyable_tlds

class TLDHelperTUI(App):
    TITLE = "TLD Helper & Domain Analyzer"
    SUBTITLE = "Analyze, Prepend, Filter, and WHOIS"
    
    # CSS Styling
    CSS = """
    Screen {
        background: #121820;
        color: #e2e8f0;
    }
    
    #main-layout {
        height: 1fr;
    }
    
    #sidebar {
        width: 35;
        background: #1a2332;
        border-right: solid #2e3e56;
        padding: 1 2;
    }
    
    #center-panel {
        width: 45%;
        background: #151d2a;
        border-right: solid #2e3e56;
        padding: 1 2;
    }
    
    #right-panel {
        width: 1fr;
        background: #121820;
        padding: 1 2;
    }
    
    .panel-title {
        text-style: bold;
        color: #38bdf8;
        margin-bottom: 1;
    }
    
    .section-label {
        text-style: bold;
        color: #94a3b8;
        margin-top: 1;
        margin-bottom: 0;
    }
    
    Input {
        background: #0f172a;
        border: tall #334155;
        color: #f8fafc;
        margin-bottom: 1;
    }
    
    Input:focus {
        border: tall #38bdf8;
    }
    
    Button {
        width: 100%;
        margin-bottom: 1;
        height: 3;
        background: #1e293b;
        color: #e2e8f0;
        border: none;
    }
    
    Button:hover {
        background: #334155;
        color: #ffffff;
    }
    
    Button.-active {
        background: #38bdf8;
        color: #0f172a;
    }
    
    Button.primary {
        background: #0284c7;
        color: #ffffff;
    }
    
    Button.primary:hover {
        background: #0369a1;
    }
    
    Button.success {
        background: #16a34a;
        color: #ffffff;
    }
    
    Button.success:hover {
        background: #15803d;
    }
    
    #domain-list {
        background: #0f172a;
        border: solid #2e3e56;
        height: 1fr;
    }
    
    #details-log {
        background: #0b0f19;
        border: solid #2e3e56;
        height: 1fr;
        padding: 1;
        color: #f1f5f9;
    }
    
    #status-log {
        background: #0f172a;
        border: solid #334155;
        height: 8;
        padding: 0 1;
        color: #94a3b8;
        margin-top: 1;
    }
    """
    
    BINDINGS = [
        ("q", "quit", "Quit App"),
        ("ctrl+s", "save_list", "Save List"),
        ("ctrl+w", "trigger_whois", "Run WHOIS"),
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_tlds = []
        self.current_domains = []
        
    def on_mount(self) -> None:
        self.load_buyable_tlds()
        self.log_status("App started. Press 'q' to quit.")
        
    def load_buyable_tlds(self) -> None:
        filename = "buyable_tlds.txt"
        if os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    self.base_tlds = [line.strip() for line in f if line.strip()]
                self.log_status(f"Loaded {len(self.base_tlds)} buyable TLDs.")
                self.update_domain_list()
            except Exception as e:
                self.log_status(f"Error loading TLDs: {e}")
        else:
            self.log_status("buyable_tlds.txt not found. Please click 'Fetch Buyable TLDs'.")
            
    def log_status(self, message: str) -> None:
        log_widget = self.query_one("#status-log", RichLog)
        log_widget.write(message)
        
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        with Horizontal(id="main-layout"):
            # Left Sidebar
            with Vertical(id="sidebar"):
                yield Label("CONTROLS", classes="panel-title")
                
                yield Label("1. Custom Prefix", classes="section-label")
                yield Input(
                    placeholder="Enter prefix (e.g. 'mybrand')",
                    id="prefix-input"
                )
                
                yield Label("2. WHOIS Lookup", classes="section-label")
                yield Input(
                    placeholder="Domain (e.g. 'google.com')",
                    id="whois-input"
                )
                yield Button("Run WHOIS", id="whois-btn", variant="primary")
                
                yield Label("3. Actions", classes="section-label")
                yield Button("Fetch All TLDs (IANA)", id="fetch-all-btn")
                yield Button("Fetch Buyable TLDs (PSL)", id="fetch-buyable-btn")
                yield Button("Save Current List", id="save-list-btn", variant="success")
                
                yield Label("System Log", classes="section-label")
                yield RichLog(id="status-log", max_lines=50, auto_scroll=True)
                
            # Middle Domain List
            with Vertical(id="center-panel"):
                yield Label("DOMAINS / SUFFIXES", classes="panel-title")
                yield Input(
                    placeholder="Search / filter list...",
                    id="filter-input"
                )
                yield OptionList(id="domain-list")
                
            # Right Details Panel
            with Vertical(id="right-panel"):
                yield Label("WHOIS / DETAILS", classes="panel-title")
                yield RichLog(id="details-log", max_lines=1000, highlight=True)
                
        yield Footer()

    def update_domain_list(self) -> None:
        prefix_input = self.query_one("#prefix-input", Input).value.strip().lower()
        filter_input = self.query_one("#filter-input", Input).value.strip().lower()
        
        # Prepend prefix if present
        if prefix_input:
            domains = [f"{prefix_input}.{tld}" for tld in self.base_tlds]
        else:
            domains = self.base_tlds
            
        # Apply filter if present
        if filter_input:
            domains = [d for d in domains if filter_input in d]
            
        self.current_domains = domains
        
        # Populate OptionList
        domain_list_widget = self.query_one("#domain-list", OptionList)
        domain_list_widget.clear_options()
        
        # Limit options loaded to prevent TUI rendering slowdown if massive
        display_domains = domains[:1000]
        for d in display_domains:
            domain_list_widget.add_option(d)
            
        if len(domains) > 1000:
            domain_list_widget.add_option(f"... and {len(domains) - 1000} more (save list to view all)")
            
    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id in ("prefix-input", "filter-input"):
            self.update_domain_list()
            
    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        # Get the selected domain
        selected_text = event.option.prompt
        if selected_text and not selected_text.startswith("..."):
            whois_input = self.query_one("#whois-input", Input)
            whois_input.value = selected_text
            self.trigger_whois_lookup()
            
    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        selected_text = event.option.prompt
        if selected_text and not selected_text.startswith("..."):
            whois_input = self.query_one("#whois-input", Input)
            whois_input.value = selected_text
            
    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "whois-input":
            self.trigger_whois_lookup()
        elif event.input.id == "prefix-input":
            self.query_one("#filter-input", Input).focus()
            
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "whois-btn":
            self.trigger_whois_lookup()
        elif event.button.id == "fetch-all-btn":
            self.run_fetch_all()
        elif event.button.id == "fetch-buyable-btn":
            self.run_fetch_buyable()
        elif event.button.id == "save-list-btn":
            self.save_current_list()
            
    def action_trigger_whois(self) -> None:
        self.trigger_whois_lookup()
        
    def action_save_list(self) -> None:
        self.save_current_list()
        
    def trigger_whois_lookup(self) -> None:
        domain = self.query_one("#whois-input", Input).value.strip().lower()
        if not domain or domain.startswith("..."):
            self.log_status("Please enter/select a valid domain for WHOIS.")
            return
            
        details_log = self.query_one("#details-log", RichLog)
        details_log.clear()
        details_log.write(f"Querying WHOIS for [bold cyan]{domain}[/bold cyan]...\n")
        
        async def do_whois():
            loop = asyncio.get_running_loop()
            try:
                # Run blocking whois in executor
                w = await loop.run_in_executor(None, whois.whois, domain)
                details_log.clear()
                details_log.write(f"[bold green]WHOIS Results for {domain}:[/bold green]\n\n")
                details_log.write(str(w))
                self.log_status(f"WHOIS completed for {domain}.")
            except Exception as e:
                details_log.write(f"[bold red]WHOIS Error:[/bold red] {e}\n")
                self.log_status(f"WHOIS failed for {domain}.")
                
        self.run_worker(do_whois(), group="whois")
        
    def run_fetch_all(self) -> None:
        self.log_status("Fetching all TLDs from IANA in background...")
        btn = self.query_one("#fetch-all-btn", Button)
        btn.disabled = True
        
        async def do_fetch():
            loop = asyncio.get_running_loop()
            try:
                await loop.run_in_executor(None, get_all_tlds)
                self.log_status("Fetched and saved all TLDs to all_tlds.txt")
            except Exception as e:
                self.log_status(f"Error fetching all TLDs: {e}")
            finally:
                btn.disabled = False
                
        self.run_worker(do_fetch())
        
    def run_fetch_buyable(self) -> None:
        self.log_status("Fetching buyable TLDs in background...")
        btn = self.query_one("#fetch-buyable-btn", Button)
        btn.disabled = True
        
        async def do_fetch():
            loop = asyncio.get_running_loop()
            try:
                await loop.run_in_executor(None, get_buyable_tlds)
                self.log_status("Fetched and saved buyable TLDs.")
                self.call_from_thread(self.load_buyable_tlds)
            except Exception as e:
                self.log_status(f"Error fetching buyable TLDs: {e}")
            finally:
                btn.disabled = False
                
        self.run_worker(do_fetch())
        
    def save_current_list(self) -> None:
        prefix = self.query_one("#prefix-input", Input).value.strip().lower()
        if not self.current_domains:
            self.log_status("No domains to save.")
            return
            
        output_filename = f"{prefix}_domains.txt" if prefix else "filtered_domains.txt"
        
        try:
            with open(output_filename, "w", encoding="utf-8") as f:
                for d in self.current_domains:
                    f.write(f"{d}\n")
            self.log_status(f"Saved {len(self.current_domains)} domains to {output_filename}")
        except Exception as e:
            self.log_status(f"Error saving list: {e}")

if __name__ == "__main__":
    app = TLDHelperTUI()
    app.run()
