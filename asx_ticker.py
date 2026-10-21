import tkinter as tk
import yfinance as yf
import webbrowser
import threading

# Your Watchlist
WATCHLIST = [
    {"ticker": "BHP.AX", "name": "BHP", "gf": "BHP:ASX"},
    {"ticker": "LYC.AX", "name": "LYC", "gf": "LYC:ASX"},
    {"ticker": "SGQ.AX", "name": "SGQ", "gf": "SGQ:ASX"},
    {"ticker": "AVL.AX", "name": "AVL", "gf": "AVL:ASX"},
]

class ASXTickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ASX Desktop Ticker")
        
        # Window styling: Always on top, dark theme, frameless
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.92)
        self.root.configure(bg="#121212")

        # Main container frame
        self.main_frame = tk.Frame(root, bg="#121212", padx=10, pady=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Title / Drag header bar
        header_frame = tk.Frame(self.main_frame, bg="#121212")
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        title_lbl = tk.Label(header_frame, text="ASX WATCHLIST", fg="#888888", bg="#121212", font=("Segoe UI", 9, "bold"))
        title_lbl.pack(side=tk.LEFT)

        close_btn = tk.Label(header_frame, text="✕", fg="#666666", bg="#121212", font=("Segoe UI", 9, "bold"), cursor="hand2")
        close_btn.pack(side=tk.RIGHT)
        close_btn.bind("<Button-1>", lambda e: self.root.destroy())

        # Enable dragging the window anywhere
        header_frame.bind("<Button-1>", self.start_move)
        header_frame.bind("<B1-Motion>", self.do_move)
        title_lbl.bind("<Button-1>", self.start_move)
        title_lbl.bind("<B1-Motion>", self.do_move)

        # Rows container
        self.rows_frame = tk.Frame(self.main_frame, bg="#121212")
        self.rows_frame.pack(fill=tk.BOTH, expand=True)

        self.stock_widgets = []
        for item in WATCHLIST:
            row = self.create_stock_row(self.rows_frame, item)
            self.stock_widgets.append(row)

        # Initial fetch & periodic refresh (every 60 seconds)
        self.update_data()

    def create_stock_row(self, parent, item):
        frame = tk.Frame(parent, bg="#1e1e1e", cursor="hand2", padx=8, pady=6)
        frame.pack(fill=tk.X, pady=3)

        lbl_ticker = tk.Label(frame, text=item["name"], fg="#ffffff", bg="#1e1e1e", font=("Segoe UI", 10, "bold"), width=6, anchor="w")
        lbl_ticker.pack(side=tk.LEFT)

        lbl_price = tk.Label(frame, text="Loading...", fg="#cccccc", bg="#1e1e1e", font=("Segoe UI", 10), width=8, anchor="e")
        lbl_price.pack(side=tk.LEFT, padx=5)

        lbl_change = tk.Label(frame, text="--", fg="#888888", bg="#1e1e1e", font=("Segoe UI", 9, "bold"), width=8, anchor="e")
        lbl_change.pack(side=tk.RIGHT)

        # Click event to open Google Finance
        url = f"https://www.google.com/finance/quote/{item['gf']}"
        for widget in (frame, lbl_ticker, lbl_price, lbl_change):
            widget.bind("<Button-1>", lambda e, u=url: webbrowser.open(u))
            widget.bind("<Enter>", lambda e, f=frame: f.config(bg="#2d2d2d"))
            widget.bind("<Leave>", lambda e, f=frame: f.config(bg="#1e1e1e"))

        return {"ticker": item["ticker"], "price_lbl": lbl_price, "change_lbl": lbl_change}

    def update_data(self):
        threading.Thread(target=self._fetch_prices, daemon=True).start()
        self.root.after(60000, self.update_data)

    def _fetch_prices(self):
        # Fetch each ticker individually to ensure robust handling for all ASX stocks
        for widget in self.stock_widgets:
            t = widget["ticker"]
            try:
                stock = yf.Ticker(t)
                df = stock.history(period="2d")
                if len(df) >= 2:
                    close_prev = df['Close'].iloc[-2]
                    close_curr = df['Close'].iloc[-1]
                    change = close_curr - close_prev
                    pct_change = (change / close_prev) * 100

                    price_text = f"${close_curr:.2f}"
                    if change >= 0:
                        change_text = f"+{pct_change:.2f}%"
                        color = "#4ade80"  # Soft green
                    else:
                        change_text = f"{pct_change:.2f}%"
                        color = "#f87171"  # Soft red

                    self.root.after(0, lambda w=widget, p=price_text, c=change_text, col=color: self._update_ui_row(w, p, c, col))
            except Exception:
                pass

    def _update_ui_row(self, widget, price, change, color):
        widget["price_lbl"].config(text=price)
        widget["change_lbl"].config(text=change, fg=color)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

if __name__ == "__main__":
    root = tk.Tk()
    # Increased height to 230 to comfortably fit all rows without clipping
    root.geometry("240x230+1500+150")
    app = ASXTickerApp(root)
    root.mainloop()
