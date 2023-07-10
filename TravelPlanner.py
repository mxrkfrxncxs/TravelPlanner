from tkinter import *
import tkinter as tk
import mysql.connector as mc
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import datetime
from PIL import Image, ImageTk


db = mc.connect(
    host="localhost",
    user="root",
    password="1234",
    database="travel_planner",
    auth_plugin='mysql_native_password'
)


#Trip CRUDL (List)
def trip_table():
    table.delete(*table.get_children())

    cursor = db.cursor()
    cursor.execute("SELECT trip_name, start_date, end_date FROM trips")
    data = cursor.fetchall()

    for index, row in enumerate(data):
        table.insert(parent='', index='end', iid=index, text=index, values=row, tags=column_names)


def fetch_trip_id(values):
    trip_name = values[0]
    cursor = db.cursor()
    query = "SELECT trip_id FROM trips WHERE trip_name = %s"
    cursor.execute(query, (trip_name,))
    result = cursor.fetchone()

    if result:
        trip_id = result[0]
        return trip_id

    return None


#Trip CRUDL (Create)
def create_trip():
    def submit_trip():
        trip_name = trip_name_entry.get()
        start_date = datetime.strptime(start_date_entry.get(), "%m/%d/%y").strftime("%Y-%m-%d")
        end_date = datetime.strptime(end_date_entry.get(), "%m/%d/%y").strftime("%Y-%m-%d")

        if not trip_name or not start_date or not end_date:
            messagebox.showwarning("Incomplete Fields", "Please fill in all fields.")
            return

        if end_date < start_date:
            messagebox.showwarning("Invalid Dates", "End date cannot be less than the start date.")
            return

        cursor = db.cursor()
        query = "INSERT INTO trips (trip_name, start_date, end_date) VALUES (%s, %s, %s)"
        values = (trip_name, start_date, end_date)
        cursor.execute(query, values)
        db.commit()

        trip_table()
        popup_window.destroy()

    popup_window = Toplevel(root)
    popup_window.title("Create New Trip")

    trip_name_label = Label(popup_window, text="Trip Name:")
    trip_name_label.grid(row=0, column=0)
    trip_name_entry = Entry(popup_window)
    trip_name_entry.grid(row=0, column=1)

    start_date_label = Label(popup_window, text="Start Date:")
    start_date_label.grid(row=1, column=0)
    start_date_entry = DateEntry(popup_window)
    start_date_entry.grid(row=1, column=1)

    end_date_label = Label(popup_window, text="End Date:")
    end_date_label.grid(row=2, column=0)
    end_date_entry = DateEntry(popup_window)
    end_date_entry.grid(row=2, column=1)

    trip_name_entry.focus()

    submit_button = Button(popup_window, text="Submit", command=submit_trip)
    submit_button.grid(row=3, columnspan=2)


#Trip CRUDL (Read)
def perform_search(event):
    search_query = search_entry.get()
    table.delete(*table.get_children())
    cursor = db.cursor()

    query = "SELECT trip_name, start_date, end_date FROM trips WHERE trip_name LIKE '%{}%'".format(search_query)

    try:
        cursor.execute(query)
        results = cursor.fetchall()

        for index, result in enumerate(results):
            table.insert(parent='', index='end', iid=index, text=index, values=result)

    except mc.Error as error:
        print("Error while performing search:", error)


def popup_menu(event):
    if event.num == 3:
        selected_item = table.selection()
        if selected_item:
            values = table.item(selected_item)['values']

            trip_id = fetch_trip_id(values)

            menu = tk.Menu(root, tearoff=0)
            menu.add_command(label="Edit", command=lambda: edit_row(selected_item, values, trip_id))
            menu.add_command(label="Delete", command=lambda: delete_row(selected_item))

            x = root.winfo_pointerx()
            y = root.winfo_pointery()

            menu.post(x, y)


#Trip CRUDL (Update)
def edit_row(selected_item, values, trip_id):
    def update_trip():
        new_trip_name = trip_name_entry.get()
        new_start_date = datetime.strptime(start_date_entry.get(), "%m/%d/%y").strftime("%Y-%m-%d")
        new_end_date = datetime.strptime(end_date_entry.get(), "%m/%d/%y").strftime("%Y-%m-%d")

        if not new_trip_name or not new_start_date or not new_end_date:
            messagebox.showwarning("Incomplete Fields", "Please fill in all fields.")
            return

        if new_end_date < new_start_date:
            messagebox.showwarning("Invalid Dates", "End date cannot be less than the start date.")
            return

        cursor = db.cursor()
        query = "UPDATE trips SET trip_name = %s, start_date = %s, end_date = %s WHERE trip_id = %s"
        new_values = (new_trip_name, new_start_date, new_end_date, trip_id)
        cursor.execute(query, new_values)
        db.commit()

        new_item = list(values)
        new_item[0] = new_trip_name
        new_item[1] = new_start_date
        new_item[2] = new_end_date

        table.item(selected_item, values=new_item)

        trip_table()
        popup_window.destroy()

    popup_window = Toplevel(frame)
    popup_window.title("Edit Trip")

    trip_name_label = Label(popup_window, text="Trip Name:")
    trip_name_label.grid(row=0, column=0)
    trip_name_entry = Entry(popup_window)
    trip_name_entry.grid(row=0, column=1)
    trip_name_entry.insert(0, values[0])

    start_date_label = Label(popup_window, text="Start Date:")
    start_date_label.grid(row=1, column=0)
    start_date_entry = DateEntry(popup_window)
    start_date_entry.grid(row=1, column=1)
    start_date_entry.set_date(datetime.strptime(values[1], "%Y-%m-%d").date())

    end_date_label = Label(popup_window, text="End Date:")
    end_date_label.grid(row=2, column=0)
    end_date_entry = DateEntry(popup_window)
    end_date_entry.grid(row=2, column=1)
    end_date_entry.set_date(datetime.strptime(values[2], "%Y-%m-%d").date())

    update_button = Button(popup_window, text="Update", command=update_trip)
    update_button.grid(row=3, columnspan=2)


