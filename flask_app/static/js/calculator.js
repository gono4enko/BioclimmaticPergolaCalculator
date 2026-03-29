document.addEventListener('DOMContentLoaded', function() {
    const state = {
        pergolaType: '',
        lamellaSize: '',
        lamellaType: '',
        width: 0,
        length: 0,
        whiteLed: true,
        rgbLed: false,
        installation: true,
        maxWidth: 13.5,
        maxLength: 8.0,
        result: null
    };

    const stepsEl = {
        step1: document.getElementById('step-1'),
        step2: document.getElementById('step-2'),
        step3: document.getElementById('step-3'),
        step4: document.getElementById('step-4'),
        calcBtn: document.getElementById('calc-btn'),
        resultsSection: document.getElementById('results-section'),
        spinner: document.getElementById('spinner-overlay')
    };

    document.querySelectorAll('.type-option').forEach(function(el) {
        el.addEventListener('click', function() {
            document.querySelectorAll('.type-option').forEach(function(o) { o.classList.remove('selected'); });
            el.classList.add('selected');
            state.pergolaType = el.dataset.type;
            loadLamellaSizes(state.pergolaType);
        });
    });

    function loadLamellaSizes(pergolaType) {
        fetch('/api/lamella-sizes/' + pergolaType)
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (!data.success) return;
                var container = document.getElementById('lamella-options');
                container.innerHTML = '';
                var defaultIdx = 0;
                data.sizes.forEach(function(s, i) {
                    if (s.id === '250') defaultIdx = i;
                });
                data.sizes.forEach(function(s, i) {
                    var div = document.createElement('div');
                    div.className = 'lamella-option col-12 col-md-6 mb-2' + (i === defaultIdx ? ' selected' : '');
                    div.dataset.size = s.id;
                    div.dataset.lamellaType = s.lamella_type;
                    div.innerHTML = '<span class="check-mark"><svg viewBox="0 0 14 14" fill="none" width="12" height="12"><path d="M2 7.5L5.5 11L12 3" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg></span><div class="lamella-name">' + s.name + '</div>';
                    div.addEventListener('click', function() {
                        container.querySelectorAll('.lamella-option').forEach(function(o) { o.classList.remove('selected'); });
                        div.classList.add('selected');
                        state.lamellaSize = s.id;
                        state.lamellaType = s.lamella_type;
                        updateMaxDimensions();
                    });
                    container.appendChild(div);
                });

                if (data.sizes.length > 0) {
                    var def = data.sizes[defaultIdx];
                    state.lamellaSize = def.id;
                    state.lamellaType = def.lamella_type;
                }
                if (data.max_dimensions) {
                    state.maxWidth = data.max_dimensions.width;
                    state.maxLength = data.max_dimensions.length;
                }
                updateDimensionHints();
                stepsEl.step2.style.display = 'block';
                stepsEl.step3.style.display = 'block';
                stepsEl.step4.style.display = 'block';
                stepsEl.calcBtn.style.display = 'block';
                setTimeout(function() {
                    stepsEl.step2.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }, 80);
            });
    }

    function updateMaxDimensions() {
        fetch('/api/max-dimensions?pergola_type=' + state.pergolaType + '&lamella_size=' + state.lamellaSize)
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.success) {
                    state.maxWidth = data.max_dimensions.width;
                    state.maxLength = data.max_dimensions.length;
                    updateDimensionHints();
                    var wInput = document.getElementById('input-width');
                    var lInput = document.getElementById('input-length');
                    wInput.max = state.maxWidth;
                    lInput.max = state.maxLength;
                }
            });
    }

    function updateDimensionHints() {
        var wHint = document.getElementById('width-hint');
        var lHint = document.getElementById('length-hint');
        if (wHint) wHint.textContent = 'Макс: ' + state.maxWidth + ' м';
        if (lHint) lHint.textContent = 'Макс: ' + state.maxLength + ' м';
    }

    document.getElementById('input-width').addEventListener('input', function() {
        state.width = parseFloat(this.value) || 0;
    });
    document.getElementById('input-length').addEventListener('input', function() {
        state.length = parseFloat(this.value) || 0;
    });

    var whiteLedEl = document.getElementById('opt-white-led');
    var rgbLedEl = document.getElementById('opt-rgb-led');
    var installEl = document.getElementById('opt-installation');
    var ledPreview = document.getElementById('led-preview');
    var rgbPreview = document.getElementById('rgb-preview');

    function updateLightingPreviews() {
        if (ledPreview) ledPreview.style.display = state.whiteLed ? 'block' : 'none';
        if (rgbPreview) rgbPreview.style.display = state.rgbLed ? 'block' : 'none';
    }

    if (whiteLedEl) whiteLedEl.addEventListener('change', function() { state.whiteLed = this.checked; updateLightingPreviews(); });
    if (rgbLedEl) rgbLedEl.addEventListener('change', function() { state.rgbLed = this.checked; updateLightingPreviews(); });
    if (installEl) installEl.addEventListener('change', function() { state.installation = this.checked; });

    updateLightingPreviews();

    document.getElementById('calc-btn').addEventListener('click', function() {
        if (!state.pergolaType) { alert('Выберите тип перголы'); return; }
        if (state.width <= 0 || state.length <= 0) { alert('Укажите размеры перголы'); return; }
        if (state.width > state.maxWidth) { alert('Ширина превышает максимум (' + state.maxWidth + ' м)'); return; }
        if (state.length > state.maxLength) { alert('Вынос превышает максимум (' + state.maxLength + ' м)'); return; }

        var lighting = [];
        if (state.whiteLed) lighting.push('white_led');
        if (state.rgbLed) lighting.push('rgb_led');

        var body = {
            pergola_type: state.pergolaType,
            width: state.width,
            length: state.length,
            lamella_size: state.lamellaSize,
            lamella_type: state.lamellaType,
            lighting: lighting,
            installation: state.installation
        };

        stepsEl.spinner.style.display = 'flex';

        fetch('/api/calculate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(body)
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            stepsEl.spinner.style.display = 'none';
            if (!data.success) {
                alert('Ошибка: ' + (data.error || 'Неизвестная ошибка'));
                return;
            }
            state.result = data.result;
            renderResults(data.result);
            setTimeout(function() {
                stepsEl.resultsSection.scrollIntoView({behavior: 'smooth', block: 'center'});
            }, 200);
        })
        .catch(function(err) {
            stepsEl.spinner.style.display = 'none';
            alert('Ошибка подключения: ' + err.message);
        });
    });

    function formatPrice(n) {
        return Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
    }

    function renderResults(result) {
        var sec = stepsEl.resultsSection;
        sec.style.display = 'block';

        var dims = result.dimensions;
        var totals = result.totals;
        var euroRate = result.euro_rate;

        var specHtml = '<table class="spec-table"><thead><tr><th>Наименование</th><th>Количество</th></tr></thead><tbody>';
        result.specification.forEach(function(s) {
            specHtml += '<tr><td>' + s.name + '</td><td>' + s.count + '</td></tr>';
        });
        specHtml += '</tbody></table>';

        var costHtml = '<table class="cost-table"><tbody>';
        result.items.forEach(function(item) {
            var priceRub = Math.round(item.price * euroRate);
            costHtml += '<tr><td>' + item.name + '</td><td>' + formatPrice(priceRub) + ' ₽</td></tr>';
        });
        costHtml += '</tbody></table>';

        var totalHtml = '<div class="total-block">' +
            '<div class="cash-price">Наличный расчёт: ' + formatPrice(totals.cash) + ' ₽</div>' +
            '<div class="other-price">Безналичный расчёт: ' + formatPrice(totals.non_cash) + ' ₽</div>' +
            '<div class="other-price">С НДС 22%: ' + formatPrice(totals.with_vat) + ' ₽</div>' +
            '</div>';

        var infoHtml = '<div style="text-align:center;margin-bottom:0.8rem;color:#555;font-size:0.9rem;">' +
            '<strong>' + result.pergola_type_name + '</strong> | ' +
            dims.width.toFixed(2) + ' × ' + dims.length.toFixed(2) + ' м | ' +
            dims.modules + ' ' + pluralModule(dims.modules) +
            '</div>';

        sec.innerHTML = '<h3>Результаты расчёта</h3>' +
            infoHtml +
            '<h4 style="font-size:1rem;font-weight:600;color:#004B9A;margin-top:1rem;">Спецификация</h4>' +
            specHtml +
            '<h4 style="font-size:1rem;font-weight:600;color:#004B9A;margin-top:1rem;">Стоимость</h4>' +
            costHtml +
            totalHtml +
            '<button class="pdf-btn" id="pdf-btn"><i class="bi bi-file-earmark-pdf"></i> Скачать КП в PDF</button>';

        document.getElementById('pdf-btn').addEventListener('click', exportPdf);

        // Формируем текст расчёта для мессенджеров
        var lightingList = [];
        if (result.items) {
            result.items.forEach(function(item) {
                if (/подсветка|LED|RGB/i.test(item.name)) lightingList.push(item.name);
            });
        }
        window._calcText = [
            '🏗 Пергола: ' + result.pergola_type_name,
            '📐 Размер: ' + dims.width.toFixed(2) + ' × ' + dims.length.toFixed(2) + ' м',
            '🔲 Модулей: ' + dims.modules,
            lightingList.length ? '💡 Подсветка: ' + lightingList.join(', ') : '',
            '',
            '💵 Наличный расчёт: ' + formatPrice(totals.cash) + ' ₽',
            '🏦 Безналичный: ' + formatPrice(totals.non_cash) + ' ₽',
            '📋 С НДС 22%: ' + formatPrice(totals.with_vat) + ' ₽',
        ].filter(Boolean).join('\n');

        // Показываем кнопку «Обсудить расчёт»
        var leadBtn = document.getElementById('openLeadBtn');
        if (leadBtn) {
            leadBtn.style.display = 'block';
            document.getElementById('leadForm').classList.remove('visible');
            document.getElementById('leadSuccess').style.display = 'none';
        }
    }

    function pluralModule(n) {
        var abs = Math.abs(n) % 100;
        if (abs >= 11 && abs <= 19) return 'модулей';
        var last = abs % 10;
        if (last === 1) return 'модуль';
        if (last >= 2 && last <= 4) return 'модуля';
        return 'модулей';
    }

    function exportPdf() {
        if (!state.result) return;
        var btn = document.getElementById('pdf-btn');
        btn.disabled = true;
        btn.textContent = 'Генерация PDF...';

        fetch('/api/export-pdf', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({result: state.result})
        })
        .then(function(r) {
            if (!r.ok) throw new Error('Ошибка генерации PDF');
            var disposition = r.headers.get('content-disposition');
            var filename = 'КП_пергола.pdf';
            if (disposition) {
                var match = disposition.match(/filename\*?=(?:UTF-8'')?["']?([^"';\n]+)/i);
                if (match) filename = decodeURIComponent(match[1]);
            }
            return r.blob().then(function(blob) { return {blob: blob, filename: filename}; });
        })
        .then(function(data) {
            var url = URL.createObjectURL(data.blob);
            var a = document.createElement('a');
            a.href = url;
            a.download = data.filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            btn.disabled = false;
            btn.innerHTML = '<i class="bi bi-file-earmark-pdf"></i> Скачать КП в PDF';
        })
        .catch(function(err) {
            alert('Ошибка: ' + err.message);
            btn.disabled = false;
            btn.innerHTML = '<i class="bi bi-file-earmark-pdf"></i> Скачать КП в PDF';
        });
    }

    // ===== ГЕОЛОКАЦИЯ =====
    (function() {
        if (window._geoDone) return;
        window._geoDone = true;
        var gx = new XMLHttpRequest();
        gx.timeout = 4000;
        gx.open('GET', 'https://ipapi.co/json/');
        gx.onload = function() {
            try {
                var g = JSON.parse(gx.responseText);
                window._userCity = g.city
                    ? (g.city + (g.region && g.region !== g.city ? ' (' + g.region + ')' : ''))
                    : g.region || 'Не определён';
            } catch(e) {}
        };
        gx.onerror = gx.ontimeout = function() {};
        gx.send();
    })();

    fetch('/api/promotions')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (!data.success) return;
            var counterEl = document.getElementById('install-counter');
            if (counterEl && data.install_count > 0) {
                var n = data.install_count;
                var word;
                var m100 = n % 100;
                var m10 = n % 10;
                if (m100 >= 11 && m100 <= 14) word = 'ПЕРГОЛ';
                else if (m10 === 1) word = 'ПЕРГОЛА';
                else if (m10 >= 2 && m10 <= 4) word = 'ПЕРГОЛЫ';
                else word = 'ПЕРГОЛ';
                counterEl.style.background = 'linear-gradient(135deg, ' + data.counter_color + ', ' + data.counter_color + 'CC)';
                counterEl.innerHTML = '<div class="counter-number">' + n + ' ' + word + '</div><div class="counter-label">установлено в ' + data.year + ' году</div>';
            }
        })
        .catch(function() {});
});

