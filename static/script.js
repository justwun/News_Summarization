async function summarize() {
    const text = document.getElementById("inputText").value;
    const sourceLang = document.getElementById("sourceLang").value;
    const targetLang = document.getElementById("targetLang").value;
    const summaryLength = document.getElementById("summaryLength").value;

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
                target_lang: targetLang,
                summary_length: summaryLength
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