#Trip CRUDL (Delete)
def delete_row(selected_item):
    trip_name = table.item(selected_item)['values'][0]

    window = tk.Toplevel()
    window.title("Delete Trip")

    label = tk.Label(window, text=f"Are you sure you want to delete this trip?")
    label.grid(row=0, rowspan=2, column=0, columnspan=2, sticky="news", padx=5, pady=5)

    def confirm_delete():
        cursor = db.cursor()
        query = "DELETE FROM trips WHERE trip_name = %s"
        cursor.execute(query, (trip_name,))
        db.commit()

        window.destroy()
        table.delete(selected_item)

    def cancel_delete():
        window.destroy()

    confirm_button = tk.Button(window, text="Confirm", command=confirm_delete)
    confirm_button.grid(row=2, column=0, sticky="news", padx=5, pady=5)

    cancel_button = tk.Button(window, text="Cancel", command=cancel_delete)
    cancel_button.grid(row=2, column=1, sticky="news", padx=5, pady=5)

    window.attributes("-topmost", True)

    window.mainloop()


#Itinerary CRUDL (List)
def itinerary_table(event):
    selected_item = table.selection()
    if selected_item:
        primary_key_value = table.item(selected_item)['values'][0]

        table2.delete(*table2.get_children())

        cursor = db.cursor()
        query = "SELECT i.itinerary_name FROM trips t JOIN itineraries i ON t.trip_id = i.trip_id WHERE trip_name = %s"
        cursor.execute(query, (primary_key_value,))
        data = cursor.fetchall()

        for index, row in enumerate(data):
            table2.insert(parent='', index='end', iid=index, text=index, values=row, tags=column_names2)


def fetch_itinerary_id(values):
    itinerary_name = values[0]
    cursor = db.cursor()
    query = "SELECT itinerary_id FROM itineraries WHERE itinerary_name = %s"
    cursor.execute(query, (itinerary_name,))
    result = cursor.fetchone()

    if result:
        return result[0]

    return None


#Itinerary CRUDL (Create)
def create_itinerary(selected_item):
    def submit_itinerary():
        new_itinerary_name = itinerary_name_entry.get()
        selected_trip_name = table.item(selected_item)['values'][0]
        cursor = db.cursor()
        query = "SELECT trip_id FROM trips WHERE trip_name = %s"
        cursor.execute(query, (selected_trip_name,))
        result = cursor.fetchone()
        if result:
            selected_trip_id = result[0]
            cursor.execute("SELECT MAX(itinerary_id) FROM itineraries")
            result = cursor.fetchone()
            if result[0]:
                new_itinerary_id = result[0] + 1
            else:
                new_itinerary_id = 1

            cursor = db.cursor()
            query = "INSERT INTO itineraries (itinerary_id, itinerary_name, trip_id) VALUES (%s, %s, %s)"
            values = (new_itinerary_id, new_itinerary_name, selected_trip_id)
            cursor.execute(query, values)
            db.commit()

            itinerary_table('')
            popup_window.destroy()

    # Create a pop-up window
    popup_window = Toplevel(frame2)
    popup_window.title("Create New Itinerary")

    # Add Entry widget for itinerary name
    itinerary_name_label = Label(popup_window, text="Itinerary Name:")
    itinerary_name_label.grid(row=0, column=0)
    itinerary_name_entry = Entry(popup_window)
    itinerary_name_entry.grid(row=0, column=1)

    # Add a button to submit the data
    submit_button = Button(popup_window, text="Submit", command=submit_itinerary)
    submit_button.grid(row=2, columnspan=2)


