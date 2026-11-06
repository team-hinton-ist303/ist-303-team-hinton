// Selecting a note in the editor (NTT-62).
//
// - Clicking a note or rest on the staff opens the editor with ?note=<id>.
//   Verovio's note and rest elements carry data-note-id (added by NTT-53).
// - The selected note is highlighted on the staff.
//
// The note list under the staff uses plain links, so selection also works
// without JavaScript. The server decides which note is selected.
(function () {
  "use strict";

  var area = document.querySelector("#staff-area[data-select-url]");
  var staff = area && area.querySelector(".staff-svg");
  if (!staff) return;

  var selected = area.dataset.selectedNote;
  if (selected) {
    staff.querySelectorAll('[data-note-id="' + selected + '"]').forEach(function (el) {
      el.classList.add("is-selected");
    });
  }

  // Notes are thin (a head and a stem), so a click on the gap between them or on a
  // staff line next to a note still picks that note: the nearest one within PAD pixels.
  var PAD = 8;

  function noteAt(x, y) {
    var best = null;
    var bestDistance = Infinity;
    staff.querySelectorAll("[data-note-id]").forEach(function (el) {
      var r = el.getBoundingClientRect();
      if (x < r.left - PAD || x > r.right + PAD || y < r.top - PAD * 3 || y > r.bottom + PAD * 3) return;
      var distance = Math.abs(x - (r.left + r.right) / 2);
      if (distance < bestDistance) {
        best = el;
        bestDistance = distance;
      }
    });
    return best;
  }

  staff.addEventListener("click", function (event) {
    var target = event.target.closest("[data-note-id]") || noteAt(event.clientX, event.clientY);
    if (!target || !staff.contains(target)) return;
    var url = new URL(area.dataset.selectUrl, window.location.href);
    url.searchParams.set("note", target.getAttribute("data-note-id"));
    window.location.href = url.toString();
  });
})();
