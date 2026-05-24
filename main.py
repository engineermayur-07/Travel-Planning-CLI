import json
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import tkinter as tk
from tkcalendar import *
from datetime import *
from fpdf import FPDF
import os
geolocator = Nominatim(user_agent="travel_itinerary",timeout=10)
destinations = {}
hotel_menu = {} 

def safe_input(prompt, type_func=int, validator=None, error_msg="Invalid input. Please try again."):
    """Helper function for safe user input with validation."""
    while True:
        try:
            value = type_func(input(prompt))
            return value
        except ValueError:
            print(error_msg)

def select_hotel_category(category, destination):
    """Helper function to select hotel and room from a category."""
    print(f"\n{'='*50}\n")
    print(f"RECOMMENDED {category.upper()} HOTELS IN {destination.upper()}:")
    print(f"\n{'='*50}\n")
    hotels = destinations[destination]["hotels"][category]
    for i, hotel in enumerate(hotels, start=1):
        print(f"-{i} {hotel[0]}")
    select_hotel = safe_input("Please select a hotel from the above list: ", validator=lambda x: 1 <= x <= len(hotels), error_msg="Invalid hotel choice.")
    select_hotel_name = hotels[select_hotel-1][0]
    print(f"You have selected {select_hotel_name} for your stay in {destination}.")
    print("This hotel offers the following rooms: ")
    max_room = 3 if category != "Budget" else 2
    if max_room == 3:
        print(f"1. Classic Chamber : {int(hotels[select_hotel-1][1])} rs/night")
        print(f"2. Deluxe Chamber : {int(hotels[select_hotel-1][2])} rs/night")
        print(f"3. Family Chamber : {int(hotels[select_hotel-1][3])} rs/night")
    else:
        print(f"1. Classic Chamber : {int(hotels[select_hotel-1][1])} rs/night")
        print(f"2. Family Chamber : {int(hotels[select_hotel-1][2])} rs/night")
    room_choice = safe_input("Please select a room type (1/2/3): ", validator=lambda x: 1 <= x <= max_room, error_msg=f"Invalid room choice. Please select 1 to {max_room}.")
    if room_choice == 1:
        room_cost = int(hotels[select_hotel-1][1])
        print(f"The cost of Classic Chamber at {select_hotel_name} is: {room_cost} rs/night")
    elif room_choice == 2:
        room_cost = int(hotels[select_hotel-1][2])
        room_type_name = "Deluxe Chamber" if max_room == 3 else "Family Chamber"
        print(f"The cost of {room_type_name} at {select_hotel_name} is: {room_cost} rs/night")
    elif room_choice == 3 and max_room == 3:
        room_cost = int(hotels[select_hotel-1][3])
        print(f"The cost of Family Chamber at {select_hotel_name} is: {room_cost} rs/night")
    return room_cost, select_hotel_name, room_choice

 