#Itinerary CRUDL (Read)
def itinerary_search(event):
    selected_item = table.focus()
    selected_values = table.item(selected_item)['values']
    search_query = search_entry2.get()

    table2.delete(*table2.get_children())
    cursor = db.cursor()

    query = "SELECT i.itinerary_name FROM trips t JOIN itineraries i ON t.trip_id = i.trip_id WHERE itinerary_name LIKE '%{}%'".format(search_query)

    if selected_values:
        query += " AND trip_name = '{}'".format(selected_values[0])

        try:
            cursor.execute(query)
            results = cursor.fetchall()

            for index, result in enumerate(results):
                table2.insert(parent='', index='end', iid=index, text=index, values=result)

        except mc.Error as error:
            print("Error while performing search:", error)


def popup_menu2(event):
    if event.num == 3:
        selected_item = table2.selection()
        if selected_item:
            values = table2.item(selected_item)['values']
            itinerary_id = fetch_itinerary_id(values)
            menu = tk.Menu(root, tearoff=0)
            menu.add_command(label="Edit", command=lambda: edit_itinerary(selected_item, values, itinerary_id))
            menu.add_command(label="Delete", command=lambda: delete_itinerary(selected_item))

            x = root.winfo_pointerx()
            y = root.winfo_pointery()

            menu.post(x, y)


#Itinerary CRUDL (Update)
def edit_itinerary(selected_item, values, itinerary_id):
    def update_itinerary():
        new_itinerary_name = new_itinerary_name_entry.get()

        cursor = db.cursor()
        query = "UPDATE itineraries SET itinerary_name = %s WHERE itinerary_id = %s"
        new_values = (new_itinerary_name, itinerary_id)
        cursor.execute(query, new_values)
        db.commit()

        new_item = list(values)
        new_item[0] = new_itinerary_name

        table2.item(selected_item, values=new_item)

        itinerary_table('')
        popup_window.destroy()

    if not selected_item:
        return

    popup_window = Toplevel(frame2)
    popup_window.title("Edit Itinerary")

    itinerary_name_label = Label(popup_window, text="Itinerary Name:")
    itinerary_name_label.grid(row=0, column=0)
    new_itinerary_name_entry = Entry(popup_window)
    new_itinerary_name_entry.grid(row=0, column=1)
    new_itinerary_name_entry.insert(0, values[0])

    update_button = Button(popup_window, text="Update", command=update_itinerary)
    update_button.grid(row=1, columnspan=2)


#Itinerary CRUDL (Delete)
def delete_itinerary(selected_item):
    itinerary_name = table2.item(selected_item)['values'][0]

    window = tk.Toplevel()
    window.title("Delete Itinerary")

    label = tk.Label(window, text=f"Are you sure you want to delete this itinerary?")
    label.grid(row=0, rowspan=2, column=0, columnspan=2, sticky="news", padx=5, pady=5)

    def confirm_delete():
        cursor = db.cursor()
        query = "DELETE FROM itineraries WHERE itinerary_name = %s"
        cursor.execute(query, (itinerary_name,))
        db.commit()

        window.destroy()
        table2.delete(selected_item)

    def cancel_delete():
        window.destroy()

    confirm_button = tk.Button(window, text="Confirm", command=confirm_delete)
    confirm_button.grid(row=2, column=0, sticky="news", padx=5, pady=5)

    cancel_button = tk.Button(window, text="Cancel", command=cancel_delete)
    cancel_button.grid(row=2, column=1, sticky="news", padx=5, pady=5)

    window.attributes("-topmost", True)

    window.mainloop()


#Activity CRUDL (List)
def activity_table(event):
    selected_item = table2.selection()
    if selected_item:
        primary_key_value = table2.item(selected_item)['values'][0]

        table3.delete(*table3.get_children())

        cursor = db.cursor()
        query = "SELECT a.activity_title, a.day, a.time, d.destination_name " \
                "FROM itineraries i JOIN activities a ON i.itinerary_id = a.itinerary_id " \
                "LEFT JOIN destinations d ON a.destination_id = d.destination_id " \
                "WHERE i.itinerary_name = %s AND i.itinerary_id = %s ORDER BY day, time"
        cursor.execute(query, (primary_key_value, fetch_itinerary_id(primary_key_value)))
        data = cursor.fetchall()

        for index, row in enumerate(data):
            new_row = list(row)
            new_row[0] = row[0]
            new_row[1] = row[1]
            table_time_str = str(row[2])
            table_time = datetime.strptime(table_time_str, '%H:%M:%S')
            new_row[2] = table_time.strftime('%I:%M %p')
            new_row[3] = row[3]
            table3.insert(parent='', index='end', iid=index, text=index, values=new_row, tags=column_names3)


def fetch_activity_id(values):
    activity_title = values[0]
    cursor = db.cursor()
    query = "SELECT activity_id FROM activities WHERE activity_title = %s"
    cursor.execute(query, (activity_title,))
    result = cursor.fetchone()

    if result:
        return result[0]

    return None


