document.addEventListener('DOMContentLoaded', function () {
    const isAllDayCheckbox = document.getElementById('id_is_all_day');
    const startTimeInput = document.getElementById('id_start_time');
    const endTimeInput = document.getElementById('id_end_time');

    function toggleTimeInputs() {
      const isChecked = isAllDayCheckbox.checked;
      startTimeInput.disabled = isChecked;
      endTimeInput.disabled = isChecked;
    }

    if (isAllDayCheckbox && startTimeInput && endTimeInput) {
        // 初期状態もチェックして制御
      toggleTimeInputs();
  
      // チェック切り替え時に制御
      isAllDayCheckbox.addEventListener('change', toggleTimeInputs);
    }

    // 日付が異なる場合、繰り返しラジオを無効化
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    const repeatRadios = document.querySelectorAll('input[name="repeat"]');

    function toggleRepeatOptions(){
        const startDate = new Date(startDateInput.value);
        const endDate = new Date(endDateInput.value);

        const isCrossDay = startDate.toDateString.toDateString() !==endDate.toDateString();

        repeatRadios.forEach(radio => {
            radio.disabled = isCrossDay;
            if (isCrossDay) {
                radio.checked = false;
            }
        });
            
    }   
    
    toggleRepeatOptions();
    startDateInput.addEventListener('change', toggleRepeatOptions);
    endDateInput.addEventListener('change', toggleRepeatOptions);
});

