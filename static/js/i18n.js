/* WEMS offline bilingual UI switcher. Database values, URLs and business logic remain unchanged. */
(function () {
  const U = {
    'ورق انٹرپرائز مینجمنٹ سسٹم': 'Waraq Enterprise Management System',
    'ورق انٹرپرائزز، گلگت کا منصوبہ': 'A project of Waraq Enterprises, Gilgit',
    'ورق انٹرپرائزز، گلگت': 'Waraq Enterprises, Gilgit',
    'ڈیش بورڈ': 'Dashboard', 'کلائنٹس': 'Clients', 'کلائنٹ': 'Client',
    'کام اور خدمات': 'Jobs & Services', 'کام': 'Jobs', 'نیا کام': 'New Job',
    'خدمات': 'Services', 'خدمت': 'Service', 'انوائسز': 'Invoices', 'انوائس': 'Invoice',
    'ادائیگیاں': 'Payments', 'ادائیگی': 'Payment', 'رپورٹس': 'Reports',
    'ڈیٹا بیس بیک اَپ': 'Database Backup', 'تلاش': 'Search', 'صاف کریں': 'Clear',
    'شامل کریں': 'Add', 'کلائنٹ شامل کریں': 'Add Client', 'محفوظ کریں': 'Save',
    'اپ ڈیٹ کریں': 'Update', 'منسوخ کریں': 'Cancel', 'ترمیم': 'Edit', 'حذف': 'Delete',
    'دیکھیں': 'View', 'سب دیکھیں': 'View All', 'شناختی نمبر': 'ID', 'نام': 'Name',
    'رابطہ فرد': 'Contact Person', 'فون': 'Phone', 'فون نمبر': 'Phone Number',
    'ای میل': 'Email', 'پتہ': 'Address', 'قسم': 'Type', 'تمام اقسام': 'All Types',
    'فرد': 'Individual', 'کاروباری ادارہ': 'Business', 'سرکاری ادارہ': 'Government',
    'کام کا عنوان': 'Job Title', 'کام کا عنوان *': 'Job Title *', 'زمرہ': 'Category',
    'تمام زمرے': 'All Categories', 'قانونی مسودہ نویسی': 'Legal Drafting',
    'عدالتی خدمات': 'Court Services', 'طباعت': 'Printing', 'آن لائن رجسٹریشن': 'Online Registration',
    'دستاویزی خدمات': 'Documentation Services', 'دیگر': 'Other', 'حیثیت': 'Status',
    'تمام حیثیتیں': 'All Statuses', 'زیرِ التوا': 'Pending', 'جاری ہے': 'In Progress',
    'مکمل': 'Completed', 'منسوخ': 'Cancelled', 'ترجیح': 'Priority', 'کم': 'Low',
    'معمول': 'Normal', 'زیادہ': 'High', 'فوری': 'Urgent', 'لاگت': 'Cost',
    'آخری تاریخ': 'Due Date', 'آغاز کی تاریخ': 'Start Date', 'تخمینی لاگت': 'Estimated Cost',
    'ذمہ دار فرد': 'Assigned To', 'تفصیل': 'Description', 'نوٹس': 'Notes',
    'خدمت منتخب کریں': 'Select Service', 'بل برائے:': 'Bill To:', 'اجراء': 'Issued',
    'اجراء کی تاریخ': 'Issue Date', 'آخری تاریخ:': 'Due Date:', 'مقرر نہیں': 'Not set',
    'انوائس نمبر': 'Invoice Number', 'مقدار': 'Quantity', 'فی یونٹ قیمت': 'Unit Price',
    'رقم': 'Amount', 'ذیلی مجموعہ:': 'Subtotal:', 'ٹیکس:': 'Tax:', 'رعایت:': 'Discount:',
    'کل رقم:': 'Total:', 'ادا شدہ:': 'Paid:', 'قابلِ ادائیگی بقایا:': 'Balance Due:',
    'بقایا': 'Outstanding', 'کل بل شدہ': 'Total Billed', 'کل ادا شدہ': 'Total Paid',
    'ادائیگی درج کریں': 'Record Payment', 'ادائیگی کی تاریخ': 'Payment Date',
    'طریقۂ ادائیگی': 'Payment Method', 'نقد': 'Cash', 'بینک ٹرانسفر': 'Bank Transfer',
    'چیک': 'Cheque', 'آن لائن': 'Online', 'حوالہ نمبر': 'Reference Number',
    'ادائیگیوں کی تاریخ': 'Payment History', 'آمدن کا جائزہ': 'Revenue Overview',
    'موصول شدہ': 'Collected', 'موصول شدہ ادائیگیاں': 'Payments Received', 'کل آمدن': 'Total Revenue',
    'بقایا جات': 'Outstanding Balances', 'حالیہ کام': 'Recent Jobs', 'حالیہ انوائسز': 'Recent Invoices',
    'پرنٹ منظر': 'Print View', 'پی ڈی ایف حاصل کریں': 'Save PDF', 'انوائس پرنٹ کریں': 'Print Invoice',
    'مجاز دستخط': 'Authorized Signature', 'ادارے کی مہر': 'Official Stamp',
    'تیار کردہ:': 'Developed by:', 'تیار کردہ': 'Developed by', 'ویب سائٹ': 'Website',
    'پروفائل': 'Profile', 'کل کلائنٹس': 'Total Clients', 'کل کام': 'Total Jobs',
    'کل انوائسز': 'Total Invoices', 'غیر ادا شدہ انوائسز': 'Unpaid Invoices',
    'زیرِ التوا کام': 'Pending Jobs', 'اس وقت کوئی بقایا رقم موجود نہیں۔': 'No outstanding balance at this time.',
    'ابھی کوئی کام موجود نہیں۔': 'No jobs yet.', 'ابھی کوئی انوائس موجود نہیں۔': 'No invoices yet.',
    'کوئی کلائنٹ نہیں ملا۔': 'No clients found.', 'کوئی کام نہیں ملا۔': 'No jobs found.',
    'دستیاب نہیں': 'Not available', 'آپ کے کاروبار کا شکریہ۔': 'Thank you for your business.',
    'کلائنٹ کامیابی سے شامل کر دیا گیا۔': 'Client added successfully.',
    'کلائنٹ کی معلومات کامیابی سے اپ ڈیٹ کر دی گئیں۔': 'Client information updated successfully.',
    'کلائنٹ کامیابی سے حذف کر دیا گیا۔': 'Client deleted successfully.',
    'سروس کامیابی سے شامل کر دی گئی۔': 'Service added successfully.',
    'سروس کامیابی سے اپ ڈیٹ کر دی گئی۔': 'Service updated successfully.',
    'سروس کامیابی سے حذف کر دی گئی۔': 'Service deleted successfully.',
    'کام کامیابی سے بنا دیا گیا۔': 'Job created successfully.', 'کام کامیابی سے اپ ڈیٹ کر دیا گیا۔': 'Job updated successfully.',
    'کام کامیابی سے حذف کر دیا گیا۔': 'Job deleted successfully.', 'ادائیگی کامیابی سے درج کر دی گئی۔': 'Payment recorded successfully.',
    'انوائس کامیابی سے حذف کر دی گئی۔': 'Invoice deleted successfully.', 'پی ڈی ایف تیار کرتے وقت خرابی پیش آئی۔': 'Error generating PDF.'
  };
  const E = Object.fromEntries(Object.entries(U).map(([u, e]) => [e, u]));
  const pairs = Object.entries(U).sort((a,b) => b[0].length - a[0].length);

  function translateString(value, map) {
    let out = value;
    const entries = map === U ? pairs : Object.entries(E).sort((a,b) => b[0].length - a[0].length);
    entries.forEach(([from, to]) => { if (out.includes(from)) out = out.split(from).join(to); });
    return out;
  }

  function translate(lang) {
    document.documentElement.lang = lang === 'en' ? 'en' : 'ur';
    document.documentElement.dir = lang === 'en' ? 'ltr' : 'rtl';
    document.body.classList.toggle('wems-english', lang === 'en');
    document.querySelectorAll('[data-lang-label]').forEach(el => el.textContent = lang === 'en' ? 'اردو' : 'English');

    document.querySelectorAll('body *:not(script):not(style)').forEach(el => {
      if (el.children.length === 0 && el.textContent.trim()) el.textContent = translateString(el.textContent, lang === 'en' ? U : E);
      ['placeholder','title','aria-label'].forEach(attr => {
        if (el.hasAttribute(attr)) el.setAttribute(attr, translateString(el.getAttribute(attr), lang === 'en' ? U : E));
      });
    });
    localStorage.setItem('wems-language', lang);
  }

  function init() {
    const btn = document.getElementById('languageToggle');
    if (btn) btn.addEventListener('click', () => translate(document.documentElement.lang === 'en' ? 'ur' : 'en'));
    const saved = localStorage.getItem('wems-language') || 'ur';
    if (saved === 'en') translate('en');
  }
  document.addEventListener('DOMContentLoaded', init);
})();
