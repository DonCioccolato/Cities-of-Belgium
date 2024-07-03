import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import csv
from unidecode import unidecode
from cairosvg import svg2png
import os
import xml.etree.ElementTree as ET

## Functions ##

def update_timer():
    global timer
    timer += 1
    minutes, seconds = divmod(timer, 60)
    timer_text = f"{minutes:02}:{seconds:02}"
    timelabel.config(text=timer_text)
    if sum(list(numberofcities.values())) < totalnumberofcities['België']:
        root.after(1000, update_timer)

def update_map(element_id = None,filepath = "tempmap.svg", fill_color ="#FF0000",fill_outline = "black"):
    if(element_id): #if correct entry: fill city (update temporary svg file)
        tree = ET.parse(filepath)
        root = tree.getroot()
        for element in root.iter():
            if 'id' in element.attrib and element.attrib['id'] == element_id:
                element.attrib['style'] = f'fill:{fill_color};stroke:{fill_outline};stroke-width:1px'
        tree.write(filepath)
        # Convert the SVG file to PNG
        image_path = "temp_map.png"
        svg2png(url=filepath, write_to=image_path) #high (1 second) delay
    else:
        image_path = "empty_map.png"

    #Display image
    image = Image.open(image_path)
    image = image.resize((800, 600), Image.LANCZOS)
    img = ImageTk.PhotoImage(image)
    map_label.config(image=img)
    map_label.image = img

def copy_svg(src,dst):
    with open(src, 'r') as original_file: # Open original file for reading
        svg_content = original_file.read()

    with open(dst, 'w') as new_file: # Create new file
        new_file.write(svg_content) # Write the content to the new file

# Function called when entry is submitted
def on_submit(event=None):
    city_name = city_entry.get()
    city_name, province, path = determine_province(city_name)
    if province in tables and city_name not in tables[province].get_children(): #correct entry and not duplicate
        tables[province].insert("", "end", values=(city_name,),iid=city_name) #insert city in table

        #update progress
        numberofcities[province] += 1
        tables[province].heading("Stad", text=f"Stad/gemeente ({numberofcities[province]}/{totalnumberofcities[province]})")
        progress_vlaanderen.set(f"Vlaanderen: {sum(list(numberofcities.values())[:5])}/{totalnumberofcities['Vlaanderen']}")
        progress_wallonie.set(f"Wallonië: {sum(list(numberofcities.values())[6:])}/{totalnumberofcities['Wallonië']}")
        progress.set(f"België: {sum(list(numberofcities.values()))}/{totalnumberofcities['België']}")

        city_entry.delete(0, tk.END)  # Empty typing field
        update_map(path)  # Update de kaart met de nieuwe stad

def determine_province(city_name):
    with open('Belgische_gemeenten.csv', mode='r', newline='') as csv_file:
            reader = csv.reader(csv_file,delimiter=';')
            clean_city_name = unidecode(city_name.lower()) #unidecode for getting rid of accents, lower for making it lowercase
            for row in reader:
                if '(' in row[0]: #brackets indicate translation. both languagues should be valid
                    if (clean_city_name == unidecode(row[0].split('(')[0].strip().lower()) or 
                    clean_city_name == unidecode(row[0].split('(')[1].split(')')[0].strip().lower())):
                        return row[0],row[2],row[6]
                elif clean_city_name == unidecode(row[0].lower()):
                    return row[0],row[2],row[6]
    return None,None,None #no match

# Function called when the window is closed
def on_closing():
    try:
        os.remove("tempmap.svg")  # Delete the temporary SVG file
        os.remove("temp_map.png")  # Delete the temporary PNG file
    except:
        pass
    root.destroy()

#data
provinces = ["West-Vlaanderen", "Oost-Vlaanderen", "Vlaams-Brabant", "Antwerpen", "Limburg", 
                "Brussel",
             "Henegouwen", "Namen", "Waals-Brabant", "Luik", "Luxemburg"]