#Activity CRUDL (Create)
def create_activity(selected_item):
    def add_activity():
        new_activity = activity_entry.get()
        new_day = day_combobox.get()
        hour = int(spinbox_hour.get())
        minute = int(spinbox_minute.get())
        time_period = time_combobox.get()
        new_time_table = f"{hour}:{minute:02d} {time_period}"
        if hour == 12:
            if time_period == "AM":
                hour -= 12
        elif hour != 12 and time_period == "PM":
            hour += 12
        new_time_submit = f"{hour:02d}:{minute:02d}:{00:02d}"
        new_destination = destination_combobox.get()

        if not new_activity or not new_day or not new_time_table or not new_destination:
            messagebox.showwarning("Incomplete Fields", "Please fill in all fields.")
            return

        # Retrieve the itinerary_id based on the selected itinerary
        selected_itinerary = table2.item(table2.selection())['values'][0]
        cursor.execute("SELECT itinerary_id, trip_id FROM itineraries WHERE itinerary_name = %s", (selected_itinerary,))
        result = cursor.fetchone()
        itinerary_id = result[0]
        trip_id = result[1]

        # Retrieve the destination_id based on the selected destination
        cursor.execute("SELECT destination_id FROM destinations WHERE destination_name = %s", (new_destination,))
        destination_id = cursor.fetchone()[0]

        # Generate activity_id
        cursor.execute("SELECT MAX(activity_id) FROM activities")
        max_activity_id = cursor.fetchone()[0]
        if max_activity_id is None:
            max_activity_id = 0
        activity_id = max_activity_id + 1

        # Insert the new activity into the activities table
        query = "INSERT INTO activities (activity_id, itinerary_id, activity_title, day, time, destination_id) " \
                "VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (activity_id, itinerary_id, new_activity, new_day, new_time_submit, destination_id))
        db.commit()

        new_item = [new_activity, new_day, new_time_table, new_destination]
        table3.insert('', 'end', values=new_item)

        popup_window.destroy()

    popup_window = tk.Toplevel(activity_frame)
    popup_window.title("Add Activity")

    activity_label = tk.Label(popup_window, text="Activity:")
    activity_label.grid(row=0, column=0)
    activity_entry = tk.Entry(popup_window)
    activity_entry.grid(row=0, column=1, columnspan=2, sticky="news")

    day_label = tk.Label(popup_window, text="Day:")
    day_label.grid(row=1, column=0)

    cursor = db.cursor()
    query = "SELECT t.start_date, t.end_date FROM trips t JOIN itineraries i ON t.trip_id = i.trip_id WHERE i.itinerary_name = %s"
    cursor.execute(query, (table2.item(selected_item)['values'][0],))
    result = cursor.fetchone()
    range_num = result[1].toordinal() - result[0].toordinal() + 1
    values = [str(i) for i in range(1, range_num + 1)]
    day_combobox = ttk.Combobox(popup_window, values=values)
    day_combobox.grid(row=1, column=1, columnspan=2)

    time_label = tk.Label(popup_window, text="Time:")
    time_label.grid(row=2, column=0)
    frame5 = Frame(popup_window)
    frame5.grid(row=2, column=1, columnspan=2, sticky="news")
    spinbox_hour = tk.Spinbox(frame5, from_=1, to=12, width=2)
    spinbox_hour.grid(row=0, column=1)
    time_label_colon = tk.Label(frame5, text=":")
    time_label_colon.grid(row=0, column=2)
    spinbox_minute = tk.Spinbox(frame5, from_=0, to=59, width=2)
    spinbox_minute.grid(row=0, column=3)
    time_combobox = ttk.Combobox(frame5, values=["AM", "PM"], width=5)
    time_combobox.grid(row=0, column=4)

    destination_label = tk.Label(popup_window, text="Destination:")
    destination_label.grid(row=3, column=0)

    # Fetch destination names from the database and set them as values for the Combobox
    cursor.execute("SELECT destination_name FROM destinations")
    destination_names = [row[0] for row in cursor.fetchall()]
    destination_combobox = ttk.Combobox(popup_window, values=destination_names)
    destination_combobox.grid(row=3, column=1, columnspan=2, sticky="news")

    add_button = tk.Button(popup_window, text="Submit", command=add_activity)
    add_button.grid(row=4, columnspan=3)


#Activity CRUDL (Read)
def activity_search(event):
    selected_item = table2.focus()
    selected_values = table2.item(selected_item)['values']
    search_query = search_entry3.get()

    table3.delete(*table3.get_children())
    cursor = db.cursor()

    query = "SELECT a.activity_title, a.day, a.time, d.destination_name " \
            "FROM itineraries i JOIN activities a ON i.itinerary_id = a.itinerary_id " \
            "LEFT JOIN destinations d ON a.destination_id = d.destination_id " \
            "WHERE a.activity_title LIKE '%{}%'".format(search_query)

    if selected_values:
        query += " AND i.itinerary_name = '{}'".format(selected_values[0])

        try:
            cursor.execute(query)
            results = cursor.fetchall()

            for index, result in enumerate(results):
                table3.insert(parent='', index='end', iid=index, text=index, values=result)

        except mc.Error as error:
            print("Error while performing search:", error)


