// chatbot.js
// هذا الملف يحتوي على منطق الدردشة مع الشات بوت.

// 1. تحديد عناصر DOM
const chatBox = document.getElementById('chat-box');
const userInputField = document.getElementById('user-input');
const sendButton = document.querySelector('.chatbot button');

// 2. دالة إرسال الرسالة إلى الشات بوت
async function sendMessage() {
    const userInput = userInputField.value.trim();
    if (!userInput) {
        // لا ترسل رسالة فارغة
        return;
    }

    // 3. إضافة رسالة المستخدم إلى صندوق الدردشة
    appendMessage('أنت', userInput, 'user-message'); // 'user-message' فئة جديدة للتصميم
    userInputField.value = ''; // مسح حقل الإدخال

    // 4. عرض رسالة "جاري المعالجة..."
    const loadingMessageElement = appendMessage('المساعد', 'جاري المعالجة...', 'loading-message'); // 'loading-message' فئة جديدة

    // 5. تمرير صندوق الدردشة للأسفل
    scrollToBottom();

    try {
        // 6. إرسال طلب إلى الواجهة الخلفية (API)
        const response = await fetch('http://localhost:5000/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: userInput })
        });

        // 7. إزالة رسالة "جاري المعالجة..."
        if (loadingMessageElement && loadingMessageElement.parentNode) {
            loadingMessageElement.parentNode.removeChild(loadingMessageElement);
        }

        if (!response.ok) { // التحقق من حالة الاستجابة (مثل 404، 500)
            const errorText = await response.text();
            throw new Error(`خطأ في استجابة الخادم: ${response.status} - ${errorText}`);
        }

        const data = await response.json();

        // 8. إضافة رد الشات بوت إلى صندوق الدردشة
        if (data.response) {
            appendMessage('المساعد', data.response, 'bot-message'); // 'bot-message' فئة جديدة
        } else {
            appendMessage('خطأ', 'لم يتم الحصول على رد مناسب من الشات بوت.', 'error-message');
        }

    } catch (error) {
        console.error('حدث خطأ أثناء التواصل مع الشات بوت:', error);
        // 9. إزالة رسالة "جاري المعالجة..." في حالة وجود خطأ
        if (loadingMessageElement && loadingMessageElement.parentNode) {
            loadingMessageElement.parentNode.removeChild(loadingMessageElement);
        }
        appendMessage('خطأ', 'فشل الاتصال بالشات بوت. يرجى المحاولة مرة أخرى.', 'error-message');
    }

    // 10. تمرير صندوق الدردشة للأسفل مرة أخرى بعد الرد
    scrollToBottom();
}

// 11. دالة مساعدة لإضافة رسالة إلى صندوق الدردشة
function appendMessage(sender, message, className = '') {
    const messageElement = document.createElement('div');
    messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
    if (className) {
        messageElement.classList.add(className);
    }
    chatBox.appendChild(messageElement);
    return messageElement; // إرجاع العنصر المضاف للتحكم فيه لاحقًا (مثل إزالته)
}

// 12. دالة تمرير صندوق الدردشة للأسفل
function scrollToBottom() {
    chatBox.scrollTop = chatBox.scrollHeight;
}

// 13. معالجات الأحداث (Event Listeners)

// عند تحميل محتوى DOM بالكامل
document.addEventListener('DOMContentLoaded', () => {
    // ربط زر الإرسال بوظيفة sendMessage
    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
    }

    // ربط حقل الإدخال بالضغط على Enter لإرسال الرسالة
    if (userInputField) {
        userInputField.addEventListener('keypress', (event) => {
            if (event.key === 'Enter') {
                event.preventDefault(); // منع السلوك الافتراضي لـ Enter (مثل إرسال النموذج)
                sendMessage();
            }
        });
    }

    // رسالة ترحيب أولية
    appendMessage('المساعد', 'مرحبًا بك! كيف يمكنني مساعدتك اليوم؟', 'bot-message');
    scrollToBottom();
});

