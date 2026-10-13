import os
import glob
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont

# MoviePy v2.0+ Split Imports
from moviepy.video.io.ImageClip import ImageClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.audio.AudioClip import CompositeAudioClip
import moviepy.audio.effects as afx

class VideoImproviserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Video Timeline Improviser")
        self.root.geometry("1000x680")
        
        # Application State
        self.timeline_segments = []
        self.selected_index = None
        self.audio_file = "temp_voiceover.mp3"
        
        self.create_layout()

    def create_layout(self):
        # Left Panel: Settings & Audio Processing Options
        left_panel = ttk.Frame(self.root, padding=10)
        left_panel.pack(side="left", fill="y", width=340)
        
        ttk.Label(left_panel, text="1. Enter Paragraph:", font=("Arial", 10, "bold")).pack(anchor="w", pady=2)
        self.text_entry = tk.Text(left_panel, height=4, width=38)
        self.text_entry.insert("1.0", "Python automatically blends text audio and background music.")
        self.text_entry.pack(fill="x", pady=5)
        
        ttk.Button(left_panel, text="Initialize Word Segments", command=self.initialize_segments).pack(fill="x", pady=5)
        
        ttk.Separator(left_panel, orient="horizontal").pack(fill="x", pady=10)
        
        # Audio Engine Checkbox Options Panel
        audio_frame = ttk.LabelFrame(left_panel, text=" Audio Mode Configurations ", padding=10)
        audio_frame.pack(fill="x", pady=5)
        
        self.stretch_voice_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(audio_frame, text="Enable Time-Stretching (Slow-Mo Voice)", variable=self.stretch_voice_var).pack(anchor="w", pady=2)
        
        self.bg_music_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(audio_frame, text="Enable Background Music Mix", variable=self.bg_music_var, command=self.toggle_music_browse).pack(anchor="w", pady=2)
        
        self.music_path_var = tk.StringVar()
        self.music_row = ttk.Frame(audio_frame)
        ttk.Entry(self.music_row, textvariable=self.music_path_var, width=24).pack(side="left", fill="x", expand=True)
        self.music_btn = ttk.Button(self.music_row, text="...", width=3, command=self.browse_music_file)
        self.music_btn.pack(side="right", padx=2)
        
        self.toggle_music_browse()

        ttk.Separator(left_panel, orient="horizontal").pack(fill="x", pady=10)

        # Timeline Modifier Form
        self.edit_frame = ttk.LabelFrame(left_panel, text=" Modify Selected Segment Range ", padding=10)
        self.edit_frame.pack(fill="x", pady=5)
        
        ttk.Label(self.edit_frame, text="Word/Text:").pack(anchor="w")
        self.edit_text_var = tk.StringVar()
        ttk.Entry(self.edit_frame, textvariable=self.edit_text_var).pack(fill="x", pady=2)
        
        ttk.Label(self.edit_frame, text="Screen Hold Duration (Seconds):").pack(anchor="w", pady=5)
        self.edit_dur_var = tk.DoubleVar()
        ttk.Spinbox(self.edit_frame, from_=0.1, to=30.0, increment=0.1, textvariable=self.edit_dur_var).pack(fill="x", pady=2)
        
        ttk.Label(self.edit_frame, text="Custom Image Path:").pack(anchor="w", pady=5)
        self.edit_img_var = tk.StringVar()
        img_row = ttk.Frame(self.edit_frame)
        img_row.pack(fill="x")
        ttk.Entry(img_row, textvariable=self.edit_img_var, width=24).pack(side="left", fill="x", expand=True)
        ttk.Button(img_row, text="...", width=3, command=self.browse_segment_image).pack(side="right", padx=2)
        
        ttk.Button(self.edit_frame, text="Apply Changes to Selected Index", command=self.save_modifications).pack(fill="x", pady=10)

        # Right Panel: Interactive Timeline Map View Grid
        right_panel = ttk.Frame(self.root, padding=10)
        right_panel.pack(side="right", fill="both", expand=True)
        
        ttk.Label(right_panel, text="2. Interactive Video Timeline Map View:", font=("Arial", 10, "bold")).pack(anchor="w", pady=2)
        
        columns = ("id", "range", "text", "duration", "image")
        self.tree = ttk.Treeview(right_panel, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("id", text="Idx")
        self.tree.heading("range", text="Playback Timestamp Frame")
        self.tree.heading("text", text="Word Screen Text")
        self.tree.heading("duration", text="Duration")
        self.tree.heading("image", text="Visual Background Image Asset")
        
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("range", width=170, anchor="center")
        self.tree.column("text", width=140, anchor="w")
        self.tree.column("duration", width=70, anchor="center")
        self.tree.column("image", width=180, anchor="w")
        
        self.tree.pack(fill="both", expand=True, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_segment_selected)
        
        ttk.Button(right_panel, text="🎬 Render & Compile Mixed Output Video (.mp4)", command=self.render_video).pack(fill="x", pady=5)

    def toggle_music_browse(self):
        if self.bg_music_var.get():
            self.music_row.pack(fill="x", pady=5)
        else:
            self.music_row.pack_forget()

    def browse_music_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])
        if file_path:
            self.music_path_var.set(file_path)

    def browse_segment_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file_path:
            self.edit_img_var.set(file_path)

    def initialize_segments(self):
        text = self.text_entry.get("1.0", "end-1c").strip()
        words = [w.strip(".,!?\"'") for w in text.split() if w.strip()]
        
        if not words:
            messagebox.showerror("Error", "Please input text.")
            return
            
        self.timeline_segments = []
        for word in words:
            self.timeline_segments.append({
                "text": word,
                "duration": 1.0, 
                "image_path": ""
            })
        self.refresh_timeline_ui()

    def refresh_timeline_ui(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        current_time = 0.0
        for idx, seg in enumerate(self.timeline_segments):
            start_time = current_time
            end_time = current_time + seg["duration"]
            range_str = f"{start_time:.2f}s  ➔  {end_time:.2f}s"
            img_display = os.path.basename(seg["image_path"]) if seg["image_path"] else "[Default Solid Canvas]"
            
            self.tree.insert("", "end", iid=str(idx), values=(
                idx + 1, range_str, seg["text"], f"{seg['duration']:.2f}s", img_display
            ))
            current_time = end_time

    def on_segment_selected(self, event):
        selected_items = self.tree.selection()
        if not selected_items:
            return
        self.selected_index = int(selected_items[0])
        seg = self.timeline_segments[self.selected_index]
        
        self.edit_text_var.set(seg["text"])
        self.edit_dur_var.set(seg["duration"])
        self.edit_img_var.set(seg["image_path"])

    def save_modifications(self):
        if self.selected_index is None:
            messagebox.showwarning("Selection Missing", "Click a timeline row to select it first.")
            return
        self.timeline_segments[self.selected_index]["text"] = self.edit_text_var.get()
        self.timeline_segments[self.selected_index]["duration"] = float(self.edit_dur_var.get())
        self.timeline_segments[self.selected_index]["image_path"] = self.edit_img_var.get()
        self.refresh_timeline_ui()

    def render_video(self):
        if not self.timeline_segments:
            messagebox.showerror("Error", "Timeline map is empty.")
            return

        output_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 Video", "*.mp4")])

        if not output_path:
            return

        width, height = 1280, 720
        video_clips = []

        try:
            font = ImageFont.truetype("arial.ttf", 60)
        except IOError:
            font = ImageFont.load_default()

        use_time_stretch = self.stretch_voice_var.get()
        use_bg_music = self.bg_music_var.get()
        music_file = self.music_path_var.get()

        if not use_time_stretch:
            full_paragraph = " ".join([seg["text"] for seg in self.timeline_segments])
            gTTS(text=full_paragraph, lang='en').save(self.audio_file)
            voice_audio = AudioFileClip(self.audio_file)

        for i, seg in enumerate(self.timeline_segments):
            text = seg["text"]
            duration = seg["duration"]
            bg_path = seg["image_path"]
            
            if bg_path and os.path.exists(bg_path):
                img = Image.open(bg_path).resize((width, height))
            else:
                img = Image.new("RGB", (width, height), color=(35, 35, 45))
                
            draw = ImageDraw.Draw(img)

            if hasattr(draw, "textbbox"):
                bbox = draw.textbbox((0, 0), text, font=font)
                w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            else:
                w, h = draw.textsize(text, font=font)

            pos = ((width - w) // 2, (height - h) // 2)
            draw.text(pos, text, fill=(255, 255, 255), font=font)
            
            temp_img = f"master_img_cache_{i}.png"
            img.save(temp_img)
            
        # MoviePy 2.0 Change: .with_duration() instead of .set_duration() Use code with caution.
        v_clip = ImageClip(temp_img).with_duration(duration)
    
        if use_time_stretch:
            temp_word_voice = f"word_{i}.mp3"
            gTTS(text=text, lang='en').save(temp_word_voice)
            word_audio = AudioFileClip(temp_word_voice)
            stretch_factor = word_audio.duration / duration
            # MoviePy 2.0 Change: .with_effects() instead of .fx()

            stretched_audio = word_audio.with_effects([afx.TimeStretch(stretch_factor)])
            v_clip = v_clip.with_audio(stretched_audio)
            video_clips.append(v_clip)
            final_video = concatenate_videoclips(video_clips, method="compose")
            total_duration = final_video.duration

        if not use_time_stretch:
            if voice_audio.duration > total_duration:
                voice_audio = voice_audio.subclip(0, total_duration)
            if use_bg_music and music_file and os.path.exists(music_file):
                music_audio = AudioFileClip(music_file).subclip(0, total_duration).volumex(0.2)
                mixed_audio = CompositeAudioClip([voice_audio, music_audio])
                final_video = final_video.with_audio(mixed_audio)
            else:
                final_video = final_video.with_audio(voice_audio)
        else:
            if use_bg_music and music_file and os.path.exists(music_file):
                music_audio = AudioFileClip(music_file).subclip(0, total_duration).volumex(0.2)
                final_video = final_video.with_audio(CompositeAudioClip([final_video.audio, music_audio]))
                final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
                final_video.close()
    
        if not use_time_stretch:
            voice_audio.close()
    
        try: os.remove(self.audio_file)
        except: pass

        for i in range(len(self.timeline_segments)):
            try: os.remove(f"master_img_cache_{i}.png")
            except: pass

            if use_time_stretch:
                try: os.remove(f"word_{i}.mp3")
                except: pass
            messagebox.showinfo("Finished", f"Video exported successfully:\n{output_path}")

    if name == "main":
        root = tk.Tk()
        app = VideoImproviserApp(root)
        root.mainloop()