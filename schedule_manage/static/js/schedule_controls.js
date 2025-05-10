document.addEventListener('DOMContentLoaded', function () {
    alert("JSファイルは正しく読み込まれています！");
    const isAllDayCheckbox = document.getElementById('id_is_all_day');
    const startTimeInput = document.getElementById('id_start_time');
    const endTimeInput = document.getElementById('id_end_time');
    const repeatOptions = document.querySelectorAll('.repeat-option');
    

    if (!isAllDayCheckbox || !startTimeInput || !endTimeInput || !repeatOptions.length) return;

    // 終日チェックで時間入力を制御
    function toggleTimeInputs() {
      const isChecked = isAllDayCheckbox.checked;
      startTimeInput.disabled = isChecked;
      endTimeInput.disabled = isChecked;
    }
    
    function toggleDateTimeFields() {
        const isAllDay = document.getElementById('id_is_all_day').checked;
        const startTime = document.getElementById('id_start_time');
        const endTime = document.getElementById('id_end_time');
    
        startTime.disabled = isAllDay;
        endTime.disabled = isAllDay;
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
    } 

    // 初期状態チェック
    toggleTimeInputs();
    toggleRepeatOptions();

    // イベントリスナー登録
    isAllDayCheckbox.addEventListener('change', () => {
        toggleTimeInputs();
        toggleRepeatOptions();
    });

    startTimeInput.addEventListener('change', toggleRepeatOptions);
    endTimeInput.addEventListener('change', toggleRepeatOptions);
});

