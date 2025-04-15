# QuickLink - Quick Access to Everything

## Description

**QuickLink** is a desktop application developed in Python using Tkinter with the `ttkbootstrap` theme and an SQLite database. Its main goal is to provide a fast and organized way to store and access your favorite websites and archives. With an intuitive interface, you can add links, associate images for easy visual identification, and organize your links across multiple pages.

![alt text](https://github.com/hipolitorodrigues/assets-for-github/blob/05d201a5a206537660018d2a967edd880216b5ea/images/01/img-quick_link.png)

## Key Features

* **Grid View:** Links are displayed in a 4x4 grid (16 links per page).
* **Add New Link:**
    * A dedicated button allows you to add new links to the current page.
    * Clicking it opens a window/dialog requesting:
        * **Website URL:** The web address you want to save.
        * **Associated Image (Optional):** You can select an image file from your computer to visually represent the link. This image will appear in the grid.
* **Delete Link:**
    * A delete button lets you remove unwanted links.
    * The app provides a mechanism to select which link on the current page you want to delete.
    * The grid is updated after deletion.
* **Change Page Title:**
    * A button allows you to modify the title of the currently displayed page.
    * A dialog box opens for you to enter a new title.
    * The title is updated at the top of the window.
* **Add New Page:**
    * A button allows you to add new pages, expanding your collection beyond 16 links per page.
    * Clicking it creates a new empty page.
* **Delete Current Page:**
    * A button allows you to delete the currently viewed page if it's no longer needed.
    * **Warning:** Page deletion is irreversible (with a possible confirmation prompt).
* **Page Navigation:**
    * "Previous" and "Next" buttons allow you to navigate easily between the pages you've created.
    * The app maintains the state of links and titles across all pages.
* **Visual Links:** Instead of plain text, links are represented by the images you associate with them. Clicking the image opens the corresponding URL in your default web browser.
* **Persistent Data:** All your links, associated images, and page titles are stored persistently in a local SQLite database. This ensures your data is saved even after closing and reopening the app.
* **Asset Folder Icons:** Example icons were downloaded from [svgrepo.com](https://www.svgrepo.com/).

## Technologies Used

* **Python:** The main programming language.
* **Tkinter:** Python’s standard GUI library for building the user interface.
* **ttkbootstrap:** A library providing modern themes and styled widgets for Tkinter, improving the visual design.
* **SQLite:** A lightweight, embedded relational database to store application data (links, images, titles).

## How to Use

1. **Run the Application:** Launch the main Python script.
    * Optionally, download and run portable\QuickLink.exe. No installation required.
2. **Add a Link:**
    * Click the "Add Link" button.
    * In the opened window, enter the website URL.
    * Optionally, click the button to choose an image from your computer to associate with the link.
    * Click "Save" (or similar) to add the link to the current page grid.
3. **Access a Link:** Click on the image of the desired link in the grid. The associated URL will open in your default browser.
4. **Delete a Link:**
    * Click the "Delete Link" button.
    * The app will provide a way to select the link to delete (e.g., by clicking the link in the grid).
    * Confirm the deletion if necessary.
5. **Change the Page Title:**
    * Click the "Change Title" button.
    * In the dialog, enter the new desired title and click "OK".
6. **Add a New Page:** Click the "Add Page" button. A new empty page will be created and displayed.
7. **Delete the Current Page:** Click the "Delete Page" button. Confirm the deletion if prompted.
8. **Navigate Between Pages:** Use the "< Previous" and "> Next" buttons to switch between your link pages.

## File Structure (Example)

```
QuickLink/
├── quicklink.py         # Main application script
├── database.db          # SQLite database file
├── assets/              # Folder to store default images (optional)
└── README.md
```

## ⭐ Developer

- **Developer**: Hipolito Rodrigues  
- **Creation Date**: 04/14/2025  
- **Last Update**: 04/15/2025  
- **Current Version**: 1.2

---

## 📜 License

This project is licensed under the MIT License. This means you are free to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the software, as long as you include the original copyright notice and license in all copies or substantial portions.

* **Asset folder icons:** Example icons were downloaded from [svgrepo.com](https://www.svgrepo.com/).

---
