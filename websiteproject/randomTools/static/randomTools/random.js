(function () {
  'use strict';

  function randomInt(min, max) {
    // inclusive of both ends
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }

  function parseLines(textarea) {
    return textarea.value
      .split('\n')
      .map(function (line) { return line.trim(); })
      .filter(function (line) { return line.length > 0; });
  }

  function copyToClipboard(inputEl) {
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(inputEl.value).catch(function () {
        fallbackCopy(inputEl);
      });
    } else {
      fallbackCopy(inputEl);
    }
  }

  function fallbackCopy(inputEl) {
    inputEl.select();
    try {
      document.execCommand('copy');
    } catch (err) {
      // clipboard unavailable, nothing more we can do
    }
  }

  // ---------- Coin flip ----------
  (function coinFlip() {
    var btn = document.getElementById('coinFlipBtn');
    var coin = document.getElementById('coin');
    var face = document.getElementById('coinFace');
    if (!btn) return;

    btn.addEventListener('click', function () {
      coin.classList.remove('flipping');
      // force reflow so the animation can restart
      void coin.offsetWidth;
      coin.classList.add('flipping');
      btn.disabled = true;

      setTimeout(function () {
        face.textContent = Math.random() < 0.5 ? 'Heads' : 'Tails';
        coin.classList.remove('flipping');
        btn.disabled = false;
      }, 600);
    });
  })();

  // ---------- Dice roller ----------
  (function diceRoller() {
    var btn = document.getElementById('diceRollBtn');
    var countInput = document.getElementById('diceCount');
    var sidesSelect = document.getElementById('diceSides');
    var resultsEl = document.getElementById('diceResults');
    var totalEl = document.getElementById('diceTotal');
    if (!btn) return;

    btn.addEventListener('click', function () {
      var count = Math.min(12, Math.max(1, parseInt(countInput.value, 10) || 1));
      var sides = parseInt(sidesSelect.value, 10);
      resultsEl.innerHTML = '';
      var total = 0;
      for (var i = 0; i < count; i++) {
        var roll = randomInt(1, sides);
        total += roll;
        var die = document.createElement('div');
        die.className = 'die';
        die.textContent = roll;
        resultsEl.appendChild(die);
      }
      totalEl.textContent = 'Total: ' + total;
    });
  })();

  // ---------- Random number ----------
  (function randomNumber() {
    var btn = document.getElementById('numberGenBtn');
    var minInput = document.getElementById('numMin');
    var maxInput = document.getElementById('numMax');
    var resultEl = document.getElementById('numberResult');
    if (!btn) return;

    btn.addEventListener('click', function () {
      var min = parseInt(minInput.value, 10);
      var max = parseInt(maxInput.value, 10);
      if (isNaN(min) || isNaN(max)) {
        resultEl.textContent = 'Enter valid numbers';
        return;
      }
      if (min > max) {
        var tmp = min; min = max; max = tmp;
      }
      resultEl.textContent = randomInt(min, max);
    });
  })();

  // ---------- Spin the wheel ----------
  (function wheel() {
    var btn = document.getElementById('wheelSpinBtn');
    var optionsEl = document.getElementById('wheelOptions');
    var canvas = document.getElementById('wheelCanvas');
    var resultEl = document.getElementById('wheelResult');
    if (!btn || !canvas) return;

    var ctx = canvas.getContext('2d');
    var palette = ['#1164a3', '#e0a800', '#28a745', '#dc3545', '#6f42c1', '#20c997', '#fd7e14', '#17a2b8'];
    var rotation = 0;
    var spinning = false;

    function drawWheel(options) {
      var size = canvas.width;
      var center = size / 2;
      var radius = center - 6;
      var segmentAngle = 360 / options.length;

      ctx.clearRect(0, 0, size, size);

      options.forEach(function (label, i) {
        var startDeg = -90 + i * segmentAngle;
        var endDeg = startDeg + segmentAngle;
        var startRad = (startDeg * Math.PI) / 180;
        var endRad = (endDeg * Math.PI) / 180;

        ctx.beginPath();
        ctx.moveTo(center, center);
        ctx.arc(center, center, radius, startRad, endRad);
        ctx.closePath();
        ctx.fillStyle = palette[i % palette.length];
        ctx.fill();
        ctx.strokeStyle = '#fff';
        ctx.stroke();

        // label
        var midRad = ((startDeg + endDeg) / 2 * Math.PI) / 180;
        ctx.save();
        ctx.translate(center, center);
        ctx.rotate(midRad);
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 12px Arial';
        ctx.textAlign = 'right';
        ctx.fillText(label.slice(0, 14), radius - 8, 4);
        ctx.restore();
      });
    }

    function currentOptions() {
      return parseLines(optionsEl);
    }

    drawWheel(currentOptions());

    optionsEl.addEventListener('input', function () {
      var options = currentOptions();
      if (options.length >= 2) {
        drawWheel(options);
      }
    });

    btn.addEventListener('click', function () {
      if (spinning) return;
      var options = currentOptions();
      if (options.length < 2) {
        resultEl.textContent = 'Add at least 2 options';
        return;
      }
      drawWheel(options);

      spinning = true;
      resultEl.textContent = '';
      var segmentAngle = 360 / options.length;
      var extraSpins = 5 * 360;
      var randomOffset = Math.random() * 360;
      rotation += extraSpins + randomOffset;
      canvas.style.transform = 'rotate(' + rotation + 'deg)';

      setTimeout(function () {
        var effectiveAngle = (360 - (rotation % 360)) % 360;
        var winningIndex = Math.floor(effectiveAngle / segmentAngle) % options.length;
        resultEl.textContent = 'Winner: ' + options[winningIndex];
        spinning = false;
      }, 4100);
    });
  })();

  // ---------- Magic 8-ball ----------
  (function eightBall() {
    var btn = document.getElementById('eightBallBtn');
    var ball = document.getElementById('eightBall');
    var answerEl = document.getElementById('eightBallAnswer');
    if (!btn) return;

    var answers = [
      'It is certain', 'Without a doubt', 'Yes definitely', 'You may rely on it',
      'As I see it, yes', 'Most likely', 'Outlook good', 'Yes',
      'Signs point to yes', 'Reply hazy, try again', 'Ask again later',
      'Better not tell you now', 'Cannot predict now', 'Concentrate and ask again',
      "Don't count on it", 'My reply is no', 'My sources say no',
      'Outlook not so good', 'Very doubtful'
    ];

    btn.addEventListener('click', function () {
      ball.classList.remove('shaking');
      void ball.offsetWidth;
      ball.classList.add('shaking');
      answerEl.textContent = answers[randomInt(0, answers.length - 1)];
    });
  })();

  // ---------- Password generator ----------
  (function passwordGenerator() {
    var btn = document.getElementById('pwGenBtn');
    var copyBtn = document.getElementById('pwCopyBtn');
    var lengthInput = document.getElementById('pwLength');
    var upperBox = document.getElementById('pwUpper');
    var lowerBox = document.getElementById('pwLower');
    var numberBox = document.getElementById('pwNumbers');
    var symbolBox = document.getElementById('pwSymbols');
    var resultEl = document.getElementById('pwResult');
    if (!btn) return;

    var sets = {
      upper: 'ABCDEFGHJKLMNPQRSTUVWXYZ',
      lower: 'abcdefghijkmnpqrstuvwxyz',
      numbers: '23456789',
      symbols: '!@#$%^&*()-_=+'
    };

    function secureRandomInt(max) {
      var array = new Uint32Array(1);
      window.crypto.getRandomValues(array);
      return array[0] % max;
    }

    btn.addEventListener('click', function () {
      var length = Math.min(64, Math.max(4, parseInt(lengthInput.value, 10) || 16));
      var charset = '';
      if (upperBox.checked) charset += sets.upper;
      if (lowerBox.checked) charset += sets.lower;
      if (numberBox.checked) charset += sets.numbers;
      if (symbolBox.checked) charset += sets.symbols;
      if (!charset) {
        charset = sets.lower;
        lowerBox.checked = true;
      }

      var password = '';
      for (var i = 0; i < length; i++) {
        password += charset[secureRandomInt(charset.length)];
      }
      resultEl.value = password;
    });

    copyBtn.addEventListener('click', function () {
      if (resultEl.value) copyToClipboard(resultEl);
    });
  })();

  // ---------- Random color ----------
  (function randomColor() {
    var btn = document.getElementById('colorGenBtn');
    var copyBtn = document.getElementById('colorCopyBtn');
    var swatch = document.getElementById('colorSwatch');
    var resultEl = document.getElementById('colorResult');
    if (!btn) return;

    btn.addEventListener('click', function () {
      var hex = '#' + randomInt(0, 0xffffff).toString(16).padStart(6, '0');
      swatch.style.backgroundColor = hex;
      resultEl.value = hex;
    });

    copyBtn.addEventListener('click', function () {
      if (resultEl.value) copyToClipboard(resultEl);
    });
  })();

  // ---------- List shuffler / picker ----------
  (function listTools() {
    var shuffleBtn = document.getElementById('listShuffleBtn');
    var pickBtn = document.getElementById('listPickBtn');
    var itemsEl = document.getElementById('listItems');
    var resultEl = document.getElementById('listResult');
    if (!shuffleBtn) return;

    shuffleBtn.addEventListener('click', function () {
      var items = parseLines(itemsEl);
      for (var i = items.length - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1));
        var tmp = items[i]; items[i] = items[j]; items[j] = tmp;
      }
      itemsEl.value = items.join('\n');
      resultEl.textContent = '';
    });

    pickBtn.addEventListener('click', function () {
      var items = parseLines(itemsEl);
      if (items.length === 0) {
        resultEl.textContent = 'Add at least 1 item';
        return;
      }
      resultEl.textContent = 'Picked: ' + items[randomInt(0, items.length - 1)];
    });
  })();
})();
