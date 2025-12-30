# JSON to Anki Converter

Công cụ chuyển đổi file JSON sang Anki deck (.apkg) với tính năng review và thêm ảnh

## Tính năng

✅ **Generate Prompt cho AI** - Tạo prompt tự động dựa trên chủ đề  
✅ Import file JSON (tạo bằng AI)  
✅ Review từng thẻ trước khi xuất  
✅ Thêm ảnh cho từng thẻ  
✅ Skip thẻ không cần thiết  
✅ **3 loại Card**: Basic, Type Answer (active recall), Cloze  
✅ Hỗ trợ HTML formatting  
✅ Xuất file .apkg cho Anki  

## Cách sử dụng

### Bước 1: Generate Prompt
1. Chạy: `python main.py`
2. Chọn **Card Type** (Basic/Type Answer/Cloze)
3. Click **"📋 Generate Prompt"**
4. Nhập chủ đề và số lượng cards
5. Copy prompt → Paste vào ChatGPT/Claude

### Bước 2: Tạo JSON với AI
- Paste prompt vào AI (ChatGPT, Claude, v.v.)
- AI sẽ tạo file JSON theo đúng format
- Lưu thành file `.json`

### Bước 3: Review & Convert
1. Click **"Browse"** → Chọn file JSON
2. Nhập tên deck (tùy chọn)
3. Click **"Review & Convert"**
4. Trong Review window:
   - Xem từng thẻ
   - Thêm/xóa ảnh
   - Skip thẻ không muốn
   - Previous/Next để điều hướng
5. **Export to Anki** → Import vào Anki

## Card Types

### 1. **Basic** (Mặc định)
Thẻ hai mặt cơ bản: Front (câu hỏi) → Back (câu trả lời)

```json
{
  "card_type": "basic",
  "cards": [
    {
      "front": "What is Python?",
      "back": "<b>Python</b><br>A high-level programming language"
    }
  ]
}
```

### 2. **Type Answer** (Active Recall) ⭐
Yêu cầu gõ đáp án → Tốt cho ghi nhớ

```json
{
  "card_type": "type",
  "cards": [
    {
      "front": "We need to [...] the code before deployment.",
      "back": "debug"
    }
  ]
}
```

### 3. **Cloze** (Fill in the blank)
Ẩn từ/cụm từ trong câu

```json
{
  "card_type": "cloze",
  "cards": [
    {
      "front": "{{c1::Python}} is a programming language",
      "back": ""
    }
  ]
}
```

## Định dạng JSON

```json
{
  "deck_name": "Tên Deck",
  "tags": ["tag1", "tag2"],
  "card_type": "basic",
  "cards": [
    {
      "front": "Câu hỏi",
      "back": "Câu trả lời",
      "image": null,
      "skip": false
    }
  ]
}
```

### Các trường:

#### Bắt buộc:
- `cards`: Mảng chứa các thẻ
  - `front`: Mặt trước thẻ
  - `back`: Mặt sau thẻ (với cloze để "")

#### Tùy chọn:
- `deck_name`: Tên deck (mặc định: "My Anki Deck")
- `card_type`: "basic", "type", hoặc "cloze" (mặc định: "basic")
- `tags`: Tags chung cho tất cả thẻ
- Trong mỗi card:
  - `image`: null hoặc đường dẫn (thêm trong Review)
  - `skip`: true/false (mặc định: false)
  - `tags`: Tags riêng cho thẻ

## Hỗ trợ HTML

**Basic** và **Type Answer**: Có thể dùng HTML
```json
{
  "back": "<b>Python</b><br><br><ul><li>Easy</li><li>Powerful</li></ul>"
}
```

**Cloze**: Dùng {{c1::text}}, {{c2::text}}
```json
{
  "front": "{{c1::Python}} is {{c2::easy}} to learn"
}
```

## Review Window

- **Xem nội dung**: Front/Back của từng thẻ
- **Thêm ảnh**: Click "Thêm ảnh" → chọn file
- **Xóa ảnh**: Click "Xóa ảnh"
- **Skip thẻ**: Click "Skip Card" (thẻ sẽ không xuất)
- **Điều hướng**: Previous/Next
- **Export**: Click "Export to Anki"

## Yêu cầu

```bash
pip install genanki
```

## Ví dụ mẫu

- [sample.json](sample.json) - Basic cards
- [sample_type.json](sample_type.json) - Type Answer cards
- [sample_cloze.json](sample_cloze.json) - Cloze cards

## Prompt Templates (trong app)

App tự động tạo prompt theo:
- **Chủ đề** của bạn
- **Số lượng** cards
- **Card type** đã chọn

Ví dụ prompt cho **Type Answer**:
```
Tạo cho tôi 20 flashcards học về "Programming vocabulary" theo định dạng JSON...

Yêu cầu:
- Card type: type
- Front: Câu có chỗ trống [...] để điền từ
- Back: Từ/cụm từ chính xác (CHỈ text thuần, KHÔNG HTML)
- Câu phải có ngữ cảnh rõ ràng
...
```

## Tips

💡 **Type Answer** tốt nhất cho active recall  
💡 **Cloze** tốt cho học trong ngữ cảnh  
💡 **Basic** linh hoạt nhất, có thể format phong phú  
💡 Thêm ảnh vào thẻ khó để dễ nhớ hơn  
💡 Skip thẻ quá dễ để tối ưu thời gian học  

## Lưu ý

- Ảnh sẽ được nhúng vào file .apkg
- Thẻ bị skip sẽ KHÔNG xuất vào Anki
- Type Answer: đáp án phải ngắn gọn (1-3 từ)
- Cloze: Back để trống "", Anki tự xử lý
- Hỗ trợ ảnh: png, jpg, jpeg, gif, bmp