totalnumberofcities = {"West-Vlaanderen":64, "Oost-Vlaanderen":60, "Vlaams-Brabant":65, "Antwerpen":69, "Limburg":42, 
                "Brussel":19, "Vlaanderen":300,"Wallonië":262,"België":581,
             "Henegouwen":69, "Namen":38, "Waals-Brabant":27, "Luik":84, "Luxemburg":44}

numberofcities = {"West-Vlaanderen":0, "Oost-Vlaanderen":0, "Vlaams-Brabant":0, "Antwerpen":0, "Limburg":0,
                "Brussel":0,
             "Henegouwen":0, "Namen":0, "Waals-Brabant":0, "Luik":0, "Luxemburg":0}


## Make GUI ##
# Main window
root = tk.Tk()
root.title("Cities of Belgium")
root.state('zoomed')  # Maak het venster volledig scherm

# Frame for input
input_frame = tk.Frame(root)
input_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

# Inputfield and add button
city_label = tk.Label(input_frame, text="Voer een stad of gemeente in:")
city_label.pack(side=tk.LEFT, padx=5)
city_entry = tk.Entry(input_frame, width=50)
city_entry.pack(side=tk.LEFT, padx=5)
submit_button = tk.Button(input_frame, text="Toevoegen", command=on_submit) #bind button to submit function
submit_button.pack(side=tk.LEFT, padx=5)

# Timer
timer = 0
timelabel = tk.Label(input_frame, text="", font=("Helvetica", 24))
timelabel.pack(side=tk.RIGHT, padx=5)

#Progress
progress_vlaanderen = tk.StringVar()
progresslabel_vlaanderen = tk.Label(input_frame, textvariable=progress_vlaanderen)
progresslabel_vlaanderen.pack(side=tk.LEFT, padx=5)
progress_vlaanderen.set(f"Vlaanderen: 0/{totalnumberofcities['Vlaanderen']}")

progress_wallonie = tk.StringVar()
progresslabel_wallonie = tk.Label(input_frame, textvariable=progress_wallonie)
progresslabel_wallonie.pack(side=tk.LEFT, padx=5)
progress_wallonie.set(f"Wallonië: 0/{totalnumberofcities['Wallonië']}")

progress = tk.StringVar()
progresslabel = tk.Label(input_frame, textvariable=progress)
progresslabel.pack(side=tk.LEFT, padx=5)
progress.set(f"België: 0/{totalnumberofcities['België']}")

# Frame for tables and map
content_frame = tk.Frame(root)
content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

# Frame for map
map_frame = tk.Frame(content_frame)
map_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
map_label = tk.Label(map_frame, bg="white") #placeholder label
map_label.pack(fill=tk.BOTH, expand=True)

#Tables
table_container = tk.Frame(content_frame)
table_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
canvas = tk.Canvas(table_container) #scrollable frame
scrollbar = tk.Scrollbar(table_container, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)
scrollable_frame.bind("<Configure>",lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Create tables for each province
tables = {}
for i, province in enumerate(provinces):
    table_frame = tk.Frame(scrollable_frame)
    table_frame.grid(row=i//2, column=i%2, padx=5, pady=5, sticky='nsew')
    
    table_label = tk.Label(table_frame, text=province)
    table_label.pack(side=tk.TOP)
    
    table = ttk.Treeview(table_frame, columns=("Stad"), show="headings") #use tree as a table
    table.heading("Stad", text=f"Stad/gemeente (0/{totalnumberofcities[province]})")
    table.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    tables[province] = table

#style for headers
style = ttk.Style(root)
style.theme_use("clam")
style.configure("Treeview.Heading", background="white", foreground="black")

#copy svg file. This new file is a temporary file that can be modified
copy_svg(src = "Map_of_Belgium.svg",dst = "tempmap.svg")

# Load map
update_map()
update_timer()

# Bind closing function closing the window
root.protocol("WM_DELETE_WINDOW", on_closing)

# Bind Enter key to the submit function
city_entry.bind("<Return>", on_submit)

# Start GUI-mainloop
root.mainloop()
