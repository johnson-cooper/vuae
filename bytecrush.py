import cv2
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import numpy as np
from tqdm import tqdm
from tkinter import PhotoImage
from PIL import Image, ImageTk
import threading

smaller_width = 640  # Replace with your desired width
smaller_height = 480  # Replace with your desired height

def upscale_and_enhance_video(input_path, output_path, scale_factor, sharpen_intensity, denoise_strength, deinterlace_strength):
    try:
        # Open the input video file
        cap = cv2.VideoCapture(input_path)

        # Get the original video's frame width and height
        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))

        # Calculate the new frame dimensions after upscaling
        new_width = int(frame_width * scale_factor)
        new_height = int(frame_height * scale_factor)

        # Define the codec and create a VideoWriter object to save the output video
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, 30.0, (new_width, new_height))

        # Calculate the total number of frames in the video
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Create a tqdm progress bar
        progress_bar = tqdm(total=total_frames, desc="Processing Frames", unit="frame")

        # Loop through the frames of the input video
        while True:
            ret, frame = cap.read()

            # Break the loop if we have reached the end of the video
            if not ret:
                break

            # Apply sharpening with user-defined intensity
            if sharpen_intensity > 0:
                kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]], dtype=np.float32)
                frame = cv2.filter2D(frame, -1, kernel)

            # Reduce frame size before denoising
            frame = cv2.resize(frame, (smaller_width, smaller_height))
            frame = cv2.fastNlMeansDenoisingColored(frame, None, denoise_strength, 10, 7, 21)

            # Apply deinterlacing with user-defined strength
            if deinterlace_strength > 0:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)
                frame[:, :, 1] = cv2.equalizeHist(frame[:, :, 1])
                frame[:, :, 2] = cv2.equalizeHist(frame[:, :, 2])
                frame = cv2.cvtColor(frame, cv2.COLOR_YUV2BGR)

            # Resize the frame to the new dimensions
            resized_frame = cv2.resize(frame, (new_width, new_height))

            # Write the resized frame to the output video
            out.write(resized_frame)

            # Update the progress bar
            progress_bar.update(1)

        # Close the progress bar
        progress_bar.close()

        # Release video objects
        cap.release()
        out.release()

        print("Video upscaling and enhancement complete. Output saved as", output_path)

    except Exception as e:
        print("An error occurred:", str(e))



def upscale_button_click():
    input_video_path = input_path_var.get()
    output_video_path = output_path_var.get()
    scale_factor = float(scale_factor_entry.get())
    sharpen_intensity = sharpen_intensity_scale.get()
    denoise_strength = denoise_strength_scale.get()
    deinterlace_strength = deinterlace_strength_scale.get()

    # Start a thread for the video preview
    preview_thread = threading.Thread(target=update_preview)
    preview_thread.daemon = True
    preview_thread.start()

    # Start video processing
    upscale_and_enhance_video(input_video_path, output_video_path, scale_factor, sharpen_intensity, denoise_strength, deinterlace_strength)

def update_preview():
    try:
        cap = cv2.VideoCapture(input_path_var.get())
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            # Apply the selected effects to the frame (same as in upscale_and_enhance_video)
            frame = cv2.resize(frame, (400, 300))
            if sharpen_intensity_scale.get() > 0:
                kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]], dtype=np.float32)
                frame = cv2.filter2D(frame, -1, kernel)
            if denoise_strength_scale.get() > 0:
                frame = cv2.fastNlMeansDenoisingColored(frame, None, denoise_strength_scale.get(), 10, 7, 21)
            if deinterlace_strength_scale.get() > 0:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)
                frame[:, :, 1] = cv2.equalizeHist(frame[:, :, 1])
                frame[:, :, 2] = cv2.equalizeHist(frame[:, :, 2])
                frame = cv2.cvtColor(frame, cv2.COLOR_YUV2BGR)
            # Convert the frame to RGB for displaying in Tkinter
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            photo = ImageTk.PhotoImage(image=Image.fromarray(frame_rgb))
            preview_label.config(image=photo)
            preview_label.photo = photo
            preview_label.update()
    except Exception as e:
        print("An error occurred during preview:", str(e))

def start_preview():
    # Start a thread for the video preview
    preview_thread = threading.Thread(target=update_preview)
    preview_thread.daemon = True
    preview_thread.start()        


