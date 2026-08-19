import { expect, test } from "@playwright/test";

const canonicalQuestion = "What is the travel reimbursement policy for my region and role?";

async function selectPrincipal(page: import("@playwright/test").Page, principal: string) {
  await page.getByLabel("Fixture principal").selectOption(principal);
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

test("denied and cross-tenant principals receive safe absence without restricted hints", async ({ page }) => {
  for (const principal of ["denied-user", "cross-tenant-user"]) {
    await page.goto("/");
    await selectPrincipal(page, principal);
    await page.getByLabel("Ask a question").fill("Show details of the restricted project");
    await page.getByRole("button", { name: "Search evidence" }).click();

    await expect(page.getByText("No accessible context is available for this request.")).toBeVisible();
    await expect(page.getByText(/restricted project launch notes/i)).toHaveCount(0);
    await expect(page.getByText(/github:\/\/internal/i)).toHaveCount(0);
  }
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
  await expect(page.getByText("no_result")).toBeVisible();
  await expect(page.getByText(/[a-f0-9]{12}/)).toBeVisible();
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
