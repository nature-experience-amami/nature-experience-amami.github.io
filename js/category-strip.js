/*
  カテゴリー帯(横スクロールのカテゴリーナビ)共通の挙動。
  - 開いた瞬間、現在地カテゴリーが見やすい位置になるよう自動スクロール
  - 帯の中身が画面幅からはみ出している時だけ、右端にフェードと矢印を表示
  - 矢印タップで少し右へスクロール
  カテゴリー一覧ページ・図鑑ページから共通で読み込む。
*/
(function () {
  document.querySelectorAll(".cat-strip-wrap").forEach(function (wrap) {
    var strip = wrap.querySelector(".cat-strip");
    var fade = wrap.querySelector(".fade-right");
    var hint = wrap.querySelector(".scroll-hint");
    if (!strip) return;

    function updateHint() {
      var overflowing = strip.scrollWidth > strip.clientWidth + 4;
      var nearEnd = strip.scrollLeft + strip.clientWidth >= strip.scrollWidth - 4;
      var show = overflowing && !nearEnd;
      if (fade) fade.classList.toggle("show", show);
      if (hint) hint.classList.toggle("show", show);
    }

    function scrollCurrentIntoView() {
      var current = strip.querySelector(".cat-item.current");
      if (!current) return;
      var offset = current.offsetLeft - (strip.clientWidth / 2) + (current.clientWidth / 2);
      strip.scrollTo({ left: Math.max(offset, 0), behavior: "smooth" });
    }

    scrollCurrentIntoView();
    updateHint();
    setTimeout(updateHint, 400);

    strip.addEventListener("scroll", updateHint);
    window.addEventListener("resize", updateHint);
    if (hint) {
      hint.addEventListener("click", function () {
        strip.scrollBy({ left: strip.clientWidth * 0.7, behavior: "smooth" });
      });
    }
  });
})();
