import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import genanki
import random
import json
import os
import shutil
from pathlib import Path

class AnkiGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("JSON to Anki Converter")
        self.root.geometry("700x600")
        
        # Title
        title = tk.Label(root, text="JSON to Anki Converter", 
                        font=("Arial", 20, "bold"))
        title.pack(pady=20)
        
        # Instructions
        instructions = tk.Label(root, 
                              text="Chọn file JSON hoặc paste JSON text để chuyển đổi sang Anki deck",
                              font=("Arial", 11),
                              wraplength=500)
        instructions.pack(pady=10)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, padx=20, fill=tk.BOTH)
        
        # Tab 1: File selection
        file_tab = tk.Frame(self.notebook)
        self.notebook.add(file_tab, text="📁 From File")
        
        tk.Label(file_tab, text="Chọn file JSON:", font=("Arial", 11)).pack(pady=20)
        
        file_frame = tk.Frame(file_tab)
        file_frame.pack(pady=10)
        
        self.file_path_var = tk.StringVar(value="Chưa chọn file...")
        file_label = tk.Label(file_frame, textvariable=self.file_path_var, 
                            font=("Arial", 10), fg="gray",
                            width=50, anchor="w")
        file_label.pack(side=tk.LEFT, padx=5)
        
        select_btn = tk.Button(file_frame, text="Browse", 
                             command=self.select_json_file,
                             font=("Arial", 10),
                             bg="#2196F3", fg="white",
                             padx=15, pady=5)
        select_btn.pack(side=tk.LEFT, padx=5)
        
        # Tab 2: Text input
        text_tab = tk.Frame(self.notebook)
        self.notebook.add(text_tab, text="📝 Paste JSON")
        
        tk.Label(text_tab, text="Paste JSON text:", font=("Arial", 11)).pack(pady=10)
        
        # JSON text area
        text_frame = tk.Frame(text_tab)
        text_frame.pack(pady=10, padx=20, fill=tk.BOTH)
        
        self.json_text = tk.Text(text_frame, height=10, font=("Consolas", 10), wrap=tk.WORD)
        self.json_text.pack(side=tk.LEFT, fill=tk.BOTH)
        
        scrollbar = tk.Scrollbar(text_frame, command=self.json_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.json_text.config(yscrollcommand=scrollbar.set)
        
        # Placeholder text
        placeholder = '''{
  "deck_name": "My Deck",
  "tags": ["learning"],
  "card_type": "basic",
  "cards": [
    {
      "front": "Question?",
      "back": "Answer",
      "image": null,
      "skip": false
    }
  ]
}'''
        self.json_text.insert(1.0, placeholder)
        self.json_text.bind("<FocusIn>", self.clear_placeholder)
        
        self.json_file_path = None
        self.is_placeholder = True
        
        # Deck name
        tk.Label(root, text="Tên Deck (tùy chọn):", font=("Arial", 12)).pack(pady=5)
        self.deck_name_entry = tk.Entry(root, width=50, font=("Arial", 11))
        self.deck_name_entry.pack(pady=5)
        
        # Card type selection
        tk.Label(root, text="Card Type:", font=("Arial", 12)).pack(pady=5)
        self.card_type_var = tk.StringVar(value="basic")
        type_frame = tk.Frame(root)
        type_frame.pack(pady=5)
        tk.Radiobutton(type_frame, text="Basic", variable=self.card_type_var, 
                      value="basic", font=("Arial", 10)).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(type_frame, text="Type Answer", variable=self.card_type_var, 
                      value="type", font=("Arial", 10)).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(type_frame, text="Cloze", variable=self.card_type_var, 
                      value="cloze", font=("Arial", 10)).pack(side=tk.LEFT, padx=10)
        
        # Advanced template checkbox
        self.use_advanced_template = tk.BooleanVar(value=False)
        tk.Checkbutton(root, text="⭐ Use Advanced Template (English-English, Professional Styling)", 
                      variable=self.use_advanced_template, 
                      font=("Arial", 10, "bold"),
                      fg="#2196F3").pack(pady=5)
        
        # Buttons frame
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=20)
        
        # Generate Prompt button
        prompt_btn = tk.Button(btn_frame, text="📋 Generate Prompt", 
                              font=("Arial", 11),
                              bg="#2196F3", fg="white",
                              command=self.generate_prompt,
                              padx=20, pady=8)
        prompt_btn.pack(side=tk.LEFT, padx=10)
        
        # Convert button
        convert_btn = tk.Button(btn_frame, text="Review & Convert", 
                              font=("Arial", 14, "bold"),
                              bg="#4CAF50", fg="white",
                              command=self.open_review_window,
                              padx=30, pady=10)
        convert_btn.pack(side=tk.LEFT, padx=10)
        
        # Progress label
        self.status_label = tk.Label(root, text="", font=("Arial", 10), 
                                    fg="blue")
        self.status_label.pack(pady=5)
        
        self.json_file_path = None
    
    def clear_placeholder(self, event):
        """Xóa placeholder khi focus vào text area"""
        if self.is_placeholder:
            self.json_text.delete(1.0, tk.END)
            self.is_placeholder = False
    
    def select_json_file(self):
        """Chọn file JSON"""
        file_path = filedialog.askopenfilename(
            title="Select JSON File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            self.json_file_path = file_path
            # Hiển thị tên file
            filename = os.path.basename(file_path)
            self.file_path_var.set(filename)
    
    def generate_prompt(self):
        """Tạo prompt cho AI để generate JSON"""
        # Tạo dialog để nhập topic
        prompt_window = tk.Toplevel(self.root)
        prompt_window.title("Generate AI Prompt")
        prompt_window.geometry("700x600")
        
        tk.Label(prompt_window, text="Tạo Prompt cho AI", 
                font=("Arial", 16, "bold")).pack(pady=15)
        
        # Topic input
        tk.Label(prompt_window, text="Nhập chủ đề/topic:", 
                font=("Arial", 11)).pack(pady=5)
        topic_entry = tk.Entry(prompt_window, width=60, font=("Arial", 11))
        topic_entry.pack(pady=5)
        topic_entry.insert(0, "English vocabulary for programming")
        
        # Number of cards
        tk.Label(prompt_window, text="Số lượng cards:", 
                font=("Arial", 11)).pack(pady=5)
        num_entry = tk.Entry(prompt_window, width=20, font=("Arial", 11))
        num_entry.pack(pady=5)
        num_entry.insert(0, "20")
        
        # Generated prompt display
        tk.Label(prompt_window, text="Prompt (copy và paste vào ChatGPT/Claude):", 
                font=("Arial", 11, "bold")).pack(pady=10)
        
        prompt_text = tk.Text(prompt_window, width=80, height=20, 
                             font=("Arial", 10), wrap=tk.WORD)
        prompt_text.pack(padx=20, pady=10)
        
        def update_prompt():
            topic = topic_entry.get().strip() or "[TOPIC]"
            num = num_entry.get().strip() or "20"
            card_type = self.card_type_var.get()
            
            if card_type == "basic":
                example_cards = '''[
    {
      "front": "What does 'async' mean in programming?",
      "back": "<b>async</b><br><br>Nghĩa: bất đồng bộ<br>Giải thích: Allows code to run without blocking<br>Example: async function fetchData() {...}",
      "image": null,
      "skip": false
    }
  ]'''
            elif card_type == "type":
                example_cards = '''[
    {
      "front": "The program needs to [...] data from the API asynchronously.",
      "back": "fetch",
      "image": null,
      "skip": false
    }
  ]'''
            else:  # cloze
                example_cards = '''[
    {
      "front": "{{c1::async}} function allows code to run without blocking the main thread",
      "back": "",
      "image": null,
      "skip": false
    }
  ]'''
            
            prompt = f'''Tạo cho tôi {num} flashcards học về "{topic}" theo định dạng JSON sau:

{{
  "deck_name": "{topic}",
  "tags": ["learning"],
  "card_type": "{card_type}",
  "cards": {example_cards}
}}

Yêu cầu:
- Tạo CHÍNH XÁC {num} cards
- Card type: {card_type}
'''
            
            if card_type == "basic":
                prompt += '''- Front: Câu hỏi hoặc từ vựng cần học
- Back: Câu trả lời chi tiết với HTML format (<b>, <br>, <ul>, <li>)
  * Định nghĩa/nghĩa tiếng Việt
  * Giải thích rõ ràng
  * Ví dụ cụ thể
  * Collocation (nếu có)
'''
            elif card_type == "type":
                prompt += '''- Front: Câu có chỗ trống [...] để điền từ
- Back: Từ/cụm từ chính xác cần điền (KHÔNG có HTML, CHỈ text thuần)
- Câu phải có ngữ cảnh rõ ràng để đoán được đáp án
- Đáp án ngắn gọn (1-3 từ)
'''
            else:  # cloze
                prompt += '''- Front: Câu có {{c1::answer}} để ẩn phần cần học
- Back: Để trống "" (Anki tự động xử lý)
- Dùng {{c1::text}} cho phần cần ẩn
- Có thể dùng {{c2::text}}, {{c3::text}} cho nhiều chỗ trống
'''
            
            prompt += '''
- image và skip luôn để null và false
- Nội dung phải chất lượng, hữu ích
- Trả về ĐÚNG format JSON, không thêm text nào khác
'''
            
            prompt_text.delete(1.0, tk.END)
            prompt_text.insert(1.0, prompt)
        
        # Update button
        tk.Button(prompt_window, text="Generate Prompt", 
                 command=update_prompt,
                 font=("Arial", 11, "bold"),
                 bg="#4CAF50", fg="white",
                 padx=20, pady=8).pack(pady=10)
        
        # Copy button
        def copy_to_clipboard():
            prompt_window.clipboard_clear()
            prompt_window.clipboard_append(prompt_text.get(1.0, tk.END))
            messagebox.showinfo("Copied", "Prompt đã copy vào clipboard!")
        
        tk.Button(prompt_window, text="📋 Copy to Clipboard", 
                 command=copy_to_clipboard,
                 font=("Arial", 11),
                 bg="#2196F3", fg="white",
                 padx=20, pady=8).pack(pady=5)
        
        # Generate initial prompt
        update_prompt()
    
    def open_review_window(self):
        """Mở cửa sổ review và thêm ảnh"""
        try:
            # Kiểm tra tab nào đang active
            current_tab = self.notebook.index(self.notebook.select())
            
            if current_tab == 0:  # File tab
                if not self.json_file_path:
                    messagebox.showwarning("Lỗi", "Vui lòng chọn file JSON!")
                    return
                
                # Đọc file JSON
                with open(self.json_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
            else:  # Text tab
                json_text = self.json_text.get(1.0, tk.END).strip()
                
                if not json_text or self.is_placeholder:
                    messagebox.showwarning("Lỗi", "Vui lòng paste JSON text!")
                    return
                
                # Parse JSON text
                data = json.loads(json_text)
            
            # Lấy tên deck
            deck_name = self.deck_name_entry.get().strip()
            if not deck_name:
                deck_name = data.get('deck_name', 'My Anki Deck')
            
            # Lấy card type
            card_type = self.card_type_var.get()
            # Cập nhật card_type vào data nếu chưa có
            if 'card_type' not in data:
                data['card_type'] = card_type
            
            # Thêm advanced template flag
            data['use_advanced_template'] = self.use_advanced_template.get()
            
            # Mở cửa sổ review
            ReviewWindow(self.root, data, deck_name, self.json_file_path)
            
        except json.JSONDecodeError as e:
            messagebox.showerror("Lỗi", f"JSON không hợp lệ!\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đọc dữ liệu:\n{str(e)}")

    def create_deck_from_json(self, data, deck_name, media_files=None):
        """Tạo Anki deck từ dữ liệu JSON"""
        card_type = data.get('card_type', 'basic')
        
        # Tạo model tùy theo card type
        model_id = random.randrange(1 << 30, 1 << 31)
        
        if card_type == 'cloze':
            # Cloze model
            model = genanki.Model(
                model_id,
                'Cloze Model with Image',
                model_type=genanki.Model.CLOZE,
                fields=[
                    {'name': 'Text'},
                    {'name': 'Image'},
                    {'name': 'Extra'},
                ],
                templates=[
                    {
                        'name': 'Cloze',
                        'qfmt': '{{cloze:Text}}<br>{{Image}}',
                        'afmt': '{{cloze:Text}}<br>{{Image}}<br><br>{{Extra}}',
                    },
                ])
        elif card_type == 'type':
            # Type Answer model
            model = genanki.Model(
                model_id,
                'Type Answer Model with Image',
                fields=[
                    {'name': 'Front'},
                    {'name': 'Back'},
                    {'name': 'Image'},
                ],
                templates=[
                    {
                        'name': 'Card 1',
                        'qfmt': '{{Front}}<br>{{Image}}<br><br>{{type:Back}}',
                        'afmt': '{{Front}}<br>{{Image}}<hr id="answer">{{Back}}',
                    },
                ])
        else:
            # Basic model (default)
            model = genanki.Model(
                model_id,
                'Flashcard Model with Image',
                fields=[
                    {'name': 'Front'},
                    {'name': 'Back'},
                    {'name': 'Image'},
                ],
                templates=[
                    {
                        'name': 'Card 1',
                        'qfmt': '{{Front}}<br>{{Image}}',
                        'afmt': '{{FrontSide}}<hr id="answer">{{Back}}',
                    },
                ])
        
        # Tạo deck
        deck_id = random.randrange(1 << 30, 1 << 31)
        deck = genanki.Deck(deck_id, deck_name)
        
        # Lấy danh sách cards từ JSON
        cards = data.get('cards', [])
        tags = data.get('tags', [])
        
        # Thêm các note vào deck
        for card in cards:
            # Skip nếu card bị đánh dấu skip
            if card.get('skip', False):
                continue
                
            front = card.get('front', card.get('question', ''))
            back = card.get('back', card.get('answer', ''))
            
            # Xử lý ảnh
            image_html = ''
            if card.get('image'):
                image_filename = os.path.basename(card['image'])
                image_html = f'<img src="{image_filename}">'
            
            # Lấy tags cho card này hoặc dùng tags chung
            card_tags = card.get('tags', tags)
            if isinstance(card_tags, str):
                card_tags = [card_tags]
            
            # Tạo note tùy theo card type
            if card_type == 'cloze':
                note = genanki.Note(
                    model=model,
                    fields=[str(front), image_html, str(back)],
                    tags=card_tags
                )
            else:
                note = genanki.Note(
                    model=model,
                    fields=[str(front), str(back), image_html],
                    tags=card_tags
                )
            deck.add_note(note)
        
        # Tạo package với media files
        if media_files:
            return genanki.Package(deck, media_files=media_files)
        else:
            return genanki.Package(deck)


class ReviewWindow:
    """Cửa sổ review và thêm ảnh cho cards"""
    def __init__(self, parent, data, deck_name, json_path):
        self.window = tk.Toplevel(parent)
        self.window.title("Review Cards")
        self.window.geometry("800x600")
        
        self.data = data
        self.deck_name = deck_name
        self.json_path = json_path
        self.cards = data.get('cards', [])
        self.current_index = 0
        self.media_files = []
        
        # Tạo UI
        self.create_ui()
        self.show_card()
    
    def create_ui(self):
        """Tạo giao diện"""
        # Header
        header = tk.Frame(self.window, bg="#2196F3", height=60)
        header.pack(fill=tk.X)
        
        tk.Label(header, text=f"Review Deck: {self.deck_name}", 
                font=("Arial", 16, "bold"), bg="#2196F3", fg="white").pack(pady=15)
        
        # Card counter
        self.counter_label = tk.Label(self.window, text="", 
                                     font=("Arial", 11), fg="gray")
        self.counter_label.pack(pady=10)
        
        # Card content frame
        content_frame = tk.Frame(self.window, relief=tk.RIDGE, borderwidth=2)
        content_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # Front
        tk.Label(content_frame, text="FRONT:", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=10, pady=(10,5))
        self.front_text = tk.Text(content_frame, height=4, font=("Arial", 11), wrap=tk.WORD)
        self.front_text.pack(padx=10, pady=5, fill=tk.X)
        
        # Back
        tk.Label(content_frame, text="BACK:", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=10, pady=(10,5))
        self.back_text = tk.Text(content_frame, height=4, font=("Arial", 11), wrap=tk.WORD)
        self.back_text.pack(padx=10, pady=5, fill=tk.X)
        
        # Image section
        image_frame = tk.Frame(content_frame)
        image_frame.pack(pady=10, padx=10, fill=tk.X)
        
        tk.Label(image_frame, text="IMAGE:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        self.image_path_var = tk.StringVar(value="Không có ảnh")
        tk.Label(image_frame, textvariable=self.image_path_var, 
                font=("Arial", 9), fg="gray").pack(anchor=tk.W, pady=5)
        
        img_btn_frame = tk.Frame(image_frame)
        img_btn_frame.pack(anchor=tk.W)
        
        tk.Button(img_btn_frame, text="Thêm ảnh", 
                 command=self.add_image).pack(side=tk.LEFT, padx=5)
        tk.Button(img_btn_frame, text="Xóa ảnh", 
                 command=self.remove_image).pack(side=tk.LEFT, padx=5)
        
        # Navigation buttons
        nav_frame = tk.Frame(self.window)
        nav_frame.pack(pady=20)
        
        tk.Button(nav_frame, text="⬅ Previous", 
                 command=self.previous_card,
                 font=("Arial", 11), width=12).pack(side=tk.LEFT, padx=5)
        
        tk.Button(nav_frame, text="Skip Card", 
                 command=self.skip_card,
                 font=("Arial", 11), bg="#FF9800", fg="white", width=12).pack(side=tk.LEFT, padx=5)
        
        tk.Button(nav_frame, text="Next ➡", 
                 command=self.next_card,
                 font=("Arial", 11), width=12).pack(side=tk.LEFT, padx=5)
        
        # Bottom buttons
        bottom_frame = tk.Frame(self.window)
        bottom_frame.pack(pady=10)
        
        tk.Button(bottom_frame, text="Export to Anki", 
                 command=self.export_deck,
                 font=("Arial", 12, "bold"), bg="#4CAF50", fg="white",
                 padx=20, pady=5).pack(side=tk.LEFT, padx=10)
        
        tk.Button(bottom_frame, text="Cancel", 
                 command=self.window.destroy,
                 font=("Arial", 12), padx=20, pady=5).pack(side=tk.LEFT, padx=10)
    
    def show_card(self):
        """Hiển thị card hiện tại"""
        if not self.cards:
            messagebox.showwarning("Lỗi", "Không có cards nào!")
            self.window.destroy()
            return
        
        card = self.cards[self.current_index]
        
        # Update counter
        total = len(self.cards)
        skipped = sum(1 for c in self.cards if c.get('skip', False))
        self.counter_label.config(text=f"Card {self.current_index + 1}/{total} | Skipped: {skipped}")
        
        # Show content
        self.front_text.delete(1.0, tk.END)
        self.front_text.insert(1.0, card.get('front', card.get('question', '')))
        
        self.back_text.delete(1.0, tk.END)
        self.back_text.insert(1.0, card.get('back', card.get('answer', '')))
        
        # Show image status
        if card.get('skip', False):
            self.image_path_var.set("⚠ Card này sẽ bị bỏ qua")
        elif card.get('image'):
            self.image_path_var.set(f"✓ {os.path.basename(card['image'])}")
        else:
            self.image_path_var.set("Không có ảnh")
    
    def add_image(self):
        """Thêm ảnh cho card"""
        # Đảm bảo window ở phía trước
        self.window.attributes('-topmost', True)
        self.window.attributes('-topmost', False)
        
        file_path = filedialog.askopenfilename(
            parent=self.window,
            title="Chọn ảnh",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.cards[self.current_index]['image'] = file_path
            self.cards[self.current_index]['skip'] = False  # Bỏ skip nếu có ảnh
            
            # Thêm vào media files
            if file_path not in self.media_files:
                self.media_files.append(file_path)
            
            self.show_card()
        
        # Focus lại window
        self.window.focus_force()
    
    def remove_image(self):
        """Xóa ảnh khỏi card"""
        if self.cards[self.current_index].get('image'):
            image_path = self.cards[self.current_index]['image']
            self.cards[self.current_index]['image'] = None
            
            # Xóa khỏi media files nếu không card nào dùng
            if not any(c.get('image') == image_path for c in self.cards):
                if image_path in self.media_files:
                    self.media_files.remove(image_path)
            
            self.show_card()
    
    def skip_card(self):
        """Bỏ qua card này"""
        current_skip = self.cards[self.current_index].get('skip', False)
        self.cards[self.current_index]['skip'] = not current_skip
        self.show_card()
    
    def previous_card(self):
        """Card trước"""
        if self.current_index > 0:
            self.current_index -= 1
            self.show_card()
    
    def next_card(self):
        """Card tiếp theo"""
        if self.current_index < len(self.cards) - 1:
            self.current_index += 1
            self.show_card()
    
    def export_deck(self):
        """Export sang Anki"""
        # Đếm cards không bị skip
        active_cards = [c for c in self.cards if not c.get('skip', False)]
        
        if not active_cards:
            messagebox.showwarning("Lỗi", "Tất cả cards đã bị skip!")
            return
        
        confirm = messagebox.askyesno(
            "Xác nhận", 
            f"Xuất {len(active_cards)}/{len(self.cards)} cards?\n"
            f"({len(self.cards) - len(active_cards)} cards bị skip)"
        )
        
        if not confirm:
            return
        
        try:
            # Tạo deck trực tiếp
            deck = self.create_anki_deck(self.data, self.deck_name, self.media_files)
            
            # Lưu file
            save_path = filedialog.asksaveasfilename(
                parent=self.window,
                defaultextension=".apkg",
                filetypes=[("Anki Deck", "*.apkg")],
                initialfile=f"{self.deck_name.replace(' ', '_')}.apkg"
            )
            
            if save_path:
                deck.write_to_file(save_path)
                messagebox.showinfo(
                    "Thành công", 
                    f"Đã xuất {len(active_cards)} cards!\n"
                    f"Media files: {len(self.media_files)}\n"
                    f"Lưu tại: {save_path}"
                )
                self.window.destroy()
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xuất:\n{str(e)}")
    
    def create_anki_deck(self, data, deck_name, media_files=None):
        """Tạo Anki deck từ dữ liệu JSON (static method)"""
        card_type = data.get('card_type', 'basic')
        use_advanced = data.get('use_advanced_template', False)
        
        # Tạo model tùy theo card type
        model_id = random.randrange(1 << 30, 1 << 31)
        
        if use_advanced and card_type == 'type':
            # Advanced Professional Template (Type + Cloze)
            model = genanki.Model(
                model_id,
                'Advanced English Learning Model',
                fields=[
                    {'name': 'CardNo'},
                    {'name': 'Image'},
                    {'name': 'Suggestion'},
                    {'name': 'Explanation'},
                    {'name': 'ShortMeaning'},
                    {'name': 'Transcription'},
                    {'name': 'Keyword'},
                    {'name': 'FullMeaning'},
                ],
                templates=[
                    {
                        'name': 'Type & Cloze',
                        'qfmt': '''<div style='font-family: Arial; font-size: 14px;color:blue;text-align: left;'>Card No.: {{CardNo}}</div><br>
<div style='text-align: center;'>{{Image}}</div>

<div style='font-family: Arial; font-size: 26px;color:red;text-align: left;'>{{Suggestion}}</div><br>

<div style='font-family: Arial; font-size: 20px;text-align: left;'>{{Explanation}}</div><br>
<div style='font-family: Arial; font-size: 20px;color:blue;text-align: left;'>{{ShortMeaning}}</div>

<div style='font-family: Arial; font-size: 22px;text-align: left;'>{{type:Keyword}}''',
                        'afmt': '''<div style='font-family: Arial; font-size: 14px;color:blue;text-align: left;'>Card No.: {{CardNo}}</div>

<div style='font-family: Arial; font-size: 24px;text-align: center;'>{{type:Keyword}}</div>

<div style='font-family: Arial; font-size: 24px;color:blue;text-align:center;'>{{Transcription}}</div>

<div style='font-family: Arial; font-size: 22px;text-align: left;'>{{Explanation}}</div>

<div style='text-align: center;'>{{Image}}</div>

<div style='font-family: Arial; font-size: 22px;color:black;text-align:center;'>{{Keyword}}</div>
<div style='font-family: Arial; font-size: 20px;color:black;text-align:center;'>{{Transcription}}</div>
<div style='font-family: Arial; font-size: 22px;color:blue;text-align:center;'>{{ShortMeaning}}</div><br>

<div style='font-family: Arial; font-size: 20px;text-align: left;'>{{FullMeaning}}</div>''',
                    },
                ],
                css='''.card {
 font-family: arial; line-height: 1.5em;
 font-size: 20px;
 color: black;
 text-align: center;
 background-color: white;
}
.cloze {
 font-weight: bold;
 color: blue;
}

#typeans {
 padding-top: 0.5em;
 text-align: center;
 max-width: 300px;
}
input#typeans {
 border-radius: 19px
}

div span {
 max-width: 900px;
 display: inline-block;
 text-align:left;
}

.card {color: black; background-color: #f3f3f3;}
#typeans span {background-color: #f3f3f3;}
.typeBad {color: #dc322f;font-weight:bold;font-size: 23px;}
.typeMissed, .typePass {color: #268bd2;font-weight:bold;font-size: 23px;}
.typeGood{color: #2ed85a;font-weight:bold;}'''
            )
        elif card_type == 'cloze':
            # Cloze model
            model = genanki.Model(
                model_id,
                'Cloze Model with Image',
                model_type=genanki.Model.CLOZE,
                fields=[
                    {'name': 'Text'},
                    {'name': 'Image'},
                    {'name': 'Extra'},
                ],
                templates=[
                    {
                        'name': 'Cloze',
                        'qfmt': '{{cloze:Text}}<br>{{Image}}',
                        'afmt': '{{cloze:Text}}<br>{{Image}}<br><br>{{Extra}}',
                    },
                ])
        elif card_type == 'type':
            # Type Answer model
            model = genanki.Model(
                model_id,
                'Type Answer Model with Image',
                fields=[
                    {'name': 'Front'},
                    {'name': 'Back'},
                    {'name': 'Image'},
                ],
                templates=[
                    {
                        'name': 'Card 1',
                        'qfmt': '{{Front}}<br>{{Image}}<br><br>{{type:Back}}',
                        'afmt': '{{Front}}<br>{{Image}}<hr id="answer">{{Back}}',
                    },
                ])
        else:
            # Basic model (default)
            model = genanki.Model(
                model_id,
                'Flashcard Model with Image',
                fields=[
                    {'name': 'Front'},
                    {'name': 'Back'},
                    {'name': 'Image'},
                ],
                templates=[
                    {
                        'name': 'Card 1',
                        'qfmt': '{{Front}}<br>{{Image}}',
                        'afmt': '{{FrontSide}}<hr id="answer">{{Back}}',
                    },
                ])
        
        # Tạo deck
        deck_id = random.randrange(1 << 30, 1 << 31)
        deck = genanki.Deck(deck_id, deck_name)
        
        # Lấy danh sách cards từ JSON
        cards = data.get('cards', [])
        tags = data.get('tags', [])
        
        # Thêm các note vào deck
        for card in cards:
            # Skip nếu card bị đánh dấu skip
            if card.get('skip', False):
                continue
            
            # Xử lý ảnh
            image_html = ''
            if card.get('image'):
                image_filename = os.path.basename(card['image'])
                image_html = f'<img src="{image_filename}">'
            
            # Lấy tags cho card này hoặc dùng tags chung
            card_tags = card.get('tags', tags)
            if isinstance(card_tags, str):
                card_tags = [card_tags]
            
            # Tạo note tùy theo template
            if use_advanced and card_type == 'type':
                # Advanced template fields
                note = genanki.Note(
                    model=model,
                    fields=[
                        str(card.get('card_no', '')),
                        image_html,
                        str(card.get('suggestion', '')),
                        str(card.get('explanation', card.get('front', ''))),
                        str(card.get('short_meaning', '')),
                        str(card.get('transcription', '')),
                        str(card.get('keyword', card.get('back', ''))),
                        str(card.get('full_meaning', '')),
                    ],
                    tags=card_tags
                )
            elif card_type == 'cloze':
                front = card.get('front', card.get('question', ''))
                back = card.get('back', card.get('answer', ''))
                note = genanki.Note(
                    model=model,
                    fields=[str(front), image_html, str(back)],
                    tags=card_tags
                )
            else:
                front = card.get('front', card.get('question', ''))
                back = card.get('back', card.get('answer', ''))
                note = genanki.Note(
                    model=model,
                    fields=[str(front), str(back), image_html],
                    tags=card_tags
                )
            deck.add_note(note)
        
        # Tạo package với media files
        if media_files:
            return genanki.Package(deck, media_files=media_files)
        else:
            return genanki.Package(deck)

if __name__ == "__main__":
    root = tk.Tk()
    app = AnkiGeneratorApp(root)
    root.mainloop()
