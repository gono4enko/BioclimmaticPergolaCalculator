document.addEventListener('DOMContentLoaded', function() {
    var state = {
        pergolaType: '',
        lamellaSize: '',
        lamellaType: '',
        selectedVariant: '',
        width: 0,
        length: 0,
        whiteLed: true,
        rgbLed: false,
        installation: true,
        maxWidth: 13.5,
        maxLength: 8.0,
        result: null,
        allResults: null,
        variantsData: null
    };

    var stepsEl = {
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
            stepsEl.step3.style.display = 'none';
            stepsEl.step4.style.display = 'none';
            stepsEl.calcBtn.style.display = 'none';
            stepsEl.resultsSection.style.display = 'none';
            loadVariantOptions(state.pergolaType);
        });
    });

    function setDefaultLamellaForType(pergolaType) {
        if (pergolaType === 'B600') {
            state.lamellaSize = 'PIR';
            state.lamellaType = 'B600-PIR';
        } else {
            state.lamellaSize = '250';
            if (pergolaType === 'B500NEW') state.lamellaType = 'B500-25NEW';
            else state.lamellaType = 'B700-25NEW';
        }
    }

    function selectVariant(container, clickedDiv, variant, lamellaSize, pergolaType) {
        container.querySelectorAll('.variant-option').forEach(function(o) { o.classList.remove('selected'); });
        clickedDiv.classList.add('selected');
        state.selectedVariant = variant;

        if (variant === 'auto' || variant === 'all') {
            setDefaultLamellaForType(pergolaType);
        } else {
            state.lamellaSize = lamellaSize;
            if (pergolaType === 'B500NEW') {
                state.lamellaType = 'B500-' + (lamellaSize === '200' ? '20' : '25') + 'NEW';
            } else if (pergolaType === 'B700NEW') {
                state.lamellaType = 'B700-' + (lamellaSize === '200' ? '20' : '25') + 'NEW';
            } else {
                state.lamellaType = 'B600-PIR';
            }
        }

        updateMaxDimensions();
        stepsEl.step3.style.display = 'block';
        stepsEl.step4.style.display = 'block';
        stepsEl.calcBtn.style.display = 'block';
        setTimeout(function() {
            stepsEl.step3.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 80);
    }

    function loadVariantOptions(pergolaType) {
        fetch('/api/variant-options/' + pergolaType)
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (!data.success || !data.variants.length) return;
                var container = document.getElementById('variant-options');
                container.innerHTML = '';
                state.selectedVariant = '';
                state.lamellaSize = '';
                state.lamellaType = '';
                state.variantsData = data.variants;

                var autoDiv = document.createElement('div');
                autoDiv.className = 'variant-option variant-special col-12 col-md-6 mb-2';
                autoDiv.dataset.variant = 'auto';
                autoDiv.innerHTML = '<span class="check-mark"><svg viewBox="0 0 14 14" fill="none" width="12" height="12"><path d="M2 7.5L5.5 11L12 3" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg></span>' +
                    '<div class="variant-label variant-label-special"><span class="special-icon">&#9733;</span> Автовыбор</div>' +
                    '<div class="variant-special-desc">Самый бюджетный вариант — система автоматически подберёт оптимальную модификацию по минимальной цене</div>';
                autoDiv.addEventListener('click', function() {
                    selectVariant(container, autoDiv, 'auto', '', pergolaType);
                });
                container.appendChild(autoDiv);

                var allDiv = document.createElement('div');
                allDiv.className = 'variant-option variant-special col-12 col-md-6 mb-2';
                allDiv.dataset.variant = 'all';
                allDiv.innerHTML = '<span class="check-mark"><svg viewBox="0 0 14 14" fill="none" width="12" height="12"><path d="M2 7.5L5.5 11L12 3" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg></span>' +
                    '<div class="variant-label variant-label-special"><span class="special-icon">&#9776;</span> Все варианты</div>' +
                    '<div class="variant-special-desc">Сравнительная таблица всех модификаций — от самой доступной до премиальной</div>';
                allDiv.addEventListener('click', function() {
                    selectVariant(container, allDiv, 'all', '', pergolaType);
                });
                container.appendChild(allDiv);

                data.variants.forEach(function(v) {
                    var div = document.createElement('div');
                    div.className = 'variant-option col-12 col-md-6 mb-2';
                    div.dataset.variant = v.variant;
                    div.dataset.lamellaSize = v.lamella_size;

                    var specsHtml = '<div class="variant-specs">';
                    specsHtml += '<div class="spec-row"><span class="spec-icon">\u25AC</span> \u041B\u0430\u043C\u0435\u043B\u044C: <strong>' + v.lamella + '</strong></div>';
                    specsHtml += '<div class="spec-row"><span class="spec-icon">\u25AE</span> \u041A\u043E\u043B\u043E\u043D\u043D\u0430: <strong>' + v.column + '</strong></div>';
                    specsHtml += '<div class="spec-row"><span class="spec-icon">\u2501</span> \u0411\u0430\u043B\u043A\u0430: <strong>' + v.beam + '</strong></div>';
                    specsHtml += '<div class="spec-row"><span class="spec-icon">\u2550</span> \u0411\u0430\u043B\u043A\u0430 \u0434\u0432\u0443\u0445\u0441\u0442.: <strong>' + v.beam_double + '</strong></div>';
                    if (v.max_overhang) {
                        specsHtml += '<div class="spec-row spec-overhang"><span class="spec-icon">\u2194</span> \u041C\u0430\u043A\u0441. \u0432\u044B\u043B\u0435\u0442 \u0431\u0435\u0437 \u0434\u043E\u043F. \u043A\u043E\u043B\u043E\u043D\u043D\u044B: <strong>' + v.max_overhang + ' \u043C</strong></div>';
                    }
                    specsHtml += '</div>';

                    div.innerHTML = '<span class="check-mark"><svg viewBox="0 0 14 14" fill="none" width="12" height="12"><path d="M2 7.5L5.5 11L12 3" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg></span>' +
                        '<div class="variant-label">' + v.label + '</div>' +
                        specsHtml;

                    div.addEventListener('click', function() {
                        selectVariant(container, div, v.variant, v.lamella_size, pergolaType);
                    });
                    container.appendChild(div);
                });

                stepsEl.step2.style.display = 'block';
                setTimeout(function() {
                    stepsEl.step2.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }, 80);
            });
    }

    function updateMaxDimensions() {
        var ls = state.lamellaSize;
        if (state.selectedVariant === 'auto' || state.selectedVariant === 'all') {
            if (state.pergolaType === 'B600') {
                ls = 'PIR';
            } else {
                ls = '250';
            }
        }
        fetch('/api/max-dimensions?pergola_type=' + state.pergolaType + '&lamella_size=' + ls)
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
        if (wHint) wHint.textContent = '\u041C\u0430\u043A\u0441: ' + state.maxWidth + ' \u043C';
        if (lHint) lHint.textContent = '\u041C\u0430\u043A\u0441: ' + state.maxLength + ' \u043C';
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
        if (!state.pergolaType) { alert('\u0412\u044B\u0431\u0435\u0440\u0438\u0442\u0435 \u0442\u0438\u043F \u043F\u0435\u0440\u0433\u043E\u043B\u044B'); return; }
        if (!state.selectedVariant) { alert('\u0412\u044B\u0431\u0435\u0440\u0438\u0442\u0435 \u043C\u043E\u0434\u0438\u0444\u0438\u043A\u0430\u0446\u0438\u044E'); return; }
        if (state.width <= 0 || state.length <= 0) { alert('\u0423\u043A\u0430\u0436\u0438\u0442\u0435 \u0440\u0430\u0437\u043C\u0435\u0440\u044B \u043F\u0435\u0440\u0433\u043E\u043B\u044B'); return; }
        if (state.width > state.maxWidth) { alert('\u0428\u0438\u0440\u0438\u043D\u0430 \u043F\u0440\u0435\u0432\u044B\u0448\u0430\u0435\u0442 \u043C\u0430\u043A\u0441\u0438\u043C\u0443\u043C (' + state.maxWidth + ' \u043C)'); return; }
        if (state.length > state.maxLength) { alert('\u0412\u044B\u043D\u043E\u0441 \u043F\u0440\u0435\u0432\u044B\u0448\u0430\u0435\u0442 \u043C\u0430\u043A\u0441\u0438\u043C\u0443\u043C (' + state.maxLength + ' \u043C)'); return; }

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
            installation: state.installation,
            selected_variant: state.selectedVariant
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
                alert('\u041E\u0448\u0438\u0431\u043A\u0430: ' + (data.error || '\u041D\u0435\u0438\u0437\u0432\u0435\u0441\u0442\u043D\u0430\u044F \u043E\u0448\u0438\u0431\u043A\u0430'));
                return;
            }
            if (data.mode === 'all') {
                state.allResults = data.results;
                state.result = data.results[0];
                renderAllResults(data.results);
            } else {
                state.result = data.result;
                state.allResults = null;
                renderResults(data.result);
            }
            try { if (typeof ym === 'function') ym(YM_ID, 'reachGoal', 'calc_success', { calculator_type: CALC_TYPE }); } catch(e) {}
            setTimeout(function() {
                stepsEl.resultsSection.scrollIntoView({behavior: 'smooth', block: 'center'});
            }, 200);
        })
        .catch(function(err) {
            stepsEl.spinner.style.display = 'none';
            alert('\u041E\u0448\u0438\u0431\u043A\u0430 \u043F\u043E\u0434\u043A\u043B\u044E\u0447\u0435\u043D\u0438\u044F: ' + err.message);
        });
    });

    function formatPrice(n) {
        return Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
    }

    function renderAllResults(results) {
        var sec = stepsEl.resultsSection;
        sec.style.display = 'block';

        var first = results[0];
        var dims = first.dimensions;

        var infoHtml = '<div style="text-align:center;margin-bottom:0.8rem;color:#555;font-size:0.9rem;">' +
            '<strong>' + first.pergola_type_name + '</strong> | ' +
            dims.width.toFixed(2) + ' \u00D7 ' + dims.length.toFixed(2) + ' \u043C' +
            '</div>';

        var tableHtml = '<div class="compare-table-wrap"><table class="compare-table">';
        tableHtml += '<thead><tr><th>\u041C\u043E\u0434\u0438\u0444\u0438\u043A\u0430\u0446\u0438\u044F</th>';
        tableHtml += '<th>\u041D\u0430\u043B\u0438\u0447\u043D\u044B\u0435</th>';
        tableHtml += '<th>\u0411\u0435\u0437\u043D\u0430\u043B\u0438\u0447\u043D\u044B\u0439</th>';
        tableHtml += '<th>\u0421 \u041D\u0414\u0421 22%</th>';
        tableHtml += '</tr></thead><tbody>';

        var cheapest = results[0].totals.cash;

        results.forEach(function(r, idx) {
            var label = r.variant_label || r.selected_variant || ('\u0412\u0430\u0440\u0438\u0430\u043D\u0442 ' + (idx + 1));
            var diffHtml = '';
            if (idx > 0) {
                var diff = r.totals.cash - cheapest;
                diffHtml = '<div class="compare-diff">+' + formatPrice(diff) + ' \u20BD</div>';
            } else {
                diffHtml = '<div class="compare-best">\u041C\u0438\u043D\u0438\u043C\u0430\u043B\u044C\u043D\u0430\u044F \u0446\u0435\u043D\u0430</div>';
            }
            tableHtml += '<tr class="' + (idx === 0 ? 'compare-row-best' : '') + '">';
            tableHtml += '<td><strong>' + label + '</strong>' + diffHtml + '</td>';
            tableHtml += '<td>' + formatPrice(r.totals.cash) + ' \u20BD</td>';
            tableHtml += '<td>' + formatPrice(r.totals.non_cash) + ' \u20BD</td>';
            tableHtml += '<td>' + formatPrice(r.totals.with_vat) + ' \u20BD</td>';
            tableHtml += '</tr>';
        });
        tableHtml += '</tbody></table></div>';

        var specsHtml = '';
        if (state.variantsData) {
            specsHtml = '<h4 style="font-size:1rem;font-weight:600;color:#004B9A;margin-top:1.2rem;">\u0422\u0435\u0445\u043D\u0438\u0447\u0435\u0441\u043A\u0438\u0435 \u0445\u0430\u0440\u0430\u043A\u0442\u0435\u0440\u0438\u0441\u0442\u0438\u043A\u0438</h4>';
            specsHtml += '<div class="compare-table-wrap"><table class="compare-specs-table">';
            specsHtml += '<thead><tr><th>\u041F\u0430\u0440\u0430\u043C\u0435\u0442\u0440</th>';
            state.variantsData.forEach(function(v) {
                specsHtml += '<th>' + v.label + '</th>';
            });
            specsHtml += '</tr></thead><tbody>';

            var specRows = [
                {key: 'lamella', label: '\u041B\u0430\u043C\u0435\u043B\u044C'},
                {key: 'column', label: '\u041A\u043E\u043B\u043E\u043D\u043D\u0430'},
                {key: 'beam', label: '\u0411\u0430\u043B\u043A\u0430'},
                {key: 'beam_double', label: '\u0411\u0430\u043B\u043A\u0430 \u0434\u0432\u0443\u0445\u0441\u0442.'},
                {key: 'max_overhang', label: '\u041C\u0430\u043A\u0441. \u0432\u044B\u043B\u0435\u0442'}
            ];
            specRows.forEach(function(sr) {
                specsHtml += '<tr><td><strong>' + sr.label + '</strong></td>';
                state.variantsData.forEach(function(v) {
                    var val = v[sr.key];
                    if (sr.key === 'max_overhang') val = val ? val + ' \u043C' : '\u2014';
                    specsHtml += '<td>' + (val || '\u2014') + '</td>';
                });
                specsHtml += '</tr>';
            });
            specsHtml += '</tbody></table></div>';
        }

        sec.innerHTML = '<h3>\u0421\u0440\u0430\u0432\u043D\u0435\u043D\u0438\u0435 \u0432\u0430\u0440\u0438\u0430\u043D\u0442\u043E\u0432</h3>' +
            infoHtml + tableHtml + specsHtml +
            '<button class="pdf-btn" id="pdf-btn"><i class="bi bi-file-earmark-pdf"></i> \u0421\u043A\u0430\u0447\u0430\u0442\u044C \u041A\u041F \u0432 PDF</button>';

        document.getElementById('pdf-btn').addEventListener('click', exportPdf);

        var bestResult = results[0];
        window._calcText = [
            '\uD83C\uDFD7 \u041F\u0435\u0440\u0433\u043E\u043B\u0430: ' + bestResult.pergola_type_name,
            '\uD83D\uDCD0 \u0420\u0430\u0437\u043C\u0435\u0440: ' + dims.width.toFixed(2) + ' \u00D7 ' + dims.length.toFixed(2) + ' \u043C',
            '',
            '\u0421\u0440\u0430\u0432\u043D\u0435\u043D\u0438\u0435 ' + results.length + ' \u0432\u0430\u0440\u0438\u0430\u043D\u0442\u043E\u0432:',
        ];
        results.forEach(function(r) {
            var lbl = r.variant_label || r.selected_variant || '';
            window._calcText.push(lbl + ': ' + formatPrice(r.totals.cash) + ' / ' + formatPrice(r.totals.non_cash) + ' / ' + formatPrice(r.totals.with_vat) + ' \u20BD');
        });
        window._calcText = window._calcText.filter(Boolean).join('\n');

        var lf = document.getElementById('leadForm');
        var ls = document.getElementById('leadSuccess');
        var cb = document.getElementById('callbackBlock');
        var lb = document.getElementById('leadBtn');
        if (lf) { lf.style.display = ''; lf.classList.add('visible'); }
        if (ls) ls.classList.remove('visible');
        if (cb) cb.style.display = 'none';
        if (lb) { lb.textContent = '\u0416\u0434\u0443 \u0437\u0432\u043E\u043D\u043A\u0430'; lb.disabled = false; }
    }

    function renderResults(result) {
        var sec = stepsEl.resultsSection;
        sec.style.display = 'block';

        var dims = result.dimensions;
        var totals = result.totals;
        var euroRate = result.euro_rate;

        var specHtml = '<table class="spec-table"><thead><tr><th>\u041D\u0430\u0438\u043C\u0435\u043D\u043E\u0432\u0430\u043D\u0438\u0435</th><th>\u041A\u043E\u043B\u0438\u0447\u0435\u0441\u0442\u0432\u043E</th></tr></thead><tbody>';
        result.specification.forEach(function(s) {
            specHtml += '<tr><td>' + s.name + '</td><td>' + s.count + '</td></tr>';
        });
        specHtml += '</tbody></table>';

        var costHtml = '<table class="cost-table"><tbody>';
        result.items.forEach(function(item) {
            var priceRub = Math.round(item.price * euroRate);
            costHtml += '<tr><td>' + item.name + '</td><td>' + formatPrice(priceRub) + ' \u20BD</td></tr>';
        });
        costHtml += '</tbody></table>';

        var totalHtml =
            '<div class="payment-variants-block">' +
                '<div class="payment-variants-title">\u0421\u0442\u043E\u0438\u043C\u043E\u0441\u0442\u044C \u043F\u043E \u0432\u0430\u0440\u0438\u0430\u043D\u0442\u0430\u043C \u043E\u043F\u043B\u0430\u0442\u044B:</div>' +
                '<div class="payment-variant-row">' +
                    '<span class="payment-variant-label">\u041D\u0430\u043B\u0438\u0447\u043D\u044B\u0435</span>' +
                    '<span class="payment-variant-price pv-cash" id="result-total-price">' + formatPrice(totals.cash) + ' \u20BD</span>' +
                '</div>' +
                '<div class="payment-variant-row">' +
                    '<span class="payment-variant-label">\u0411\u0435\u0437\u043D\u0430\u043B\u0438\u0447\u043D\u044B\u0439 \u0440\u0430\u0441\u0447\u0451\u0442</span>' +
                    '<span class="payment-variant-price" id="result-total-price-noncash">' + formatPrice(totals.non_cash) + ' \u20BD</span>' +
                '</div>' +
                '<div class="payment-variant-row pv-last">' +
                    '<span class="payment-variant-label">\u0411\u0435\u0437\u043D\u0430\u043B\u0438\u0447\u043D\u044B\u0439 \u0441 \u041D\u0414\u0421 22%</span>' +
                    '<span class="payment-variant-price" id="result-total-price-vat">' + formatPrice(totals.with_vat) + ' \u20BD</span>' +
                '</div>' +
            '</div>';

        var variantSpecHtml = '';
        if (result.selected_variant && state.variantsData) {
            var sv = result.selected_variant;
            var matchedSpec = null;
            state.variantsData.forEach(function(v) {
                if (v.variant === sv) matchedSpec = v;
            });
            if (matchedSpec) {
                variantSpecHtml = '<div class="variant-tech-block">' +
                    '<div class="variant-tech-title">\u0422\u0435\u0445\u043D\u0438\u0447\u0435\u0441\u043A\u0438\u0435 \u0445\u0430\u0440\u0430\u043A\u0442\u0435\u0440\u0438\u0441\u0442\u0438\u043A\u0438 (' + matchedSpec.label + ')</div>' +
                    '<div class="variant-tech-specs">' +
                    '<div>\u25AC \u041B\u0430\u043C\u0435\u043B\u044C: <strong>' + matchedSpec.lamella + '</strong></div>' +
                    '<div>\u25AE \u041A\u043E\u043B\u043E\u043D\u043D\u0430: <strong>' + matchedSpec.column + '</strong></div>' +
                    '<div>\u2501 \u0411\u0430\u043B\u043A\u0430: <strong>' + matchedSpec.beam + '</strong></div>' +
                    '<div>\u2550 \u0411\u0430\u043B\u043A\u0430 \u0434\u0432\u0443\u0445\u0441\u0442.: <strong>' + matchedSpec.beam_double + '</strong></div>' +
                    (matchedSpec.max_overhang ? '<div>\u2194 \u041C\u0430\u043A\u0441. \u0432\u044B\u043B\u0435\u0442: <strong>' + matchedSpec.max_overhang + ' \u043C</strong></div>' : '') +
                    '</div></div>';
            }
        }

        var infoHtml = '<div style="text-align:center;margin-bottom:0.8rem;color:#555;font-size:0.9rem;">' +
            '<strong>' + result.pergola_type_name + '</strong> | ' +
            dims.width.toFixed(2) + ' \u00D7 ' + dims.length.toFixed(2) + ' \u043C | ' +
            dims.modules + ' ' + pluralModule(dims.modules) +
            '</div>';

        sec.innerHTML = '<h3>\u0420\u0435\u0437\u0443\u043B\u044C\u0442\u0430\u0442\u044B \u0440\u0430\u0441\u0447\u0451\u0442\u0430</h3>' +
            infoHtml +
            '<h4 style="font-size:1rem;font-weight:600;color:#004B9A;margin-top:1rem;">\u0421\u043F\u0435\u0446\u0438\u0444\u0438\u043A\u0430\u0446\u0438\u044F</h4>' +
            specHtml +
            '<h4 style="font-size:1rem;font-weight:600;color:#004B9A;margin-top:1rem;">\u0421\u0442\u043E\u0438\u043C\u043E\u0441\u0442\u044C</h4>' +
            costHtml +
            totalHtml +
            variantSpecHtml +
            '<button class="pdf-btn" id="pdf-btn"><i class="bi bi-file-earmark-pdf"></i> \u0421\u043A\u0430\u0447\u0430\u0442\u044C \u041A\u041F \u0432 PDF</button>';

        document.getElementById('pdf-btn').addEventListener('click', exportPdf);

        var lightingList = [];
        if (result.items) {
            result.items.forEach(function(item) {
                if (/\u043F\u043E\u0434\u0441\u0432\u0435\u0442\u043A\u0430|LED|RGB/i.test(item.name)) lightingList.push(item.name);
            });
        }
        window._calcText = [
            '\uD83C\uDFD7 \u041F\u0435\u0440\u0433\u043E\u043B\u0430: ' + result.pergola_type_name,
            '\uD83D\uDCD0 \u0420\u0430\u0437\u043C\u0435\u0440: ' + dims.width.toFixed(2) + ' \u00D7 ' + dims.length.toFixed(2) + ' \u043C',
            '\uD83D\uDD32 \u041C\u043E\u0434\u0443\u043B\u0435\u0439: ' + dims.modules,
            lightingList.length ? '\uD83D\uDCA1 \u041F\u043E\u0434\u0441\u0432\u0435\u0442\u043A\u0430: ' + lightingList.join(', ') : '',
            '',
            '\uD83D\uDCB5 \u041D\u0430\u043B\u0438\u0447\u043D\u044B\u0439 \u0440\u0430\u0441\u0447\u0451\u0442: ' + formatPrice(totals.cash) + ' \u20BD',
            '\uD83C\uDFE6 \u0411\u0435\u0437\u043D\u0430\u043B\u0438\u0447\u043D\u044B\u0439: ' + formatPrice(totals.non_cash) + ' \u20BD',
            '\uD83D\uDCCB \u0421 \u041D\u0414\u0421 22%: ' + formatPrice(totals.with_vat) + ' \u20BD',
        ].filter(Boolean).join('\n');

        var lf = document.getElementById('leadForm');
        var ls = document.getElementById('leadSuccess');
        var cb = document.getElementById('callbackBlock');
        var lb = document.getElementById('leadBtn');
        if (lf) { lf.style.display = ''; lf.classList.add('visible'); }
        if (ls) ls.classList.remove('visible');
        if (cb) cb.style.display = 'none';
        if (lb) { lb.textContent = '\u0416\u0434\u0443 \u0437\u0432\u043E\u043D\u043A\u0430'; lb.disabled = false; }
    }

    function pluralModule(n) {
        var abs = Math.abs(n) % 100;
        if (abs >= 11 && abs <= 19) return '\u043C\u043E\u0434\u0443\u043B\u0435\u0439';
        var last = abs % 10;
        if (last === 1) return '\u043C\u043E\u0434\u0443\u043B\u044C';
        if (last >= 2 && last <= 4) return '\u043C\u043E\u0434\u0443\u043B\u044F';
        return '\u043C\u043E\u0434\u0443\u043B\u0435\u0439';
    }

    function exportPdf() {
        if (!state.result) return;
        var btn = document.getElementById('pdf-btn');
        btn.disabled = true;
        btn.textContent = '\u0413\u0435\u043D\u0435\u0440\u0430\u0446\u0438\u044F PDF...';

        var pdfBody = {};
        if (state.allResults) {
            pdfBody = {results: state.allResults, mode: 'all'};
        } else {
            pdfBody = {result: state.result, mode: 'single'};
        }

        fetch('/api/export-pdf', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(pdfBody)
        })
        .then(function(r) {
            if (!r.ok) throw new Error('\u041E\u0448\u0438\u0431\u043A\u0430 \u0433\u0435\u043D\u0435\u0440\u0430\u0446\u0438\u0438 PDF');
            var disposition = r.headers.get('content-disposition');
            var filename = '\u041A\u041F_\u043F\u0435\u0440\u0433\u043E\u043B\u0430.pdf';
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
            btn.innerHTML = '<i class="bi bi-file-earmark-pdf"></i> \u0421\u043A\u0430\u0447\u0430\u0442\u044C \u041A\u041F \u0432 PDF';
        })
        .catch(function(err) {
            alert('\u041E\u0448\u0438\u0431\u043A\u0430: ' + err.message);
            btn.disabled = false;
            btn.innerHTML = '<i class="bi bi-file-earmark-pdf"></i> \u0421\u043A\u0430\u0447\u0430\u0442\u044C \u041A\u041F \u0432 PDF';
        });
    }

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
                    : g.region || '\u041D\u0435 \u043E\u043F\u0440\u0435\u0434\u0435\u043B\u0451\u043D';
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
                if (m100 >= 11 && m100 <= 14) word = '\u041F\u0415\u0420\u0413\u041E\u041B';
                else if (m10 === 1) word = '\u041F\u0415\u0420\u0413\u041E\u041B\u0410';
                else if (m10 >= 2 && m10 <= 4) word = '\u041F\u0415\u0420\u0413\u041E\u041B\u042B';
                else word = '\u041F\u0415\u0420\u0413\u041E\u041B';
                counterEl.style.background = 'linear-gradient(135deg, ' + data.counter_color + ', ' + data.counter_color + 'CC)';
                counterEl.innerHTML = '<div class="counter-number">' + n + ' ' + word + '</div><div class="counter-label">\u0443\u0441\u0442\u0430\u043D\u043E\u0432\u043B\u0435\u043D\u043E \u0432 ' + data.year + ' \u0433\u043E\u0434\u0443</div>';
            }
            if (data.badges && data.badges.length > 0) {
                var container = document.getElementById('promo-badges-container');
                if (container) {
                    var html = '';
                    data.badges.forEach(function(b) {
                        html += '<span class="promo-badge" style="background:' + (b.color || '#004B9A') + ';">' + b.text + '</span>';
                    });
                    container.innerHTML = html;
                    container.style.display = 'flex';
                }
            }
        })
        .catch(function() {});
});