def popup_menu3(event):
    if event.num == 3:
        selected_item = table3.selection()
        if selected_item:
            values = table3.item(selected_item)['values']
            activity_id = fetch_activity_id(values)
            menu = tk.Menu(root, tearoff=0)
            menu.add_command(label="Edit", command=lambda: edit_activity(selected_item, values, activity_id))
            menu.add_command(label="Delete", command=lambda: delete_activity(selected_item))

            x = root.winfo_pointerx()
            y = root.winfo_pointery()

            menu.post(x, y)


#Activity CRUDL (Update)
def edit_activity(selected_item, values, activity_id):
    def update_activity():
        # Retrieve the updated values from the input fields
        updated_activity = activity_entry.get()
        updated_day = day_combobox.get()
        updated_hour = int(spinbox_hour.get())
        updated_minute = int(spinbox_minute.get())
        updated_time_period = time_combobox.get()
        updated_time_table = f"{updated_hour}:{updated_minute:02d} {updated_time_period}"
        if updated_hour == 12:
            if updated_time_period == "AM":
                updated_hour -= 12
        elif updated_hour != 12 and updated_time_period == "PM":
            updated_hour += 12
        updated_time_submit = f"{updated_hour:02d}:{updated_minute:02d}:{00:02d}"
        updated_destination = destination_combobox.get()

        if not updated_activity or not updated_day or not updated_time_table or not updated_destination:
            messagebox.showwarning("Incomplete Fields", "Please fill in all fields.")
            return

        # Retrieve the destination_id based on the selected destination
        cursor.execute("SELECT destination_id FROM destinations WHERE destination_name = %s",
                       (updated_destination,))
        destination_id = cursor.fetchone()[0]

        # Update the activity in the activities table
        query = "UPDATE activities SET activity_title = %s, day = %s, time = %s, destination_id = %s " \
                "WHERE activity_id = %s"
        cursor.execute(query, (updated_activity, updated_day, updated_time_submit, destination_id, activity_id))
        db.commit()

        # Update the activity in the GUI
        updated_item = [updated_activity, updated_day, updated_time_table, updated_destination]
        table3.item(selected_item, values=updated_item)
        activity_table('')

        popup_window.destroy()

    # Create the edit activity popup window
    popup_window = tk.Toplevel(activity_frame)
    popup_window.title("Edit Activity")

    # Get the current values of the selected activity
    current_activity = values[0]
    current_day = values[1]
    current_time = values[2]
    current_destination = values[3]

    # Create and populate the input fields with the current values
    activity_label = tk.Label(popup_window, text="Activity:")
    activity_label.grid(row=0, column=0)
    activity_entry = tk.Entry(popup_window)
    activity_entry.insert(0, current_activity)
    activity_entry.grid(row=0, column=1, columnspan=2, sticky="news")

    day_label = tk.Label(popup_window, text="Day:")
    day_label.grid(row=1, column=0)

    cursor = db.cursor()
    query = "SELECT t.start_date, t.end_date FROM trips t JOIN itineraries i ON t.trip_id = i.trip_id JOIN activities a ON i.itinerary_id = a.itinerary_id WHERE a.activity_title = %s"
    cursor.execute(query, (table3.item(selected_item)['values'][0],))
    result = cursor.fetchone()
    range_num = result[1].toordinal() - result[0].toordinal() + 1
    day_values = [str(i) for i in range(1, range_num + 1)]
    day_combobox = ttk.Combobox(popup_window, values=day_values)
    day_combobox.set(current_day)
    day_combobox.grid(row=1, column=1, columnspan=2)

    time_label = tk.Label(popup_window, text="Time:")
    time_label.grid(row=2, column=0)
    frame5 = Frame(popup_window)
    frame5.grid(row=2, column=1, columnspan=2, sticky="news")
    spinbox_hour = tk.Spinbox(frame5, from_=1, to=12, width=2)
    spinbox_hour.grid(row=0, column=1)
    time_label_colon = tk.Label(frame5, text=":")
    time_label_colon.grid(row=0, column=2)
    spinbox_minute = tk.Spinbox(frame5, from_=0, to=59, width=2)
    spinbox_minute.grid(row=0, column=3)
    time_combobox = ttk.Combobox(frame5, values=["AM", "PM"], width=5)
    time_combobox.set(current_time.split()[1])
    time_combobox.grid(row=0, column=4)

    destination_label = tk.Label(popup_window, text="Destination:")
    destination_label.grid(row=3, column=0)
    cursor.execute("SELECT destination_name FROM destinations")
    destination_names = [row[0] for row in cursor.fetchall()]
    destination_combobox = ttk.Combobox(popup_window, values=destination_names)
    destination_combobox.set(current_destination)
    destination_combobox.grid(row=3, column=1, columnspan=2, sticky="news")

    update_button = tk.Button(popup_window, text="Update", command=update_activity)
    update_button.grid(row=4, columnspan=3)


