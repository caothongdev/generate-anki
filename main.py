import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import genanki
import random
import json

class AnkiGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("JSON to Anki Converter")
        self.root.geometry("600x400")
        
        # Title
        title = tk.Label(root, text="JSON to Anki Converter", 
                        font=("Arial", 20, "bold"))
        title.pack(pady=20)
        
        # Instructions
        instructions = tk.Label(root, 
                              text="Chọn file JSON chứa flashcards để chuyển đổi sang Anki deck",
                              font=("Arial", 11),
                              wraplength=500)
        instructions.pack(pady=10)
        
        # JSON file selection
        file_frame = tk.Frame(root)
        file_frame.pack(pady=20)
        
        tk.Label(file_frame, text="JSON File:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        self.file_path_var = tk.StringVar(value="Chưa chọn file...")
        file_label = tk.Label(file_frame, textvariable=self.file_path_var, 
                            font=("Arial", 10), fg="gray",
                            width=40, anchor="w")
        file_label.pack(side=tk.LEFT, padx=5)
        
        select_btn = tk.Button(file_frame, text="Browse", 
                             command=self.select_json_file,
                             font=("Arial", 10))
        select_btn.pack(side=tk.LEFT, padx=5)
        
        # Deck name
        tk.Label(root, text="Tên Deck (tùy chọn):", font=("Arial", 12)).pack(pady=5)
        self.deck_name_entry = tk.Entry(root, width=50, font=("Arial", 11))
        self.deck_name_entry.pack(pady=5)
        
        # Convert button
        convert_btn = tk.Button(root, text="Convert to Anki", 
                              font=("Arial", 14, "bold"),
                              bg="#4CAF50", fg="white",
                              command=self.convert_to_anki,
                              padx=30, pady=10)
        convert_btn.pack(pady=30)
        
        # Progress label
        self.status_label = tk.Label(root, text="", font=("Arial", 10), 
                                    fg="blue")
        self.status_label.pack(pady=5)
        
        self.json_file_path = None
    
    def select_json_file(self):
        """Chọn file JSON"""
        file_path = filedialog.askopenfilename(
            title="Select JSON File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            self.json_file_path = file_path
            # Hiển thị tên file
            import os
            filename = os.path.basename(file_path)
            self.file_path_var.set(filename)
    
    def convert_to_anki(self):
        """Chuyển đổi JSON sang Anki deck"""
        if not self.json_file_path:
            messagebox.showwarning("Lỗi", "Vui lòng chọn file JSON!")
            return
        
        self.status_label.config(text="Đang chuyển đổi... Vui lòng đợi.")
        self.root.update()
        
        try:
            # Đọc file JSON
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Lấy tên deck
            deck_name = self.deck_name_entry.get().strip()
            if not deck_name:
                deck_name = data.get('deck_name', 'My Anki Deck')
            
            # Tạo deck
            deck = self.create_deck_from_json(data, deck_name)
            
            # Lưu file
            save_path = filedialog.asksaveasfilename(
                defaultextension=".apkg",
                filetypes=[("Anki Deck", "*.apkg")],
                initialfile=f"{deck_name.replace(' ', '_')}.apkg"
            )
            
            if save_path:
                deck.write_to_file(save_path)
                self.status_label.config(text="")
                messagebox.showinfo("Thành công", 
                                   f"Đã tạo deck thành công!\n"
                                   f"Số thẻ: {len(data.get('cards', []))}\n"
                                   f"Lưu tại: {save_path}")
            else:
                self.status_label.config(text="")
                
        except json.JSONDecodeError:
            self.status_label.config(text="")
            messagebox.showerror("Lỗi", "File JSON không hợp lệ!")
        except Exception as e:
            self.status_label.config(text="")
            messagebox.showerror("Lỗi", f"Không thể chuyển đổi:\n{str(e)}")
    
    def create_deck_from_json(self, data, deck_name):
        """Tạo Anki deck từ dữ liệu JSON"""
        # Tạo model
        model_id = random.randrange(1 << 30, 1 << 31)
        model = genanki.Model(
            model_id,
            'Flashcard Model',
            fields=[
                {'name': 'Front'},
                {'name': 'Back'},
            ],
            templates=[
                {
                    'name': 'Card 1',
                    'qfmt': '{{Front}}',
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
            front = card.get('front', card.get('question', ''))
            back = card.get('back', card.get('answer', ''))
            
            # Lấy tags cho card này hoặc dùng tags chung
            card_tags = card.get('tags', tags)
            if isinstance(card_tags, str):
                card_tags = [card_tags]
            
            note = genanki.Note(
                model=model,
                fields=[str(front), str(back)],
                tags=card_tags
            )
            deck.add_note(note)
        
        return genanki.Package(deck)

if __name__ == "__main__":
    root = tk.Tk()
    app = AnkiGeneratorApp(root)
    root.mainloop()
