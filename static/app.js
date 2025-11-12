const API_BASE = "/api";

async function fetchJSON(url, options = {}) {
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || "Request failed");
  }

  return response.json();
}

function createOptionRow(questionId, option) {
  const wrapper = document.createElement("div");
  wrapper.className = "option-row";

  const input = document.createElement("input");
  input.type = "radio";
  input.name = questionId;
  input.value = option.value;
  input.id = `${questionId}_${option.value}`;

  const label = document.createElement("label");
  label.htmlFor = input.id;
  label.textContent = `${option.label} (${option.value})`;

  wrapper.appendChild(input);
  wrapper.appendChild(label);
  return wrapper;
}

function createQuestionElement(question) {
  const fieldset = document.createElement("fieldset");
  fieldset.className = "question";

  const legend = document.createElement("legend");
  legend.textContent = question.text;
  fieldset.appendChild(legend);

  question.options.forEach((option) => {
    fieldset.appendChild(createOptionRow(question.id, option));
  });

  if (question.note) {
    const note = document.createElement("p");
    note.className = "note";
    note.textContent = question.note;
    fieldset.appendChild(note);
  }

  return fieldset;
}

function renderQuestionnaire(container, questionnaire, onSubmit) {
  container.innerHTML = "";

  const form = document.createElement("form");
  form.autocomplete = "off";

  questionnaire.questions.forEach((question) => {
    form.appendChild(createQuestionElement(question));
  });

  const buttonRow = document.createElement("div");
  buttonRow.className = "button-row";

  const submitButton = document.createElement("button");
  submitButton.type = "submit";
  submitButton.textContent = "Submit responses";

  buttonRow.appendChild(submitButton);
  form.appendChild(buttonRow);

  const alertBox = document.createElement("div");
  alertBox.className = "alert";
  alertBox.hidden = true;
  form.prepend(alertBox);

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    alertBox.hidden = true;

    const responses = {};
    let missing = [];

    questionnaire.questions.forEach((question) => {
      const selected = form.querySelector(`input[name="${question.id}"]:checked`);
      if (!selected) {
        missing.push(question.text);
        return;
      }
      responses[question.id] = Number(selected.value);
    });

    if (missing.length > 0) {
      alertBox.textContent = `Please answer all questions. Missing: ${missing.join(", ")}`;
      alertBox.classList.add("danger");
      alertBox.hidden = false;
      return;
    }

    submitButton.disabled = true;
    submitButton.textContent = "Submitting…";

    try {
      await onSubmit(responses, form);
    } catch (error) {
      alertBox.textContent = error.message;
      alertBox.classList.add("danger");
      alertBox.hidden = false;
    } finally {
      submitButton.disabled = false;
      submitButton.textContent = "Submit responses";
    }
  });

  container.appendChild(form);
}

function renderResult(container, content) {
  container.innerHTML = "";
  container.appendChild(content);
}

function createResultsCard(title, lines) {
  const card = document.createElement("div");
  card.className = "results-card";

  const heading = document.createElement("h3");
  heading.textContent = title;
  card.appendChild(heading);

  lines.forEach((line) => {
    const paragraph = document.createElement("p");
    paragraph.textContent = line;
    card.appendChild(paragraph);
  });

  return card;
}

class AssessmentFlow {
  constructor() {
    this.questionnaires = {};
    this.state = {
      phq4: null,
      phq9: null,
      gad7: null,
      cssrs: null,
      tier: null,
    };

    this.sections = {
      phq4: document.querySelector("#phq4-section"),
      phq9: document.querySelector("#phq9-section"),
      gad7: document.querySelector("#gad7-section"),
      cssrs: document.querySelector("#cssrs-section"),
      tier: document.querySelector("#tier-section"),
    };

    this.containers = {
      phq4: document.querySelector("#phq4-form"),
      phq9: document.querySelector("#phq9-form"),
      gad7: document.querySelector("#gad7-form"),
      cssrs: document.querySelector("#cssrs-form"),
    };

    this.resultsContainers = {
      phq4: document.querySelector("#phq4-results"),
      phq9: document.querySelector("#phq9-results"),
      gad7: document.querySelector("#gad7-results"),
      cssrs: document.querySelector("#cssrs-results"),
      tier: document.querySelector("#tier-results"),
    };
  }

  async init() {
    await this.loadQuestionnaire("phq4");
    this.renderSection("phq4");
  }

  async loadQuestionnaire(name) {
    if (this.questionnaires[name]) {
      return this.questionnaires[name];
    }
    const questionnaire = await fetchJSON(`${API_BASE}/questionnaires/${name}`);
    this.questionnaires[name] = questionnaire;
    const section = this.sections[name];
    if (section) {
      section.querySelector(".section-description").textContent = questionnaire.description;
    }
    return questionnaire;
  }

  renderSection(name) {
    const questionnaire = this.questionnaires[name];
    const container = this.containers[name];
    if (!questionnaire || !container) return;

    this.sections[name].hidden = false;

    renderQuestionnaire(container, questionnaire, async (responses) => {
      if (name === "phq4") {
        await this.submitPHQ4(responses);
      } else if (name === "phq9") {
        await this.submitPHQ9(responses);
      } else if (name === "gad7") {
        await this.submitGAD7(responses);
      } else if (name === "cssrs") {
        await this.submitCSSRS(responses);
      }
    });
  }

