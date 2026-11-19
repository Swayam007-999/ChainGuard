document.addEventListener("DOMContentLoaded", () => {
  const backendUrlInput = document.getElementById("backendUrl");
  const extensionKeyInput = document.getElementById("extensionKey");
  const fingerprintKeyInput = document.getElementById("fingerprintKey");
  const saveBtn = document.getElementById("saveBtn");
  const statusDiv = document.getElementById("status");

  // Load existing options
  chrome.storage.local.get(
    {
      backendUrl: "http://127.0.0.1:8000/v1",
      extensionKey: "cg_live_sample_fake_key_00000000000000000000000000000000",
      fingerprintKey: "fake_fingerprint_hmac_secret_key_1234567890abcdef",
    },
    (items) => {
      backendUrlInput.value = items.backendUrl;
      extensionKeyInput.value = items.extensionKey;
      fingerprintKeyInput.value = items.fingerprintKey;
    }
  );

  // Save options
  saveBtn.addEventListener("click", () => {
    chrome.storage.local.set(
      {
        backendUrl: backendUrlInput.value.trim(),
        extensionKey: extensionKeyInput.value.trim(),
        fingerprintKey: fingerprintKeyInput.value.trim(),
      },
      () => {
        statusDiv.textContent = "Settings saved successfully!";
        setTimeout(() => {
          statusDiv.textContent = "";
        }, 2500);
      }
    );
  });
});