#Activity CRUDL (Delete)
def delete_activity(selected_item):
    activity_title = table3.item(selected_item)['values'][0]

    window = tk.Toplevel()
    window.title("Delete Activity")

    label = tk.Label(window, text=f"Are you sure you want to delete this activity?")
    label.grid(row=0, rowspan=2, column=0, columnspan=2, sticky="news", padx=5, pady=5)

    def confirm_delete():
        cursor = db.cursor()

        query = "DELETE FROM activities WHERE activity_title = %s"
        cursor.execute(query, (activity_title,))
        db.commit()

        window.destroy()
        table3.delete(selected_item)

    def cancel_delete():
        window.destroy()

    confirm_button = tk.Button(window, text="Confirm", command=confirm_delete)
    confirm_button.grid(row=2, column=0, sticky="news", padx=5, pady=5)

    cancel_button = tk.Button(window, text="Cancel", command=cancel_delete)
    cancel_button.grid(row=2, column=1, sticky="news", padx=5, pady=5)

    window.attributes("-topmost", True)

    window.mainloop()


#Destination CRUDL (List)
def destination_table():
    table4.delete(*table4.get_children())

    cursor = db.cursor()
    cursor.execute("SELECT destination_name, destination_address FROM destinations")
    data = cursor.fetchall()

    for index, row in enumerate(data):
        table4.insert(parent='', index='end', iid=index, text=index, values=row, tags=column_names)


def fetch_destination_id(values):
    destination_name = values[0]
    cursor = db.cursor()
    query = "SELECT destination_id FROM destinations WHERE destination_name = %s"
    cursor.execute(query, (destination_name,))
    result = cursor.fetchone()

    if result:
        return result[0]

    return None


#Destination CRUDL (Create)
def create_destination():
    def submit_destination():
        destination_name = destination_name_entry.get()
        destination_address = destination_address_entry.get()

        if not destination_name or not destination_address:
            messagebox.showwarning("Incomplete Fields", "Please fill in all fields.")
            return

        cursor = db.cursor()
        cursor.execute("SELECT MAX(destination_id) FROM destinations")
        max_destination_id = cursor.fetchone()[0]
        if max_destination_id is None:
            destination_id = 1
        else:
            destination_id = max_destination_id + 1

        query = "INSERT INTO destinations (destination_id, destination_name, destination_address) VALUES (%s, %s, %s)"
        values = (destination_id, destination_name, destination_address)
        cursor.execute(query, values)
        db.commit()

        destination_table()
        popup_window.destroy()

    popup_window = Toplevel(root)
    popup_window.title("Create New Destination")

    destination_name_label = Label(popup_window, text="Destination Name:")
    destination_name_label.grid(row=0, column=0)
    destination_name_entry = Entry(popup_window)
    destination_name_entry.grid(row=0, column=1)

    destination_address_label = Label(popup_window, text="Destination Address:")
    destination_address_label.grid(row=1, column=0)
    destination_address_entry = Entry(popup_window)
    destination_address_entry.grid(row=1, column=1)

    destination_name_entry.focus()

    submit_button = Button(popup_window, text="Submit", command=submit_destination)
    submit_button.grid(row=2, columnspan=2)


#Destination CRUDL (Read)
def destination_search(event):
    search_query = search_entry4.get()
    table4.delete(*table4.get_children())
    cursor = db.cursor()


    query = "SELECT destination_name, destination_address FROM destinations WHERE destination_name LIKE '%{}%' OR destination_address LIKE '%{}%'".format(search_query, search_query)

    try:
        cursor.execute(query)
        results = cursor.fetchall()

        for index, result in enumerate(results):
            table4.insert(parent='', index='end', iid=index, text=index, values=result)

    except mc.Error as error:
        print("Error while performing search:", error)


def popup_menu4(event):
    if event.num == 3:
        selected_item = table4.selection()
        if selected_item:
            values = table4.item(selected_item)['values']

            destination_id = fetch_destination_id(values)

            menu = tk.Menu(root, tearoff=0)
            menu.add_command(label="Edit", command=lambda: edit_destination(selected_item, values, destination_id))
            menu.add_command(label="Delete", command=lambda: delete_destination(selected_item))

            x = root.winfo_pointerx()
            y = root.winfo_pointery()

            menu.post(x, y)


