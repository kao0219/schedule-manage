document.addEventListener('DOMContentLoaded', function () {
    /* ----------- 要素の取得 ------------------------------ */
    const isAllDayCheckbox = document.getElementById('id_is_all_day'); // 終日チェック
    const startDateTime    = document.getElementById('start_time_dt'); // datetime-local（開始）
    const endDateTime      = document.getElementById('end_time_dt');   // datetime-local（終了）
    const startDate        = document.getElementById('start_time_date'); // date（開始）
    const endDate          = document.getElementById('end_time_date');   // date（終了）
    const repeatOptions    = document.querySelectorAll('input[name="repeat_type"]'); // ラジオ一式
    const main             = document.getElementById('main'); // data-is-edit 属性用

    /* ----------- 1. 終日チェックで入力欄をトグル ---------- */
    function toggleAllDayUI() {
        // チェック状態を取得
        console.log('toggleAllDayUI が呼ばれた');
        const allDay = document.getElementById("id_is_all_day").checked;

        // 開始・終了のdatetime-local（時刻付き）を非表示
        startDateTime.style.display = allDay ? 'none'  : 'block';
        endDateTime.style.display   = allDay ? 'none'  : 'block';
         // 開始・終了のdate（終日用・日付のみ）を表示
        startDate.style.display     = allDay ? 'block' : 'none';
        endDate.style.display       = allDay ? 'block' : 'none';
        // 終日ON時は時間を削除
        if (allDay) {
            const now = new Date();
            const yyyy = now.getFullYear();
            const mm = String(now.getMonth() + 1).padStart(2, '0');
            const dd = String(now.getDate()).padStart(2, '0');
            const today = `${yyyy}-${mm}-${dd}`;

            startDate.value = today;
            endDate.value = today;
        }
        evaluateRepeatOptions();
    }

    /* ----------- 2. date → datetime-local 値同期 ---------- */
    function syncDateOnly(e, isStart) {
        // 例: 2025-07-01 → 2025-07-01T00:00 / 23:59
        const dateStr = e.target.value;
        const target  = isStart ? startDateTime : endDateTime;
        target.value  = `${dateStr}T${isStart ? '00:00' : '23:59'}`;

        evaluateRepeatOptions(); // 日付が変われば跨ぎ再判定
    }

    /* ----------- 3. 日跨ぎ判定 & ラジオ強制「なし」 ------- */
    function evaluateRepeatOptions() {
        // 入力チェック
        if (!startDateTime.value || !endDateTime.value) return;

        // 日付部のみ比較
        const sDay = new Date(startDateTime.value).toDateString();
        const eDay = new Date(endDateTime.value).toDateString();
        const isCrossDay = sDay !== eDay;

        // 全ラジオを disabled or enabled
        repeatOptions.forEach(r => r.disabled = isCrossDay);

        // 跨いでいたら value="0"（なし）を強制チェック
        if (isCrossDay) {
            const noneRadio = [...repeatOptions].find(r => r.value === '0');
            if (noneRadio) noneRadio.checked = true;
        }
    }

    /* ----------- 4. 新規登録時にデフォルトを「なし」 ------ */
    if (main && main.dataset.isEdit === 'false') {
        repeatOptions.forEach(r => {
            r.checked = r.value === '0'; // value="0" が「なし」と想定
        });
    }

    /* ----------- 5. イベント登録 -------------------------- */
    // 終日チェック ON/OFF
    if (isAllDayCheckbox) {
        isAllDayCheckbox.addEventListener('change', toggleAllDayUI);
    }

    // date input 変更 → datetime-local に反映
    startDate.addEventListener('change', e => syncDateOnly(e, true));
    endDate.addEventListener('change',   e => syncDateOnly(e, false));

    // datetime-local を直接編集した場合も跨ぎ判定
    startDateTime.addEventListener('change', evaluateRepeatOptions);
    endDateTime.addEventListener('change',   evaluateRepeatOptions);

    /* ----------- 6. 初期表示のUI反映 ---------------------- */
    toggleAllDayUI(); // 画面ロード直後に一度実行

});