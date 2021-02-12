import datetime
from datetime import date
from datetime import datetime
import tkinter as tk
from tkinter import *
import sqlite3

placeholder = 0


class PageApplication(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # The container is where we'll stack a bunch of frames on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, ReviewPage, WritingPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            frame.grid(row=0, column=0, sticky="news")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        def go_to_review():
            global placeholder
            storage = sqlite3.connect('entries.db')
            s = storage.cursor()
            s.execute("""CREATE TABLE IF NOT EXISTS entries(entry TEXT, date TEXT, time TEXT)""")

            s.execute("SELECT *, oid FROM entries")
            list_of_entries = s.fetchall()

            if len(list_of_entries) > 0:
                placeholder = 0

            controller.show_frame("PageOne")

        start = Button(self, text="write", bg="cyan", command=lambda: controller.show_frame("PageTwo"))
        start.place(relx=0.5, rely=0.4, height=50, width=100, anchor=CENTER)

        finish = Button(self, text="review", bg="lime", command=lambda: go_to_review())
        finish.place(relx=0.5, rely=0.6, height=50, width=100, anchor=CENTER)


class ReviewPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        global placeholder

        # Displays the current entry that is chosen as well as its time and date
        def display_entry():
            storage = sqlite3.connect('entries.db')
            s = storage.cursor()

            notes.config(state=NORMAL)

            notes.delete("1.0", END)

            s.execute("SELECT *, oid FROM entries")
            list_of_entries = s.fetchall()
            if len(list_of_entries) != 0 and placeholder < len(list_of_entries):
                notes.insert('1.0', list_of_entries[placeholder][1] + "\n" + list_of_entries[placeholder][2] + "\n\n"
                             + list_of_entries[placeholder][0])
                num_check.config(text="Entry #" + str(placeholder + 1))

            if len(list_of_entries) == 0:
                num_check.config(text="")

            # Disables the notes from being changed
            notes.config(state=DISABLED)

        # Allows the user to switch to a higher entry
        def add_num():
            global placeholder

            storage = sqlite3.connect('entries.db')
            s = storage.cursor()
            s.execute("SELECT *, oid FROM entries")
            list_of_entries = s.fetchall()

            # If the placeholder is already too high, it makes sure the user cannot go further
            if placeholder < len(list_of_entries) - 1:
                placeholder += 1

            # Gives current number of entry
            num_check.config(text="Entry #" + str(placeholder + 1))
            display_entry()

        # Allows the user to switch to a lower entry
        def sub_num():
            global placeholder

            # If the placeholder is already too low, it makes sure the user cannot go further
            if placeholder > 0:
                placeholder -= 1

            # Gives current number of entry
            num_check.config(text="Entry #" + str(placeholder + 1))
            display_entry()

        # Allows user to go to the first entry
        def go_to_first():
            global placeholder

            storage = sqlite3.connect('entries.db')
            s = storage.cursor()
            s.execute("SELECT *, oid FROM entries")
            list_of_entries = s.fetchall()

            placeholder = len(list_of_entries) - 1

            num_check.config(text="Entry #" + str(placeholder + 1))
            display_entry()

        # Allows user to go the last entry
        def go_to_last():
            global placeholder

            placeholder = 0

            num_check.config(text="Entry #" + str(placeholder + 1))
            display_entry()

        # Deletes the current entry that the user has chosen
        def delete_entry():
            global placeholder

            storage = sqlite3.connect('entries.db')
            s = storage.cursor()
            s.execute("SELECT *, oid FROM entries")
            list_of_entries = s.fetchall()

            if len(list_of_entries) != 0:
                s.execute("DELETE from entries WHERE oid = " + str(list_of_entries[placeholder][-1]))

                storage.commit()
                storage.close()

                sub_num()
                add_num()

        def clock():
            curr_time.config(text=datetime.now().time().strftime('%I:%M:%S%p'))
            display_entry()
            curr_time.after(1000, clock)

        del_button = Button(self, text="DELETE", bg="red", fg="white", height=3, width=12, command=delete_entry)
        del_button.pack(side="top")

        notes = Text(self, height=30, width=300, wrap=WORD)
        notes.pack(side="bottom")

        num_check = Label(self, text="Entry #" + str(placeholder + 1), font=(None, 15), pady=6)
        num_check.pack(side="bottom")

        fir_button = Button(self, text=">>", font=(None, 20), command=go_to_first)
        fir_button.pack(side="right")

        las_button = Button(self, text="<<", font=(None, 20), command=go_to_last)
        las_button.pack(side="left")

        add_button = Button(self, text=">", font=(None, 20), command=add_num)
        add_button.pack(side="right")

        sub_button = Button(self, text="<", font=(None, 20), command=sub_num)
        sub_button.pack(side="left")

        curr_time = Label(self, text=datetime.now().time().strftime('%I:%M:%S%p'))

        back_button = Button(self, text="go back", command=lambda: controller.show_frame("StartPage"))
        back_button.place(anchor=NW)

        clock()


class WritingPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # Enters a new entry into the database
        def enter_entry():
            storage = sqlite3.connect('entries.db')
            s = storage.cursor()
            if notes.get("1.0", END) != "":
                s.execute("INSERT INTO entries VALUES (:notes, :date, :time)",
                          {
                              'notes': notes.get("1.0", END),
                              'date': date.today().strftime("%B %d, %Y"),
                              'time': datetime.now().time().strftime('%I:%M:%S%p')
                          })

            storage.commit()
            storage.close()

            notes.delete("1.0", END)
            num_entries.config(text="Currently " + str(num_of_list()) + " Entries")

        # Helps indicate the current length of the database
        def num_of_list():
            storage = sqlite3.connect('entries.db')
            s = storage.cursor()

            # Used in case the table has not already been created
            s.execute("""CREATE TABLE IF NOT EXISTS entries(entry TEXT, date TEXT, time TEXT)""")

            s.execute("SELECT *, oid FROM entries")
            list_of_entries = s.fetchall()

            return len(list_of_entries)

        # Clock that helps user indicate current time
        def clock():
            curr_time.config(text=datetime.now().time().strftime('%I:%M:%S%p'))
            curr_time.after(1000, clock)
            num_entries.config(text="Currently " + str(num_of_list()) + " Entries")
            num_entries.after(1000, num_of_list)

        # Is the button for putting in the entry
        entry_button = Button(self, text="SAVE", height=3, width=12, command=enter_entry)
        entry_button.pack(side="top")

        # Takes the user back the main page
        back_button = Button(self, text="go back", command=lambda: controller.show_frame("StartPage"))
        back_button.place(anchor=NW)

        # Is the interface in which the user puts down their entry
        notes = Text(self, height=30, width=300, wrap=WORD)
        notes.pack(side="bottom")

        # Tells current number of entries and what entry the person is writing
        num_entries = Label(self, text="Currently " + str(num_of_list()) + " Entries", font=(None, 15), pady=6)
        num_entries.pack(side="bottom")

        # Tell the current time of the day
        curr_time = Label(self, text=datetime.now().time().strftime('%I:%M:%S%p'), font=(None, 15), pady=6)
        curr_time.pack(side="bottom")

        # Tells the current date
        curr_date = Label(self, text=date.today().strftime("%B %d, %Y"), font=(None, 15), pady=6)
        curr_date.pack(side="bottom")

        clock()


if __name__ == "__main__":
    app = PageApplication()
    app.geometry("850x700")
    app.title("Diary App")
    app.mainloop()
