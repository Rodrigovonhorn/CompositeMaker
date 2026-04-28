import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk
from pathlib import Path
import sys

# Main window
window = tk.Tk()
window.geometry("700x650")
window.resizable(False, False)

# Background color
background_color = "#D9D9D9"
window.configure(bg=background_color)  # Can be hex or color name, e.g., "lightblue"

# Default font settings
default_font_size = 18
default_font_family = "Commissioner"

# Base directories (EXE vs development)
if getattr(sys, 'frozen', False):
    # Where the EXE is located → used to save output files
    BASE_DIR = Path(sys.executable).parent
    # Where PyInstaller extracts bundled resources → used to load assets
    AUX_DIR = Path(sys._MEIPASS) / "Assets"
else:
    BASE_DIR = Path(__file__).parent
    AUX_DIR = BASE_DIR / "Assets"

# Template and assets
TEMPLATE_PATH = AUX_DIR / "template_vertical.png"
FONT_PATH = AUX_DIR / "Commissioner-Regular.ttf"
FONT_PATH_NAME = AUX_DIR / "Commissioner-Regular.ttf"
LOGO_PATH = AUX_DIR / "your_logo_here.png"

# Selected photos list
selected_photos = []
MAX_PHOTOS = 3  # Maximum number of photos allowed

# Labels to display selected file paths
photo_labels = []

for i in range(MAX_PHOTOS):
    lbl = tk.Label(
        window,
        text="",
        font=("Arial", 10),
        bg="#D9D9D9",
        anchor="w",       # left aligned
        justify="left",   # left justification for wrapped text
        wraplength=418    # max width before wrapping (pixels)
    )
    lbl.place(x=262, y=423 + i * 40)
    photo_labels.append(lbl)


def select_photo():
    """Opens file dialog and stores up to 3 selected photos."""
    global selected_photos

    path = filedialog.askopenfilename(
        title="Select a photo",
        filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.webp")]
    )

    if not path:
        return  # user cancelled

    # If already at max, remove the oldest
    if len(selected_photos) >= MAX_PHOTOS:
        selected_photos.pop(0)

    selected_photos.append(path)

    # Update labels
    for i in range(MAX_PHOTOS):
        if i < len(selected_photos):
            photo_labels[i].config(text=selected_photos[i])
        else:
            photo_labels[i].config(text="")


def draw_text_wrapped(draw, text, font, x, y, max_width, line_spacing=5, fill="black"):
    """Draws text with automatic line wrapping."""
    words = text.split()
    line = ""

    for word in words:
        test_line = line + word + " "
        w, h = draw.textsize(test_line, font=font)

        if w <= max_width:
            line = test_line
        else:
            draw.text((x, y), line, font=font, fill=fill)
            y += h + line_spacing
            line = word + " "

    draw.text((x, y), line, font=font, fill=fill)


def create_composite():
    """Generates the composite image based on user input."""
    # User inputs
    name = entry_name.get().strip()
    height = entry_height.get().strip()
    size = entry_size.get().strip()
    hair = entry_hair.get().strip()
    eyes = entry_eyes.get().strip()
    save_name = entry_save_as.get().strip()

    if not save_name:
        save_name = "composite_no_name"

    # Load template
    template = Image.open(str(TEMPLATE_PATH)).convert("RGBA")
    draw = ImageDraw.Draw(template)

    # Fonts
    font = ImageFont.truetype(str(FONT_PATH), 60)
    font_name = ImageFont.truetype(str(FONT_PATH_NAME), 84)

    # Center the name at the top
    img_width, img_height = template.size
    text_width, text_height = draw.textsize(name, font=font_name)

    x = (img_width - text_width) / 2
    y = 22  # top margin

    max_width = 400  # max width for wrapped text

    # Draw text
    draw.text((x, y), name, font=font_name, fill="black")

    draw_text_wrapped(draw, height, font, 616, 249, max_width)
    draw_text_wrapped(draw, size, font, 616, 444, max_width)
    draw_text_wrapped(draw, eyes, font, 616, 639, max_width)
    draw_text_wrapped(draw, hair, font, 616, 884, max_width)

    # Photo placeholders
    placeholders = [
        (40, 170, 580, 980),      # photo 1
        (40, 1110, 473, 1762),    # photo 2
        (580, 1110, 1013, 1762)   # photo 3
    ]

    # Insert photos
    for i, path in enumerate(selected_photos[:3]):
        try:
            img = Image.open(path).convert("RGBA")

            x1, y1, x2, y2 = placeholders[i]
            pw, ph = x2 - x1, y2 - y1

            # Scale proportionally
            scale_w = pw / img.width
            scale_h = ph / img.height
            scale = min(scale_w, scale_h)

            new_w = int(img.width * scale)
            new_h = int(img.height * scale)

            img = img.resize((new_w, new_h), Image.ANTIALIAS)

            ix = x1 + (pw - new_w) // 2
            iy = y1

            template.paste(img, (ix, iy), img)

        except Exception as e:
            print(f"Error inserting photo {i + 1}: {e}")

    # Save output
    out_file = BASE_DIR / f"{save_name}.png"
    template.save(out_file)
    print(f"Composite saved at: {out_file}")

    messagebox.showinfo("Success", f"The composite '{save_name}' was created successfully!")

    window.destroy()

