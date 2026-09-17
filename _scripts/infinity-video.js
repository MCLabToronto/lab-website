// Keep the recorded animation optional and respect reduced-motion preferences.
document.addEventListener("DOMContentLoaded", () => {
  const video = document.querySelector(".lab-infinity-video");
  const toggle = document.getElementById("pause-infinity");
  if (!video || !toggle) return;
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  video.muted = true;
  function updatePlayback() {
    if (toggle.checked || reducedMotion.matches || document.hidden) {
      video.pause();
      return;
    }
    const playing = video.play();
    if (playing) playing.catch(() => { toggle.checked = true; });
  }
  toggle.addEventListener("change", updatePlayback);
  reducedMotion.addEventListener("change", updatePlayback);
  document.addEventListener("visibilitychange", updatePlayback);
  updatePlayback();
});
