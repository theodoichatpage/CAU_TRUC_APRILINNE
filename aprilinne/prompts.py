"""Prompts for the writer (outline, write, edit, repair) and for the grader. The grader prompt carries only the
standards and the script: never the outline, the writer's notes or earlier scorecards."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def standards():
    return (ROOT / 'STANDARDS.md').read_text(encoding='utf-8')


def style():
    return (ROOT / 'style.md').read_text(encoding='utf-8')


def _channel(cfg):
    k = (cfg.get('kenh') or '').strip()
    return ('Tên kênh: "%s". Lời chào duy nhất ở mở đầu nhắc tên kênh này.' % k) if k else \
        'Chưa có tên kênh: lời chào duy nhất ở mở đầu nói chung ("chào mừng các bác quay lại với kênh của em"), không bịa tên kênh.'


def _length(cfg):
    w = int(cfg.get('so_chu_muc_tieu') or 0)
    return 'Độ dài: khoảng %d chữ (≈ %d phút đọc, 160 chữ/phút), lệch tối đa 15%%.' % (w, round(w / 160)) if w else ''


OUTLINE_SCHEMA = {
    'tieu_de': 'tiêu đề video',
    'tuyen_A': 'một câu: tuyến chính',
    'tuyen_B': 'một câu: tuyến đối lực / ngoại truyện',
    'doi_luc': 'một câu: vì sao B kéo ngược hoặc chạy đua với A',
    'dau_tu': {'con_so': 'vd "1000 giờ"', 'bo_su': ['tên bộ sử 1', 'tên bộ sử 2', 'tên bộ sử 3'],
               'phat_hien': 'câu chuyện sách giáo khoa không kể = tuyến B'},
    'hua_hen_mo_dau': 'điều cụ thể người xem sẽ nhận được từ tuyến B',
    'hoi': [{'so': 1, 'ten': 'tên hồi', 'buoc_A': 'diễn biến tuyến A trong hồi', 'buoc_B': 'diễn biến tuyến B trong hồi',
             'ngoai_truyen': 'mảnh ngoại truyện tuyến B mở ra trong hồi (lấy từ transcript nếu có)',
             'moc_tien_do': 'tiến độ mỗi tuyến cuối hồi', 'nhip_chuyen': 'thứ tự đan xen, vd A-B-A-B'}],
    'he_lo_lon': 'mảnh ngoại truyện lớn nhất, hé lộ gần cuối',
    'hoi_tu': 'cách hai tuyến gặp nhau để giải thích kết quả hiện tại',
}

GRADE_SCHEMA = {
    'tuyen_A': 'một câu (rỗng nếu không có)',
    'tuyen_B': 'một câu (rỗng nếu không có tuyến B có diễn biến riêng)',
    'doi_luc': 'một câu, hoặc rỗng',
    'doan': [{'hoi': 1, 'tuyen': 'A | B | chung', 'mo_dau': '8–15 chữ đầu tiên của đoạn, chép NGUYÊN VĂN'}],
    'ngoai_truyen': [{'hoi': 2, 'trich': 'câu nguyên văn kể ngoại truyện/giai thoại'}],
    'phan_rieng_giai_thoai': [{'hoi': 1, 'trich': 'câu nguyên văn — chỉ khi có phần/danh sách riêng cho giai thoại'}],
    'dau_tu': {'trich': 'đoạn tâm sự công sức nguyên văn, rỗng nếu không có', 'con_so': '', 'bo_su': ['tên đúng như trong trích'],
               'phat_hien': '', 'trung_tuyen_B': False, 'nhac_lai': 'câu nhắc lại nguyên văn gần cuối, hoặc rỗng'},
    'tieu_chi': {k: {'diem': 0, 'bang_chung': [{'hoi': 1, 'trich': 'nguyên văn'}], 'ly_do': '', 'cach_sua': ''}
                 for k in ['T1', 'T2', 'T3', 'H1', 'H2', 'H3', 'H4', 'H5']},
    'su_that': [{'trich': 'nguyên văn', 'ghi_chu': 'nghi sai ở đâu'}],
}


def outline(cfg, transcript):
    return '\n\n'.join(x for x in [
        'Bạn là biên kịch trưởng. Nhiệm vụ: lập DÀN Ý để viết lại video dưới đây thành kịch bản mới đạt bộ tiêu chuẩn Aprilinne.',
        '# BỘ TIÊU CHUẨN\n\n' + standards(),
        '# GIỌNG KÊNH\n\n' + style(),
        _channel(cfg), _length(cfg),
        'Yêu cầu dàn ý:\n'
        '- Chọn hai tuyến A và B ĐỐI LỰC từ chính nội dung transcript (tuyến B là lực kéo ngược hoặc câu chuyện song song ít ai biết, có diễn biến riêng). Nếu transcript kể một mạch, hãy tách những sự kiện/giai thoại thuộc phía đối lực ra thành tuyến B và phân bố lại theo thời gian.\n'
        '- 5 đến 8 hồi. HỒI NÀO CŨNG có bước tuyến A và bước tuyến B; ngoại truyện của tuyến B rải ở ít nhất một nửa số hồi; không hồi nào chỉ dành cho giai thoại.\n'
        '- Hồi 1 chứa mở đầu: câu đầu khớp tiêu đề, giới thiệu cả hai tuyến, lời tâm sự công sức (con số cường điệu được, ≥ 2 bộ sử có thật, phát hiện = tuyến B), lời chào kênh một lần.\n'
        '- Hồi cuối: hé lộ lớn của tuyến B, hai tuyến hội tụ, kết ở cao trào.',
        'Chỉ trả về MỘT khối JSON đúng mẫu sau (giữ nguyên tên trường):\n```json\n%s\n```' % json.dumps(OUTLINE_SCHEMA, ensure_ascii=False, indent=1),
        '# TRANSCRIPT VIDEO GỐC\n\n' + transcript,
    ] if x)


def write(cfg, transcript, plan):
    return '\n\n'.join(x for x in [
        'Bạn là biên kịch. Viết TOÀN BỘ kịch bản đọc (voice-over) tiếng Việt theo dàn ý đã duyệt, đạt bộ tiêu chuẩn Aprilinne.',
        '# BỘ TIÊU CHUẨN\n\n' + standards(),
        '# GIỌNG KÊNH\n\n' + style(),
        _channel(cfg), _length(cfg),
        '# DÀN Ý\n\n```json\n%s\n```' % json.dumps(plan, ensure_ascii=False, indent=1),
        'Cách trình bày:\n'
        '- Mỗi hồi mở bằng dòng `## Hồi N — tên hồi`, theo đúng thứ tự dàn ý.\n'
        '- Trong mỗi hồi, kể xen kẽ tuyến A và tuyến B theo "nhịp chuyển"; mỗi lần đổi tuyến có câu bắc cầu và cho người xem biết tuyến đó đang tới đâu.\n'
        '- Không ghi nhãn A/B, không ghi chú biên tập, không gạch đầu dòng. Chỉ trả về kịch bản, không lời giải thích.',
        '# TRANSCRIPT VIDEO GỐC (tư liệu)\n\n' + transcript,
    ] if x)


def edit(cfg, script):
    return '\n\n'.join(x for x in [
        'Bạn là biên tập viên. Biên tập kịch bản dưới đây cho liền mạch và đúng giọng kênh, KHÔNG làm hỏng cấu trúc hai tuyến.',
        '# BỘ TIÊU CHUẨN\n\n' + standards(),
        '# GIỌNG KÊNH\n\n' + style(),
        _channel(cfg), _length(cfg),
        'Việc cần làm: cắt chỗ kể lại/tóm tắt lại, câu cửa miệng lặp, lời chào thừa, đoạn bình luận kéo dài; giữ mọi đoạn tuyến B, '
        'mọi ngoại truyện, lời tâm sự công sức và hé lộ cuối; giữ tiêu đề `## Hồi N — …`. Chỉ trả về kịch bản đã biên tập.',
        '# KỊCH BẢN\n\n' + script,
    ] if x)


def repair(cfg, transcript, plan, script, scorecard_md):
    return '\n\n'.join(x for x in [
        'Bạn là biên kịch. Kịch bản dưới đây CHƯA ĐẠT bộ tiêu chuẩn Aprilinne. Viết lại TOÀN BỘ kịch bản để sửa mọi tiêu chí trượt, giữ nguyên những gì đã đạt.',
        '# BỘ TIÊU CHUẨN\n\n' + standards(),
        '# GIỌNG KÊNH\n\n' + style(),
        _channel(cfg), _length(cfg),
        '# BẢNG ĐIỂM CỦA NGƯỜI CHẤM\n\n' + scorecard_md,
        '# DÀN Ý\n\n```json\n%s\n```' % json.dumps(plan, ensure_ascii=False, indent=1),
        'Trình bày như cũ: `## Hồi N — tên hồi`, đoạn văn đọc thành tiếng, `[HÌNH: …]` trên dòng riêng. Chỉ trả về kịch bản.',
        '# KỊCH BẢN CẦN SỬA\n\n' + script,
        '# TRANSCRIPT VIDEO GỐC (tư liệu)\n\n' + transcript,
    ] if x)


def grade(numbered_script):
    return '\n\n'.join([
        'Bạn là NGƯỜI CHẤM độc lập, khắt khe. Chấm kịch bản dưới đây theo đúng bộ tiêu chuẩn Aprilinne. '
        'Bạn không biết ai viết và không có tài liệu nào khác ngoài tiêu chuẩn và kịch bản. Không nương tay: '
        'một điều kiện đạt không trích được bằng chứng là chưa đạt; áp mọi giới hạn điểm trong tiêu chuẩn.',
        '# BỘ TIÊU CHUẨN\n\n' + standards(),
        'Cách làm:\n'
        '1. Đọc hết kịch bản. Xác định tuyến A và tuyến B theo định nghĩa T1. Nếu không có tuyến B có diễn biến riêng, để `tuyen_B` rỗng và đánh mọi đoạn là A hoặc chung.\n'
        '2. Chia TOÀN BỘ kịch bản, từ đầu đến cuối, thành các đoạn tuyến liên tiếp theo thứ tự (`doan`): mỗi lần mạch kể đổi sang tuyến khác là một đoạn mới. '
        '`mo_dau` là 8–15 chữ đầu tiên của đoạn, CHÉP NGUYÊN VĂN từ kịch bản (máy sẽ dò, sai một chữ là mất). Lời chào, lời kêu gọi theo dõi là `chung`.\n'
        '3. Liệt kê ngoại truyện/giai thoại (`ngoai_truyen`), và chỉ khi có phần/danh sách riêng gom giai thoại thì liệt kê ở `phan_rieng_giai_thoai`.\n'
        '4. Tìm lời tâm sự công sức (`dau_tu`); bằng chứng phải nguyên văn. `trung_tuyen_B` = true chỉ khi phát hiện trong lời tâm sự đúng là tuyến B.\n'
        '5. Chấm 8 tiêu chí: mỗi tiêu chí có điểm 0–10, bằng chứng trích nguyên văn kèm số hồi, lý do ngắn, cách sửa cụ thể nếu dưới ngưỡng.\n'
        '6. Ghi chú sự thật nếu nghi sai (không trừ điểm).',
        'Chỉ trả về MỘT khối JSON đúng mẫu sau:\n```json\n%s\n```' % json.dumps(GRADE_SCHEMA, ensure_ascii=False, indent=1),
        '# KỊCH BẢN CẦN CHẤM\n\n' + numbered_script,
    ])
