এখানে Python-এর tkinter লাইব্রেরি ব্যবহার করে একটি রেসপনসিভ Grid Canvas-এর অবজেক্ট-ওরিয়েন্টেড (OOP) কাস্টম ক্লাস ডিজাইন দেখানো হলো। এই কোডে ক্যানভাসের ওপর একটি গ্রিড আঁকা হবে এবং মাউস ক্লিকের মাধ্যমে গ্রিডের নির্দিষ্ট ঘর (cell) সনাক্ত করে রঙ পরিবর্তন করার ফিচার অন্তর্ভুক্ত করা হয়েছে।
## কাস্টম ক্লাস ডিজাইন কোড উদাহরণ

import tkinter as tk
class GridCanvas(tk.Canvas):
    """
    একটি কাস্টম ক্যানভাস ক্লাস যা গ্রিড লেআউট ম্যানেজ করে এবং মাউস ইন্টারেকশন সাপোর্ট করে।
    """
    def __init__(self, parent, rows=10, cols=10, cell_size=40, grid_color="#CCCCCC", **kwargs):
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.grid_color = grid_color
        
        # গ্রিডের ভেতরের ডাটা ট্র্যাকিং করার জন্য একটি 2D Matrix (0 = খালি, 1 = ফিল করা)
        self.grid_data = [[0 for _ in range(cols)] for _ in range(rows)]
        
        # ক্যানভাসের আসল সাইজ নির্ধারণ করা
        width = cols * cell_size
        height = rows * cell_size
        
        # মূল tk.Canvas ক্লাসকে ইনিশিয়ালাইজ করা
        super().__init__(parent, width=width, height=height, **kwargs)
        
        # গ্রিড লাইন ড্রয়িং এবং মাউস ইভেন্ট বাইন্ডিং
        self.draw_grid()
        self.bind("<Button-1>", self.on_cell_click)

    def draw_grid(self):
        """ক্যানভাসের ওপর গ্রিডের দাগ বা গ্রিড লাইনগুলো টানে।"""
        width = self.cols * self.cell_size
        height = self.rows * self.cell_size

        # উল্লম্ব (Vertical) রেখা অঙ্কন
        for col in range(self.cols + 1):
            x = col * self.cell_size
            self.create_line(x, 0, x, height, fill=self.grid_color, tags="grid_line")

        # অনুভূমিক (Horizontal) রেখা অঙ্কন
        for row in range(self.rows + 1):
            y = row * self.cell_size
            self.create_line(0, y, width, y, fill=self.grid_color, tags="grid_line")

    def on_cell_click(self, event):
        """মাউস ক্লিকের স্থানাঙ্ক (X, Y) থেকে গ্রিডের Row এবং Column বের করে।"""
        # ক্লিক করা কোঅর্ডিনেটকে সেল সাইজ দিয়ে ভাগ করে ইনডেক্স বের করা
        col = event.x // self.cell_size
        row = event.y // self.cell_size

        # ক্লিকটি গ্রিড সীমানার মধ্যে আছে কিনা তা নিশ্চিত করা
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.toggle_cell(row, col)

    def toggle_cell(self, row, col):
        """গ্রিড ঘরের স্টেট টগল করে এবং তার ভিজ্যুয়াল আপডেট করে।"""
        # ট্যাগ দিয়ে নির্দিষ্ট সেল আইডেন্টিফাই করা
        cell_tag = f"cell_{row}_{col}"
        
        if self.grid_data[row][col] == 0:
            # যদি ঘরটি খালি থাকে তবে ভরাট করা
            self.grid_data[row][col] = 1
            
            # সেলের চারদিকের স্থানাঙ্ক বের করা
            x1 = col * self.cell_size
            y1 = row * self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size
            
            # ক্যানভাসে চতুর্ভুজ (Rectangle) আঁকা
            self.create_rectangle(x1, y1, x2, y2, fill="#4CAF50", outline=self.grid_color, tags=cell_tag)
        else:
            # যদি ঘরটি আগে থেকেই ফিল করা থাকে তবে তা মুছে ফেলা
            self.grid_data[row][col] = 0
            self.delete(cell_tag)
            
        # গ্রিড লাইন যাতে কালারের নিচে ঢাকা না পড়ে, তাই লাইনগুলোকে সবার ওপরে আনা
        self.tag_raise("grid_line")