var YM_ID     = 65714473;
var CALC_TYPE = 'bioclimatic';
var CALC_NAME = '\u0411\u0438\u043E\u043A\u043B\u0438\u043C\u0430\u0442\u0438\u0447\u0435\u0441\u043A\u0430\u044F \u043F\u0435\u0440\u0433\u043E\u043B\u0430';

window._calcText = '';
window._userCity = '\u041D\u0435 \u043E\u043F\u0440\u0435\u0434\u0435\u043B\u0451\u043D';

(function() {
    try {
        fetch('https://get.geojs.io/v1/ip/geo.json')
            .then(function(r) { return r.json(); })
            .then(function(g) {
                if (g && g.city) window._userCity = g.city + (g.region ? ', ' + g.region : '');
            })
            .catch(function() {});
    } catch(e) {}
})();

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
    btn.textContent = '\u041E\u0442\u043F\u0440\u0430\u0432\u043B\u044F\u0435\u043C\u2026';
    btn.disabled = true;

    fetch('/api/submit-lead', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            phone: phone,
            city: window._userCity || '\u041D\u0435 \u043E\u043F\u0440\u0435\u0434\u0435\u043B\u0451\u043D',
            calc_text: window._calcText || '',
            channel: 'callback'
        })
    }).catch(function() {});

    showOk(phone);

    try {
        if (typeof ym === 'function') ym(YM_ID, 'reachGoal', 'calculator_lead', { channel: 'callback', calculator_type: CALC_TYPE });
    } catch(e) {}
};

