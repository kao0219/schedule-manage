/* ------------ メモ編集モーダル：送信処理 ------------ */
document.addEventListener('DOMContentLoaded', () => {

  // 編集フォーム（.edit-memo-form）がページ内に複数あっても OK
  document.querySelectorAll('.edit-memo-form').forEach(form => {

    form.addEventListener('submit', e => {
      e.preventDefault();                         // 既定送信を止める

      /* --- 多重クリック防止 --- */
      const submitBtn = form.querySelector('.memo-edit-submit-btn');
      if (submitBtn) submitBtn.disabled = true;

      /* --- fetch で非同期送信 --- */
      const url       = form.getAttribute('action');
      const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;
      const formData  = new FormData(form);

      fetch(url, {
        method : 'POST',
        headers: { 'X-CSRFToken': csrfToken },
        body   : formData,
      })
      .then(res => {
        if (!res.ok) {         // ステータス 200 以外ならエラー扱い
          throw new Error('保存に失敗しました');
        }
        return res.text();     // 必要なら JSON に変換する
      })
      .then(() => {
        /* --- 成功時 --- */
        const modalEl = form.closest('.modal');
        const modal   = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();

        // Backdrop を除去
        document.querySelectorAll('.modal-backdrop')
                .forEach(el => el.remove());

        // 一覧を更新
        window.location.reload();
      })
      .catch(err => {
        console.error(err);    // 必要ならトースト表示などに置き換え
        if (submitBtn) submitBtn.disabled = false; // 失敗時は再度有効化
      });
    });

  });
});

/* ------------ 画像選択時：ファイル名表示 ------------ */
function handleFileSelect(input, memoId) {
  const filename = input.files.length > 0
    ? input.files[0].name
    : 'ファイル未選択';
  document.getElementById(`filename-display-${memoId}`).textContent = filename;
}