# Window title
window.title("Create Composite")

# Load logo image
logo_img = Image.open(str(LOGO_PATH))

# Resize logo while keeping proportions
desired_width = 146
desired_height = 146
logo_img_resized = logo_img.resize((desired_width, desired_height), Image.LANCZOS)

# Convert to Tkinter-compatible image
logo_img_tk = ImageTk.PhotoImage(logo_img_resized)

# Display logo
logo_label = tk.Label(window, image=logo_img_tk, bg=background_color)
logo_label.place(x=547, y=4)

# Info label
label_info = tk.Label(
    window,
    text="Fill in the information below to create the Composite",
    font=(default_font_family, default_font_size),
    justify="left",
    bg=background_color,
    anchor="w",
    wraplength=482
)
label_info.place(x=35, y=43)

# Name label
label_name = tk.Label(window, text="Name:", font=(default_font_family, default_font_size), bg=background_color)
label_name.place(x=35, y=133)

# Name entry
entry_name = tk.Entry(
    window,
    font=(default_font_family, default_font_size),
    width=30,
    fg="black",
    bg="white"
)
entry_name.place(x=117, y=133, width=430, height=34)

# Height label
label_height = tk.Label(window, text="Height:", font=(default_font_family, default_font_size), bg=background_color)
label_height.place(x=35, y=191)

# Height entry
entry_height = tk.Entry(
    window,
    font=(default_font_family, default_font_size),
    width=30,
    fg="black",
    bg="white"
)
entry_height.place(x=127, y=191, width=75, height=34)

# Size label
label_size = tk.Label(window, text="Size:", font=(default_font_family, default_font_size), bg=background_color)
label_size.place(x=338, y=191)

# Size entry
entry_size = tk.Entry(
    window,
    font=(default_font_family, default_font_size),
    width=30,
    fg="black",
    bg="white"
)
entry_size.place(x=401, y=191, width=75, height=34)

# Hair label
label_hair = tk.Label(window, text="Hair:", font=(default_font_family, default_font_size), bg=background_color)
label_hair.place(x=35, y=249)

# Hair entry
entry_hair = tk.Entry(
    window,
    font=(default_font_family, default_font_size),
    width=30,
    fg="black",
    bg="white"
)
entry_hair.place(x=100, y=249, width=406, height=34)

# Eyes label
label_eyes = tk.Label(window, text="Eyes:", font=(default_font_family, default_font_size), bg=background_color)
label_eyes.place(x=35, y=307)

# Eyes entry
entry_eyes = tk.Entry(
    window,
    font=(default_font_family, default_font_size),
    width=30,
    fg="black",
    bg="white"
)
entry_eyes.place(x=105, y=307, width=428, height=34)

# Save as label
label_save_as = tk.Label(window, text="Save file as:", font=(default_font_family, default_font_size), bg=background_color)
label_save_as.place(x=35, y=365)

# Save as entry
entry_save_as = tk.Entry(
    window,
    font=(default_font_family, default_font_size),
    width=30,
    fg="black",
    bg="white"
)
entry_save_as.place(x=172, y=365, width=270, height=34)

# Select photos button
button_select_photos = tk.Button(
    window,
    text="Select 3 photos",
    font=(default_font_family, default_font_size),
    bg="#919191",
    fg="black",
    command=select_photo
)
button_select_photos.place(x=35, y=423, width=210, height=48)

# Create composite button
button_create = tk.Button(
    window,
    text="Create",
    font=(default_font_family, default_font_size),
    bg="#919191",
    fg="black",
    command=create_composite
)
button_create.place(x=235, y=581, width=210, height=48)

# Start window loop
window.mainloop()