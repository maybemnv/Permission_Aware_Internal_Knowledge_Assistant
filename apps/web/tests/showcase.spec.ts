import { expect, test } from "@playwright/test";

const canonicalQuestion = "What is the travel reimbursement policy for my region and role?";

async function selectPrincipal(page: import("@playwright/test").Page, principal: string) {
  const switched = page.waitForResponse((response) => response.url().includes("/api/demo-principal") && response.request().method() === "POST");
  await page.getByLabel("Fixture principal").selectOption(principal);
  await switched;
  const search = page.getByRole("button", { name: "Search evidence" });
  if (await search.count()) await expect(search).toBeEnabled();
}

test("allowed principal can search, answer, and preview authorized fixture evidence", async ({ page }) => {
  await page.goto("/");
  await selectPrincipal(page, "allowed-user");
  await page.getByLabel("Ask a question").fill(canonicalQuestion);
  await page.getByRole("button", { name: "Search evidence" }).click();

  await expect(page.getByRole("heading", { name: "Permitted evidence for your question" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Travel reimbursement policy", exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Generate cited answer" }).click();
  await expect(page.getByText("Supporting citations")).toBeVisible();
  await page.getByRole("button", { name: /Travel reimbursement policy/ }).click();
  await expect(page.getByRole("heading", { name: "Verify the evidence" })).toBeVisible();
});

test("denied and cross-tenant principals cannot see restricted primary-tenant evidence", async ({ page }) => {
  await page.goto("/");
  await selectPrincipal(page, "denied-user");
  await page.getByLabel("Ask a question").fill("Show details of the restricted project");
  await page.getByRole("button", { name: "Search evidence" }).click();
  await expect(page.getByText("No accessible context is available for this request.")).toBeVisible();

  await page.goto("/");
  await selectPrincipal(page, "cross-tenant-user");
  await page.getByLabel("Ask a question").fill("Show details of the restricted project");
  await page.getByRole("button", { name: "Search evidence" }).click();
  await expect(page.getByRole("heading", { name: "Other tenant project notes" })).toBeVisible();
  await expect(page.getByText(/restricted project launch notes/i)).toHaveCount(0);
  await expect(page.getByText(/github:\/\/internal/i)).toHaveCount(0);
});

test("admin sees live fixture API administration surfaces", async ({ page }) => {
  const unansweredQuestion = "Which stationery supplies are reimbursable?";
  await page.goto("/");
  await selectPrincipal(page, "allowed-user");
  await page.getByLabel("Ask a question").fill(unansweredQuestion);
  await page.getByRole("button", { name: "Search evidence" }).click();
  await page.getByRole("button", { name: "Generate safe answer" }).click();
  await expect(page.getByText("There is not enough authorized evidence to answer this question.")).toBeVisible();

  await page.goto("/admin");
  await selectPrincipal(page, "admin-user");
  await page.getByRole("button", { name: "Refresh connector status" }).click();
  await expect(page.getByRole("heading", { name: "Eight source boundaries" })).toBeVisible();
  await expect(page.locator(".connector-card")).toHaveCount(8);
  await page.getByRole("button", { name: "Start fixture sync" }).first().click();
  await expect(page.getByText(/completed|failed/i).first()).toBeVisible();
  await page.getByRole("tab", { name: "Unanswered" }).click();
  await expect(page.getByRole("heading", { name: "Where evidence is thin" })).toBeVisible();
  await expect(page.getByText("no_result").first()).toBeVisible();
  await expect(page.getByText(/[a-f0-9]{12}/).first()).toBeVisible();
  await expect(page.getByText(unansweredQuestion)).toHaveCount(0);
  await page.getByRole("tab", { name: "Evaluation" }).click();
  await page.getByRole("button", { name: "Run fixture evaluation" }).click();
  await expect(page.getByText("Permission leakage")).toBeVisible();
  await page.getByRole("tab", { name: "Audit" }).click();
  await expect(page.getByRole("heading", { name: "What the system recorded" })).toBeVisible();
});

test("primary controls are keyboard reachable and mobile layout does not overflow", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await page.keyboard.press("Tab");
  await expect(page.locator(":focus-visible")).toHaveCount(1);
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
  expect(overflow).toBeFalsy();
});

