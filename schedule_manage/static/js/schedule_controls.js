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

  
function toggleAllDayUI() {
  const allDay = document.getElementById('id_is_all_day').checked;

  const sDt  = document.getElementById('start_time_dt');
  const eDt  = document.getElementById('end_time_dt');
  const sDat = document.getElementById('start_time_date');
  const eDat = document.getElementById('end_time_date');

  if (allDay) {
    // 表示切替
    sDt.style.display = eDt.style.display = 'none';
    sDat.style.display = eDat.style.display = 'inline-block';

    // date input に初期値をコピー
    if (sDt.value) sDat.value = sDt.value.slice(0, 10);
    if (eDt.value) eDat.value = eDt.value.slice(0, 10);
  } else {
    sDt.style.display = eDt.style.display = 'inline-block';
    sDat.style.display = eDat.style.display = 'none';
  }

  evaluateRepeatOptions();   // 終日ON/OFF してもラジオ再判定
}

/*****************************************************************
 * date input を編集したら datetime-local に反映
 *****************************************************************/
function syncDateOnly(e, isStart) {
  const dateStr = e.target.value;             // YYYY-MM-DD
  const dtField = document.getElementById(isStart ? 'start_time_dt' : 'end_time_dt');
  if (!dateStr) return;
  dtField.value = `${dateStr}T${isStart ? '00:00' : '23:59'}`;
  evaluateRepeatOptions();                    // 日付が変わったら再判定
}

/*****************************************************************
 * 日跨ぎ判定 → ラジオ無効化／「なし」に強制
 *****************************************************************/
function evaluateRepeatOptions() {
  const start = new Date(document.getElementById('start_time_dt').value || '');
  const end   = new Date(document.getElementById('end_time_dt').value   || '');
  if (!start || !end || isNaN(start) || isNaN(end)) return;

  const isCrossDay = start.toDateString() !== end.toDateString();
  const radios = document.querySelectorAll('.repeat-option');

  radios.forEach(r => r.disabled = isCrossDay);

  if (isCrossDay) {
    // value="0" が「なし」想定
    const noneRadio = [...radios].find(r => r.value === '0');
    if (noneRadio) noneRadio.checked = true;
  }
}

/*****************************************************************
 * 初期化
 *****************************************************************/
document.addEventListener('DOMContentLoaded', () => {
  // 1) 終日UI 初期化
  toggleAllDayUI();

  // 2) 終日チェック変化
  document.getElementById('id_is_all_day')
          .addEventListener('change', toggleAllDayUI);

  // 3) date input → datetime-local 同期
  document.getElementById('start_time_date')
          .addEventListener('change', e => syncDateOnly(e, true));
  document.getElementById('end_time_date')
          .addEventListener('change',  e => syncDateOnly(e, false));

  // 4) datetime-local 直接編集 → ラジオ再判定
  document.getElementById('start_time_dt')
          .addEventListener('change', evaluateRepeatOptions);
  document.getElementById('end_time_dt')
          .addEventListener('change',  evaluateRepeatOptions);
});