def generate_pdf(dest, start, arrival, departure, days, members, dist, mode, hotel, room_type, rooms, food_list, activities_list, total_breakdown, total):
    pdf = FPDF()
    pdf.add_page()
    
    # --- 1. HEADER WITH LOGO ---
    try:
        if os.path.exists("logo.jpg"):
            pdf.image("logo.jpg", 10, 8, 33)    # Image(path, x, y, width)
    except:
        pass
    pdf.set_font("Arial", 'B', 24)
    pdf.set_text_color(44, 62, 80)  
    pdf.cell(0, 10, txt="SAFARNAMA", ln=True, align='R')
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, txt="Your Journey, Our Passion", ln=True, align='R')
    pdf.ln(15)

    # Decorative Line
    pdf.set_draw_color(44, 62, 80)
    pdf.line(10, 45, 200, 45)
    pdf.ln(5)

    # --- 2. TRIP OVERVIEW BOX ---
    pdf.set_fill_color(240, 240, 240) # Light Grey background
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, txt=f" TRIP TO {dest.upper()}", ln=True, fill=True)
    
    pdf.set_font("Arial", size=11)
    pdf.set_text_color(0, 0, 0)
    
    # Two-column layout for details
    col_width = 90
    pdf.cell(col_width, 8, txt=f"From: {start}", ln=0)
    pdf.cell(col_width, 8, txt=f"Distance: {dist:.2f} km", ln=1)
    
    pdf.cell(col_width, 8, txt=f"Arrival: {arrival}", ln=0)
    pdf.cell(col_width, 8, txt=f"Departure: {departure}", ln=1)
    
    pdf.cell(col_width, 8, txt=f"Travelers: {members}", ln=0)
    pdf.cell(col_width, 8, txt=f"Duration: {days} Days", ln=1)
    
    # --- 3. ACCOMMODATION ---
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="ACCOMMODATION", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8, txt=f"Stay at {hotel}\nRoom Type: {room_type} ({rooms} rooms)", border='L')

    # --- 4. FOOD & ACTIVITIES ---
    # We use two columns if possible, or stacked with icons
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="DAILY MEAL PLAN", ln=True)
    pdf.set_font("Arial", size=10)
    for item in food_list:
        pdf.cell(0, 7, txt=f"  > {item}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="PLANNED ACTIVITIES", ln=True)
    pdf.set_font("Arial", size=10)
    for act in activities_list:
        pdf.cell(0, 7, txt=f"  * {act}", ln=True)

    # --- 5. BUDGET SUMMARY (The Invoice Look) ---
    pdf.ln(10)
    pdf.set_fill_color(44, 62, 80)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt=" BUDGET BREAKDOWN", ln=True, fill=True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=11)
    for label,cost in total_breakdown.items():
        pdf.cell(140, 8, txt=label, border='B', ln=0)
        pdf.cell(50, 8, txt=f"Rs. {cost:,.2f}", border='B', ln=1, align='R')
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(192, 57, 43) # Soft Red
    pdf.cell(0, 12, txt=f"GRAND TOTAL: Rs. {total:,.2f}", ln=True, align='R')

    # Footer
    pdf.set_y(-20)
    pdf.set_font("Arial", 'I', 12)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 10, txt="Generated by Safarnama Travel Services", align='C')
    pdf.cell(0,10, txt=f"Page {pdf.page_no()}", align='R')

    # Note: Clean symbols logic as discussed before
 # Call it at the end of your code:
    file_name = f"{destination}_Itinerary.pdf"
    try:
        pdf.output(file_name)
        print(f"Success! PDF downloaded as {file_name}")
        
        # Automatically open the PDF (Windows)
        os.startfile(file_name)
    except Exception as e:
        print(f"Error generating or opening PDF: {e}")
# generate_pdf_report(destination, starting_point, distance, travel_mode, hotel, no_rooms, activities, total_cost)


def get_selected_date(title, min_date):
    """Universal function to handle date selection logic."""
    selected_date = [None] # Use a list to store data across scopes

    def on_select():
        selected_date[0] = cal.get_date()
        root.destroy()

    root = tk.Tk()
    root.title(title)
    root.geometry("350x400")
    
    # Force the window to stay on top
    root.attributes('-topmost', True)

    cal = Calendar(root, selectmode='day', 
                   mindate=min_date, 
                   date_pattern='dd/mm/yyyy')
    cal.pack(pady=20, padx=20)

    btn = tk.Button(root, text="Confirm Selection", 
                    command=on_select, 
                    bg="#2c3e50", fg="white", padx=10)
    btn.pack(pady=10)

    root.mainloop()
    return selected_date[0]

def arrival_date_selection():
    print("Opening Arrival Date Picker...")
    today = date.today()
    res = get_selected_date("Select Arrival Date", today)
    if res:
        return datetime.strptime(res, "%d/%m/%Y").date()
    return today # Fallback to today if closed without selection

def departure_date_selection(arrival_date, destination):
    print(f"Opening Departure Date Picker for {destination}...")
    # Departure must be at least the day of arrival or later
    res = get_selected_date(f"Departure from {destination}", arrival_date)
    if res:
        return datetime.strptime(res, "%d/%m/%Y").date()
    return arrival_date
def load_database():
    """Load destinations and hotel menu data from travel_data.json."""
    global destinations,hotel_menu
    try:
        with open("travel_data.json", "r") as file:
            data = json.load(file)
            destinations=data["destinations"]
            hotel_menu=data["hotel_menu"]
    except FileNotFoundError:
        print("Error, database not loaded, try after sometime.")
    except json.JSONDecodeError:
        print("Error, database file is corrupted, contact the owner.")
    except Exception as e:
        print(f"An unexpected error occurred while loading the database: {e}")
      
