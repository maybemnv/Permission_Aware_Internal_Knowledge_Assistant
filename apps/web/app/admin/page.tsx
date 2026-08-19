import { cookies } from "next/headers";
import { ConnectorGrid } from "@/components/ConnectorGrid";

export default async function AdminPage() {
  const stored = (await cookies()).get("demo_principal")?.value;
  const initialPrincipal = stored === "allowed-user" || stored === "denied-user" || stored === "unmapped-user" || stored === "changed-group-user" || stored === "cross-tenant-user" || stored === "admin-user" ? stored : "allowed-user";
  return <ConnectorGrid initialPrincipal={initialPrincipal} />;
}