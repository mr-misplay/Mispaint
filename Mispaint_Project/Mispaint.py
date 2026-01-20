import tkinter as tk
from tkinter import filedialog, PhotoImage
import colorsys, sys, os, tempfile
from PIL import Image, ImageTk

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

icon_path = resource_path("icon.png")

BASE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(BASE_DIRECTORY, "icon.png")

root = tk.Tk()
icon = PhotoImage(file=ICON_PATH)
root.iconphoto(True, icon)
root.title("Mispaint")
root.resizable(False, False)

#TOOLBAR
toolbar = tk.Frame(root)
toolbar.columnconfigure(0, weight=1)

toolbar.rowconfigure(0, weight=1)
toolbar.rowconfigure(1, weight=1)
toolbar.rowconfigure(2, weight=1)
toolbar.rowconfigure(3, weight=1)
toolbar.rowconfigure(4, weight=1)
toolbar.rowconfigure(5, weight=1)
toolbar.rowconfigure(6, weight=1)
toolbar.rowconfigure(9, weight=1)
toolbar.pack(side=tk.LEFT, anchor="nw")

#CANVAS
canvas = tk.Canvas(root, width=900, height=500, bg="white")
canvas.pack()

#BRUSH PREVIEW
preview =tk.LabelFrame(toolbar, text="Brush Preview")
preview.grid(row=0, column=0)

preview_canvas=tk.Canvas(preview, width=144, height= 77, bg="grey")
preview_canvas.pack()

