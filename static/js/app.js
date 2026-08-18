document.addEventListener("DOMContentLoaded", () => {
    // -------------------------------------------------------------
    // 1. Tab Navigation & State
    // -------------------------------------------------------------
    const navItems = document.querySelectorAll(".nav-item");
    const tabPanels = document.querySelectorAll(".tab-panel");
    const activeTabTitle = document.getElementById("active-tab-title");

    const tabTitles = {
        "chat-tab": "Socratic Tutor",
        "flashcards-tab": "Flashcard Study Deck",
        "quiz-tab": "Practice Quiz Center",
        "summary-tab": "Note Synthesizer"
    };

    navItems.forEach(item => {
        item.addEventListener("click", () => {
            const targetTab = item.getAttribute("data-tab");

            navItems.forEach(n => n.classList.remove("active"));
            tabPanels.forEach(p => p.classList.remove("active"));

            item.classList.add("active");
            document.getElementById(targetTab).classList.add("active");
            activeTabTitle.textContent = tabTitles[targetTab] || "Student Copilot";
        });
    });

    // -------------------------------------------------------------
    // 2. Health & Engine Status Check
    // -------------------------------------------------------------
    const aiStatusBadge = document.getElementById("ai-status-badge");
    fetch("/api/health")
        .then(res => res.json())
        .then(data => {
            if (data.status === "healthy") {
                const engine = data.ai_engine === "azure" ? "Azure OpenAI" :
                    data.ai_engine === "openai" ? "OpenAI" : "Simulation Engine";
                aiStatusBadge.textContent = `Engine: ${engine}`;
            }
        })
        .catch(() => {
            aiStatusBadge.textContent = "Engine: Offline";
            aiStatusBadge.style.color = "#ef4444";
        });

    // -------------------------------------------------------------
    // 3. Socratic Chat Handler
    // -------------------------------------------------------------
    const chatForm = document.getElementById("chat-form");
    const chatInput = document.getElementById("chat-input");
    const chatHistory = document.getElementById("chat-history");
    const personaSelect = document.getElementById("persona-select");

    let messages = [];

    chatForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const text = chatInput.value.trim();
        if (!text) return;

        // Append user message
        appendChatMessage("user", text);
        messages.push({ role: "user", content: text });
        chatInput.value = "";

        // Placeholder for bot
        const botBubble = appendChatMessage("bot", "Thinking...");

        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    messages: messages,
                    mode: personaSelect.value
                })
            });

            const data = await response.json();
            if (data.reply) {
                botBubble.querySelector(".msg-content").innerHTML = formatMarkdown(data.reply);
                messages.push({ role: "assistant", content: data.reply });
            } else {
                botBubble.querySelector(".msg-content").textContent = "Error: Could not retrieve response.";
            }
        } catch (err) {
            botBubble.querySelector(".msg-content").textContent = "Network error. Server may be down.";
        }

        chatHistory.scrollTop = chatHistory.scrollHeight;
    });

    function appendChatMessage(sender, text) {
        const msgDiv = document.createElement("div");
        msgDiv.className = `message ${sender}-msg`;
        msgDiv.innerHTML = `<div class="msg-content">${formatMarkdown(text)}</div>`;
        chatHistory.appendChild(msgDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
        return msgDiv;
    }

    // -------------------------------------------------------------
    // 4. Flashcard Generator & 3D Flip Handler
    // -------------------------------------------------------------
    const fcTopicInput = document.getElementById("fc-topic-input");
    const fcGenerateBtn = document.getElementById("fc-generate-btn");
    const flashcardDeck = document.getElementById("flashcard-deck");

    fcGenerateBtn.addEventListener("click", async () => {
        const topic = fcTopicInput.value.trim() || "Cloud Fundamentals";
        fcGenerateBtn.textContent = "Generating...";
        fcGenerateBtn.disabled = true;

        try {
            const res = await fetch("/api/study/flashcards", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ topic: topic })
            });
            const data = await res.json();

            flashcardDeck.innerHTML = "";
            if (data.cards && data.cards.length > 0) {
                data.cards.forEach(card => {
                    const cardEl = document.createElement("div");
                    cardEl.className = "card-item";
                    cardEl.innerHTML = `
                        <div class="card-inner">
                            <div class="card-front">${card.front}</div>
                            <div class="card-back">${card.back}</div>
                        </div>
                    `;
                    cardEl.addEventListener("click", () => {
                        cardEl.classList.toggle("flipped");
                    });
                    flashcardDeck.appendChild(cardEl);
                });
            } else {
                flashcardDeck.innerHTML = `<p class="empty-state">No flashcards returned. Try another topic.</p>`;
            }
        } catch (err) {
            flashcardDeck.innerHTML = `<p class="empty-state">Error generating flashcards.</p>`;
        } finally {
            fcGenerateBtn.textContent = "Generate Deck";
            fcGenerateBtn.disabled = false;
        }
    });

    // -------------------------------------------------------------
    // 5. Interactive Practice Quiz Handler
    // -------------------------------------------------------------
    const quizTopicInput = document.getElementById("quiz-topic-input");
    const quizGenerateBtn = document.getElementById("quiz-generate-btn");
    const quizContainer = document.getElementById("quiz-container");

    quizGenerateBtn.addEventListener("click", async () => {
        const topic = quizTopicInput.value.trim() || "Azure Services";
        quizGenerateBtn.textContent = "Generating Quiz...";
        quizGenerateBtn.disabled = true;

        try {
            const res = await fetch("/api/study/quiz", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ topic: topic })
            });
            const data = await res.json();

            quizContainer.innerHTML = "";
            if (data.questions && data.questions.length > 0) {
                data.questions.forEach((q, idx) => {
                    const qCard = document.createElement("div");
                    qCard.className = "quiz-card";

                    let optionsHtml = "";
                    q.options.forEach((opt, oIdx) => {
                        optionsHtml += `<button class="option-btn" data-correct="${oIdx === q.correct_index}">${opt}</button>`;
                    });

                    qCard.innerHTML = `
                        <h3>Q${idx + 1}: ${q.question}</h3>
                        <div class="quiz-options">${optionsHtml}</div>
                        <div class="quiz-explanation" style="display:none;"><strong>Explanation:</strong> ${q.explanation}</div>
                    `;

                    // Handle answer selection
                    const btns = qCard.querySelectorAll(".option-btn");
                    const expl = qCard.querySelector(".quiz-explanation");

                    btns.forEach(b => {
                        b.addEventListener("click", () => {
                            btns.forEach(btn => {
                                btn.disabled = true;
                                if (btn.getAttribute("data-correct") === "true") {
                                    btn.classList.add("correct");
                                }
                            });
                            if (b.getAttribute("data-correct") !== "true") {
                                b.classList.add("wrong");
                            }
                            expl.style.display = "block";
                        });
                    });

                    quizContainer.appendChild(qCard);
                });
            } else {
                quizContainer.innerHTML = `<p class="empty-state">No questions found. Try another topic.</p>`;
            }
        } catch (err) {
            quizContainer.innerHTML = `<p class="empty-state">Error generating practice quiz.</p>`;
        } finally {
            quizGenerateBtn.textContent = "Generate Quiz";
            quizGenerateBtn.disabled = false;
        }
    });

    // -------------------------------------------------------------
    // 6. Summarizer / Note Synthesizer Handler
    // -------------------------------------------------------------
    const summaryInput = document.getElementById("summary-input");
    const summaryGenerateBtn = document.getElementById("summary-generate-btn");
    const summaryOutput = document.getElementById("summary-output");

    summaryGenerateBtn.addEventListener("click", async () => {
        const text = summaryInput.value.trim();
        if (!text) return;

        summaryGenerateBtn.textContent = "Synthesizing...";
        summaryGenerateBtn.disabled = true;

        try {
            const res = await fetch("/api/study/summarize", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ content: text })
            });
            const data = await res.json();
            if (data.summary) {
                summaryOutput.innerHTML = formatMarkdown(data.summary);
            } else {
                summaryOutput.innerHTML = `<p class="empty-state">Unable to summarize text.</p>`;
            }
        } catch (err) {
            summaryOutput.innerHTML = `<p class="empty-state">Error connecting to summarizer.</p>`;
        } finally {
            summaryGenerateBtn.textContent = "Synthesize Notes";
            summaryGenerateBtn.disabled = false;
        }
    });

    // Lightweight markdown formatter for bolding, code blocks, lists
    function formatMarkdown(str) {
        if (!str) return "";
        return str
            .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
            .replace(/\*(.*?)\*/g, "<em>$1</em>")
            .replace(/`([^`]+)`/g, "<code>$1</code>")
            .replace(/\n\n/g, "<br><br>")
            .replace(/\n/g, "<br>");
    }
});