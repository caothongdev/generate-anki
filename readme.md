# JSON to Anki Converter

Công cụ chuyển đổi file JSON sang Anki deck (.apkg)

## Cách sử dụng

1. **Tạo file JSON** bằng AI (ChatGPT, Claude, v.v.) với định dạng sau:

```json
{
  "deck_name": "Tên Deck của bạn",
  "tags": ["tag1", "tag2"],
  "cards": [
    {
      "front": "Câu hỏi/Mặt trước thẻ",
      "back": "Câu trả lời/Mặt sau thẻ"
    },
    {
      "front": "Câu hỏi 2",
      "back": "Câu trả lời 2",
      "tags": ["tag riêng cho thẻ này"]
    }
  ]
}
```

2. **Chạy chương trình**: `python main.py`
3. **Chọn file JSON** đã tạo
4. **Nhập tên deck** (tùy chọn)
5. **Click "Convert to Anki"** và lưu file .apkg
6. **Import vào Anki**

## Định dạng JSON chi tiết

### Các trường bắt buộc:
- `cards`: Mảng chứa các thẻ flashcard
  - Mỗi card phải có `front` và `back`

### Các trường tùy chọn:
- `deck_name`: Tên của deck (mặc định: "My Anki Deck")
- `tags`: Tags chung cho tất cả thẻ
- Trong mỗi card:
  - `tags`: Tags riêng cho thẻ đó (ghi đè tags chung)
  - Có thể dùng `question`/`answer` thay cho `front`/`back`

### Hỗ trợ HTML:
Bạn có thể dùng HTML trong `front` và `back`:
```json
{
  "front": "What is <b>Python</b>?",
  "back": "Python is a <i>programming language</i><br><br><b>Features:</b><ul><li>Easy to learn</li><li>Powerful</li></ul>"
}
```

## Ví dụ

Xem file `sample.json` để tham khảo định dạng

## Yêu cầu

```bash
pip install genanki
```

## Prompt gợi ý cho AI

Bạn có thể dùng prompt này với ChatGPT/Claude:

```
Tạo cho tôi 20 flashcards học tiếng Anh về chủ đề [TOPIC] theo định dạng JSON sau:
{
  "deck_name": "Tên deck",
  "tags": ["english"],
  "cards": [
    {
      "front": "Câu hỏi hoặc từ vựng",
      "back": "Câu trả lời với HTML format, bao gồm nghĩa, ví dụ, collocation"
    }
  ]
}

Mỗi thẻ cần có:
- Front: Câu hỏi hoặc từ cần học
- Back: Định nghĩa, nghĩa tiếng Việt, ví dụ sử dụng (dùng HTML để format đẹp)
```
