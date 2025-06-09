async function summarize() {
    const text = document.getElementById("inputText").value;
    const sourceLang = document.getElementById("sourceLang").value;
    const targetLang = document.getElementById("targetLang").value;

    const resultArea = document.getElementById("resultArea");
    const loadingMessage = document.getElementById("loadingMessage");
    const button = document.querySelector("button");

    // Clear previous result and show loading
    resultArea.innerText = "";
    loadingMessage.style.display = "block";
    button.disabled = true;

    // Validate input
    if (!text.trim()) {
        loadingMessage.style.display = "none";
        resultArea.innerText = "⚠️ Vui lòng nhập nội dung để tóm tắt.";
        button.disabled = false;
        return;
    }

    try {
        const response = await fetch("/summarize_translate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                text: text,
                source_lang: sourceLang,
                target_lang: targetLang
            })
        });

        const result = await response.json();
        console.log(result);  // For debugging
        resultArea.innerText = result.summary || result.error || "⚠️ Lỗi không xác định.";
    } catch (error) {
        console.error("Fetch error:", error);
        resultArea.innerText = "❌ Đã xảy ra lỗi khi gửi yêu cầu.";
    } finally {
        loadingMessage.style.display = "none";
        button.disabled = false;
    }
}

async function loadHistory() {
    const historyArea = document.getElementById("historyArea");
    historyArea.innerHTML = "<p>📚 Đang tải lịch sử...</p>";

    try {
        const response = await fetch("/history");
        const data = await response.json();

        if (!Array.isArray(data)) {
            historyArea.innerHTML = "<p>⚠️ Không lấy được dữ liệu lịch sử.</p>";
            return;
        }

        if (data.length === 0) {
            historyArea.innerHTML = "<p>🕘 Chưa có bản tóm tắt nào được lưu.</p>";
            return;
        }

        const html = data.map(item => `
            <div style="margin-bottom: 1.5rem; padding: 1rem; background: #f1f5f9; border-radius: 0.75rem;">
              <p><strong>📝 Gốc (${item.source_lang}):</strong> ${item.input_text}</p>
              <p><strong>🔍 Tóm tắt (${item.target_lang}):</strong> ${item.summary_text}</p>
              <p style="font-size: 0.85rem; color: gray;">⏱ ${item.timestamp}</p>
            </div>
        `).join("");

        historyArea.innerHTML = html;

    } catch (error) {
        console.error("History error:", error);
        historyArea.innerHTML = "<p>❌ Lỗi khi tải lịch sử.</p>";
    }
}
