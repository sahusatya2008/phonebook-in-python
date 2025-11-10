#15)  Make a phonebook by saving the Name and the phone number in the mysql table and when searched by the user, it should fetch the matching contacts also have the facility to edit and delete contacts.
import mysql.connector

# --- Database connection ---
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",        
        password="root123",  
        database="phonebook_db"
    )

# --- Add new contact (with duplicate checking) ---
def add_contact():
    name = input("Enter name: ").strip()
    phone = input("Enter phone number: ").strip()

    con = connect_db()
    cur = con.cursor()

    # Check for duplicate phone number
    cur.execute("SELECT * FROM contacts WHERE phone = %s", (phone,))
    phone_exists = cur.fetchone()
    cur.fetchall()  # clear any remaining results (prevents 'Unread result found')

    if phone_exists:
        print("\nThis phone number already exists. Cannot save duplicate numbers.\n")
        con.close()
        return

    # Check for duplicate name
    cur.execute("SELECT * FROM contacts WHERE name = %s", (name,))
    name_exists = cur.fetchone()
    cur.fetchall()  # clear again just to be safe

    if name_exists:
        print(f"\nThe name '{name}' already exists in your phonebook.")
        choice = input("Do you want to save it as a copy? (y/n): ").lower()
        if choice == "y":
            name = f"{name} (copy)"
            print(f"Contact will be saved as '{name}'.")
        else:
            print("Contact not added.\n")
            con.close()
            return

    cur.execute("INSERT INTO contacts (name, phone) VALUES (%s, %s)", (name, phone))
    con.commit()
    con.close()
    print("Contact added successfully!\n")

# --- View all contacts ---
def view_contacts():
    con = connect_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM contacts")
    rows = cur.fetchall()
    if not rows:
        print("No contacts found!\n")
    else:
        print("\n--- All Contacts ---")
        for r in rows:
            print(f"{r[0]}. {r[1]} - {r[2]}")
        print()
    con.close()

# --- Search contact ---
def search_contact():
    keyword = input("Enter name or number to search: ").strip()
    con = connect_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM contacts WHERE name LIKE %s OR phone LIKE %s", (f"%{keyword}%", f"%{keyword}%"))
    rows = cur.fetchall()
    if not rows:
        print("No matching contacts found!\n")
    else:
        print("\n--- Matching Contacts ---")
        for r in rows:
            print(f"{r[0]}. {r[1]} - {r[2]}")
        print()
    con.close()

# --- Edit contact ---
def edit_contact():
    view_contacts()
    cid = input("Enter contact ID to edit: ").strip()

    con = connect_db()
    cur = con.cursor()

    # Fetch current contact details
    cur.execute("SELECT name, phone FROM contacts WHERE id = %s", (cid,))
    contact = cur.fetchone()
    cur.fetchall()  # clear results

    if not contact:
        print("Contact not found.\n")
        con.close()
        return

    old_name, old_phone = contact
    print(f"\nCurrent Name: {old_name}")
    print(f"Current Phone: {old_phone}\n")

    # Ask for new values (allow skipping)
    new_name = input("Enter new name (press Enter to keep same): ").strip()
    new_phone = input("Enter new phone (press Enter to keep same): ").strip()

    # If user pressed Enter, keep old values
    if new_name == "":
        new_name = old_name
    if new_phone == "":
        new_phone = old_phone

    # Prevent duplicate phone number (if number changed)
    if new_phone != old_phone:
        cur.execute("SELECT * FROM contacts WHERE phone = %s AND id != %s", (new_phone, cid))
        phone_exists = cur.fetchone()
        cur.fetchall()
        if phone_exists:
            print("\nThis phone number already exists. Cannot use duplicate numbers.\n")
            con.close()
            return

    # Handle duplicate name (if name changed)
    if new_name != old_name:
        cur.execute("SELECT * FROM contacts WHERE name = %s AND id != %s", (new_name, cid))
        name_exists = cur.fetchone()
        cur.fetchall()

        if name_exists:
            print(f"\nThe name '{new_name}' already exists.")
            choice = input("Do you want to save it as a copy? (y/n): ").lower()
            if choice == "y":
                new_name = f"{new_name} (copy)"
                print(f"✔️ Name will be saved as '{new_name}'.")
            else:
                print("❌ Changes not saved.\n")
                con.close()
                return

    # Update only changed fields
    cur.execute("UPDATE contacts SET name=%s, phone=%s WHERE id=%s", (new_name, new_phone, cid))
    con.commit()
    con.close()
    print("Contact updated successfully!\n")


# --- Delete contact ---
def delete_contact():
    view_contacts()
    cid = input("Enter contact ID to delete: ").strip()
    con = connect_db()
    cur = con.cursor()
    cur.execute("DELETE FROM contacts WHERE id=%s", (cid,))
    con.commit()
    con.close()
    print("Contact deleted successfully!\n")

# --- Main menu ---
while True:
    print("=== PHONEBOOK MENU ===")
    print("1. Add Contact")
    print("2. View Contacts")
    print("3. Search Contact")
    print("4. Edit Contact")
    print("5. Delete Contact")
    print("6. Exit")
    choice = input("Enter your choice: ")

    if choice == "1":
        add_contact()
    elif choice == "2":
        view_contacts()
    elif choice == "3":
        search_contact()
    elif choice == "4":
        edit_contact()
    elif choice == "5":
        delete_contact()
    elif choice == "6":
        print("Goodbye!")
        break
    else:
        print("Invalid choice! Please try again.\n")
