# Bộ tiêu chuẩn Aprilinne — viết lại và chấm kịch bản

Bản này dùng cho cả **người viết** và **người chấm** (hai lần gọi Claude độc lập). Người chấm chỉ thấy tiêu chuẩn này và kịch bản, không thấy dàn ý hay lập luận của người viết.

Nguyên tắc chung:

- Mỗi điểm phải có **bằng chứng trích nguyên văn** từ kịch bản, và phải chỉ ra **ở hồi nào**. Máy sẽ dò từng câu trích trong kịch bản: câu trích không tìm thấy coi như không có bằng chứng.
- Điểm 0–10. Có **giới hạn điểm**: vi phạm nào thì điểm tối đa là bao nhiêu, dù phần còn lại hay đến đâu. Máy tự áp các giới hạn đo được (xem cuối tài liệu); người chấm áp các giới hạn còn lại.
- Ba tiêu chí trụ cột **T1, T2, T3** là yêu cầu gốc của người dùng. Trượt một trong ba là kịch bản **không được duyệt**, dù các tiêu chí khác điểm cao đến đâu.
- Kiểm tra sự thật **không chặn duyệt**. Dã sử, giai thoại, kịch tính hóa đều được phép. Người chấm chỉ ghi chú những chỗ nghi sai để người dùng xem.
- Độ dài đọc tính theo 150–170 chữ/phút (một "chữ" là một âm tiết tiếng Việt). Cụ thể: 20 giây ≈ 55 chữ, 1 phút ≈ 160 chữ, 2 phút ≈ 350 chữ, 4 phút ≈ 650 chữ.
- **Hồi** là các phần lớn của kịch bản, mở đầu bằng dòng `## …`. Kịch bản không có tiêu đề hồi thì máy tự chia thành các hồi dài gần bằng nhau.

---

## T1. Tương phản — hai tuyến truyện đối lực, đan xen xuyên suốt (trụ cột)

**Định nghĩa.** Video có **hai tuyến truyện chạy song song từ đầu đến cuối**, kể xen kẽ nhau, và **đối lực** nhau: tuyến này đẩy, tuyến kia kéo ngược lại (hoặc hai tuyến cùng chạy đua, người xem so tiến độ). Đến cuối, hai tuyến **gặp nhau** để giải thích kết quả mà người xem đang thấy hôm nay.

- **Tuyến A (tuyến chính):** hành trình chính của nhân vật/sự kiện.
- **Tuyến B (tuyến đối lực / ngoại truyện):** lực tác động ngược lại tuyến A, hoặc câu chuyện song song ít ai biết. Tuyến B có diễn biến riêng, có tiến độ riêng, không phải lời bình về tuyến A.

Tương phản **không phải** là gắn tính từ trái nghĩa cho một nhân vật ("vừa công thần vừa gian thần", "bàn tay sắt nhưng giữ phép nước"). Đó chỉ là một nhận định, không phải hai câu chuyện.

**Điều kiện đạt (≥ 8), phải có đủ:**

1. Gọi tên được hai tuyến trong một câu mỗi tuyến, và nói được vì sao B đối lực A.
2. **Cả hai tuyến được giới thiệu trong phần mở đầu** (khoảng 2 phút đầu, ≈ 350 chữ): người xem biết ngay mình sẽ theo dõi hai mạch.
3. **Hồi nào cũng có cả A lẫn B** — trích được ít nhất một đoạn của mỗi tuyến ở từng hồi.
4. **Đan xen thật**: tuyến B không bị dồn thành một khối kể một lần; không đoạn nào kể liền một tuyến quá khoảng 4 phút (≈ 650 chữ).
5. **Có mốc tiến độ**: mỗi lần quay lại một tuyến, người xem biết tuyến đó đang ở đâu (đã tới bước nào, mất gì, còn gì) — giống như theo dõi "đội 1 được bao nhiêu %, đội 2 được bao nhiêu %".
6. **Hai tuyến hội tụ ở cuối**: đoạn kết dùng cả A và B để giải thích kết quả hiện tại.

**Giới hạn điểm khi vi phạm:**

| Vi phạm | Điểm tối đa |
|---|---|
| Tương phản chỉ là tính từ/nhận định trái chiều, không có tuyến B có diễn biến riêng | 3 |
| Tuyến B kể dồn một lần (một hồi hoặc một khối liền) rồi biến mất | 4 |
| Có hồi không có tuyến B | 4 |
| Tuyến B chỉ chiếm dưới 15% lời đọc | 4 |
| Tuyến B chỉ là bối cảnh/phụ họa, không đối lực tuyến A | 5 |
| Tuyến B xuất hiện muộn (sau 15% đầu kịch bản) | 6 |
| Có đoạn kể liền một tuyến quá ≈ 900 chữ (≈ 5,5 phút) | 6 |
| Không có mốc tiến độ khi quay lại tuyến | 7 |
| Hai tuyến không hội tụ ở cuối | 7 |