def calculate_distance(start, destination):
    try:
         
        location1 = geolocator.geocode(start)
        location2 = geolocator.geocode(destination)

        if not location1 or not location2:
            print("Error: Your starting point could not be found.")
            return None
        else:
            coords1 = (location1.latitude, location1.longitude)
            coords2 = (location2.latitude, location2.longitude)

            distance = geodesic(coords1, coords2).kilometers
            return distance
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
def display_travel_options():
    print("We have major three categories of travel destinations: ")
    print("1. Hills and Mountains")
    print("2. Coastal Areas")
    print("3. Devotional Sites")
    choice = input("Please select a category (1/2/3): ")
    if choice == '1':
        print(f"\n{'='*50}\n")
        print("These are the options available for hill and mountain destinations:")
        print(f"\n{'='*50}\n")

        for place in destinations["Hills and Mountains"]:
            print(f"- {place}")
    elif choice == '2':
        print(f"\n{'='*50}\n")
        print("These are the options available for coastal destinations:")
        print(f"\n{'='*50}\n")
        for place in destinations["Coastal"]:
            print(f"- {place}")
    elif choice == '3':
        print(f"\n{'='*50}\n")
        print("These are the options available for devotional sites:")
        print(f"\n{'='*50}\n")
        for place in destinations["Devotional Sites"]:
            print(f"- {place}")
    else:
        print("Invalid choice. Please select 1, 2, or 3.")
        return display_travel_options()

def travel_modes(distance,destination):
    members = safe_input(f"How many members are travelling to {destination}:- ", validator=lambda x: 1 <= x <= 100, error_msg="Invalid number of members. Please enter a positive integer between 1 and 100.")
    mode={
        "rented car":[10 ,60 ,distance/60],
        "personal car":[1 ,70,distance/70],
        "train":[3 ,100 ,distance/100],
        "plane":[8 ,800 ,distance/800]
    }
 
    print(f"The total travel distance is {distance:.3f} km\n")
    print("Follow is the estimated rate table for various modes")
    print()
    print("   Vehicles           Rate(rs/km)            Time(hrs)       Total travel cost(rs)")
    for i,j in mode.items():
        print(f".  {i:15}             {j[0]:.3f}            {j[2]:.3f}         {(j[0]*distance):.3f}")

    travel_mode=input("\nSelect the mode of travel :- \n\t1.Rented Car\n\t2.Personal Car\n\t3.Train\n\t4.Plane\n Ans:- ").lower()
    travel_cost=0
    match travel_mode:
        case "rented car":
            travel_cost = mode["rented car"][0] * distance
            print("So you are going through a Rented Car")
            return travel_cost,travel_mode,members
        case "personal car":
            travel_cost = mode["personal car"][0] * distance
            print("So you are going through a Personal Car")
            return travel_cost,travel_mode,members
        case "train":
            travel_cost = mode["train"][0] * distance
            print("So you are going through a Train")
            return travel_cost,travel_mode,members
        case "plane":
            airport=input("Enter the nearest city to you having airport :- ")
            plane_distance = calculate_distance(airport,destination)
            if(plane_distance==None):
                print("Distance returned is none")
                return travel_modes(distance,destination)
            travel_cost = mode["plane"][0] * plane_distance
            print("So you are going through a Plane")
            return travel_cost,travel_mode,members
        case _:
            print("Entered wrong mode choice")
            print("Returning back to mode selection")
            return travel_modes(distance,destination)

