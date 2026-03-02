document.addEventListener('DOMContentLoaded', function() {
    const state = {
        pergolaType: '',
        lamellaSize: '',
        lamellaType: '',
        width: 0,
        length: 0,
        whiteLed: false,
        rgbLed: false,
        installation: false,
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
                    div.innerHTML = '<div class="lamella-name">' + s.name + '</div>';
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

    if (whiteLedEl) whiteLedEl.addEventListener('change', function() { state.whiteLed = this.checked; });
    if (rgbLedEl) rgbLedEl.addEventListener('change', function() { state.rgbLed = this.checked; });
    if (installEl) installEl.addEventListener('change', function() { state.installation = this.checked; });

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
});
