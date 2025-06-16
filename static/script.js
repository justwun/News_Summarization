let isLoggedIn = false;
let currentUsername = "";

function updateLoginStatus() {
  const loginStatus = document.getElementById("loginStatus");
  const logoutBtn = document.getElementById("logoutBtn");
  const historyBtn = document.getElementById("historyBtn");

  if (isLoggedIn) {
    loginStatus.innerText = `🔐 Đã đăng nhập: ${currentUsername}`;
    logoutBtn.style.display = "inline-block";
    historyBtn.disabled = false;
  } else {
    loginStatus.innerText = "👤 Bạn đang ở chế độ khách.";
    logoutBtn.style.display = "none";
    historyBtn.disabled = true;
  }
}

async function summarize() {
  const text = document.getElementById("inputText").value;
  const sourceLang = document.getElementById("sourceLang").value;
  const targetLang = document.getElementById("targetLang").value;

  const resultArea = document.getElementById("resultArea");
  const loadingMessage = document.getElementById("loadingMessage");
  const button = document.querySelector("button");

  resultArea.innerText = "";
  loadingMessage.style.display = "block";
  button.disabled = true;

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
    resultArea.innerText = result.summary || result.message || result.error || "⚠️ Lỗi không xác định.";
  } catch (error) {
    resultArea.innerText = "❌ Đã xảy ra lỗi khi gửi yêu cầu.";
  } finally {
    loadingMessage.style.display = "none";
    button.disabled = false;
  }
}

async function loadHistory() {
  if (!isLoggedIn) {
    alert("⚠️ Bạn cần đăng nhập để xem lịch sử.");
    return;
  }

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
    historyArea.innerHTML = "<p>❌ Lỗi khi tải lịch sử.</p>";
  }
}

async function login() {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value;

  const res = await fetch("/login", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ username, password })
  });

  const data = await res.json();
  if (res.ok) {
    isLoggedIn = true;
    currentUsername = username;
    updateLoginStatus();
  } else {
    document.getElementById("loginStatus").innerText = data.error;
  }
}

async function register() {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value;

  const res = await fetch("/register", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ username, password })
  });

  const data = await res.json();
  document.getElementById("loginStatus").innerText = data.message || data.error;
}

async function logout() {
  await fetch("/logout", { method: "POST" });
  isLoggedIn = false;
  currentUsername = "";
  updateLoginStatus();
}

function chooseGuest() {
  isLoggedIn = false;
  currentUsername = "";
  updateLoginStatus();
}

function showLoginForm() {
  document.getElementById("authChoice").style.display = "none";
  document.getElementById("authArea").style.display = "";
  updateLoginStatus();
}
