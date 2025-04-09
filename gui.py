import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
from main import process_file
import pandas as pd
from datetime import datetime
from ttkthemes import ThemedTk

class ModernBookkeepingSystem:
    def __init__(self):
        self.root = ThemedTk(theme="arc")
        self.root.title("Bookkeeping System")
        self.root.geometry("1200x800")  # Increased size for better receipt viewing
        
        # Style configuration for Frutiger Aero look
        style = ttk.Style()
        style.configure('Header.TLabel', font=('Segoe UI', 24, 'bold'), foreground='#1a477f')
        style.configure('SubHeader.TLabel', font=('Segoe UI', 12))
        style.configure('Modern.TButton', font=('Segoe UI', 10))
        style.configure('Receipt.TFrame', background='#f0f8ff', relief='groove')
        
        # Configure Notebook style
        style.configure('TNotebook', background='#e8f0f8')
        style.configure('TNotebook.Tab', padding=[12, 4], font=('Segoe UI', 10))
        style.map('TNotebook.Tab',
                 background=[("selected", "#c8ddf2"), ("!selected", "#e8f0f8")],
                 foreground=[("selected", "#1a477f"), ("!selected", "#666666")])
        
        # Configure Combobox style
        style.configure('TCombobox', padding=5)
        style.map('TCombobox',
                 fieldbackground=[("readonly", "#ffffff")],
                 selectbackground=[("readonly", "#c8ddf2")])
        
        self.setup_gui()
        
    def setup_gui(self):
        # Main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Create tabs
        self.process_tab = ttk.Frame(self.notebook)
        self.view_tab = ttk.Frame(self.notebook)
        self.journal_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.process_tab, text='Process Orders')
        self.notebook.add(self.view_tab, text='View Receipts')
        self.notebook.add(self.journal_tab, text='Cash Receipts Journal')
        
        self.setup_process_tab()
        self.setup_view_tab()
        self.setup_journal_tab()
        
    def setup_process_tab(self):
        # Title
        header = ttk.Label(
            self.process_tab,
            text="Process Orders",
            style='Header.TLabel'
        )
        header.pack(pady=20)
        
        # Main form frame
        form_frame = ttk.LabelFrame(
            self.process_tab,
            text="Order Processing",
            padding=20,
            style='Modern.TLabelframe'
        )
        form_frame.pack(fill='x', padx=20, pady=10)
        
        # Platform selection
        platform_frame = ttk.Frame(form_frame)
        platform_frame.pack(fill='x', pady=5)
        
        ttk.Label(platform_frame, text="Platform:", font=('Segoe UI', 10)).pack(side='left')
        
        self.platform_var = tk.StringVar(value="Shopee")
        self.platform_combo = ttk.Combobox(
            platform_frame,
            textvariable=self.platform_var,
            values=["Shopee", "Lazada"],
            state="readonly",
            width=30
        )
        self.platform_combo.pack(side='left', padx=(10, 0))
        
        # Seller fee
        fee_frame = ttk.Frame(form_frame)
        fee_frame.pack(fill='x', pady=10)
        
        ttk.Label(fee_frame, text="Seller Fee:").pack(side='left')
        
        self.seller_fee = tk.StringVar()
        fee_entry = ttk.Entry(
            fee_frame,
            textvariable=self.seller_fee,
            width=32
        )
        fee_entry.pack(side='left', padx=(10, 0))
        
        ttk.Label(
            form_frame,
            text="Note: Add % for percentage (e.g., 5%) or enter fixed amount (e.g., 10)",
            foreground='gray'
        ).pack(anchor='w', pady=(0, 10))
        
        # File selection
        file_frame = ttk.Frame(form_frame)
        file_frame.pack(fill='x', pady=10)
        
        self.file_path = tk.StringVar()
        
        ttk.Button(
            file_frame,
            text="Select XLSX File",
            command=self.select_file,
            style='Modern.TButton'
        ).pack(side='left')
        
        ttk.Label(
            file_frame,
            textvariable=self.file_path,
            wraplength=400
        ).pack(side='left', padx=(10, 0))
        
        # Process button
        ttk.Button(
            form_frame,
            text="Process Orders",
            command=self.process_file,
            style='Modern.TButton',
            width=20
        ).pack(pady=20)
        
    def setup_view_tab(self):
        # Title
        header = ttk.Label(
            self.view_tab,
            text="Generated Receipts",
            style='Header.TLabel'
        )
        header.pack(pady=20)
        
        # Create a canvas with scrollbar for the receipts
        canvas_frame = ttk.Frame(self.view_tab)
        canvas_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(canvas_frame)
        scrollbar.pack(side='right', fill='y')
        
        # Create canvas
        self.canvas = tk.Canvas(
            canvas_frame,
            yscrollcommand=scrollbar.set,
            background='#f0f8ff'
        )
        self.canvas.pack(side='left', fill='both', expand=True)
        
        scrollbar.config(command=self.canvas.yview)
        
        # Create frame for receipts
        self.receipts_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.receipts_frame, anchor='nw')
        
        # Bind resize events
        self.receipts_frame.bind('<Configure>', self.on_frame_configure)
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        
        # Bind mouse wheel for scrolling
        self.canvas.bind_all('<MouseWheel>', self._on_mousewheel)
        self.canvas.bind_all('<Shift-MouseWheel>', self._on_horizontal_mousewheel)
        
        # Refresh button
        ttk.Button(
            self.view_tab,
            text="↻ Refresh Receipts",
            command=self.refresh_receipts,
            style='Modern.TButton'
        ).pack(pady=10)
        
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
    def _on_horizontal_mousewheel(self, event):
        self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
        
    def on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        
    def on_canvas_configure(self, event):
        # Update the receipts frame width when canvas is resized
        width = event.width - 4  # Subtract some padding
        self.canvas.itemconfig(self.canvas.find_withtag('all')[0], width=width)
        
    def setup_journal_tab(self):
        # Title
        header = ttk.Label(
            self.journal_tab,
            text="Cash Receipts Journal",
            style='Header.TLabel'
        )
        header.pack(pady=20)
        
        # Journal controls
        control_frame = ttk.LabelFrame(self.journal_tab, text="Journal Controls", padding=20)
        control_frame.pack(fill='x', padx=20, pady=10)
        
        # Starting SI number
        si_frame = ttk.Frame(control_frame)
        si_frame.pack(fill='x', pady=5)
        
        ttk.Label(si_frame, text="Starting S.I. Number:").pack(side='left')
        
        self.si_number = tk.StringVar(value="00001")
        si_entry = ttk.Entry(
            si_frame,
            textvariable=self.si_number,
            width=10
        )
        si_entry.pack(side='left', padx=(10, 0))
        
        # Generate button
        ttk.Button(
            control_frame,
            text="Generate Journal",
            command=self.generate_journal,
            style='Modern.TButton',
            width=20
        ).pack(pady=10)
        
        # Journal viewer
        self.journal_text = scrolledtext.ScrolledText(
            self.journal_tab,
            wrap=tk.WORD,
            width=80,
            height=20,
            font=('Courier', 10)
        )
        self.journal_text.pack(fill='both', expand=True, padx=20, pady=10)
        
    def refresh_receipts(self):
        # Clear existing receipts
        for widget in self.receipts_frame.winfo_children():
            widget.destroy()
            
        try:
            # Get list of receipt files
            receipt_files = []
            for file in os.listdir("output"):
                if file.startswith("receipt_") and file.endswith(".txt"):
                    receipt_files.append(file)
            
            # Sort files by date
            receipt_files.sort()
            
            # Create grid of receipts
            row = 0
            col = 0
            max_cols = 2  # Number of receipts per row
            
            for filename in receipt_files:
                # Create frame for receipt
                receipt_frame = ttk.Frame(self.receipts_frame, style='Receipt.TFrame')
                receipt_frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
                
                # Extract date and customer from filename
                parts = filename.replace('.txt', '').split('_')
                date = parts[1]
                customer = ' '.join(parts[2:])
                
                # Add header
                header_frame = ttk.Frame(receipt_frame)
                header_frame.pack(fill='x', padx=5, pady=5)
                
                ttk.Label(
                    header_frame,
                    text=customer,
                    style='SubHeader.TLabel'
                ).pack(side='left')
                
                ttk.Label(
                    header_frame,
                    text=date,
                    style='SubHeader.TLabel'
                ).pack(side='right')
                
                # Add receipt content
                with open(os.path.join("output", filename), 'r', encoding='utf-8') as f:
                    content = f.read()
                
                text_widget = scrolledtext.ScrolledText(
                    receipt_frame,
                    wrap=tk.WORD,
                    width=50,
                    height=15,
                    font=('Courier', 9)
                )
                text_widget.pack(padx=5, pady=5)
                text_widget.insert('1.0', content)
                text_widget.configure(state='disabled')
                
                # Update grid position
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
                    
            # Configure grid columns to be equal width
            for i in range(max_cols):
                self.receipts_frame.grid_columnconfigure(i, weight=1)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading receipts: {str(e)}")
            
    def select_file(self):
        filename = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if filename:
            self.file_path.set(filename)
            
    def process_file(self):
        if not self.file_path.get():
            messagebox.showwarning("Warning", "Please select a file first!")
            return
            
        try:
            # Create output directory if it doesn't exist
            os.makedirs("output", exist_ok=True)
            
            # Get seller fee value
            fee_value = self.seller_fee.get().strip()
            if fee_value:
                # Validate fee format
                if fee_value.endswith('%'):
                    try:
                        float(fee_value[:-1])
                    except ValueError:
                        messagebox.showwarning(
                            "Warning",
                            "Invalid percentage format! Please enter a valid number followed by %"
                        )
                        return
                else:
                    try:
                        float(fee_value)
                    except ValueError:
                        messagebox.showwarning(
                            "Warning",
                            "Invalid fee amount! Please enter a valid number"
                        )
                        return
            
            # Process the file
            process_file(
                self.file_path.get(),
                platform=self.platform_var.get(),
                platform_fee=fee_value if fee_value else None
            )
            
            messagebox.showinfo(
                "Success",
                "Processing complete!\nCheck the 'View Receipts' tab to view the generated receipts."
            )
            
            # Refresh receipt list
            self.refresh_receipts()
            
            # Switch to view tab
            self.notebook.select(1)
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            
    def generate_journal(self):
        try:
            # Get starting SI number
            try:
                si_start = int(self.si_number.get())
            except ValueError:
                messagebox.showwarning("Warning", "Please enter a valid starting S.I. number!")
                return
                
            # Read all receipt files and extract data
            entries = []
            for file in os.listdir("output"):
                if file.startswith("receipt_") and file.endswith(".txt"):
                    date_str = file.split("_")[1]  # Get date from filename
                    date = datetime.strptime(date_str, "%Y%m%d")
                    
                    with open(os.path.join("output", file), 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Extract customer name and total
                        for line in content.split('\n'):
                            if line.startswith("Name:"):
                                customer = line.split(":")[1].strip()
                            elif line.startswith("Grand total:"):
                                total = float(line.split("₱")[1].strip())
                                
                    entries.append({
                        'date': date,
                        'customer': customer,
                        'amount': total
                    })
            
            # Sort entries by date
            entries.sort(key=lambda x: x['date'])
            
            # Generate journal
            journal = "Cash Receipts Journal\n"
            journal += "=" * 70 + "\n"
            journal += f"{'Date':<12} {'Name of Customer':<30} {'S.I.':<8} {'Cash':>10} {'Sales':>10}\n"
            journal += "-" * 70 + "\n"
            
            total_amount = 0
            for i, entry in enumerate(entries):
                si_number = f"{si_start + i:05d}"
                amount = entry['amount']
                total_amount += amount
                
                journal += f"{entry['date'].strftime('%m/%d/%Y'):<12} "
                journal += f"{entry['customer']:<30} "
                journal += f"{si_number:<8} "
                journal += f"{amount:>10.2f} "
                journal += f"{amount:>10.2f}\n"
            
            journal += "=" * 70 + "\n"
            journal += f"{'Total:':<51} {total_amount:>10.2f} {total_amount:>10.2f}\n"
            
            # Display journal
            self.journal_text.delete('1.0', tk.END)
            self.journal_text.insert('1.0', journal)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generating journal: {str(e)}")
            
    def run(self):
        self.root.mainloop()

def create_gui():
    app = ModernBookkeepingSystem()
    app.run()

if __name__ == "__main__":
    create_gui() 