def hotel_recommendation(destination,ChoiceStay):

    room_cost=0
    select_hotel_name=None
    if ChoiceStay>1:
        print(f"\n{'='*50}\n")
        print(f"\nSearching for top-rated hotels in {destination} for you...")
        print(f"\n{'='*50}\n")
        print("There are three categories of hotels available: ")
        print("1. Luxury Hotels(7500 rs/night and above)")
        print("2. Mid-range Hotels(3000-7500 rs/night)")
        print("3. Budget Hotels(< 3000 rs/night)")
        hotel_choice=input("Please select a category (1/2/3): ")
        if hotel_choice=='1':
            print(f"\n{'='*50}\n")
            print(f"RECOMMENDED LUXURY HOTELS IN {destination.upper()}:")
            print(f"\n{'='*50}\n")
            for i, hotel in enumerate(destinations[destination]["hotels"]["Luxury"], start=1):
                print(f"-{i} {hotel[0]}")
            select_hotel=int(input("Please select a hotel from the above list: (1/2/3) "))
            try:
                select_hotel_name = destinations[destination]["hotels"]["Luxury"][select_hotel-1][0]
            except :
                print("Invalid hotel choice.")
                return hotel_recommendation(destination)
 
            print(f"You have selected {select_hotel_name} for your stay in {destination}.")
            print("This hotel offers the following rooms: ")
            print(f"1. Classic Chamber : {int(destinations[destination]['hotels']['Luxury'][select_hotel-1][1])} rs/night")
            print(f"2. Deluxe Chamber : {int(destinations[destination]['hotels']['Luxury'][select_hotel-1][2])} rs/night")
            print(f"3. Family Chamber : {int(destinations[destination]['hotels']['Luxury'][select_hotel-1][3])} rs/night    ")
            room_choice=input("Please select a room type (1/2/3): ")
            if room_choice=='1':
                room_cost = int(destinations[destination]["hotels"]["Luxury"][select_hotel-1][1])
                print(f"The cost of Classic Chamber at {select_hotel_name} is: {room_cost} rs/night")
            elif room_choice=='2':
                room_cost = int(destinations[destination]["hotels"]["Luxury"][select_hotel-1][2])
                print(f"The cost of Deluxe Chamber at {select_hotel_name} is: {room_cost} rs/night")
            elif room_choice=='3':
                room_cost = int(destinations[destination]["hotels"]["Luxury"][select_hotel-1][3])
                print(f"The cost of Family Chamber at {select_hotel_name} is: {room_cost} rs/night")
            else:
                print("Invalid room choice. Please follow process again.")
                return hotel_recommendation(destination)
        elif hotel_choice=='2':
            print(f"\n{'='*50}\n")
            print(f"RECOMMENDED MID-RANGE HOTELS IN {destination.upper()}:")
            print(f"\n{'='*50}\n")
            for i, hotel in enumerate(destinations[destination]["hotels"]["Mid-range"], start=1):
                print(f"-{i}. {hotel[0]}")
            select_hotel=int(input("Please select a hotel from the above list: (1/2/3) "))
            try:
                select_hotel_name = destinations[destination]["hotels"]["Mid-range"][select_hotel-1][0]
            except  :
                print("Invalid hotel choice.")
                return hotel_recommendation(destination)
            print(f"You have selected {select_hotel_name} for your stay in {destination}.")
            print("This hotel offers the following rooms: ")
            print(f"1. Classic Chamber : {int(destinations[destination]['hotels']['Mid-range'][select_hotel-1][1])} rs/night")
            print(f"2. Deluxe Chamber : {int(destinations[destination]['hotels']['Mid-range'][select_hotel-1][2])} rs/night")
            print(f"3. Family Chamber : {int(destinations[destination]['hotels']['Mid-range'][select_hotel-1][3])} rs/night")
            room_choice=input("Please select a room type (1/2/3): ")
            if room_choice=='1':
                room_cost = int(destinations[destination]["hotels"]["Mid-range"][select_hotel-1][1])
                print(f"The cost of Classic Chamber at {select_hotel} is: {room_cost} rs/night")
            elif room_choice=='2':
                room_cost = int(destinations[destination]["hotels"]["Mid-range"][select_hotel-1][2])
                print(f"The cost of Deluxe Chamber at {select_hotel} is: {room_cost} rs/night")
            elif room_choice=='3':
                room_cost = int(destinations[destination]["hotels"]["Mid-range"][select_hotel-1][3])
                print(f"The cost of Family Chamber at {select_hotel} is: {room_cost} rs/night")
            else:
                print("Invalid room choice. Please select 1, 2, or 3.")
                print("Returning back to the hotels selections")
                return hotel_recommendation(destination)
        elif hotel_choice=='3':
            print(f"\n{'='*50}\n")
            print(f"RECOMMENDED BUDGET HOTELS IN {destination.upper()}:")
            print(f"\n{'='*50}\n")
            for i, hotel in enumerate(destinations[destination]["hotels"]["Budget"], start=1):
                print(f"-{i}. {hotel[0]}")
            select_hotel=int(input("Please select a hotel from the above list: (1/2 ...) "))
            try:
                select_hotel_name = destinations[destination]["hotels"]["Budget"][select_hotel-1][0]
            except  :
                print("Invalid hotel choice.")
                return hotel_recommendation(destination)
            print(f"You have selected {select_hotel_name} for your stay in {destination}.")
            print("This hotel offers the following rooms: ")
            print(f"1. Classic Chamber : {int(destinations[destination]['hotels']['Budget'][select_hotel-1][1])} rs/night")
            print(f"2. Family Chamber : {int(destinations[destination]['hotels']['Budget'][select_hotel-1][2])} rs/night ")
            room_choice=input("Please select a room type (1/2/3): ")
            if room_choice=='1':
                room_cost = int(destinations[destination]["hotels"]["Budget"][select_hotel-1][1])
                print(f"The cost of Classic Chamber at {select_hotel} is: {room_cost} rs/night")
            elif room_choice=='2':
                room_cost = int(destinations[destination]["hotels"]["Budget"][select_hotel-1][2])
                print(f"The cost of Family Chamber at {select_hotel} is: {room_cost} rs/night")
                
            else:
                print("Invalid room choice. Please select 1, 2, or 3.")
                print("Returning back to the hotels selections")
                return hotel_recommendation(destination)

        else:
            print("Invalid choice. Please select 1, 2, or 3.")
            print("Returning back to the hotels selections")
            return hotel_recommendation(destination)

        if(room_choice=='1'):
            room_type="Classic Chamber"
        elif(room_choice=='2'):
            room_type="Deluxe Chamber"
        elif(room_choice=='3'):     
            room_type="Family Chamber"
        stay_cost= room_cost*ChoiceStay 
        return stay_cost,select_hotel_name,room_type

    elif ChoiceStay==1:
        print("Since you are not planning to stay for more than a day, we will not search for hotels.")
        return 0,None,None
    else:
        print("Invalid input for days of stay. Please enter a valid number.")
        print("Returning back to hotel selction")
        return hotel_recommendation(destination)
    

