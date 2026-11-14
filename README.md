# CẤU TRÚC APRILINNE

Viết lại và chấm kịch bản YouTube tiếng Việt theo bộ tiêu chuẩn [`STANDARDS.md`](STANDARDS.md), dùng Claude cho cả viết và chấm. Người viết và người chấm là hai lần gọi Claude độc lập: người chấm chỉ thấy tiêu chuẩn và kịch bản.

- `STANDARDS.md` — tiêu chuẩn: 3 trụ cột (tương phản hai tuyến, phần thưởng = ngoại truyện trong tuyến song song, mức đầu tư) và 6 tiêu chí hỗ trợ (có kêu gọi tương tác), điều kiện đạt, giới hạn điểm.
- `style.md` — giọng kênh (xưng "em", gọi "các bác").
- `aprilinne/` — công cụ (Python 3, không cần cài thêm gì).
- `runs/<tên>/` — mỗi lần chạy: `nguon.txt` (transcript), `dan_y.md`, `vong<N>/kich_ban.md`, `vong<N>/bang_diem.md`, `KET_QUA.md`; `buoc/` giữ đề bài và câu trả lời của từng bước.

## Chạy

```bash
python -m aprilinne moi <tên> --url <link YouTube> [--kenh "Tên kênh"] [--phut 15]
python -m aprilinne chay <tên>
python -m aprilinne cham <tên> <file kịch bản>     # chỉ chấm một kịch bản có sẵn
python -m aprilinne xem
```

Transcript lấy qua Transcript Engine local (`http://127.0.0.1:8000`, cùng cách gọi với AI MANAGER, chỉ đọc). Có thể đưa file thay link: `--transcript file.txt`.

### Ai trả lời từng bước (`--may`)

- `file` (mặc định): công cụ ghi đề bài `runs/<tên>/buoc/<bước>.prompt.md` rồi dừng (mã thoát 3). Một phiên Claude Code làm bước đó và ghi `…out.md`; bước chấm giao cho một tác tử mới, không biết gì ngoài đề bài. Rồi chạy `chay` để đi tiếp.
- `cli`: tự gọi Claude Code không giao diện (`claude -p`), mỗi bước một tiến trình mới. Cần Claude Code đã đăng nhập trên máy (chạy `claude` một lần và `/login`).

## Quy trình

transcript → dàn ý (máy kiểm: hồi nào cũng có tuyến B, đủ lời tâm sự công sức) → viết → biên tập → chấm → nếu chưa đạt thì sửa từ bản tốt nhất và chấm lại, tối đa 3 vòng.

Chấm: người chấm chia kịch bản thành các đoạn tuyến A/B và trích bằng chứng nguyên văn từng hồi; máy dò lại mọi câu trích, đo tỷ lệ tuyến B, đoạn liền dài nhất, hồi thiếu tuyến B, vị trí lời tâm sự… rồi áp giới hạn điểm. Duyệt khi T1–T3 ≥ 8, H1–H6 ≥ 7 và không có lỗi chặn.

## Test

```bash
python -m unittest discover -s tests -t .
```
