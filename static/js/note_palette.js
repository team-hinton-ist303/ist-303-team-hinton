// Note palette behaviour for the composition editor (NTT-40).
//
// - Greys out pitches outside the treble-clef range (A3 to C6) for the chosen octave.
// - At the range edges, greys out the accidental that would step outside it
//   (no A-flat 3, no C-sharp 6), including when the key signature would add it.
// - "Key" (no accidental) follows the key signature: F in G major is F-sharp.
// - "Rest instead of a note" disables pitch, octave and accidental.
// - Shows a live preview of the note that Add note will create.
//
// This is a convenience only. The add-note route (NTT-41/42) still validates on the server.
(function () {
  "use strict";

  var form = document.getElementById("note-form");
  if (!form) return;

  var LETTERS = ["C", "D", "E", "F", "G", "A", "B"];
  var SYMBOLS = { "": "", natural: "♮", sharp: "♯", flat: "♭" };

  function parseNote(text) {
    return { pitch: text.charAt(0), octave: parseInt(text.slice(1), 10) };
  }

  function step(pitch, octave) {
    return octave * 7 + LETTERS.indexOf(pitch);
  }

  var low = parseNote(form.dataset.rangeLow);
  var high = parseNote(form.dataset.rangeHigh);
  var keyAcc = JSON.parse(form.dataset.keyAccidentals || "{}");
  var lowStep = step(low.pitch, low.octave);
  var highStep = step(high.pitch, high.octave);

  function inputs(name) {
    return Array.prototype.slice.call(form.querySelectorAll('input[name="' + name + '"]'));
  }

  function checked(name) {
    var el = form.querySelector('input[name="' + name + '"]:checked');
    return el ? el.value : null;
  }

  var restBox = document.getElementById("is-rest");
  var previewText = document.getElementById("note-preview-text");

  function labelFor(input) {
    var label = form.querySelector('label[for="' + input.id + '"]');
    return label ? label.textContent.trim() : input.value;
  }

  // The accidental a note actually gets: the one chosen, or else the key signature's.
  function effective(pitch, chosen) {
    return chosen || keyAcc[pitch] || "";
  }

  function update() {
    var isRest = restBox && restBox.checked;
    var octave = parseInt(checked("octave"), 10);

    // Pitches: disable anything outside the range for this octave.
    var pitchInputs = inputs("pitch");
    pitchInputs.forEach(function (input) {
      var s = step(input.value, octave);
      input.disabled = isRest || s < lowStep || s > highStep;
    });
    var selectedPitch = form.querySelector('input[name="pitch"]:checked');
    if (!isRest && (!selectedPitch || selectedPitch.disabled)) {
      var firstOk = pitchInputs.filter(function (i) { return !i.disabled; })[0];
      if (firstOk) firstOk.checked = true;
    }
    var pitch = checked("pitch");

    // Octaves: only disabled for rests.
    inputs("octave").forEach(function (input) { input.disabled = isRest; });

    // Accidentals: no flat on the lowest note, no sharp on the highest,
    // whether chosen directly or coming from the key signature.
    var s = step(pitch, octave);
    inputs("accidental").forEach(function (input) {
      var acc = effective(pitch, input.value);
      input.disabled = isRest ||
        (s === lowStep && acc === "flat") ||
        (s === highStep && acc === "sharp");
    });
    var selectedAcc = form.querySelector('input[name="accidental"]:checked');
    if (!isRest && selectedAcc && selectedAcc.disabled) {
      var natural = form.querySelector('input[name="accidental"][value="natural"]');
      if (natural) natural.checked = true;
    }

    // Preview.
    var durInput = form.querySelector('input[name="duration"]:checked');
    var duration = durInput ? labelFor(durInput).toLowerCase() : "";
    if (previewText) {
      previewText.textContent = isRest
        ? duration + " rest"
        : pitch + SYMBOLS[effective(pitch, checked("accidental") || "")] + octave + " " + duration;
    }
  }

  form.addEventListener("change", update);
  update();
})();