**Ví dụ đạt** (theo lời người dùng):
- *Trần Thủ Độ:* Tuyến A — ông quyết đoán đến mức máu lạnh, từng bước đưa họ Trần lên ngôi. Tuyến B — phía triều đình và các thế lực khác liên tục có động thái tác động ngược lại, có lúc đến mức suýt tiêu diệt ông. Mỗi hồi đặt một bước tiến của ông cạnh một đòn phản công từ phía bên kia; cuối video hai mạch gặp nhau để giải thích vì sao kết cục lại là nhà Trần.
- *Thử thách 3 vùng khắc nghiệt nhất thế giới:* đội chia làm 3, video cắt qua lại giữa các đội, mỗi lần quay lại đều báo "đội này đã xong bao nhiêu %". Người xem theo dõi các tuyến tiến độ từ đầu đến cuối.

**Ví dụ không đạt:**
- "Ông từng bị lên án vì thủ đoạn khắc nghiệt, nhưng cũng được ghi nhận về công lao…" rồi kể một mạch theo thời gian. → Chỉ là nhận định hai mặt, không có tuyến B. Tối đa 3.
- "Một bên là bàn tay sắt với hoàng tộc, một bên lại có những hành động giữ phép nước" ở mở đầu, sau đó không quay lại mạch nào tương ứng ở các hồi. → Tối đa 3.

---

## T2. Phần thưởng cho khán giả — ngoại truyện nằm TRONG tuyến song song (trụ cột)

**Định nghĩa.** Ngoài việc chính của nhân vật, người xem được thưởng bằng những **ngoại truyện** (giai thoại, chuyện ít ai biết) về họ. Phần thưởng này **chỉ được đến qua tuyến B**: mỗi lần quay về tuyến B, người xem nhận thêm một mảnh ngoại truyện mới, và mảnh lớn nhất được hé lộ gần cuối. Phần thưởng **có mặt khi tương phản đạt chuẩn và xuyên suốt** — nó không phải một phần viết riêng.

**Điều kiện đạt (≥ 8), phải có đủ:**

1. Mở đầu **hứa hẹn cụ thể** điều người xem sẽ nhận được từ tuyến B (không phải lời hứa chung chung kiểu "hiểu cả công lẫn tội").
2. Ngoại truyện **nằm trong các đoạn của tuyến B**, trích được ở **ít nhất một nửa số hồi**.
3. **Không có** hồi, đoạn, tiêu đề hay danh sách riêng dành cho giai thoại/phần thưởng ("ba câu chuyện khó tin về ông", "phần thưởng dành cho các bác", "những giai thoại thú vị").
4. Có **một hé lộ lớn** gần cuối, thuộc tuyến B, trả lời lời hứa ở mở đầu.

**Giới hạn điểm khi vi phạm:**

| Vi phạm | Điểm tối đa |
|---|---|
| "Phần thưởng" chỉ là lời hứa trừu tượng (hiểu sâu hơn, nhìn hai mặt…) | 2 |
| Giai thoại được liệt kê hoặc gom thành một phần/đoạn riêng | 3 |
| Giai thoại nằm ngoài tuyến B (chen vào tuyến A như chuyện bên lề) | 4 |
| Có hồi không có tuyến B | 5 |
| Ngoại truyện trích được ở dưới một nửa số hồi | 5 |
| Không có hé lộ lớn gần cuối | 6 |
| Mở đầu không hứa hẹn cụ thể | 7 |

**Ví dụ đạt:** Tuyến B về những lần triều đình phản đòn Trần Thủ Độ; mỗi lần quay về tuyến này kể thêm một giai thoại về cách ông đối phó (chuyện người lính ngăn kiệu, chuyện người họ hàng xin chức…), mỗi giai thoại gắn đúng vào thời điểm của nó trong mạch phản đòn; giai thoại lớn nhất để dành đến lúc hai tuyến hội tụ.

**Ví dụ không đạt:** Ngay mở đầu: "sử cũ còn ghi lại ba câu chuyện khó tin: thưởng người lính dám ngăn kiệu vợ mình, răn đe người họ hàng xin chức và thưởng cả viên quan dám tố cáo ông" — ba giai thoại gom thành một danh sách, rồi kể dồn ở một phần riêng. → Tối đa 3.

---

## T3. Mức đầu tư — lời tâm sự công sức tra cứu, dẫn thẳng vào tuyến ngoại truyện (trụ cột)