# --- অ্যাপ্লিকেশন রান করার মূল অংশ ---if __name__ == "__main__":
    root = tk.Tk()
    root.title("Custom Grid Canvas Example")
    
    # কাস্টম গ্রিড ক্যানভাসের অবজেক্ট তৈরি (১৫টি রো এবং ২০টি কলাম)
    grid = GridCanvas(root, rows=15, cols=20, cell_size=35, bg="white")
    grid.pack(padx=10, pady=10)
    
    root.mainloop()

## ডিজাইনের বিস্তারিত ও কার্যপ্রণালী (Details)
১. ইনহেরিটেন্স (Inheritance): ক্লাসটিকে tk.Canvas থেকে ইনহেরিট (super().__init__) করা হয়েছে। ফলে এই ক্লাসটি সাধারণ ক্যানভাসের সব উইজেট বৈশিষ্ট্য পাওয়ার পাশাপাশি নিজের কাস্টম মেথডগুলোও ব্যবহার করতে পারে।
২. ডাটা ট্র্যাকিং (self.grid_data): গ্রিডের ভেতরের অবস্থা ট্র্যাক করার জন্য একটি 2D List (Matrix) ব্যবহার করা হয়েছে। এটি গেম ডেভেলপমেন্ট (যেমন- Game of Life, Pathfinding) বা পিক্সেল আর্ট এডিটরের ব্যাকএন্ড লজিক হ্যান্ডেল করতে সাহায্য করে।
৩. স্থানাঙ্ক রূপান্তর (Coordinate Mapping): event.x // self.cell_size সূত্রের সাহায্যে স্ক্রিনের পিক্সেল কোঅর্ডিনেটকে খুব সহজেই গ্রিডের ম্যাট্রিক্স ইনডেক্সে (Row/Col) রূপান্তর করা হয়েছে।
৪. ক্যানভাস ট্যাগিং (Canvas Tags): গ্রিডের প্রতিটি রেকট্যাঙ্গেল তৈরি করার সময় ইউনিক tags (যেমন: f"cell_{row}_{col}") দেওয়া হয়েছে। এর ফলে পরবর্তীতে নির্দিষ্ট ঘরের কালার রিফ্রেশ বা ডিলিট করা সহজ হয়।
৫. লেয়ার ম্যানেজমেন্ট (tag_raise): ক্যানভাসে নতুন অবজেক্ট আঁকলে তা আগের অবজেক্টের ওপর চলে আসে। ক্লিকের পর গ্রিডের বর্ডার বা লাইন যেন হারিয়ে না যায়, সেজন্য self.tag_raise("grid_line") দিয়ে গ্রিড লাইনকে সর্বদা সবার উপরে প্রদর্শন করা হয়েছে। [1, 2, 3, 4] 
আপনি যদি এই গ্রিডে আরও কোনো কাস্টম ফিচার যেমন জুম ইন/আউট (Zooming), ড্র্যাগ করে একসাথে অনেক ঘর সিলেক্ট করা, অথবা কোনো নির্দিষ্ট গেমের লজিক বসাতে চান, তবে জানাতে পারেন।

