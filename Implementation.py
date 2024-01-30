from datetime import *
import os.path
from tkinter import *
from tkcalendar import Calendar
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

scope = ["https://www.googleapis.com/auth/calendar"]
creds = None
def main():
    global creds
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json")
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("project.json", scope)
            creds = flow.run_local_server(port=0)

            with open("token.json", "w") as token:
                token.write(creds.to_json())
def read_upcoming_events():
    global root2
    try:
        root3.destroy()
    except:
        pass
    root2 = Toplevel()
    root2.config(background='#A1F2F5')
    
    service = build("calendar", "v3", credentials=creds)
    now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    def destro():
        root2.destroy()
    events_result = (
        service.events()
        .list(
            calendarId='primary',
            timeMin=now,
            singleEvents=True,
            orderBy='startTime',
        )
        .execute()
    )
    events = events_result.get('items', [])

    if not events:
        l = Label(root2,
            text='NO UPCOMING EVENTS !!',
            font=("calibre", 40, 'bold'),
            bg='#A1F2F5',
            padx=50, pady=50,
        )
        b = Button(root2,
            text='CLOSE',
            font=('bold'),
            command=destro,
        )
        l.pack()
        b.pack()
    else:
        
        root2.attributes('-zoomed', True)
        canvas = Canvas(root2)
        canvas.config(background='#A1F2F5')
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar = Scrollbar(root2, command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)

        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        canvas.bind("<Configure>", on_configure)

        # Create a frame to hold the labels
        frame = Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor="nw")

        for i, event in enumerate(events):
            start = event['start'].get('dateTime', event['start'].get('date'))
            start_time = datetime.fromisoformat(start)
            formatted_start_time = start_time.strftime("%I:%M:%S %p \nDated %d/%m/%Y")

            # Create a label widget and add it to the frame
            label = Label(
                frame,
                text=f'Upcoming Event : {event["summary"]}\nAt : {formatted_start_time}',
                font=("calibre", 40, 'bold'),
                # bg='#A1F2F5',
                fg='black'
            )
            label.grid(row=i, column=0, sticky="n", padx=700,pady=10)  # Adjust the pady value as needed
        root2.mainloop()

# Function to create a new event
def create_event():
    service = build("calendar", "v3", credentials=creds)
    global root3
    try:
        root2.destroy()
    except:
        pass
    root3 = Toplevel()
    e = Entry(root3, width=30, font=('Arial', 16)) # Name of event
    l = Label(root3,text="Name Of Event:",font=('Arial', 16))
    l1 = Label(root3,text="Date:",font=('Arial', 16))
    root3.geometry("600x500")
    # e.insert(0,"demn")
    l.place(x=0,y=50)
    e.place(x=175,y=50)
    l1.place(x=0,y=100)
    # l.grid(row=0, column=0, padx=10, pady=10)
    # e.grid(row=0, column=5, padx=10, pady=10)
    dam = datetime.now()
    m = dam.month
    y = dam.year
    d = dam.day

    cal = Calendar(root3, selectmode="day", year=y, month=m, day=d)
    cal.place(x=175,y=100)
    l2 = Label(root3,text="Start Time:",font=('Arial', 16))
    l3 = Label(root3,text="End Time:",font=('Arial', 16))
    e1 = Entry(root3, width=30, font=('Arial', 16)) #start time
    e2 = Entry(root3, width=30, font=('Arial', 16)) # end time
    e1.place(x=175,y=300)
    l2.place(x=0,y=300)
    e2.place(x=175,y=350)
    l3.place(x=0,y=350)
    summary = None;st=None;et=None;dat=None
    l4 = Label(root3,text="ddef")
    def submit(e, e1, e2, cal):
        summary = e.get()  # name
        st = e1.get()  # start time
        et = e2.get()  # end time
        dat = cal.get_date()  # date

        # Default values
        start_time = None
        end_time = None

        try:
            start_time = datetime.strptime(f"{dat} {st}", "%m/%d/%y %I:%M %p")
            utc_now = start_time.astimezone(timezone.utc)
            end_time = datetime.strptime(f"{dat} {et}", "%m/%d/%y %I:%M %p")
            utc_next = end_time.astimezone(timezone.utc)
        except Exception as e:
            print('Error parsing date/time:', e)
            l4.config(text="Wrong Format Try Again")
            # You might want to show a message box or handle the error in a different way

        if start_time and end_time:
            event = {
                'summary': summary,
                'start': {'dateTime': utc_now.isoformat(), 'timeZone': 'UTC'},
                'end': {'dateTime': utc_next.isoformat(), 'timeZone': 'UTC'},
            }

            try:
                event = service.events().insert(calendarId='primary', body=event).execute()
                print('bhai Hogya !!!')
                root3.destroy()
            except Exception as e:
                print('Error creating event:', e)
                l4.config(text="")

    b1 = Button(root3,
        text='Submit',
        command=lambda: submit(e, e1, e2, cal),

    )
    
    b1.place(x=225,y=400)
    l4.place(x=225,y=450)
    root3.mainloop()
    
if __name__ == "__main__":
    main()
    root = Tk()
    root2=None;root3 = None
    root.attributes('-zoomed', True)
    root.config(background='#F4B5B5')
    b1 = Button(
        text='Read Upcoming Events',
        font=('TimesNewRoman','40','bold'),
        fg='white',
        bg='pink',
        padx=100,pady=100,
        activebackground='cyan',
        activeforeground='white',
        command=read_upcoming_events
    )
    b1.place(x=600,y=200)
    b2 = Button(
        text='Create Events',
        command=create_event,
        font=('TimesNewRoman','40','bold'),
        fg='white',
        bg='pink',
        padx=200,pady=100,
        activebackground='cyan',
        activeforeground='white',

    )
    b2.place(x=600,y=550)
    root.mainloop()