function showOk(phone) {
    var lf  = document.getElementById('leadForm');
    var ls  = document.getElementById('leadSuccess');
    var sub = document.getElementById('successSub');
    if (lf) { lf.classList.remove('visible'); lf.style.display = 'none'; }
    if (ls && sub) {
        sub.textContent = '\u041F\u0435\u0440\u0435\u0437\u0432\u043E\u043D\u0438\u043C \u043D\u0430 ';
        var st = document.createElement('strong');
        st.textContent = phone;
        sub.appendChild(st);
        sub.appendChild(document.createTextNode(' \u0432 \u0442\u0435\u0447\u0435\u043D\u0438\u0435 15 \u043C\u0438\u043D\u0443\u0442. \u0420\u0430\u0441\u0447\u0451\u0442 \u0443\u0436\u0435 \u0443 \u043C\u0435\u043D\u0435\u0434\u0436\u0435\u0440\u0430.'));
        ls.classList.add('visible');
    }
}

document.addEventListener('click', function(e) {
    var btn = e.target.closest('#btnTelegram, #btnMax');
    if (!btn) return;
    var ch = btn.id === 'btnTelegram' ? 'telegram' : 'max';

    try {
        if (typeof ym === 'function') ym(YM_ID, 'reachGoal', 'calculator_lead', { channel: ch, calculator_type: CALC_TYPE });
    } catch(e) {}

    var city = window._userCity || '\u041D\u0435 \u043E\u043F\u0440\u0435\u0434\u0435\u043B\u0451\u043D';
    var calcText = window._calcText || '';

    fetch('/api/submit-lead', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            phone: ch === 'telegram' ? '(Telegram)' : '(Max)',
            city: city,
            calc_text: calcText,
            channel: ch
        })
    }).catch(function() {});

    if (btn.id === 'btnTelegram') {
        e.preventDefault();
        var txt = calcText
            ? '\uD83D\uDCCD \u0413\u043E\u0440\u043E\u0434: ' + city + '\n\n\u0414\u043E\u0431\u0440\u044B\u0439 \u0434\u0435\u043D\u044C! \u0425\u043E\u0447\u0443 \u043E\u0431\u0441\u0443\u0434\u0438\u0442\u044C \u0440\u0430\u0441\u0447\u0451\u0442 \u043F\u0435\u0440\u0433\u043E\u043B\u044B:\n' + calcText
            : '\u0414\u043E\u0431\u0440\u044B\u0439 \u0434\u0435\u043D\u044C! \u0425\u043E\u0447\u0443 \u043E\u0431\u0441\u0443\u0434\u0438\u0442\u044C \u0440\u0430\u0441\u0447\u0451\u0442 \u043F\u0435\u0440\u0433\u043E\u043B\u044B.';
        var enc = encodeURIComponent(txt);
        var tgApp = 'tg://resolve?domain=comfort_dom_andrey&text=' + enc;
        var tgWeb = 'https://t.me/comfort_dom_andrey?text=' + enc;
        var _tgFallback = setTimeout(function() { window.open(tgWeb, '_blank'); }, 750);
        window.addEventListener('blur', function _tgBlur() {
            clearTimeout(_tgFallback);
            window.removeEventListener('blur', _tgBlur);
        }, { once: true });
        try { window.location.href = tgApp; } catch(ignore) {}
    }
});

(function() {
    var inp = document.getElementById('leadPhone');
    if (!inp) return;
    function digits(v) { return v.replace(/\D/g, ''); }
    function mask(raw) {
        if (!raw) return '';
        var d = raw.startsWith('8') ? '7' + raw.slice(1) : raw;
        var m = '+' + d[0];
        if (d.length > 1) m += ' (' + d.substring(1, 4);
        if (d.length > 4) m += ') ' + d.substring(4, 7);
        if (d.length > 7) m += '-' + d.substring(7, 9);
        if (d.length > 9) m += '-' + d.substring(9, 11);
        return m;
    }
    inp.addEventListener('input', function() {
        var raw = digits(inp.value).slice(0, 11);
        inp.value = mask(raw);
        inp.classList.remove('err');
    });
    inp.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') { e.preventDefault(); submitLead(); }
    });
})();
