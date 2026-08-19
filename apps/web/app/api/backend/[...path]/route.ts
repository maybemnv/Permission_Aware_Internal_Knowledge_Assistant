import { cookies } from "next/headers";
import { NextResponse } from "next/server";

const apiOrigin = process.env.API_ORIGIN ?? "http://127.0.0.1:8102";
const principals = new Set(["allowed-user", "denied-user", "cross-tenant-user", "admin-user"]);

async function proxy(request: Request, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  const principal = (await cookies()).get("demo_principal")?.value ?? "allowed-user";
  if (!principals.has(principal)) return NextResponse.json({ error: "Fixture principal is unavailable." }, { status: 401 });
  try {
    const upstream = await fetch(`${apiOrigin}/${path.join("/")}${new URL(request.url).search}`, {
      method: request.method,
      headers: { "Content-Type": request.headers.get("content-type") ?? "application/json", "X-Demo-Principal": principal },
      body: ["GET", "HEAD"].includes(request.method) ? undefined : await request.text(),
      cache: "no-store",
    });
    return new NextResponse(await upstream.text(), { status: upstream.status, headers: { "Content-Type": upstream.headers.get("content-type") ?? "application/json" } });
  } catch {
    return NextResponse.json({ error: "The fixture API is unavailable." }, { status: 503 });
  }
}

export const GET = proxy;
export const POST = proxy;