**Định nghĩa.** Người dẫn ("em") kể với các bác về công sức mình đã bỏ ra: một **con số công sức** (được cường điệu cho hấp dẫn), **tên các bộ sử/tài liệu lớn** đã tra, và **điều phát hiện ra mà sách giáo khoa không kể**. Điều phát hiện đó **chính là tuyến B** — lời tâm sự là cánh cửa mở vào tuyến ngoại truyện.

**Điều kiện đạt (≥ 8), phải có đủ:**

1. Một đoạn tâm sự ngôi thứ nhất trong **khoảng 2 phút đầu** (≈ 350 chữ).
2. Có **con số công sức** cụ thể (giờ, ngày, tháng, số cuốn…). Cường điệu được phép.
3. Gọi tên **ít nhất hai bộ sử/tài liệu** cụ thể.
4. Nói rõ **phát hiện** ("câu chuyện mà sách giáo khoa không kể", "điều chẳng ai nói với các bác"…).
5. Phát hiện đó **trùng với tuyến B** (cùng nhân vật, cùng mạch sự kiện).
6. Gần cuối, khi tuyến B hé lộ lớn, có **một câu nhắc lại** công sức/nguồn ("chính trong bộ … em mới thấy…").

**Giới hạn điểm khi vi phạm:**

| Vi phạm | Điểm tối đa |
|---|---|
| Không có lời tâm sự công sức (chỉ rải "theo Toàn thư chép…" như chú thích nguồn) | 2 |
| Phát hiện không trùng tuyến B, hoặc không có phát hiện | 4 |
| Không gọi tên được hai bộ sử cụ thể ("sử cũ", "nhiều tài liệu") | 5 |
| Không có con số công sức | 5 |
| Lời tâm sự nằm sau 2 phút đầu | 6 |
| Không nhắc lại ở hé lộ lớn | 7 |
| Có ghi chú biên tập lọt vào lời đọc ("[CẦN KIỂM TRA]", "theo tư liệu được cung cấp") | 6 |

**Ví dụ đạt** (theo lời người dùng): "Em đã dành 1000 giờ tra cứu ba bộ sử lớn nhất là A, B, C, và nhận ra một câu chuyện vô cùng thú vị mà sách giáo khoa chắc chắn không ai kể cho các bác" — và câu chuyện ấy chính là tuyến B được kể xuyên suốt video.

**Ví dụ không đạt:** "Theo những ghi chép trong Đại Việt sử ký toàn thư, mâu thuẫn này gay gắt đến mức…" — đây là dẫn nguồn trong lúc kể, không phải lời tâm sự công sức, không có con số, không có phát hiện. → Tối đa 2.

---

## Các tiêu chí hỗ trợ (đạt khi ≥ 7)

### H1. Mở đầu 20 giây
Câu đầu khớp tiêu đề/chủ đề; trong ≈ 55 chữ đầu có bối cảnh, cái giá hoặc phần thưởng, và một khoảng trống tò mò. **Trích:** câu đầu và câu tạo tò mò.
Giới hạn: câu đầu chung chung, không nêu nhân vật/sự kiện → tối đa 5; không có khoảng trống tò mò → tối đa 5.

### H2. Vào chuyện sớm, liền mạch
Lời chào kênh một lần duy nhất, vào nội dung chính trong ≈ 30 giây. Không chào lại ở các hồi sau, không mở hồi bằng "Các bác ạ" lặp đi lặp lại, không kể lại điều vừa kể, không tóm tắt lại. **Trích:** lời chào, và mọi chỗ lặp.
Giới hạn: chào kênh hơn một lần → tối đa 4; có sự kiện bị kể lại hai lần → tối đa 5; ghi chú biên tập lọt vào lời đọc → tối đa 4.

### H3. Nhịp độ
Cứ khoảng 2–4 phút có một điểm chuyển nhịp (đổi tuyến, đổi cường độ, một biến cố). Không đoạn bình luận/đạo đức kéo dài làm chùng mạch. **Trích:** đoạn dài nhất không có biến cố.
Giới hạn: có đoạn bình luận liền quá ≈ 500 chữ → tối đa 5.

### H4. Hé lộ lớn và kết ở cao trào
Gần cuối hé lộ phần thưởng lớn (thuộc tuyến B, xem T2), hai tuyến hội tụ, rồi kết ngay ở cao trào (kịch tính, ấm áp hoặc hài hước). Lời kêu gọi cuối video đặt sau cao trào, không chen trước hé lộ (xem H6). **Trích:** câu hé lộ và câu kết.
Giới hạn: kết bằng tóm tắt/bài học chung chung → tối đa 5; sau cao trào còn kéo dài quá ≈ 150 chữ trước lời kêu gọi → tối đa 6.

