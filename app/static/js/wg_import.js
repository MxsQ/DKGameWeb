(function(){
    // 处理“导入彩虹WG数据”模态框的基础交互（打开/关闭与文件校验）

    const openBtn = document.getElementById('btn-import-wg');
    const modal = document.getElementById('modal-import-wg');
    const cancelBtn = document.getElementById('wg-cancel');
    const confirmBtn = document.getElementById('wg-confirm');
    const fileInput = document.getElementById('wg-excel');
    const gameSelect = document.getElementById('wg-game-select');
    const aliasSelect = document.getElementById('wg-alias-select');

    if(!openBtn || !modal) return;

    function deduplicateAndRenderAliases(options){
        // options: string[] | Array<{value?: string, label?: string}>
        if(!aliasSelect) return;
        const seen = new Set();
        const unique = [];
        (options || []).forEach(item => {
            const value = typeof item === 'string' ? item : (item && (item.value || item.label || ''));
            const label = typeof item === 'string' ? item : (item && (item.label || item.value || ''));
            const key = (value || '').trim().toLowerCase();
            if(!key) return;
            if(!seen.has(key)){
                seen.add(key);
                unique.push({ value, label });
            }
        });
        aliasSelect.innerHTML = '';
        unique.forEach(({value, label}) => {
            const opt = document.createElement('option');
            opt.value = value;
            opt.textContent = label;
            aliasSelect.appendChild(opt);
        });
    }

    function dedupeExistingAliasOptions(){
        if(!aliasSelect) return;
        const current = Array.from(aliasSelect.options).map(o => ({ value: o.value, label: o.textContent || '' }));
        deduplicateAndRenderAliases(current);
    }

    async function loadGames(){
        if(!gameSelect) return;
        try{
            const res = await fetch('/api/games/all');
            const list = await res.json();
            gameSelect.innerHTML = '';
            (list || []).forEach(g => {
                const opt = document.createElement('option');
                opt.value = g.id;
                opt.textContent = g.name;
                gameSelect.appendChild(opt);
            });
        }catch(e){
            gameSelect.innerHTML = '';
        }
    }

    function openModal(){
        modal.classList.remove('hidden');
        if (fileInput) fileInput.value = '';
        // 打开时对现有下拉选项做一次去重
        dedupeExistingAliasOptions();
        // 加载游戏列表
        loadGames();
    }

    function closeModal(){
        modal.classList.add('hidden');
    }

    function validateFile(file){
        if(!file) return { ok: false, msg: '请选择Excel文件' };
        const name = (file.name || '').toLowerCase();
        if(!(name.endsWith('.xlsx') || name.endsWith('.xls'))){
            return { ok: false, msg: '仅支持 .xlsx 或 .xls 文件' };
        }
        return { ok: true };
    }

    openBtn.addEventListener('click', openModal);
    if (cancelBtn) cancelBtn.addEventListener('click', closeModal);

    if (fileInput) {
        fileInput.addEventListener('change', async function(){
            const file = fileInput.files && fileInput.files[0];
            const check = validateFile(file);
            if(!check.ok){
                alert(check.msg);
                fileInput.value = '';
                if (aliasSelect) aliasSelect.innerHTML = '';
                return;
            }

            // 解析Excel，收集“渠道名称”去重后填充到别名下拉
            if (!aliasSelect) return;
            try{
                const arrayBuffer = await file.arrayBuffer();
                const workbook = XLSX.read(arrayBuffer, { type: 'array' });
                const firstSheetName = workbook.SheetNames && workbook.SheetNames[0];
                const sheet = workbook.Sheets[firstSheetName];
                const json = XLSX.utils.sheet_to_json(sheet, { defval: '' });

                const aliasSet = new Set();
                for (const row of json){
                    const raw = row['渠道名称'] ?? row['渠道名'] ?? row['渠道'];
                    const val = raw != null ? String(raw).trim() : '';
                    if (val) aliasSet.add(val);
                }

                const values = Array.from(aliasSet);
                deduplicateAndRenderAliases(values);
                // 默认选中第一项
                if (aliasSelect.options.length > 0) aliasSelect.selectedIndex = 0;
                if (aliasSelect.options.length === 0){
                    const noOpt = document.createElement('option');
                    noOpt.value = '';
                    noOpt.textContent = '未在Excel中找到“渠道名称”列数据';
                    aliasSelect.appendChild(noOpt);
                }
            }catch(err){
                aliasSelect.innerHTML = '';
                const errOpt = document.createElement('option');
                errOpt.value = '';
                errOpt.textContent = 'Excel解析失败：' + (err && err.message ? err.message : String(err));
                aliasSelect.appendChild(errOpt);
            }
        });
    }

    if (confirmBtn) {
        confirmBtn.addEventListener('click', async function(){
            const file = fileInput && fileInput.files && fileInput.files[0];
            const gid = gameSelect ? (gameSelect.value || '') : '';
            const check = validateFile(file);
            if(!check.ok){
                alert(check.msg);
                return;
            }
            if(!gid){
                alert('请选择游戏');
                return;
            }
            const alias = aliasSelect ? (aliasSelect.value || '') : '';
            const form = new FormData();
            form.append('game_id', gid);
            form.append('file', file);
            form.append('alias', alias);
            try{
                const res = await fetch('/api/import/wg', { method: 'POST', body: form });
                const raw = await res.text();
                let data; try { data = JSON.parse(raw); } catch(_) { data = { raw }; }
                if(res.ok){
                    if (data && data.inserted !== undefined && data.updated !== undefined) {
                        if (typeof window.showToast === 'function') {
                            window.showToast(`导入完成！新增 ${data.inserted} 条记录，更新 ${data.updated} 条记录，共处理 ${data.total} 条记录`);
                        } else {
                            alert(`导入完成！新增 ${data.inserted} 条记录，更新 ${data.updated} 条记录，共处理 ${data.total} 条记录`);
                        }
                    } else {
                        if (typeof window.showToast === 'function') {
                            window.showToast('导入成功：' + ((data && data.count) || 0) + ' 条');
                        } else {
                            alert('导入成功：' + ((data && data.count) || 0) + ' 条');
                        }
                    }
                    closeModal();
                } else {
                    const parts = [];
                    if(data && data.message) parts.push(data.message);
                    if(data && data.error) parts.push(String(data.error));
                    if(parts.length === 0 && data && data.raw) parts.push(String(data.raw));
                    parts.push('HTTP ' + res.status);
                    alert('导入失败：' + parts.join(' | '));
                }
            }catch(err){
                alert('请求失败：' + (err && err.message ? err.message : String(err)));
            }
        });
    }

    // 暴露一个全局方法以便后续在获取到别名列表时设置（自动去重）
    window.setWGAliasOptions = function(options){
        deduplicateAndRenderAliases(options);
    };
})();