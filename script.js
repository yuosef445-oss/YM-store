// script.js
// هذا الملف يحتوي على منطق سلة المشتريات ووظائف عامة للموقع.

// 1. تحديد عناصر DOM
const cartItemsList = document.getElementById('cart-items');
const checkoutButton = document.querySelector('.cart button');
const navLinks = document.querySelectorAll('nav ul li a');

// 2. وظيفة عرض رسالة مخصصة (بدلاً من alert)
function showMessage(message, type = 'info') {
    // في تطبيق احترافي، ستستخدم هنا مكونًا مرئيًا (مثل مودال أو توست)
    // لعرض الرسائل للمستخدم بدلاً من alert() المزعج.
    // لغرض هذا المثال، سنستخدم console.log ورسالة بسيطة في DOM إذا كان هناك مكان مخصص.
    console.log(`[${type.toUpperCase()}]: ${message}`);

    // يمكنك إضافة عنصر رسالة مؤقت إلى DOM هنا
    const messageContainer = document.createElement('div');
    messageContainer.className = `app-message ${type}`; // ستحتاج إلى تعريف هذه الأنماط في style.css
    messageContainer.textContent = message;
    document.body.appendChild(messageContainer);

    // إزالة الرسالة بعد بضع ثوانٍ
    setTimeout(() => {
        messageContainer.remove();
    }, 3000);
}

// 3. وظيفة تحديث عرض سلة المشتريات
function updateCartDisplay() {
    let cart = [];
    try {
        cart = JSON.parse(localStorage.getItem('cart')) || [];
    } catch (e) {
        console.error("خطأ في تحليل بيانات السلة من التخزين المحلي:", e);
        cart = []; // إعادة تعيين السلة في حالة وجود بيانات تالفة
        showMessage("حدث خطأ في تحميل سلة المشتريات. تم إعادة تعيينها.", "error");
    }

    if (cartItemsList) { // التأكد من وجود العنصر قبل التلاعب به
        cartItemsList.innerHTML = ''; // مسح القائمة الحالية

        if (cart.length === 0) {
            const emptyMessage = document.createElement('p');
            emptyMessage.textContent = 'سلة المشتريات فارغة!';
            cartItemsList.appendChild(emptyMessage);
            if (checkoutButton) {
                checkoutButton.disabled = true; // تعطيل زر الدفع إذا كانت السلة فارغة
            }
        } else {
            cart.forEach(item => {
                const li = document.createElement('li');
                li.textContent = item; // يمكن تحسين هذا لعرض تفاصيل أكثر مثل السعر والكمية
                cartItemsList.appendChild(li);
            });
            if (checkoutButton) {
                checkoutButton.disabled = false; // تفعيل زر الدفع
            }
        }
    }
}

// 4. وظيفة إضافة منتج للسلة
function addToCart(productName) {
    let cart = [];
    try {
        cart = JSON.parse(localStorage.getItem('cart')) || [];
    } catch (e) {
        console.error("خطأ في تحليل بيانات السلة من التخزين المحلي عند الإضافة:", e);
        cart = [];
    }

    cart.push(productName);
    localStorage.setItem('cart', JSON.stringify(cart));
    showMessage(`${productName} تم إضافته إلى سلة المشتريات بنجاح.`, "success");
    updateCartDisplay(); // تحديث العرض بعد الإضافة
}

// 5. وظيفة إتمام الشراء
function checkout() {
    let cart = [];
    try {
        cart = JSON.parse(localStorage.getItem('cart')) || [];
    } catch (e) {
        console.error("خطأ في تحليل بيانات السلة من التخزين المحلي عند الدفع:", e);
        cart = [];
    }

    if (cart.length > 0) {
        // هنا يمكن إضافة منطق معقد لإتمام الشراء، مثل:
        // - إرسال طلب إلى الواجهة الخلفية (API) لمعالجة الطلب.
        // - عرض نموذج دفع.
        // - تأكيد الطلب.
        showMessage("جاري معالجة طلبك...", "info");
        // محاكاة عملية دفع ناجحة
        setTimeout(() => {
            localStorage.removeItem('cart'); // مسح السلة بعد الدفع
            updateCartDisplay(); // تحديث عرض السلة
            showMessage("تم إتمام الشراء بنجاح! شكرًا لك.", "success");
        }, 1500);
    } else {
        showMessage("سلة المشتريات فارغة. لا يمكن إتمام الشراء.", "warning");
    }
}

// 6. وظيفة تحديد الرابط النشط في شريط التنقل
function setActiveNavLink() {
    const currentPath = window.location.pathname.split('/').pop(); // الحصول على اسم الملف الحالي
    navLinks.forEach(link => {
        // إزالة الفئة النشطة من جميع الروابط أولاً
        link.classList.remove("active");
        // إضافة الفئة النشطة إذا كان href يطابق المسار الحالي
        if (link.getAttribute("href") === currentPath) {
            link.classList.add("active");
        }
    });
}

// 7. معالجات الأحداث (Event Listeners)

// عند تحميل محتوى DOM بالكامل
document.addEventListener("DOMContentLoaded", () => {
    setActiveNavLink(); // تحديد الرابط النشط عند تحميل الصفحة

    // ربط معالجات الأحداث لجميع أزرار "إضافة إلى السلة"
    document.querySelectorAll('.product button').forEach(button => {
        button.addEventListener('click', (event) => {
            const productName = event.target.dataset.productName || event.target.previousElementSibling.previousElementSibling.textContent;
            addToCart(productName);
        });
    });

    // ربط معالج الحدث لزر إتمام الشراء (إذا كان موجودًا في الصفحة الحالية)
    if (checkoutButton) {
        checkoutButton.addEventListener('click', checkout);
    }

    // إذا كانت الصفحة الحالية هي سلة المشتريات، قم بتحميل العناصر
    if (window.location.pathname.includes('cart.html')) {
        updateCartDisplay();
    }
});

// ملاحظة: تم إزالة وظائف `window.onload` واستبدالها بـ `DOMContentLoaded`
// لضمان تشغيل الكود بمجرد أن يكون DOM جاهزًا، دون انتظار تحميل جميع الموارد (الصور، إلخ).