// ===== КОНФИГУРАЦИЯ ФОРМЫ =====
var TG_TOKEN  = '8658950389:AAGmL1Ii4BFzce0EpYuhQHEY0V-hCBSkGgE';
var TG_CHAT   = '-5258227787';
var EMAIL     = 'zakaz@infopergola.ru';
var YM_ID     = 65714473;
var CALC_TYPE = 'bioclimatic';
var CALC_NAME = 'Биоклиматическая пергола';

window._calcText  = '';
window._userCity  = 'Не определён';

// ===== ОТПРАВКА ЗАЯВКИ НА ЗВОНОК =====
window.submitLead = function() {
    var inp = document.getElementById('leadPhone');
    var raw = inp.value.replace(/\D/g, '');
    if (raw.length !== 11) {
        inp.classList.add('err');
        inp.focus();
        setTimeout(function() { inp.classList.remove('err'); }, 600);
        return;
    }
    var phone = '+' + raw;
    var btn = document.getElementById('leadBtn');
    btn.textContent = 'Отправляем...';
    btn.disabled = true;

    var done = setTimeout(function() { showOk(phone); }, 10000);
    var gx = new XMLHttpRequest();
    gx.timeout = 4000;
    gx.open('GET', 'https://ipapi.co/json/');
    gx.onload = function() {
        try {
            var g = JSON.parse(gx.responseText);
            var city = g.city
                ? (g.city + (g.region && g.region !== g.city ? ' (' + g.region + ')' : ''))
                : g.region || 'Не определён';
            clearTimeout(done);
            sendCallback(phone, city);
        } catch(e) { clearTimeout(done); sendCallback(phone, window._userCity || 'Не определён'); }
    };
    gx.onerror = gx.ontimeout = function() { clearTimeout(done); sendCallback(phone, window._userCity || 'Не определён'); };
    gx.send();
};

