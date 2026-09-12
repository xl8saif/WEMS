/* WEMS offline bilingual UI switcher. UI text is translated; database values and business logic remain unchanged. */
(function () {
  const U = {
    'ورق انٹرپرائز مینجمنٹ سسٹم': 'Waraq Enterprise Management System',
    'ورق انٹرپرائزز، گلگت کا منصوبہ': 'A project of Waraq Enterprises, Gilgit',
    'ورق انٹرپرائزز، گلگت': 'Waraq Enterprises, Gilgit',
    'ورق انٹرپرائزز، گلگت — WEMS v1.0': 'Waraq Enterprises, Gilgit — WEMS v1.0',
    'سید سیف اللہ جیلانی': 'Saif Ullah Jailani',
    'سینئر مترجم، لوکلائزیشن اسپیشلسٹ اور لینگویج ٹیکنالوجی ماہر': 'Senior Translator, Localization Specialist & Language Technology Expert',
    'ڈیش بورڈ': 'Dashboard', 'کلائنٹس': 'Clients', 'کلائنٹ': 'Client',
    'کلائنٹ پروفائل': 'Client Profile', 'کلائنٹ کا نام *': 'Client Name *', 'کلائنٹ کی قسم': 'Client Type',
    'کام اور خدمات': 'Jobs & Services', 'کام': 'Jobs', 'کام کی تفصیلات': 'Job Details', 'نیا کام': 'New Job',
    'کام میں ترمیم': 'Edit Job', 'کام کا عنوان': 'Job Title', 'کام کا عنوان *': 'Job Title *',
    'خدمات': 'Services', 'خدمت': 'Service', 'خدمت کا نام': 'Service Name', 'خدمات کا کیٹلاگ': 'Service Catalog',
    'نئی خدمت شامل کریں': 'Add New Service', 'خدمت میں ترمیم': 'Edit Service',
    'انوائسز': 'Invoices', 'انوائس': 'Invoice', 'نئی انوائس': 'New Invoice', 'نئی انوائس بنائیں': 'Create New Invoice',
    'انوائس کی اشیاء': 'Invoice Items', 'انوائس بنائیں': 'Create Invoice',
    'ادائیگیاں': 'Payments', 'ادائیگی': 'Payment', 'ادائیگیوں کا ریکارڈ': 'Payment Records',
    'ادائیگی درج کریں': 'Record Payment', 'ادائیگیوں کی تاریخ': 'Payment History',
    'رپورٹس': 'Reports', 'کاروباری رپورٹس': 'Business Reports',
    'ڈیٹا بیس بیک اَپ': 'Database Backup', 'تلاش': 'Search', 'صاف کریں': 'Clear',
    'کلائنٹس تلاش کریں۔۔۔': 'Search clients...', 'کام تلاش کریں۔۔۔': 'Search jobs...', 'انوائسز تلاش کریں۔۔۔': 'Search invoices...',
    'شامل کریں': 'Add', 'کلائنٹ شامل کریں': 'Add Client', 'خدمت شامل کریں': 'Add Service', 'شے شامل کریں': 'Add Item',
    'محفوظ کریں': 'Save', 'اپ ڈیٹ کریں': 'Update', 'منسوخ کریں': 'Cancel', 'ترمیم': 'Edit', 'حذف': 'Delete',
    'دیکھیں': 'View', 'سب دیکھیں': 'View All', 'کارروائیاں': 'Actions', 'پرنٹ': 'Print', 'پرنٹ منظر': 'Print View',
    'پی ڈی ایف': 'PDF', 'پی ڈی ایف محفوظ کریں': 'Save PDF', 'انوائس پرنٹ کریں': 'Print Invoice',
    'شناختی نمبر': 'ID', 'شناختی کارڈ / شناختی نمبر': 'CNIC / ID Number', 'نام': 'Name', 'رابطہ فرد': 'Contact Person',
    'فون': 'Phone', 'فون نمبر': 'Phone Number', 'ای میل': 'Email', 'پتہ': 'Address', 'قسم': 'Type',
    'تمام اقسام': 'All Types', 'فرد': 'Individual', 'کاروباری ادارہ': 'Business', 'سرکاری ادارہ': 'Government',
    'زمرہ': 'Category', 'تمام زمرے': 'All Categories', 'قانونی مسودہ نویسی': 'Legal Drafting',
    'عدالتی خدمات': 'Court Services', 'طباعت': 'Printing', 'آن لائن رجسٹریشن': 'Online Registration',
    'دستاویزی خدمات': 'Documentation Services', 'دیگر': 'Other',
    'حیثیت': 'Status', 'تمام حیثیتیں': 'All Statuses', 'ادا شدہ': 'Paid', 'غیر ادا شدہ': 'Unpaid',
    'جزوی ادائیگی': 'Partially Paid', 'زیرِ التوا': 'Pending', 'جاری ہے': 'In Progress', 'مکمل': 'Completed', 'منسوخ': 'Cancelled',
    'ترجیح': 'Priority', 'کم': 'Low', 'معمول': 'Normal', 'زیادہ': 'High', 'فوری': 'Urgent',
    'لاگت': 'Cost', 'تخمینی لاگت': 'Estimated Cost', 'آخری تاریخ': 'Due Date', 'آغاز کی تاریخ': 'Start Date',
    'ادائیگی کی آخری تاریخ': 'Payment Due Date', 'تکمیل کی تاریخ': 'Completion Date', 'ذمہ دار فرد': 'Assigned To',
    'متعین نہیں': 'Not assigned', 'ابھی مکمل نہیں ہوا': 'Not completed yet', 'بنایا گیا': 'Created',
    'تفصیل': 'Description', 'کوئی تفصیل فراہم نہیں کی گئی۔': 'No description provided.', 'کوئی تفصیل موجود نہیں۔': 'No description available.',
    'نوٹس': 'Notes', 'کوئی نوٹس نہیں۔': 'No notes.', 'تاریخ': 'Date', 'اجراء': 'Issued', 'اجراء کی تاریخ': 'Issue Date',
    'مقرر نہیں': 'Not set', 'انوائس نمبر': 'Invoice Number', 'متعلقہ کام': 'Related Job', 'کل': 'Total',
    'مقدار': 'Quantity', 'فی یونٹ قیمت': 'Unit Price', 'رقم': 'Amount', 'ذیلی مجموعہ:': 'Subtotal:', 'ٹیکس:': 'Tax:',
    'ٹیکس (0٪):': 'Tax (0%):', 'رعایت:': 'Discount:', 'کل رقم:': 'Total Amount:', 'ادا شدہ:': 'Paid:',
    'قابلِ ادائیگی بقایا:': 'Balance Due:', 'بقایا': 'Outstanding', 'کل بل شدہ': 'Total Billed', 'کل ادا شدہ': 'Total Paid',
    'موصول شدہ': 'Collected', 'موصول شدہ ادائیگیاں': 'Payments Received', 'کل آمدن': 'Total Revenue',
    'بقایا جات': 'Outstanding Balances', 'آمدن کا جائزہ': 'Revenue Overview', 'حالیہ کام': 'Recent Jobs', 'حالیہ انوائسز': 'Recent Invoices',
    'ادائیگی کی تاریخ': 'Payment Date', 'طریقۂ ادائیگی': 'Payment Method', 'نقد': 'Cash', 'بینک ٹرانسفر': 'Bank Transfer',
    'چیک': 'Cheque', 'آن لائن': 'Online', 'حوالہ نمبر': 'Reference Number', 'حوالہ': 'Reference',
    'کلائنٹس برآمد کریں': 'Export Clients', 'انوائسز برآمد کریں': 'Export Invoices', 'کام برآمد کریں': 'Export Jobs',
    'زمرے کے لحاظ سے آمدن': 'Revenue by Category', 'ماہانہ خلاصہ': 'Monthly Summary', 'ماہ': 'Month', 'وصول شدہ': 'Collected',
    'اخراجات کا خلاصہ': 'Expense Summary', 'کل رقم': 'Total Amount',
    'کوئی کلائنٹ نہیں ملا۔': 'No clients found.', 'اس کلائنٹ کے لیے کوئی کام موجود نہیں۔': 'No jobs found for this client.',
    'اس کلائنٹ کے لیے کوئی انوائس موجود نہیں۔': 'No invoices found for this client.', 'کوئی کام نہیں ملا۔': 'No jobs found.',
    'ابھی کوئی کام موجود نہیں۔': 'No jobs yet.', 'کوئی انوائس نہیں ملی۔': 'No invoices found.', 'ابھی کوئی انوائس موجود نہیں۔': 'No invoices yet.',
    'ابھی کوئی ادائیگی درج نہیں کی گئی۔': 'No payments recorded yet.', 'اس وقت کوئی بقایا رقم موجود نہیں۔': 'No outstanding balance at this time.',
    'ابھی کوئی خدمت ترتیب نہیں دی گئی۔': 'No services configured yet.',
    'دستیاب نہیں': 'Not available', 'آپ کے کاروبار کا شکریہ۔': 'Thank you for your business.',
    'کیا آپ اس کلائنٹ کو حذف کرنا چاہتے ہیں؟': 'Are you sure you want to delete this client?',
    'کیا آپ اس کام کو حذف کرنا چاہتے ہیں؟': 'Are you sure you want to delete this job?',
    'کیا آپ اس انوائس کو حذف کرنا چاہتے ہیں؟': 'Are you sure you want to delete this invoice?',
    'کیا آپ اس خدمت کو حذف کرنا چاہتے ہیں؟': 'Are you sure you want to delete this service?',
    'کلائنٹ کامیابی سے شامل کر دیا گیا۔': 'Client added successfully.',
    'کلائنٹ کی معلومات کامیابی سے اپ ڈیٹ کر دی گئیں۔': 'Client information updated successfully.',
    'کلائنٹ کامیابی سے حذف کر دیا گیا۔': 'Client deleted successfully.',
    'سروس کامیابی سے شامل کر دی گئی۔': 'Service added successfully.', 'سروس کامیابی سے اپ ڈیٹ کر دی گئی۔': 'Service updated successfully.',
    'سروس کامیابی سے حذف کر دی گئی۔': 'Service deleted successfully.', 'کام کامیابی سے بنا دیا گیا۔': 'Job created successfully.',
    'کام کامیابی سے اپ ڈیٹ کر دیا گیا۔': 'Job updated successfully.', 'کام کامیابی سے حذف کر دیا گیا۔': 'Job deleted successfully.',
    'ادائیگی کامیابی سے درج کر دی گئی۔': 'Payment recorded successfully.', 'انوائس کامیابی سے حذف کر دی گئی۔': 'Invoice deleted successfully.',
    'پی ڈی ایف تیار کرتے وقت خرابی پیش آئی۔': 'Error generating PDF.',
    'تیار کردہ:': 'Developed by:', 'تیار کردہ': 'Developed by', 'ویب سائٹ': 'Website', 'پروفائل': 'Profile',
    'کل کلائنٹس': 'Total Clients', 'کل کام': 'Total Jobs', 'کل انوائسز': 'Total Invoices', 'غیر ادا شدہ انوائسز': 'Unpaid Invoices',
    'زیرِ التوا کام': 'Pending Jobs', 'مینو کھولیں': 'Open menu', 'English': 'English'
  };

  const E = Object.fromEntries(Object.entries(U).map(([u, e]) => [e, u]));
  const pairs = Object.entries(U).sort((a, b) => b[0].length - a[0].length);

  function translateString(value, map) {
    let out = String(value);
    const entries = map === U ? pairs : Object.entries(E).sort((a, b) => b[0].length - a[0].length);
    entries.forEach(([from, to]) => { if (out.includes(from)) out = out.split(from).join(to); });
    return out;
  }

  function translate(lang) {
    const isEnglish = lang === 'en';
    document.documentElement.lang = isEnglish ? 'en' : 'ur';
    document.documentElement.dir = isEnglish ? 'ltr' : 'rtl';
    document.body.classList.toggle('wems-english', isEnglish);

    document.querySelectorAll('[data-lang-label]').forEach(el => {
      el.textContent = isEnglish ? 'اردو' : 'English';
    });

    // Translate page title as well as visible UI text.
    document.title = translateString(document.title, isEnglish ? U : E);

    document.querySelectorAll('body *:not(script):not(style)').forEach(el => {
      if (el.children.length === 0 && el.textContent.trim()) {
        el.textContent = translateString(el.textContent, isEnglish ? U : E);
      }
      ['placeholder', 'title', 'aria-label'].forEach(attr => {
        if (el.hasAttribute(attr)) {
          el.setAttribute(attr, translateString(el.getAttribute(attr), isEnglish ? U : E));
        }
      });
    });

    // Native confirmation dialogs are stored in onsubmit attributes.
    document.querySelectorAll('[onsubmit]').forEach(el => {
      el.setAttribute('onsubmit', translateString(el.getAttribute('onsubmit'), isEnglish ? U : E));
    });

    // Keep language preference between pages.
    localStorage.setItem('wems-language', lang);
  }

  function init() {
    const btn = document.getElementById('languageToggle');
    if (btn) btn.addEventListener('click', () => {
      translate(document.documentElement.lang === 'en' ? 'ur' : 'en');
    });
    const saved = localStorage.getItem('wems-language') || 'ur';
    if (saved === 'en') translate('en');
  }

  document.addEventListener('DOMContentLoaded', init);
})();
