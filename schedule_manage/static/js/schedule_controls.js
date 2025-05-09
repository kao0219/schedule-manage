document.addEventListener('DOMContentLoaded', function () {
    const isAllDayCheckbox = document.getElementById('id_is_all_day');
    const startTimeInput = document.getElementById('id_start_time');
    const endTimeInput = document.getElementById('id_end_time');
    const repeatOptions = document.querySelectorAll('.repeat-option');
    

    if (!isAllDayCheckbox || !startTimeInput || !endTimeInput || !repeatOptions.length || !mainElement) return;

    const isEdit = mainElement?.dataset?.isEdit === 'true';

    // 新規登録の場合、繰り返し「なし」をデフォルト
    function setDefaultRepeatOption() {
      if (!isEdit) {
        repeatOptions.forEach(option => {
            if (option.value === "0") {
              option.checked = true;
            }
        });
      }
    }
        
    
    // 終日チェックで時間入力を制御
    function toggleTimeInputs() {
      const isChecked = isAllDayCheckbox.checked;
      startTimeInput.disabled = isChecked;
      endTimeInput.disabled = isChecked;
    }

    // 日付を跨いでいたら繰り返し設定を無効化
    function toggleRepeatOptions() {
        const startDateStr = startTimeInput.value;
        const endDateStr = endTimeInput.value;

        if (!startDateStr || !endDateStr) return;

        const startDate = new Date(startDateStr);
        const endDate = new Date(endDateStr);
        const isDifferentDay = startDate.toDateString() !== endDate.toDateString();

        repeatOptions.forEach(option => {
            option.disabled = isDifferentDay;
        });
        
        // 日にち跨ぎの場合は「なし」に強制リセット
        if (isDifferentDay) {
            repeatOptions.forEach(option => {
                if (option.value === "0") {
                    option.checked = true;
                }
            });
        }
    } 

    // 初期状態チェック
    toggleTimeInputs();
    toggleRepeatOptions();
    setDefaultRepeatOption();

    // イベントリスナー登録
    isAllDayCheckbox.addEventListener('change', () => {
        toggleTimeInputs();
        toggleRepeatOptions();
    });

    startTimeInput.addEventListener('change', toggleRepeatOptions);
    endTimeInput.addEventListener('change', toggleRepeatOptions);
});
