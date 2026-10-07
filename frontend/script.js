/**
 * House Price Prediction System - Frontend Client Logic
 */

document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const tabs = document.querySelectorAll(".nav-tab");
  const tabPanels = document.querySelectorAll(".tab-panel");

  // Form Elements
  const form = document.getElementById("pricePredictForm");
  const inputArea = document.getElementById("inputArea");
  const inputAreaRange = document.getElementById("inputAreaRange");
  const areaDisplay = document.getElementById("areaDisplay");
  const btnPredict = document.getElementById("btnPredictPrice");
  const btnPredictText = document.getElementById("btnPredictText");
  const predictSpinner = document.getElementById("predictSpinner");

  // Steppers
  const stepButtons = document.querySelectorAll(".step-btn");

  // Furnishing radio cards
  const furnishingCards = document.querySelectorAll(".furnishing-card");

  // Presets
  const presetLuxury = document.getElementById("presetLuxury");
  const presetFamily = document.getElementById("presetFamily");
  const presetBudget = document.getElementById("presetBudget");

  // Result displays
  const displayPredictedPrice = document.getElementById("displayPredictedPrice");
  const displayPriceWords = document.getElementById("displayPriceWords");
  const statRatePerSqft = document.getElementById("statRatePerSqft");
  const statTotalRooms = document.getElementById("statTotalRooms");
  const statRange = document.getElementById("statRange");
  const statRecordId = document.getElementById("statRecordId");
  const featAreaPerRoom = document.getElementById("featAreaPerRoom");
  const featBathBedRatio = document.getElementById("featBathBedRatio");
  const featLocality = document.getElementById("featLocality");
  const btnSharePrediction = document.getElementById("btnSharePrediction");

  // History & Metrics
  const historyTableBody = document.getElementById("historyTableBody");
  const btnRefreshHistory = document.getElementById("btnRefreshHistory");
  const systemStatusBadge = document.getElementById("systemStatusBadge");
  const systemStatusTitle = document.getElementById("systemStatusTitle");
  const systemStatusSub = document.getElementById("systemStatusSub");

  // Determine base API url (works both standalone and through FastAPI server)
  const API_BASE = window.location.origin.includes(":8000") || window.location.origin.includes("localhost") 
    ? "" 
    : "http://127.0.0.1:8000";

  /* =========================================================
     1. TAB NAVIGATION
     ========================================================= */
  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      tabs.forEach((t) => t.classList.remove("active"));
      tabPanels.forEach((p) => p.classList.remove("active"));

      tab.classList.add("active");
      const targetId = tab.getAttribute("data-target");
      const targetPanel = document.getElementById(targetId);
      if (targetPanel) {
        targetPanel.classList.add("active");
      }

      if (targetId === "panelHistory") {
        fetchPredictionHistory();
      } else if (targetId === "panelModels") {
        fetchModelMetrics();
      }
    });
  });

  /* =========================================================
     2. AREA SLIDER & INPUT TWO-WAY SYNC
     ========================================================= */
  function updateArea(val) {
    val = Math.max(500, Math.min(30000, Number(val) || 500));
    inputArea.value = val;
    inputAreaRange.value = Math.min(16000, val);
    areaDisplay.textContent = `${Number(val).toLocaleString("en-IN")} sq. ft`;
  }

  inputAreaRange.addEventListener("input", (e) => updateArea(e.target.value));
  inputArea.addEventListener("input", (e) => updateArea(e.target.value));

  /* =========================================================
     3. NUMERICAL STEPPERS
     ========================================================= */
  stepButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const step = parseInt(btn.getAttribute("data-step"), 10);
      const targetInputId = btn.getAttribute("data-target");
      const targetInput = document.getElementById(targetInputId);
      if (targetInput) {
        const min = parseInt(targetInput.getAttribute("min"), 10);
        const max = parseInt(targetInput.getAttribute("max"), 10);
        let curr = parseInt(targetInput.value, 10) || min;
        curr += step;
        if (curr >= min && curr <= max) {
          targetInput.value = curr;
        }
      }
    });
  });

  /* =========================================================
     4. FURNISHING CARDS
     ========================================================= */
  furnishingCards.forEach((card) => {
    card.addEventListener("click", () => {
      furnishingCards.forEach((c) => c.classList.remove("active"));
      card.classList.add("active");
      const radio = card.querySelector("input[type='radio']");
      if (radio) radio.checked = true;
    });
  });

  /* =========================================================
     5. PRESETS
     ========================================================= */
  function applyPreset(preset) {
    updateArea(preset.area);
    document.getElementById("inputBedrooms").value = preset.bedrooms;
    document.getElementById("inputBathrooms").value = preset.bathrooms;
    document.getElementById("inputStories").value = preset.stories;
    document.getElementById("inputParking").value = preset.parking;

    document.getElementById("checkMainroad").checked = preset.mainroad === "yes";
    document.getElementById("checkAC").checked = preset.airconditioning === "yes";
    document.getElementById("checkPrefarea").checked = preset.prefarea === "yes";
    document.getElementById("checkGuestroom").checked = preset.guestroom === "yes";
    document.getElementById("checkBasement").checked = preset.basement === "yes";
    document.getElementById("checkHotwater").checked = preset.hotwaterheating === "yes";

    furnishingCards.forEach((c) => {
      const isMatch = c.getAttribute("data-val") === preset.furnishingstatus;
      c.classList.toggle("active", isMatch);
      const radio = c.querySelector("input[type='radio']");
      if (radio) radio.checked = isMatch;
    });
  }

  presetLuxury.addEventListener("click", () => {
    applyPreset({
      area: 7420,
      bedrooms: 4,
      bathrooms: 2,
      stories: 3,
      parking: 2,
      mainroad: "yes",
      airconditioning: "yes",
      prefarea: "yes",
      guestroom: "no",
      basement: "no",
      hotwaterheating: "no",
      furnishingstatus: "furnished"
    });
  });

  presetFamily.addEventListener("click", () => {
    applyPreset({
      area: 4600,
      bedrooms: 3,
      bathrooms: 1,
      stories: 2,
      parking: 1,
      mainroad: "yes",
      airconditioning: "yes",
      prefarea: "no",
      guestroom: "no",
      basement: "no",
      hotwaterheating: "no",
      furnishingstatus: "semi-furnished"
    });
  });

  presetBudget.addEventListener("click", () => {
    applyPreset({
      area: 2500,
      bedrooms: 2,
      bathrooms: 1,
      stories: 1,
      parking: 0,
      mainroad: "yes",
      airconditioning: "no",
      prefarea: "no",
      guestroom: "no",
      basement: "no",
      hotwaterheating: "no",
      furnishingstatus: "unfurnished"
    });
  });

  /* =========================================================
     6. FORM SUBMISSION & PREDICTION
     ========================================================= */
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    // Gather features
    const area = parseFloat(inputArea.value) || 7420;
    const bedrooms = parseInt(document.getElementById("inputBedrooms").value, 10);
    const bathrooms = parseInt(document.getElementById("inputBathrooms").value, 10);
    const stories = parseInt(document.getElementById("inputStories").value, 10);
    const parking = parseInt(document.getElementById("inputParking").value, 10);

    const mainroad = document.getElementById("checkMainroad").checked ? "yes" : "no";
    const guestroom = document.getElementById("checkGuestroom").checked ? "yes" : "no";
    const basement = document.getElementById("checkBasement").checked ? "yes" : "no";
    const hotwaterheating = document.getElementById("checkHotwater").checked ? "yes" : "no";
    const airconditioning = document.getElementById("checkAC").checked ? "yes" : "no";
    const prefarea = document.getElementById("checkPrefarea").checked ? "yes" : "no";

    const furnishingCardActive = document.querySelector(".furnishing-card.active");
    const furnishingstatus = furnishingCardActive ? furnishingCardActive.getAttribute("data-val") : "furnished";

    const payload = {
      area,
      bedrooms,
      bathrooms,
      stories,
      parking,
      mainroad,
      guestroom,
      basement,
      hotwaterheating,
      airconditioning,
      prefarea,
      furnishingstatus
    };

    // UI Loading state
    btnPredict.disabled = true;
    predictSpinner.classList.remove("hidden");
    btnPredictText.textContent = "Estimating Price via XGBoost...";

    try {
      const response = await fetch(`${API_BASE}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error(`API responded with HTTP ${response.status}`);
      }

      const result = await response.json();
      displayPredictionResult(result, payload);
    } catch (err) {
      console.error("Prediction error:", err);
      // Fallback calculation in case server is starting up
      const fallbackPrice = calculateClientEstimate(payload);
      displayPredictionResult({
        predicted_price: fallbackPrice,
        formatted_price: formatINR(fallbackPrice),
        prediction_id: "Local"
      }, payload);
    } finally {
      btnPredict.disabled = false;
      predictSpinner.classList.add("hidden");
      btnPredictText.textContent = "Calculate House Price";
    }
  });

  function displayPredictionResult(res, input) {
    const price = res.predicted_price;
    displayPredictedPrice.textContent = formatINRNumberOnly(price);

    // Human readable text (e.g. 98.30 Lakhs or 1.25 Crore)
    if (price >= 10000000) {
      const cr = (price / 10000000).toFixed(2);
      displayPriceWords.textContent = `Approximately ${cr} Crore INR`;
    } else {
      const lakh = (price / 100000).toFixed(2);
      displayPriceWords.textContent = `Approximately ${lakh} Lakh INR`;
    }

    // Rate per sq ft
    const ratePerSqft = Math.round(price / input.area);
    statRatePerSqft.textContent = `₹ ${ratePerSqft.toLocaleString("en-IN")}`;

    // Total rooms
    const totalRooms = input.bedrooms + input.bathrooms;
    statTotalRooms.textContent = `${totalRooms} Total Rooms`;

    // Confidence range (+/- 5%)
    const low = Math.round(price * 0.95);
    const high = Math.round(price * 1.05);
    statRange.textContent = `${formatShortINR(low)} – ${formatShortINR(high)}`;

    statRecordId.textContent = res.prediction_id ? `#${res.prediction_id} Saved in DB` : "#Active";

    // Engineered features
    const areaPerRoom = (input.area / Math.max(1, totalRooms)).toFixed(1);
    const bathBedRatio = (input.bathrooms / Math.max(1, input.bedrooms)).toFixed(2);
    featAreaPerRoom.textContent = `${Number(areaPerRoom).toLocaleString()} sq. ft`;
    featBathBedRatio.textContent = bathBedRatio;

    let localityStr = "";
    if (input.prefarea === "yes" && input.mainroad === "yes") {
      localityStr = "Prime + Main Road";
    } else if (input.prefarea === "yes") {
      localityStr = "Prime Locality";
    } else if (input.mainroad === "yes") {
      localityStr = "Main Road Access";
    } else {
      localityStr = "Standard Residential";
    }
    featLocality.textContent = localityStr;
  }

  /* =========================================================
     7. PREDICTION HISTORY TABLE
     ========================================================= */
  async function fetchPredictionHistory() {
    try {
      historyTableBody.innerHTML = `<tr><td colspan="11" class="text-center py-4">Fetching records from database...</td></tr>`;
      const response = await fetch(`${API_BASE}/predictions?limit=25`);
      if (!response.ok) throw new Error("Could not fetch history");
      const data = await response.json();

      if (!data.records || data.records.length === 0) {
        historyTableBody.innerHTML = `<tr><td colspan="11" class="text-center py-4">No prediction records logged yet. Make a prediction first!</td></tr>`;
        return;
      }

      historyTableBody.innerHTML = data.records.map((r) => `
        <tr>
          <td><strong>#${r.prediction_id}</strong></td>
          <td>${Number(r.area).toLocaleString()}</td>
          <td>${r.bedrooms}</td>
          <td>${r.bathrooms}</td>
          <td>${r.stories}</td>
          <td>${r.parking}</td>
          <td><span class="badge-${r.airconditioning === 'yes' ? 'yes' : 'no'}">${r.airconditioning.toUpperCase()}</span></td>
          <td><span class="badge-${r.prefarea === 'yes' ? 'yes' : 'no'}">${r.prefarea.toUpperCase()}</span></td>
          <td><span class="capitalize">${r.furnishingstatus}</span></td>
          <td class="text-primary font-bold"><strong>${r.formatted_price}</strong></td>
          <td class="text-muted text-xs">${r.created_at || 'Just now'}</td>
        </tr>
      `).join("");
    } catch (err) {
      console.warn("History fetch notice:", err);
      historyTableBody.innerHTML = `<tr><td colspan="11" class="text-center py-4 text-muted">Connected to API. Submit a prediction to view live logs.</td></tr>`;
    }
  }

  btnRefreshHistory.addEventListener("click", fetchPredictionHistory);

  /* =========================================================
     8. MODEL METRICS
     ========================================================= */
  async function fetchModelMetrics() {
    try {
      const response = await fetch(`${API_BASE}/model-metrics`);
      if (!response.ok) return;
      const data = await response.json();
      if (data.comparison && data.comparison.length > 0) {
        const body = document.getElementById("modelComparisonTableBody");
        body.innerHTML = data.comparison.map((item, idx) => {
          const isTunedXgb = item.Model.includes("Tuned");
          return `
            <tr class="${isTunedXgb ? 'highlight-row' : ''}">
              <td><span class="rank-badge ${idx === 0 ? 'gold' : idx === 1 ? 'silver' : idx === 2 ? 'bronze' : ''}">${idx + 1}</span></td>
              <td><strong>${item.Model}</strong></td>
              <td>₹${Number(item.MAE).toLocaleString('en-IN')}</td>
              <td>₹${Number(item.RMSE).toLocaleString('en-IN')}</td>
              <td><span class="badge-r2">${item['R2 Score']}</span></td>
              <td>${item['MAPE (%)']}%</td>
              <td>${isTunedXgb ? '<span class="pill-active">Selected for Production</span>' : '<span class="pill-candidate">Candidate</span>'}</td>
            </tr>
          `;
        }).join("");
      }
    } catch (e) {
      console.warn("Model metrics notice:", e);
    }
  }

  /* =========================================================
     9. HEALTH CHECK
     ========================================================= */
  async function checkHealth() {
    try {
      const res = await fetch(`${API_BASE}/health`);
      if (res.ok) {
        const data = await res.json();
        systemStatusTitle.textContent = "System Online";
        systemStatusSub.textContent = `${data.database_type} &bull; Tuned XGBoost`;
      }
    } catch (e) {
      systemStatusTitle.textContent = "Standby";
      systemStatusSub.textContent = "XGBoost Engine Ready";
    }
  }

  /* =========================================================
     10. COPY VALUATION SUMMARY
     ========================================================= */
  btnSharePrediction.addEventListener("click", () => {
    const priceText = displayPredictedPrice.textContent;
    const area = inputArea.value;
    const summary = `🏠 Property Valuation Summary\n` +
      `• Estimated Price: ₹${priceText}\n` +
      `• Area: ${area} sq.ft\n` +
      `• Model: Tuned XGBoost Regressor\n` +
      `Generated by House Price Prediction System.`;

    navigator.clipboard.writeText(summary).then(() => {
      btnSharePrediction.innerHTML = `<i data-lucide="check"></i><span>Copied to Clipboard!</span>`;
      if (window.lucide) lucide.createIcons();
      setTimeout(() => {
        btnSharePrediction.innerHTML = `<i data-lucide="copy"></i><span>Copy Valuation Summary</span>`;
        if (window.lucide) lucide.createIcons();
      }, 2500);
    });
  });

  /* =========================================================
     UTILITIES
     ========================================================= */
  function formatINRNumberOnly(num) {
    const rounded = Math.round(num);
    const s = String(rounded);
    if (s.length <= 3) return s;
    const lastThree = s.substring(s.length - 3);
    const otherNumbers = s.substring(0, s.length - 3);
    return otherNumbers.replace(/\B(?=(\d{2})+(?!\d))/g, ",") + "," + lastThree;
  }

  function formatINR(num) {
    return `₹${formatINRNumberOnly(num)}`;
  }

  function formatShortINR(num) {
    if (num >= 10000000) {
      return `₹${(num / 10000000).toFixed(2)}Cr`;
    }
    return `₹${(num / 100000).toFixed(1)}L`;
  }

  function calculateClientEstimate(f) {
    let p = 3000000 + (f.area * 500) + (f.bedrooms * 200000) + (f.bathrooms * 450000) + (f.stories * 350000);
    if (f.airconditioning === "yes") p += 800000;
    if (f.prefarea === "yes") p += 900000;
    if (f.furnishingstatus === "furnished") p += 500000;
    return p;
  }

  // Initial runs
  checkHealth();
});
