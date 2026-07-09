/**
 * MediSphere AI — Frontend JavaScript
 * Built by Zarak Khan
 */

document.addEventListener('DOMContentLoaded', function() {
  const chatMessages = document.getElementById('chatMessages');
  const messageInput = document.getElementById('messageInput');
  const sendBtn = document.getElementById('sendBtn');
  const typingIndicator = document.getElementById('typingIndicator');
  const welcomeTime = document.getElementById('welcomeTime');

  // Set welcome message time
  if (welcomeTime) {
    welcomeTime.textContent = formatTime(new Date());
  }

  // Quick action buttons
  const quickButtons = document.querySelectorAll('.action-card');
  quickButtons.forEach(btn => {
    btn.addEventListener('click', function() {
      const action = this.dataset.action;
      handleQuickAction(action);
    });
  });

  // Send on button click
  sendBtn.addEventListener('click', sendMessage);

  // Send on Enter key
  messageInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
      sendMessage();
    }
  });

  // Focus input on load
  messageInput.focus();

  function handleQuickAction(action) {
    const messages = {
      register: 'register my name is ',
      appointment: 'book appointment with Dr. ',
      report: 'check my report',
      queue: 'my token status',
      emergency: 'emergency contact'
    };

    messageInput.value = messages[action] || '';
    messageInput.focus();

    // Highlight button briefly
    const btn = document.querySelector(`[data-action="${action}"]`);
    if (btn) {
      btn.style.borderColor = 'var(--accent)';
      setTimeout(() => {
        btn.style.borderColor = '';
      }, 800);
    }
  }

  async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    // Add user message
    addUserMessage(message);
    messageInput.value = '';
    messageInput.focus();

    // Show typing
    showTyping();

    try {
      const response = await fetch('/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: message,
          user_id: 'user_' + getSessionId()
        })
      });

      const data = await response.json();

      // Hide typing
      hideTyping();

      if (data.status === 'error') {
        addAgentMessage(data.message, 'System', 'error');
      } else {
        addAgentMessage(
          data.message,
          data.agent || 'MediSphere AI',
          data.intent || 'response'
        );
      }
    } catch (error) {
      hideTyping();
      addAgentMessage(
        'Sorry, I encountered an error. Please try again.',
        'System',
        'error'
      );
      console.error('Chat error:', error);
    }
  }

  function addUserMessage(text) {
    const div = document.createElement('div');
    div.className = 'message message-user';
    div.innerHTML = `
      <div class="message-avatar">👤</div>
      <div class="message-content">
        <div class="message-header">
          <span class="message-sender">You</span>
        </div>
        <div class="message-body">
          <p>${escapeHtml(text)}</p>
        </div>
        <div class="message-time">${formatTime(new Date())}</div>
      </div>
    `;
    chatMessages.appendChild(div);
    scrollToBottom();
  }

  function addAgentMessage(text, agentName, intent) {
    const agentIcons = {
      'PatientRegistrationAgent': '📝',
      'AppointmentBookingAgent': '📅',
      'FAQGuidanceAgent': '❓',
      'ReportQueueAgent': '📄',
      'MasterOrchestrator': '🤖',
      'System': '⚠️',
      'MediSphere AI': '🤖'
    };

    const icon = agentIcons[agentName] || '🤖';

    const div = document.createElement('div');
    div.className = 'message message-agent';
    div.innerHTML = `
      <div class="message-avatar">${icon}</div>
      <div class="message-content">
        <div class="message-header">
          <span class="message-sender">${escapeHtml(agentName)}</span>
          <span class="message-badge">${escapeHtml(intent)}</span>
        </div>
        <div class="message-body">
          ${formatMessage(text)}
        </div>
        <div class="message-time">${formatTime(new Date())}</div>
      </div>
    `;
    chatMessages.appendChild(div);
    scrollToBottom();
  }

  function showTyping() {
    typingIndicator.classList.add('active');
    scrollToBottom();
  }

  function hideTyping() {
    typingIndicator.classList.remove('active');
  }

  function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function formatTime(date) {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });
  }

  function formatMessage(text) {
    if (!text) return '<p></p>';
    
    const lines = text.split('\n');
    let html = '';
    let inList = false;

    lines.forEach(line => {
      const trimmed = line.trim();
      if (!trimmed) return;

      // Check for list items
      if (trimmed.startsWith('•') || trimmed.startsWith('-') || trimmed.startsWith('*')) {
        if (!inList) {
          html += '<ul>';
          inList = true;
        }
        html += `<li>${escapeHtml(trimmed.substring(1).trim())}</li>`;
      } else {
        if (inList) {
          html += '</ul>';
          inList = false;
        }

        // Bold text before colon
        if (trimmed.includes(':') && !trimmed.startsWith('http')) {
          const parts = trimmed.split(':');
          if (parts.length >= 2 && parts[0].length < 50) {
            const label = parts[0].trim();
            const rest = parts.slice(1).join(':').trim();
            html += `<p><strong>${escapeHtml(label)}:</strong> ${escapeHtml(rest)}</p>`;
          } else {
            html += `<p>${escapeHtml(trimmed)}</p>`;
          }
        } else {
          html += `<p>${escapeHtml(trimmed)}</p>`;
        }
      }
    });

    if (inList) {
      html += '</ul>';
    }

    return html;
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function getSessionId() {
    let sessionId = localStorage.getItem('medisphere_session');
    if (!sessionId) {
      sessionId = 'sess_' + Math.random().toString(36).substring(2, 15);
      localStorage.setItem('medisphere_session', sessionId);
    }
    return sessionId;
  }
});