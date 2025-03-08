// Airtasker Bot Manager - Client-side Scripts

document.addEventListener("DOMContentLoaded", function () {
  // Auto-dismiss alerts after 5 seconds
  setTimeout(function () {
    const alerts = document.querySelectorAll(".alert-dismissible");
    alerts.forEach(function (alert) {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    });
  }, 5000);

  // Confirm before starting bot
  const botForm = document.querySelector('form[action*="start_bot"]');
  if (botForm) {
    botForm.addEventListener("submit", function (e) {
      if (
        !confirm("Are you sure you want to start the bot with these settings?")
      ) {
        e.preventDefault();
        return false;
      }
    });
  }

  // Initialize tooltips
  const tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]')
  );
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // Preview image uploads
  const imageInputs = document.querySelectorAll('input[type="file"]');
  imageInputs.forEach(function (input) {
    input.addEventListener("change", function (e) {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
          const previewId = input.id + "-preview";
          let previewElement = document.getElementById(previewId);

          if (!previewElement) {
            previewElement = document.createElement("div");
            previewElement.id = previewId;
            previewElement.className = "mt-3";
            input.parentNode.appendChild(previewElement);
          }

          previewElement.innerHTML = `
                        <div class="card">
                            <div class="card-header bg-light">Image Preview</div>
                            <div class="card-body text-center">
                                <img src="${e.target.result}" class="img-fluid message-image-preview" alt="Preview">
                            </div>
                        </div>
                    `;
        };
        reader.readAsDataURL(file);
      }
    });
  });

  // Dynamically update form elements based on settings
  const enableRandomDelaysCheckbox = document.getElementById(
    "enable_random_delays"
  );
  if (enableRandomDelaysCheckbox) {
    const timeoutInput = document.getElementById("timeout_between_actions");

    // Add a note about random delays
    const updateTimeoutHelp = function () {
      const helpText = timeoutInput.parentNode.querySelector(".form-text");
      if (enableRandomDelaysCheckbox.checked) {
        helpText.textContent =
          "Base wait time. Actual delay will be randomized.";
      } else {
        helpText.textContent = "Wait time between actions (in seconds)";
      }
    };

    enableRandomDelaysCheckbox.addEventListener("change", updateTimeoutHelp);
    // Run once on page load
    updateTimeoutHelp();
  }

  // Show current time in dashboard
  const updateClock = function () {
    const clockElement = document.getElementById("current-time");
    if (clockElement) {
      const now = new Date();
      clockElement.textContent = now.toLocaleString();
    }
  };

  // Update clock every second if element exists
  if (document.getElementById("current-time")) {
    setInterval(updateClock, 1000);
    updateClock(); // Run immediately
  }
});