test("principal switches discard delayed search responses", async ({ page }) => {
  await page.route("**/api/backend/v1/search", async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 250));
    await route.continue();
  });
  await page.goto("/");
  await page.getByLabel("Ask a question").fill(canonicalQuestion);
  await page.getByRole("button", { name: "Search evidence" }).click();
  await page.getByLabel("Fixture principal").selectOption("denied-user");
  await expect(page.getByText("No accessible context is available for this request.")).toHaveCount(0);
  await page.waitForTimeout(400);
  await expect(page.getByText("Travel reimbursement policy", { exact: true })).toHaveCount(0);
});

test("principal switching disables data actions and blocks old authorized results", async ({ page }) => {
  let releasePrincipal!: () => void;
  const principalPending = new Promise<void>((resolve) => { releasePrincipal = resolve; });
  let releaseSearch!: () => void;
  const searchPending = new Promise<void>((resolve) => { releaseSearch = resolve; });
  const backendRequests: string[] = [];
  page.on("request", (request) => {
    if (request.url().includes("/api/backend/")) backendRequests.push(request.url());
  });
  await page.route("**/api/demo-principal", async (route) => {
    await principalPending;
    await route.continue();
  });
  await page.route("**/api/backend/v1/search", async (route) => {
    await searchPending;
    await route.continue();
  });
  await page.goto("/");
  await page.getByRole("button", { name: "Search evidence" }).click();
  await page.getByLabel("Fixture principal").selectOption("denied-user");

  await expect(page.getByLabel("Fixture principal")).toHaveValue("denied-user");
  await expect(page.getByLabel("Ask a question")).toBeDisabled();
  await expect(page.getByRole("button", { name: "Search evidence" })).toBeDisabled();
  await expect(page.getByRole("button", { name: "Use the seeded travel question" })).toBeDisabled();
  const requestsDuringSwitch = backendRequests.length;
  await page.waitForTimeout(100);
  expect(backendRequests).toHaveLength(requestsDuringSwitch);

  releasePrincipal();
  releaseSearch();
  await expect(page.getByRole("button", { name: "Search evidence" })).toBeEnabled();
  await expect(page.getByText("Travel reimbursement policy", { exact: true })).toHaveCount(0);
});

test("principal switches discard delayed answer and preview responses", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("Ask a question").fill(canonicalQuestion);
  await page.getByRole("button", { name: "Search evidence" }).click();
  await expect(page.getByRole("heading", { name: "Travel reimbursement policy", exact: true })).toBeVisible();
  await page.route("**/api/backend/v1/answers", async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 250));
    await route.continue();
  });
  await page.getByRole("button", { name: "Generate cited answer" }).click();
  await page.getByLabel("Fixture principal").selectOption("denied-user");
  await page.waitForTimeout(400);
  await expect(page.getByText("Supporting citations")).toHaveCount(0);

  await page.goto("/");
  await page.getByLabel("Fixture principal").selectOption("allowed-user");
  await page.getByLabel("Ask a question").fill(canonicalQuestion);
  await page.getByRole("button", { name: "Search evidence" }).click();
  await expect(page.getByRole("heading", { name: "Travel reimbursement policy", exact: true })).toBeVisible();
  await page.route("**/api/backend/v1/results/*/preview", async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 250));
    await route.continue();
  });
  await page.getByRole("button", { name: "Open safe preview" }).first().click();
  await page.getByLabel("Fixture principal").selectOption("denied-user");
  await page.waitForTimeout(400);
  await expect(page.getByRole("heading", { name: "Verify the evidence" })).toHaveCount(0);
});