#Destination CRUDL (Update)
def edit_destination(selected_item, values, destination_id):
    def update_destination():
        new_destination_name = destination_name_entry.get()
        new_destination_address = destination_address_entry.get()

        if not new_destination_name or not new_destination_address:
            messagebox.showwarning("Incomplete Fields", "Please fill in all fields.")
            return

        cursor = db.cursor()
        query = "UPDATE destinations SET destination_name = %s, destination_address = %s WHERE destination_id = %s"
        new_values = (new_destination_name, new_destination_address, destination_id)
        cursor.execute(query, new_values)
        db.commit()

        new_item = list(values)
        new_item[0] = new_destination_name
        new_item[1] = new_destination_address

        table4.item(selected_item, values=new_item)

        # Call any additional function to update the destination table
        destination_table()

        popup_window.destroy()

    popup_window = Toplevel(frame)
    popup_window.title("Edit Destination")

    destination_name_label = Label(popup_window, text="Destination Name:")
    destination_name_label.grid(row=0, column=0)
    destination_name_entry = Entry(popup_window)
    destination_name_entry.grid(row=0, column=1)
    destination_name_entry.insert(0, values[0])

    destination_address_label = Label(popup_window, text="Destination Address:")
    destination_address_label.grid(row=1, column=0)
    destination_address_entry = Entry(popup_window)
    destination_address_entry.grid(row=1, column=1)
    destination_address_entry.insert(0, values[1])

    update_button = Button(popup_window, text="Update", command=update_destination)
    update_button.grid(row=2, columnspan=2)


#Destination CRUDL (Delete)
def delete_destination(selected_item):
    destination_name = table4.item(selected_item)['values'][0]

    window = tk.Toplevel()
    window.title("Delete Destination")

    label = tk.Label(window, text=f"Are you sure you want to delete this destination?")
    label.grid(row=0, rowspan=2, column=0, columnspan=2, sticky="news", padx=5, pady=5)

    def confirm_delete():
        cursor = db.cursor()
        query = "DELETE FROM destinations WHERE destination_name = %s"
        cursor.execute(query, (destination_name,))
        db.commit()

        window.destroy()
        table4.delete(selected_item)

    def cancel_delete():
        window.destroy()

    confirm_button = tk.Button(window, text="Confirm", command=confirm_delete)
    confirm_button.grid(row=2, column=0, sticky="news", padx=5, pady=5)

    cancel_button = tk.Button(window, text="Cancel", command=cancel_delete)
    cancel_button.grid(row=2, column=1, sticky="news", padx=5, pady=5)

    window.attributes("-topmost", True)

    window.mainloop()


root = Tk()
root.geometry("900x600")
root.title("Travel Planner")
root.resizable(False, False)
root.configure(bg="#a0d2e7")

frame = Frame(root, width=300, height=600, bg="#81B1D5")
frame.grid(row=0, rowspan=2, column=0, sticky="news")
frame.rowconfigure(1, minsize=10)
frame.rowconfigure(4, minsize=20)


title = Label(frame, text="Travel Planner", font=('bold', 20), bg=frame['bg'], fg="white")
title.grid(row=0, column=0, columnspan=5)

search_entry = tk.Entry(frame, width=24, font=('', 13))
search_entry.insert(0, "Search Trip")
search_entry.grid(row=2, column=1, columnspan=2, sticky="news")
search_entry.bind('<FocusIn>', lambda event: search_entry.delete(0, "end"))
search_entry.bind('<KeyRelease>', perform_search)

image = Image.open("magnifying-glass.png")
image = image.resize((20, 20))
photo = ImageTk.PhotoImage(image)

image_label = Label(frame, image=photo, bg=frame["bg"], width=20, height=20)
image_label.grid(row=2, column=3, sticky="w")

create_button = tk.Button(frame, text="Add Trip", width=29, command=create_trip)
create_button.grid(row=3, column=0, columnspan=5)

trip_frame = LabelFrame(frame, text="Trip Information")
trip_frame.grid(row=5, column=0, columnspan=5, sticky="news")
trip_frame.rowconfigure(0)

table = ttk.Treeview(trip_frame, show="headings", height=20)
column_names = ["Trip", "From", "To"]
table["columns"] = column_names
for column_name in column_names:
    table.heading(column_name, text=column_name)
    if column_name == "Trip":
        table.column(column_name, width=120)
    elif column_name == "From":
        table.column(column_name, width=70)
    elif column_name == "To":
        table.column(column_name, width=70)
    table.tag_configure(column_name, anchor='center')
table.grid(row=0, column=0, padx=5, pady=5, sticky="news")
table.bind("<<TreeviewSelect>>", itinerary_table)
table.bind("<Button-3>", popup_menu)

scrollbar = ttk.Scrollbar(trip_frame, orient="vertical", command=table.yview)
scrollbar.grid(row=0, column=1, sticky="ns")
table.configure(yscrollcommand=scrollbar.set)

for widget in frame.winfo_children():
    widget.grid_configure(padx=5, pady=3)

frame2 = Frame(root, width=200, height=300, bg="#26408b", padx=5, pady=5)
frame2.grid(row=0, column=1, sticky="news")

itinerary_title = Label(frame2, text="Itineraries", font=('', 14), bg=frame2['bg'], fg="white")
itinerary_title.grid(row=0, column=0, sticky="w")

search_entry2 = tk.Entry(frame2, font=('', 13), width=12)
search_entry2.insert(0, "Search Itinerary")
search_entry2.grid(row=0, column=1, sticky="ew")
search_entry2.bind('<FocusIn>', lambda event: search_entry2.delete(0, "end"))
search_entry2.bind('<KeyRelease>', itinerary_search)

