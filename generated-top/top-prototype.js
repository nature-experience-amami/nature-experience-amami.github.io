(function () {
  const root = document.querySelector("[data-top-mode]");
  const mode = root.dataset.topMode;
  const status = document.getElementById("gallery-status");
  const gallery = document.getElementById("gallery");
  const categoryGrid = document.getElementById("category-grid");
  const generated = new Set(["hebi/habu", "hebi/akamata", "kaeru/amami-aka-gaeru"]);
  let timer;

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, char => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    }[char]));
  }

  function pageHref(creature) {
    const key = `${creature.category}/${creature.id}`;
    return generated.has(key) ? `../generated-creatures/${key}.html` : "";
  }

  function addPreviewCreatures(creatures) {
    const preview = {
      id: "amami-aka-gaeru",
      name: "アマミアカガエル",
      category: "kaeru",
      category_name: "カエル",
      photos: []
    };
    return creatures.some(creature => creature.id === preview.id)
      ? creatures
      : [...creatures, preview];
  }

  function shuffled(items) {
    return [...items].sort(() => Math.random() - 0.5);
  }

  function photoItems(creatures) {
    return creatures.filter(creature => creature.photos && creature.photos.length);
  }

  function renderLink(creature, content) {
    const href = pageHref(creature);
    return href ? `<a href="${href}">${content}</a>` : content;
  }

  function cardHtml(creature) {
    const image = creature.photos && creature.photos.length
      ? `<img src="../${shuffled(creature.photos)[0]}" alt="${escapeHtml(creature.name)}">`
      : `<div class="placeholder">写真準備中</div>`;
    return renderLink(creature,
      `${image}<div class="gallery-caption"><span>${escapeHtml(creature.category_name)}</span><strong>${escapeHtml(creature.name)}</strong></div>`);
  }

  function renderCategories(creatures) {
    const categories = new Map();
    creatures.forEach(creature => {
      if (!categories.has(creature.category)) {
        categories.set(creature.category, { name: creature.category_name, count: 0 });
      }
      categories.get(creature.category).count += 1;
    });
    categoryGrid.innerHTML = [...categories].sort((a, b) => a[0].localeCompare(b[0])).map(([id, category]) => {
      const href = id === "hebi" ? "../hebi.html" : "";
      const content = `<strong>${escapeHtml(category.name)}</strong><span>${category.count}種類${href ? "・一覧を見る →" : "・一覧準備中"}</span>`;
      return href ? `<a class="category-card" href="${href}">${content}</a>` : `<div class="category-card category-card-disabled">${content}</div>`;
    }).join("");
  }

  function renderA(creatures) {
    const items = photoItems(creatures);
    gallery.className = "gallery";
    gallery.innerHTML = `<div class="gallery-items">${items.map((creature, index) => `<div class="gallery-item${index === 0 ? " active" : ""}">${cardHtml(creature)}</div>`).join("")}</div>`;
    let index = 0;
    timer = setInterval(() => {
      const slides = gallery.querySelectorAll(".gallery-item");
      if (!slides.length) return;
      slides[index].classList.remove("active");
      index = (index + 1) % slides.length;
      slides[index].classList.add("active");
    }, 8000);
    status.textContent = "写真を8秒ごとに切り替えています。クリックできる写真は試作ページへ移動します。";
  }

  function renderB(creatures) {
    const items = creatures.filter(creature => creature.photos && creature.photos.length || creature.id === "amami-aka-gaeru");
    gallery.className = "gallery-card-grid";
    function showBatch() {
      const byCategory = new Map();
      shuffled(items).forEach(creature => {
        if (!byCategory.has(creature.category)) byCategory.set(creature.category, []);
        byCategory.get(creature.category).push(creature);
      });
      const categories = shuffled([...byCategory.keys()]);
      const batch = [];
      categories.forEach(category => {
        if (batch.length < 4) batch.push(byCategory.get(category)[0]);
      });
      if (batch.length < 4 && categories.length >= 4) {
        shuffled(items).forEach(creature => {
          if (batch.length >= 4) return;
          if (!batch.some(selected => selected.id === creature.id)) batch.push(creature);
        });
      }
      gallery.innerHTML = batch.map(creature => `<div class="gallery-card active">${cardHtml(creature)}</div>`).join("");
      const categoryCount = new Set(batch.map(creature => creature.category)).size;
      status.textContent = `異なるカテゴリー${categoryCount}種類・生き物${batch.length}種類を表示中。同じ画面内で同じ生き物は重複しません。`;
    }
    showBatch();
    timer = setInterval(showBatch, 8000);
  }

  fetch("../data/creatures.json")
    .then(response => {
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.json();
    })
    .then(creatures => {
      creatures = addPreviewCreatures(creatures);
      renderCategories(creatures);
      if (mode === "a") renderA(creatures);
      else renderB(creatures);
    })
    .catch(error => {
      console.error("creatures.json の読み込みに失敗しました:", error);
      status.textContent = "生き物データを読み込めませんでした。";
    });
})();