# Create the main GUI window
root = tk.Tk()
root.title("Bytecrush - Video Upscaler and Enhancer")
root.iconbitmap('favicon.ico')

style = ttk.Style()

# Set the theme to "clam" or any other built-in theme
style.theme_use("clam")  # You can change "clam" to other available th

try:
    
    # Set dark mode theme
    root.tk_setPalette(background='#FFFFFF', foreground='#1e1e1e')

    # Set larger window size
    root.geometry("800x600")

    # Load the background image
    bg_image = PhotoImage(file="background.png")  # Replace "background.png" with your image file

    # Create a Label widget to display the background image
    background_label = tk.Label(root, image=bg_image)
    background_label.place(relwidth=1, relheight=1)
            

    # Buttons and forms on the left
    form_frame = tk.Frame(root)
    form_frame.pack(side="left", padx=20, pady=10)

    # Create a Label widget for the video preview
    preview_label = tk.Label(form_frame)
    preview_label.pack(side="right", padx=20, pady=10)

    # Input video path File Dialog button
    input_path_label = tk.Label(form_frame, text="Select Input Video:", fg='#1e1e1e', bg='white')
    input_path_label.pack()
    input_path_var = tk.StringVar()
    input_path_entry = tk.Entry(form_frame, textvariable=input_path_var, state='readonly')
    input_path_entry.pack()

    def browse_input_path():
        file_path = filedialog.askopenfilename(title="Select Input Video File", filetypes=[("Video Files", "*.mp4")])
        if file_path:
            input_path_var.set(file_path)

    input_browse_button = tk.Button(form_frame, text="Browse", command=browse_input_path)
    input_browse_button.pack()

    # Output video path File Dialog button
    output_path_label = tk.Label(form_frame, text="Select Output Video:", fg='#1e1e1e', bg='white')
    output_path_label.pack()
    output_path_var = tk.StringVar()
    output_path_entry = tk.Entry(form_frame, textvariable=output_path_var, state='readonly')
    output_path_entry.pack()
 
    def browse_output_path():
        file_path = filedialog.asksaveasfilename(title="Save Output Video As", filetypes=[("Video Files", "*.mp4")])
        if file_path:
            output_path_var.set(file_path)

    output_browse_button = tk.Button(form_frame, text="Browse", command=browse_output_path)
    output_browse_button.pack()

    # Scale factor label and entry
    scale_factor_label = tk.Label(form_frame, text="Scale Factor:", fg='#1e1e1e', bg='white')
    scale_factor_label.pack()
    scale_factor_entry = tk.Entry(form_frame)
    scale_factor_entry.pack()

    # Sharpening intensity slider
    sharpen_intensity_label = tk.Label(form_frame, text="Sharpening Intensity", fg='#1e1e1e', bg='white')
    sharpen_intensity_label.pack(anchor="w")
    sharpen_intensity_scale = ttk.Scale(form_frame, from_=0, to=10, orient="horizontal")
    sharpen_intensity_scale.set(0)  # Default value
    sharpen_intensity_scale.pack(fill="x")

    # Denoise strength slider
    denoise_strength_label = tk.Label(form_frame, text="Denoise Strength", fg='#1e1e1e', bg='white')
    denoise_strength_label.pack(anchor="w")
    denoise_strength_scale = ttk.Scale(form_frame, from_=0, to=10, orient="horizontal")
    denoise_strength_scale.set(0)  # Default value
    denoise_strength_scale.pack(fill="x")

    # Deinterlace strength slider
    deinterlace_strength_label = tk.Label(form_frame, text="Deinterlace Strength", fg='#1e1e1e', bg='white')
    deinterlace_strength_label.pack(anchor="w")
    deinterlace_strength_scale = ttk.Scale(form_frame, from_=0, to=10, orient="horizontal")
    deinterlace_strength_scale.set(0)  # Default value
    deinterlace_strength_scale.pack(fill="x")

    # Upscale button
    upscale_button = tk.Button(form_frame, text="Upscale and Enhance Video", command=upscale_button_click)
    upscale_button.pack()

        # Create a "Preview" button
    preview_button = tk.Button(form_frame, text="Preview", command=start_preview)
    preview_button.pack()

    # Start the GUI main loop
    root.mainloop()

except Exception as e:
    print("An error occurred:", str(e))