  async submitPHQ4(responses) {
    const result = await fetchJSON(`${API_BASE}/assessments/phq4`, {
      method: "POST",
      body: JSON.stringify({ responses }),
    });

    this.state.phq4 = result;

    const content = document.createElement("div");
    content.className = "results-grid";

    content.appendChild(
      createResultsCard("PHQ-4 Scores", [
        `Total score: ${result.total_score}`,
        `Depression component: ${result.depression_score}`,
        `Anxiety component: ${result.anxiety_score}`,
      ])
    );

    const messageCard = createResultsCard("Next steps", [result.message]);
    content.appendChild(messageCard);

    renderResult(this.resultsContainers.phq4, content);

    if (result.recommend_phq9) {
      await this.loadQuestionnaire("phq9");
      this.renderSection("phq9");
    }

    if (result.recommend_gad7) {
      await this.loadQuestionnaire("gad7");
      this.renderSection("gad7");
    }

    if (!result.recommend_phq9 && !result.recommend_gad7) {
      this.renderTierFromMinimalScreen();
    }
  }

  async submitPHQ9(responses) {
    const result = await fetchJSON(`${API_BASE}/assessments/phq9`, {
      method: "POST",
      body: JSON.stringify({ responses }),
    });

    this.state.phq9 = result;

    const content = document.createElement("div");
    content.className = "results-grid";

    content.appendChild(
      createResultsCard("PHQ-9 Summary", [
        `Total score: ${result.total_score} (${result.severity})`,
        `Item 9 score: ${result.item_9_score}`,
      ])
    );

    const nextStepsCard = createResultsCard("Next steps", [result.message]);
    content.appendChild(nextStepsCard);

    renderResult(this.resultsContainers.phq9, content);

    if (result.recommend_cssrs) {
      await this.loadQuestionnaire("cssrs");
      this.renderSection("cssrs");
    }

    this.updateTierRecommendation();
  }

  async submitGAD7(responses) {
    const result = await fetchJSON(`${API_BASE}/assessments/gad7`, {
      method: "POST",
      body: JSON.stringify({ responses }),
    });

    this.state.gad7 = result;

    const content = document.createElement("div");
    content.className = "results-grid";
    content.appendChild(
      createResultsCard("GAD-7 Summary", [
        `Total score: ${result.total_score} (${result.severity})`,
      ])
    );

    renderResult(this.resultsContainers.gad7, content);

    this.updateTierRecommendation();
  }

  async submitCSSRS(responses) {
    const result = await fetchJSON(`${API_BASE}/assessments/cssrs`, {
      method: "POST",
      body: JSON.stringify({ responses }),
    });

    this.state.cssrs = result;

    const content = document.createElement("div");
    content.className = "results-grid";
    content.appendChild(
      createResultsCard("C-SSRS Risk", [
        `Risk level: ${result.risk_level}`,
        result.description,
      ])
    );

    renderResult(this.resultsContainers.cssrs, content);
  }

  renderTierFromMinimalScreen() {
    const tierSection = this.sections.tier;
    tierSection.hidden = false;

    const container = this.resultsContainers.tier;
    container.innerHTML = "";

    const card = createResultsCard("Summary", [
      "No additional screening required at this time.",
      "Recommend Tier 1: Self-management and monitoring.",
    ]);

    const emphasis = document.createElement("p");
    emphasis.className = "tier-emphasis";
    emphasis.textContent = "Tier 1 · Self-management and monitoring";
    container.appendChild(emphasis);
    container.appendChild(card);
  }

  async updateTierRecommendation() {
    const phq9Total = this.state.phq9?.total_score ?? null;
    const gad7Total = this.state.gad7?.total_score ?? null;

    if (phq9Total === null && gad7Total === null) {
      return;
    }

    const result = await fetchJSON(`${API_BASE}/assessments/tier`, {
      method: "POST",
      body: JSON.stringify({ phq9_total: phq9Total, gad7_total: gad7Total }),
    });

    this.state.tier = result;
    this.renderTier(result);
  }

  renderTier(result) {
    const tierSection = this.sections.tier;
    tierSection.hidden = false;

    const container = this.resultsContainers.tier;
    container.innerHTML = "";

    const tierInfo = document.createElement("p");
    tierInfo.className = "tier-emphasis";
    tierInfo.textContent = `${result.tier.name} · ${result.tier.label}`;

    const description = document.createElement("p");
    description.textContent = result.tier.description;

    const breakdownWrapper = document.createElement("div");
    breakdownWrapper.className = "results-grid";

    Object.entries(result.tool_breakdown).forEach(([tool, data]) => {
      const title = tool.toUpperCase();
      const tierLevel = data.tier;
      breakdownWrapper.appendChild(
        createResultsCard(`${title} contribution`, [
          `Score: ${data.score}`,
          `Tier level: ${tierLevel}`,
        ])
      );
    });

    container.appendChild(tierInfo);
    container.appendChild(description);
    container.appendChild(breakdownWrapper);
  }
}

const app = new AssessmentFlow();
app.init().catch((error) => {
  console.error("Failed to initialise application", error);
});

