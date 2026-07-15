document.addEventListener('DOMContentLoaded', () => {
    // 1. Build chatbot container elements
    const botContainer = document.createElement('div');
    botContainer.id = 'proctor-chatbot';
    botContainer.style.position = 'fixed';
    botContainer.style.bottom = '30px';
    botContainer.style.right = '30px';
    botContainer.style.zIndex = '100000';
    botContainer.style.fontFamily = "'Outfit', sans-serif";

    botContainer.innerHTML = `
        <!-- Floating Action Button -->
        <button id="chatbot-toggle" style="width: 60px; height: 60px; border-radius: 50%; background: linear-gradient(135deg, #ff3b5c 0%, #7c3aed 100%); border: none; color: white; font-size: 1.8rem; cursor: pointer; box-shadow: 0 8px 25px rgba(255, 59, 92, 0.4); display: flex; align-items: center; justify-content: center; transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);">
            💬
        </button>

        <!-- Chat Window -->
        <div id="chatbot-window" style="display: none; width: 350px; height: 450px; background: rgba(20, 27, 45, 0.95); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 20px; box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5); position: absolute; bottom: 80px; right: 0; flex-direction: column; overflow: hidden; animation: fadeInUp 0.4s cubic-bezier(0.16, 1, 0.3, 1);">
            <!-- Header -->
            <div style="background: rgba(255, 255, 255, 0.03); padding: 15px 20px; border-bottom: 1px solid rgba(255, 255, 255, 0.08); display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background-color: #00e676; animation: pulse 1.5s infinite;"></span>
                    <strong style="color: white; font-size: 1.05rem;">Shield Assistant</strong>
                </div>
                <button id="chatbot-close" style="background: transparent; border: none; color: rgba(255, 255, 255, 0.6); font-size: 1.2rem; cursor: pointer;">&times;</button>
            </div>

            <!-- Messages Area -->
            <div id="chatbot-messages" style="flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; font-size: 0.9rem;">
                <div style="background: rgba(255, 255, 255, 0.05); color: #ffffff; padding: 12px 16px; border-radius: 14px 14px 14px 0; max-width: 85%;">
                    Hello candidate! I am the ProctorShield Assistant. How can I help you prepare or troubleshoot today?
                </div>
            </div>

            <!-- Quick Suggestions -->
            <div id="chatbot-suggestions" style="padding: 10px 15px; display: flex; flex-wrap: wrap; gap: 8px; border-top: 1px solid rgba(255, 255, 255, 0.05); background: rgba(0,0,0,0.2);">
                <button class="chat-sug-btn" data-topic="permissions" style="background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; color: white; padding: 6px 12px; font-size: 0.75rem; cursor: pointer; transition: all 0.2s;">📷 Fix Webcam</button>
                <button class="chat-sug-btn" data-topic="violations" style="background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; color: white; padding: 6px 12px; font-size: 0.75rem; cursor: pointer; transition: all 0.2s;">⚠️ Rules & Violations</button>
                <button class="chat-sug-btn" data-topic="tf" style="background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; color: white; padding: 6px 12px; font-size: 0.75rem; cursor: pointer; transition: all 0.2s;">✔️ True/False Quiz</button>
                <button class="chat-sug-btn" data-topic="analytics" style="background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; color: white; padding: 6px 12px; font-size: 0.75rem; cursor: pointer; transition: all 0.2s;">📊 Analytics Tools</button>
            </div>
        </div>
    `;

    document.body.appendChild(botContainer);

    const toggleBtn = document.getElementById('chatbot-toggle');
    const chatWindow = document.getElementById('chatbot-window');
    const closeBtn = document.getElementById('chatbot-close');
    const msgArea = document.getElementById('chatbot-messages');

    // Toggle Chat visibility
    toggleBtn.addEventListener('click', () => {
        if (chatWindow.style.display === 'none' || !chatWindow.style.display) {
            chatWindow.style.display = 'flex';
            toggleBtn.style.transform = 'scale(0) rotate(90deg)';
        }
    });

    closeBtn.addEventListener('click', () => {
        chatWindow.style.display = 'none';
        toggleBtn.style.transform = 'scale(1) rotate(0deg)';
    });

    // Handle Quick Suggestions clicks
    document.querySelectorAll('.chat-sug-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const topic = btn.getAttribute('data-topic');
            let userMsg = btn.textContent;
            let botReply = '';

            if (topic === 'permissions') {
                botReply = 'To fix camera permissions: click the lock icon to the left of the URL bar in Google Chrome, select Site Settings, and change Camera & Microphone to Allow. Refresh the page to start calibration!';
            } else if (topic === 'violations') {
                botReply = 'ProctorShield tracks: Fullscreen Exits, Tab Switches, Face Missing, Multiple Faces, and Voice Noise levels. Minimizing the browser or looking away repeatedly will flag your attempt as suspicious!';
            } else if (topic === 'tf') {
                botReply = 'Yes! When creating a quiz, teachers can toggle the Question Type between MCQ and True/False. Option C & D will automatically hide and default to empty so candidates only see True and False options.';
            } else if (topic === 'analytics') {
                botReply = 'As a Business Analytics candidate, ProctorShield features custom analytics dashboards for teachers! It aggregates candidate scores, maps class risk distribution models, and visualizes violation frequencies via live Chart.js graphs.';
            }

            // Append User message
            const uDiv = document.createElement('div');
            uDiv.style.alignSelf = 'flex-end';
            uDiv.style.background = 'linear-gradient(135deg, #ff3b5c 0%, #7c3aed 100%)';
            uDiv.style.color = '#ffffff';
            uDiv.style.padding = '10px 14px';
            uDiv.style.borderRadius = '14px 14px 0 14px';
            uDiv.style.maxWidth = '85%';
            uDiv.textContent = userMsg;
            msgArea.appendChild(uDiv);

            // Scroll down
            msgArea.scrollTop = msgArea.scrollHeight;

            // Typing latency animation simulation
            setTimeout(() => {
                const bDiv = document.createElement('div');
                bDiv.style.alignSelf = 'flex-start';
                bDiv.style.background = 'rgba(255, 255, 255, 0.05)';
                bDiv.style.color = '#ffffff';
                bDiv.style.padding = '10px 14px';
                bDiv.style.borderRadius = '14px 14px 14px 0';
                bDiv.style.maxWidth = '85%';
                bDiv.textContent = botReply;
                msgArea.appendChild(bDiv);
                msgArea.scrollTop = msgArea.scrollHeight;
            }, 500);
        });
    });
});