function sendCallback(phone, city) {
    var tgText = '📞 Заявка на звонок — ' + CALC_NAME + '\n\n'
        + '📞 Телефон: ' + phone + '\n'
        + '📍 Город: ' + city + '\n\n'
        + (window._calcText || '');

    var tx = new XMLHttpRequest();
    tx.timeout = 8000;
    tx.open('POST', 'https://api.telegram.org/bot' + TG_TOKEN + '/sendMessage');
    tx.setRequestHeader('Content-Type', 'application/json');
    tx.onload = function() { showOk(phone); };
    tx.onerror = tx.ontimeout = function() { showOk(phone); };
    tx.send(JSON.stringify({ chat_id: TG_CHAT, text: tgText, parse_mode: 'HTML' }));

    var fd = new FormData();
    fd.append('Телефон', phone);
    fd.append('Город', city);
    fd.append('Расчёт', window._calcText || '');
    fd.append('_subject', '📞 Заявка на звонок — ' + CALC_NAME);
    fd.append('_captcha', 'false');
    fd.append('_template', 'table');
    var ex = new XMLHttpRequest();
    ex.timeout = 8000;
    ex.open('POST', 'https://formsubmit.co/ajax/' + EMAIL);
    ex.send(fd);

    try {
        if (typeof ym === 'function') ym(YM_ID, 'reachGoal', 'calculator_lead', { channel: 'callback', calculator_type: CALC_TYPE });
    } catch(e) {}
}

