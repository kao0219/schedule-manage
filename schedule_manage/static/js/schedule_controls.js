// window.toggleDateTimeFields = function() {
//     const isAllDay = document.getElementById('id_is_all_day').checked;
//     const startTime = document.getElementById('id_start_time');
//     const endTime = document.getElementById('id_end_time');

//     startTime.disabled = isAllDay;
//     endTime.disabled = isAllDay;
// };

// document.addEventListener('DOMContentLoaded', function () {
//     const isAllDayCheckbox = document.getElementById('id_is_all_day');
//     const startTimeInput = document.getElementById('id_start_time');
//     const endTimeInput = document.getElementById('id_end_time');
//     const repeatOptions = document.querySelectorAll('.repeat-option');
    

//     if (!isAllDayCheckbox || !startTimeInput || !endTimeInput || !repeatOptions.length) return;

//     // 終日チェックで時間入力を制御
//     function toggleTimeInputs() {
//       const isChecked = isAllDayCheckbox.checked;
//       startTimeInput.disabled = isChecked;
//       endTimeInput.disabled = isChecked;
//     }
    
//     function toggleDateTimeFields() {
//         const isAllDay = document.getElementById('id_is_all_day').checked;
//         const startTime = document.getElementById('id_start_time');
//         const endTime = document.getElementById('id_end_time');
    
//         startTime.disabled = isAllDay;
//         endTime.disabled = isAllDay;
//     }

//     // 日付を跨いでいたら繰り返し設定を無効化
//     function toggleRepeatOptions() {
//         const startDateStr = startTimeInput.value;
//         const endDateStr = endTimeInput.value;

//         if (!startDateStr || !endDateStr) return;

//         const startDate = new Date(startDateStr);
//         const endDate = new Date(endDateStr);
//         const isDifferentDay = startDate.toDateString() !== endDate.toDateString();

//         repeatOptions.forEach(option => {
//             option.disabled = isDifferentDay;
//         });
//     } 

//     // 初期状態チェック
//     toggleTimeInputs();
//     toggleRepeatOptions();

//     // イベントリスナー登録
//     isAllDayCheckbox.addEventListener('change', () => {
//         toggleTimeInputs();
//         toggleRepeatOptions();
//     });

//     startTimeInput.addEventListener('change', toggleRepeatOptions);
//     endTimeInput.addEventListener('change', toggleRepeatOptions);
// });

  
// function toggleAllDayUI() {
//   const allDay = document.getElementById('id_is_all_day').checked;

//   const sDt  = document.getElementById('start_time_dt');
//   const eDt  = document.getElementById('end_time_dt');
//   const sDat = document.getElementById('start_time_date');
//   const eDat = document.getElementById('end_time_date');

//   if (allDay) {
//     // 表示切替
//     sDt.style.display = eDt.style.display = 'none';
//     sDat.style.display = eDat.style.display = 'inline-block';

//     // date input に初期値をコピー
//     if (sDt.value) sDat.value = sDt.value.slice(0, 10);
//     if (eDt.value) eDat.value = eDt.value.slice(0, 10);
//   } else {
//     sDt.style.display = eDt.style.display = 'inline-block';
//     sDat.style.display = eDat.style.display = 'none';
//   }

//   evaluateRepeatOptions();   // 終日ON/OFF してもラジオ再判定
// }

// /*****************************************************************
//  * date input を編集したら datetime-local に反映
//  *****************************************************************/
// function syncDateOnly(e, isStart) {
//   const dateStr = e.target.value;             // YYYY-MM-DD
//   const dtField = document.getElementById(isStart ? 'start_time_dt' : 'end_time_dt');
//   if (!dateStr) return;
//   dtField.value = `${dateStr}T${isStart ? '00:00' : '23:59'}`;
//   evaluateRepeatOptions();                    // 日付が変わったら再判定
// }

// /*****************************************************************
//  * 日跨ぎ判定 → ラジオ無効化／「なし」に強制
//  *****************************************************************/
// function evaluateRepeatOptions() {
//   const start = new Date(document.getElementById('start_time_dt').value || '');
//   const end   = new Date(document.getElementById('end_time_dt').value   || '');
//   if (!start || !end || isNaN(start) || isNaN(end)) return;

//   const isCrossDay = start.toDateString() !== end.toDateString();
//   const radios = document.querySelectorAll('.repeat-option');

//   radios.forEach(r => r.disabled = isCrossDay);

//   if (isCrossDay) {
//     // value="0" が「なし」想定
//     const noneRadio = [...radios].find(r => r.value === '0');
//     if (noneRadio) noneRadio.checked = true;
//   }
// }

// /*****************************************************************
//  * 初期化
//  *****************************************************************/
// document.addEventListener('DOMContentLoaded', () => {
//   // 1) 終日UI 初期化
//   toggleAllDayUI();

//   // 2) 終日チェック変化
//   document.getElementById('id_is_all_day')
//           .addEventListener('change', toggleAllDayUI);

//   // 3) date input → datetime-local 同期
//   document.getElementById('start_time_date')
//           .addEventListener('change', e => syncDateOnly(e, true));
//   document.getElementById('end_time_date')
//           .addEventListener('change',  e => syncDateOnly(e, false));

//   // 4) datetime-local 直接編集 → ラジオ再判定
//   document.getElementById('start_time_dt')
//           .addEventListener('change', evaluateRepeatOptions);
//   document.getElementById('end_time_dt')
//           .addEventListener('change',  evaluateRepeatOptions);
// });


/* =========================================================
   終日チェック・日跨ぎ・繰り返し設定 UI 制御スクリプト
   ・終日ON ⇒ 時間入力(hidden) / 日付入力(visible)
   ・日跨ぎ ⇒ 繰り返しは「なし」に強制
   ・新規登録画面ではデフォルトで「なし」を選択
   ========================================================= */

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
        const allDay = isAllDayCheckbox.checked;

        // display を切り替え（disabled にはしない）
        startDateTime.style.display = allDay ? 'none'  : 'block';
        endDateTime.style.display   = allDay ? 'none'  : 'block';
        startDate.style.display     = allDay ? 'block' : 'none';
        endDate.style.display       = allDay ? 'block' : 'none';

        /* 終日 ON のときは 00:00 / 23:59 を自動付与
           - 既に値が入っている場合 slice(0,10) で YYYY-MM-DD へ */
        if (allDay) {
            if (startDateTime.value) startDateTime.value = startDateTime.value.slice(0, 10) + 'T00:00';
            if (endDateTime.value)   endDateTime.value   = endDateTime.value.slice(0, 10) + 'T23:59';
        }

        // 日跨ぎ判定も併せて再評価
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