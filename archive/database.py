import sqlite3

def print_vehicle_data(db_path='vehicle_data.db'):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vehicles';")
        if not cursor.fetchone():
            print("No table named 'vehicles' found in the database.")
            return

        cursor.execute("SELECT * FROM vehicles")
        rows = cursor.fetchall()

        if not rows:
            print("No records found in the vehicles table.")
            return

        print("\n--- Vehicle Data ---")
        for row in rows:
            id, plate_number, timestamp, vehicle_video, vehicle_image = row
            print(f"ID: {id}")
            print(f"Plate Number: {plate_number}")
            print(f"Timestamp: {timestamp}")
            print(f"Vehicle Video: {vehicle_video}")
            print(f"Vehicle Image: {vehicle_image}")
            print("-" * 30)

    except sqlite3.Error as e:
        print("Database error:", e)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print_vehicle_data()