def brush_preview():
    global brush_size
    global colour
    global brush_shape
    preview_canvas.delete("all")
    if brush_shape[0] == "circ":
        preview_canvas.create_oval((144//2) - brush_size, (77//2) - brush_size, (144//2) + brush_size, (77//2) + brush_size, fill=colour, outline="")
    if brush_shape[0] == "rect":
        preview_canvas.create_rectangle((144//2) - brush_size, (77//2) - brush_size, (144//2) + brush_size, (77//2) + brush_size, fill=colour, outline="")
    


#BRUSH SIZES
brush_size_frame = tk.LabelFrame(toolbar, text="Brush Size", width=152, height=70)
brush_size_frame.grid(row=1, column=0)
brush_size_frame.grid_propagate(False)

brush_size = 10

def set_brush_size(size):
    global brush_size
    brush_size = brush_slider.get()
    brush_preview()
   
brush_slider = tk.Scale(brush_size_frame, from_=0, to=100, orient="horizontal", command=set_brush_size, length=140)
brush_slider.grid(row=1, column=0)
brush_slider.set(10)
brush_slider.grid_propagate(False)

#BRUSHES
brushes = tk.LabelFrame(toolbar, text="Brush Shape")
brushes.rowconfigure(0, weight=1)
brushes.rowconfigure(1, weight=1)
brushes.columnconfigure(0, weight=1)
brushes.columnconfigure(1, weight=1)
brushes.grid(row=2, column=0)

brush_shape = ("circ", 0, 0)


def setbrush(shape, a, b):
    global brush_shape
    brush_shape = (shape, a, b)
    brush_preview()

pad = 5


round_brush = tk.Button(brushes, text="Round", width =8, pady=pad, command=lambda:setbrush("circ", 0, 0))
round_brush.grid(row=0, column=0)

sq_brush = tk.Button(brushes, text="Square", width =8, pady=pad, command=lambda:setbrush("rect", 0, 0))
sq_brush.grid(row=0, column=1)

#COLOUR
colours = tk.LabelFrame(toolbar, text="Colour")
colours.grid(row=3, column=0)

hsb_size = 144

def hsb_square(hue):
    img = Image.new("RGB", (hsb_size, hsb_size))
    pixels = img.load()

    for y in range(hsb_size):
        brightness = 1 - (y/(hsb_size - 1))
        for x in range(hsb_size):
            saturation = x / (hsb_size -1)
            r, g, b = colorsys.hsv_to_rgb(hue, saturation, brightness)
            pixels[x, y]= (
                int(r*255),
                int(g*255),
                int(b*255)
            )
    return ImageTk.PhotoImage(img)

def clamp(value, min_=0.0, max_=1.0):
    return max(min_, min(value, max_))

def update_hue(value):
    global img_tk
    hue = float(value) / 360
    img_tk = hsb_square(hue)
    hsb_canvas.itemconfig(image_id, image=img_tk)

hsb_canvas = tk.Canvas(colours, width=hsb_size, height=hsb_size)
hsb_canvas.grid(row=3, column=0)
hsb_canvas.grid_propagate(False)

img_tk = hsb_square(0)
image_id = hsb_canvas.create_image(0, 0, anchor="nw", image=img_tk)

hue_slider = tk.Scale(colours, from_=0, to=360, orient="horizontal", showvalue=False, command=update_hue, length=140)
hue_slider.grid(row=4, column=0)
hue_slider.grid_propagate(False)

current_col = tk.Canvas(colours, width=hsb_size, height=hsb_size // 4, bg="black")
current_col.grid(row=5, column=0)


def pick_colour(event):
    global colour
    x = clamp(event.x, 0, hsb_size - 1)
    y = clamp(event.y, 0, hsb_size - 1)

    saturation = clamp(x / (hsb_size -1))
    brightness = 1 -(y / (hsb_size - 1))
    hue = clamp(hue_slider.get() / 360)
    r, g, b = colorsys.hsv_to_rgb(hue, saturation, brightness)
    colour = "#%02x%02x%02x" % (round(r*255), round(g*255), round(b*255))
    current_col.config(bg=colour)


    global inv_colour
    inv_colour = "#%02x%02x%02x" % (255-int(colour[1:3], 16), 255-int(colour[3:5], 16), 255-int(colour[5:7], 16))
    hsb_canvas.coords(reticle, event.x - rad, event.y - rad, event.x + rad, event.y + rad)
    hsb_canvas.itemconfig(reticle, outline=inv_colour)
    #Reticle
    brush_preview()

rad = 5
reticle = hsb_canvas.create_oval(hsb_size - rad, hsb_size - rad, hsb_size + rad, hsb_size + rad, fill="", outline="white")

colour = "black"
inv_colour="white"

hsb_canvas.bind("<Button-1>", pick_colour)
hsb_canvas.bind("<B1-Motion>", pick_colour)

#DRAWING LOGIC
def paint(event):
    global brush_shape
    global colour
    x = event.x 
    y = event.y
    
    if brush_shape[0] == "rect":
        canvas.create_rectangle(
            #Top Left
            x - brush_size - brush_shape[1], 
            y - brush_size - brush_shape[2],
            # #Bottom Right
            x + brush_size + brush_shape[1],
            y + brush_size + brush_shape[2],
        
        #Colour
        
        fill=colour,
        outline=""
    )
        
    if brush_shape[0] == "circ":
        canvas.create_oval(
            #Top Left
            x - brush_size - brush_shape[1], 
            y - brush_size - brush_shape[2],
            # #Bottom Right
            x + brush_size + brush_shape[1],
            y + brush_size + brush_shape[2],
        
        #Colour
        
        fill=colour,
        outline=""
    )    

canvas.bind("<Button-1>", paint)
canvas.bind("<B1-Motion>", paint)

def save_canvas_png(canvas):
    file_path = filedialog.asksaveasfilename(
        defaultextension=".jpg",
        filetypes=[
            ("PNG File", "*.png"),
            ("JPEG File", "*.jpg")
            ]
    )
    
    if not file_path:
        return
    
    fd, ps_file = tempfile.mkstemp(suffix=".ps")
    os.close(fd)
    try:
        canvas.postscript(
            file=ps_file, 
            colormode="color",
            width=canvas.winfo_width(),
            height=canvas.winfo_height()
            )
    
        with Image.open(ps_file) as img:
            img.load(scale=1)
    
            if file_path.lower().endswith(".png"):
                img.save(file_path, "PNG")
            else:
                img.save(file_path, "JPEG", quality=95)

    finally:
        os.remove(ps_file)

save = tk.Button(toolbar, text="Save", width=5, command= lambda: save_canvas_png(canvas))
save.grid(row=9, column=0, sticky="sw")
save.grid_propagate(False)

clear = tk.Button(toolbar, text="Clear", width=5, command=lambda: canvas.delete("all"))
clear.grid(row=9, column=0,)
clear.grid_propagate(False)

exit = tk.Button(toolbar, text="Exit", width=5, command=root.destroy)
exit.grid(row=9, column=0, sticky="e")
exit.grid_propagate(False)

root.mainloop()