document.addEventListener('DOMContentLoaded', function () {
    const isAllDayCheckbox = document.getElementById('id_is_all_day');
    const startTimeInput = document.getElementById('id_start_time');
    const endTimeInput = document.getElementById('id_end_time');
    
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
    }

    function toggleRepeatOptions(){
        const startVal = startDateInput.value;
        const endVal = endDateInput.value;

        const isCrossDay = startDate.toDateString() !==endDate.toDateString();

        repeatRadios.forEach(radio => {
            radio.disabled = isCrossDay;
            if (isCrossDay) radio.checked = false;   
        });  
    }   
    
    toggleRepeatOptions();
    startDateInput.addEventListener('change', toggleRepeatOptions);
    endDateInput.addEventListener('change', toggleRepeatOptions);
});

