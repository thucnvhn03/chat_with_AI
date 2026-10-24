/* Chuyển trạng thái xem mẫu. Không thuộc sản phẩm: chỉ để duyệt các trạng thái thiết kế (UIUX_Blueprint mục 3.7).
   - Nút:  <button data-state-btn="ten-trang-thai">
   - Khối: <div data-show="trang-thai-1 trang-thai-2"> chỉ hiện ở các trạng thái liệt kê. */
(function () {
  var body = document.body;
  function setState(s) {
    body.setAttribute('data-state', s);
    document.querySelectorAll('[data-show]').forEach(function (el) {
      el.hidden = el.getAttribute('data-show').split(/\s+/).indexOf(s) === -1;
    });
    document.querySelectorAll('[data-state-btn]').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.getAttribute('data-state-btn') === s));
    });
    var live = document.getElementById('state-live');
    if (live) {
      var btn = document.querySelector('[data-state-btn="' + s + '"]');
      live.textContent = btn ? 'Trạng thái xem mẫu: ' + btn.textContent : '';
    }
  }
  document.querySelectorAll('[data-state-btn]').forEach(function (b) {
    b.addEventListener('click', function () { setState(b.getAttribute('data-state-btn')); });
  });
  // Cho phép mở thẳng một trạng thái, ví dụ S-02-man-hinh-chinh.html#state=empty
  var m = /state=([A-Za-z0-9-]+)/.exec(location.hash);
  setState((m && m[1]) || body.getAttribute('data-default') || 'default');
})();
