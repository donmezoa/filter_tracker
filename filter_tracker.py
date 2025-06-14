import sqlite3
import argparse
import csv
from datetime import datetime

# Database file name
DB_NAME = "filters.db"

def initialize_database():
    """Create the filters table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS filters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT NOT NULL,
            size TEXT NOT NULL,
            product_number TEXT NOT NULL,
            change_date TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def add_filter_change(location, size, product_number, change_date=None):
    """Add a new filter change record."""
    if not change_date:
        change_date = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO filters (location, size, product_number, change_date)
        VALUES (?, ?, ?, ?)
    """, (location, size, product_number, change_date))

    conn.commit()
    conn.close()

    print(f"Filter change recorded for {location} on {change_date}.")

def check_last_filter_change(location):
    """Check the last filter change for a given location."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT change_date, product_number
        FROM filters
        WHERE location = ?
        ORDER BY change_date DESC
        LIMIT 1
    """, (location,))

    result = cursor.fetchone()
    conn.close()

    if result:
        change_date, product_number = result
        print(f"The filter at '{location}' was last changed on {change_date} using product '{product_number}'.")
    else:
        print(f"No record found for location '{location}'.")

def list_all_filter_changes():
    """List all filter change records."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, location, size, product_number, change_date
        FROM filters
        ORDER BY location ASC, change_date DESC
    """)

    records = cursor.fetchall()
    conn.close()

    if records:
        print(f"{'ID':<4} {'Location':<20} {'Size':<10} {'Product #':<15} {'Change Date':<12}")
        print("-" * 70)
        for record in records:
            id_, location, size, product_number, change_date = record
            print(f"{id_:<4} {location:<20} {size:<10} {product_number:<15} {change_date:<12}")
    else:
        print("No filter change records found.")

def delete_filter_record(record_id):
    """Delete a filter change record by ID."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM filters WHERE id = ?", (record_id,))
    record = cursor.fetchone()

    if record:
        cursor.execute("DELETE FROM filters WHERE id = ?", (record_id,))
        conn.commit()
        print(f"Record with ID {record_id} deleted.")
    else:
        print(f"No record found with ID {record_id}.")

    conn.close()

def edit_filter_record(record_id, location=None, size=None, product_number=None, change_date=None):
    """Edit an existing filter change record by ID."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM filters WHERE id = ?", (record_id,))
    record = cursor.fetchone()

    if not record:
        print(f"No record found with ID {record_id}.")
        conn.close()
        return

    updates = []
    values = []

    if location:
        updates.append("location = ?")
        values.append(location)
    if size:
        updates.append("size = ?")
        values.append(size)
    if product_number:
        updates.append("product_number = ?")
        values.append(product_number)
    if change_date:
        updates.append("change_date = ?")
        values.append(change_date)

    if updates:
        values.append(record_id)
        query = f"UPDATE filters SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, tuple(values))
        conn.commit()
        print(f"Record with ID {record_id} updated.")
    else:
        print("No fields provided to update.")

    conn.close()

def export_all_to_csv(filename):
    """Export all filter change records to a CSV file."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, location, size, product_number, change_date
        FROM filters
        ORDER BY location ASC, change_date DESC
    """)

    records = cursor.fetchall()
    conn.close()

    if records:
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Location", "Size", "Product Number", "Change Date"])
            writer.writerows(records)
        print(f"All records exported to {filename}.")
    else:
        print("No records to export.")

def export_last_changes_to_csv(filename):
    """Export last filter change per location to a CSV file."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT location, MAX(change_date)
        FROM filters
        GROUP BY location
    """)

    last_changes = cursor.fetchall()

    results = []
    for location, change_date in last_changes:
        cursor.execute("""
            SELECT id, location, size, product_number, change_date
            FROM filters
            WHERE location = ? AND change_date = ?
            ORDER BY id DESC
            LIMIT 1
        """, (location, change_date))
        results.append(cursor.fetchone())

    conn.close()

    if results:
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Location", "Size", "Product Number", "Change Date"])
            writer.writerows(results)
        print(f"Last filter change per location exported to {filename}.")
    else:
        print("No records to export.")


def print_last_change_per_location():
    """Print the last filter change for each location."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT location, MAX(change_date)
        FROM filters
        GROUP BY location
    """)

    last_changes = cursor.fetchall()

    if last_changes:
        print(f"{'Location':<20} {'Last Change Date':<12}")
        print("-" * 35)
        for location, change_date in last_changes:
            cursor.execute("""
                SELECT product_number
                FROM filters
                WHERE location = ? AND change_date = ?
                ORDER BY id DESC
                LIMIT 1
            """, (location, change_date))
            product_number = cursor.fetchone()[0]
            print(f"{location:<20} {change_date:<12} (Product: {product_number})")
    else:
        print("No records found.")

    conn.close()



# Command-line interface
def main():
    initialize_database()

    parser = argparse.ArgumentParser(description="Air Filter Change Tracker")
    subparsers = parser.add_subparsers(dest="command")

    # Add command
    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("--location", required=True)
    add_parser.add_argument("--size", required=True)
    add_parser.add_argument("--product_number", required=True)
    add_parser.add_argument("--change_date")

    # Check command
    check_parser = subparsers.add_parser("check")
    check_parser.add_argument("--location", required=True)

    # List command
    subparsers.add_parser("list")
    subparsers.add_parser("last_changes")

    # Delete command
    delete_parser = subparsers.add_parser("delete")
    delete_parser.add_argument("--id", type=int, required=True)

    # Edit command
    edit_parser = subparsers.add_parser("edit")
    edit_parser.add_argument("--id", type=int, required=True)
    edit_parser.add_argument("--location")
    edit_parser.add_argument("--size")
    edit_parser.add_argument("--product_number")
    edit_parser.add_argument("--change_date")

    # Export all command
    export_all_parser = subparsers.add_parser("export_all")
    export_all_parser.add_argument("--filename", required=True)

    # Export last changes command
    export_last_parser = subparsers.add_parser("export_last")
    export_last_parser.add_argument("--filename", required=True)

    args = parser.parse_args()

    if args.command == "add":
        add_filter_change(args.location, args.size, args.product_number, args.change_date)
    elif args.command == "check":
        check_last_filter_change(args.location)
    elif args.command == "list":
        list_all_filter_changes()
    elif args.command == "delete":
        delete_filter_record(args.id)
    elif args.command == "edit":
        edit_filter_record(args.id, args.location, args.size, args.product_number, args.change_date)
    elif args.command == "export_all":
        export_all_to_csv(args.filename)
    elif args.command == "export_last":
        export_last_changes_to_csv(args.filename)
    elif args.command == "last_changes":
        print_last_change_per_location()

if __name__ == "__main__":
    main()