def rooms_calc(hotel_name, room_type):
    no_rooms = safe_input(f"How many rooms of {room_type} do you want to book in {hotel_name} :- ", validator=lambda x: 1 <= x <= 10, error_msg="Invalid number of rooms. Please enter a positive integer between 1 and 10.")
    return no_rooms 
    

def activity_recommendation(destination):
    print(f"Here are some recommended activities to do in {destination}:")
    for i, activity in enumerate(destinations[destination]["activities"], start=1):
        print(f"-{i}. {activity}")
    print("You can explore these activities during your stay in the destination. The average cost for each activity is approximately 500-1000 rs.")
     
    activities_todo=[]
    try:
        for i in destinations[destination]["activities"]:
            activity_choice = (input(f"Do you want to do '{i}'? (yes/no): "))
            if activity_choice == 'yes':
                activities_todo.append(i)
    except ValueError:
        print("Invalid input. Please enter 'yes' or 'no'.")
        print("Returning back to activity selection")
        return activity_recommendation(destination)
    print("Enjoy your trip!")
    return 1000*len(activities_todo),activities_todo

def food_planning(destination, hotel_name, days):
    print(f"\n{'='*50}\n")
    print(f"FOOD PLANNING FOR {hotel_name.upper()} at {destination}")
    print(f"\n{'='*50}\n")
    print(f"\nWe have the following menu options available at {hotel_name}:")
    print("\n--- BREAKFAST MENU ---")
    print("VEG OPTIONS:")
    for item, price in hotel_menu["Breakfast"]["VEG"].items():
        print(f"  {item}: Rs. {price}")
    print("NON-VEG OPTIONS:")
    for item, price in hotel_menu["Breakfast"]["NON-VEG"].items():
        print(f"  {item}: Rs. {price}")
    
    print("\n--- LUNCH MENU ---")
    print("VEG OPTIONS:")
    for item, price in hotel_menu["Lunch"]["VEG"].items():
        print(f"  {item}: Rs. {price}")
    print("NON-VEG OPTIONS:")
    for item, price in hotel_menu["Lunch"]["NON-VEG"].items():
        print(f"  {item}: Rs. {price}")
    
    print("\n--- DINNER MENU ---")
    print("VEG OPTIONS:")
    for item, price in hotel_menu["Dinner"]["VEG"].items():
        print(f"  {item}: Rs. {price}")
    print("NON-VEG OPTIONS:")
    for item, price in hotel_menu["Dinner"]["NON-VEG"].items():
        print(f"  {item}: Rs. {price}")
    
    total_food_cost = 0
    food_items = []
    day_food_plan=0
    while(day_food_plan<days):
        day_food_plan+=1
        # Breakfast selection
        print("\n" + "="*50)
        print(f"BREAKFAST SELECTION for Day {day_food_plan}")
        print("="*50)
        print("Available Breakfast items:")
        print("VEG OPTIONS:")
        for i, (item, price) in enumerate(hotel_menu["Breakfast"]["VEG"].items(), 1):
            print(f"  {i}. {item} - Rs. {price}")
        print("NON-VEG OPTIONS:")
        for i, (item, price) in enumerate(hotel_menu["Breakfast"]["NON-VEG"].items(), len(hotel_menu["Breakfast"]["VEG"]) + 1):
            print(f"  {i}. {item} - Rs. {price}")

        try:
            breakfast_choice = int(input("\nEnter breakfast item number (or press enter to skip): "))
            if breakfast_choice:
                breakfast_idx = int(breakfast_choice) - 1
                if 0 <= breakfast_idx < (len(hotel_menu["Breakfast"]["VEG"]) + len(hotel_menu["Breakfast"]["NON-VEG"])):
                    breakfast_item = list(hotel_menu["Breakfast"]["VEG"].keys())[breakfast_idx] if breakfast_idx < len(hotel_menu["Breakfast"]["VEG"]) else list(hotel_menu["Breakfast"]["NON-VEG"].keys())[breakfast_idx - len(hotel_menu["Breakfast"]["VEG"])]
                    breakfast_qty = int(input(f"Enter quantity for {breakfast_item}: "))
                    if(breakfast_idx < len(hotel_menu["Breakfast"]["VEG"])):
                        breakfast_cost = hotel_menu["Breakfast"]["VEG"][breakfast_item] * breakfast_qty 
                    else:
                        breakfast_cost = hotel_menu["Breakfast"]["NON-VEG"][breakfast_item] * breakfast_qty 
                    total_food_cost += breakfast_cost
                    food_items.append(f"Breakfast: {breakfast_item} x {breakfast_qty} x DAY {day_food_plan}  = Rs. {breakfast_cost}")
                    print(f"Added {breakfast_item} x {breakfast_qty} for  day {day_food_plan} = Rs. {breakfast_cost}")
        except (ValueError, IndexError):
            print("Skipping breakfast selection.")
        
        # Lunch selection
        print("\n" + "="*50)
        print(f"LUNCH SELECTION for Day {day_food_plan}")
        print("="*50)
        print("VEG OPTIONS:")
        for i, (item, price) in enumerate(hotel_menu["Lunch"]["VEG"].items(), 1):
            print(f"  {i}. {item} - Rs. {price}")
        print("NON-VEG OPTIONS:")
        for i, (item, price) in enumerate(hotel_menu["Lunch"]["NON-VEG"].items(), len(hotel_menu["Lunch"]["VEG"]) + 1):
            print(f"  {i}. {item} - Rs. {price}")
        
        try:
            lunch_choice = int(input("\nEnter lunch item number (or press enter to skip): "))
            if lunch_choice:
                lunch_idx = int(lunch_choice) - 1
                if 0 <= lunch_idx < (len(hotel_menu["Lunch"]["VEG"]) + len(hotel_menu["Lunch"]["NON-VEG"])):
                    lunch_item = list(hotel_menu["Lunch"]["VEG"].keys())[lunch_idx] if lunch_idx < len(hotel_menu["Lunch"]["VEG"]) else list(hotel_menu["Lunch"]["NON-VEG"].keys())[lunch_idx - len(hotel_menu["Lunch"]["VEG"])]
                    lunch_qty = int(input(f"Enter quantity for {lunch_item}: "))
                    if(lunch_idx < len(hotel_menu["Lunch"]["VEG"])):
                        lunch_cost = hotel_menu["Lunch"]["VEG"][lunch_item] * lunch_qty 
                    else:
                        lunch_cost = hotel_menu["Lunch"]["NON-VEG"][lunch_item] * lunch_qty 
                    total_food_cost += lunch_cost
                    food_items.append(f"Lunch: {lunch_item} x {lunch_qty} x  day {day_food_plan} = Rs. {lunch_cost}")
                    print(f"Added {lunch_item} x {lunch_qty} for  day {day_food_plan} = Rs. {lunch_cost}")
        except (ValueError, IndexError):
            print("Skipping lunch selection.")
        
        # Dinner selection
        print("\n" + "="*50)
        print(f"DINNER SELECTION for Day {day_food_plan}")
        print("="*50)
        print("VEG OPTIONS:")
        for i, (item, price) in enumerate(hotel_menu["Dinner"]["VEG"].items(), 1):
            print(f"  {i}. {item} - Rs. {price}")
        print("NON-VEG OPTIONS:")
        for i, (item, price) in enumerate(hotel_menu["Dinner"]["NON-VEG"].items(), len(hotel_menu["Dinner"]["VEG"]) + 1):
            print(f"  {i}. {item} - Rs. {price}")
        try:
            dinner_choice = input("\nEnter dinner item number (or press enter to skip): ")
            if dinner_choice.strip():
                dinner_idx = int(dinner_choice) - 1
                if 0 <= dinner_idx < (len(hotel_menu["Dinner"]["VEG"]) + len(hotel_menu["Dinner"]["NON-VEG"])):
                    dinner_item = list(hotel_menu["Dinner"]["VEG"].keys())[dinner_idx] if dinner_idx < len(hotel_menu["Dinner"]["VEG"]) else list(hotel_menu["Dinner"]["NON-VEG"].keys())[dinner_idx - len(hotel_menu["Dinner"]["VEG"])]
                    dinner_qty = int(input(f"Enter quantity for {dinner_item}: "))
                    if(dinner_idx < len(hotel_menu["Dinner"]["VEG"])):
                        dinner_cost = hotel_menu["Dinner"]["VEG"][dinner_item] * dinner_qty 
                    else:
                        dinner_cost = hotel_menu["Dinner"]["NON-VEG"][dinner_item] * dinner_qty 
                    total_food_cost += dinner_cost
                    food_items.append(f"Dinner: {dinner_item} x {dinner_qty} x  day {day_food_plan} = Rs. {dinner_cost}")
                    print(f"Added {dinner_item} x {dinner_qty} for  day {day_food_plan} = Rs. {dinner_cost}")
        except (ValueError, IndexError):
            print("Skipping dinner selection.")
        
    print(f"\n{'='*50}")
    print(f"TOTAL FOOD COST: Rs. {total_food_cost}")
    print(f"{'='*50}")
    
    return total_food_cost, food_items