function showOk(phone) {
    var form = document.getElementById('leadForm');
    var s    = document.getElementById('leadSuccess');
    if (form) form.style.display = 'none';
    if (s) {
        document.getElementById('successSub').innerHTML =
            'Перезвоним на <strong>' + phone + '</strong> в течение 15 минут.';
        s.style.display = 'block';
    }
}

// ===== КЛИК ПО МЕССЕНДЖЕРАМ =====
document.addEventListener('click', function(e) {
    var btn = e.target.closest('#btnWhatsapp, #btnTelegram, #btnMax');
    if (!btn) return;
    var ch = btn.id === 'btnWhatsapp' ? 'whatsapp' : btn.id === 'btnTelegram' ? 'telegram' : 'max';
    try {
        if (typeof ym === 'function') ym(YM_ID, 'reachGoal', 'calculator_lead', { channel: ch, calculator_type: CALC_TYPE });
    } catch(e) {}

    var city = window._userCity || 'Не определён';
    var calcText = window._calcText || '';

    if ((btn.id === 'btnWhatsapp' || btn.id === 'btnTelegram') && calcText) {
        e.preventDefault();
        var txt = '📍 Город: ' + city + '\n\nДобрый день! Хочу обсудить расчёт:\n' + calcText;
        var enc = encodeURIComponent(txt);
        var url = btn.id === 'btnWhatsapp'
            ? 'https://api.whatsapp.com/send?phone=79064297420&text=' + enc
            : 'https://t.me/comfort_dom_andrey?text=' + enc;
        window.open(url, '_blank');
    }

    if (btn.id === 'btnMax' && calcText) {
        var tgText = '📊 Заявка через Max — ' + CALC_NAME + '\n\n📍 Город: ' + city + '\n\n' + calcText;
        var tx = new XMLHttpRequest();
        tx.timeout = 8000;
        tx.open('POST', 'https://api.telegram.org/bot' + TG_TOKEN + '/sendMessage');
        tx.setRequestHeader('Content-Type', 'application/json');
        tx.send(JSON.stringify({ chat_id: TG_CHAT, text: tgText, parse_mode: 'HTML' }));

        var fd = new FormData();
        fd.append('Канал', 'Max'); fd.append('Город', city); fd.append('Расчёт', calcText);
        fd.append('_subject', '📊 Заявка через Max — ' + CALC_NAME);
        fd.append('_captcha', 'false'); fd.append('_template', 'table');
        var ex = new XMLHttpRequest();
        ex.timeout = 8000;
        ex.open('POST', 'https://formsubmit.co/ajax/' + EMAIL);
        ex.send(fd);
    }
});

// Enter в поле телефона
document.addEventListener('keydown', function(e) {
    if (e.target.id === 'leadPhone' && e.key === 'Enter') { e.preventDefault(); submitLead(); }
});