add_itinerary = tk.Button(frame2, text="Add Itinerary", command=lambda: create_itinerary(table.focus()))
add_itinerary.grid(row=1, column=0, columnspan=2, sticky="news")

itinerary_frame = LabelFrame(frame2, text="Itinerary Information")
itinerary_frame.grid(row=2, column=0, columnspan=2, sticky="news")

table2 = ttk.Treeview(itinerary_frame, show="headings", height=9)
column_names2 = ["Itinerary"]
table2["columns"] = column_names2
for column_name in column_names2:
    table2.heading(column_name, text=column_name)
    table2.column(column_name, width=170)
    table2.tag_configure(column_name, anchor='center')
table2.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="news")
table2.bind("<<TreeviewSelect>>", activity_table)
table2.bind("<Button-3>", popup_menu2)

scrollbar2 = ttk.Scrollbar(itinerary_frame, orient="vertical", command=table2.yview)
scrollbar2.grid(row=0, column=2, sticky="ns")
table2.configure(yscrollcommand=scrollbar2.set)

for widget in frame2.winfo_children():
    widget.grid_configure(pady=4)

frame3 = Frame(root, width=300, height=300, bg="#3d60a7", padx=5, pady=5)
frame3.grid(row=1, column=1, columnspan=2, sticky="news")

activity_title = Label(frame3, text="Activities", font=('', 16), bg=frame3['bg'], fg="white")
activity_title.grid(row=0, column=0, sticky="nws")

search_entry3 = tk.Entry(frame3, font=('', 13))
search_entry3.insert(0, "Search Activity")
search_entry3.grid(row=0, column=1, columnspan=4, sticky="ew", padx=(0, 10))
search_entry3.bind('<FocusIn>', lambda event: search_entry3.delete(0, "end"))
search_entry3.bind('<KeyRelease>', activity_search)

add_activity = tk.Button(frame3, text="Add Activity", command=lambda: create_activity(table2.focus()))
add_activity.grid(row=0, column=5, columnspan=5, sticky="ew")

activity_frame = LabelFrame(frame3, text="Activity Information")
activity_frame.grid(row=1, column=0, columnspan=10, sticky="news")

table3 = ttk.Treeview(activity_frame, show="headings", height=9)
column_names3 = ["Activity", "Day", "Time", "Destination"]
table3["columns"] = column_names3
for column_name in column_names3:
    table3.heading(column_name, text=column_name)
    if column_name == "Activity":
        table3.column(column_name, width=205)
    elif column_name == "Day":
        table3.column(column_name, width=70)
    elif column_name == "Time":
        table3.column(column_name, width=100)
    elif column_name == "Destination":
        table3.column(column_name, width=180)
    table3.tag_configure(column_name, anchor='center')
table3.grid(row=1, column=0, columnspan=5, padx=5, pady=5, sticky="news")
table3.bind("<Button-3>", popup_menu3)

scrollbar3 = ttk.Scrollbar(activity_frame, orient="vertical", command=table3.yview)
scrollbar3.grid(row=1, column=5, sticky="ns")
table3.configure(yscrollcommand=scrollbar3.set)

frame4 = Frame(root, width=400, height=300, bg="#81b1d5", padx=5, pady=5)
frame4.grid(row=0, column=2, columnspan=2, sticky="news")

destination_title = Label(frame4, text="Destinations       ", font=('', 14), bg=frame4['bg'], fg="white")
destination_title.grid(row=0, column=0, sticky="w")

search_entry4 = tk.Entry(frame4, font=('', 13), width=25)
search_entry4.insert(0, "Search Destination")
search_entry4.grid(row=0, column=1, columnspan=2, sticky="ew")
search_entry4.bind('<FocusIn>', lambda event: search_entry4.delete(0, "end"))
search_entry4.bind('<KeyRelease>', destination_search)

add_destination = tk.Button(frame4, text="Add Destination", command=create_destination)
add_destination.grid(row=1, column=0, columnspan=3, sticky="news")

destination_frame = LabelFrame(frame4, text="Destination Information")
destination_frame.grid(row=2, column=0, columnspan=3, sticky="news")

table4 = ttk.Treeview(destination_frame, show="headings", height=9)
column_names4 = ["Destination", "Address"]
table4["columns"] = column_names4
for column_name in column_names4:
    table4.heading(column_name, text=column_name)
    if column_name == "Destination":
        table4.column(column_name, width=120)
    elif column_name == "Address":
        table4.column(column_name, width=220)
    table4.tag_configure(column_name, anchor='center')
table4.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="news")
table4.bind("<Button-3>", popup_menu4)

scrollbar4 = ttk.Scrollbar(destination_frame, orient="vertical", command=table4.yview)
scrollbar4.grid(row=1, column=3, sticky="ns")
table4.configure(yscrollcommand=scrollbar4.set)

for widget in frame4.winfo_children():
    widget.grid_configure(pady=4)

trip_table()
destination_table()
root.mainloop()
