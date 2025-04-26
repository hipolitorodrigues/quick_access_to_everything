import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import sqlite3
import os
import webbrowser
from PIL import Image, ImageTk
import io

class QuickLink:
    def __init__(self, root):
        self.root = root
        self.root.title("QuickLink - Quick Access to Everything")
        self.root.geometry("1100x700")
        
        # Initialize database
        self.setup_database()
        
        # Variables
        self.current_page_id = None
        self.links_buttons = []
        
        # Create main layout
        self.create_ui()
        
        # Upload or create first page
        self.load_initial_page()
    
    def setup_database(self):
        """Configure the SQLite database"""
        self.conn = sqlite3.connect('quicklink.db')
        self.cursor = self.conn.cursor()
        
        # Check if the "title" column exists in the links table
        self.cursor.execute("PRAGMA table_info(links)")
        columns = self.cursor.fetchall()
        has_title_column = any(column[1] == 'title' for column in columns)
        
        # Create page table if not exists
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT DEFAULT 'New Page'
            )
        ''')
        
        # Create link table if not exists
        if not has_title_column:
            # If the table already exists but does not have the "title" column
            try:
                self.cursor.execute("ALTER TABLE links ADD COLUMN title TEXT")
            except sqlite3.OperationalError:
                # If the table does not yet exist, create it with the new column
                self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS links (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        page_id INTEGER,
                        url TEXT,
                        position INTEGER,
                        image BLOB,
                        title TEXT,
                        FOREIGN KEY (page_id) REFERENCES pages (id)
                    )
                ''')
        else:
            # If the table does not exist, create it with the "title" column
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS links (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    page_id INTEGER,
                    url TEXT,
                    position INTEGER,
                    image BLOB,
                    title TEXT,
                    FOREIGN KEY (page_id) REFERENCES pages (id)
                )
            ''')
        
        self.conn.commit()
    
    def create_ui(self):
        """Creates the user interface"""
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill=BOTH, expand=YES)

        # === ROW 1: CENTERED BUTTONS ===
        self.buttons_frame = ttk.Frame(self.main_frame)
        self.buttons_frame.pack(pady=(0, 15))  # Without fill=X, so as not to expand to the full width

        # Centered buttons
        self.add_link_btn = ttk.Button(
            self.buttons_frame, text="New Link", command=self.add_link, bootstyle="success", width=15
        )
        self.add_link_btn.pack(side=LEFT, padx=5)

        self.del_link_btn = ttk.Button(
            self.buttons_frame, text="Delete Link", command=self.delete_link, bootstyle="danger", width=12
        )
        self.del_link_btn.pack(side=LEFT, padx=5)

        self.change_title_btn = ttk.Button(
            self.buttons_frame, text="Page Title", command=self.change_page_title, bootstyle="info", width=18
        )
        self.change_title_btn.pack(side=LEFT, padx=5)

        self.add_page_btn = ttk.Button(
            self.buttons_frame, text="New Page", command=self.add_page, bootstyle="success", width=18
        )
        self.add_page_btn.pack(side=LEFT, padx=5)

        self.del_page_btn = ttk.Button(
            self.buttons_frame, text="Del. Current Page", command=self.delete_page, bootstyle="danger", width=15
        )
        self.del_page_btn.pack(side=LEFT, padx=5)
        
        # === LINE 2: PAGE TITLE ===
        self.title_frame = ttk.Frame(self.main_frame)
        self.title_frame.pack(fill=X, pady=(0, 20))
        
        self.title_label = ttk.Label(self.title_frame, text="Untitled page", 
                                    font=("Helvetica", 22, "bold"))
        self.title_label.pack(anchor=CENTER)
        
        # === LINE 3: LINKS AND NAVIGATION ===
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=BOTH, expand=YES)
        
        # Navigation button on the left
        self.prev_btn = ttk.Button(self.content_frame, text="<", command=self.prev_page, 
                                  bootstyle="secondary", width=4, padding=10)
        self.prev_btn.pack(side=LEFT, fill=Y, padx=(0, 15))
        
        # Central container for links
        self.links_container = ttk.Frame(self.content_frame)
        self.links_container.pack(side=LEFT, fill=BOTH, expand=YES)
        
        # Link grid (4x4)
        self.links_frame = ttk.Frame(self.links_container)
        self.links_frame.pack(fill=BOTH, expand=YES)
        
        # Configure 4x4 grid
        for i in range(4):
            self.links_frame.columnconfigure(i, weight=1, uniform="column")
            self.links_frame.rowconfigure(i, weight=1, uniform="row")
        
        # Navigation button on the right
        self.next_btn = ttk.Button(self.content_frame, text=">", command=self.next_page, 
                                  bootstyle="secondary", width=4, padding=10)
        self.next_btn.pack(side=RIGHT, fill=Y, padx=(15, 0))
    
    def load_initial_page(self):
        """Loads the first page or creates one if it doesn't exist"""
        self.cursor.execute("SELECT id FROM pages LIMIT 1")
        result = self.cursor.fetchone()
        
        if result:
            self.current_page_id = result[0]
            self.load_page(self.current_page_id)
        else:
            # Create first page if not exists
            self.cursor.execute("INSERT INTO pages (title) VALUES ('Quick Access to Everything')")
            self.conn.commit()
            self.current_page_id = self.cursor.lastrowid
            self.load_page(self.current_page_id)
    
    def load_page(self, page_id):
        """Loads a specific page"""
        # Clear current grid
        self.clear_links_grid()
        
        # Load page title
        self.cursor.execute("SELECT title FROM pages WHERE id = ?", (page_id,))
        title = self.cursor.fetchone()[0]
        self.title_label.config(text=title)
        
        # Load page links
        self.cursor.execute("SELECT id, url, position, image, title FROM links WHERE page_id = ? ORDER BY position", (page_id,))
        links = self.cursor.fetchall()
        
        # Create empty 4x4 grid
        self.links_buttons = []
        for i in range(16):
            row = i // 4
            col = i % 4
            
            # Find link to this position (if it exists)
            link_data = None
            for link in links:
                if link[2] == i:  # position = i
                    link_data = link
                    break
            
            # Create frame for the link
            link_frame = ttk.Frame(self.links_frame, bootstyle="default")
            link_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            if link_data:
                # Add button with image (if available) or title
                if link_data[3]:  # If you have an image
                    img = Image.open(io.BytesIO(link_data[3]))
                    img = img.resize((120, 120), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    
                    btn = ttk.Button(link_frame, image=photo, bootstyle="success-outline", command=lambda url=link_data[1]: self.open_url(url))
                    btn.image = photo  # Keep reference
                else:
                    # Use title or URL if no image
                    link_title = link_data[4] if link_data[4] else "Link"
                    btn = ttk.Button(link_frame, text=link_title, bootstyle="success-outline",
                                   command=lambda url=link_data[1]: self.open_url(url))
                
                btn.link_id = link_data[0]  # Store Link ID for Deletion
                btn.position = link_data[2]  # Store position
                btn.pack(fill=BOTH, expand=YES)
                self.links_buttons.append(btn)
            else:
                # Create empty button if there is no link at this position
                empty_btn = ttk.Button(link_frame, text="Empty", state="disabled", bootstyle="light")
                empty_btn.position = i  # Store position
                empty_btn.link_id = None  # No link ID
                empty_btn.pack(fill=BOTH, expand=YES)
                self.links_buttons.append(empty_btn)
        
        # Update navigation buttons
        self.update_navigation_buttons()
    
    def clear_links_grid(self):
        """Clear the link grid"""
        for widget in self.links_frame.winfo_children():
            widget.destroy()
        self.links_buttons = []
    
    def add_link(self):
        """Add a new link"""
        # Check if we already have 16 links on the page
        self.cursor.execute("SELECT COUNT(*) FROM links WHERE page_id = ?", (self.current_page_id,))
        count = self.cursor.fetchone()[0]
        
        if count >= 16:
            messagebox.showinfo("Limit Reached", "This page already contains the maximum of 16 links.")
            return
        
        # Create custom dialog window
        dialog = ttk.Toplevel(self.root)
        dialog.title("Add New Link")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        
        # Make the window modal
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Variables to store values
        url_var = tk.StringVar()
        title_var = tk.StringVar()
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding=15)
        main_frame.pack(fill=BOTH, expand=YES)
        
        # URL
        url_frame = ttk.Frame(main_frame)
        url_frame.pack(fill=X, pady=(0, 10))
        ttk.Label(url_frame, text="Website URL:", width=12).pack(side=LEFT)
        ttk.Entry(url_frame, textvariable=url_var, width=40).pack(side=LEFT, fill=X, expand=YES)
        
        # Title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=X, pady=(0, 20))
        ttk.Label(title_frame, text="Link title:", width=12).pack(side=LEFT)
        ttk.Entry(title_frame, textvariable=title_var, width=40).pack(side=LEFT, fill=X, expand=YES)
        
        # Dialogue result
        result = {"url": None, "title": None, "submitted": False}
        
        def on_submit():
            # Validate basic URL
            url = url_var.get()
            if not url:
                messagebox.showwarning("Invalid URL", "Please enter a valid URL.")
                return
            
            # Comment this condition to open PDF files or other types of files
            """ if not (url.startswith("http://") or url.startswith("https://")):
                url = "https://" + url """
                
            result["url"] = url
            result["title"] = title_var.get()
            result["submitted"] = True
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=X)
        
        ttk.Button(buttons_frame, text="Cancel", command=on_cancel, 
                bootstyle="secondary", width=10).pack(side=RIGHT, padx=(5, 0))
        ttk.Button(buttons_frame, text="Add", command=on_submit, 
                bootstyle="success", width=10).pack(side=RIGHT)
        
        # Centralize dialogue
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Wait until the dialog is closed
        dialog.wait_window()
        
        # If the form has been submitted, continue with adding the link
        if result["submitted"] and result["url"]:
            url = result["url"]
            title = result["title"]
            
            # Ask if you want to add an image
            add_image = messagebox.askyesno("Add Image", "Want to add an image to this link?")
            image_data = None
            
            if add_image:
                file_path = filedialog.askopenfilename(title="Select an image", 
                                                filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp")])
                if file_path:
                    with open(file_path, "rb") as f:
                        image_data = f.read()
            
            # Find the next available position
            position = None
            for i, btn in enumerate(self.links_buttons):
                if btn.link_id is None:
                    position = btn.position
                    break
            
            if position is None:
                position = 0  # Fallback (should not happen)
            
            # Insert into database
            self.cursor.execute("""
                INSERT INTO links (page_id, url, position, image, title) 
                VALUES (?, ?, ?, ?, ?)
            """, (self.current_page_id, url, position, image_data, title))
            self.conn.commit()
            
            # Reload page
            self.load_page(self.current_page_id)

    def delete_link(self):
        """Deletes a link from the current page"""
        # Check for links to delete
        self.cursor.execute("SELECT COUNT(*) FROM links WHERE page_id = ?", (self.current_page_id,))
        count = self.cursor.fetchone()[0]
        
        if count == 0:
            messagebox.showinfo("No Link", "There are no links that can be deleted on this page.")
            return
        
        # Create window for selecting links to delete
        delete_window = ttk.Toplevel(self.root)
        delete_window.title("Delete Link")
        delete_window.geometry("450x500")
        
        ttk.Label(delete_window, text="Select a link to delete:").pack(pady=10)
        
        # List of links
        links_listbox = ttk.Treeview(delete_window, columns=("title", "url"), show="headings")
        links_listbox.heading("title", text="Title")
        links_listbox.heading("url", text="URL")
        links_listbox.column("title", width=150)
        links_listbox.column("url", width=300)
        links_listbox.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        
        # Populate list with links from current page
        self.cursor.execute("SELECT id, url, title FROM links WHERE page_id = ? ORDER BY position", (self.current_page_id,))
        links = self.cursor.fetchall()
        
        for link in links:
            # Truncate URL for display
            display_url = link[1]
            if len(display_url) > 40:
                display_url = display_url[:37] + "..."
                
            # Use title or "Link" if there is no title
            display_title = link[2] if link[2] else "Untitled link"
            
            links_listbox.insert("", "end", values=(display_title, display_url), iid=link[0])
        
        # Delete button
        def confirm_delete():
            selected = links_listbox.selection()
            if selected:
                link_id = selected[0]
                
                if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this link??"):
                    self.cursor.execute("DELETE FROM links WHERE id = ?", (link_id,))
                    self.conn.commit()
                    delete_window.destroy()
                    self.load_page(self.current_page_id)
            else:
                messagebox.showinfo("Selection required", "Please select a link to delete.")
        
        ttk.Button(delete_window, text="Delete Selected Link", bootstyle="danger", 
                 command=confirm_delete).pack(pady=10)
    
    def change_page_title(self):
        """Changes the title of the current page"""
        current_title = self.title_label.cget("text")
        new_title = simpledialog.askstring("Change Title", "Enter new page title:", initialvalue=current_title)
        
        if new_title:
            self.cursor.execute("UPDATE pages SET title = ? WHERE id = ?", (new_title, self.current_page_id))
            self.conn.commit()
            self.title_label.config(text=new_title)
    
    def add_page(self):
        """Add a new page"""
        title = simpledialog.askstring("New Page", "Enter the title of the new page:", initialvalue="New Page")
        
        if title:
            self.cursor.execute("INSERT INTO pages (title) VALUES (?)", (title,))
            self.conn.commit()
            page_id = self.cursor.lastrowid
            self.current_page_id = page_id
            self.load_page(page_id)
    
    def delete_page(self):
        """Deletes the current page"""
        # Count total pages
        self.cursor.execute("SELECT COUNT(*) FROM pages")
        total_pages = self.cursor.fetchone()[0]
        
        if total_pages <= 1:
            messagebox.showinfo("Operation Denied", "Cannot delete last page.")
            return
        
        # Confirm deletion
        confirm = messagebox.askyesno("Confirm Deletion", 
                                     "Are you sure you want to delete this page and all its links? This action cannot be undone.")
        
        if confirm:
            # Find previous or next page to navigate after deletion
            self.cursor.execute("SELECT id FROM pages WHERE id < ? ORDER BY id DESC LIMIT 1", (self.current_page_id,))
            prev_page = self.cursor.fetchone()
            
            if not prev_page:
                self.cursor.execute("SELECT id FROM pages WHERE id > ? ORDER BY id LIMIT 1", (self.current_page_id,))
                prev_page = self.cursor.fetchone()
            
            if prev_page:
                next_page_id = prev_page[0]
                
                # Delete links from current page
                self.cursor.execute("DELETE FROM links WHERE page_id = ?", (self.current_page_id,))
                
                # Delete current page
                self.cursor.execute("DELETE FROM pages WHERE id = ?", (self.current_page_id,))
                self.conn.commit()
                
                # Load next page
                self.current_page_id = next_page_id
                self.load_page(next_page_id)
    
    def prev_page(self):
        """Navigate to the previous page"""
        self.cursor.execute("SELECT id FROM pages WHERE id < ? ORDER BY id DESC LIMIT 1", (self.current_page_id,))
        prev_page = self.cursor.fetchone()
        
        if prev_page:
            self.current_page_id = prev_page[0]
            self.load_page(self.current_page_id)
    
    def next_page(self):
        """Navigate to the next page"""
        self.cursor.execute("SELECT id FROM pages WHERE id > ? ORDER BY id LIMIT 1", (self.current_page_id,))
        next_page = self.cursor.fetchone()
        
        if next_page:
            self.current_page_id = next_page[0]
            self.load_page(self.current_page_id)
    
    def update_navigation_buttons(self):
        """Updates the state of the navigation buttons"""
        # Check for previous page
        self.cursor.execute("SELECT EXISTS(SELECT 1 FROM pages WHERE id < ?)", (self.current_page_id,))
        has_prev = self.cursor.fetchone()[0]
        
        # Check for next page
        self.cursor.execute("SELECT EXISTS(SELECT 1 FROM pages WHERE id > ?)", (self.current_page_id,))
        has_next = self.cursor.fetchone()[0]
        
        # Update button state
        if has_prev:
            self.prev_btn.config(state="normal")
        else:
            self.prev_btn.config(state="disabled")
        
        if has_next:
            self.next_btn.config(state="normal")
        else:
            self.next_btn.config(state="disabled")
    
    def open_url(self, url):
        """Opens the URL in the default browser"""
        webbrowser.open(url)
    
    def on_close(self):
        """Closing the application"""
        self.conn.close()
        self.root.destroy()

def main():
    # Check dependencies
    try:
        import ttkbootstrap
        import PIL
    except ImportError:
        print("Installing required dependencies...")
        import subprocess
        subprocess.call(['pip', 'install', 'ttkbootstrap', 'pillow'])
    
    root = ttk.Window(themename="journal")
    app = QuickLink(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()

if __name__ == "__main__":
    main()