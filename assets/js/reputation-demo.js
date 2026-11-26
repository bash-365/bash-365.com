/*
 * The reputation demo's walk-through (_includes/reputation-demo.html).
 * Without this script every review and step is on the page; with it the review
 * list becomes tabs (arrow keys, Home and End move between them) and each
 * review's five steps appear one at a time ("Next step", or "Show every step").
 * The steps list is aria-live="polite", so a step that appears is announced.
 * No dependencies, no network, no storage.
 */
(function () {
  'use strict';
  var root = document.querySelector('[data-reputation-demo]');
  if (!root) return;
  var tabs = Array.prototype.slice.call(root.querySelectorAll('[data-demo-tab]'));
  var panels = Array.prototype.slice.call(root.querySelectorAll('[data-demo-panel]'));
  if (!tabs.length || tabs.length !== panels.length) return;
  root.classList.add('is-interactive');

  function steps(panel) {
    return Array.prototype.slice.call(panel.querySelectorAll('[data-demo-step]'));
  }

  function reveal(panel, count) {
    var all = steps(panel);
    var shown = Math.max(1, Math.min(count, all.length));
    all.forEach(function (step, i) { step.hidden = i >= shown; });
    panel.setAttribute('data-shown', String(shown));
    var next = panel.querySelector('[data-demo-next]');
    var every = panel.querySelector('[data-demo-all]');
    var done = shown >= all.length;
    next.disabled = done;
    next.textContent = done ? 'All five steps shown' : 'Next step';
    every.hidden = done;
  }

  function select(index, focus) {
    tabs.forEach(function (tab, i) {
      var on = i === index;
      tab.setAttribute('aria-selected', on ? 'true' : 'false');
      tab.tabIndex = on ? 0 : -1;
      panels[i].hidden = !on;
    });
    var panel = panels[index];
    reveal(panel, Number(panel.getAttribute('data-shown') || 1));
    if (focus) tabs[index].focus();
  }

  panels.forEach(function (panel) {
    var controls = panel.querySelector('[data-demo-controls]');
    controls.hidden = false;
    panel.querySelector('[data-demo-next]').addEventListener('click', function () {
      reveal(panel, Number(panel.getAttribute('data-shown') || 1) + 1);
    });
    panel.querySelector('[data-demo-all]').addEventListener('click', function () {
      reveal(panel, steps(panel).length);
    });
  });

  tabs.forEach(function (tab, i) {
    tab.addEventListener('click', function () { select(i, false); });
    tab.addEventListener('keydown', function (event) {
      var to = null;
      if (event.key === 'ArrowDown' || event.key === 'ArrowRight') to = (i + 1) % tabs.length;
      else if (event.key === 'ArrowUp' || event.key === 'ArrowLeft') to = (i - 1 + tabs.length) % tabs.length;
      else if (event.key === 'Home') to = 0;
      else if (event.key === 'End') to = tabs.length - 1;
      if (to !== null) {
        event.preventDefault();
        select(to, true);
      }
    });
  });

  select(0, false);
})();
