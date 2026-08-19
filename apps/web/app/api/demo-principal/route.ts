import { NextResponse } from "next/server";

const principals = new Set(["allowed-user", "denied-user", "unmapped-user", "changed-group-user", "cross-tenant-user", "admin-user"]);

export async function POST(request: Request) {
  const body = await request.json().catch(() => null);
  if (!body || typeof body.principal !== "string" || !principals.has(body.principal)) {
    return NextResponse.json({ error: "Unknown fixture principal." }, { status: 400 });
  }
  const response = NextResponse.json({ principal: body.principal });
  response.cookies.set("demo_principal", body.principal, { httpOnly: true, sameSite: "lax", path: "/" });
  return response;
}
