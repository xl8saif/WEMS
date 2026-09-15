/* Keep standalone invoice PDF/print views synchronized with the UI language. */
(function () {
  function currentLanguage() {
    return localStorage.getItem('wems-language') || document.documentElement.lang || 'ur';
  }

  function syncInvoiceLinks() {
    const lang = currentLanguage() === 'en' ? 'en' : 'ur';
    document.querySelectorAll('a[href*="/pdf"], a[href*="/print"]').forEach(function (link) {
      try {
        const url = new URL(link.href, window.location.href);
        url.searchParams.set('lang', lang);
        link.href = url.toString();
      } catch (_) {}
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    syncInvoiceLinks();
    window.addEventListener('storage', syncInvoiceLinks);
    const observer = new MutationObserver(syncInvoiceLinks);
    observer.observe(document.body, { childList: true, subtree: true });
  });
})();
