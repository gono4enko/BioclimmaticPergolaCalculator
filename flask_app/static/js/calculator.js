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
        variantsData: null,
        clientName: ''
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
            showVideos(state.pergolaType);
            loadVariantOptions(state.pergolaType);
        });
    });

    var PERGOLA_VIDEOS = {
        'B500NEW': [
            {id: '351f7009cda5991ef24138f05f7a8692', type: 'shorts', title: '\u041F\u0435\u0440\u0433\u043E\u043B\u0430 B500 \u0432 \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u0438'},
            {id: 'df0131deee13f2a2fd945146aacaeed8', type: 'full', title: '\u041E\u0431\u0437\u043E\u0440 \u0431\u0438\u043E\u043A\u043B\u0438\u043C\u0430\u0442\u0438\u0447\u0435\u0441\u043A\u043E\u0439 \u043F\u0435\u0440\u0433\u043E\u043B\u044B'}
        ],
        'B700NEW': [
            {id: 'e51c7aaa6b00e9c125bbcdb92866b626', type: 'shorts', title: '\u041F\u0435\u0440\u0433\u043E\u043B\u0430 B700 \u2014 \u043F\u043E\u0432\u043E\u0440\u043E\u0442 \u0438 \u0441\u0434\u0432\u0438\u0433'},
            {id: 'f281d74466c7636d0e30186a7db3e70d', type: 'full', title: 'B700 \u2014 \u043F\u0440\u0435\u043C\u0438\u0430\u043B\u044C\u043D\u0430\u044F \u043F\u0435\u0440\u0433\u043E\u043B\u0430'}
        ],
        'B600': [
            {id: 'b01e73426cb0d008adbb72a544ec6f18', type: 'full', title: '\u041F\u0435\u0440\u0433\u043E\u043B\u0430 B600 \u2014 PIR \u043A\u0440\u044B\u0448\u0430'},
            {id: 'ca7d582f5793c56641c7c6c3ecef4cfa', type: 'full', title: 'B600 \u2014 \u0432\u0441\u0435\u0441\u0435\u0437\u043E\u043D\u043D\u0430\u044F \u0442\u0435\u0440\u0440\u0430\u0441\u0430'}
        ]
    };

    function showVideos(modelType) {
        var videos = PERGOLA_VIDEOS[modelType] || [];
        var grid = document.getElementById('video-grid');
        var block = document.getElementById('pergola-videos');
        if (!grid || !block) return;
        grid.innerHTML = '';
        videos.forEach(function(v) {
            var isShorts = v.type === 'shorts';
            var wrapper = document.createElement('div');
            wrapper.className = 'video-card' + (isShorts ? ' video-card-shorts' : ' video-card-full');
            wrapper.innerHTML =
                '<div class="video-iframe-wrap' + (isShorts ? ' video-iframe-shorts' : '') + '">' +
                '<iframe data-src="https://rutube.ru/play/embed/' + v.id + '" frameborder="0" allowfullscreen allow="autoplay" loading="lazy"></iframe>' +
                '</div>' +
                '<div class="video-card-title">' + v.title + '</div>';
            grid.appendChild(wrapper);
        });
        block.style.display = videos.length ? 'block' : 'none';
        initLazyIframes();
    }

    var _lazyObserver = null;
    function initLazyIframes() {
        if (!('IntersectionObserver' in window)) {
            document.querySelectorAll('iframe[data-src]').forEach(function(f) {
                f.src = f.dataset.src;
                f.removeAttribute('data-src');
            });
            return;
        }
        if (!_lazyObserver) {
            _lazyObserver = new IntersectionObserver(function(entries) {
                entries.forEach(function(entry) {
                    if (entry.isIntersecting) {
                        var iframe = entry.target;
                        iframe.src = iframe.dataset.src;
                        iframe.removeAttribute('data-src');
                        _lazyObserver.unobserve(iframe);
                    }
                });
            }, {rootMargin: '200px'});
        }
        document.querySelectorAll('iframe[data-src]').forEach(function(f) {
            _lazyObserver.observe(f);
        });
    }

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
                    if (v.hermiticity) {
                        specsHtml += '<div class="spec-row"><span class="spec-icon">\uD83D\uDCA7</span> \u0413\u0435\u0440\u043C\u0435\u0442\u0438\u0447\u043D\u043E\u0441\u0442\u044C: <strong>' + v.hermiticity + '</strong></div>';
                    }
                    if (v.snow_wind_load) {
                        specsHtml += '<div class="spec-row"><span class="spec-icon">\u2744\uFE0F</span> \u0421\u043D\u0435\u0433./\u0432\u0435\u0442\u0440. \u043D\u0430\u0433\u0440\u0443\u0437\u043A\u0430: <strong>' + v.snow_wind_load + '</strong></div>';
                    }
                    if (v.heat_protection) {
                        specsHtml += '<div class="spec-row"><span class="spec-icon">\u2600\uFE0F</span> \u0417\u0430\u0449\u0438\u0442\u0430 \u043E\u0442 \u043D\u0430\u0433\u0440\u0435\u0432\u0430: <strong>' + v.heat_protection + '</strong></div>';
                    }
                    if (v.rotation_type) {
                        var rotLabel = v.rotation_type;
                        if (v.rotation_angle) rotLabel += ' ' + v.rotation_angle;
                        specsHtml += '<div class="spec-row"><span class="spec-icon">\uD83D\uDD04</span> \u0412\u0440\u0430\u0449\u0435\u043D\u0438\u0435 \u043B\u0430\u043C\u0435\u043B\u0435\u0439: <strong>' + rotLabel + '</strong></div>';
                    }
                    if (v.opening_percent && v.opening_percent !== '\u2014') {
                        specsHtml += '<div class="spec-row"><span class="spec-icon">\u2B1C</span> \u041E\u0442\u043A\u0440\u044B\u0432\u0430\u043D\u0438\u0435 (90\u00B0): <strong>' + v.opening_percent + '</strong></div>';
                    }
                    if (v.parking_zone && v.parking_zone !== '\u2014') {
                        specsHtml += '<div class="spec-row"><span class="spec-icon">\u2B1B</span> \u041F\u0430\u0440\u043A\u043E\u0432\u043E\u0447\u043D\u0430\u044F \u0437\u043E\u043D\u0430: <strong>' + v.parking_zone + '</strong></div>';
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

        var nameInput = document.getElementById('input-client-name');
        state.clientName = nameInput ? nameInput.value.trim() : '';

        var body = {
            pergola_type: state.pergolaType,
            width: state.width,
            length: state.length,
            lamella_size: state.lamellaSize,
            lamella_type: state.lamellaType,
            lighting: lighting,
            installation: state.installation,
            selected_variant: state.selectedVariant,
            client_name: state.clientName
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
            state.kpNumber = data.kp_number || '';
            state.pergolaCount = data.pergola_count || 0;
            state.deadline = data.deadline || '';
            state.calcId = data.calc_id || '';
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
                stepsEl.resultsSection.scrollIntoView({behavior: 'smooth', block: 'start'});
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

    var SPEC_ICONS = {
        lamella: '/static/images/specs/lamella.svg',
        column: '/static/images/specs/column.svg',
        beam: '/static/images/specs/beam.svg',
        beam_double: '/static/images/specs/beam_double.svg',
        max_overhang: '/static/images/specs/max_overhang.svg'
    };

    function calcTotalWeight(weightStr, w, l) {
        if (!weightStr || !w || !l) return '';
        var m = weightStr.match(/([\d.,]+)/);
        if (!m) return '';
        var kgPerM2 = parseFloat(m[1].replace(',', '.'));
        if (isNaN(kgPerM2)) return '';
        var total = Math.round(kgPerM2 * w * l);
        return total + ' \u043A\u0433';
    }

    function buildSpecsTable(variantsData) {
        if (!variantsData) return '';
        var specsHtml = '<h4 style="font-size:1rem;font-weight:600;color:#004B9A;margin-top:1.2rem;">\u0422\u0435\u0445\u043D\u0438\u0447\u0435\u0441\u043A\u0438\u0435 \u0445\u0430\u0440\u0430\u043A\u0442\u0435\u0440\u0438\u0441\u0442\u0438\u043A\u0438</h4>';

        var hasImages = variantsData.some(function(v) { return v.images && (v.images.skl || v.images.lamella); });
        if (hasImages) {
            specsHtml += '<div class="compare-table-wrap"><table class="compare-specs-table">';
            specsHtml += '<thead><tr><th colspan="2">\u0421\u0438\u0441\u0442\u0435\u043C\u0430 \u043A\u0440\u0435\u043F\u043B\u0435\u043D\u0438\u044F \u043B\u0430\u043C\u0435\u043B\u0438</th>';
            variantsData.forEach(function(v) { specsHtml += '<th>' + v.label + '</th>'; });
            specsHtml += '</tr></thead><tbody><tr><td colspan="2"></td>';
            variantsData.forEach(function(v) {
                var img = (v.images && v.images.skl) || '';
                specsHtml += '<td class="spec-photo-cell">' + (img ? '<img src="' + img + '" class="spec-photo" alt="\u0421\u041A\u041B">' : '\u2014') + '</td>';
            });
            specsHtml += '</tr>';
            specsHtml += '<tr><td colspan="2"><strong>\u041B\u0430\u043C\u0435\u043B\u044C</strong></td>';
            variantsData.forEach(function(v) {
                var img = (v.images && v.images.lamella) || '';
                specsHtml += '<td class="spec-photo-cell">' + (img ? '<img src="' + img + '" class="spec-photo" alt="\u041B\u0430\u043C\u0435\u043B\u044C"><br>' : '') + '<span class="spec-photo-label">' + (v.lamella || '\u2014') + '</span></td>';
            });
            specsHtml += '</tr>';
            specsHtml += '<tr><td colspan="2"><strong>\u0411\u0430\u043B\u043A\u0430 \u0441 \u0438\u043D\u0442\u0435\u0433\u0440. \u043B\u043E\u0442\u043A\u043E\u043C</strong></td>';
            variantsData.forEach(function(v) {
                var img = (v.images && v.images.beam) || '';
                specsHtml += '<td class="spec-photo-cell">' + (img ? '<img src="' + img + '" class="spec-photo" alt="\u0411\u0430\u043B\u043A\u0430"><br>' : '') + '<span class="spec-photo-label">' + (v.beam || '\u2014') + '</span></td>';
            });
            specsHtml += '</tr></tbody></table></div>';
        }

        specsHtml += '<div class="compare-table-wrap"><table class="compare-specs-table">';
        specsHtml += '<thead><tr><th>\u041F\u0430\u0440\u0430\u043C\u0435\u0442\u0440</th>';
        variantsData.forEach(function(v) { specsHtml += '<th>' + v.label + '</th>'; });
        specsHtml += '</tr></thead><tbody>';

        var specRows = [
            {key: 'lamella', label: '\u041B\u0430\u043C\u0435\u043B\u044C'},
            {key: 'column', label: '\u041A\u043E\u043B\u043E\u043D\u043D\u0430'},
            {key: 'beam', label: '\u0411\u0430\u043B\u043A\u0430'},
            {key: 'beam_double', label: '\u0411\u0430\u043B\u043A\u0430 \u0434\u0432\u0443\u0445\u0441\u0442.'},
            {key: 'max_overhang', label: '\u041C\u0430\u043A\u0441. \u0432\u044B\u043B\u0435\u0442', suffix: ' \u043C'},
            {key: 'max_module_width', label: '\u041C\u0430\u043A\u0441. \u0448\u0438\u0440\u0438\u043D\u0430 \u043C\u043E\u0434\u0443\u043B\u044F', suffix: ' \u043C'},
            {key: 'weight', label: '\u0412\u0435\u0441 \u043A\u043E\u043D\u0441\u0442\u0440\u0443\u043A\u0446\u0438\u0438 (\u043A\u0433/\u043C\u00B2)'},
            {key: '_total_weight', label: '\u0412\u0435\u0441 \u0440\u0430\u0441\u0441\u0447\u0438\u0442\u0430\u043D\u043D\u043E\u0439 \u043C\u043E\u0434\u0435\u043B\u0438', computed: true},
            {key: 'snow_wind_load', label: '\u0421\u043D\u0435\u0433\u043E\u0432\u0430\u044F \u0438 \u0432\u0435\u0442\u0440\u043E\u0432\u0430\u044F \u043D\u0430\u0433\u0440\u0443\u0437\u043A\u0430'},
            {key: 'hermiticity', label: '\u0413\u0435\u0440\u043C\u0435\u0442\u0438\u0447\u043D\u043E\u0441\u0442\u044C'},
            {key: 'heat_protection', label: '\u0417\u0430\u0449\u0438\u0442\u0430 \u043E\u0442 \u043D\u0430\u0433\u0440\u0435\u0432\u0430'},
            {key: '_rotation', label: '\u0412\u0440\u0430\u0449\u0435\u043D\u0438\u0435 \u043B\u0430\u043C\u0435\u043B\u0435\u0439', computed: true},
            {key: 'opening_percent', label: '\u041E\u0442\u043A\u0440\u044B\u0432\u0430\u043D\u0438\u0435 (90\u00B0)'},
            {key: 'parking_zone', label: '\u041F\u0430\u0440\u043A\u043E\u0432\u043E\u0447\u043D\u0430\u044F \u0437\u043E\u043D\u0430'},
            {key: 'max_structure_size', label: '\u041C\u0430\u043A\u0441. \u0440\u0430\u0437\u043C\u0435\u0440 \u043D\u0430 4 \u043E\u043F\u043E\u0440\u0430\u0445', suffix: ' \u043C'},
            {key: 'frame_rigidity', label: '\u0416\u0451\u0441\u0442\u043A\u043E\u0441\u0442\u044C \u043E\u0431\u0432\u044F\u0437\u043A\u0438'}
        ];
        specRows.forEach(function(sr) {
            specsHtml += '<tr><td><strong>' + sr.label + '</strong></td>';
            variantsData.forEach(function(v) {
                var val;
                if (sr.computed && sr.key === '_total_weight') {
                    val = calcTotalWeight(v.weight, state.width, state.length);
                } else if (sr.computed && sr.key === '_rotation') {
                    val = v.rotation_type || '';
                    if (v.rotation_angle) val += ' ' + v.rotation_angle;
                } else {
                    val = v[sr.key];
                    if (sr.suffix && val && typeof val === 'number') val = val + sr.suffix;
                }
                specsHtml += '<td>' + (val || '\u2014') + '</td>';
            });
            specsHtml += '</tr>';
        });
        specsHtml += '</tbody></table></div>';
        return specsHtml;
    }

    function buildVariantDetail(result) {
        var dims = result.dimensions;
        var totals = result.totals;
        var euroRate = result.euro_rate;
        var label = result.variant_label || result.selected_variant || '';

        var html = '<div class="variant-detail-panel">';
        html += '<div class="variant-detail-header">\u0420\u0435\u0437\u0443\u043B\u044C\u0442\u0430\u0442\u044B \u0440\u0430\u0441\u0447\u0451\u0442\u0430: ' + label + '</div>';

        html += '<div style="text-align:center;margin-bottom:0.6rem;color:#555;font-size:0.85rem;">' +
            '<strong>' + result.pergola_type_name + '</strong> | ' +
            dims.width.toFixed(2) + ' \u00D7 ' + dims.length.toFixed(2) + ' \u043C | ' +
            dims.modules + ' ' + pluralModule(dims.modules) +
            '</div>';

        html += '<h4 style="font-size:0.95rem;font-weight:600;color:#004B9A;margin-top:0.8rem;">\u0421\u043F\u0435\u0446\u0438\u0444\u0438\u043A\u0430\u0446\u0438\u044F</h4>';
        html += '<table class="spec-table"><thead><tr><th>\u041D\u0430\u0438\u043C\u0435\u043D\u043E\u0432\u0430\u043D\u0438\u0435</th><th>\u041A\u043E\u043B\u0438\u0447\u0435\u0441\u0442\u0432\u043E</th></tr></thead><tbody>';
        result.specification.forEach(function(s) {
            html += '<tr><td>' + s.name + '</td><td>' + s.count + '</td></tr>';
        });
        html += '</tbody></table>';

        html += '<h4 style="font-size:0.95rem;font-weight:600;color:#004B9A;margin-top:0.8rem;">\u0421\u0442\u043E\u0438\u043C\u043E\u0441\u0442\u044C</h4>';
        html += '<table class="cost-table"><tbody>';
        result.items.forEach(function(item) {
            var priceRub = Math.round(item.price * euroRate);
            html += '<tr><td>' + item.name + '</td><td>' + formatPrice(priceRub) + ' \u20BD</td></tr>';
        });
        html += '</tbody></table>';

        html += '<div class="payment-variants-block">' +
            '<div class="payment-variants-title">\u0421\u0442\u043E\u0438\u043C\u043E\u0441\u0442\u044C \u043F\u043E \u0432\u0430\u0440\u0438\u0430\u043D\u0442\u0430\u043C \u043E\u043F\u043B\u0430\u0442\u044B:</div>' +
            '<div class="payment-variant-row">' +
                '<span class="payment-variant-label">\u041D\u0430\u043B\u0438\u0447\u043D\u044B\u0435</span>' +
                '<span class="payment-variant-price pv-cash">' + formatPrice(totals.cash) + ' \u20BD</span>' +
            '</div>' +
            '<div class="payment-variant-row">' +
                '<span class="payment-variant-label">\u0411\u0435\u0437\u043D\u0430\u043B\u0438\u0447\u043D\u044B\u0439 \u0440\u0430\u0441\u0447\u0451\u0442</span>' +
                '<span class="payment-variant-price">' + formatPrice(totals.non_cash) + ' \u20BD</span>' +
            '</div>' +
            '<div class="payment-variant-row pv-last">' +
                '<span class="payment-variant-label">\u0411\u0435\u0437\u043D\u0430\u043B\u0438\u0447\u043D\u044B\u0439 \u0441 \u041D\u0414\u0421 22%</span>' +
                '<span class="payment-variant-price">' + formatPrice(totals.with_vat) + ' \u20BD</span>' +
            '</div>' +
        '</div>';

        if (result.selected_variant && state.variantsData) {
            var sv = result.selected_variant;
            var sls = state.lamellaSize || '';
            var matchedSpec = null;
            state.variantsData.forEach(function(v) {
                if (v.variant === sv && (!sls || v.lamella_size === sls)) matchedSpec = v;
            });
            if (!matchedSpec) {
                state.variantsData.forEach(function(v) {
                    if (v.variant === sv) matchedSpec = v;
                });
            }
            if (matchedSpec) {
                html += '<div class="variant-tech-block">' +
                    '<div class="variant-tech-title">\u0422\u0435\u0445\u043D\u0438\u0447\u0435\u0441\u043A\u0438\u0435 \u0445\u0430\u0440\u0430\u043A\u0442\u0435\u0440\u0438\u0441\u0442\u0438\u043A\u0438 (' + matchedSpec.label + ')</div>';
                var imgs = matchedSpec.images || {};
                if (imgs.skl || imgs.lamella || imgs.beam) {
                    html += '<div class="tech-photos-row">';
                    if (imgs.skl) html += '<div class="tech-photo-item"><img src="' + imgs.skl + '" class="tech-photo" alt="\u0421\u041A\u041B"><div class="tech-photo-caption">\u0421\u0438\u0441\u0442\u0435\u043C\u0430 \u043A\u0440\u0435\u043F\u043B\u0435\u043D\u0438\u044F</div></div>';
                    if (imgs.lamella) html += '<div class="tech-photo-item"><img src="' + imgs.lamella + '" class="tech-photo" alt="\u041B\u0430\u043C\u0435\u043B\u044C"><div class="tech-photo-caption">\u041B\u0430\u043C\u0435\u043B\u044C ' + matchedSpec.lamella + '</div></div>';
                    if (imgs.beam) html += '<div class="tech-photo-item"><img src="' + imgs.beam + '" class="tech-photo" alt="\u0411\u0430\u043B\u043A\u0430"><div class="tech-photo-caption">\u0411\u0430\u043B\u043A\u0430 ' + matchedSpec.beam + '</div></div>';
                    html += '</div>';
                }
                html += '<div class="variant-tech-specs">';
                var techItems = [
                    {icon: SPEC_ICONS.lamella, label: '\u041B\u0430\u043C\u0435\u043B\u044C', val: matchedSpec.lamella},
                    {icon: SPEC_ICONS.column, label: '\u041A\u043E\u043B\u043E\u043D\u043D\u0430', val: matchedSpec.column},
                    {icon: SPEC_ICONS.beam, label: '\u0411\u0430\u043B\u043A\u0430', val: matchedSpec.beam},
                    {icon: SPEC_ICONS.beam_double, label: '\u0411\u0430\u043B\u043A\u0430 \u0434\u0432\u0443\u0445\u0441\u0442.', val: matchedSpec.beam_double},
                    {icon: SPEC_ICONS.max_overhang, label: '\u041C\u0430\u043A\u0441. \u0432\u044B\u043B\u0435\u0442', val: matchedSpec.max_overhang ? matchedSpec.max_overhang + ' \u043C' : ''},
                    {icon: '', label: '\u041C\u0430\u043A\u0441. \u0448\u0438\u0440\u0438\u043D\u0430 \u043C\u043E\u0434\u0443\u043B\u044F', val: matchedSpec.max_module_width ? matchedSpec.max_module_width + ' \u043C' : ''},
                    {icon: '', label: '\u0412\u0435\u0441 \u043A\u043E\u043D\u0441\u0442\u0440\u0443\u043A\u0446\u0438\u0438', val: matchedSpec.weight},
                    {icon: '', label: '\u0412\u0435\u0441 \u043C\u043E\u0434\u0435\u043B\u0438', val: calcTotalWeight(matchedSpec.weight, dims.width, dims.length)},
                    {icon: '', label: '\u0421\u043D\u0435\u0433./\u0432\u0435\u0442\u0440. \u043D\u0430\u0433\u0440\u0443\u0437\u043A\u0430', val: matchedSpec.snow_wind_load},
                    {icon: '', label: '\u0413\u0435\u0440\u043C\u0435\u0442\u0438\u0447\u043D\u043E\u0441\u0442\u044C', val: matchedSpec.hermiticity},
                    {icon: '', label: '\u0417\u0430\u0449\u0438\u0442\u0430 \u043E\u0442 \u043D\u0430\u0433\u0440\u0435\u0432\u0430', val: matchedSpec.heat_protection},
                    {icon: '', label: '\u0412\u0440\u0430\u0449\u0435\u043D\u0438\u0435 \u043B\u0430\u043C\u0435\u043B\u0435\u0439', val: (matchedSpec.rotation_type || '') + (matchedSpec.rotation_angle ? ' ' + matchedSpec.rotation_angle : '')},
                    {icon: '', label: '\u041E\u0442\u043A\u0440\u044B\u0432\u0430\u043D\u0438\u0435 (90\u00B0)', val: matchedSpec.opening_percent && matchedSpec.opening_percent !== '\u2014' ? matchedSpec.opening_percent : ''},
                    {icon: '', label: '\u041F\u0430\u0440\u043A\u043E\u0432\u043E\u0447\u043D\u0430\u044F \u0437\u043E\u043D\u0430', val: matchedSpec.parking_zone && matchedSpec.parking_zone !== '\u2014' ? matchedSpec.parking_zone : ''},
                    {icon: '', label: '\u041C\u0430\u043A\u0441. \u0440\u0430\u0437\u043C\u0435\u0440 \u043D\u0430 4 \u043E\u043F\u043E\u0440\u0430\u0445', val: matchedSpec.max_structure_size ? matchedSpec.max_structure_size + ' \u043C' : ''},
                    {icon: '', label: '\u0416\u0451\u0441\u0442\u043A\u043E\u0441\u0442\u044C \u043E\u0431\u0432\u044F\u0437\u043A\u0438', val: matchedSpec.frame_rigidity}
                ];
                techItems.forEach(function(ti) {
                    if (ti.val) {
                        html += '<div class="tech-spec-row">';
                        if (ti.icon) html += '<img src="' + ti.icon + '" alt="' + ti.label + '" class="tech-spec-icon">';
                        html += '<span>' + ti.label + ': <strong>' + ti.val + '</strong></span></div>';
                    }
                });
                html += '</div></div>';
            }
        }

        html += '</div>';
        return html;
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
            tableHtml += '<tr class="compare-row-clickable' + (idx === 0 ? ' compare-row-best' : '') + '" data-variant-idx="' + idx + '">';
            tableHtml += '<td><strong>' + label + '</strong>' + diffHtml + '</td>';
            tableHtml += '<td>' + formatPrice(r.totals.cash) + ' \u20BD</td>';
            tableHtml += '<td>' + formatPrice(r.totals.non_cash) + ' \u20BD</td>';
            tableHtml += '<td>' + formatPrice(r.totals.with_vat) + ' \u20BD</td>';
            tableHtml += '</tr>';
        });
        tableHtml += '</tbody></table></div>';
        tableHtml += '<div class="compare-hint">\u041D\u0430\u0436\u043C\u0438\u0442\u0435 \u043D\u0430 \u0441\u0442\u0440\u043E\u043A\u0443, \u0447\u0442\u043E\u0431\u044B \u0443\u0432\u0438\u0434\u0435\u0442\u044C \u043F\u043E\u0434\u0440\u043E\u0431\u043D\u044B\u0439 \u0440\u0430\u0441\u0447\u0451\u0442</div>';

        var specsHtml = buildSpecsTable(state.variantsData);

        sec.innerHTML = '<h3>\u0421\u0440\u0430\u0432\u043D\u0435\u043D\u0438\u0435 \u0432\u0430\u0440\u0438\u0430\u043D\u0442\u043E\u0432</h3>' +
            infoHtml + tableHtml + specsHtml +
            '<div id="variant-detail-container"></div>' +
            '<div class="kp-actions-row"><button class="pdf-btn" id="pdf-btn"><i class="bi bi-file-earmark-pdf"></i> \u0421\u043A\u0430\u0447\u0430\u0442\u044C \u041A\u041F \u0432 PDF</button>' +
            '<button class="share-btn" id="share-btn" title="\u041F\u043E\u0434\u0435\u043B\u0438\u0442\u044C\u0441\u044F"><i class="bi bi-share"></i> \u041F\u043E\u0434\u0435\u043B\u0438\u0442\u044C\u0441\u044F</button></div>' +
            '<div id="marketing-kp-container"></div>';

        document.getElementById('pdf-btn').addEventListener('click', exportPdf);
        document.getElementById('share-btn').addEventListener('click', shareKp);

        var rows = sec.querySelectorAll('.compare-row-clickable');
        rows.forEach(function(row) {
            row.addEventListener('click', function() {
                var idx = parseInt(this.dataset.variantIdx);
                var r = results[idx];
                rows.forEach(function(rw) { rw.classList.remove('compare-row-active'); });
                this.classList.add('compare-row-active');
                state.result = r;
                var container = document.getElementById('variant-detail-container');
                container.innerHTML = buildVariantDetail(r);
                setTimeout(function() {
                    container.scrollIntoView({behavior: 'smooth', block: 'start'});
                }, 100);
            });
        });

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

        loadDecoDataAndRender(results);
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
            var sls = state.lamellaSize || '';
            var matchedSpec = null;
            state.variantsData.forEach(function(v) {
                if (v.variant === sv && (!sls || v.lamella_size === sls)) matchedSpec = v;
            });
            if (!matchedSpec) {
                state.variantsData.forEach(function(v) {
                    if (v.variant === sv) matchedSpec = v;
                });
            }
            if (matchedSpec) {
                variantSpecHtml = '<div class="variant-tech-block">' +
                    '<div class="variant-tech-title">\u0422\u0435\u0445\u043D\u0438\u0447\u0435\u0441\u043A\u0438\u0435 \u0445\u0430\u0440\u0430\u043A\u0442\u0435\u0440\u0438\u0441\u0442\u0438\u043A\u0438 (' + matchedSpec.label + ')</div>';
                var sImgs = matchedSpec.images || {};
                if (sImgs.skl || sImgs.lamella || sImgs.beam) {
                    variantSpecHtml += '<div class="tech-photos-row">';
                    if (sImgs.skl) variantSpecHtml += '<div class="tech-photo-item"><img src="' + sImgs.skl + '" class="tech-photo" alt="\u0421\u041A\u041B"><div class="tech-photo-caption">\u0421\u0438\u0441\u0442\u0435\u043C\u0430 \u043A\u0440\u0435\u043F\u043B\u0435\u043D\u0438\u044F</div></div>';
                    if (sImgs.lamella) variantSpecHtml += '<div class="tech-photo-item"><img src="' + sImgs.lamella + '" class="tech-photo" alt="\u041B\u0430\u043C\u0435\u043B\u044C"><div class="tech-photo-caption">\u041B\u0430\u043C\u0435\u043B\u044C ' + matchedSpec.lamella + '</div></div>';
                    if (sImgs.beam) variantSpecHtml += '<div class="tech-photo-item"><img src="' + sImgs.beam + '" class="tech-photo" alt="\u0411\u0430\u043B\u043A\u0430"><div class="tech-photo-caption">\u0411\u0430\u043B\u043A\u0430 ' + matchedSpec.beam + '</div></div>';
                    variantSpecHtml += '</div>';
                }
                variantSpecHtml += '<div class="variant-tech-specs">';
                var techItems = [
                    {icon: SPEC_ICONS.lamella, label: '\u041B\u0430\u043C\u0435\u043B\u044C', val: matchedSpec.lamella},
                    {icon: SPEC_ICONS.column, label: '\u041A\u043E\u043B\u043E\u043D\u043D\u0430', val: matchedSpec.column},
                    {icon: SPEC_ICONS.beam, label: '\u0411\u0430\u043B\u043A\u0430', val: matchedSpec.beam},
                    {icon: SPEC_ICONS.beam_double, label: '\u0411\u0430\u043B\u043A\u0430 \u0434\u0432\u0443\u0445\u0441\u0442.', val: matchedSpec.beam_double},
                    {icon: SPEC_ICONS.max_overhang, label: '\u041C\u0430\u043A\u0441. \u0432\u044B\u043B\u0435\u0442', val: matchedSpec.max_overhang ? matchedSpec.max_overhang + ' \u043C' : ''},
                    {icon: '', label: '\u041C\u0430\u043A\u0441. \u0448\u0438\u0440\u0438\u043D\u0430 \u043C\u043E\u0434\u0443\u043B\u044F', val: matchedSpec.max_module_width ? matchedSpec.max_module_width + ' \u043C' : ''},
                    {icon: '', label: '\u0412\u0435\u0441 \u043A\u043E\u043D\u0441\u0442\u0440\u0443\u043A\u0446\u0438\u0438', val: matchedSpec.weight},
                    {icon: '', label: '\u0412\u0435\u0441 \u043C\u043E\u0434\u0435\u043B\u0438', val: calcTotalWeight(matchedSpec.weight, dims.width, dims.length)},
                    {icon: '', label: '\u0421\u043D\u0435\u0433./\u0432\u0435\u0442\u0440. \u043D\u0430\u0433\u0440\u0443\u0437\u043A\u0430', val: matchedSpec.snow_wind_load},
                    {icon: '', label: '\u0413\u0435\u0440\u043C\u0435\u0442\u0438\u0447\u043D\u043E\u0441\u0442\u044C', val: matchedSpec.hermiticity},
                    {icon: '', label: '\u0417\u0430\u0449\u0438\u0442\u0430 \u043E\u0442 \u043D\u0430\u0433\u0440\u0435\u0432\u0430', val: matchedSpec.heat_protection},
                    {icon: '', label: '\u0412\u0440\u0430\u0449\u0435\u043D\u0438\u0435 \u043B\u0430\u043C\u0435\u043B\u0435\u0439', val: (matchedSpec.rotation_type || '') + (matchedSpec.rotation_angle ? ' ' + matchedSpec.rotation_angle : '')},
                    {icon: '', label: '\u041E\u0442\u043A\u0440\u044B\u0432\u0430\u043D\u0438\u0435 (90\u00B0)', val: matchedSpec.opening_percent && matchedSpec.opening_percent !== '\u2014' ? matchedSpec.opening_percent : ''},
                    {icon: '', label: '\u041F\u0430\u0440\u043A\u043E\u0432\u043E\u0447\u043D\u0430\u044F \u0437\u043E\u043D\u0430', val: matchedSpec.parking_zone && matchedSpec.parking_zone !== '\u2014' ? matchedSpec.parking_zone : ''},
                    {icon: '', label: '\u041C\u0430\u043A\u0441. \u0440\u0430\u0437\u043C\u0435\u0440 \u043D\u0430 4 \u043E\u043F\u043E\u0440\u0430\u0445', val: matchedSpec.max_structure_size ? matchedSpec.max_structure_size + ' \u043C' : ''},
                    {icon: '', label: '\u0416\u0451\u0441\u0442\u043A\u043E\u0441\u0442\u044C \u043E\u0431\u0432\u044F\u0437\u043A\u0438', val: matchedSpec.frame_rigidity}
                ];
                techItems.forEach(function(ti) {
                    if (ti.val) {
                        variantSpecHtml += '<div class="tech-spec-row">';
                        if (ti.icon) variantSpecHtml += '<img src="' + ti.icon + '" alt="' + ti.label + '" class="tech-spec-icon">';
                        variantSpecHtml += '<span>' + ti.label + ': <strong>' + ti.val + '</strong></span></div>';
                    }
                });
                variantSpecHtml += '</div></div>';
            }
        }

        var infoHtml = '<div style="text-align:center;margin-bottom:0.8rem;color:#555;font-size:0.9rem;">' +
            '<strong>' + result.pergola_type_name + '</strong> | ' +
            dims.width.toFixed(2) + ' \u00D7 ' + dims.length.toFixed(2) + ' \u043C | ' +
            dims.modules + ' ' + pluralModule(dims.modules) +
            '</div>';

        state._variantSpecHtml = variantSpecHtml;

        sec.innerHTML = '<div class="kp-actions-row"><button class="pdf-btn" id="pdf-btn"><i class="bi bi-file-earmark-pdf"></i> \u0421\u043A\u0430\u0447\u0430\u0442\u044C \u041A\u041F \u0432 PDF</button>' +
            '<button class="share-btn" id="share-btn" title="\u041F\u043E\u0434\u0435\u043B\u0438\u0442\u044C\u0441\u044F"><i class="bi bi-share"></i> \u041F\u043E\u0434\u0435\u043B\u0438\u0442\u044C\u0441\u044F</button></div>' +
            '<div id="marketing-kp-container"></div>';

        document.getElementById('pdf-btn').addEventListener('click', exportPdf);
        document.getElementById('share-btn').addEventListener('click', shareKp);

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

        loadDecoDataAndRender(result);
    }

    function escHtml(s) {
        if (!s) return '';
        return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    }

    function buildMarketingKP(resultOrResults, decoData) {
        var isAll = Array.isArray(resultOrResults);
        var mainResult = isAll ? resultOrResults[0] : resultOrResults;
        var dims = mainResult.dimensions;
        var totals = mainResult.totals;
        var pType = mainResult.pergola_type_name || state.pergolaType;
        var area = (dims.width * dims.length).toFixed(1);
        var clientName = escHtml(state.clientName || '');
        var greeting = clientName ? (clientName + ', ') : '';
        var dd = decoData || {};
        var kpNum = state.kpNumber || '';
        var pergolaCount = state.pergolaCount || 0;
        var deadlineStr = state.deadline || '';
        var html = '<div class="kp-section">';

        var kpDate = new Date().toLocaleDateString('ru-RU');
        var decoKeyMap = {'B500NEW': 'b500', 'B700NEW': 'b700', 'B600': 'b600'};
        var decoKey = decoKeyMap[state.pergolaType] || '';
        var modelImgMap = {'B500NEW': 'b500.jpg', 'B700NEW': 'b700.jpg', 'B600': 'b600.jpg'};
        var modelImg = modelImgMap[state.pergolaType] || 'hero_pergola.jpg';

        /* Block 1: KP header — number, date, greeting */
        html += '<div class="kp-block" style="text-align:center;">' +
            '<div class="kp-number-badge">' + escHtml(kpNum) + '</div>' +
            '<h3 style="font-size:1.2rem;font-weight:700;color:#1a3a6e;margin:0.5rem 0 0.3rem;">' + greeting + '\u0432\u0430\u0448\u0435 \u043A\u043E\u043C\u043C\u0435\u0440\u0447\u0435\u0441\u043A\u043E\u0435 \u043F\u0440\u0435\u0434\u043B\u043E\u0436\u0435\u043D\u0438\u0435</h3>' +
            '<p style="font-size:0.88rem;color:#666;margin:0;">' + pType + ' | ' + dims.width.toFixed(2) + ' \u00D7 ' + dims.length.toFixed(2) + ' \u043C (' + area + ' \u043C\u00B2)</p>' +
            '<p style="font-size:0.82rem;color:#999;margin:0.3rem 0 0;">\u0414\u0430\u0442\u0430: ' + kpDate + (deadlineStr ? ' | \u0414\u0435\u0439\u0441\u0442\u0432\u0438\u0442\u0435\u043B\u044C\u043D\u043E \u0434\u043E ' + deadlineStr : ' | \u0414\u0435\u0439\u0441\u0442\u0432\u0438\u0442\u0435\u043B\u044C\u043D\u043E 14 \u0434\u043D\u0435\u0439') + '</p>' +
            '</div>';

        /* Block 2: Price hero with urgency + 80/20 */
        html += '<div class="kp-price-hero">' +
            '<div class="kp-urgency-banner" style="margin-bottom:0.8rem;">' +
            '<span class="kp-urgency-icon">\u23F0</span>' +
            '<span>\u0426\u0435\u043D\u044B \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u0442\u0435\u043B\u044C\u043D\u044B ' + (deadlineStr ? '\u0434\u043E <strong>' + deadlineStr + '</strong>' : '<strong>14 \u0434\u043D\u0435\u0439</strong>') + '</span>' +
            '</div>' +
            '<div class="kp-price-label">\u0421\u0442\u043E\u0438\u043C\u043E\u0441\u0442\u044C \u043F\u0435\u0440\u0433\u043E\u043B\u044B (\u043D\u0430\u043B\u0438\u0447\u043D\u044B\u0439 \u0440\u0430\u0441\u0447\u0451\u0442)</div>' +
            '<div class="kp-price-sublabel">\u0434\u043B\u044F \u0444\u0438\u0437\u0438\u0447\u0435\u0441\u043A\u0438\u0445 \u043B\u0438\u0446</div>' +
            '<div class="kp-price-amount">' + formatPrice(totals.cash) + ' \u20BD</div>' +
            '<div class="kp-price-label" style="margin-top:10px;">\u0411\u0435\u0437\u043D\u0430\u043B: ' + formatPrice(totals.non_cash) + ' \u20BD <span class="kp-price-sublabel">\u0434\u043B\u044F \u0418\u041F \u0438 \u041E\u041E\u041E \u0431\u0435\u0437 \u041D\u0414\u0421</span></div>' +
            '<div class="kp-price-label" style="margin-top:4px;">\u0421 \u041D\u0414\u0421: ' + formatPrice(totals.with_vat) + ' \u20BD <span class="kp-price-sublabel">\u0434\u043B\u044F \u041E\u041E\u041E \u2014 \u043F\u043B\u0430\u0442\u0435\u043B\u044C\u0449\u0438\u043A\u043E\u0432 \u041D\u0414\u0421</span></div>' +
            '<div class="kp-payment-terms">' +
            '<strong>\u0423\u0441\u043B\u043E\u0432\u0438\u044F:</strong> 80% \u043F\u043E\u0441\u043B\u0435 \u043F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043D\u0438\u044F \u0437\u0430\u043A\u0430\u0437\u0430 \u2014 \u043C\u044B \u0437\u0430\u043F\u0443\u0441\u043A\u0430\u0435\u043C \u043F\u0440\u043E\u0438\u0437\u0432\u043E\u0434\u0441\u0442\u0432\u043E; 20% \u043F\u043E\u0441\u043B\u0435 \u0437\u0430\u0432\u0435\u0440\u0448\u0435\u043D\u0438\u044F \u043C\u043E\u043D\u0442\u0430\u0436\u0430 \u0438 \u0432\u0430\u0448\u0435\u0439 \u043F\u0440\u0438\u0451\u043C\u043A\u0438' +
            '</div></div>';

        /* Block 3: Model info with product photo from Decolife */
        html += '<div class="kp-block">' +
            '<div class="kp-block-header"><div class="kp-block-icon" style="background:#1a3a6e;">\u2139</div><div class="kp-block-title">\u041E \u043C\u043E\u0434\u0435\u043B\u0438 ' + escHtml(dd.model || pType) + '</div></div>' +
            '<div class="kp-model-photo"><img src="' + (decoKey ? '/static/decolife/' + decoKey + '/images/product.jpg' : '/static/images/' + modelImg) + '" alt="' + escHtml(dd.model || pType) + '" onerror="this.src=\'/static/images/' + modelImg + '\';this.onerror=function(){this.parentElement.style.display=\'none\';}" style="width:100%;max-height:200px;object-fit:cover;border-radius:8px;margin-bottom:0.8rem;"></div>';
        if (dd.description) {
            html += '<p>' + escHtml(dd.description) + '</p>';
        }
        if (dd.production) {
            html += '<p style="margin-top:0.5rem;font-size:0.85rem;color:#555;"><em>' + escHtml(dd.production) + '</em></p>';
        }
        html += '</div>';

        /* Block 4: Key features */
        if (dd.features && dd.features.length) {
            html += '<div class="kp-block">' +
                '<div class="kp-block-header"><div class="kp-block-icon" style="background:#2e7d32;">\u2605</div><div class="kp-block-title">\u041A\u043B\u044E\u0447\u0435\u0432\u044B\u0435 \u043E\u0441\u043E\u0431\u0435\u043D\u043D\u043E\u0441\u0442\u0438</div></div>' +
                '<div class="kp-features-grid">';
            dd.features.forEach(function(f) {
                html += '<div class="kp-feature-item"><span class="kp-feature-check">\u2713</span><div><strong>' + escHtml(f.title) + '</strong><br>' + escHtml(f.text) + '</div></div>';
            });
            html += '</div></div>';
        }

        /* Block 5: Advantages */
        if (dd.advantages && dd.advantages.length) {
            html += '<div class="kp-block">' +
                '<div class="kp-block-header"><div class="kp-block-icon" style="background:#f59e0b;">\u2B50</div><div class="kp-block-title">\u041F\u0440\u0435\u0438\u043C\u0443\u0449\u0435\u0441\u0442\u0432\u0430</div></div>' +
                '<ul>';
            dd.advantages.forEach(function(a) { html += '<li>' + escHtml(a) + '</li>'; });
            html += '</ul></div>';
        }

        /* Block 7: Specification with micro-explanations */
        var specHints = {
            '\u041A\u043E\u043B\u043E\u043D\u043D\u0430': '\u041D\u0435\u0441\u0443\u0449\u0438\u0435 \u043E\u043F\u043E\u0440\u044B \u0438\u0437 \u0430\u043B\u044E\u043C\u0438\u043D\u0438\u044F, \u043E\u043A\u0440\u0430\u0448\u0435\u043D\u043D\u044B\u0435 \u043F\u043E\u0440\u043E\u0448\u043A\u043E\u0432\u044B\u043C \u043C\u0435\u0442\u043E\u0434\u043E\u043C',
            '\u0411\u0430\u043B\u043A\u0430': '\u041E\u0441\u043D\u043E\u0432\u043D\u043E\u0439 \u043D\u0435\u0441\u0443\u0449\u0438\u0439 \u044D\u043B\u0435\u043C\u0435\u043D\u0442 \u0441 \u0438\u043D\u0442\u0435\u0433\u0440\u0438\u0440\u043E\u0432\u0430\u043D\u043D\u044B\u043C \u0432\u043E\u0434\u043E\u043E\u0442\u0432\u043E\u0434\u043E\u043C',
            '\u041B\u0430\u043C\u0435\u043B': '\u041F\u043E\u0432\u043E\u0440\u043E\u0442\u043D\u044B\u0435 \u044D\u043B\u0435\u043C\u0435\u043D\u0442\u044B \u043A\u0440\u044B\u0448\u0438 \u0434\u043B\u044F \u0440\u0435\u0433\u0443\u043B\u0438\u0440\u043E\u0432\u043A\u0438 \u0441\u0432\u0435\u0442\u0430 \u0438 \u0432\u0435\u043D\u0442\u0438\u043B\u044F\u0446\u0438\u0438',
            '\u041B\u043E\u0442\u043E\u043A': '\u042D\u043B\u0435\u043C\u0435\u043D\u0442 \u0441\u0438\u0441\u0442\u0435\u043C\u044B \u0432\u043E\u0434\u043E\u043E\u0442\u0432\u0435\u0434\u0435\u043D\u0438\u044F \u043C\u0435\u0436\u0434\u0443 \u043C\u043E\u0434\u0443\u043B\u044F\u043C\u0438',
            '\u041F\u0440\u0438\u0432\u043E\u0434': '\u042D\u043B\u0435\u043A\u0442\u0440\u043E\u043C\u043E\u0442\u043E\u0440 \u0434\u043B\u044F \u0430\u0432\u0442\u043E\u043C\u0430\u0442\u0438\u0447\u0435\u0441\u043A\u043E\u0433\u043E \u0443\u043F\u0440\u0430\u0432\u043B\u0435\u043D\u0438\u044F \u043B\u0430\u043C\u0435\u043B\u044F\u043C\u0438',
            '\u041F\u0443\u043B\u044C\u0442': '\u0411\u0435\u0441\u043F\u0440\u043E\u0432\u043E\u0434\u043D\u043E\u0435 \u0434\u0438\u0441\u0442\u0430\u043D\u0446\u0438\u043E\u043D\u043D\u043E\u0435 \u0443\u043F\u0440\u0430\u0432\u043B\u0435\u043D\u0438\u0435',
            '\u041F\u043E\u0434\u0441\u0432\u0435\u0442\u043A\u0430': '\u0412\u0441\u0442\u0440\u043E\u0435\u043D\u043D\u044B\u0435 LED-\u043B\u0435\u043D\u0442\u044B \u0432 \u043F\u0440\u043E\u0444\u0438\u043B\u044F\u0445 \u0431\u0430\u043B\u043E\u043A',
            '\u0423\u0441\u0438\u043B\u0438\u0442\u0435\u043B\u044C': '\u0414\u043E\u043F\u043E\u043B\u043D\u0438\u0442\u0435\u043B\u044C\u043D\u043E\u0435 \u0443\u0441\u0438\u043B\u0435\u043D\u0438\u0435 \u0434\u043B\u044F \u0431\u043E\u043B\u044C\u0448\u0438\u0445 \u043F\u0440\u043E\u043B\u0451\u0442\u043E\u0432',
            'Bansbach': '\u0413\u0430\u0437\u043E\u0432\u044B\u0435 \u043F\u0440\u0443\u0436\u0438\u043D\u044B Bansbach (\u0413\u0435\u0440\u043C\u0430\u043D\u0438\u044F) \u0434\u043B\u044F \u043F\u043B\u0430\u0432\u043D\u043E\u0433\u043E \u0443\u043F\u0440\u0430\u0432\u043B\u0435\u043D\u0438\u044F',
            'Somfy': '\u042D\u043B\u0435\u043A\u0442\u0440\u043E\u043F\u0440\u0438\u0432\u043E\u0434 Somfy (\u0424\u0440\u0430\u043D\u0446\u0438\u044F) \u2014 \u043C\u0438\u0440\u043E\u0432\u043E\u0439 \u043B\u0438\u0434\u0435\u0440 \u0430\u0432\u0442\u043E\u043C\u0430\u0442\u0438\u043A\u0438',
            'Simu': '\u042D\u043B\u0435\u043A\u0442\u0440\u043E\u043F\u0440\u0438\u0432\u043E\u0434 Simu (\u0424\u0440\u0430\u043D\u0446\u0438\u044F) \u2014 \u043D\u0430\u0434\u0451\u0436\u043D\u0430\u044F \u0430\u0432\u0442\u043E\u043C\u0430\u0442\u0438\u043A\u0430',
            '\u0414\u0438\u043C\u043C\u0435\u0440': '\u0420\u0435\u0433\u0443\u043B\u0438\u0440\u043E\u0432\u043A\u0430 \u044F\u0440\u043A\u043E\u0441\u0442\u0438 LED-\u043F\u043E\u0434\u0441\u0432\u0435\u0442\u043A\u0438 \u043F\u0443\u043B\u044C\u0442\u043E\u043C',
            '\u043B\u0435\u043D\u0442\u0430': 'LED-\u043B\u0435\u043D\u0442\u0430 IP65 \u0441 \u0437\u0430\u0449\u0438\u0442\u043E\u0439 \u043E\u0442 \u0432\u043B\u0430\u0433\u0438',
            '\u0414\u043E\u0441\u0442\u0430\u0432\u043A\u0430': '\u0414\u043E\u0441\u0442\u0430\u0432\u043A\u0430 \u0434\u043E \u043E\u0431\u044A\u0435\u043A\u0442\u0430 \u0432 \u043F\u0440\u0435\u0434\u0435\u043B\u0430\u0445 \u0420\u0424',
            '\u041C\u043E\u043D\u0442\u0430\u0436': '\u041F\u0440\u043E\u0444\u0435\u0441\u0441\u0438\u043E\u043D\u0430\u043B\u044C\u043D\u0430\u044F \u0443\u0441\u0442\u0430\u043D\u043E\u0432\u043A\u0430 \u0431\u0440\u0438\u0433\u0430\u0434\u043E\u0439 Decolife'
        };
        if (!isAll && mainResult.specification) {
            html += '<div class="kp-block">' +
                '<div class="kp-block-header"><div class="kp-block-icon" style="background:#7c3aed;">\u2630</div><div class="kp-block-title">\u0421\u043F\u0435\u0446\u0438\u0444\u0438\u043A\u0430\u0446\u0438\u044F \u0432\u0430\u0448\u0435\u0433\u043E \u043F\u0440\u043E\u0435\u043A\u0442\u0430</div></div>' +
                '<table class="spec-table"><thead><tr><th>\u041D\u0430\u0438\u043C\u0435\u043D\u043E\u0432\u0430\u043D\u0438\u0435</th><th>\u041A\u043E\u043B-\u0432\u043E</th></tr></thead><tbody>';
            mainResult.specification.forEach(function(s) {
                var hint = '';
                Object.keys(specHints).forEach(function(k) {
                    if (s.name && s.name.indexOf(k) !== -1) hint = specHints[k];
                });
                html += '<tr><td>' + s.name + (hint ? '<div class="kp-spec-hint">' + hint + '</div>' : '') + '</td><td>' + s.count + '</td></tr>';
            });
            html += '</tbody></table></div>';
        }

        /* Block 8: Cost details */
        if (!isAll && mainResult.items) {
            html += '<div class="kp-block">' +
                '<div class="kp-block-header"><div class="kp-block-icon" style="background:#1a3a6e;">\u20BD</div><div class="kp-block-title">\u0414\u0435\u0442\u0430\u043B\u0438\u0437\u0430\u0446\u0438\u044F \u0441\u0442\u043E\u0438\u043C\u043E\u0441\u0442\u0438</div></div>' +
                '<table class="cost-table"><tbody>';
            mainResult.items.forEach(function(item) {
                var priceRub = Math.round(item.price * mainResult.euro_rate);
                html += '<tr><td>' + item.name + '</td><td>' + formatPrice(priceRub) + ' \u20BD</td></tr>';
            });
            html += '</tbody></table></div>';
        }

        /* Variant comparison (for "all" mode) */
        if (isAll) {
            html += '<div class="kp-block">' +
                '<div class="kp-block-header"><div class="kp-block-icon" style="background:#7c3aed;">\u2261</div><div class="kp-block-title">\u0421\u0440\u0430\u0432\u043D\u0435\u043D\u0438\u0435 \u0432\u0430\u0440\u0438\u0430\u043D\u0442\u043E\u0432</div></div>' +
                '<div class="compare-table-wrap"><table class="compare-table"><thead><tr><th>\u041C\u043E\u0434\u0438\u0444\u0438\u043A\u0430\u0446\u0438\u044F</th><th>\u041D\u0430\u043B\u0438\u0447\u043D\u044B\u0435</th><th>\u0411\u0435\u0437\u043D\u0430\u043B.</th><th>\u0421 \u041D\u0414\u0421</th></tr></thead><tbody>';
            resultOrResults.forEach(function(r, idx) {
                var label = r.variant_label || r.selected_variant || '';
                html += '<tr' + (idx === 0 ? ' class="compare-row-best"' : '') + '><td><strong>' + label + '</strong></td>' +
                    '<td>' + formatPrice(r.totals.cash) + ' \u20BD</td>' +
                    '<td>' + formatPrice(r.totals.non_cash) + ' \u20BD</td>' +
                    '<td>' + formatPrice(r.totals.with_vat) + ' \u20BD</td></tr>';
            });
            html += '</tbody></table></div></div>';
        }

        /* Block 8: Technical specifications (from variant specs) */
        if (state._variantSpecHtml) {
            html += '<div class="kp-block">' + state._variantSpecHtml + '</div>';
        }

        /* Block 9: Guarantees + Company info with dynamic counter (merged) */
        html += '<div class="kp-block">' +
            '<div class="kp-block-header"><div class="kp-block-icon" style="background:#2e7d32;">\u2714</div><div class="kp-block-title">\u0413\u0430\u0440\u0430\u043D\u0442\u0438\u0438 \u0438 \u043A\u043E\u043C\u043F\u0430\u043D\u0438\u044F</div></div>' +
            '<div class="kp-warranty-row"><span class="kp-warranty-icon">\uD83D\uDEE1</span><span class="kp-warranty-text"><strong>5 \u043B\u0435\u0442</strong> \u0433\u0430\u0440\u0430\u043D\u0442\u0438\u044F \u043D\u0430 \u043A\u043E\u043D\u0441\u0442\u0440\u0443\u043A\u0446\u0438\u044E</span></div>' +
            '<div class="kp-warranty-row"><span class="kp-warranty-icon">\u2699</span><span class="kp-warranty-text"><strong>2 \u0433\u043E\u0434\u0430</strong> \u0433\u0430\u0440\u0430\u043D\u0442\u0438\u044F \u043D\u0430 \u0430\u0432\u0442\u043E\u043C\u0430\u0442\u0438\u043A\u0443</span></div>' +
            '<div class="kp-warranty-row"><span class="kp-warranty-icon">\uD83C\uDFED</span><span class="kp-warranty-text">\u041F\u0440\u043E\u0438\u0437\u0432\u043E\u0434\u0441\u0442\u0432\u043E <strong>Decolife</strong> (\u0411\u0435\u043B\u0430\u0440\u0443\u0441\u044C)</span></div>' +
            '<hr style="margin:0.7rem 0;border-color:#eee;">' +
            '<div class="kp-trust-stats">' +
            '<div class="kp-stat"><div class="kp-stat-number">8+</div><div class="kp-stat-label">\u043B\u0435\u0442 \u043D\u0430 \u0440\u044B\u043D\u043A\u0435</div></div>' +
            '<div class="kp-stat"><div class="kp-stat-number">200+</div><div class="kp-stat-label">\u043F\u0440\u043E\u0435\u043A\u0442\u043E\u0432</div></div>' +
            '<div class="kp-stat"><div class="kp-stat-number">8</div><div class="kp-stat-label">\u0440\u0435\u0433\u0438\u043E\u043D\u043E\u0432</div></div>' +
            '</div></div>';

        /* Block 9: Work stages + upsell (merged) */
        html += '<div class="kp-block">' +
            '<div class="kp-block-header"><div class="kp-block-icon" style="background:#f59e0b;">\u23F1</div><div class="kp-block-title">\u042D\u0442\u0430\u043F\u044B \u0440\u0430\u0431\u043E\u0442\u044B</div></div>' +
            '<div class="kp-warranty-row"><span class="kp-warranty-icon">1\uFE0F\u20E3</span><span class="kp-warranty-text"><strong>\u0417\u0430\u043C\u0435\u0440 \u0438 \u043F\u0440\u043E\u0435\u043A\u0442</strong> \u2014 \u0432\u044B\u0435\u0437\u0434 \u0441\u043F\u0435\u0446\u0438\u0430\u043B\u0438\u0441\u0442\u0430</span></div>' +
            '<div class="kp-warranty-row"><span class="kp-warranty-icon">2\uFE0F\u20E3</span><span class="kp-warranty-text"><strong>\u0414\u043E\u0433\u043E\u0432\u043E\u0440</strong> \u2014 80% \u043F\u043E\u0441\u043B\u0435 \u043F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043D\u0438\u044F \u0437\u0430\u043A\u0430\u0437\u0430</span></div>' +
            '<div class="kp-warranty-row"><span class="kp-warranty-icon">3\uFE0F\u20E3</span><span class="kp-warranty-text"><strong>\u041F\u0440\u043E\u0438\u0437\u0432\u043E\u0434\u0441\u0442\u0432\u043E</strong> \u2014 30\u201345 \u0434\u043D\u0435\u0439</span></div>' +
            '<div class="kp-warranty-row"><span class="kp-warranty-icon">4\uFE0F\u20E3</span><span class="kp-warranty-text"><strong>\u041C\u043E\u043D\u0442\u0430\u0436</strong> \u2014 3\u20137 \u0434\u043D\u0435\u0439, 20% \u043F\u043E\u0441\u043B\u0435 \u043F\u0440\u0438\u0451\u043C\u043A\u0438</span></div>' +
            '<hr style="margin:0.7rem 0;border-color:#eee;">' +
            '<div style="font-weight:600;margin-bottom:0.4rem;">\u0414\u043E\u043F\u043E\u043B\u043D\u0438\u0442\u0435\u043B\u044C\u043D\u044B\u0435 \u043E\u043F\u0446\u0438\u0438:</div>' +
            '<div class="kp-upsell-grid">' +
            '<div class="kp-upsell-card"><div class="kp-upsell-icon">\uD83E\uDE9F</div><div class="kp-upsell-title">\u041E\u0441\u0442\u0435\u043A\u043B\u0435\u043D\u0438\u0435</div><div class="kp-upsell-desc">\u0420\u0430\u0437\u0434\u0432\u0438\u0436\u043D\u043E\u0435, \u0440\u0430\u0441\u043F\u0430\u0448\u043D\u043E\u0435, \u0441\u043A\u043B\u0430\u0434\u043D\u043E\u0435, \u0433\u0438\u043B\u044C\u043E\u0442\u0438\u043D\u043D\u043E\u0435</div></div>' +
            '<div class="kp-upsell-card"><div class="kp-upsell-icon">\uD83E\uDDF5</div><div class="kp-upsell-title">\u041C\u043E\u0441\u043A\u0438\u0442\u043D\u044B\u0435 \u0441\u0435\u0442\u043A\u0438</div></div>' +
            '<div class="kp-upsell-card"><div class="kp-upsell-icon">\uD83C\uDF00</div><div class="kp-upsell-title">ZIP \u043C\u0430\u0440\u043A\u0438\u0437\u044B</div></div>' +
            '<div class="kp-upsell-card"><div class="kp-upsell-icon">\uD83C\uDFDB\uFE0F</div><div class="kp-upsell-title">\u0424\u0430\u0441\u0430\u0434\u043D\u044B\u0435 \u043F\u0430\u043D\u0435\u043B\u0438</div><div class="kp-upsell-desc">\u0421\u043F\u043B\u043E\u0448\u043D\u044B\u0435 \u0438 \u0436\u0430\u043B\u044E\u0437\u0438</div></div>' +
            '<div class="kp-upsell-card"><div class="kp-upsell-icon">\uD83C\uDF21</div><div class="kp-upsell-title">\u0418\u041A \u043E\u0431\u043E\u0433\u0440\u0435\u0432\u0430\u0442\u0435\u043B\u0438</div></div>' +
            '<div class="kp-upsell-card"><div class="kp-upsell-icon">\uD83D\uDCA1</div><div class="kp-upsell-title">LED \u043E\u0441\u0432\u0435\u0449\u0435\u043D\u0438\u0435</div></div>' +
            '</div></div>';

        /* Block 10: Videos + Gallery + CTA */
        var allVids = [
            {id:'351f7009cda5991ef24138f05f7a8692', type:'shorts', title:'\u041F\u0435\u0440\u0433\u043E\u043B\u0430 B500', group:'bio'},
            {id:'df0131deee13f2a2fd945146aacaeed8', type:'full', title:'\u041E\u0431\u0437\u043E\u0440 \u0431\u0438\u043E\u043A\u043B\u0438\u043C\u0430\u0442\u0438\u0447\u0435\u0441\u043A\u043E\u0439 \u043F\u0435\u0440\u0433\u043E\u043B\u044B', group:'bio'},
            {id:'e51c7aaa6b00e9c125bbcdb92866b626', type:'shorts', title:'\u041F\u0435\u0440\u0433\u043E\u043B\u0430 B700', group:'bio'},
            {id:'f281d74466c7636d0e30186a7db3e70d', type:'full', title:'B700 \u2014 \u043F\u0440\u0435\u043C\u0438\u0430\u043B\u044C\u043D\u0430\u044F \u043F\u0435\u0440\u0433\u043E\u043B\u0430', group:'bio'},
            {id:'b01e73426cb0d008adbb72a544ec6f18', type:'full', title:'\u041F\u0435\u0440\u0433\u043E\u043B\u0430 B600 \u2014 PIR \u043A\u0440\u044B\u0448\u0430', group:'pir'},
            {id:'ca7d582f5793c56641c7c6c3ecef4cfa', type:'full', title:'B600 \u2014 \u0432\u0441\u0435\u0441\u0435\u0437\u043E\u043D\u043D\u0430\u044F \u0442\u0435\u0440\u0440\u0430\u0441\u0430', group:'pir'}
        ];
        html += '<div class="kp-block">' +
            '<div class="kp-block-header"><div class="kp-block-icon" style="background:#1a3a6e;">\uD83C\uDFA5</div><div class="kp-block-title">\u0412\u0438\u0434\u0435\u043E \u0441 \u043D\u0430\u0448\u0438\u0445 \u0443\u0441\u0442\u0430\u043D\u043E\u0432\u043E\u043A</div></div>' +
            '<div class="kp-video-grid">';
        var pirStarted = false;
        allVids.forEach(function(v) {
            if (v.group === 'pir' && !pirStarted) {
                pirStarted = true;
                html += '<div class="kp-video-divider"><span>\u041F\u0435\u0440\u0433\u043E\u043B\u0430 B600 \u2014 \u0441\u0442\u0430\u0446\u0438\u043E\u043D\u0430\u0440\u043D\u0430\u044F \u043A\u0440\u044B\u0448\u0430 (PIR \u043F\u0430\u043D\u0435\u043B\u0438)</span></div>';
            }
            var borderColor = v.group === 'bio' ? '#1a3a6e' : '#f59e0b';
            var isShorts = v.type === 'shorts';
            html += '<div class="kp-video-card' + (isShorts ? ' kp-video-card-shorts' : '') + '" style="border-top:3px solid ' + borderColor + ';">' +
                '<div class="video-iframe-wrap' + (isShorts ? ' video-iframe-shorts' : '') + '">' +
                '<iframe data-src="https://rutube.ru/play/embed/' + v.id + '" frameborder="0" allowfullscreen allow="autoplay" loading="lazy"></iframe>' +
                '</div>' +
                '<div class="video-card-title">' + v.title + '</div></div>';
        });
        html += '</div></div>';

        var galleryImages = [
            'IMG_5914.jpg',
            'pergola_b500_garden_view.jpg',
            'pergola_b700_poolside.jpg',
            'pergola_evening_lighting.jpg',
            'pergola_b500_led_lighting.jpg',
            'pergola_panoramic_glass_walls.jpg',
            'IMG_0672_2_882acf32.jpg',
            'IMG_0748_827e14fe.jpg'
        ];
        html += '<div class="kp-block">' +
            '<div class="kp-block-header"><div class="kp-block-icon" style="background:#1a3a6e;">\uD83D\uDCF7</div><div class="kp-block-title">\u0420\u0435\u0430\u043B\u0438\u0437\u043E\u0432\u0430\u043D\u043D\u044B\u0435 \u043F\u0440\u043E\u0435\u043A\u0442\u044B</div></div>' +
            '<div class="kp-gallery-grid">';
        galleryImages.forEach(function(img, idx) {
            html += '<div class="kp-gallery-item"><img src="/static/images/gallery/' + img + '" alt="\u041F\u0440\u043E\u0435\u043A\u0442 ' + (idx+1) + '" onerror="this.parentElement.style.display=\'none\'"></div>';
        });
        html += '</div></div>';

        html +=
            '<div class="kp-cta-block">' +
            '<h4>\u0413\u043E\u0442\u043E\u0432\u044B \u043E\u0431\u0441\u0443\u0434\u0438\u0442\u044C \u043F\u0440\u043E\u0435\u043A\u0442?</h4>' +
            '<p>\u0421\u0432\u044F\u0436\u0438\u0442\u0435\u0441\u044C \u0441 \u043D\u0430\u043C\u0438 \u2014 \u043E\u0442\u0432\u0435\u0442\u0438\u043C \u043D\u0430 \u0432\u0441\u0435 \u0432\u043E\u043F\u0440\u043E\u0441\u044B</p>' +
            '</div>';

        html += '</div>';
        return html;
    }

    function loadDecoDataAndRender(resultOrResults) {
        fetch('/api/decolife-data/' + state.pergolaType)
            .then(function(r) { return r.json(); })
            .then(function(resp) {
                var decoData = (resp.success && resp.data) ? resp.data : {};
                var kpContainer = document.getElementById('marketing-kp-container');
                if (kpContainer) {
                    kpContainer.innerHTML = buildMarketingKP(resultOrResults, decoData);
                    initLazyIframes();
                }
            })
            .catch(function() {
                var kpContainer = document.getElementById('marketing-kp-container');
                if (kpContainer) {
                    kpContainer.innerHTML = buildMarketingKP(resultOrResults, {});
                    initLazyIframes();
                }
            });
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
            pdfBody = {results: state.allResults, mode: 'all', client_name: state.clientName, kp_number: state.kpNumber, deadline: state.deadline, calc_id: state.calcId};
        } else {
            pdfBody = {result: state.result, mode: 'single', client_name: state.clientName, kp_number: state.kpNumber, deadline: state.deadline, calc_id: state.calcId};
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

    function shareKp() {
        if (!state.calcId) { alert('Сначала выполните расчёт'); return; }
        var url = window.location.origin + '/kp/' + state.calcId;
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(url).then(function() {
                var btn = document.getElementById('share-btn');
                btn.innerHTML = '<i class="bi bi-check-lg"></i> Скопировано!';
                setTimeout(function() { btn.innerHTML = '<i class="bi bi-share"></i> Поделиться'; }, 2000);
            });
        } else {
            var ta = document.createElement('textarea');
            ta.value = url;
            document.body.appendChild(ta);
            ta.select();
            document.execCommand('copy');
            document.body.removeChild(ta);
            var btn = document.getElementById('share-btn');
            btn.innerHTML = '<i class="bi bi-check-lg"></i> Скопировано!';
            setTimeout(function() { btn.innerHTML = '<i class="bi bi-share"></i> Поделиться'; }, 2000);
        }
    }

    if (window.__CALC_ID__) {
        fetch('/api/kp/' + window.__CALC_ID__)
        .then(function(r) { return r.json(); })
        .then(function(resp) {
            if (!resp.success || !resp.data) return;
            var d = resp.data;
            state.calcId = window.__CALC_ID__;
            state.kpNumber = d.kp_number || '';
            state.deadline = d.deadline || '';
            state.clientName = d.client_name || '';
            if (stepsEl.step1) stepsEl.step1.style.display = 'none';
            if (stepsEl.step2) stepsEl.step2.style.display = 'none';
            if (stepsEl.step3) stepsEl.step3.style.display = 'none';
            if (stepsEl.step4) stepsEl.step4.style.display = 'none';
            var req = d.request || {};
            if (req.pergola_type) state.pergolaType = req.pergola_type;

            var typeNames = {'B500NEW': 'В500 — поворотные ламели', 'B700NEW': 'В700 — поворотно-сдвижные', 'B600': 'В600 — PIR панели'};
            var pergolaTypeName = '';
            var dimWidth = req.width || 0;
            var dimLength = req.length || 0;
            var modLabel = '';

            if (d.mode === 'all' && d.results) {
                if (d.results[0] && d.results[0].options) state.pergolaType = d.results[0].options.pergola_type || state.pergolaType;
                pergolaTypeName = (d.results[0] && d.results[0].pergola_type_name) || '';
                if (d.results[0] && d.results[0].dimensions) {
                    dimWidth = dimWidth || d.results[0].dimensions.width;
                    dimLength = dimLength || d.results[0].dimensions.length;
                }
                modLabel = 'Все модификации';
                state.allResults = d.results;
                state.result = d.results[0];
                renderAllResults(d.results);
            } else if (d.result) {
                if (d.result.options) state.pergolaType = d.result.options.pergola_type || state.pergolaType;
                pergolaTypeName = d.result.pergola_type_name || '';
                if (d.result.dimensions) {
                    dimWidth = dimWidth || d.result.dimensions.width;
                    dimLength = dimLength || d.result.dimensions.length;
                }
                modLabel = d.result.variant_label || d.result.selected_variant || '';
                state.result = d.result;
                renderResults(d.result);
            }

            pergolaTypeName = pergolaTypeName || typeNames[state.pergolaType] || state.pergolaType;

            var bannerHtml = '<div class="saved-kp-banner">';
            bannerHtml += '<div class="saved-kp-banner-title">Сохранённое коммерческое предложение</div>';
            bannerHtml += '<div class="saved-kp-banner-params">';
            bannerHtml += '<span class="saved-kp-param"><strong>Модель:</strong> ' + escHtml(pergolaTypeName) + '</span>';
            if (dimWidth && dimLength) {
                bannerHtml += '<span class="saved-kp-param"><strong>Размеры:</strong> ' + Number(dimWidth).toFixed(2) + ' × ' + Number(dimLength).toFixed(2) + ' м</span>';
            }
            if (modLabel) {
                bannerHtml += '<span class="saved-kp-param"><strong>Модификация:</strong> ' + escHtml(modLabel) + '</span>';
            }
            if (state.clientName) {
                bannerHtml += '<span class="saved-kp-param"><strong>Заказчик:</strong> ' + escHtml(state.clientName) + '</span>';
            }
            bannerHtml += '</div>';
            bannerHtml += '<a href="/calculator" class="saved-kp-new-btn">Новый расчёт</a>';
            bannerHtml += '</div>';

            var bannerDiv = document.createElement('div');
            bannerDiv.innerHTML = bannerHtml;
            var calcContainer = document.querySelector('.calc-container');
            if (calcContainer) {
                calcContainer.insertBefore(bannerDiv.firstChild, calcContainer.firstChild);
            }
        })
        .catch(function() {});
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
