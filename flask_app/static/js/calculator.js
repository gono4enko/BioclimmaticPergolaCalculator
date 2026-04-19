document.addEventListener('DOMContentLoaded', function() {
    var SVG_V = 'v107';
    var state = {
        pergolaType: '',
        lamellaSize: '',
        lamellaType: '',
        selectedVariant: '',
        width: 0,
        length: 0,
        height: 3.0,
        whiteLed: true,
        rgbLed: false,
        installation: true,
        facadeType: '',
        facadeOpenings: [],
        facadePerOpening: {},
        glazingPerOpening: {},
        zipPerOpening: {},
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
            {id: '125f1443e86b56ebfd2ca7a65831f034', type: 'full', title: 'B700 \u2014 \u043F\u0440\u0435\u043C\u0438\u0430\u043B\u044C\u043D\u0430\u044F \u043F\u0435\u0440\u0433\u043E\u043B\u0430'}
        ],
        'B600': [
            {id: 'b01e73426cb0d008adbb72a544ec6f18', type: 'full', title: '\u041F\u0435\u0440\u0433\u043E\u043B\u0430 B600 PIR \u2014 \u0432 \u043A\u0430\u0447\u0435\u0441\u0442\u0432\u0435 \u043F\u0430\u0432\u0438\u043B\u044C\u043E\u043D\u0430 \u0434\u043B\u044F \u0431\u0430\u0441\u0441\u0435\u0439\u043D\u0430'},
            {id: 'ca7d582f5793c56641c7c6c3ecef4cfa', type: 'full', title: 'B600 \u2014 \u0432\u0441\u0435\u0441\u0435\u0437\u043E\u043D\u043D\u0430\u044F \u0442\u0435\u0440\u0440\u0430\u0441\u0430'}
        ],
        'B200': []
    };

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
        } else if (pergolaType === 'B200') {
            state.lamellaSize = '20';
            state.lamellaType = 'B200-20A';
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
            } else if (pergolaType === 'B200') {
                var bSuffix = (variant && variant.indexOf('AERO') === 0) ? 'A' : 'F';
                state.lamellaType = 'B200-' + lamellaSize + bSuffix;
            } else {
                state.lamellaType = 'B600-PIR';
            }
        }

        var _spec2 = null;
        if (state.variantsData) {
            state.variantsData.forEach(function(sv2) {
                if (sv2.variant === variant && (!lamellaSize || sv2.lamella_size === lamellaSize)) _spec2 = sv2;
            });
            if (!_spec2) state.variantsData.forEach(function(sv2) { if (sv2.variant === variant) _spec2 = sv2; });
        }
        state._maxModuleWidth = _spec2 ? (_spec2.max_module_width || null) : null;
        state._maxOverhang = _spec2 ? (_spec2.max_overhang || null) : null;

        updateMaxDimensions();
        stepsEl.step3.style.display = 'block';
        stepsEl.step4.style.display = 'block';
        stepsEl.calcBtn.style.display = 'block';
        buildFacadeTopView();
        buildFacadeTable();
        buildGlazingTable();
        buildZipTable();
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

                    var imgHtml = '';
                    if (v.images && v.images.hero) {
                        imgHtml = '<div class="variant-thumb" style="text-align:center;margin-bottom:0.5rem;"><img src="' + v.images.hero + '?_v=' + SVG_V + '" alt="' + v.variant + '" style="max-width:100%;max-height:150px;object-fit:contain;border-radius:6px;background:#f5f7fb;"></div>';
                    }
                    div.innerHTML = '<span class="check-mark"><svg viewBox="0 0 14 14" fill="none" width="12" height="12"><path d="M2 7.5L5.5 11L12 3" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg></span>' +
                        imgHtml +
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
            } else if (state.pergolaType === 'B200') {
                ls = '20';
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

    function _markFilled(el, ok) {
        if (!el) return;
        if (ok) el.classList.add('is-filled');
        else el.classList.remove('is-filled');
    }
    document.getElementById('input-width').addEventListener('input', function() {
        state.width = parseFloat(this.value) || 0;
        _markFilled(this, state.width > 0);
        buildFacadeTopView();
        buildFacadeTable();
        buildGlazingTable();
        buildZipTable();
    });
    document.getElementById('input-length').addEventListener('input', function() {
        state.length = parseFloat(this.value) || 0;
        _markFilled(this, state.length > 0);
        buildFacadeTopView();
        buildFacadeTable();
        buildGlazingTable();
        buildZipTable();
    });
    document.getElementById('input-height').addEventListener('input', function() {
        var raw = parseFloat(this.value);
        var h = isNaN(raw) ? 0 : raw;
        state.height = h > 0 ? Math.min(3.0, Math.max(2.0, h)) : 0;
        _markFilled(this, state.height >= 2.0);
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

    var facadeTypeEl = null;
    var facadeAreaInfo = document.getElementById('facade-area-info');

    function facadeModules(width) {
        var mw = state._maxModuleWidth || 4.5;
        return Math.max(1, Math.ceil(width / mw));
    }

    function facadeLengthModules(length) {
        var mo = state._maxOverhang || null;
        if (!mo || length <= mo + 0.001) return 1;
        return Math.max(2, Math.ceil(length / mo));
    }

    function getFillForSide(side) {
        if (!state.facadePerOpening) return '';
        var bays = (side === 'front' || side === 'back') ? facadeModules(state.width) : facadeLengthModules(state.length);
        for (var i = 0; i < bays; i++) {
            var t = state.facadePerOpening[side + '_' + i];
            if (t) return t;
        }
        return '';
    }

    function getGlzForSide(side) {
        if (!state.glazingPerOpening) return '';
        var bays = (side === 'front' || side === 'back') ? facadeModules(state.width) : facadeLengthModules(state.length);
        // Priority: W-series (returns its specific code) > S100 > S500
        var hasS100 = false, hasS500 = false;
        for (var i = 0; i < bays; i++) {
            var g = state.glazingPerOpening[side + '_' + i];
            if (!g || !g.enabled) continue;
            var sU = (g.series || 'S500').toUpperCase();
            if (sU === 'W500' || sU === 'W600' || sU === 'W700') {
                var wSashes = g.sashes || 2;
                var wColor  = g.color  || 'ral9t08';
                var wGlass  = g.glass  || 'transparent';
                return sU + ':' + wSashes + ':' + wColor + ':' + wGlass;
            }
            if (sU === 'S100') hasS100 = true;
            else hasS500 = true;
        }
        if (hasS100) return 'S100';
        return hasS500 ? 'S500' : '';
    }

    function getBayFillQs(side, count, xPerBay) {
        if (!state.facadePerOpening) return '';
        var parts = [];
        var fillIdx = 1;
        var sections = (xPerBay > 0) ? (xPerBay + 1) : 1;
        for (var i = 0; i < count; i++) {
            var f = state.facadePerOpening[side + '_' + i] || '';
            for (var j = 0; j < sections; j++) {
                if (f) parts.push('fill_' + fillIdx + '=' + encodeURIComponent(f));
                fillIdx++;
            }
            if (!f) break;
        }
        var qs = parts.filter(Boolean).join('&');
        return qs ? ('&' + qs) : '';
    }

    function facadeOpeningArea(opening, mods) {
        var colW = (state.selectedVariant === 'Light') ? 0.150 : (state.pergolaType === 'B200' ? 0.100 : 0.164);
        var beamH = (state.selectedVariant === 'Light') ? 0.250 : (state.pergolaType === 'B200' ? 0.200 : 0.280);
        var openH = Math.max(0.1, 3.0 - beamH);
        var lMods = facadeLengthModules(state.length);
        if (opening.side === 'front' || opening.side === 'back') {
            var n = Math.max(1, mods);
            return Math.max(0.01, (state.width - (n + 1) * colW) / n) * openH;
        }
        var nL = Math.max(1, lMods);
        return Math.max(0.01, (state.length - (nL + 1) * colW) / nL) * openH;
    }

    function facadeOpeningDims(opening) {
        var colW = (state.selectedVariant === 'Light') ? 0.150 : (state.pergolaType === 'B200' ? 0.100 : 0.164);
        var beamH = (state.selectedVariant === 'Light') ? 0.250 : (state.pergolaType === 'B200' ? 0.200 : 0.280);
        var hMm = Math.round((3.0 - beamH) * 1000);
        var n, totalDim;
        if (opening.side === 'front' || opening.side === 'back') {
            n = Math.max(1, facadeModules(state.width));
            totalDim = state.width;
        } else {
            n = Math.max(1, facadeLengthModules(state.length));
            totalDim = state.length;
        }
        var wMm = Math.round(Math.max(100, (totalDim - (n + 1) * colW) / n * 1000));
        return {wMm: wMm, hMm: hMm};
    }

    function openingLabel(side, bay) {
        var letter = side === 'front' ? 'F' : side === 'back' ? 'B' : side === 'left' ? 'A' : 'C';
        var mods = facadeModules(state.width);
        var lMods = facadeLengthModules(state.length);
        var total = (side === 'front' || side === 'back') ? mods : lMods;
        return total > 1 ? letter + (bay + 1) : letter;
    }

    function computeFacadeOpenings() {
        return Object.keys(state.facadePerOpening)
            .filter(function(k) { return state.facadePerOpening[k]; })
            .map(function(k) {
                var parts = k.split('_');
                var bay = parseInt(parts.pop());
                var side = parts.join('_');
                return {side: side, bay: bay, type: state.facadePerOpening[k]};
            });
    }

    function updateFacadeAreaInfo() {
        if (!facadeAreaInfo) return;
        var actives = computeFacadeOpenings();
        if (actives.length === 0) {
            facadeAreaInfo.style.display = 'none'; facadeAreaInfo.textContent = ''; return;
        }
        var mods = facadeModules(state.width);
        var total = 0;
        var labels = [];
        actives.forEach(function(o) {
            total += facadeOpeningArea(o, mods);
            labels.push(openingLabel(o.side, o.bay));
        });
        facadeAreaInfo.style.display = 'block';
        facadeAreaInfo.textContent = '\u0418\u0442\u043e\u0433\u043e \u043f\u0440\u043e\u0451\u043c\u043e\u0432: ' + labels.join(', ')
            + ' \u2014 \u043f\u043b\u043e\u0449\u0430\u0434\u044c \u2248 ' + total.toFixed(2) + ' \u043c\u00b2';
    }

    function buildFacadeTable() {
        var tableEl = document.getElementById('facade-opening-table');
        if (!tableEl) return;
        var W = state.width; var L = state.length;
        if (W <= 0 || L <= 0) { tableEl.innerHTML = ''; return; }
        var mods = facadeModules(W);
        var lMods = facadeLengthModules(L);
        var TYPES = [
            {v: 'FP-20',    n: 'FP-20 \u2014 \u0444\u0430\u0441\u0430\u0434\u043d\u044b\u0435 \u043f\u0430\u043d\u0435\u043b\u0438'},
            {v: 'FP-PIR',   n: 'FP-PIR \u2014 PIR-\u0441\u044d\u043d\u0434\u0432\u0438\u0447'},
            {v: 'FZ-44-50', n: 'FZ-44 \u2014 \u0436\u0430\u043b\u044e\u0437\u0438 50%'},
            {v: 'FZ-44-70', n: 'FZ-44 \u2014 \u0436\u0430\u043b\u044e\u0437\u0438 70%'},
            {v: 'FZ-44-100',n: 'FZ-44 \u2014 \u0436\u0430\u043b\u044e\u0437\u0438 100%'},
            {v: 'S500',     n: 'S500 \u2014 \u043f\u0430\u043d\u043e\u0440\u0430\u043c\u043d\u043e\u0435 \u043e\u0441\u0442\u0435\u043a\u043b\u0435\u043d\u0438\u0435 (\u043d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u043d\u0438\u0436\u0435)'},
            {v: 'S100',     n: 'S100 \u2014 \u0431\u0435\u0437\u0440\u0430\u043c\u043d\u043e\u0435 \u043e\u0441\u0442\u0435\u043a\u043b\u0435\u043d\u0438\u0435 10\u00a0\u043c\u043c (\u043d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u043d\u0438\u0436\u0435)'},
            {v: 'W500',     n: 'W500 \u2014 \u0433\u0438\u043b\u044c\u043e\u0442\u0438\u043d\u043d\u043e\u0435, \u0441\u0442\u0435\u043a\u043b\u043e\u043f\u0430\u043a\u0435\u0442 20\u00a0\u043c\u043c (\u043d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u043d\u0438\u0436\u0435)'},
            {v: 'W600',     n: 'W600 \u2014 \u0433\u0438\u043b\u044c\u043e\u0442\u0438\u043d\u043d\u043e\u0435, \u0441\u0442\u0435\u043a\u043b\u043e\u043f\u0430\u043a\u0435\u0442 28\u00a0\u043c\u043c (\u043d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u043d\u0438\u0436\u0435)'},
            {v: 'W700',     n: 'W700 \u2014 \u0433\u0438\u043b\u044c\u043e\u0442\u0438\u043d\u043d\u043e\u0435 \u0441 \u0442\u0435\u0440\u043c\u043e\u0440\u0430\u0437\u0440\u044b\u0432\u043e\u043c, 28\u00a0\u043c\u043c (\u043d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u043d\u0438\u0436\u0435)'},
            {v: 'ZIP',      n: 'ZIP-\u043c\u0430\u0440\u043a\u0438\u0437\u0430 \u2014 \u0432\u0435\u0440\u0442\u0438\u043a\u0430\u043b\u044c\u043d\u0430\u044f (\u043d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u043d\u0438\u0436\u0435)'}
        ];
        var openings = [];
        for (var ai = 0; ai < lMods; ai++) {
            openings.push({side: 'left', bay: ai,
                label: lMods > 1 ? 'A' + (ai+1) : 'A',
                desc: lMods > 1 ? '\u0421\u043b\u0435\u0432\u0430 \u00b7 \u041f\u0440\u043e\u0451\u043c ' + (ai+1) : '\u0421\u043b\u0435\u0432\u0430'});
        }
        for (var bi = 0; bi < mods; bi++) {
            openings.push({side: 'back', bay: bi,
                label: mods > 1 ? 'B' + (bi+1) : 'B',
                desc: mods > 1 ? '\u0421\u0437\u0430\u0434\u0438 \u00b7 \u041f\u0440\u043e\u0451\u043c ' + (bi+1) : '\u0421\u0437\u0430\u0434\u0438'});
        }
        for (var ci = 0; ci < lMods; ci++) {
            openings.push({side: 'right', bay: ci,
                label: lMods > 1 ? 'C' + (ci+1) : 'C',
                desc: lMods > 1 ? '\u0421\u043f\u0440\u0430\u0432\u0430 \u00b7 \u041f\u0440\u043e\u0451\u043c ' + (ci+1) : '\u0421\u043f\u0440\u0430\u0432\u0430'});
        }
        for (var fi = 0; fi < mods; fi++) {
            openings.push({side: 'front', bay: fi,
                label: mods > 1 ? 'F' + (fi+1) : 'F',
                desc: mods > 1 ? '\u0424\u0430\u0441\u0430\u0434 \u00b7 \u041f\u0440\u043e\u0451\u043c ' + (fi+1) : '\u0424\u0430\u0441\u0430\u0434'});
        }
        var html = '<table class="facade-table"><thead><tr>'
            + '<th>\u041f\u0440\u043e\u0451\u043c</th>'
            + '<th>\u0420\u0430\u0441\u043f\u043e\u043b\u043e\u0436\u0435\u043d\u0438\u0435</th>'
            + '<th>\u0422\u0438\u043f \u0437\u0430\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u044f</th>'
            + '<th>\u0420\u0430\u0437\u043c\u0435\u0440 / \u041f\u043b\u043e\u0449\u0430\u0434\u044c</th>'
            + '</tr></thead><tbody>';
        openings.forEach(function(o) {
            var key = o.side + '_' + o.bay;
            var glzEntry = state.glazingPerOpening && state.glazingPerOpening[key];
            var hasGlz = !!(glzEntry && glzEntry.enabled);
            var glzSeries = hasGlz ? ((glzEntry.series || 'S500').toUpperCase()) : '';
            var zipEnabled = !!(state.zipPerOpening && state.zipPerOpening[key] && state.zipPerOpening[key].enabled && !hasGlz && !state.facadePerOpening[key]);
            var selType = state.facadePerOpening[key] || glzSeries || (zipEnabled ? 'ZIP' : '');
            var dims = facadeOpeningDims(o);
            var dimsHtml = '<span style="font-size:0.82em;color:#555;white-space:nowrap;">' + dims.wMm + '\u00d7' + dims.hMm + ' \u043c\u043c</span>';
            var areaVal = (dims.wMm * dims.hMm / 1e6).toFixed(2);
            var areaHtml = '<br><span style="font-size:0.9em;">' + areaVal + ' \u043c\u00b2</span>';
            html += '<tr data-key="' + key + '"><td><span class="facade-lbl">' + o.label + '</span></td>'
                + '<td>' + o.desc + '</td>'
                + '<td><select class="form-select form-select-sm facade-type-sel" data-side="' + o.side + '" data-bay="' + o.bay + '">'
                + '<option value="">\u2014 \u0431\u0435\u0437 \u0437\u0430\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u044f \u2014</option>';
            TYPES.forEach(function(t) {
                html += '<option value="' + t.v + '"' + (selType === t.v ? ' selected' : '') + '>' + t.n + '</option>';
            });
            html += '</select></td><td class="facade-area">' + dimsHtml + areaHtml + '</td></tr>';
        });
        html += '</tbody></table>';
        tableEl.innerHTML = html;
        tableEl.querySelectorAll('.facade-type-sel').forEach(function(sel) {
            sel.addEventListener('change', function() {
                var key2 = this.dataset.side + '_' + this.dataset.bay;
                var val = this.value;
                var isGlzVal = (val === 'S500' || val === 'S100' || val === 'W500' || val === 'W600' || val === 'W700');
                var isZipVal = (val === 'ZIP');
                if (isGlzVal) {
                    // Enable glazing for this opening, clear facade and ZIP
                    state.facadePerOpening[key2] = '';
                    if (state.zipPerOpening && state.zipPerOpening[key2]) state.zipPerOpening[key2].enabled = false;
                    var defColor = (val === 'S500') ? 'ral7016' : 'ral9t08';
                    var existing = state.glazingPerOpening[key2];
                    if (!existing || (existing.series || 'S500') !== val) {
                        // Reset to series defaults when switching/initializing
                        state.glazingPerOpening[key2] = {series: val, pc: 0, direction: 'right', color: defColor, glass: 'transparent', sashes: 0, plavnik: null, count: 1, enabled: true};
                    } else {
                        existing.series = val;
                        existing.enabled = true;
                        state.glazingPerOpening[key2] = existing;
                    }
                } else if (isZipVal) {
                    // Enable ZIP for this opening, clear glazing and facade fill
                    state.facadePerOpening[key2] = '';
                    if (state.glazingPerOpening[key2]) state.glazingPerOpening[key2].enabled = false;
                    if (!state.zipPerOpening) state.zipPerOpening = {};
                    var existingZip = state.zipPerOpening[key2] || {fabric: 'veozip', color: 'ral9016', drive: 'manual', count: 1};
                    existingZip.enabled = true;
                    state.zipPerOpening[key2] = existingZip;
                } else {
                    // Regular facade or none — disable glazing and ZIP for this opening
                    state.facadePerOpening[key2] = val;
                    if (state.glazingPerOpening[key2]) state.glazingPerOpening[key2].enabled = false;
                    if (state.zipPerOpening && state.zipPerOpening[key2] && !val) {
                        // "none" deselection: keep ZIP as-is (user can manage in ZIP section)
                    } else if (state.zipPerOpening && state.zipPerOpening[key2] && val) {
                        // Switching to a facade fill: disable ZIP
                        state.zipPerOpening[key2].enabled = false;
                    }
                }
                state.facadeOpenings = computeFacadeOpenings();
                state.facadeType = (isGlzVal || isZipVal) ? '' : val;
                var tr = this.closest('tr');
                if (tr) {
                    var areaTd = tr.querySelector('.facade-area');
                    if (areaTd) {
                        var o2 = {side: this.dataset.side, bay: parseInt(this.dataset.bay)};
                        var dims2 = facadeOpeningDims(o2);
                        var dHtml = '<span style="font-size:0.82em;color:#555;white-space:nowrap;">' + dims2.wMm + '\u00d7' + dims2.hMm + ' \u043c\u043c</span>';
                        var areaVal2 = (dims2.wMm * dims2.hMm / 1e6).toFixed(2);
                        areaTd.innerHTML = dHtml + '<br><span style="font-size:0.9em;">' + areaVal2 + ' \u043c\u00b2</span>';
                    }
                }
                buildFacadeTopView();
                updateFacadeAreaInfo();
                buildGlazingTable();
                buildZipTable();
                if (state._lastMainResult) updateSchemeForVariant(state.result || state._lastMainResult);
            });
        });
    }

    // ============== Glazing (S500) helpers ==============
    var GLAZING_COLORS_JS = [
        {v:'ral7016', n:'\u0410\u043d\u0442\u0440\u0430\u0446\u0438\u0442'},
        {v:'ral8028', n:'\u041a\u043e\u0440\u0438\u0447\u043d\u0435\u0432\u044b\u0439'},
        {v:'ral9016', n:'\u0411\u0435\u043b\u044b\u0439'},
        {v:'custom',  n:'\u041e\u043a\u0440\u0430\u0441\u043a\u0430 \u043f\u043e RAL'}
    ];
    var GLAZING_GLASS_JS = [
        {v:'transparent', n:'\u041f\u0440\u043e\u0437\u0440\u0430\u0447\u043d\u043e\u0435'},
        {v:'tinted',      n:'\u0422\u043e\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u043e\u0435'}
    ];
    var GLAZING_DIRS_JS = [
        {v:'right',  n:'\u0412\u043f\u0440\u0430\u0432\u043e'},
        {v:'left',   n:'\u0412\u043b\u0435\u0432\u043e'},
        {v:'center', n:'\u041e\u0442 \u0446\u0435\u043d\u0442\u0440\u0430'}
    ];
    var GLAZING_PCS_JS = [2, 3, 4, 5, 6, 8, 10];

    // S100 frameless option lists
    var S100_COLORS_JS = [
        {v:'ral9t08',     n:'Графит текстурный RAL 9T08'},
        {v:'ral7024',     n:'Графит матовый RAL 7024'},
        {v:'ral8028',     n:'Коричневый Муар RAL 8028'},
        {v:'ral9016',     n:'Белый матовый RAL 9016'},
        {v:'ral_special', n:'RAL special (+10%)'}
    ];
    var S100_GLASS_JS = [
        {v:'transparent', n:'\u041f\u0440\u043e\u0437\u0440\u0430\u0447\u043d\u043e\u0435'},
        {v:'tinted_mass', n:'\u0422\u043e\u043d\u0438\u0440. \u0432 \u043c\u0430\u0441\u0441\u0435'}
    ];
    var S100_PCS_JS = [3, 4, 6, 8, 12];

    // W-series guillotine option lists (W500/W600/W700)
    var W_COLORS_JS = [
        {v:'ral9t08',     n:'\u0413\u0440\u0430\u0444\u0438\u0442 \u0442\u0435\u043a\u0441\u0442. RAL 9T08'},
        {v:'ral7024',     n:'\u0413\u0440\u0430\u0444\u0438\u0442 \u043c\u0430\u0442\u043e\u0432\u044b\u0439 RAL 7024'},
        {v:'ral8028',     n:'\u041a\u043e\u0440\u0438\u0447\u043d\u0435\u0432\u044b\u0439 RAL 8028'},
        {v:'ral9016',     n:'\u0411\u0435\u043b\u044b\u0439 \u043c\u0430\u0442. RAL 9016'},
        {v:'ral_special', n:'RAL special (+10%)'}
    ];
    var W_GLASS_JS = [
        {v:'transparent',     n:'\u041f\u0440\u043e\u0437\u0440\u0430\u0447\u043d\u043e\u0435'},
        {v:'multifunctional', n:'\u041c\u0443\u043b\u044c\u0442\u0438\u0444\u0443\u043d\u043a\u0446. (+10%)'}
    ];
    var W_SASHES_JS = [2, 3];
    var W_BOUNDS_JS = {
        W500: {wMin:1.0, wMax:5.0, hMin:1.5, hMax:3.5},
        W600: {wMin:2.0, wMax:5.0, hMin:2.0, hMax:4.0},
        W700: {wMin:2.0, wMax:5.0, hMin:2.0, hMax:4.0}
    };
    function wMinSashes(w) { return (w > 3.6) ? 3 : 2; }
    function isWSeries(s) { s = (s || '').toUpperCase(); return s === 'W500' || s === 'W600' || s === 'W700'; }
    // Explicit S100 configurations as the supplier exposes them.
    // Each entry: cfg-key (v), total panels (pc), direction lock (dir),
    // and human label (n). dir=null means user can pick left/right.
    var S100_CFG_JS = [
        {v:'3',   pc:3,  dir:null,     n:'3'},
        {v:'4',   pc:4,  dir:null,     n:'4'},
        {v:'6',   pc:6,  dir:'side',   n:'6'},
        {v:'3+3', pc:6,  dir:'center', n:'3+3'},
        {v:'4+4', pc:8,  dir:'center', n:'4+4'},
        {v:'6+6', pc:12, dir:'center', n:'6+6'}
    ];
    function s100CfgKey(g) {
        var pc = g.pc, dir = g.direction;
        if (pc === 8)  return '4+4';
        if (pc === 12) return '6+6';
        if (pc === 6)  return (dir === 'center') ? '3+3' : '6';
        if (pc === 4)  return '4';
        return '3';
    }

    function s100MinPanels(w, h) {
        if (!w || !h) return 3;
        if (w > 8.0) return 12;
        if (w > 6.0) return 8;
        if (w > 4.0) return 6;
        if (w > 3.6) return 4;
        return 3;
    }

    function glazingMinPanels(w, h) {
        if (!w || !h) return 2;
        var minByWeight = Math.ceil(w * h * 30 / 88);
        var minByWidth = 2;
        if (w > 3.6) minByWidth = 4;
        if (w > 5.0) minByWidth = 5;
        if (w > 6.0) minByWidth = 6;
        if (w > 7.0) minByWidth = 8;
        if (w > 10.0) minByWidth = 10;
        return Math.max(minByWidth, minByWeight);
    }

    function getGlazingForSide(side) {
        if (!state.glazingPerOpening) return null;
        var bays = (side === 'front' || side === 'back') ? facadeModules(state.width) : facadeLengthModules(state.length);
        for (var i = 0; i < bays; i++) {
            var g = state.glazingPerOpening[side + '_' + i];
            if (g && g.enabled) return g;
        }
        return null;
    }

    function glazingSpec(g) {
        if (!g || !g.enabled) return '';
        var series = (g.series || 'S500').toUpperCase();
        if (isWSeries(series)) {
            var sashes = parseInt(g.sashes) || 0;
            if (sashes !== 2 && sashes !== 3) sashes = 2;
            return [series, sashes, g.color || 'ral9t08', g.glass || 'transparent'].join(':');
        }
        if (series === 'S100') {
            return ['S100', g.pc || 3, g.direction || 'right', g.color || 'ral9t08', g.glass || 'transparent'].join(':');
        }
        return [g.pc || 4, g.direction || 'right', g.color || 'ral7016', g.glass || 'transparent'].join(':');
    }

    function getBayGlzQs(side, count, xPerBay) {
        if (!state.glazingPerOpening) return '';
        var parts = [];
        var idx = 1;
        var sections = (xPerBay > 0) ? (xPerBay + 1) : 1;
        for (var i = 0; i < count; i++) {
            var g = state.glazingPerOpening[side + '_' + i];
            var spec = (g && g.enabled) ? glazingSpec(g) : '';
            for (var j = 0; j < sections; j++) {
                if (spec) parts.push('glz_' + idx + '=' + encodeURIComponent(spec));
                idx++;
            }
        }
        return parts.length ? ('&' + parts.join('&')) : '';
    }

    function computeGlazingOpenings() {
        var out = [];
        Object.keys(state.glazingPerOpening || {}).forEach(function(k) {
            var g = state.glazingPerOpening[k];
            if (!g || !g.enabled) return;
            // mutual exclusion: skip if facade is set on the same key
            if (state.facadePerOpening && state.facadePerOpening[k]) return;
            var parts = k.split('_');
            var bay = parseInt(parts.pop());
            var side = parts.join('_');
            var seriesU = (g.series || 'S500').toUpperCase();
            var defColor = (seriesU === 'S100') ? 'ral9t08' : 'ral7016';
            var entry = {
                series: seriesU,
                side: side, bay: bay,
                color: g.color || defColor,
                glass: g.glass || 'transparent',
                count: parseInt(g.count) || 1
            };
            if (isWSeries(seriesU)) {
                var sashes = parseInt(g.sashes) || 0;
                if (sashes !== 2 && sashes !== 3) sashes = 2;
                entry.sashes = sashes;
                entry.plavnik = (g.plavnik === true);
                if (g.brand === 'simu' || g.brand === 'somfy') entry.brand = g.brand;
            } else {
                entry.pc = parseInt(g.pc) || (seriesU === 'S100' ? 3 : 4);
                entry.direction = g.direction || 'right';
            }
            out.push(entry);
        });
        return out;
    }

    function _glazingDimsForKey(side) {
        var colW = (state.selectedVariant === 'Light') ? 0.150 : (state.pergolaType === 'B200' ? 0.100 : 0.164);
        var beamH = (state.selectedVariant === 'Light') ? 0.250 : (state.pergolaType === 'B200' ? 0.200 : 0.280);
        var ph = state.height || 3.0;
        var hM = Math.max(0.1, ph - beamH);
        var n, totalDim;
        if (side === 'front' || side === 'back') {
            n = Math.max(1, facadeModules(state.width));
            totalDim = state.width;
        } else {
            n = Math.max(1, facadeLengthModules(state.length));
            totalDim = state.length;
        }
        var fullBay = totalDim / n;
        var wM = Math.max(0.1, fullBay - 2 * colW);
        return {wM: wM, hM: hM};
    }

    function updateGlazingAreaInfo() {
        var infoEl = document.getElementById('glazing-area-info');
        if (!infoEl) return;
        var actives = computeGlazingOpenings();
        if (actives.length === 0) {
            infoEl.style.display = 'none'; infoEl.textContent = ''; return;
        }
        var totalArea = 0;
        actives.forEach(function(o) {
            var d = _glazingDimsForKey(o.side);
            totalArea += d.wM * d.hM * (o.count || 1);
        });
        infoEl.style.display = 'block';
        infoEl.textContent = '\u041e\u0441\u0442\u0435\u043a\u043b\u0451\u043d\u043d\u044b\u0445 \u043f\u0440\u043e\u0451\u043c\u043e\u0432: ' + actives.length
            + ' \u2014 \u043f\u043b\u043e\u0449\u0430\u0434\u044c \u2248 ' + totalArea.toFixed(2) + ' \u043c\u00b2';
    }

    function _drawGlazingMiniSvg(svgEl, w, h, pc, direction, color, glass, series, sashes) {
        if (!svgEl || !w || !h) { if (svgEl) svgEl.innerHTML = ''; return; }
        series = (series || 'S500').toUpperCase();
        if (isWSeries(series)) {
            var sN = parseInt(sashes) || 2;
            if (sN !== 2 && sN !== 3) sN = 2;
            var pCw;
            if (color === 'ral9016') pCw = '#d8d8d8';
            else if (color === 'ral8028') pCw = '#5c3d1e';
            else if (color === 'ral7024') pCw = '#3a4148';
            else if (color === 'ral_special') pCw = '#7a7a7a';
            else pCw = '#2e3338';
            var isMulti = (glass === 'multifunctional');
            var cG1w = isMulti ? '#a8c0d0' : '#cce0f0';
            var cG2w = isMulti ? '#7d97a8' : '#a8c8e0';
            var fW = 200, asp = h / w;
            var fH = Math.max(60, Math.min(190, Math.round(fW * asp)));
            var fxw = 8, fyw = 8, VWw = fW + 16, VHw = fH + 22;
            svgEl.setAttribute('viewBox', '0 0 ' + VWw + ' ' + VHw);
            svgEl.setAttribute('width', VWw); svgEl.setAttribute('height', VHw);
            var topPxw = 9, botPxw = 5, sidePxw = 4, midPxw = 3;
            var iXw = fxw + sidePxw, iYw = fyw + topPxw;
            var iWw = fW - 2 * sidePxw, iHw = fH - topPxw - botPxw;
            var sashHpx = (iHw - (sN - 1) * midPxw) / sN;
            var sw = '';
            for (var iw = 0; iw < sN; iw++) {
                var syw = iYw + iw * (sashHpx + midPxw);
                sw += '<rect x="' + iXw + '" y="' + syw + '" width="' + iWw + '" height="' + sashHpx + '" fill="' + cG1w + '"/>';
                sw += '<rect x="' + (iXw + iWw * 0.55) + '" y="' + syw + '" width="' + (iWw * 0.4) + '" height="' + sashHpx + '" fill="' + cG2w + '" opacity="0.35"/>';
                if (iw < sN - 1) sw += '<rect x="' + iXw + '" y="' + (syw + sashHpx) + '" width="' + iWw + '" height="' + midPxw + '" fill="' + pCw + '"/>';
            }
            sw += '<rect x="' + fxw + '" y="' + fyw + '" width="' + sidePxw + '" height="' + fH + '" fill="' + pCw + '"/>';
            sw += '<rect x="' + (fxw + fW - sidePxw) + '" y="' + fyw + '" width="' + sidePxw + '" height="' + fH + '" fill="' + pCw + '"/>';
            sw += '<rect x="' + fxw + '" y="' + fyw + '" width="' + fW + '" height="' + topPxw + '" fill="' + pCw + '"/>';
            sw += '<rect x="' + fxw + '" y="' + (fyw + fH - botPxw) + '" width="' + fW + '" height="' + botPxw + '" fill="' + pCw + '"/>';
            // Chain marker on top rail
            sw += '<circle cx="' + (fxw + fW * 0.5) + '" cy="' + (fyw + topPxw * 0.5) + '" r="2.5" fill="#dfe7ef" stroke="#1a3a6e" stroke-width="0.6"/>';
            sw += '<text x="' + (fxw + fW * 0.5) + '" y="' + (fyw + fH - botPxw * 0.25) + '" text-anchor="middle" font-size="6" fill="#dfe7ef" font-family="Arial,sans-serif">' + series + '</text>';
            var dimYw = fyw + fH + 8;
            sw += '<line x1="' + fxw + '" y1="' + dimYw + '" x2="' + (fxw + fW) + '" y2="' + dimYw + '" stroke="#8a9bbf" stroke-width="0.6"/>';
            sw += '<text x="' + (fxw + fW / 2) + '" y="' + (dimYw + 8) + '" text-anchor="middle" font-size="8" fill="#8a9bbf" font-family="Arial,sans-serif">' + Math.round(w * 1000) + '\u00d7' + Math.round(h * 1000) + ' \u043c\u043c</text>';
            svgEl.innerHTML = sw;
            return;
        }
        var n = parseInt(pc) || 3;
        var isS100 = (series === 'S100');
        var isCenter;
        if (isS100) {
            isCenter = (direction === 'center') || n === 8 || n === 12;
        } else {
            isCenter = (direction === 'center' || n === 6 || n === 8 || n === 10);
        }
        var pC, isTinted, cG1, cG2;
        if (isS100) {
            if (color === 'ral9016') pC = '#d8d8d8';
            else if (color === 'ral8028') pC = '#5c3d1e';
            else if (color === 'ral7024') pC = '#3a4148';
            else if (color === 'ral_special') pC = '#7a7a7a';
            else pC = '#2e3338';
            isTinted = (glass === 'tinted_mass');
            cG1 = isTinted ? '#7d8e96' : '#d8e8f0';
            cG2 = isTinted ? '#5d7078' : '#b8d4e6';
        } else {
            if (color === 'ral9016') pC = '#d0d0d0';
            else if (color === 'ral8028') pC = '#5c3d1e';
            else if (color === 'custom') pC = '#777';
            else pC = '#3a4048';
            isTinted = (glass === 'tinted');
            var isBronze = isTinted && color === 'ral8028';
            cG1 = isBronze ? '#b8956a' : (isTinted ? '#8a9ea8' : '#cce0f0');
            cG2 = isBronze ? '#9a7548' : (isTinted ? '#6a8088' : '#a8c8e0');
        }
        var frameW = 200;
        var aspect = h / w;
        var frameH = Math.round(frameW * aspect);
        if (frameH < 50) frameH = 50;
        if (frameH > 180) frameH = 180;
        var topPx, botPx, sidePx, midPx, centerPx;
        if (isS100) {
            topPx = (n === 3) ? 6 : 5.5;
            botPx = 3;
            sidePx = 3.5;  // frameless between panels, but L/R end profiles per spec
            midPx = 1.6;
            centerPx = 3;
        } else {
            topPx = 8; botPx = 4; sidePx = 6; midPx = 2.4; centerPx = 4;
        }
        var fx = 8, fy = 8;
        var VW = frameW + 16, VH = frameH + 22;
        svgEl.setAttribute('viewBox', '0 0 ' + VW + ' ' + VH);
        svgEl.setAttribute('height', VH);
        svgEl.setAttribute('width', VW);
        var s = '';
        // Top + bottom rails
        s += '<rect x="' + fx + '" y="' + fy + '" width="' + frameW + '" height="' + topPx + '" fill="' + pC + '"/>';
        s += '<rect x="' + fx + '" y="' + (fy + frameH - botPx) + '" width="' + frameW + '" height="' + botPx + '" fill="' + pC + '"/>';
        // Side frames (S500 only — frameless for S100)
        if (sidePx > 0) {
            s += '<rect x="' + fx + '" y="' + fy + '" width="' + sidePx + '" height="' + frameH + '" fill="' + pC + '"/>';
            s += '<rect x="' + (fx + frameW - sidePx) + '" y="' + fy + '" width="' + sidePx + '" height="' + frameH + '" fill="' + pC + '"/>';
        }
        var iX = fx + sidePx, iY = fy + topPx;
        var iW = frameW - 2 * sidePx, iH = frameH - topPx - botPx;
        if (isCenter) {
            var cx = iX + iW / 2;
            s += '<rect x="' + (cx - centerPx / 2) + '" y="' + iY + '" width="' + centerPx + '" height="' + iH + '" fill="' + pC + '"/>';
        }
        var halfN = isCenter ? n / 2 : n;
        var panelW = isCenter ? ((iW - centerPx) / 2 - (halfN - 1) * midPx) / halfN
                              : (iW - (n - 1) * midPx) / n;
        for (var i = 0; i < n; i++) {
            var sIdx = isCenter ? (i % (n / 2)) : i;
            var sOff = (isCenter && i >= n / 2) ? ((iW - centerPx) / 2 + centerPx) : 0;
            var px = iX + sOff + sIdx * (panelW + midPx);
            if (sIdx > 0) {
                s += '<rect x="' + (px - midPx) + '" y="' + iY + '" width="' + midPx + '" height="' + iH + '" fill="' + pC + '"/>';
            }
            s += '<rect x="' + px + '" y="' + iY + '" width="' + panelW + '" height="' + iH + '" fill="' + cG1 + '"/>';
            s += '<rect x="' + (px + panelW * 0.5) + '" y="' + iY + '" width="' + (panelW * 0.5) + '" height="' + iH + '" fill="' + cG2 + '" opacity="0.3"/>';
        }
        var dimY = fy + frameH + 8;
        s += '<line x1="' + fx + '" y1="' + dimY + '" x2="' + (fx + frameW) + '" y2="' + dimY + '" stroke="#8a9bbf" stroke-width="0.6"/>';
        s += '<text x="' + (fx + frameW / 2) + '" y="' + (dimY + 8) + '" text-anchor="middle" font-size="8" fill="#8a9bbf" font-family="Arial,sans-serif">' + Math.round(w * 1000) + '\u00d7' + Math.round(h * 1000) + ' \u043c\u043c</text>';
        svgEl.innerHTML = s;
    }

    function _normalizeGlzCfg(g, w, h) {
        var series = (g.series || 'S500').toUpperCase();
        if (isWSeries(series)) {
            var minSash = wMinSashes(w);
            if (g.sashes !== 2 && g.sashes !== 3) g.sashes = minSash;
            if (g.sashes < minSash) g.sashes = minSash;
            if (['ral9t08','ral7024','ral8028','ral9016','ral_special'].indexOf(g.color) === -1) g.color = 'ral9t08';
            if (g.glass !== 'transparent' && g.glass !== 'multifunctional') g.glass = 'transparent';
            if (typeof g.plavnik !== 'boolean') g.plavnik = (w > 3.0);
            if (w > 3.0) g.plavnik = true; // forced auto when wider than 3m
            if (g.brand !== 'simu' && g.brand !== 'somfy') g.brand = '';
            return g;
        }
        if (series === 'S100') {
            var minS = s100MinPanels(w, h);
            if (!g.pc || g.pc < minS) g.pc = minS;
            if (S100_PCS_JS.indexOf(g.pc) === -1) {
                for (var ks = 0; ks < S100_PCS_JS.length; ks++) {
                    if (S100_PCS_JS[ks] >= g.pc) { g.pc = S100_PCS_JS[ks]; break; }
                }
            }
            if (g.pc === 8 || g.pc === 12) g.direction = 'center';
            if (!g.color || ['ral9t08','ral7024','ral8028','ral9016','ral_special'].indexOf(g.color) === -1) g.color = 'ral9t08';
            if (g.glass !== 'transparent' && g.glass !== 'tinted_mass') g.glass = 'transparent';
            return g;
        }
        var minP = glazingMinPanels(w, h);
        if (!g.pc || g.pc < minP) g.pc = minP;
        if (GLAZING_PCS_JS.indexOf(g.pc) === -1) {
            for (var k = 0; k < GLAZING_PCS_JS.length; k++) {
                if (GLAZING_PCS_JS[k] >= g.pc) { g.pc = GLAZING_PCS_JS[k]; break; }
            }
        }
        if ((w >= 6 && g.pc >= 6) || g.pc >= 8) g.direction = 'center';
        if (g.pc % 2 !== 0 && g.direction === 'center') g.direction = 'right';
        return g;
    }

    function buildGlazingTable() {
        var tableEl = document.getElementById('glazing-opening-table');
        if (!tableEl) return;
        var W = state.width, L = state.length;
        if (W <= 0 || L <= 0) { tableEl.innerHTML = '<div style="color:#999;font-size:0.85rem;padding:8px 4px;">\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u0440\u0430\u0437\u043c\u0435\u0440\u044b \u043d\u0430 \u0448\u0430\u0433\u0435 3</div>'; return; }
        var mods = facadeModules(W);
        var lMods = facadeLengthModules(L);
        var openings = [];
        for (var ai = 0; ai < lMods; ai++) openings.push({side:'left', bay:ai, label:lMods>1?'A'+(ai+1):'A', desc:lMods>1?'\u0421\u043b\u0435\u0432\u0430 \u00b7 \u041f\u0440\u043e\u0451\u043c '+(ai+1):'\u0421\u043b\u0435\u0432\u0430'});
        for (var bi = 0; bi < mods; bi++)  openings.push({side:'back', bay:bi, label:mods>1?'B'+(bi+1):'B', desc:mods>1?'\u0421\u0437\u0430\u0434\u0438 \u00b7 \u041f\u0440\u043e\u0451\u043c '+(bi+1):'\u0421\u0437\u0430\u0434\u0438'});
        for (var ci = 0; ci < lMods; ci++) openings.push({side:'right', bay:ci, label:lMods>1?'C'+(ci+1):'C', desc:lMods>1?'\u0421\u043f\u0440\u0430\u0432\u0430 \u00b7 \u041f\u0440\u043e\u0451\u043c '+(ci+1):'\u0421\u043f\u0440\u0430\u0432\u0430'});
        for (var fi = 0; fi < mods; fi++)  openings.push({side:'front', bay:fi, label:mods>1?'F'+(fi+1):'F', desc:mods>1?'\u0424\u0430\u0441\u0430\u0434 \u00b7 \u041f\u0440\u043e\u0451\u043c '+(fi+1):'\u0424\u0430\u0441\u0430\u0434'});

        // Build only config rows for openings where glazing is enabled (toggled via the facade dropdown above)
        var enabledOpenings = openings.filter(function(o) {
            var key = o.side + '_' + o.bay;
            var g = state.glazingPerOpening[key];
            return g && g.enabled;
        });
        if (enabledOpenings.length === 0) {
            tableEl.innerHTML = '<div style="color:#7a8aa8;font-size:0.85rem;padding:10px 4px;font-style:italic;">'
                + '\u0427\u0442\u043e\u0431\u044b \u0434\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u043e\u0441\u0442\u0435\u043a\u043b\u0435\u043d\u0438\u0435 \u0432 \u043f\u0440\u043e\u0451\u043c \u2014 \u0432\u044b\u0431\u0435\u0440\u0438\u0442\u0435 <strong>S500</strong> \u0438\u043b\u0438 <strong>S100</strong> \u0432 \u0442\u0430\u0431\u043b\u0438\u0446\u0435 \u00ab\u0422\u0438\u043f \u0437\u0430\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u044f\u00bb \u0432\u044b\u0448\u0435.'
                + '</div>';
            updateGlazingAreaInfo();
            return;
        }
        var html = '<table class="facade-table"><thead><tr>'
            + '<th>\u041f\u0440\u043e\u0451\u043c</th>'
            + '<th>\u0420\u0430\u0441\u043f\u043e\u043b\u043e\u0436\u0435\u043d\u0438\u0435</th>'
            + '<th>\u041a\u043e\u043d\u0444\u0438\u0433\u0443\u0440\u0430\u0446\u0438\u044f \u043e\u0441\u0442\u0435\u043a\u043b\u0435\u043d\u0438\u044f</th>'
            + '<th>\u0420\u0430\u0437\u043c\u0435\u0440 / \u041f\u043b\u043e\u0449\u0430\u0434\u044c</th>'
            + '</tr></thead><tbody>';
        enabledOpenings.forEach(function(o) {
            var key = o.side + '_' + o.bay;
            var dims = _glazingDimsForKey(o.side);
            var g = state.glazingPerOpening[key];
            var seriesU = (g.series || 'S500').toUpperCase();
            var outOfRange;
            if (isWSeries(seriesU)) {
                var wb = W_BOUNDS_JS[seriesU];
                outOfRange = (dims.wM < wb.wMin || dims.hM < wb.hMin || dims.wM > wb.wMax || dims.hM > wb.hMax);
            } else if (seriesU === 'S100') {
                outOfRange = (dims.wM < 1.8 || dims.hM < 1.5 || dims.wM > 12.0 || dims.hM > 3.0);
            } else {
                outOfRange = (dims.wM < 1.8 || dims.hM < 1.7 || dims.wM > 12.0 || dims.hM > 3.25);
            }
            if (outOfRange) {
                g.enabled = false;
                state.glazingPerOpening[key] = g;
                return;
            }
            g = _normalizeGlzCfg(g, dims.wM, dims.hM);
            state.glazingPerOpening[key] = g;
            var dimsHtml = '<span style="font-size:0.82em;color:#555;white-space:nowrap;">' + Math.round(dims.wM*1000) + '\u00d7' + Math.round(dims.hM*1000) + ' \u043c\u043c</span>';
            var areaVal = (dims.wM * dims.hM).toFixed(2);
            var areaHtml = '<br><span style="font-size:0.9em;">' + areaVal + ' \u043c\u00b2</span>';
            var COLORS, GLASS, PCS, minP, unitWord, summary;
            if (isWSeries(seriesU)) {
                COLORS = W_COLORS_JS; GLASS = W_GLASS_JS;
                summary = seriesU + ' \u00b7 ' + (g.sashes || 2) + ' \u0441\u0442\u0432\u043e\u0440\u043e\u043a \u00b7 '
                    + (COLORS.find(function(c){return c.v===g.color;})||{n:g.color}).n + ' \u00b7 '
                    + (GLASS.find(function(c){return c.v===g.glass;})||{n:g.glass}).n
                    + (g.plavnik ? ' \u00b7 +\u043f\u043b\u0430\u0432\u043d\u0438\u043a' : '');
            } else {
                COLORS = (seriesU === 'S100') ? S100_COLORS_JS : GLAZING_COLORS_JS;
                GLASS  = (seriesU === 'S100') ? S100_GLASS_JS  : GLAZING_GLASS_JS;
                PCS    = (seriesU === 'S100') ? S100_PCS_JS    : GLAZING_PCS_JS;
                minP   = (seriesU === 'S100') ? s100MinPanels(dims.wM, dims.hM) : glazingMinPanels(dims.wM, dims.hM);
                unitWord = (seriesU === 'S100') ? '\u043f\u0430\u043d.' : '\u0441\u0442\u0432.';
                summary = seriesU + ' \u00b7 ' + (g.pc || minP) + ' ' + unitWord + ' \u00b7 '
                    + (GLAZING_DIRS_JS.find(function(d){return d.v===g.direction;})||{n:g.direction}).n + ' \u00b7 '
                    + (COLORS.find(function(c){return c.v===g.color;})||{n:g.color}).n + ' \u00b7 '
                    + (GLASS.find(function(c){return c.v===g.glass;})||{n:g.glass}).n;
            }
            html += '<tr data-key="' + key + '">';
            html += '<td><span class="facade-lbl">' + o.label + '</span></td>';
            html += '<td>' + o.desc + '</td>';
            html += '<td><span style="font-size:0.85em;color:#1a3a6e;font-weight:600;">' + summary + '</span></td>';
            html += '<td class="facade-area">' + dimsHtml + areaHtml + '</td></tr>';
            if (isWSeries(seriesU)) {
                var minSash = wMinSashes(dims.wM);
                var sashOpts = '';
                W_SASHES_JS.forEach(function(s) {
                    var dis = (s < minSash) ? ' disabled' : '';
                    var auto = (s === minSash) ? ' (\u0430\u0432\u0442\u043e)' : '';
                    sashOpts += '<option value="' + s + '"' + dis + (g.sashes === s ? ' selected' : '') + '>' + s + ' \u0441\u0442\u0432\u043e\u0440\u043e\u043a' + auto + '</option>';
                });
                var wColOpts = '';
                COLORS.forEach(function(c) { wColOpts += '<option value="' + c.v + '"' + (g.color===c.v?' selected':'') + '>' + c.n + '</option>'; });
                var wGlOpts = '';
                GLASS.forEach(function(c) { wGlOpts += '<option value="' + c.v + '"' + (g.glass===c.v?' selected':'') + '>' + c.n + '</option>'; });
                var brOpts = '<option value=""' + (!g.brand?' selected':'') + '>\u0410\u0432\u0442\u043e (\u043f\u043e \u043f\u0435\u0440\u0433\u043e\u043b\u0435)</option>'
                           + '<option value="simu"' + (g.brand==='simu'?' selected':'') + '>SIMU</option>'
                           + '<option value="somfy"' + (g.brand==='somfy'?' selected':'') + '>SOMFY</option>';
                var plavForced = (dims.wM > 3.0);
                var plavChecked = g.plavnik ? ' checked' : '';
                var plavDis = plavForced ? ' disabled' : '';
                html += '<tr class="glz-cfg-row" data-key="' + key + '"><td colspan="4" style="background:#f6f9fc;padding:0.6rem 0.9rem;">';
                html += '<div class="glz-grid">';
                html += '<div><label>\u0421\u0442\u0432\u043e\u0440\u043a\u0438 (\u0430\u0432\u0442\u043e\u043f\u043e\u0434\u0431\u043e\u0440)</label><select class="form-select form-select-sm glz-fld" data-fld="sashes" data-key="' + key + '">' + sashOpts + '</select></div>';
                html += '<div><label>\u0426\u0432\u0435\u0442 \u043f\u0440\u043e\u0444\u0438\u043b\u044f</label><select class="form-select form-select-sm glz-fld" data-fld="color" data-key="' + key + '">' + wColOpts + '</select></div>';
                html += '<div><label>\u0421\u0442\u0435\u043a\u043b\u043e\u043f\u0430\u043a\u0435\u0442</label><select class="form-select form-select-sm glz-fld" data-fld="glass" data-key="' + key + '">' + wGlOpts + '</select></div>';
                html += '<div><label>\u041c\u0430\u0440\u043a\u0430 \u043f\u0440\u0438\u0432\u043e\u0434\u0430</label><select class="form-select form-select-sm glz-fld" data-fld="brand" data-key="' + key + '">' + brOpts + '</select></div>';
                html += '<div style="display:flex;align-items:end;"><label style="font-size:0.85em;cursor:' + (plavForced ? 'not-allowed' : 'pointer') + ';"><input type="checkbox" class="glz-fld" data-fld="plavnik" data-key="' + key + '"' + plavChecked + plavDis + '> \u041f\u043b\u0430\u0432\u043d\u0438\u043a' + (plavForced ? ' (\u043e\u0431\u044f\u0437.)' : '') + '</label></div>';
                html += '</div>';
                html += '<div style="margin-top:0.4rem;font-size:0.8em;color:#5a6a85;">' + 
                    '\u0413\u0438\u043b\u044c\u043e\u0442\u0438\u043d\u043d\u043e\u0435 \u043e\u0441\u0442\u0435\u043a\u043b\u0435\u043d\u0438\u0435: \u0441\u0442\u0432\u043e\u0440\u043a\u0438 \u043f\u043e\u0434\u043d\u0438\u043c\u0430\u044e\u0442\u0441\u044f \u0432\u0432\u0435\u0440\u0445 \u044d\u043b\u0435\u043a\u0442\u0440\u043e\u043f\u0440\u0438\u0432\u043e\u0434\u043e\u043c. \u041f\u0440\u0438\u0432\u043e\u0434 \u0438 \u043f\u0443\u043b\u044c\u0442 \u0432\u044b\u0431\u0438\u0440\u0430\u044e\u0442\u0441\u044f \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u0438.</div>';
                html += '<div class="glz-preview" style="margin-top:0.5rem;"><svg class="glz-mini-svg" data-key="' + key + '" xmlns="http://www.w3.org/2000/svg"></svg></div>';
                html += '</td></tr>';
                return;
            }
            {
                var pcOpts = '';
                if (seriesU === 'S100') {
                    var curCfg = s100CfgKey(g);
                    S100_CFG_JS.forEach(function(c) {
                        var disP = c.pc < minP ? ' disabled' : '';
                        var autoTag = (c.pc === minP && c.dir !== 'center') ? ' (\u0430\u0432\u0442\u043e)' : '';
                        pcOpts += '<option value="' + c.v + '" data-pc="' + c.pc + '" data-dir="' + (c.dir || '') + '"' + disP + (curCfg === c.v ? ' selected' : '') + '>' + c.n + autoTag + '</option>';
                    });
                } else {
                    PCS.forEach(function(p) {
                        var disP = p < minP ? ' disabled' : '';
                        var autoTag = (p === minP) ? ' (\u0430\u0432\u0442\u043e)' : '';
                        var lbl = (p===6?'6 (3+3)':p===8?'8 (4+4)':p===10?'10 (5+5)':p+(p===2||p===3||p===4?' \u043f\u0430\u043d\u0435\u043b\u0438':' \u043f\u0430\u043d\u0435\u043b\u0435\u0439'));
                        pcOpts += '<option value="' + p + '"' + disP + (g.pc===p?' selected':'') + '>' + lbl + autoTag + '</option>';
                    });
                }
                var dirOpts = '';
                var allowCenter, forceCenter, denyCenter = false;
                if (seriesU === 'S100') {
                    var ck = s100CfgKey(g);
                    forceCenter = (ck === '3+3' || ck === '4+4' || ck === '6+6');
                    allowCenter = forceCenter;
                    denyCenter = (ck === '6');
                } else {
                    allowCenter = (g.pc % 2 === 0 && g.pc >= 4) || g.pc >= 6;
                    forceCenter = (dims.wM >= 6 && g.pc >= 6) || g.pc >= 8;
                }
                GLAZING_DIRS_JS.forEach(function(d) {
                    var dd = (d.v==='center' && !allowCenter) ? ' disabled' : '';
                    if (forceCenter && d.v !== 'center') dd = ' disabled';
                    dirOpts += '<option value="' + d.v + '"' + dd + (g.direction===d.v?' selected':'') + '>' + d.n + '</option>';
                });
                var colOpts = '';
                COLORS.forEach(function(c) { colOpts += '<option value="' + c.v + '"' + (g.color===c.v?' selected':'') + '>' + c.n + '</option>'; });
                var glOpts = '';
                GLASS.forEach(function(c) { glOpts += '<option value="' + c.v + '"' + (g.glass===c.v?' selected':'') + '>' + c.n + '</option>'; });
                var glassLabel = (seriesU === 'S100') ? '\u0422\u0438\u043f \u0441\u0442\u0435\u043a\u043b\u0430' : '\u0422\u0438\u043f \u0441\u0442\u0435\u043a\u043b\u043e\u043f\u0430\u043a\u0435\u0442\u0430';
                var pcLabel = (seriesU === 'S100') ? '\u041f\u0430\u043d\u0435\u043b\u0435\u0439 (\u0430\u0432\u0442\u043e\u043f\u043e\u0434\u0431\u043e\u0440)' : '\u0421\u0442\u0432\u043e\u0440\u043e\u043a (\u0430\u0432\u0442\u043e\u043f\u043e\u0434\u0431\u043e\u0440)';
                html += '<tr class="glz-cfg-row" data-key="' + key + '"><td colspan="4" style="background:#f6f9fc;padding:0.6rem 0.9rem;">';
                html += '<div class="glz-grid">';
                html += '<div><label>' + pcLabel + '</label><select class="form-select form-select-sm glz-fld" data-fld="pc" data-key="' + key + '">' + pcOpts + '</select></div>';
                html += '<div><label>\u041d\u0430\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435</label><select class="form-select form-select-sm glz-fld" data-fld="direction" data-key="' + key + '">' + dirOpts + '</select></div>';
                html += '<div><label>\u0426\u0432\u0435\u0442 \u043f\u0440\u043e\u0444\u0438\u043b\u044f</label><select class="form-select form-select-sm glz-fld" data-fld="color" data-key="' + key + '">' + colOpts + '</select></div>';
                html += '<div><label>' + glassLabel + '</label><select class="form-select form-select-sm glz-fld" data-fld="glass" data-key="' + key + '">' + glOpts + '</select></div>';
                html += '</div>';
                html += '<div class="glz-preview" style="margin-top:0.5rem;"><svg class="glz-mini-svg" data-key="' + key + '" xmlns="http://www.w3.org/2000/svg"></svg></div>';
                html += '</td></tr>';
            }
        });
        html += '</tbody></table>';
        tableEl.innerHTML = html;

        // Wire up — dropdown enable/disable
        tableEl.querySelectorAll('.glz-en').forEach(function(sel) {
            sel.addEventListener('change', function() {
                var k = this.dataset.key;
                state.glazingPerOpening[k] = state.glazingPerOpening[k] || {pc:0, direction:'right', color:'ral7016', glass:'transparent', count:1};
                state.glazingPerOpening[k].enabled = (this.value === '1');
                buildGlazingTable();
                buildZipTable();
                buildFacadeTable();
                updateGlazingAreaInfo();
                if (state._lastMainResult) updateSchemeForVariant(state.result || state._lastMainResult);
            });
        });
        tableEl.querySelectorAll('.glz-fld').forEach(function(el) {
            el.addEventListener('change', function() {
                var k = this.dataset.key;
                var fld = this.dataset.fld;
                var val = this.value;
                state.glazingPerOpening[k] = state.glazingPerOpening[k] || {enabled:true};
                var entry = state.glazingPerOpening[k];
                var seriesL = (entry.series || 'S500').toUpperCase();
                if (fld === 'plavnik') {
                    entry.plavnik = !!this.checked;
                } else if (fld === 'sashes') {
                    entry.sashes = parseInt(val) || 2;
                } else if (fld === 'pc' && seriesL === 'S100') {
                    var opt = this.options[this.selectedIndex];
                    var pcN = parseInt(opt.dataset.pc) || parseInt(val) || 3;
                    var dirLock = opt.dataset.dir || '';
                    entry.pc = pcN;
                    if (dirLock === 'center') entry.direction = 'center';
                    else if (dirLock === 'side' && entry.direction === 'center') entry.direction = 'right';
                } else {
                    if (fld === 'pc' || fld === 'count') val = parseInt(val) || 1;
                    entry[fld] = val;
                }
                buildGlazingTable();
                buildZipTable();
                updateGlazingAreaInfo();
                if (state._lastMainResult) updateSchemeForVariant(state.result || state._lastMainResult);
            });
        });
        // Render mini previews
        tableEl.querySelectorAll('.glz-mini-svg').forEach(function(svg) {
            var k = svg.dataset.key;
            var g = state.glazingPerOpening[k];
            if (!g || !g.enabled) return;
            var sideLocal = k.split('_').slice(0, -1).join('_');
            var d = _glazingDimsForKey(sideLocal);
            _drawGlazingMiniSvg(svg, d.wM, d.hM, g.pc, g.direction, g.color, g.glass, g.series, g.sashes);
        });
        updateGlazingAreaInfo();
    }

    function buildGlazingPreviewBlock() {
        var W = state.width, L = state.length;
        if (!W || !L || W <= 0 || L <= 0) return '';
        var mods = facadeModules(W);
        var lMods = facadeLengthModules(L);
        var openings = [];
        for (var ai = 0; ai < lMods; ai++) openings.push({side:'left',  bay:ai, label:lMods>1?'A'+(ai+1):'A', desc:lMods>1?'\u0421\u043b\u0435\u0432\u0430 \u00b7 \u041f\u0440\u043e\u0451\u043c '+(ai+1):'\u0421\u043b\u0435\u0432\u0430'});
        for (var bi = 0; bi < mods;  bi++) openings.push({side:'back',  bay:bi, label:mods>1?'B'+(bi+1):'B',  desc:mods>1?'\u0421\u0437\u0430\u0434\u0438 \u00b7 \u041f\u0440\u043e\u0451\u043c '+(bi+1):'\u0421\u0437\u0430\u0434\u0438'});
        for (var ci = 0; ci < lMods; ci++) openings.push({side:'right', bay:ci, label:lMods>1?'C'+(ci+1):'C', desc:lMods>1?'\u0421\u043f\u0440\u0430\u0432\u0430 \u00b7 \u041f\u0440\u043e\u0451\u043c '+(ci+1):'\u0421\u043f\u0440\u0430\u0432\u0430'});
        for (var fi = 0; fi < mods;  fi++) openings.push({side:'front', bay:fi, label:mods>1?'F'+(fi+1):'F',  desc:mods>1?'\u0424\u0430\u0441\u0430\u0434 \u00b7 \u041f\u0440\u043e\u0451\u043c '+(fi+1):'\u0424\u0430\u0441\u0430\u0434'});

        var enabled = openings.filter(function(o) {
            var g = state.glazingPerOpening[o.side + '_' + o.bay];
            return g && g.enabled;
        });
        if (enabled.length === 0) return '';

        var html = '<div class="kp-block" id="kp-glazing-preview-block">' +
            '<div class="kp-block-header"><div class="kp-block-icon" style="background:#1a3a6e;">\uD83E\uDE9F</div><div class="kp-block-title">\u041e\u0441\u0442\u0435\u043a\u043b\u0435\u043d\u0438\u0435 \u043f\u043e \u043f\u0440\u043e\u0451\u043c\u0430\u043c</div></div>' +
            '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:0.8rem;">';
        enabled.forEach(function(o) {
            var key = o.side + '_' + o.bay;
            var g = state.glazingPerOpening[key];
            var dims = _glazingDimsForKey(o.side);
            var seriesU = (g.series || 'S500').toUpperCase();
            var summary;
            if (isWSeries(seriesU)) {
                var Cw = W_COLORS_JS, Gw = W_GLASS_JS;
                summary = seriesU + ' \u00b7 ' + (g.sashes || 2) + ' \u0441\u0442\u0432\u043e\u0440\u043e\u043a \u00b7 ' +
                    ((Cw.find(function(c){return c.v===g.color;}) || {n:g.color}).n) + ' \u00b7 ' +
                    ((Gw.find(function(c){return c.v===g.glass;}) || {n:g.glass}).n) +
                    (g.plavnik ? ' \u00b7 +\u043f\u043b\u0430\u0432\u043d\u0438\u043a' : '');
            } else {
                var Cs = (seriesU === 'S100') ? S100_COLORS_JS : GLAZING_COLORS_JS;
                var Gs = (seriesU === 'S100') ? S100_GLASS_JS  : GLAZING_GLASS_JS;
                var unitWord = (seriesU === 'S100') ? '\u043f\u0430\u043d.' : '\u0441\u0442\u0432.';
                summary = seriesU + ' \u00b7 ' + (g.pc || '') + ' ' + unitWord + ' \u00b7 ' +
                    ((GLAZING_DIRS_JS.find(function(d){return d.v===g.direction;}) || {n:g.direction}).n) + ' \u00b7 ' +
                    ((Cs.find(function(c){return c.v===g.color;}) || {n:g.color}).n) + ' \u00b7 ' +
                    ((Gs.find(function(c){return c.v===g.glass;}) || {n:g.glass}).n);
            }
            html += '<div style="border:1px solid #e5e9f0;border-radius:8px;padding:0.6rem;background:#fbfcfe;">' +
                '<div style="display:flex;align-items:center;gap:0.4rem;margin-bottom:0.4rem;">' +
                    '<span style="background:#1a3a6e;color:#fff;border-radius:4px;padding:1px 7px;font-weight:700;font-size:0.85em;">' + o.label + '</span>' +
                    '<span style="font-size:0.85em;color:#1a3a6e;font-weight:600;">' + escHtml(o.desc) + '</span>' +
                '</div>' +
                '<div style="text-align:center;"><svg class="glz-preview-mini-svg" data-key="' + key + '" xmlns="http://www.w3.org/2000/svg"></svg></div>' +
                '<div style="margin-top:0.3rem;font-size:0.78em;color:#1a3a6e;font-weight:600;text-align:center;">' + summary + '</div>' +
                '<div style="margin-top:0.15rem;font-size:0.75em;color:#666;text-align:center;">' + Math.round(dims.wM * 1000) + '\u00d7' + Math.round(dims.hM * 1000) + ' \u043c\u043c \u00b7 ' + (dims.wM * dims.hM).toFixed(2) + ' \u043c\u00b2</div>' +
            '</div>';
        });
        html += '</div></div>';
        return html;
    }

    function renderGlazingPreviewSvgs(rootEl) {
        if (!rootEl) return;
        rootEl.querySelectorAll('.glz-preview-mini-svg').forEach(function(svg) {
            var k = svg.dataset.key;
            var g = state.glazingPerOpening[k];
            if (!g || !g.enabled) return;
            var sideLocal = k.split('_').slice(0, -1).join('_');
            var d = _glazingDimsForKey(sideLocal);
            _drawGlazingMiniSvg(svg, d.wM, d.hM, g.pc, g.direction, g.color, g.glass, g.series, g.sashes);
        });
    }

    function injectGlazingPreviewIntoSavedKp() {
        var sec = stepsEl.resultsSection;
        if (!sec) return;
        var existing = document.getElementById('kp-glazing-preview-block');
        if (existing) existing.parentNode.removeChild(existing);
        var html = buildGlazingPreviewBlock();
        if (!html) return;
        var holder = document.createElement('div');
        holder.innerHTML = html;
        var node = holder.firstChild;
        var anchor = document.getElementById('marketing-kp-container');
        if (anchor && anchor.parentNode) {
            anchor.parentNode.insertBefore(node, anchor);
        } else {
            sec.appendChild(node);
        }
        renderGlazingPreviewSvgs(node);
    }

    // ===================== ZIP awning per-opening editor =====================
    var ZIP_FABRICS_JS = [
        {v:'veozip', n:'Veozip (Screen Veosol)'},
        {v:'soltis', n:'Soltis W96/W88 (+15 \u20ac/\u043c\u00b2)'},
        {v:'copaco',  n:'Copaco Lunar Blackout (+15 \u20ac/\u043c\u00b2)'}
    ];
    var ZIP_COLORS_JS = [
        {v:'ral9016',    n:'\u0411\u0435\u043b\u044b\u0439 RAL 9016'},
        {v:'ral7024',    n:'\u0413\u0440\u0430\u0444\u0438\u0442 RAL 7024'},
        {v:'ral9t08',    n:'\u0413\u0440\u0430\u0444\u0438\u0442 \u0442\u0435\u043a\u0441\u0442. RAL 9T08'},
        {v:'ral8028',    n:'\u041a\u043e\u0440\u0438\u0447\u043d\u0435\u0432\u044b\u0439 RAL 8028'},
        {v:'ral_special',n:'RAL special (+10%)'}
    ];
    var ZIP_DRIVES_JS = [
        {v:'manual',   n:'\u0420\u0443\u0447\u043d\u043e\u0435 (50 \u20ac)'},
        {v:'simu',     n:'\u042d\u043b\u0435\u043a\u0442\u0440\u043e SIMU'},
        {v:'somfy',    n:'\u042d\u043b\u0435\u043a\u0442\u0440\u043e Somfy'},
        {v:'decolife', n:'\u042d\u043b\u0435\u043a\u0442\u0440\u043e Decolife'}
    ];

    function computeZipOpenings() {
        var out = [];
        Object.keys(state.zipPerOpening || {}).forEach(function(k) {
            var z = state.zipPerOpening[k];
            if (!z || !z.enabled) return;
            var parts = k.split('_');
            var bay = parseInt(parts.pop());
            var side = parts.join('_');
            out.push({
                side: side, bay: bay,
                fabric: z.fabric || 'veozip',
                color: z.color || 'ral9016',
                drive: z.drive || 'manual',
                count: parseInt(z.count) || 1
            });
        });
        return out;
    }

    function updateZipAreaInfo() {
        var infoEl = document.getElementById('zip-area-info');
        if (!infoEl) return;
        var actives = computeZipOpenings();
        if (actives.length === 0) { infoEl.style.display = 'none'; infoEl.textContent = ''; return; }
        infoEl.style.display = 'block';
        infoEl.textContent = 'ZIP-\u043c\u0430\u0440\u043a\u0438\u0437: ' + actives.length + ' \u043f\u0440\u043e\u0451\u043c\u0430';
    }

    function buildZipTable() {
        var tableEl = document.getElementById('zip-opening-table');
        if (!tableEl) return;
        var W = state.width, L = state.length;
        if (W <= 0 || L <= 0) { tableEl.innerHTML = '<div style="color:#999;font-size:0.85rem;padding:8px 4px;">\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u0440\u0430\u0437\u043c\u0435\u0440\u044b \u043d\u0430 \u0448\u0430\u0433\u0435 3</div>'; return; }
        var mods = facadeModules(W);
        var lMods = facadeLengthModules(L);
        var openings = [];
        for (var ai = 0; ai < lMods; ai++) openings.push({side:'left', bay:ai, label:lMods>1?'A'+(ai+1):'A', desc:lMods>1?'\u0421\u043b\u0435\u0432\u0430 \u00b7 \u041f\u0440\u043e\u0451\u043c '+(ai+1):'\u0421\u043b\u0435\u0432\u0430'});
        for (var bi = 0; bi < mods; bi++)  openings.push({side:'back', bay:bi, label:mods>1?'B'+(bi+1):'B', desc:mods>1?'\u0421\u0437\u0430\u0434\u0438 \u00b7 \u041f\u0440\u043e\u0451\u043c '+(bi+1):'\u0421\u0437\u0430\u0434\u0438'});
        for (var ci = 0; ci < lMods; ci++) openings.push({side:'right', bay:ci, label:lMods>1?'C'+(ci+1):'C', desc:lMods>1?'\u0421\u043f\u0440\u0430\u0432\u0430 \u00b7 \u041f\u0440\u043e\u0451\u043c '+(ci+1):'\u0421\u043f\u0440\u0430\u0432\u0430'});
        for (var fi = 0; fi < mods; fi++)  openings.push({side:'front', bay:fi, label:mods>1?'F'+(fi+1):'F', desc:mods>1?'\u0424\u0430\u0441\u0430\u0434 \u00b7 \u041f\u0440\u043e\u0451\u043c '+(fi+1):'\u0424\u0430\u0441\u0430\u0434'});

        var html = '<table class="facade-table"><thead><tr>'
            + '<th>\u041f\u0440\u043e\u0451\u043c</th>'
            + '<th>\u0420\u0430\u0441\u043f\u043e\u043b\u043e\u0436\u0435\u043d\u0438\u0435</th>'
            + '<th>ZIP-\u043c\u0430\u0440\u043a\u0438\u0437\u0430</th>'
            + '<th>\u041f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u044b</th>'
            + '</tr></thead><tbody>';

        openings.forEach(function(o) {
            var key = o.side + '_' + o.bay;
            var z = state.zipPerOpening[key] || {};
            var enabled = !!z.enabled;
            var hasGlz = !!(state.glazingPerOpening[key] && state.glazingPerOpening[key].enabled);
            var overlayNotice = '';
            if (hasGlz) {
                overlayNotice = '<br><span style="font-size:0.75em;color:#b45309;">\u041d\u0430\u043a\u043b\u0430\u0434\u043d\u043e\u0439 \u043c\u043e\u043d\u0442\u0430\u0436: +100 \u043c\u043c \u0448\u0438\u0440\u0438\u043d\u0430, +100/130 \u043c\u043c \u0432\u044b\u0441\u043e\u0442\u0430</span>';
            }
            var toggleBtnStyle = enabled ? 'background:#1a3a6e;color:#fff' : 'background:#e5e9f0;color:#555';
            var toggleBtnText = enabled ? 'ZIP \u2713' : '+ ZIP';
            html += '<tr data-key="' + key + '">';
            html += '<td><span class="facade-lbl">' + o.label + '</span></td>';
            html += '<td>' + o.desc + overlayNotice + '</td>';
            html += '<td><button class="zip-toggle-btn" data-key="' + key + '" style="' + toggleBtnStyle + ';border:none;border-radius:5px;padding:3px 10px;font-size:0.83em;cursor:pointer;">' + toggleBtnText + '</button></td>';
            if (enabled) {
                var fabOpts = '';
                ZIP_FABRICS_JS.forEach(function(f) { fabOpts += '<option value="' + f.v + '"' + ((z.fabric||'veozip')===f.v?' selected':'') + '>' + f.n + '</option>'; });
                var colOpts = '';
                ZIP_COLORS_JS.forEach(function(c) { colOpts += '<option value="' + c.v + '"' + ((z.color||'ral9016')===c.v?' selected':'') + '>' + c.n + '</option>'; });
                var driveType = (z.drive && z.drive !== 'manual') ? 'electric' : 'manual';
                var drvTypeSel = '<select class="form-select form-select-sm zip-fld" data-fld="drive_type" data-key="' + key + '">'
                    + '<option value="manual"' + (driveType==='manual'?' selected':'') + '>\u0420\u0443\u0447\u043d\u043e\u0435 (50 \u20ac)</option>'
                    + '<option value="electric"' + (driveType==='electric'?' selected':'') + '>\u042d\u043b\u0435\u043a\u0442\u0440\u043e</option>'
                    + '</select>';
                var brandSel = '';
                if (driveType === 'electric') {
                    var ZIP_BRANDS = [{v:'simu',n:'SIMU'},{v:'somfy',n:'Somfy'},{v:'decolife',n:'Decolife'}];
                    var brOpts = '';
                    var curBrand = (z.drive && z.drive !== 'manual') ? z.drive : 'simu';
                    ZIP_BRANDS.forEach(function(b) { brOpts += '<option value="' + b.v + '"' + (curBrand===b.v?' selected':'') + '>' + b.n + '</option>'; });
                    brandSel = '<div><label>\u0411\u0440\u0435\u043d\u0434</label><select class="form-select form-select-sm zip-fld" data-fld="drive" data-key="' + key + '">' + brOpts + '</select></div>';
                }
                html += '<td><div class="glz-grid">'
                    + '<div><label>\u0422\u043a\u0430\u043d\u044c</label><select class="form-select form-select-sm zip-fld" data-fld="fabric" data-key="' + key + '">' + fabOpts + '</select></div>'
                    + '<div><label>\u0426\u0432\u0435\u0442 \u043f\u0440\u043e\u0444\u0438\u043b\u044f</label><select class="form-select form-select-sm zip-fld" data-fld="color" data-key="' + key + '">' + colOpts + '</select></div>'
                    + '<div><label>\u041f\u0440\u0438\u0432\u043e\u0434</label>' + drvTypeSel + '</div>'
                    + brandSel
                    + '</div></td>';
            } else {
                html += '<td style="color:#aaa;font-size:0.82em;">\u2014</td>';
            }
            html += '</tr>';
        });
        html += '</tbody></table>';
        tableEl.innerHTML = html;

        tableEl.querySelectorAll('.zip-toggle-btn').forEach(function(btn) {
            btn.addEventListener('click', function() {
                var k = this.dataset.key;
                var z = state.zipPerOpening[k] || {fabric:'veozip', color:'ral9016', drive:'manual', count:1};
                z.enabled = !z.enabled;
                state.zipPerOpening[k] = z;
                buildZipTable();
                updateZipAreaInfo();
                buildFacadeTable();
            });
        });
        tableEl.querySelectorAll('.zip-fld').forEach(function(sel) {
            sel.addEventListener('change', function() {
                var k = this.dataset.key;
                var fld = this.dataset.fld;
                if (!state.zipPerOpening[k]) state.zipPerOpening[k] = {fabric:'veozip', color:'ral9016', drive:'manual', count:1, enabled:true};
                if (fld === 'drive_type') {
                    if (this.value === 'manual') {
                        state.zipPerOpening[k].drive = 'manual';
                    } else {
                        if (state.zipPerOpening[k].drive === 'manual') {
                            state.zipPerOpening[k].drive = 'simu';
                        }
                    }
                    buildZipTable();
                } else {
                    state.zipPerOpening[k][fld] = this.value;
                    updateZipAreaInfo();
                }
            });
        });
        updateZipAreaInfo();
    }

    function buildFacadeTopView() {
        var svg = document.getElementById('facade-topview-svg');
        var hint = document.getElementById('facade-topview-hint');
        if (!svg) return;
        var W = state.width;
        var L = state.length;
        if (W <= 0 || L <= 0) {
            svg.setAttribute('viewBox', '0 0 300 60');
            svg.setAttribute('width', '300'); svg.setAttribute('height', '60');
            svg.innerHTML = '<rect width="300" height="60" fill="none"/>' +
                '<text x="150" y="34" text-anchor="middle" fill="#aab" font-size="12" font-family="Arial,sans-serif">' +
                '\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u0440\u0430\u0437\u043c\u0435\u0440\u044b \u043d\u0430 \u0448\u0430\u0433\u0435 3</text>';
            if (hint) { hint.textContent = ''; }
            return;
        }
        var mods = facadeModules(W);
        var lMods = facadeLengthModules(L);
        var ML = 30; var MR = 16; var MT = 22; var MB = 24;
        var STRIP = 16; var COL = 14;
        var MAX_W = 270; var MAX_H = 240;
        var scale = Math.min(MAX_W / W, MAX_H / L);
        var drawW = Math.max(110, Math.round(W * scale));
        var drawH = Math.max(75, Math.round(L * scale));
        var svgW = drawW + ML + MR;
        var svgH = drawH + MT + MB;
        var ox = ML; var oy = MT;
        var innerBayW = (drawW - 2 * COL) / mods;
        var innerBayH = (drawH - 2 * COL) / lMods;
        var canClick = true;
        var selFill = '#1a3a6e'; var selStroke = '#0d2550';
        var unFill = '#cde0f5';
        var unStroke = '#7aA0c8';
        var cur = 'pointer';
        var p = [];

        function isSel(s, b) { return !!(state.facadePerOpening[s+'_'+b]); }

        p.push('<rect x="'+ox+'" y="'+oy+'" width="'+drawW+'" height="'+drawH+'" fill="#b8cadf" rx="2"/>');
        var ix=ox+STRIP; var iy=oy+STRIP; var iw=drawW-2*STRIP; var ih=drawH-2*STRIP;
        p.push('<rect x="'+ix+'" y="'+iy+'" width="'+iw+'" height="'+ih+'" fill="#eef6ff" rx="1"/>');
        var nLam=Math.max(3,Math.min(Math.round(L/0.25),22));
        for(var li=0;li<nLam;li++){
            var ly=iy+(li+0.5)*ih/nLam;
            p.push('<line x1="'+ix+'" y1="'+ly+'" x2="'+(ix+iw)+'" y2="'+ly+'" stroke="#b0c8e0" stroke-width="0.7"/>');
        }
        for(var mc=1;mc<mods;mc++){
            var mbx=Math.round(ox+mc*drawW/mods-COL/2);
            var mby=oy+STRIP; var mbh=drawH-2*STRIP;
            p.push('<rect x="'+mbx+'" y="'+mby+'" width="'+COL+'" height="'+mbh+'" fill="#b8cadf" pointer-events="none"><title>\u0411\u0430\u043b\u043a\u0430 298\xd7280 \u2014 \u0434\u0432\u043e\u0439\u043d\u043e\u0439 \u0441\u043b\u0438\u0432\u043d\u043e\u0439 \u043b\u043e\u0442\u043e\u043a</title></rect>');
            var dcx=mbx+COL/2;
            p.push('<line x1="'+(dcx-2)+'" y1="'+(mby+5)+'" x2="'+(dcx-2)+'" y2="'+(mby+mbh-5)+'" stroke="#7a8fab" stroke-width="1.2" stroke-linecap="round" pointer-events="none"/>');
            p.push('<line x1="'+(dcx+1.5)+'" y1="'+(mby+5)+'" x2="'+(dcx+1.5)+'" y2="'+(mby+mbh-5)+'" stroke="#7a8fab" stroke-width="1.2" stroke-linecap="round" pointer-events="none"/>');
        }
        function bayLbl(side, bay) {
            var letter = side === 'front' ? 'F' : side === 'back' ? 'B' : side === 'left' ? 'A' : 'C';
            var total = (side === 'front' || side === 'back') ? mods : lMods;
            return total > 1 ? letter + (bay + 1) : letter;
        }

        for(var lm=1;lm<lMods;lm++){
            var lbY=Math.round(oy+COL+lm*innerBayH-COL/2);
            var lbX=ox+STRIP; var lbW=drawW-2*STRIP;
            p.push('<rect x="'+lbX+'" y="'+lbY+'" width="'+lbW+'" height="'+COL+'" fill="#b8cadf" pointer-events="none"><title>\u0411\u0430\u043b\u043a\u0430 298\xd7280 \u2014 \u0434\u0432\u043e\u0439\u043d\u043e\u0439 \u0441\u043b\u0438\u0432\u043d\u043e\u0439 \u043b\u043e\u0442\u043e\u043a</title></rect>');
            var dcY=lbY+COL/2;
            p.push('<line x1="'+(lbX+5)+'" y1="'+(dcY-2)+'" x2="'+(lbX+lbW-5)+'" y2="'+(dcY-2)+'" stroke="#7a8fab" stroke-width="1.2" stroke-linecap="round" pointer-events="none"/>');
            p.push('<line x1="'+(lbX+5)+'" y1="'+(dcY+1.5)+'" x2="'+(lbX+lbW-5)+'" y2="'+(dcY+1.5)+'" stroke="#7a8fab" stroke-width="1.2" stroke-linecap="round" pointer-events="none"/>');
        }

        for(var bb=0;bb<mods;bb++){
            var sb=isSel('back',bb);
            var bbx=ox+COL+bb*innerBayW; var bbw=innerBayW;
            p.push('<rect x="'+bbx+'" y="'+oy+'" width="'+bbw+'" height="'+STRIP+'" fill="'+(sb?selFill:unFill)+'" stroke="'+(sb?selStroke:unStroke)+'" stroke-width="1" rx="1" cursor="'+cur+'" data-side="back" data-bay="'+bb+'"/>');
            p.push('<text x="'+(bbx+bbw/2)+'" y="'+(oy+STRIP/2+3.5)+'" text-anchor="middle" fill="'+(sb?'#fff':'#1e3d70')+'" font-size="8" font-weight="bold" font-family="Arial,sans-serif" pointer-events="none">'+bayLbl('back',bb)+'</text>');
        }
        for(var bf=0;bf<mods;bf++){
            var s=isSel('front',bf);
            var bx=ox+COL+bf*innerBayW; var bw=innerBayW;
            p.push('<rect x="'+bx+'" y="'+(oy+drawH-STRIP)+'" width="'+bw+'" height="'+STRIP+'" fill="'+(s?selFill:unFill)+'" stroke="'+(s?selStroke:unStroke)+'" stroke-width="1" rx="1" cursor="'+cur+'" data-side="front" data-bay="'+bf+'"/>');
            p.push('<text x="'+(bx+bw/2)+'" y="'+(oy+drawH-STRIP/2+3.5)+'" text-anchor="middle" fill="'+(s?'#fff':'#1e3d70')+'" font-size="8" font-weight="bold" font-family="Arial,sans-serif" pointer-events="none">'+bayLbl('front',bf)+'</text>');
        }
        for(var la=0;la<lMods;la++){
            var sLA=isSel('left',la);
            var laY=oy+COL+la*innerBayH; var laH=innerBayH;
            var laMidY=laY+laH/2;
            p.push('<rect x="'+ox+'" y="'+laY+'" width="'+STRIP+'" height="'+laH+'" fill="'+(sLA?selFill:unFill)+'" stroke="'+(sLA?selStroke:unStroke)+'" stroke-width="1" rx="1" cursor="'+cur+'" data-side="left" data-bay="'+la+'"/>');
            p.push('<text transform="translate('+(ox+STRIP/2)+','+laMidY+') rotate(-90)" text-anchor="middle" fill="'+(sLA?'#fff':'#1e3d70')+'" font-size="8" font-weight="bold" font-family="Arial,sans-serif" pointer-events="none">'+bayLbl('left',la)+'</text>');
        }
        for(var lc=0;lc<lMods;lc++){
            var sRC=isSel('right',lc);
            var lcY=oy+COL+lc*innerBayH; var lcH=innerBayH;
            var lcMidY=lcY+lcH/2;
            p.push('<rect x="'+(ox+drawW-STRIP)+'" y="'+lcY+'" width="'+STRIP+'" height="'+lcH+'" fill="'+(sRC?selFill:unFill)+'" stroke="'+(sRC?selStroke:unStroke)+'" stroke-width="1" rx="1" cursor="'+cur+'" data-side="right" data-bay="'+lc+'"/>');
            p.push('<text transform="translate('+(ox+drawW-STRIP/2)+','+lcMidY+') rotate(-90)" text-anchor="middle" fill="'+(sRC?'#fff':'#1e3d70')+'" font-size="8" font-weight="bold" font-family="Arial,sans-serif" pointer-events="none">'+bayLbl('right',lc)+'</text>');
        }
        var cf='#1a3a6e';
        [[ox,oy],[ox+drawW-COL,oy],[ox,oy+drawH-COL],[ox+drawW-COL,oy+drawH-COL]].forEach(function(c){
            p.push('<rect x="'+c[0]+'" y="'+c[1]+'" width="'+COL+'" height="'+COL+'" fill="'+cf+'" rx="2" pointer-events="none"/>');
        });
        for(var mc2=1;mc2<mods;mc2++){
            var mcx2=Math.round(ox+mc2*drawW/mods-COL/2);
            p.push('<rect x="'+mcx2+'" y="'+oy+'" width="'+COL+'" height="'+COL+'" fill="'+cf+'" rx="2" pointer-events="none"/>');
            p.push('<rect x="'+mcx2+'" y="'+(oy+drawH-COL)+'" width="'+COL+'" height="'+COL+'" fill="'+cf+'" rx="2" pointer-events="none"/>');
        }
        for(var lm2=1;lm2<lMods;lm2++){
            var lbY2=Math.round(oy+COL+lm2*innerBayH-COL/2);
            p.push('<rect x="'+ox+'" y="'+lbY2+'" width="'+COL+'" height="'+COL+'" fill="'+cf+'" rx="2" pointer-events="none"/>');
            p.push('<rect x="'+(ox+drawW-COL)+'" y="'+lbY2+'" width="'+COL+'" height="'+COL+'" fill="'+cf+'" rx="2" pointer-events="none"/>');
            for(var mc3=1;mc3<mods;mc3++){
                var mcx3=Math.round(ox+mc3*drawW/mods-COL/2);
                p.push('<rect x="'+mcx3+'" y="'+lbY2+'" width="'+COL+'" height="'+COL+'" fill="'+cf+'" rx="2" pointer-events="none"/>');
            }
        }
        p.push('<text x="'+(ox+drawW/2)+'" y="'+(oy-8)+'" text-anchor="middle" fill="#667" font-size="8" font-style="italic" font-family="Arial,sans-serif">\u0412\u0438\u0434 \u0441\u0432\u0435\u0440\u0445\u0443 \u00b7 S = '+(W*L).toFixed(1)+' \u043c\u00b2</text>');
        p.push('<text x="'+(ox+drawW/2)+'" y="'+(oy+drawH+14)+'" text-anchor="middle" fill="#334" font-size="10" font-weight="bold" font-family="Arial,sans-serif">'+W.toFixed(2)+' \u043c</text>');
        p.push('<text transform="translate('+(ox-18)+','+(oy+drawH/2)+') rotate(-90)" text-anchor="middle" fill="#334" font-size="10" font-weight="bold" font-family="Arial,sans-serif">'+L.toFixed(2)+' \u043c</text>');
        if(mods===1 && lMods===1){
            p.push('<text x="'+(ox+drawW/2)+'" y="'+(oy+drawH/2+4)+'" text-anchor="middle" fill="#99bbcc" font-size="9" font-family="Arial,sans-serif" pointer-events="none">1 \u043c\u043e\u0434\u0443\u043b\u044c</text>');
        }

        svg.setAttribute('viewBox','0 0 '+svgW+' '+svgH);
        svg.setAttribute('width',svgW); svg.setAttribute('height',svgH);
        svg.innerHTML = p.join('');

        svg.querySelectorAll('rect[data-side]').forEach(function(rect){
            if(canClick){
                rect.addEventListener('mouseenter',function(){
                    var s2=this.dataset.side; var b2=parseInt(this.dataset.bay);
                    if(!isSel(s2,b2)) this.setAttribute('fill','#8ab8dc');
                });
                rect.addEventListener('mouseleave',function(){
                    var s2=this.dataset.side; var b2=parseInt(this.dataset.bay);
                    if(!isSel(s2,b2)) this.setAttribute('fill',unFill);
                });
            }
            rect.addEventListener('click',function(){
                var s3=this.dataset.side; var b3=parseInt(this.dataset.bay);
                var sel=document.querySelector('.facade-type-sel[data-side="'+s3+'"][data-bay="'+b3+'"]');
                if(sel){
                    sel.scrollIntoView({behavior:'smooth',block:'nearest'});
                    sel.focus();
                    var tr=sel.closest('tr');
                    if(tr){
                        tr.classList.add('facade-row-flash');
                        setTimeout(function(){tr.classList.remove('facade-row-flash');},800);
                    }
                }
            });
        });

        if(hint){
            var cnt=computeFacadeOpenings().length;
            if(cnt===0){
                hint.textContent='\u041a\u043b\u0438\u043a\u043d\u0438\u0442\u0435 \u043d\u0430 \u043f\u0440\u043e\u0451\u043c \u0434\u043b\u044f \u0431\u044b\u0441\u0442\u0440\u043e\u0433\u043e \u0434\u043e\u0441\u0442\u0443\u043f\u0430, \u043b\u0438\u0431\u043e \u0432\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u0442\u0438\u043f \u0432 \u0442\u0430\u0431\u043b\u0438\u0446\u0435 \u043d\u0438\u0436\u0435';
                hint.style.color='#888';
            } else {
                hint.textContent='\u0412\u044b\u0431\u0440\u0430\u043d\u043e \u043f\u0440\u043e\u0451\u043c\u043e\u0432: '+cnt;
                hint.style.color='#1a3a6e';
            }
        }
    }

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
            height: state.height,
            lamella_size: state.lamellaSize,
            lamella_type: state.lamellaType,
            lighting: lighting,
            installation: state.installation,
            selected_variant: state.selectedVariant,
            client_name: state.clientName,
            facade_openings: computeFacadeOpenings(),
            glazing_openings: computeGlazingOpenings(),
            zip_openings: computeZipOpenings()
        };

        state._pergolaHeight = state.height || 3.0;
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

        var minCash = Math.min.apply(null, results.map(function(r) { return r.totals.cash; }));
        var minNonCash = Math.min.apply(null, results.map(function(r) { return r.totals.non_cash; }));
        var minWithVat = Math.min.apply(null, results.map(function(r) { return r.totals.with_vat; }));
        var cheapest = minCash;

        function priceCellDiff(val, base) {
            if (!base || val <= base) return '';
            var diff = Math.round(val - base);
            var pct = Math.round((val - base) / base * 100);
            return '<div class="compare-diff">+' + formatPrice(diff) + ' \u20BD (+' + pct + '%)</div>';
        }

        results.forEach(function(r, idx) {
            var label = r.variant_label || r.selected_variant || ('\u0412\u0430\u0440\u0438\u0430\u043D\u0442 ' + (idx + 1));
            var diffHtml = '';
            if (idx > 0) {
                var diff = r.totals.cash - cheapest;
                var pct = cheapest ? Math.round((r.totals.cash - cheapest) / cheapest * 100) : 0;
                diffHtml = '<div class="compare-diff">+' + formatPrice(diff) + ' \u20BD (+' + pct + '%)</div>';
            } else {
                diffHtml = '<div class="compare-best">\u043B\u0443\u0447\u0448\u0430\u044F \u0446\u0435\u043D\u0430</div>';
            }
            tableHtml += '<tr class="compare-row-clickable' + (idx === 0 ? ' compare-row-best' : '') + '" data-variant-idx="' + idx + '">';
            tableHtml += '<td><strong>' + label + '</strong>' + diffHtml + '</td>';
            tableHtml += '<td>' + formatPrice(r.totals.cash) + ' \u20BD' + priceCellDiff(r.totals.cash, minCash) + '</td>';
            tableHtml += '<td>' + formatPrice(r.totals.non_cash) + ' \u20BD' + priceCellDiff(r.totals.non_cash, minNonCash) + '</td>';
            tableHtml += '<td>' + formatPrice(r.totals.with_vat) + ' \u20BD' + priceCellDiff(r.totals.with_vat, minWithVat) + '</td>';
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
                updateSchemeForVariant(r);
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
        state._maxOverhang = (matchedSpec && matchedSpec.max_overhang) ? matchedSpec.max_overhang : null;

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

    function findMatchedSpecForResult(r) {
        if (!r || !r.selected_variant || !state.variantsData) return null;
        var sv = r.selected_variant;
        var sls = r.lamella_size || state.lamellaSize || '';
        var found = null;
        state.variantsData.forEach(function(v) {
            if (v.variant === sv && (!sls || v.lamella_size === sls)) found = v;
        });
        if (!found) {
            state.variantsData.forEach(function(v) { if (v.variant === sv) found = v; });
        }
        return found;
    }

    function findMoForResult(r) {
        var spec = findMatchedSpecForResult(r);
        return spec && spec.max_overhang ? spec.max_overhang : null;
    }

    function updateSchemeForVariant(r) {
        var block = document.getElementById('kp-scheme-block');
        if (!block) return;
        var mo = findMoForResult(r);
        state._maxOverhang = mo;
        var w = block.dataset.w, l = block.dataset.l, m = block.dataset.m;
        var pir = block.dataset.pir === '1';
        var lc = block.dataset.lc;
        var pergolaH = parseFloat(block.dataset.h) || 3.0;
        var refDim = Math.max(parseFloat(w), parseFloat(l), pergolaH);
        var qs = 'w=' + w + '&l=' + l + '&m=' + m +
            (lc ? '&lc=' + lc : '') +
            (mo ? '&mo=' + mo : '') +
            (pir ? '&pir=1' : '') + '&ref=' + refDim;
        var img = document.getElementById('kp-scheme-img');
        if (img) img.src = '/api/pergola-scheme.svg?' + qs + '&_v=' + SVG_V;
        var lm = parseInt(block.dataset.lm) || 1;
        var moAttr = block.dataset.mo || '';
        var _fillF = getFillForSide('front');
        var _fillA = getFillForSide('left');
        var _fillC = getFillForSide('right');
        var _fillB = getFillForSide('back');
        var _fRes = (r && r.facade) || {};
        var _xcF = parseInt(_fRes.extra_cols_f || 0, 10) || 0;
        var _xcB = parseInt(_fRes.extra_cols_b || 0, 10) || 0;
        var _xcA = parseInt(_fRes.extra_cols_a || 0, 10) || 0;
        var _xcC = parseInt(_fRes.extra_cols_c || 0, 10) || 0;
        var xcFront = _xcF > 0 ? ('&xc=' + _xcF) : '';
        var xcBack  = _xcB > 0 ? ('&xc=' + _xcB) : '';
        var xcLeft  = _xcA > 0 ? ('&xc=' + _xcA) : '';
        var xcRight = _xcC > 0 ? ('&xc=' + _xcC) : '';
        var _bayF = getBayFillQs('front', parseInt(m) || 1, _xcF);
        var _bayB = getBayFillQs('back', parseInt(m) || 1, _xcB);
        var _bayA = getBayFillQs('left', lm, _xcA);
        var _bayC = getBayFillQs('right', lm, _xcC);
        var _glzF = getBayGlzQs('front', parseInt(m) || 1, _xcF);
        var _glzB = getBayGlzQs('back', parseInt(m) || 1, _xcB);
        var _glzA = getBayGlzQs('left', lm, _xcA);
        var _glzC = getBayGlzQs('right', lm, _xcC);
        var fqs = 'w=' + w + '&h=' + pergolaH + '&m=' + m + '&ref=' + refDim + xcFront + '&title=' + encodeURIComponent('\u0412\u0438\u0434 \u0441\u043f\u0435\u0440\u0435\u0434\u0438') + _bayF + _glzF;
        var fimg = document.getElementById('kp-front-img');
        if (fimg) fimg.src = '/api/pergola-front.svg?' + fqs + '&_v=' + SVG_V;
        var bqs = 'w=' + w + '&h=' + pergolaH + '&m=' + m + '&ref=' + refDim + xcBack + '&title=' + encodeURIComponent('\u0412\u0438\u0434 \u0441\u0437\u0430\u0434\u0438') + _bayB + _glzB;
        var bimg = document.getElementById('kp-back-img');
        if (bimg) bimg.src = '/api/pergola-front.svg?' + bqs + '&_v=' + SVG_V;
        var sqs = 'w=' + l + '&h=' + pergolaH + '&m=' + lm + (moAttr ? '&mo=' + moAttr : '') + '&ref=' + refDim + xcLeft + '&title=' + encodeURIComponent('\u0412\u0438\u0434 \u0441\u043b\u0435\u0432\u0430') + _bayA + _glzA;
        var simg = document.getElementById('kp-side-img');
        if (simg) simg.src = '/api/pergola-front.svg?' + sqs + '&_v=' + SVG_V;
        var rqs = 'w=' + l + '&h=' + pergolaH + '&m=' + lm + (moAttr ? '&mo=' + moAttr : '') + '&ref=' + refDim + xcRight + '&title=' + encodeURIComponent('\u0412\u0438\u0434 \u0441\u043f\u0440\u0430\u0432\u0430') + _bayC + _glzC;
        var rimg = document.getElementById('kp-right-img');
        if (rimg) rimg.src = '/api/pergola-front.svg?' + rqs + '&_v=' + SVG_V;
        var lcAttr = block.dataset.lc;
        var pirAttr = block.dataset.pir === '1';
        var isoimg = document.getElementById('kp-iso-img');
        if (isoimg && (pirAttr || lcAttr)) {
            var _isoF = _fillF || getGlzForSide('front');
            var _isoA = _fillA || getGlzForSide('left');
            var _isoC = _fillC || getGlzForSide('right');
            var _isoB = _fillB || getGlzForSide('back');
            var iqs = 'w=' + w + '&l=' + l + '&h=' + pergolaH + '&m=' + m + (lcAttr ? '&lc=' + lcAttr : '') + (mo ? '&mo=' + mo : '') + (pirAttr ? '&pir=1' : '') + (_isoF ? '&fill_front=' + encodeURIComponent(_isoF) : '') + (_isoC ? '&fill_right=' + encodeURIComponent(_isoC) : '') + (_isoA ? '&fill_left=' + encodeURIComponent(_isoA) : '') + (_isoB ? '&fill_back=' + encodeURIComponent(_isoB) : '') + '&_v=' + SVG_V;
            isoimg.src = '/api/pergola-iso.svg?' + iqs;
        }
        var warn = document.getElementById('kp-scheme-warn');
        if (warn) {
            var lf = parseFloat(l);
            var needs = mo && lf > mo + 0.001;
            warn.style.display = needs ? 'block' : 'none';
            if (needs) {
                warn.innerHTML = '\u26A0\uFE0F \u0412\u044B\u043D\u043E\u0441 ' + lf + ' \u043C \u043F\u0440\u0435\u0432\u044B\u0448\u0430\u0435\u0442 \u043C\u0430\u043A\u0441\u0438\u043C\u0443\u043C \u0431\u0435\u0437 \u0434\u043E\u043F. \u043E\u043F\u043E\u0440 (' + mo + ' \u043C). \u0414\u043E\u0431\u0430\u0432\u043B\u0435\u043D\u044B \u043F\u0440\u043E\u043C\u0435\u0436\u0443\u0442\u043E\u0447\u043D\u044B\u0435 \u043A\u043E\u043B\u043E\u043D\u043D\u044B \u043F\u043E \u0446\u0435\u043D\u0442\u0440\u0443.';
            }
        }
    }

    function buildMarketingKP(resultOrResults, decoData) {
        var isAll = Array.isArray(resultOrResults);
        var mainResult = isAll ? resultOrResults[0] : resultOrResults;
        state._lastMainResult = mainResult;
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
        var decoKeyMap = {'B500NEW': 'b500', 'B700NEW': 'b700', 'B600': 'b600', 'B200': 'b200'};
        var decoKey = decoKeyMap[state.pergolaType] || '';
        var modelImgMap = {'B500NEW': 'b500.jpg', 'B700NEW': 'b700.jpg', 'B600': 'b600.jpg', 'B200': 'b200.jpg'};
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
            '<div class="kp-model-photo"><img src="' + (decoKey ? '/static/decolife/' + decoKey + '/images/product.jpg' : '/static/images/' + modelImg) + '" alt="' + escHtml(dd.model || pType) + '" onerror="this.src=\'/static/images/' + modelImg + '\';this.onerror=function(){this.parentElement.style.display=\'none\';}" style="width:100%;max-height:400px;object-fit:contain;border-radius:8px;margin-bottom:0.8rem;background:#f5f7fb;"></div>';
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

        /* Block 8a: ZIP awning results */
        var zipRes = mainResult && mainResult.zip;
        if (!isAll && zipRes && zipRes.count > 0) {
            html += '<div class="kp-block">';
            html += '<div class="kp-block-header"><div class="kp-block-icon" style="background:#0ea5e9;">\uD83C\uDF00</div><div class="kp-block-title">ZIP-\u043C\u0430\u0440\u043A\u0438\u0437\u044B (' + zipRes.count + ' \u0448\u0442.)</div></div>';
            html += '<table class="cost-table"><tbody>';
            (zipRes.openings || []).forEach(function(zo) {
                var sideMap = {front:'\u0424\u0430\u0441\u0430\u0434', back:'\u0421\u0437\u0430\u0434\u0438', left:'\u0421\u043B\u0435\u0432\u0430', right:'\u0421\u043F\u0440\u0430\u0432\u0430'};
                var sideLabel = sideMap[zo.side] || zo.side;
                var typeLabel = zo.zip_type || 'ZIP100';
                var adjWmm = zo.adj_w ? Math.round(zo.adj_w * 1000) : 0;
                var adjHmm = zo.adj_h ? Math.round(zo.adj_h * 1000) : 0;
                var dimLabel = (adjWmm && adjHmm) ? (adjWmm + '\u00d7' + adjHmm + ' \u043c\u043c') : '';
                var fabricMap = {veozip:'Veozip', soltis:'Soltis W96', copaco:'Copaco Blackout'};
                var fabricLabel = fabricMap[zo.fabric] || zo.fabric;
                var colorMap = {ral9016:'\u0411\u0435\u043b\u044b\u0439 RAL 9016', ral7024:'\u0413\u0440\u0430\u0444\u0438\u0442 RAL 7024', ral9t08:'\u0413\u0440\u0430\u0444\u0438\u0442 RAL 9T08', ral8028:'\u041a\u043e\u0440\u0438\u0447\u043d. RAL 8028', ral_special:'RAL special'};
                var colorLabel = colorMap[zo.color] || zo.color;
                var driveMap = {manual:'\u0420\u0443\u0447\u043d\u043e\u0435', simu:'SIMU', somfy:'Somfy', decolife:'Decolife'};
                var driveLabel = driveMap[zo.drive] || zo.drive;
                var priceRub = Math.round((zo.total_eur || 0) * mainResult.euro_rate);
                html += '<tr><td>' + sideLabel + ' \u00b7 \u041f\u0440\u043e\u0451\u043c ' + (zo.bay + 1) + ' \u00b7 ' + typeLabel + ' \u00b7 ' + dimLabel + '<br><span style="font-size:0.8em;color:#555;">' + fabricLabel + ' \u00b7 ' + colorLabel + ' \u00b7 ' + driveLabel + '</span></td>' +
                        '<td style="white-space:nowrap;">' + formatPrice(priceRub) + ' \u20BD</td></tr>';
            });
            if (zipRes.pult_name) {
                var pultRub = Math.round((zipRes.pult_eur || 0) * mainResult.euro_rate);
                html += '<tr><td>\u041f\u0443\u043b\u044c\u0442 \u0414\u0423 ' + zipRes.pult_name + ' (ZIP)</td>' +
                        '<td style="white-space:nowrap;">' + formatPrice(pultRub) + ' \u20BD</td></tr>';
            }
            var zipTotalRub = Math.round((zipRes.price || 0) * mainResult.euro_rate);
            html += '<tr style="font-weight:700;border-top:2px solid #e5e9f0;">' +
                    '<td>ZIP-\u043c\u0430\u0440\u043a\u0438\u0437\u044b: \u0438\u0442\u043e\u0433\u043e</td>' +
                    '<td style="white-space:nowrap;">' + formatPrice(zipTotalRub) + ' \u20BD</td></tr>';
            html += '</tbody></table></div>';
        }

        /* Variant comparison (for "all" mode) */
        if (isAll) {
            html += '<div class="kp-block">' +
                '<div class="kp-block-header"><div class="kp-block-icon" style="background:#7c3aed;">\u2261</div><div class="kp-block-title">\u0421\u0440\u0430\u0432\u043D\u0435\u043D\u0438\u0435 \u0432\u0430\u0440\u0438\u0430\u043D\u0442\u043E\u0432</div></div>' +
                '<div class="compare-table-wrap"><table class="compare-table"><thead><tr><th>\u041C\u043E\u0434\u0438\u0444\u0438\u043A\u0430\u0446\u0438\u044F</th><th>\u041D\u0430\u043B\u0438\u0447\u043D\u044B\u0435</th><th>\u0411\u0435\u0437\u043D\u0430\u043B.</th><th>\u0421 \u041D\u0414\u0421</th></tr></thead><tbody>';
            resultOrResults.forEach(function(r, idx) {
                var label = r.variant_label || r.selected_variant || '';
                var badgeHtml = (idx === 0 && resultOrResults.length > 1)
                    ? '<div class="compare-best">\u043B\u0443\u0447\u0448\u0430\u044F \u0446\u0435\u043D\u0430</div>'
                    : '';
                html += '<tr' + (idx === 0 ? ' class="compare-row-best"' : '') + '><td><strong>' + label + '</strong>' + badgeHtml + '</td>' +
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

        /* Block 8b: Top-view scheme */
        var schW = dims.width, schL = dims.length, schM = dims.modules || 1;
        if (schW > 0 && schL > 0) {
            var isPir = state.pergolaType === 'B600';
            var isB200 = state.pergolaType === 'B200';
            var isLight = state.selectedVariant === 'Light';
            var lamMm;
            if (state.pergolaType === 'B200') {
                lamMm = state.lamellaSize === '20' ? 400 : 500;
            } else {
                lamMm = state.lamellaSize === '200' ? 200 : 250;
            }
            var lamCnt = isPir ? '' : Math.floor(schL * 1000 / lamMm);
            var moLocal = findMoForResult(mainResult);
            if (moLocal) state._maxOverhang = moLocal;
            var pergolaH = state._pergolaHeight || 3.0;
            var refDim = Math.max(schW, schL, pergolaH);
            var reinf = (mainResult && mainResult.reinforcement) || {kind: null, extra_columns_count: 0};
            var xc = parseInt(reinf.extra_columns_count || 0, 10) || 0;
            var xcQs = xc > 0 ? '&xc=' + xc : '';
            var facadeRes = (mainResult && mainResult.facade) || {};
            var xcF = parseInt(facadeRes.extra_cols_f || 0, 10) || 0;
            var xcB = parseInt(facadeRes.extra_cols_b || 0, 10) || 0;
            var xcA = parseInt(facadeRes.extra_cols_a || 0, 10) || 0;
            var xcC = parseInt(facadeRes.extra_cols_c || 0, 10) || 0;
            var xcFqs = xcF > 0 ? ('&xc=' + xcF) : '';
            var xcBqs = xcB > 0 ? ('&xc=' + xcB) : '';
            var xcAqs = Math.max(xc, xcA) > 0 ? ('&xc=' + Math.max(xc, xcA)) : '';
            var xcCqs = Math.max(xc, xcC) > 0 ? ('&xc=' + Math.max(xc, xcC)) : '';
            var facadeSchemeQs = (xcA > 0 ? '&xc_a=' + xcA : '') +
                                  (xcC > 0 ? '&xc_c=' + xcC : '') +
                                  (xcF > 0 ? '&xc_f=' + xcF : '') +
                                  (xcB > 0 ? '&xc_b=' + xcB : '');
            var qs = 'w=' + schW + '&l=' + schL + '&m=' + schM +
                (lamCnt !== '' ? '&lc=' + lamCnt : '') +
                (moLocal ? '&mo=' + moLocal : '') +
                (isPir ? '&pir=1' : '') + '&ref=' + refDim + xcQs + facadeSchemeQs;
            var needsExtra = (moLocal && schL > moLocal + 0.001) || xc > 0;
            var colMmQs = isB200 ? '&col_mm=100' : (isLight ? '&col_mm=150&beam_h_mm=250' : '');
            var schLMods = facadeLengthModules(schL);
            var _kpFillF = getFillForSide('front');
            var _kpFillA = getFillForSide('left');
            var _kpFillC = getFillForSide('right');
            var _kpFillB = getFillForSide('back');
            var _kpBayF = getBayFillQs('front', schM, xcF);
            var _kpBayB = getBayFillQs('back', schM, xcB);
            var _kpBayA = getBayFillQs('left', schLMods, xcA);
            var _kpBayC = getBayFillQs('right', schLMods, xcC);
            var _kpGlzF = getBayGlzQs('front', schM, xcF);
            var _kpGlzB = getBayGlzQs('back', schM, xcB);
            var _kpGlzA = getBayGlzQs('left', schLMods, xcA);
            var _kpGlzC = getBayGlzQs('right', schLMods, xcC);
            var fqs = 'w=' + schW + '&h=' + pergolaH + '&m=' + schM + '&ref=' + refDim + xcFqs + '&title=' + encodeURIComponent('\u0412\u0438\u0434 \u0441\u043f\u0435\u0440\u0435\u0434\u0438') + colMmQs + _kpBayF + _kpGlzF + '&_v=' + SVG_V;
            var bqs = 'w=' + schW + '&h=' + pergolaH + '&m=' + schM + '&ref=' + refDim + xcBqs + '&title=' + encodeURIComponent('\u0412\u0438\u0434 \u0441\u0437\u0430\u0434\u0438') + colMmQs + _kpBayB + _kpGlzB + '&_v=' + SVG_V;
            var sqs = 'w=' + schL + '&h=' + pergolaH + '&m=' + schLMods + (moLocal ? '&mo=' + moLocal : '') + '&ref=' + refDim + xcAqs + colMmQs + '&title=' + encodeURIComponent('\u0412\u0438\u0434 \u0441\u043b\u0435\u0432\u0430') + _kpBayA + _kpGlzA + '&_v=' + SVG_V;
            var rqs = 'w=' + schL + '&h=' + pergolaH + '&m=' + schLMods + (moLocal ? '&mo=' + moLocal : '') + '&ref=' + refDim + xcCqs + colMmQs + '&title=' + encodeURIComponent('\u0412\u0438\u0434 \u0441\u043f\u0440\u0430\u0432\u0430') + _kpBayC + _kpGlzC + '&_v=' + SVG_V;
            var _kpIsoF = _kpFillF || getGlzForSide('front');
            var _kpIsoA = _kpFillA || getGlzForSide('left');
            var _kpIsoC = _kpFillC || getGlzForSide('right');
            var _kpIsoB = _kpFillB || getGlzForSide('back');
            var iqs = 'w=' + schW + '&l=' + schL + '&h=' + pergolaH + '&m=' + schM + (lamCnt !== '' ? '&lc=' + lamCnt : '') + (moLocal ? '&mo=' + moLocal : '') + (isPir ? '&pir=1' : '') + xcQs + (_kpIsoF ? '&fill_front=' + encodeURIComponent(_kpIsoF) : '') + (_kpIsoC ? '&fill_right=' + encodeURIComponent(_kpIsoC) : '') + (_kpIsoA ? '&fill_left=' + encodeURIComponent(_kpIsoA) : '') + (_kpIsoB ? '&fill_back=' + encodeURIComponent(_kpIsoB) : '') + '&_v=' + SVG_V;
            var isoLabel = isPir ? '\u0418\u0437\u043E\u043C\u0435\u0442\u0440\u0438\u044F (PIR \u043F\u0430\u043D\u0435\u043B\u0438)' : (isB200 ? '\u0418\u0437\u043E\u043C\u0435\u0442\u0440\u0438\u044F (\u0441\u0442\u0430\u0446\u0438\u043E\u043D\u0430\u0440\u043D\u044B\u0435)' : '\u0418\u0437\u043E\u043C\u0435\u0442\u0440\u0438\u044F (\u043B\u0430\u043C\u0435\u043B\u0438 \u043E\u0442\u043A\u0440\u044B\u0442\u044B)');
            var isoBlock = (isPir || lamCnt) ? (
                '<div style="text-align:center;"><div style="font-size:0.85rem;color:#1a3a6e;font-weight:600;margin-bottom:0.4rem;">' + isoLabel + '</div>' +
                '<img id="kp-iso-img" src="/api/pergola-iso.svg?' + iqs + '" alt="\u0418\u0437\u043E\u043C\u0435\u0442\u0440\u0438\u044F" style="max-width:100%;height:auto;"></div>'
            ) : '';
            html += '<div class="kp-block" id="kp-scheme-block" data-w="' + schW + '" data-l="' + schL + '" data-m="' + schM + '" data-lm="' + schLMods + '" data-pir="' + (isPir ? '1' : '0') + '" data-lc="' + lamCnt + '" data-h="' + pergolaH + '" data-mo="' + (moLocal || '') + '">' +
                '<div class="kp-block-header"><div class="kp-block-icon" style="background:#1a3a6e;">\uD83D\uDCD0</div><div class="kp-block-title">\u0421\u0445\u0435\u043C\u0430 \u043F\u0435\u0440\u0433\u043E\u043B\u044B</div></div>' +
                '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1rem;align-items:start;">' +
                '<div style="text-align:center;"><div style="font-size:0.85rem;color:#1a3a6e;font-weight:600;margin-bottom:0.4rem;">\u0412\u0438\u0434 \u0441\u0432\u0435\u0440\u0445\u0443</div>' +
                '<img id="kp-scheme-img" src="/api/pergola-scheme.svg?' + qs + '&_v=' + SVG_V + '" alt="\u0412\u0438\u0434 \u0441\u0432\u0435\u0440\u0445\u0443" style="max-width:100%;height:auto;"></div>' +
                '<div style="text-align:center;"><div style="font-size:0.85rem;color:#1a3a6e;font-weight:600;margin-bottom:0.4rem;">\u0412\u0438\u0434 \u0441\u043f\u0435\u0440\u0435\u0434\u0438 (F)</div>' +
                '<img id="kp-front-img" src="/api/pergola-front.svg?' + fqs + '" alt="\u0412\u0438\u0434 \u0441\u043f\u0435\u0440\u0435\u0434\u0438" style="max-width:100%;height:auto;"></div>' +
                '<div style="text-align:center;"><div style="font-size:0.85rem;color:#1a3a6e;font-weight:600;margin-bottom:0.4rem;">\u0412\u0438\u0434 \u0441\u0437\u0430\u0434\u0438 (B)</div>' +
                '<img id="kp-back-img" src="/api/pergola-front.svg?' + bqs + '" alt="\u0412\u0438\u0434 \u0441\u0437\u0430\u0434\u0438" style="max-width:100%;height:auto;"></div>' +
                '<div style="text-align:center;"><div style="font-size:0.85rem;color:#1a3a6e;font-weight:600;margin-bottom:0.4rem;">\u0412\u0438\u0434 \u0441\u043b\u0435\u0432\u0430 (A)</div>' +
                '<img id="kp-side-img" src="/api/pergola-front.svg?' + sqs + '" alt="\u0412\u0438\u0434 \u0441\u043b\u0435\u0432\u0430" style="max-width:100%;height:auto;"></div>' +
                '<div style="text-align:center;"><div style="font-size:0.85rem;color:#1a3a6e;font-weight:600;margin-bottom:0.4rem;">\u0412\u0438\u0434 \u0441\u043f\u0440\u0430\u0432\u0430 (C)</div>' +
                '<img id="kp-right-img" src="/api/pergola-front.svg?' + rqs + '" alt="\u0412\u0438\u0434 \u0441\u043f\u0440\u0430\u0432\u0430" style="max-width:100%;height:auto;"></div>' +
                isoBlock +
                '</div>' +
                '<div style="margin-top:0.6rem;font-size:0.82rem;color:#666;text-align:center;">\u0412\u044B\u0441\u043E\u0442\u0430 \u043F\u0435\u0440\u0433\u043E\u043B\u044B: ' + pergolaH.toFixed(2) + ' \u043C (\u0441\u0442\u0430\u043D\u0434\u0430\u0440\u0442). ' + (isB200 ? '\u041A\u043E\u043B\u043E\u043D\u043D\u044B 100\u00D7100 \u043C\u043C, \u0431\u0430\u043B\u043A\u0430 200\u00D750 \u043C\u043C, \u043B\u0430\u043C\u0435\u043B\u0438 200\u00D750 \u043C\u043C.' : (isLight ? '\u041A\u043E\u043B\u043E\u043D\u043D\u044B 150\u00D7150 \u043C\u043C, \u0431\u0430\u043B\u043A\u0430 150\u00D7250 \u043C\u043C.' : '\u041A\u043E\u043B\u043E\u043D\u043D\u044B 164\u00D7164 \u043C\u043C, \u0432\u044B\u0441\u043E\u0442\u0430 \u043B\u043E\u0442\u043A\u0430 280 \u043C\u043C, \u0432\u044B\u043B\u0435\u0442 \u043F\u043B\u043E\u0449\u0430\u0434\u043A\u0438 82 \u043C\u043C.')) + '</div>' +
                '<div id="kp-scheme-warn" style="display:' + (needsExtra ? 'block' : 'none') + ';margin-top:0.6rem;padding:0.6rem 0.8rem;background:#fff8e1;border-left:3px solid #f59e0b;font-size:0.88rem;color:#5d4a00;">' +
                (needsExtra ? '\u26A0\uFE0F \u0412\u044B\u043D\u043E\u0441 ' + schL + ' \u043C \u043F\u0440\u0435\u0432\u044B\u0448\u0430\u0435\u0442 \u043C\u0430\u043A\u0441\u0438\u043C\u0443\u043C \u0431\u0435\u0437 \u0434\u043E\u043F. \u043E\u043F\u043E\u0440 (' + state._maxOverhang + ' \u043C). \u0414\u043E\u0431\u0430\u0432\u043B\u0435\u043D\u044B \u043F\u0440\u043E\u043C\u0435\u0436\u0443\u0442\u043E\u0447\u043D\u044B\u0435 \u043A\u043E\u043B\u043E\u043D\u043D\u044B \u043F\u043E \u0446\u0435\u043D\u0442\u0440\u0443.' : '') +
                '</div>' +
                '</div>';
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
        var kpVideos = PERGOLA_VIDEOS[state.pergolaType] || [];
        if (kpVideos.length) {
            var kpVideoColor = state.pergolaType === 'B600' ? '#f59e0b' : '#1a3a6e';
            html += '<div class="kp-block">' +
                '<div class="kp-block-header"><div class="kp-block-icon" style="background:' + kpVideoColor + ';">\uD83C\uDFA5</div><div class="kp-block-title">\u0412\u0438\u0434\u0435\u043E \u0441 \u043D\u0430\u0448\u0438\u0445 \u0443\u0441\u0442\u0430\u043D\u043E\u0432\u043E\u043A</div></div>' +
                '<div class="kp-video-grid">';
            kpVideos.forEach(function(v) {
                var isShorts = v.type === 'shorts';
                html += '<div class="kp-video-card' + (isShorts ? ' kp-video-card-shorts' : '') + '" style="border-top:3px solid ' + kpVideoColor + ';">' +
                    '<div class="video-iframe-wrap' + (isShorts ? ' video-iframe-shorts' : '') + '">' +
                    '<iframe data-src="https://rutube.ru/play/embed/' + v.id + '" frameborder="0" allowfullscreen allow="autoplay" loading="lazy"></iframe>' +
                    '</div>' +
                    '<div class="video-card-title">' + v.title + '</div></div>';
            });
            html += '</div></div>';
        }

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
            // Rehydrate dimensions and per-opening selections from saved request
            // so renderResults / updateSchemeForVariant can rebuild scheme URLs
            // with the right glz_*/fill_* params (S500 + S100 mix).
            if (req.width)  state.width  = parseFloat(req.width)  || state.width;
            if (req.length) state.length = parseFloat(req.length) || state.length;
            if (req.height) state.height = parseFloat(req.height) || state.height;
            if (req.modules) state.modules = parseInt(req.modules) || state.modules;
            if (req.lamella_type) state.lamellaType = req.lamella_type;
            if (req.selected_variant) state.selectedVariant = req.selected_variant;
            state.facadePerOpening = state.facadePerOpening || {};
            state.glazingPerOpening = state.glazingPerOpening || {};
            (req.facade_openings || []).forEach(function(f) {
                if (f && f.side != null && f.bay != null && f.type) {
                    state.facadePerOpening[f.side + '_' + f.bay] = f.type;
                }
            });
            (req.glazing_openings || []).forEach(function(g) {
                if (!g || g.side == null || g.bay == null) return;
                var seriesU = (g.series || 'S500').toUpperCase();
                var defC = (seriesU === 'S500') ? 'ral7016' : 'ral9t08';
                var entry = {
                    enabled: true,
                    series: seriesU,
                    color: g.color || defC,
                    glass: g.glass || 'transparent',
                    count: parseInt(g.count) || 1
                };
                if (isWSeries(seriesU)) {
                    var s = parseInt(g.sashes) || 0;
                    if (s !== 2 && s !== 3) s = 2;
                    entry.sashes = s;
                    entry.plavnik = (g.plavnik === true);
                    entry.brand = (g.brand === 'simu' || g.brand === 'somfy') ? g.brand : '';
                } else {
                    entry.pc = parseInt(g.pc) || (seriesU === 'S100' ? 3 : 4);
                    entry.direction = g.direction || 'right';
                }
                state.glazingPerOpening[g.side + '_' + g.bay] = entry;
            });
            state.zipPerOpening = state.zipPerOpening || {};
            (req.zip_openings || []).forEach(function(z) {
                if (!z || z.side == null || z.bay == null) return;
                state.zipPerOpening[z.side + '_' + z.bay] = {
                    enabled: true,
                    fabric: z.fabric || 'veozip',
                    color: z.color || 'ral9016',
                    drive: z.drive || 'manual',
                    count: parseInt(z.count) || 1
                };
            });

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

            injectGlazingPreviewIntoSavedKp();

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
