# CMS
**CMS** là một hệ thống quản trị nội dung hiện đại, cho phép người dùng tạo các không gian làm việc riêng biệt (Workspaces), mời người khác cùng soạn thảo bài viết trong thời gian thực (Real-time Collaboration) và tích hợp AI để kiểm duyệt nội dung tự động trước khi public.

## 🛠️ Công nghệ sử dụng (Tech Stack)

### Backend
*   **FastAPI (Python 3.14):** Framework hiệu năng cao, hỗ trợ xử lý bất đồng bộ (async).
*   **PostgreSQL:** Cơ sở dữ liệu quan hệ chính.
*   **SQLAlchemy:** ORM để quản lý Database.
*   **RabbitMQ & Celery:** Quản lý hàng đợi và tác vụ chạy ngầm.
*   **Google Gemini API:** "Bộ não" AI kiểm duyệt nội dung.

### Frontend
*   **Next.js (React):** UI/UX mượt mà, tối ưu SEO.
*   **Tiptap Editor:** Trình soạn thảo văn bản headless mạnh mẽ.
*   **Tailwind CSS:** Thiết kế giao diện hiện đại, responsive.

### Infrastructure
*   **Docker & Docker Compose:** Container hóa toàn bộ dịch vụ (Postgres, RabbitMQ, Redis).
*   **WebSockets:** Truyền tải dữ liệu thời gian thực.
