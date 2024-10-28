import whisper
from tkinter import *
from tkinter import filedialog
from tkinter import ttk  # Import ttk cho Progressbar
import threading
from translate import Translator  # Sử dụng thư viện translate

# Hàm chuyển video thành văn bản sử dụng Whisper
def transcribe_audio_with_whisper(video_file, progress):
    model = whisper.load_model("base")
    result = model.transcribe(video_file, verbose=True)
    segments = result['segments']
    total_segments = len(segments)

    sentences = []
    # Sau mỗi segment, cập nhật tiến độ và gom các đoạn thành từng câu
    for i, segment in enumerate(segments):
        text = segment['text'].strip()
        sentences.append(text)  # Lưu từng câu vào danh sách
        progress['value'] += (50 / total_segments)  # Giả sử 50% là cho việc nhận diện giọng nói
        progress.update_idletasks()
    
    return sentences

# Hàm dịch từng câu sang tiếng Việt
def translate_text_to_vietnamese(sentences, progress):
    translator = Translator(to_lang="vi")
    translated_sentences = []

    total_sentences = len(sentences)
    # Dịch từng câu và lưu lại
    for i, sentence in enumerate(sentences):
        translated_sentence = translator.translate(sentence)
        translated_sentences.append(translated_sentence)
        
        # Cập nhật tiến độ dịch văn bản
        progress['value'] += (50 / total_sentences)  # Giả sử 50% là cho việc dịch toàn bộ văn bản
        progress.update_idletasks()
    
    return translated_sentences

# Tạo file văn bản từ nội dung đã dịch theo từng dòng
def create_text_file(translated_sentences, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        for sentence in translated_sentences:
            f.write(sentence + "\n")  # Ghi mỗi câu trên một dòng

# Tạo GUI để kéo thả file video
def open_file_dialog():
    file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mkv")])
    if file_path:
        video_label.config(text=file_path)
        process_button.config(state=NORMAL)

# Hàm xử lý chính khi người dùng bấm nút bắt đầu
def process_video():
    video_file = video_label.cget("text")
    
    # Kiểm tra nếu không chọn video
    if video_file == "Chưa chọn video":
        result_label.config(text="Vui lòng chọn video!")
        return
    
    if video_file:
        process_button.config(state=DISABLED)
        progress_bar['value'] = 0  # Reset thanh trạng thái về 0
        result_label.config(text="Đang xử lý video...")

        def run():
            try:
                # Bước 1: Chuyển giọng nói thành văn bản, chia thành từng câu
                sentences = transcribe_audio_with_whisper(video_file, progress_bar)
                
                # Bước 2: Dịch từng câu sang tiếng Việt
                translated_sentences = translate_text_to_vietnamese(sentences, progress_bar)
                
                # Bước 3: Lưu văn bản dịch ra file theo từng dòng
                output_file = "output_translated.txt"
                create_text_file(translated_sentences, output_file)
                
                progress_bar['value'] = 100  # Đặt tiến độ thành 100 khi hoàn thành
                result_label.config(text=f"Hoàn thành! File văn bản: {output_file}")
            except Exception as e:
                result_label.config(text=f"Lỗi: {str(e)}")
            finally:
                process_button.config(state=NORMAL)
        
        # Chạy quá trình xử lý trong luồng riêng để tránh làm đơ giao diện
        threading.Thread(target=run).start()

# Khởi tạo giao diện với Tkinter
root = Tk()
root.title("Auto Vietsub Tool")
root.geometry("400x350")

# Tiêu đề
title_label = Label(root, text="Tạo phụ đề Vietsub tự động", font=("Arial", 16))
title_label.pack(pady=20)

# Nút để chọn file video
select_button = Button(root, text="Chọn video", command=open_file_dialog, font=("Arial", 12))
select_button.pack(pady=10)

# Hiển thị đường dẫn video đã chọn
video_label = Label(root, text="Chưa chọn video", font=("Arial", 10))
video_label.pack(pady=10)

# Nút bắt đầu xử lý video
process_button = Button(root, text="Bắt đầu", command=process_video, font=("Arial", 12), state=DISABLED)
process_button.pack(pady=10)

# Thanh trạng thái Progressbar
progress_bar = ttk.Progressbar(root, orient=HORIZONTAL, length=300, mode='determinate')
progress_bar.pack(pady=10)

# Nhãn hiển thị kết quả
result_label = Label(root, text="", font=("Arial", 10))
result_label.pack(pady=20)

# Chạy giao diện
root.mainloop()
