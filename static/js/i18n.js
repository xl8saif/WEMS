/* WEMS offline bilingual UI switcher.
   Database values and business logic remain unchanged.
   This version translates text nodes, labels, placeholders, option values,
   dynamic content and mixed icon/text controls instead of only leaf elements.
*/
(function () {
  const U = {
    'ورق انٹرپرائز مینجمنٹ سسٹم': 'Waraq Enterprise Management System',
    'ورق انٹرپرائزز، گلگت کا منصوبہ': 'A project of Waraq Enterprises, Gilgit',
    'ورق انٹرپرائزز، گلگت': 'Waraq Enterprises, Gilgit',
    'ورق انٹرپرائزز، گلگت — WEMS v1.0': 'Waraq Enterprises, Gilgit — WEMS v1.0',
    'سید سیف اللہ جیلانی': 'Saif Ullah Jailani',
    'سینئر مترجم، لوکلائزیشن اسپیشلسٹ اور لینگویج ٹیکنالوجی ماہر': 'Senior Translator, Localization Specialist & Language Technology Expert',
    '12+ سالہ پیشہ ورانہ تجربہ، 3,500+ منصوبے؛ قانونی، مذہبی، کارپوریٹ، تکنیکی، تعلیمی، میڈیکل، حکومتی اور گیم لوکلائزیشن میں ترجمہ، MTPE، LQA، لسانی جانچ اور کثیر لسانی مواد کی تیاری۔ اردو مادری زبان؛ عربی، فارسی، انگریزی اور علاقائی زبانوں میں عملی مہارت، بشمول انڈس کوہستانی اور شینا۔': '12+ years of professional experience and 3,500+ projects across legal, religious, corporate, technical, educational, medical, government and game localization, including translation, MTPE, LQA, linguistic testing and multilingual content production. Native Urdu speaker with working proficiency in Arabic, Persian, English and regional languages, including Indus-Kohistani and Shina.',
    'Waraq KIU Road، Konodas، Gilgit': 'Waraq KIU Road, Konodas, Gilgit',

    'ڈیش بورڈ': 'Dashboard', 'کلائنٹس': 'Clients', 'کلائنٹ': 'Client', 'کلائنٹ پروفائل': 'Client Profile',
    'کلائنٹ کا نام': 'Client Name', 'کلائنٹ کا نام *': 'Client Name *', 'کلائنٹ کی قسم': 'Client Type',
    'کام اور خدمات': 'Jobs & Services', 'کام': 'Jobs', 'کام کی تفصیلات': 'Job Details', 'نیا کام': 'New Job',
    'کام میں ترمیم': 'Edit Job', 'کام کا عنوان': 'Job Title', 'کام کا عنوان *': 'Job Title *',
    'خدمات': 'Services', 'خدمت': 'Service', 'خدمت کا نام': 'Service Name', 'خدمات کا کیٹلاگ': 'Service Catalog',
    'نئی خدمت شامل کریں': 'Add New Service', 'خدمت میں ترمیم': 'Edit Service',
    'انوائسز': 'Invoices', 'انوائس': 'Invoice', 'نئی انوائس': 'New Invoice', 'نئی انوائس بنائیں': 'Create New Invoice',
    'انوائس کی اشیاء': 'Invoice Items', 'انوائس بنائیں': 'Create Invoice',
    'ادائیگیاں': 'Payments', 'ادائیگی': 'Payment', 'ادائیگیوں کا ریکارڈ': 'Payment Records',
    'ادائیگی درج کریں': 'Record Payment', 'ادائیگیوں کی تاریخ': 'Payment History',
    'رپورٹس': 'Reports', 'کاروباری رپورٹس': 'Business Reports', 'ڈیٹا بیس بیک اَپ': 'Database Backup',
    'تلاش': 'Search', 'صاف کریں': 'Clear', 'شامل کریں': 'Add', 'کلائنٹ شامل کریں': 'Add Client',
    'خدمت شامل کریں': 'Add Service', 'شے شامل کریں': 'Add Item', 'محفوظ کریں': 'Save', 'اپ ڈیٹ کریں': 'Update',
    'منسوخ کریں': 'Cancel', 'ترمیم': 'Edit', 'حذف': 'Delete', 'دیکھیں': 'View', 'سب دیکھیں': 'View All',
    'کارروائیاں': 'Actions', 'پرنٹ': 'Print', 'پرنٹ منظر': 'Print View', 'پی ڈی ایف': 'PDF',
    'پی ڈی ایف محفوظ کریں': 'Save PDF', 'انوائس پرنٹ کریں': 'Print Invoice',

    'کلائنٹس تلاش کریں۔۔۔': 'Search clients...', 'کام تلاش کریں۔۔۔': 'Search jobs...', 'انوائسز تلاش کریں۔۔۔': 'Search invoices...',
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
    'نوٹس': 'Notes', 'کوئی نوٹس نہیں۔': 'No notes.', 'ٹائم لائن': 'Timeline', 'تاریخ': 'Date', 'اجراء': 'Issued',
    'اجراء کی تاریخ': 'Issue Date', 'مقرر نہیں': 'Not set', 'انوائس نمبر': 'Invoice Number', 'متعلقہ کام': 'Related Job',
    'کل': 'Total', 'مقدار': 'Quantity', 'فی یونٹ قیمت': 'Unit Price', 'رقم': 'Amount', 'ذیلی مجموعہ:': 'Subtotal:',
    'ٹیکس:': 'Tax:', 'ٹیکس (0٪):': 'Tax (0%):', 'رعایت:': 'Discount:', 'کل رقم:': 'Total Amount:',
    'ادا شدہ:': 'Paid:', 'قابلِ ادائیگی بقایا:': 'Balance Due:', 'بقایا': 'Outstanding', 'کل بل شدہ': 'Total Billed',
    'کل ادا شدہ': 'Total Paid', 'موصول شدہ': 'Collected', 'موصول شدہ ادائیگیاں': 'Payments Received',
    'کل آمدن': 'Total Revenue', 'بقایا جات': 'Outstanding Balances', 'آمدن کا جائزہ': 'Revenue Overview',
    'حالیہ کام': 'Recent Jobs', 'حالیہ انوائسز': 'Recent Invoices', 'آمدن': 'Revenue', 'وصول شدہ': 'Collected',
    'ادائیگی کی تاریخ': 'Payment Date', 'طریقۂ ادائیگی': 'Payment Method', 'نقد': 'Cash', 'بینک ٹرانسفر': 'Bank Transfer',
    'چیک': 'Cheque', 'آن لائن': 'Online', 'حوالہ نمبر': 'Reference Number', 'حوالہ': 'Reference',
    'کلائنٹس برآمد کریں': 'Export Clients', 'انوائسز برآمد کریں': 'Export Invoices', 'کام برآمد کریں': 'Export Jobs',
    'زمرے کے لحاظ سے آمدن': 'Revenue by Category', 'ماہانہ خلاصہ': 'Monthly Summary', 'ماہ': 'Month',
    'اخراجات کا خلاصہ': 'Expense Summary',

    'کل کلائنٹس': 'Total Clients', 'کل کام': 'Total Jobs', 'کل انوائسز': 'Total Invoices', 'غیر ادا شدہ انوائسز': 'Unpaid Invoices',
    'زیرِ التوا کام': 'Pending Jobs', 'کلائنٹ کی معلومات': 'Client Information', 'کام کی معلومات': 'Job Information',
    'انوائس کی تفصیلات': 'Invoice Details', 'ادائیگی کی تفصیلات': 'Payment Details', 'خدمت کی تفصیلات': 'Service Details',
    'کام کا عنوان': 'Job Title', 'خدمت کی قسم': 'Service Type', 'ذمہ داری': 'Responsibility', 'ذمہ دار': 'Assigned',
    'شروع کریں': 'Start', 'مکمل کریں': 'Complete', 'واپس': 'Back', 'جمع کریں': 'Submit', 'تلاش کریں': 'Search',
    'مینو کھولیں': 'Open menu', 'تیار کردہ:': 'Developed by:', 'تیار کردہ': 'Developed by', 'ویب سائٹ': 'Website', 'پروفائل': 'Profile',

    'کوئی کلائنٹ نہیں ملا۔': 'No clients found.', 'اس کلائنٹ کے لیے کوئی کام موجود نہیں۔': 'No jobs found for this client.',
    'اس کلائنٹ کے لیے کوئی انوائس موجود نہیں۔': 'No invoices found for this client.', 'کوئی کام نہیں ملا۔': 'No jobs found.',
    'ابھی کوئی کام موجود نہیں۔': 'No jobs yet.', 'کوئی انوائس نہیں ملی۔': 'No invoices found.', 'ابھی کوئی انوائس موجود نہیں۔': 'No invoices yet.',
    'ابھی کوئی ادائیگی درج نہیں کی گئی۔': 'No payments recorded yet.', 'اس وقت کوئی بقایا رقم موجود نہیں۔': 'No outstanding balance at this time.',
    'ابھی کوئی خدمت ترتیب نہیں دی گئی۔': 'No services configured yet.', 'دستیاب نہیں': 'Not available', 'آپ کے کاروبار کا شکریہ۔': 'Thank you for your business.',

    'کیا آپ اس کلائنٹ کو حذف کرنا چاہتے ہیں؟': 'Are you sure you want to delete this client?',
    'کیا آپ اس کام کو حذف کرنا چاہتے ہیں؟': 'Are you sure you want to delete this job?',
    'کیا آپ اس انوائس کو حذف کرنا چاہتے ہیں؟': 'Are you sure you want to delete this invoice?',
    'کیا آپ اس خدمت کو حذف کرنا چاہتے ہیں؟': 'Are you sure you want to delete this service?',
    'کلائنٹ کامیابی سے شامل کر دیا گیا۔': 'Client added successfully.', 'کلائنٹ کی معلومات کامیابی سے اپ ڈیٹ کر دی گئیں۔': 'Client information updated successfully.',
    'کلائنٹ کامیابی سے حذف کر دیا گیا۔': 'Client deleted successfully.', 'سروس کامیابی سے شامل کر دی گئی۔': 'Service added successfully.',
    'سروس کامیابی سے اپ ڈیٹ کر دی گئی۔': 'Service updated successfully.', 'سروس کامیابی سے حذف کر دی گئی۔': 'Service deleted successfully.',
    'کام کامیابی سے بنا دیا گیا۔': 'Job created successfully.', 'کام کامیابی سے اپ ڈیٹ کر دیا گیا۔': 'Job updated successfully.',
    'کام کامیابی سے حذف کر دیا گیا۔': 'Job deleted successfully.', 'ادائیگی کامیابی سے درج کر دی گئی۔': 'Payment recorded successfully.',
    'انوائس کامیابی سے حذف کر دی گئی۔': 'Invoice deleted successfully.', 'پی ڈی ایف تیار کرتے وقت خرابی پیش آئی۔': 'Error generating PDF.',

    '-- کوئی نہیں --': '-- None --', '-- کلائنٹ منتخب کریں --': '-- Select Client --', '-- خدمت منتخب کریں --': '-- Select Service --',
    'تمام خدمات': 'All Services', 'تمام ادائیگیاں': 'All Payments', 'تمام حیثیتیں': 'All Statuses', 'تمام ترجیحات': 'All Priorities',
    'فرد': 'Individual', 'کاروبار': 'Business', 'حکومت': 'Government', 'مقامی': 'Local', 'بین الاقوامی': 'International',
    'درمیانہ': 'Medium', 'فعال': 'Active', 'غیر فعال': 'Inactive', 'ہاں': 'Yes', 'نہیں': 'No',
    'کلائنٹ محفوظ کریں': 'Save Client', 'کلائنٹ اپ ڈیٹ کریں': 'Update Client', 'کام محفوظ کریں': 'Save Job', 'کام اپ ڈیٹ کریں': 'Update Job',
    'خدمت محفوظ کریں': 'Save Service', 'خدمت اپ ڈیٹ کریں': 'Update Service', 'انوائس محفوظ کریں': 'Save Invoice',
    'ادائیگی محفوظ کریں': 'Save Payment', 'ادائیگی درج کریں': 'Record Payment',
    'انوائس نمبر': 'Invoice Number', 'انوائس کی تاریخ': 'Invoice Date', 'ادائیگی کی آخری تاریخ': 'Payment Due Date',
    'کل رقم': 'Total Amount', 'بقایا رقم': 'Balance Due', 'رعایت': 'Discount', 'ٹیکس': 'Tax', 'ذیلی مجموعہ': 'Subtotal',
    'رقم': 'Amount', 'شرح': 'Rate', 'فی یونٹ': 'Per Unit', 'اشیاء': 'Items', 'آئٹمز': 'Items',
    'ادائیگی کا طریقہ': 'Payment Method', 'ادائیگی کی رقم': 'Payment Amount', 'حوالہ نمبر': 'Reference Number',
    'ادائیگی کی تاریخ': 'Payment Date', 'ادائیگی کی تفصیل': 'Payment Description',
    'برآمد کریں': 'Export', 'بیک اَپ': 'Backup', 'بحال کریں': 'Restore', 'ڈاؤن لوڈ': 'Download',
    'خلاصہ': 'Summary', 'رپورٹ': 'Report', 'ماہانہ': 'Monthly', 'سالانہ': 'Annual', 'زمرہ': 'Category',
    'جنوری': 'January', 'فروری': 'February', 'مارچ': 'March', 'اپریل': 'April', 'مئی': 'May', 'جون': 'June',
    'جولائی': 'July', 'اگست': 'August', 'ستمبر': 'September', 'اکتوبر': 'October', 'نومبر': 'November', 'دسمبر': 'December'
  };

  const E = Object.fromEntries(Object.entries(U).map(([u, e]) => [e, u]));
  const makePairs = map => Object.entries(map).sort((a, b) => b[0].length - a[0].length);
  const UR_PAIRS = makePairs(U);
  const EN_PAIRS = makePairs(E);
  let currentLang = localStorage.getItem('wems-language') || 'ur';
  let translating = false;

  function translateString(value, lang) {
    let out = String(value == null ? '' : value);
    const entries = lang === 'en' ? UR_PAIRS : EN_PAIRS;
    entries.forEach(([from, to]) => {
      if (from && out.includes(from)) out = out.split(from).join(to);
    });
    if (lang === 'en') {
      out = out.replace(/انوائس\s+(.+?)\s+کامیابی سے بنا دی گئی۔/g, 'Invoice $1 created successfully.');
      out = out.replace(/ڈیٹا بیس کا بیک اَپ کامیابی سے بنا دیا گیا۔/g, 'Database backup created successfully.');
    } else {
      out = out.replace(/Invoice\s+(.+?)\s+created successfully\./g, 'انوائس $1 کامیابی سے بنا دی گئی۔');
      out = out.replace(/Database backup created successfully\./g, 'ڈیٹا بیس کا بیک اَپ کامیابی سے بنا دیا گیا۔');
    }
    return out;
  }

  function translateTextNode(node, lang) {
    const text = node.nodeValue;
    if (!text || !text.trim()) return;
    const translated = translateString(text, lang);
    if (translated !== text) node.nodeValue = translated;
  }

  function translateElement(el, lang) {
    if (!el || el.nodeType !== 1) return;
    if (el.matches('script,style,svg,path')) return;

    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        const parent = node.parentElement;
        if (!parent || parent.closest('script,style,svg')) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    const nodes = [];
    let node;
    while ((node = walker.nextNode())) nodes.push(node);
    nodes.forEach(n => translateTextNode(n, lang));

    ['placeholder', 'title', 'aria-label', 'data-tooltip'].forEach(attr => {
      document.querySelectorAll('[' + attr + ']').forEach(item => {
        const value = item.getAttribute(attr);
        const translated = translateString(value, lang);
        if (translated !== value) item.setAttribute(attr, translated);
      });
    });

    document.querySelectorAll('input,textarea').forEach(item => {
      if (item.type !== 'text' && item.type !== 'search' && item.type !== 'button' && item.type !== 'submit') return;
      const value = item.value;
      if (value) {
        const translated = translateString(value, lang);
        if (translated !== value) item.value = translated;
      }
    });
  }

  function applyLanguage(lang) {
    if (translating) return;
    translating = true;
    currentLang = lang === 'en' ? 'en' : 'ur';
    document.documentElement.lang = currentLang;
    document.documentElement.dir = currentLang === 'en' ? 'ltr' : 'rtl';
    document.body.classList.toggle('wems-english', currentLang === 'en');

    const observer = window.__wemsI18nObserver;
    if (observer) observer.disconnect();

    document.title = translateString(document.title, currentLang);
    translateElement(document.body, currentLang);
    document.querySelectorAll('[data-lang-label]').forEach(el => {
      el.textContent = currentLang === 'en' ? 'اردو' : 'English';
    });

    localStorage.setItem('wems-language', currentLang);
    translating = false;

    if (observer) observer.observe(document.body, { childList: true, subtree: true });
  }

  function init() {
    const btn = document.getElementById('languageToggle');
    if (btn) btn.addEventListener('click', () => applyLanguage(currentLang === 'en' ? 'ur' : 'en'));

    const observer = new MutationObserver(mutations => {
      if (translating || currentLang !== 'en') return;
      const targets = [];
      mutations.forEach(m => {
        m.addedNodes.forEach(n => {
          if (n.nodeType === Node.TEXT_NODE) translateTextNode(n, currentLang);
          else if (n.nodeType === Node.ELEMENT_NODE) targets.push(n);
        });
      });
      targets.forEach(n => translateElement(n, currentLang));
    });
    window.__wemsI18nObserver = observer;
    observer.observe(document.body, { childList: true, subtree: true });

    if (currentLang === 'en') applyLanguage('en');
    else {
      document.documentElement.lang = 'ur';
      document.documentElement.dir = 'rtl';
      document.querySelectorAll('[data-lang-label]').forEach(el => { el.textContent = 'English'; });
    }
  }

  document.addEventListener('DOMContentLoaded', init);
})();