def mis_cost(days,destination):
    print(f"Miscellaneous costs include local transportation, food outside hotel, shopping, etc. at {destination}.")
    pub_transport = safe_input("How much would you spend on public transport : avg cost is 5000-10000 per day (rs) :- ", validator=lambda x: x >= 0, error_msg="Please enter a non-negative number.")
    other_mis = safe_input(f"how much would you spend on other miscellaneous expenses (shopping, food outside hotel, etc.) : avg cost is 5000-10000 per day (rs) :- ", validator=lambda x: x >= 0, error_msg="Please enter a non-negative number.")
    mis_cost = pub_transport + other_mis
    return mis_cost * days

'''
starting main program
'''
load_database()
print("----- Welcome to the MR Travel Services -----")
display_travel_options()
while True:
    destination=input("Please enter your desired destination from the above list: ").upper()
    if destination not in destinations["Hills and Mountains"] and destination not in destinations["Coastal"] and destination not in destinations["Devotional Sites"]:
        print("Invalid destination choice. Please select a destination from the provided list.")
        continue
    break

starting_point=input("Please enter your starting point :-  ")
distance = calculate_distance(starting_point, destination)

if distance is not None:
    arrival = arrival_date_selection()
    print(f"You are visiting {destination} on {arrival}")
    departure = departure_date_selection(arrival,destination)
    print(f"You are leaving {destination} on {departure}")
 
    days=abs((arrival-departure).days)
    print(f"The total number of days of your travel is :- {days} days")


    travel_cost,travel_mode,members=travel_modes(distance,destination)
    hotel_cost,hotel,room_type=hotel_recommendation(destination,days)
    no_rooms=rooms_calc(hotel,room_type)
    hotel_cost=hotel_cost*no_rooms
    
    food_cost = 0
    food_items = []
    while True:
        plan_food = input("Do you want to plan for food at the hotel? (yes/no): ").lower()
        if plan_food == "yes":
            food_cost, food_items = food_planning(destination, hotel, days)
            break
        elif plan_food == "no":
            print("Skipping food planning.")
            break
        else :
            print("Invalid choice.Entering food planning again")
    travel_cost=travel_cost*members
    activity_cost,activities=activity_recommendation(destination)
    total_cost=travel_cost+hotel_cost+activity_cost+food_cost
     
    more_act=input("Do you want to add more activities to your trip plan (yes/no) :-  ").lower()
    if(more_act=="yes"):
        while(True):
            try:
                more_activities=input("Enter activity :- ")
                more_act_cost=int(input("Enter the estimated cost of the added activity :- "))
                activities.append(more_activities)
                activity_cost+=more_act_cost
            except:
                print("Enter valid activities or valid prices :- ")  
                continue     
            choice=input("Enter 'no' to stop adding more activities or press enter :- ").lower()
            if(choice=="no"):
                break
    print("Now lets calculate the miscellaneous expenses")
    mis_cost=mis_cost(days,destination)
    total_cost=travel_cost+hotel_cost+activity_cost+mis_cost

    
    print(f"\n{'='*50}\n")
    print("<\t\t**** The following is the planned trip details ****\t\t>")
    print(f"{'='*50}\n\n\n")
    print(f"The trip is planned to {destination} ")
    print(f"The tour starts from :- {starting_point}")
    print(f"Arrival at {destination} :- {arrival}")
    print(f"Departure from {destination} :- {departure}")
    print(f"The total distance from {starting_point} to {destination} is :- {distance} km")
    print(f"The mode of travel for the tour is {travel_mode}")
    print(f"No of days of the travel :- {days}")
    print(f"Number of members in the tour :- {members}")
    print(f"\n{'-'*50}\n")
    print(f"You are staying in the hotel :- {hotel}")
    print(f"The type of room you have booked is :- {room_type}")
    print(f"The no of rooms you have booked is :- {no_rooms}")
    print(f"\n{'-'*50}\n")
    print("Food items planned for the tour are :- ")
    for item in food_items:
        print(f"- {item}")
    print(f"\n{'-'*50}\n")
    print(f"Following are the activities you are going to do in {destination}")
    for i in activities:
        print(f"- {i}")
    print(f"\n{'-'*50}\n")
    print("Now lets calculate the total budget of the tour :")
    print(f"Travel cost :- {travel_cost}")
    print(f"Hotel cost :- {hotel_cost}")
    print(f"Food cost :- {food_cost}")
    print(f"Activity cost :- {activity_cost}")
    print(f"Miscelaneous cost :- {mis_cost}")
    print(f"Total cost of the tour :- {total_cost}")
    budget_list={
    "Travel Cost": travel_cost,
    "Hotel Cost": hotel_cost,
    "Food Cost": food_cost,
    "Activity Cost": activity_cost,
    "Miscellaneous Cost": mis_cost
    }
    while(True):
        print(f"Would you like to get a detailed itinerary pdf for your trip to {destination}? (yes/no)")
        itinerary_choice = input().lower()
        if itinerary_choice=="yes":
             generate_pdf(destination, starting_point, arrival, departure, days, members, distance, travel_mode, hotel, room_type,no_rooms, food_items, activities,budget_list, total_cost)
        elif itinerary_choice=="no":
            exit()
        else:
            print("invalid choice, select again")
            continue;
else:
    print(f"Could not calculate distance,")
    print(f"The reasons may be")
    print(f"1. Network Issue ( Check your Internet Connection)")
    print(f"2. Rate limit expired ( Try after some time)")
    print(f"3. Unknown error (Try again or contact the owner)")