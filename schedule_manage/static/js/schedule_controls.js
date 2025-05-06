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
});