[1] [https://stackoverflow.com](https://stackoverflow.com/questions/55364449/how-to-display-a-grid-on-a-canvas-tkinter-object)
[2] [https://www.pythontutorial.net](https://www.pythontutorial.net/tkinter/tkinter-canvas/)
[3] [https://gist.github.com](https://gist.github.com/2306105)
[4] [https://stackoverflow.com](https://stackoverflow.com/questions/72385054/how-to-design-a-board-in-tkinter-canvas)

Python-এ **kwargs (Keyword Arguments)-এর অর্থ হলো "নামযুক্ত অনিয়মিত সংখ্যক আর্গুমেন্ট"।
সহজ কথায়, আপনি যখন এই কাস্টম GridCanvas ক্লাসটি তৈরি করবেন, তখন আপনার ডিফাইন করা নির্দিষ্ট প্যারামিটারগুলো (rows, cols, cell_size, grid_color) ছাড়াও tkinter.Canvas-এর অন্য যেকোনো স্ট্যান্ডার্ড প্রোপার্টি (যেমন: bg, bd, cursor, relief ইত্যাদি) সরাসরি পাস করতে পারবেন।
নিচে এর বিস্তারিত কার্যপ্রণালী দেওয়া হলো:
## ১. মূল কাজ (Pass-through Mechanism)
আমাদের GridCanvas ক্লাসটি মূলত tkinter.Canvas ক্লাসের একটি বর্ধিত রূপ (Child Class)। ক্যানভাসের নিজস্ব অসংখ্য কনফিগারেশন অপশন আছে। আমরা যদি **kwargs ব্যবহার না করতাম, তবে ব্যাকগ্রাউন্ড কালার পরিবর্তন করার জন্য আমাদের আলাদাভাবে bg="white" প্যারামিটারটি __init__ মেথডের ভেতরে লিখতে হতো।
**kwargs ব্যবহার করায় ডিকশনারি আকারে সব অতিরিক্ত আর্গুমেন্ট একসাথে ক্যাচ করা হয় এবং super().__init__(parent, ..., **kwargs) লাইনের মাধ্যমে তা মূল ক্যানভাস ক্লাসের কাছে পাঠিয়ে দেওয়া হয়।
## ২. একটি বাস্তব উদাহরণ
যেমন ধরুন, আপনি যখন ক্লাসটির অবজেক্ট তৈরি করছেন:

grid = GridCanvas(root, rows=15, cols=20, bg="white", highlightthickness=2, relief="sunken")

এখানে:

* rows=15 এবং cols=20 আপনার কাস্টম ক্লাসের নিজস্ব ভ্যারিয়েবলে জমা হবে।
* বাকি অংশ, অর্থাৎ bg="white", highlightthickness=2, এবং relief="sunken"—এই তিনটি আর্গুমেন্টকে **kwargs একটি ডিকশনারি (Dictionary) হিসেবে গ্রহণ করবে, যা দেখতে এমন হবে:

kwargs = {'bg': 'white', 'highlightthickness': 2, 'relief': 'sunken'}

* এরপর super().__init__ কল হওয়ার সময় এই ডিকশনারিটি আনপ্যাক (Unpack) হয়ে মূল ক্যানভাসের ব্যাকগ্রাউন্ড, বর্ডার ও রিলিফ সেট করে দেবে।

## ৩. **kwargs ব্যবহারের সুবিধা

* ফ্লেক্সিবিলিটি: tkinter.Canvas-এর শতশত বিল্ট-ইন প্রোপার্টি মুখস্থ করে কাস্টম ক্লাসে আলাদাভাবে লেখার প্রয়োজন পড়ে না।
* ক্লিন কোড: কোডের সাইজ ছোট থাকে এবং এটি ফিউচার-প্রুফ হয় (ভবিষ্যতে tkinter ক্যানভাসে নতুন কোনো ফিচার যুক্ত হলেও এই কাস্টম ক্লাসটি না ভেঙেই কাজ করবে)।

আপনি কি এই ক্লাসে কাস্টম মেথড ব্যবহার করে রানটাইমে ক্যানভাসের প্রোপার্টি পরিবর্তন করার কোনো লজিক যোগ করতে চান, নাকি এর লেআউট ম্যানেজমেন্ট নিয়ে আরও জানতে চান?

নিচে আগের কাস্টম GridCanvas কম্পোনেন্টটিকে ব্যবহার করে এবং সেটিকে একটি মূল অ্যাপ্লিকেশন ক্লাসের সাথে যুক্ত করে Interactive Drag & Drop / Slide লজিক ডিজাইন করে দেখানো হলো।
এখানে মাউস দিয়ে গ্রিডের ওপর যেকোনো জ্যামিতিক উপাদান (যেমন একটি বৃত্ত বা বল) ড্র্যাগ করে এক ঘর থেকে অন্য ঘরে স্লাইড বা মুভ করা যাবে।
## সম্পূর্ণ কার্যকারী কোড উদাহরণ

import tkinter as tk
# ১. আগের তৈরি করা কাস্টম গ্রিড ক্যানভাস কম্পোনেন্টclass GridCanvas(tk.Canvas):
    def __init__(self, parent, rows=15, cols=20, cell_size=40, grid_color="#E0E0E0", **kwargs):
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.grid_color = grid_color
        
        width = cols * cell_size
        height = rows * cell_size
        super().__init__(parent, width=width, height=height, **kwargs)
        self.draw_grid()

    def draw_grid(self):
        width = self.cols * self.cell_size
        height = self.rows * self.cell_size
        for col in range(self.cols + 1):
            x = col * self.cell_size
            self.create_line(x, 0, x, height, fill=self.grid_color, tags="grid_line")
        for row in range(self.rows + 1):
            y = row * self.cell_size
            self.create_line(0, y, width, y, fill=self.grid_color, tags="grid_line")

# ২. মূল অ্যাপ্লিকেশন ক্লাস (Geometry Engine) যা আপনার কম্পোনেন্টটি ব্যবহার করছেclass GeometryEngine:
    def __init__(self, root):
        # উইন্ডো কনফিগারেশন
        self.root = root
        self.root.title("Interactive Drag & Slide Geometry Engine")
        self.root.geometry("1000x800")
        self.root.config(bg="#F5F5F5")
        
        # ড্র্যাগ অ্যান্ড ড্রপ লজিকের জন্য ট্র্যাকিং ভ্যারিয়েবল
        self.selected_item = None
        self.drag_data = {"x": 0, "y": 0}
        
        # আপনার কাস্টম ক্যানভাস কম্পোনেন্ট ব্যবহার করা হলো
        self.canvas = GridCanvas(self.root, rows=16, cols=22, cell_size=40, bg="white", highlightthickness=0)
        self.canvas.pack(padx=20, pady=20, expand=True)
        
        # ক্যানভাসে একটি ড্র্যাগ করার মতো জ্যামিতিক অবজেক্ট (বৃত্ত) তৈরি করা
        self.create_geometry_object(2, 2, "circle")
        self.create_geometry_object(5, 4, "square")

        # মাউস ইভেন্ট বাইন্ডিং (Drag & Drop-এর জন্য)
        self.canvas.tag_bind("draggable", "<ButtonPress-1>", self.on_start_drag)
        self.canvas.tag_bind("draggable", "<B1-Motion>", self.on_drag)
        self.canvas.tag_bind("draggable", "<ButtonRelease-1>", self.on_drop)

    def create_geometry_object(self, row, col, shape_type):
        """গ্রিডের নির্দিষ্ট রো এবং কলামে একটি ড্র্যাগযোগ্য জ্যামিতিক অবজেক্ট তৈরি করে।"""
        size = self.canvas.cell_size
        x1 = col * size + 5   # সামান্য মার্জিন রাখা হয়েছে যাতে গ্রিড লাইনের মাঝে বসে
        y1 = row * size + 5
        x2 = x1 + size - 10
        y2 = y1 + size - 10
        
        if shape_type == "circle":
            # একটি নীল রঙের বৃত্ত তৈরি এবং সেটিকে "draggable" ট্যাগ দেওয়া
            self.canvas.create_oval(x1, y1, x2, y2, fill="#2196F3", outline="#0D47A1", width=2, tags="draggable")
        elif shape_type == "square":
            # একটি লাল রঙের চতুর্ভুজ তৈরি
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="#F44336", outline="#B71C1C", width=2, tags="draggable")
            
        self.canvas.tag_raise("grid_line") # গ্রিড লাইন যেন শেপের ওপরে থাকে

    def on_start_drag(self, event):
        """ব্যবহারকারী যখন অবজেক্টের ওপর মাউস ক্লিক করবে।"""
        # ক্লিক করা অবজেক্টের আইডি খুঁজে বের করা
        self.selected_item = self.canvas.find_closest(event.x, event.y)[0]
        # কারেন্ট মাউস পজিশন রেকর্ড করা
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_drag(self, event):
        """মাউস ক্লিক করে চেপে ধরে যখন ড্র্যাগ/মুভ করা হবে (Slide)।"""
        if not self.selected_item:
            return
            
        # মাউস কতটুকু সরল (Delta X, Delta Y) তা হিসাব করা
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        
        # অবজেক্টটিকে স্ক্রিনে সমপরিমাণ পিক্সেল মুভ করা
        self.canvas.move(self.selected_item, dx, dy)
        
        # পরবর্তী হিসেবের জন্য মাউসের নতুন পージিশন আপডেট করা
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_drop(self, event):
        """মাউস ছেড়ে দিলে অবজেক্টটি স্বয়ংক্রিয়ভাবে সবচেয়ে কাছের গ্রিড সেলে স্ন্যাপ (Snap) করবে।"""
        if not self.selected_item:
            return
            
        size = self.canvas.cell_size
        # অবজেক্টটির বর্তমান বাউন্ডিং বক্স (চারদিকের পিক্সেল কোঅর্ডিনেট) নেওয়া
        x1, y1, x2, y2 = self.canvas.coords(self.selected_item)
        
        # অবজেক্টের কেন্দ্রবিন্দু হিসাব করে সেটি কোন রো এবং কলামে আছে তা বের করা
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        
        target_col = int(center_x // size)
        target_row = int(center_y // size)
        
        # সীমানা পরীক্ষা (গ্রিডের বাইরে চলে যাওয়া রোধ করতে)
        target_col = max(0, min(target_col, self.canvas.cols - 1))
        target_row = max(0, min(target_row, self.canvas.rows - 1))
        
        # নিখুঁতভাবে গ্রিডের ঘরের ভেতর অবজেক্টটিকে বসানোর (Snap to Grid) নতুন পিক্সেল হিসাব
        new_x1 = target_col * size + 5
        new_y1 = target_row * size + 5
        
        # অবজেক্টটিকে ফাইনাল পজিশনে সেট করা
        self.canvas.moveto(self.selected_item, new_x1, new_y1)
        
        # গ্রিড লাইনগুলোকে শেপের উপরে রিফ্রেশ করা
        self.canvas.tag_raise("grid_line")
        
        # ড্র্যাগ প্রসেস শেষ, তাই ভ্যারিয়েবল রিসেট
        self.selected_item = None

# --- রান করার মূল অংশ ---if __name__ == "__main__":
    app_root = tk.Tk()
    engine = GeometryEngine(app_root)
    app_root.mainloop()

## এই ডিজাইনের মূল মেকানিজম (কিভাবে কাজ করছে):
১. GridCanvas কম্পোনেন্টের ব্যবহার: GeometryEngine ক্লাসের ভেতরে আমরা self.canvas = GridCanvas(...) লাইনের মাধ্যমে আপনার কাস্টম ক্যানভাসটিকে উইজেট হিসেবে বসিয়েছি।
২. ট্যাগ বাইন্ডিং (tag_bind): ক্যানভাসের সব অবজেক্টের ওপর মাউস ইভেন্ট না চালিয়ে, আমরা সুনির্দিষ্টভাবে "draggable" ট্যাগ দেওয়া অবজেক্টগুলোর ওপর মাউস ক্লিক ও ড্র্যাগ বাইন্ড করেছি। ফলে গ্রিড লাইনে ক্লিক করলে কিছুই হবে না, শুধু শেপগুলোতে কাজ করবে।
৩. স্মুথ স্লাইডিং লজিক (dx, dy): মাউস মুভ করার সময় প্রতি মুহূর্তে আগের পিক্সেল ও বর্তমান পিক্সেলের দূরত্ব (dx, dy) বের করে অবজেক্টটিকে ইনস্ট্যান্টলি সরানো হচ্ছে, যা একটি নিখুঁত Slide ইফেক্ট দেয়।
４. গ্রিডে স্ন্যাপ করা (Snap to Grid): মাউস ছেড়ে দেওয়ার সাথে সাথে on_drop মেথডটি শেপটিকে এলোমেলো জায়গায় থাকতে দেয় না। এটি ক্যানভাসের cell_size ব্যবহার করে অবজেক্টটিকে স্বয়ংক্রিয়ভাবে সবচেয়ে কাছের বর্গাকার ঘরের (Cell) চৌকাঠের ভেতর সোজা করে বসিয়ে দেয়।
আপনি কি এই জ্যামিতিক শেপগুলোর ওপর ক্লিক করলে কোনো লাইন তৈরি হওয়া বা দুটি বিন্দুর মধ্যে দূরত্ব পরিমাপ করার কোনো জ্যামিতিক রুলস যোগ করতে চান?

ক্যানভাসের চারপাশের গ্রিডে রো (Row) এবং কলাম (Col) নম্বর যুক্ত করার জন্য আমাদের কাস্টম GridCanvas ক্লাসের draw_grid মেথডটিকে কিছুটা মডিফাই করতে হবে।
নাম্বারিং করার জন্য গ্রিডের চারপাশে কিছুটা জায়গা (Padding/Margin) ছেড়ে দিতে হবে। নিচে কোডটি এমনভাবে আপডেট করা হয়েছে যাতে ক্যানভাসের বাম পাশে এবং ওপরে গ্রিড লাইনের বাইরে সুন্দরভাবে রো ও কলামের ইনডেক্স নম্বর (যেমন: 0, 1, 2...) দেখা যায়।
## মডিফাইড কাস্টম ক্যানভাস কোড উদাহরণ

import tkinter as tk
class GridCanvas(tk.Canvas):
    def __init__(self, parent, rows=15, cols=20, cell_size=40, grid_color="#E0E0E0", **kwargs):
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.grid_color = grid_color
        
        # নাম্বারিং বা লেবেলের জন্য অফসেট (পিক্সেল মার্জিন) নির্ধারণ করা
        self.offset_x = 30  # বাম পাশে রো নম্বরের জন্য জায়গা
        self.offset_y = 30  # ওপরে কলাম নম্বরের জন্য জায়গা
        
        # ক্যানভাসের মোট সাইজ (গ্রিড সাইজ + অফসেট মার্জিন)
        width = (cols * cell_size) + self.offset_x
        height = (rows * cell_size) + self.offset_y
        
        super().__init__(parent, width=width, height=height, **kwargs)
        self.draw_grid()

    def draw_grid(self):
        # গ্রিডের মূল সীমানা হিসাব
        grid_width = self.cols * self.cell_size
        grid_height = self.rows * self.cell_size

        # ১. উল্লম্ব (Vertical) রেখা এবং কলাম নম্বর অঙ্কন
        for col in range(self.cols + 1):
            x = self.offset_x + (col * self.cell_size)
            
            # গ্রিড লাইন টানা (অফসেট থেকে শুরু করে নিচে পর্যন্ত)
            self.create_line(x, self.offset_y, x, grid_height + self.offset_y, fill=self.grid_color, tags="grid_line")
            
            # কলাম নম্বর লেখা (শেষ লাইনের পর নম্বর যেন না বসে তাই শর্ত)
            if col < self.cols:
                label_x = x + (self.cell_size / 2)
                label_y = self.offset_y / 2  # অফসেটের ঠিক মাঝামাঝি উঁচুতে
                self.create_text(label_x, label_y, text=str(col), fill="#666666", font=("Arial", 10, "bold"), tags="label")

        # ২. অনুভূমিক (Horizontal) রেখা এবং রো নম্বর অঙ্কন
        for row in range(self.rows + 1):
            y = self.offset_y + (row * self.cell_size)
            
            # গ্রিড লাইন টানা (অফসেট থেকে শুরু করে ডানপাশ পর্যন্ত)
            self.create_line(self.offset_x, y, grid_width + self.offset_x, y, fill=self.grid_color, tags="grid_line")
            
            # রো নম্বর লেখা
            if row < self.rows:
                label_x = self.offset_x / 2  # অফসেটের ঠিক মাঝামাঝি বামে
                label_y = y + (self.cell_size / 2)
                self.create_text(label_x, label_y, text=str(row), fill="#666666", font=("Arial", 10, "bold"), tags="label")

class GeometryEngine:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Drag & Slide Geometry Engine")
        self.root.geometry("1000x800")
        
        self.selected_item = None
        self.drag_data = {"x": 0, "y": 0}
        
        # আমাদের নতুন ক্যানভাস কম্পোনেন্ট
        self.canvas = GridCanvas(self.root, rows=15, cols=20, cell_size=40, bg="white", highlightthickness=0)
        self.canvas.pack(padx=20, pady=20, expand=True)
        
        # অবজেক্ট তৈরি এবং ইভেন্ট বাইন্ডিং
        self.create_geometry_object(2, 2, "circle")
        self.create_geometry_object(5, 4, "square")

        self.canvas.tag_bind("draggable", "<ButtonPress-1>", self.on_start_drag)
        self.canvas.tag_bind("draggable", "<B1-Motion>", self.on_drag)
        self.canvas.tag_bind("draggable", "<ButtonRelease-1>", self.on_drop)

    def create_geometry_object(self, row, col, shape_type):
        size = self.canvas.cell_size
        # অফসেট বা মার্জিন যোগ করে পিক্সেল কোঅর্ডিনেট হিসাব
        x1 = self.canvas.offset_x + (col * size) + 5
        y1 = self.canvas.offset_y + (row * size) + 5
        x2 = x1 + size - 10
        y2 = y1 + size - 10
        
        if shape_type == "circle":
            self.canvas.create_oval(x1, y1, x2, y2, fill="#2196F3", outline="#0D47A1", width=2, tags="draggable")
        elif shape_type == "square":
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="#F44336", outline="#B71C1C", width=2, tags="draggable")
            
        self.canvas.tag_raise("grid_line")
        self.canvas.tag_raise("label")  # লেবেলগুলোকেও শেপের ওপরে রাখা হলো

    def on_start_drag(self, event):
        self.selected_item = self.canvas.find_closest(event.x, event.y)
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_drag(self, event):
        if not self.selected_item:
            return
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        self.canvas.move(self.selected_item, dx, dy)
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_drop(self, event):
        if not self.selected_item:
            return
            
        size = self.canvas.cell_size
        x1, y1, x2, y2 = self.canvas.coords(self.selected_item)
        
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        
        # ড্রপ করার পর রো/কলাম হিসাব করার সময় অফসেট বাদ দিয়ে হিসাব করতে হবে
        target_col = int((center_x - self.canvas.offset_x) // size)
        target_row = int((center_y - self.canvas.offset_y) // size)
        
        target_col = max(0, min(target_col, self.canvas.cols - 1))
        target_row = max(0, min(target_row, self.canvas.rows - 1))
        
        # নতুন স্ন্যাপিং পজিশন (অফসেট সহ)
        new_x1 = self.canvas.offset_x + (target_col * size) + 5
        new_y1 = self.canvas.offset_y + (target_row * size) + 5
        
        self.canvas.moveto(self.selected_item, new_x1, new_y1)
        self.canvas.tag_raise("grid_line")
        self.canvas.tag_raise("label")
        self.selected_item = None
if __name__ == "__main__":
    app_root = tk.Tk()
    engine = GeometryEngine(app_root)
    app_root.mainloop()

## কোডে কী কী পরিবর্তন করা হয়েছে (Key Changes):
১. self.offset_x এবং self.offset_y: ক্যানভাসের বামে এবং ওপরে 30 পিক্সেল করে খালি জায়গা রাখা হয়েছে যেখানে নম্বরগুলো লেখা থাকবে।
২. self.create_text(): গ্রিড লাইন লুপ চলার সময় টেক্সট ফাংশন ব্যবহার করে নির্দিষ্ট ঘরে কলাম নম্বর ও রো নম্বর বসিয়ে দেওয়া হয়েছে। টেক্সটের পজিশন করা হয়েছে অফসেট জোনের ঠিক মাঝখানে (offset / 2)।
৩. কোঅর্ডিনেট শিফটিং: অবজেক্ট তৈরি করা এবং ড্রপ করার পর স্ন্যাপ করার পুরো লজিকে self.canvas.offset_x এবং offset_y যোগ/বিয়োগ করা হয়েছে। এর ফলে মাউস দিয়ে অবজেক্ট স্লাইড করার সময় তা নম্বরগুলোর ওপরে চলে যাবে না, বরং একদম নিখুঁতভাবে গ্রিড বক্সের ভেতরেই থাকবে।
পরবর্তীতে কি আপনি এই রো এবং কলাম নম্বরগুলোকে অ্যালাইনমেন্ট পরিবর্তন করতে চান, নাকি এর সাথে কোনো অ্যাক্সিস বা স্কেল (যেমন: X-Axis, Y-Axis) যোগ করার পরিকল্পনা করছেন?