### H5. Giọng kênh
Người dẫn xưng "em", gọi khán giả là "các bác"; giọng tán gẫu như kể chuyện ở quán nước; thành ngữ, so sánh dân dã, câu hỏi tu từ vừa phải (không cuối mọi đoạn); mỗi câu cửa miệng dùng tối đa hai lần. Viết thành đoạn văn để đọc, không gạch đầu dòng; chỗ chèn hình ghi `[HÌNH: …]`. **Trích:** 2–3 câu tiêu biểu.
Giới hạn: xưng hô sai ("tôi", "các bạn") → tối đa 5; câu cửa miệng lặp quá 3 lần → tối đa 6.

### H6. Kêu gọi tương tác
Người dẫn xin like, theo dõi, bình luận **ở 2–3 chỗ**, mỗi chỗ **một cách nói khác nhau**, giọng "em" tự nhiên như nhờ người quen:

1. **Sau mở đầu** (trong khoảng 2 phút đầu), dành cho người mới — ví dụ: "Nếu các bác lần đầu đến kênh của em, hãy cho em xin một like, một lượt theo dõi để ủng hộ kênh em nha."
2. **Giữa video**, ở chỗ chuyển tuyến hoặc vừa xong một đỉnh, không cắt ngang lúc gay cấn — ví dụ: "Kênh của em thường xuyên làm về những nhân vật như thế này; nếu các bác đã xem đến đây, cho em xin một lượt theo dõi để không bỏ sót những video tiếp theo nhé."
3. **Cuối video**, sau cao trào: xin theo dõi và mời các bác để lại bình luận, tốt nhất là một câu hỏi gắn với tuyến B (vd. "nếu là các bác, các bác chọn phe nào?").

Các câu chỉ là ví dụ, mỗi kịch bản phải tự viết cách nói riêng, đa dạng. **Trích:** từng lời kêu gọi kèm hồi.
Giới hạn: không có lời kêu gọi nào → tối đa 3; chỉ có một chỗ → tối đa 5; các lời kêu gọi gần như lặp lại một câu → tối đa 6; chen ngang đoạn gay cấn hoặc đứng trước hé lộ lớn → tối đa 6; quá 4 chỗ hoặc kéo dài như quảng cáo → tối đa 6.

---

## Ghi chú sự thật (không chặn duyệt)
Người chấm liệt kê những chỗ nghi sai (tên, năm, quan hệ), mỗi chỗ một câu trích và lý do. Không trừ điểm vì dã sử, giai thoại, kịch tính hóa hay con số công sức cường điệu.

## Điều kiện duyệt

Kịch bản được duyệt khi **đồng thời**:

1. T1, T2, T3 đều **≥ 8** (sau khi áp giới hạn).
2. H1–H6 đều **≥ 7**.
3. Máy kiểm tra không báo lỗi chặn (bên dưới).

## Phần máy kiểm tra (không dựa vào lời người chấm)

Người chấm phải chia kịch bản thành các **đoạn tuyến** theo thứ tự: mỗi đoạn ghi thuộc tuyến A, B hay chung, kèm câu mở đầu đoạn trích nguyên văn. Máy dò các câu mở đầu đó trong kịch bản để đo, rồi tự áp giới hạn:

| Máy đo | Giới hạn tự động |
|---|---|
| Câu trích không có trong kịch bản | bằng chứng đó bị loại; tiêu chí không còn bằng chứng → tối đa 3 |
| Hồi không có đoạn tuyến B | T1 ≤ 4, T2 ≤ 5 |
| Tuyến B < 15% số chữ | T1 ≤ 4 |
| Đoạn B đầu tiên bắt đầu sau 15% kịch bản | T1 ≤ 6 |
| Đoạn liền một tuyến > 900 chữ | T1 ≤ 6 |
| Ngoại truyện (trích, nằm trong đoạn B) ở dưới một nửa số hồi | T2 ≤ 5 |
| Có phần riêng cho giai thoại (người chấm đánh dấu, kèm trích) | T2 ≤ 3 |
| Không có lời tâm sự công sức (trích được) | T3 ≤ 2 |
| Lời tâm sự bắt đầu sau 350 chữ đầu | T3 ≤ 6 |
| Lời tâm sự không có con số | T3 ≤ 5 |
| Lời tâm sự gọi tên dưới hai bộ sử | T3 ≤ 5 |
| Người chấm xác nhận phát hiện không trùng tuyến B | T3 ≤ 4 |
| Ghi chú biên tập trong lời đọc ("CẦN KIỂM TRA", "tư liệu được cung cấp", "tư liệu đầu vào") | lỗi chặn |
| Lời chào kênh xuất hiện hơn một lần | H2 ≤ 4 |
| Không có lời kêu gọi nào (like / theo dõi / đăng ký / bình luận) | H6 ≤ 3 |
| Lời kêu gọi chỉ ở một hồi | H6 ≤ 5 |
