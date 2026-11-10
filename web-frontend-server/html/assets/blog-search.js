(() => {
  "use strict";

  const form = document.getElementById("blog-tools");
  if (!form) return;

  const search = document.getElementById("blog-search");
  const category = document.getElementById("blog-category");
  const status = document.getElementById("blog-results-count");
  const empty = document.getElementById("blog-empty");
  const clearEmpty = document.getElementById("clear-empty-filters");
  const normalize = (value) => value.trim().toLocaleLowerCase("vi")
    .normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/đ/g, "d")
    .replace(/\s+/g, " ");
  const entries = Array.from(document.querySelectorAll(".blog-entry"), (element) => ({
    element,
    title: normalize(element.querySelector("h2").textContent),
    category: element.dataset.category,
  }));

  function filterPosts() {
    const query = normalize(search.value);
    let count = 0;
    for (const entry of entries) {
      const matches = entry.title.includes(query)
        && (category.value === "all" || entry.category === category.value);
      entry.element.hidden = !matches;
      if (matches) count += 1;
    }
    status.textContent = `Hiển thị ${count} trong ${entries.length} bài viết`;
    empty.hidden = count !== 0;
  }

  function resetFilters() {
    search.value = "";
    category.value = "all";
    filterPosts();
    search.focus();
  }

  form.addEventListener("submit", (event) => event.preventDefault());
  form.addEventListener("reset", (event) => {
    event.preventDefault();
    resetFilters();
  });
  search.addEventListener("input", filterPosts);
  category.addEventListener("change", filterPosts);
  clearEmpty.addEventListener("click", resetFilters);
  form.hidden = false;
  status.hidden = false;
  filterPosts();
})();
