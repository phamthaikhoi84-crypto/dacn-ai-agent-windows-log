# Tuần 0: Đề cương và chốt đề tài (05/10 – 15/10/2026)

## Việc đã làm

- Viết đề cương (hiện ở bản v9: [docs/De_cuong_DACN.pdf](../docs/De_cuong_DACN.pdf)).
- Khôi thử nghiệm sơ bộ mô hình ngôn ngữ nhỏ trên Ollama (06–07/10/2026): Qwen3 0.6B, 4B, 8B, 30B-A3B, chạy CPU. Kết quả chính: mô hình đoán sai mã kỹ thuật khi tự nhớ, nhưng chọn đúng khi được đưa danh sách ứng viên; khi đáp án đúng không có trong danh sách, mô hình vẫn chọn bừa và bịa lý do.

## Góp ý của thầy

- Buổi 08/10: đề tài và đề cương được đánh giá tốt nhưng chưa duyệt, vì nhóm chưa giải thích được (phụ thuộc AI). Yêu cầu: tên đề tài dùng một cách gọi và ngắn hơn; so sánh mô hình nhiều họ khác nhau; tự viết agent, không dùng LangChain/LangGraph; dùng dữ liệu log tấn công và log bình thường có nhãn; agent tự phát hiện lỗi của mình; xử lý log liên quan của cùng người dùng nhưng cách xa nhau về thời gian.
- Buổi thứ 2: có nhóm 3 làm đề tài gần giống. Hai nhóm phải trao đổi để khác nhau về phương pháp và hành vi tấn công.

## Kết quả

- Tên đề tài: "Xây dựng AI Agent sử dụng mô hình ngôn ngữ nhỏ phát hiện mối đe dọa dựa trên log Windows".
- Trao đổi với nhóm 3: nhóm 3 dùng Security log; nhóm mình dùng Sysmon + PowerShell làm nguồn chính, chuỗi 8 kỹ thuật, agent tự viết bằng Python.
